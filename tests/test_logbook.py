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
