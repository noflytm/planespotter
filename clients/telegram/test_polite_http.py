import os
import sys
import unittest
import urllib.request
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "aws_lambda"))

import polite_http


class _Resp:
    def __init__(self, body=b""):
        self._body = body
        self.status = 200

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class PoliteHttpTests(unittest.TestCase):
    def setUp(self):
        polite_http._robots.clear()
        polite_http._last_request.clear()
        self.env = mock.patch.dict(os.environ, {"SCRAPING_ENABLED": "1", "SCRAPING_MIN_INTERVAL": "0"})
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_off_by_default(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(polite_http.ScrapingDisabled):
                polite_http.urlopen("https://example.test/page")

    def test_robots_disallow_blocks_the_request(self):
        calls = []

        def fake(req, timeout=None):
            calls.append(req.full_url)
            return _Resp(b"User-agent: *\nDisallow: /private\n")

        with mock.patch("urllib.request.urlopen", fake):
            with self.assertRaises(polite_http.BlockedByRobots):
                polite_http.urlopen(urllib.request.Request("https://example.test/private/x"))
        self.assertEqual(calls, ["https://example.test/robots.txt"])  # the page itself was never requested

    def test_refused_robots_means_no_scraping(self):
        def fake(req, timeout=None):
            raise urllib.error.HTTPError(req.full_url, 403, "Forbidden", {}, None)

        with mock.patch("urllib.request.urlopen", fake):
            with self.assertRaises(polite_http.BlockedByRobots):
                polite_http.urlopen("https://example.test/page")

    def test_missing_robots_allows_and_user_agent_is_honest(self):
        seen = {}

        def fake(req, timeout=None):
            if req.full_url.endswith("/robots.txt"):
                raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, None)
            seen["ua"] = req.get_header("User-agent")
            return _Resp(b"ok")

        request = urllib.request.Request("https://example.test/page", headers={"User-Agent": "Mozilla/5.0 Chrome/131"})
        with mock.patch("urllib.request.urlopen", fake):
            polite_http.urlopen(request)
        self.assertEqual(seen["ua"], polite_http.USER_AGENT)
        self.assertNotIn("Mozilla", seen["ua"])

    def test_requests_to_one_host_are_spaced_out(self):
        def fake(req, timeout=None):
            if req.full_url.endswith("/robots.txt"):
                return _Resp(b"User-agent: *\nDisallow:\n")
            return _Resp(b"ok")

        with mock.patch.dict(os.environ, {"SCRAPING_MIN_INTERVAL": "2"}), \
                mock.patch("urllib.request.urlopen", fake), mock.patch("time.sleep") as sleep:
            polite_http.urlopen("https://example.test/a")
            polite_http.urlopen("https://example.test/b")
        self.assertTrue(sleep.called)
        self.assertGreater(sleep.call_args[0][0], 0)


if __name__ == "__main__":
    unittest.main()
