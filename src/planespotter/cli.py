"""Command line interface: ``planespotter log | seen``."""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from planespotter.logbook import DuplicateSighting, Logbook
from planespotter.registration import InvalidRegistration


def _default_db() -> Path:
    return Path(os.environ.get("PLANESPOTTER_DB", Path.home() / ".planespotter" / "logbook.db"))


def _parse_when(value: str) -> datetime:
    try:
        when = datetime.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not an ISO time: {value!r} (e.g. 2026-11-03T17:08Z)") from None
    if when.tzinfo is None:
        raise argparse.ArgumentTypeError("time needs a UTC offset, e.g. 2026-11-03T17:08Z")
    return when


def _ordinal(n: int) -> str:
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="planespotter", description="A spotter's logbook.")
    parser.add_argument("--db", type=Path, default=None, help="logbook file (default: ~/.planespotter/logbook.db)")
    sub = parser.add_subparsers(dest="command", required=True)

    log = sub.add_parser("log", help="log a sighting and see if the aircraft is new to you")
    log.add_argument("registration", help="e.g. SP-EXE")
    log.add_argument("--type", dest="aircraft_type", default="", help="aircraft type, e.g. 'Boeing 737 MAX 8'")
    log.add_argument("--at", dest="location", default="", help="where you saw it, e.g. WAW")
    log.add_argument("--when", type=_parse_when, default=None, help="ISO time with offset (default: now)")

    sub.add_parser("seen", help="list every aircraft in your logbook")
    return parser


def main(argv: list[str] | None = None, *, out=None, err=None) -> int:
    out = out or sys.stdout
    err = err or sys.stderr
    args = _build_parser().parse_args(argv)
    book = Logbook(args.db or _default_db())
    try:
        if args.command == "log":
            result = book.log(
                args.registration,
                aircraft_type=args.aircraft_type,
                location=args.location,
                spotted_at=args.when,
            )
            s = result.sighting
            detail = (f" - {s.aircraft_type}" if s.aircraft_type else "") + (f" at {s.location}" if s.location else "")
            label = "NEW aircraft" if result.is_new else f"Seen before ({_ordinal(result.times_seen)} sighting)"
            print(f"{label}: {s.registration} ({s.country}){detail}", file=out)
        else:
            for row in book.seen():
                print(
                    f"{row.registration:<8} {row.country:<22} {row.aircraft_type:<24} "
                    f"x{row.times_seen}  last {row.last_seen:%Y-%m-%d %H:%M} UTC",
                    file=out,
                )
    except (InvalidRegistration, DuplicateSighting, ValueError) as exc:
        print(f"error: {exc}", file=err)
        return 2
    finally:
        book.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
