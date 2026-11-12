import pytest

from gospot import InvalidRegistration, parse_registration


@pytest.mark.parametrize(
    ("text", "code", "country"),
    [
        ("SP-EXE", "SP-EXE", "Poland"),
        ("sp exe", "SP-EXE", "Poland"),
        ("  spexe ", "SP-EXE", "Poland"),
        ("g-euuu", "G-EUUU", "United Kingdom"),
        ("DABCD", "D-ABCD", "Germany"),
        ("9H-VUA", "9H-VUA", "Malta"),
        ("N123AB", "N123AB", "United States"),
        ("n-123ab", "N123AB", "United States"),
        ("JA123A", "JA123A", "Japan"),
        ("HL7777", "HL7777", "South Korea"),
        ("ZZ-ABC", "ZZ-ABC", "Unknown"),
    ],
)
def test_canonical_form_and_country(text, code, country):
    reg = parse_registration(text)
    assert (reg.code, reg.country) == (code, country)


@pytest.mark.parametrize(
    "text",
    ["", "   ", "SP-", "-EXE", "S", "SP-E", "SP-TOOLONG", "ZZABC", "SP-EXE!", "N0123", "NABC", "N123456", "HL12", "banana", "FOOBAR"],
)
def test_rejects_non_registrations(text):
    with pytest.raises(InvalidRegistration):
        parse_registration(text)


def test_unprefixed_text_does_not_match_a_one_letter_prefix_by_accident():
    # "N..." must be a valid US N-number, not any word starting with N.
    with pytest.raises(InvalidRegistration):
        parse_registration("NOTAPLANE")


@pytest.mark.parametrize(
    "text",
    [
        "ſp-exe",  # long s upper-cases to S
        "ſpexe",
        "ıb-abc",  # dotless i upper-cases to I
        "spß",  # sharp s upper-cases to SS
        "ＳＰ-ＥＸＥ",  # full-width letters
        "sp-exé",
    ],
)
def test_rejects_non_ascii_before_case_folding(text):
    with pytest.raises(InvalidRegistration):
        parse_registration(text)


def test_lowercase_ascii_is_still_accepted():
    assert parse_registration("sp-exe").code == "SP-EXE"
    assert parse_registration("spexe").code == "SP-EXE"


def test_error_message_does_not_echo_control_characters():
    with pytest.raises(InvalidRegistration) as excinfo:
        parse_registration("\x1b[31mSP-EXE")
    assert "\x1b" not in str(excinfo.value)
