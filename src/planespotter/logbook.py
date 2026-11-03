"""A spotter's logbook: record sightings, know which aircraft are new to you."""

import os
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from planespotter.registration import parse_registration

_CLOCK_SKEW = timedelta(minutes=5)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sightings (
    id            INTEGER PRIMARY KEY,
    registration  TEXT NOT NULL,
    country       TEXT NOT NULL,
    aircraft_type TEXT NOT NULL DEFAULT '',
    location      TEXT NOT NULL DEFAULT '',
    spotted_at    TEXT NOT NULL,
    UNIQUE (registration, location, spotted_at)
);
CREATE INDEX IF NOT EXISTS sightings_registration ON sightings (registration);
"""


class DuplicateSighting(Exception):
    """The same aircraft was already logged at that place and minute."""


@dataclass(frozen=True)
class Sighting:
    id: int
    registration: str
    country: str
    aircraft_type: str
    location: str
    spotted_at: datetime


@dataclass(frozen=True)
class LogResult:
    sighting: Sighting
    is_new: bool
    times_seen: int


@dataclass(frozen=True)
class SeenAircraft:
    registration: str
    country: str
    aircraft_type: str
    times_seen: int
    last_seen: datetime


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _create_private(path: Path) -> None:
    """Make sure the logbook file exists and only its owner can read it.

    SQLite gives its journal files the same mode as the database file, so securing
    the file covers those too. An existing file is tightened rather than trusted.
    """
    os.close(os.open(path, os.O_CREAT | os.O_RDWR, 0o600))
    os.chmod(path, 0o600)


class Logbook:
    def __init__(self, path: str | Path = ":memory:", *, clock: Callable[[], datetime] = _utc_now):
        if str(path) != ":memory:":
            path = Path(path)
            # Only a directory created here gets 0700; one that already exists is not ours to change.
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            _create_private(path)
        self._clock = clock
        # Autocommit; transactions are opened explicitly where atomicity matters.
        self._conn = sqlite3.connect(str(path), isolation_level=None)
        self._conn.executescript(_SCHEMA)

    def close(self) -> None:
        self._conn.close()

    def log(
        self,
        registration: str,
        *,
        aircraft_type: str = "",
        location: str = "",
        spotted_at: datetime | None = None,
    ) -> LogResult:
        """Record a sighting. ``is_new`` is true the first time a registration is logged."""
        reg = parse_registration(registration)
        when = self._normalise_time(spotted_at)
        aircraft_type = aircraft_type.strip()
        location = location.strip().upper()

        # IMMEDIATE takes the write lock up front, so two processes logging the same
        # registration cannot both be told it is new.
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            (before,) = self._conn.execute(
                "SELECT COUNT(*) FROM sightings WHERE registration = ?", (reg.code,)
            ).fetchone()
            try:
                cursor = self._conn.execute(
                    "INSERT INTO sightings (registration, country, aircraft_type, location, spotted_at)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (reg.code, reg.country, aircraft_type, location, when.isoformat()),
                )
            except sqlite3.IntegrityError as exc:
                raise DuplicateSighting(
                    f"{reg.code} is already logged at {location or 'this place'} at {when:%Y-%m-%d %H:%M} UTC"
                ) from exc
            self._conn.execute("COMMIT")
        except BaseException:
            if self._conn.in_transaction:
                self._conn.execute("ROLLBACK")
            raise

        sighting = Sighting(cursor.lastrowid, reg.code, reg.country, aircraft_type, location, when)
        return LogResult(sighting=sighting, is_new=before == 0, times_seen=before + 1)

    def has_seen(self, registration: str) -> bool:
        reg = parse_registration(registration)
        row = self._conn.execute(
            "SELECT 1 FROM sightings WHERE registration = ? LIMIT 1", (reg.code,)
        ).fetchone()
        return row is not None

    def seen(self) -> list[SeenAircraft]:
        """Every aircraft in the logbook, most recently seen first."""
        rows = self._conn.execute(
            "SELECT registration, country,"
            "       (SELECT aircraft_type FROM sightings s2"
            "         WHERE s2.registration = s.registration AND s2.aircraft_type <> ''"
            "         ORDER BY s2.spotted_at DESC LIMIT 1),"
            "       COUNT(*), MAX(spotted_at)"
            " FROM sightings s GROUP BY registration ORDER BY MAX(spotted_at) DESC, registration"
        ).fetchall()
        return [
            SeenAircraft(reg, country, aircraft_type or "", count, datetime.fromisoformat(last))
            for reg, country, aircraft_type, count, last in rows
        ]

    def _normalise_time(self, spotted_at: datetime | None) -> datetime:
        now = self._clock()
        if spotted_at is None:
            spotted_at = now
        if spotted_at.tzinfo is None:
            raise ValueError("spotted_at must be timezone-aware")
        spotted_at = spotted_at.astimezone(timezone.utc)
        if spotted_at > now + _CLOCK_SKEW:
            raise ValueError("spotted_at is in the future")
        # Minute precision: logging the same aircraft twice in one minute is a duplicate.
        return spotted_at.replace(second=0, microsecond=0)
