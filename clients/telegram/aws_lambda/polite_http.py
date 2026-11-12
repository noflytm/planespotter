"""Polite network access for the optional scrapers.

Scraping third-party sites is OFF by default. When SCRAPING_ENABLED=1:

* the request carries an honest User-Agent that names this project (no browser impersonation);
* the target host's robots.txt is fetched with that same User-Agent and obeyed; if it cannot be
  fetched, or the honest client is refused, the request is not made;
* at most one request per host every SCRAPING_MIN_INTERVAL seconds (default 2).

Nothing fetched through here is committed to the repository; callers decide what to cache.
"""

import os
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

USER_AGENT = "goSpot/0.1 (+https://github.com/noflytm/planespotter)"


class ScrapingDisabled(RuntimeError):
    """Scraping is off (the default)."""


class BlockedByRobots(RuntimeError):
    """robots.txt does not allow this request, or could not be read."""


_robots = {}
_last_request = {}


def enabled() -> bool:
    return os.environ.get("SCRAPING_ENABLED") == "1"


def _min_interval() -> float:
    try:
        return max(0.0, float(os.environ.get("SCRAPING_MIN_INTERVAL", "2")))
    except ValueError:
        return 2.0


def _robots_for(origin: str) -> urllib.robotparser.RobotFileParser:
    parser = _robots.get(origin)
    if parser is not None:
        return parser
    parser = urllib.robotparser.RobotFileParser()
    request = urllib.request.Request(origin + "/robots.txt", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=5) as resp:
            parser.parse(resp.read().decode("utf-8", errors="ignore").splitlines())
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            parser.allow_all = True  # no robots.txt: nothing is disallowed
        else:
            parser.disallow_all = True  # refused (403, 429, 5xx): do not scrape
    except Exception:
        parser.disallow_all = True
    _robots[origin] = parser
    return parser


def urlopen(request, timeout: float = 10):
    """Drop-in for urllib.request.urlopen that applies the rules above."""
    if not enabled():
        raise ScrapingDisabled("scraping is disabled; set SCRAPING_ENABLED=1 to turn it on")
    if isinstance(request, str):
        request = urllib.request.Request(request)
    parts = urllib.parse.urlsplit(request.full_url)
    origin = f"{parts.scheme}://{parts.netloc}"
    if not _robots_for(origin).can_fetch(USER_AGENT, request.full_url):
        raise BlockedByRobots(f"robots.txt of {parts.netloc} does not allow {parts.path or '/'}")
    wait = _last_request.get(parts.netloc, 0.0) + _min_interval() - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    _last_request[parts.netloc] = time.monotonic()
    request.add_header("User-Agent", USER_AGENT)  # always ours, whatever the caller set
    return urllib.request.urlopen(request, timeout=timeout)
