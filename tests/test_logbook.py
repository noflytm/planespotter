import os
import stat
from datetime import datetime, timedelta, timezone

import pytest

from planespotter import DuplicateSighting, InvalidRegistration, Logbook

NOW = datetime(2026, 11, 3, 18, 0, tzinfo=timezone.utc)


@pytest.fixture
def book():
    b = Logbook(clock=lambda: NOW)
    yield b
    b.close()


def test_first_sighting_is_new(book):
    result = book.log("SP-EXE", aircraft_type="Boeing 737 MAX 8", location="waw")
    assert result.is_new
    assert result.times_seen == 1
    assert result.sighting.registration == "SP-EXE"
    assert result.sighting.country == "Poland"
    assert result.sighting.location == "WAW"


def test_second_sighting_is_not_new(book):
    book.log("SP-EXE", spotted_at=NOW - timedelta(days=2))
    result = book.log("sp exe")
    assert not result.is_new
    assert result.times_seen == 2


def test_different_spellings_are_the_same_aircraft(book):
    book.log("SP-EXE", spotted_at=NOW - timedelta(days=1))
    assert book.has_seen("spexe")


def test_has_seen_is_false_for_unlogged_aircraft(book):
    book.log("SP-EXE")
    assert not book.has_seen("SP-LMG")


def test_same_aircraft_same_place_same_minute_is_a_duplicate(book):
    book.log("SP-EXE", location="WAW")
    with pytest.raises(DuplicateSighting):
        book.log("SP-EXE", location="waw", spotted_at=NOW + timedelta(seconds=30))


def test_failed_duplicate_does_not_change_the_count(book):
    book.log("SP-EXE", location="WAW")
    with pytest.raises(DuplicateSighting):
        book.log("SP-EXE", location="WAW")
    assert book.log("SP-EXE", location="WMI").times_seen == 2


def test_same_aircraft_at_another_place_is_not_a_duplicate(book):
    book.log("SP-EXE", location="WAW")
    assert book.log("SP-EXE", location="WMI").times_seen == 2


def test_invalid_registration_is_rejected_and_nothing_is_stored(book):
    with pytest.raises(InvalidRegistration):
        book.log("not a plane")
    assert book.seen() == []


def test_naive_time_is_rejected(book):
    with pytest.raises(ValueError, match="timezone-aware"):
        book.log("SP-EXE", spotted_at=datetime(2026, 11, 3, 17, 0))


def test_future_time_is_rejected(book):
    with pytest.raises(ValueError, match="future"):
        book.log("SP-EXE", spotted_at=NOW + timedelta(hours=1))


def test_times_are_stored_in_utc(book):
    warsaw = timezone(timedelta(hours=1))
    result = book.log("SP-EXE", spotted_at=datetime(2026, 11, 3, 17, 8, tzinfo=warsaw))
    assert result.sighting.spotted_at == datetime(2026, 11, 3, 16, 8, tzinfo=timezone.utc)


def test_seen_lists_each_aircraft_once_most_recent_first(book):
    book.log("SP-EXE", aircraft_type="Boeing 737 MAX 8", spotted_at=NOW - timedelta(days=3))
    book.log("SP-LMG", aircraft_type="Embraer E190STD", spotted_at=NOW - timedelta(days=1))
    book.log("SP-EXE", location="WAW", spotted_at=NOW - timedelta(days=2))
    seen = book.seen()
    assert [(s.registration, s.times_seen) for s in seen] == [("SP-LMG", 1), ("SP-EXE", 2)]
    assert seen[1].aircraft_type == "Boeing 737 MAX 8"


def test_logbook_persists_to_disk(tmp_path):
    path = tmp_path / "nested" / "logbook.db"
    first = Logbook(path, clock=lambda: NOW)
    first.log("SP-EXE", spotted_at=NOW - timedelta(days=1))
    first.close()
    second = Logbook(path, clock=lambda: NOW)
    assert not second.log("SP-EXE").is_new
    second.close()


def test_small_clock_drift_is_allowed_but_not_more(book):
    assert book.log("SP-EXE", spotted_at=NOW + timedelta(minutes=4)).is_new
    with pytest.raises(ValueError, match="future"):
        book.log("SP-LMG", spotted_at=NOW + timedelta(minutes=6))


posix_only = pytest.mark.skipif(os.name != "posix", reason="POSIX file modes")


def _mode(path):
    return stat.S_IMODE(path.stat().st_mode)


@posix_only
def test_new_logbook_is_private_to_the_owner(tmp_path):
    old_umask = os.umask(0o022)
    try:
        path = tmp_path / "fresh" / "logbook.db"
        book = Logbook(path, clock=lambda: NOW)
        book.log("SP-EXE", spotted_at=NOW - timedelta(days=1))
        book.close()
    finally:
        os.umask(old_umask)
    assert _mode(path) == 0o600
    assert _mode(path.parent) == 0o700


@posix_only
def test_existing_logbook_is_tightened_but_its_directory_is_left_alone(tmp_path):
    path = tmp_path / "logbook.db"
    path.touch()
    path.chmod(0o644)
    before = _mode(tmp_path)
    Logbook(path, clock=lambda: NOW).close()
    assert _mode(path) == 0o600
    assert _mode(tmp_path) == before
