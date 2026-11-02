import pytest

from planespotter import InvalidRegistration, parse_registration


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
