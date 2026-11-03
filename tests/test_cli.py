import io

from gospot.cli import main


def run(db, *argv):
    out, err = io.StringIO(), io.StringIO()
    code = main(["--db", str(db), *argv], out=out, err=err)
    return code, out.getvalue(), err.getvalue()


def test_log_reports_new_then_seen_before(tmp_path):
    db = tmp_path / "logbook.db"
    code, out, _ = run(db, "log", "sp-exe", "--type", "Boeing 737 MAX 8", "--at", "waw", "--when", "2026-11-02T17:08Z")
    assert code == 0
    assert out.strip() == "NEW aircraft: SP-EXE (Poland) - Boeing 737 MAX 8 at WAW"

    code, out, _ = run(db, "log", "SP-EXE", "--at", "WMI", "--when", "2026-11-02T20:00Z")
    assert code == 0
    assert out.strip() == "Seen before (2nd sighting): SP-EXE (Poland) at WMI"


def test_seen_lists_the_logbook(tmp_path):
    db = tmp_path / "logbook.db"
    run(db, "log", "SP-EXE", "--when", "2026-11-02T17:08Z")
    code, out, _ = run(db, "seen")
    assert code == 0
    assert "SP-EXE" in out and "x1" in out


def test_invalid_registration_exits_2(tmp_path):
    code, out, err = run(tmp_path / "logbook.db", "log", "banana")
    assert code == 2
    assert out == ""
    assert "not a valid registration" in err


def test_duplicate_exits_2(tmp_path):
    db = tmp_path / "logbook.db"
    run(db, "log", "SP-EXE", "--at", "WAW", "--when", "2026-11-02T17:08Z")
    code, _, err = run(db, "log", "SP-EXE", "--at", "WAW", "--when", "2026-11-02T17:08Z")
    assert code == 2
    assert "already logged" in err


def test_unusable_db_path_is_a_clean_error_not_a_traceback(tmp_path):
    blocker = tmp_path / "afile"
    blocker.write_text("not a directory")
    code, out, err = run(blocker / "logbook.db", "seen")
    assert code == 2
    assert out == ""
    assert err.startswith("error:")
    assert "Traceback" not in err


def test_db_path_that_is_a_directory_is_a_clean_error(tmp_path):
    code, _, err = run(tmp_path, "seen")
    assert code == 2
    assert err.startswith("error:")
