"""Aircraft registration parsing and normalisation.

"sp exe", "SP-EXE" and "spexe" are the same aircraft, so the logbook keys on the
canonical form returned here.
"""

import re
from dataclasses import dataclass

# Nationality prefixes that are written with a hyphen (SP-EXE). Unlisted prefixes are
# still accepted when the hyphen is present; they just have no country name.
_HYPHENATED_PREFIXES = {
    "SP": "Poland",
    "OE": "Austria",
    "9H": "Malta",
    "D": "Germany",
    "F": "France",
    "G": "United Kingdom",
    "EI": "Ireland",
    "EJ": "Ireland",
    "TC": "Turkey",
    "A6": "United Arab Emirates",
    "A7": "Qatar",
    "HZ": "Saudi Arabia",
    "4X": "Israel",
    "UR": "Ukraine",
    "RA": "Russia",
    "RF": "Russia",
    "EW": "Belarus",
    "YL": "Latvia",
    "LY": "Lithuania",
    "ES": "Estonia",
    "HB": "Switzerland",
    "OH": "Finland",
    "SE": "Sweden",
    "LN": "Norway",
    "OY": "Denmark",
    "PH": "Netherlands",
    "OO": "Belgium",
    "LX": "Luxembourg",
    "EC": "Spain",
    "CS": "Portugal",
    "I": "Italy",
    "SX": "Greece",
    "HA": "Hungary",
    "OK": "Czechia",
    "OM": "Slovakia",
    "9A": "Croatia",
    "S5": "Slovenia",
    "YU": "Serbia",
    "LZ": "Bulgaria",
    "YR": "Romania",
    "B": "China / Taiwan",
    "VT": "India",
    "VH": "Australia",
    "ZK": "New Zealand",
    "C": "Canada",
}

_UNKNOWN_COUNTRY = "Unknown"

# Registrations written without a hyphen.
_US = re.compile(r"N[1-9][0-9]{0,4}[A-Z]{0,2}")
_JAPAN = re.compile(r"JA(?:[0-9]{4}|[0-9]{3}[A-Z]|[0-9]{2}[A-Z]{2})")
_KOREA = re.compile(r"HL[0-9]{4}")

_HYPHENATED = re.compile(r"([A-Z0-9]{1,2})-([A-Z0-9]{2,5})")
# Without a hyphen the prefix/suffix split is a guess, so be strict about the suffix length:
# one-letter prefixes (D-ABCD, G-EUUU, B-1234) always have four characters after them.
_UNHYPHENATED_REST = {1: re.compile(r"[A-Z0-9]{4}"), 2: re.compile(r"[A-Z0-9]{3,5}")}
_ALLOWED_CHARS = re.compile(r"[A-Z0-9 \t_-]+")


class InvalidRegistration(ValueError):
    """The text is not a plausible aircraft registration."""


@dataclass(frozen=True)
class Registration:
    code: str
    country: str


def parse_registration(text: str) -> Registration:
    """Return the canonical registration (e.g. ``SP-EXE``) and its country."""
    text = text or ""
    # Check for ASCII before stripping or changing case: str.strip() also removes Unicode
    # whitespace (no-break space, em space) and a few letters (ſ, ı) upper-case into ASCII.
    if not text.isascii():
        raise InvalidRegistration(f"not a valid registration: {text!r}")
    upper = text.strip().upper()
    if not _ALLOWED_CHARS.fullmatch(upper):
        raise InvalidRegistration(f"not a valid registration: {text!r}")

    had_hyphen = "-" in upper
    compact = re.sub(r"[ \t_-]", "", upper)

    if len(compact) <= 6 and _US.fullmatch(compact):
        return Registration(compact, "United States")
    if _JAPAN.fullmatch(compact):
        return Registration(compact, "Japan")
    if _KOREA.fullmatch(compact):
        return Registration(compact, "South Korea")

    if had_hyphen:
        match = _HYPHENATED.fullmatch(re.sub(r"[ \t_]", "", upper))
        if match:
            prefix, rest = match.groups()
            return Registration(f"{prefix}-{rest}", _HYPHENATED_PREFIXES.get(prefix, _UNKNOWN_COUNTRY))
        raise InvalidRegistration(f"not a valid registration: {text!r}")

    # No hyphen: infer the split from the known prefixes, longest first.
    for size in (2, 1):
        prefix, rest = compact[:size], compact[size:]
        if prefix in _HYPHENATED_PREFIXES and _UNHYPHENATED_REST[size].fullmatch(rest):
            return Registration(f"{prefix}-{rest}", _HYPHENATED_PREFIXES[prefix])
    raise InvalidRegistration(f"not a valid registration: {text!r}")
