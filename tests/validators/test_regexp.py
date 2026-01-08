import re

import pytest

from wtforms.validators import regexp
from wtforms.validators import ValidationError
from wtforms.validators import ValidatorSetupError


def grab_error_message(callable, form, field):
    try:
        callable(form, field)
    except ValidationError as e:
        return e.args[0]


@pytest.mark.parametrize(
    "re_pattern, re_flags, re_mode, test_v, expected_v",
    [
        # match mode
        ("^a", None, "match", "abcd", "a"),
        ("^a", re.I, "match", "ABcd", "A"),
        ("^ab", None, "match", "abcd", "ab"),
        ("^ab", re.I, "match", "ABcd", "AB"),
        ("^abcd", None, "match", "abcd", "abcd"),
        ("^abcd", re.I, "match", "ABcd", "ABcd"),
        (r"^\w+", None, "match", "abcd", "abcd"),
        (r"^\w+", re.I, "match", "ABcd", "ABcd"),
        (re.compile("^a"), None, "match", "abcd", "a"),
        (re.compile("^a", re.I), None, "match", "ABcd", "A"),
        (re.compile("^ab"), None, "match", "abcd", "ab"),
        (re.compile("^ab", re.I), None, "match", "ABcd", "AB"),
        (re.compile("^abcd"), None, "match", "abcd", "abcd"),
        (re.compile("^abcd", re.I), None, "match", "ABcd", "ABcd"),
        (re.compile(r"^\w+"), None, "match", "abcd", "abcd"),
        (re.compile(r"^\w+", re.I), None, "match", "ABcd", "ABcd"),
        # fullmatch mode
        ("^abcd", None, "fullmatch", "abcd", "abcd"),
        ("^abcd", re.I, "fullmatch", "ABcd", "ABcd"),
        ("^abcd$", None, "fullmatch", "abcd", "abcd"),
        ("^abcd$", re.I, "fullmatch", "ABcd", "ABcd"),
        (r"^\w+", None, "fullmatch", "abcd", "abcd"),
        (r"^\w+", re.I, "fullmatch", "ABcd", "ABcd"),
        (r"^\w+$", None, "fullmatch", "abcd", "abcd"),
        (r"^\w+$", re.I, "fullmatch", "ABcd", "ABcd"),
        (re.compile("^abcd"), None, "fullmatch", "abcd", "abcd"),
        (re.compile("^abcd", re.I), None, "fullmatch", "ABcd", "ABcd"),
        (re.compile("^abcd$"), None, "fullmatch", "abcd", "abcd"),
        (re.compile("^abcd$", re.I), None, "fullmatch", "ABcd", "ABcd"),
        (re.compile(r"^\w+"), None, "fullmatch", "abcd", "abcd"),
        (re.compile(r"^\w+", re.I), None, "fullmatch", "ABcd", "ABcd"),
        (re.compile(r"^\w+$"), None, "fullmatch", "abcd", "abcd"),
        (re.compile(r"^\w+$", re.I), None, "fullmatch", "ABcd", "ABcd"),
        # search mode
        ("^a", None, "search", "abcd", "a"),
        ("^a", re.I, "search", "ABcd", "A"),
        ("bc", None, "search", "abcd", "bc"),
        ("bc", re.I, "search", "ABcd", "Bc"),
        ("cd$", None, "search", "abcd", "cd"),
        ("cd$", re.I, "search", "ABcd", "cd"),
        (r"\w", None, "search", "abcd", "a"),
        (r"\w", re.I, "search", "ABcd", "A"),
        (r"\w$", None, "search", "abcd", "d"),
        (r"\w$", re.I, "search", "ABcd", "d"),
        (r"\w+", None, "search", "abcd", "abcd"),
        (r"\w+", re.I, "search", "ABcd", "ABcd"),
        (r"\w+$", None, "search", "abcd", "abcd"),
        (r"\w+$", re.I, "search", "ABcd", "ABcd"),
        (re.compile("^a"), None, "search", "abcd", "a"),
        (re.compile("^a", re.I), None, "search", "ABcd", "A"),
        (re.compile(r"d$"), None, "search", "abcd", "d"),
        (re.compile(r"d$", re.I), None, "search", "ABcd", "d"),
        (re.compile("bc"), None, "search", "abcd", "bc"),
        (re.compile("bc", re.I), None, "search", "ABcd", "Bc"),
        (re.compile(r"\w"), None, "search", "abcd", "a"),
        (re.compile(r"\w", re.I), None, "search", "ABcd", "A"),
        (re.compile(r"\w+"), None, "search", "abcd", "abcd"),
        (re.compile(r"\w+", re.I), None, "search", "ABcd", "ABcd"),
    ],
)
def test_regex_passes(
    re_pattern, re_flags, re_mode, test_v, expected_v, dummy_form, dummy_field
):
    """
    Regex should pass if there is a match.
    Should work for compile regex too
    """
    kwargs = {
        "regex": re_pattern,
        "flags": re_flags or 0,
        "message": None,
        "mode": re_mode,
    }
    validator = regexp(**kwargs)
    dummy_field.data = test_v
    assert validator(dummy_form, dummy_field).group(0) == expected_v


@pytest.mark.parametrize(
    "re_pattern, re_flags, re_mode, test_v",
    [
        # math mode
        ("^a", None, "match", "ABC"),
        ("^a", re.I, "match", "foo"),
        ("^a", None, "match", None),
        ("^ab", None, "match", "ABC"),
        ("^ab", re.I, "match", "foo"),
        ("^ab", None, "match", None),
        ("^ab$", None, "match", "ABC"),
        ("^ab$", re.I, "match", "foo"),
        ("^ab$", None, "match", None),
        (re.compile("^a"), None, "match", "ABC"),
        (re.compile("^a", re.I), None, "match", "foo"),
        (re.compile("^a"), None, "match", None),
        (re.compile("^ab"), None, "match", "ABC"),
        (re.compile("^ab", re.I), None, "match", "foo"),
        (re.compile("^ab"), None, "match", None),
        (re.compile("^ab$"), None, "match", "ABC"),
        (re.compile("^ab$", re.I), None, "match", "foo"),
        (re.compile("^ab$"), None, "match", None),
        # fullmatch mode
        ("^abcd", None, "fullmatch", "abc"),
        ("^abcd", re.I, "fullmatch", "abc"),
        ("^abcd", None, "fullmatch", "foo"),
        ("^abcd", re.I, "fullmatch", "foo"),
        ("^abcd", None, "fullmatch", None),
        ("^abcd", re.I, "fullmatch", None),
        ("abcd$", None, "fullmatch", "abc"),
        ("abcd$", re.I, "fullmatch", "abc"),
        ("abcd$", None, "fullmatch", "foo"),
        ("abcd$", re.I, "fullmatch", "foo"),
        ("abcd$", None, "fullmatch", None),
        ("abcd$", re.I, "fullmatch", None),
        ("^abcd$", None, "fullmatch", "abc"),
        ("^abcd$", re.I, "fullmatch", "abc"),
        ("^abcd$", None, "fullmatch", "foo"),
        ("^abcd$", re.I, "fullmatch", "foo"),
        ("^abcd$", None, "fullmatch", None),
        ("^abcd$", re.I, "fullmatch", None),
        (re.compile("^abcd"), None, "fullmatch", "abc"),
        (re.compile("^abcd", re.I), None, "fullmatch", "abc"),
        (re.compile("^abcd"), None, "fullmatch", "foo"),
        (re.compile("^abcd", re.I), None, "fullmatch", "foo"),
        (re.compile("^abcd"), None, "fullmatch", None),
        (re.compile("^abcd", re.I), None, "fullmatch", None),
        (re.compile("abcd$"), None, "fullmatch", "abc"),
        (re.compile("abcd$", re.I), None, "fullmatch", "abc"),
        (re.compile("abcd$"), None, "fullmatch", "foo"),
        (re.compile("abcd$", re.I), None, "fullmatch", "foo"),
        (re.compile("abcd$"), None, "fullmatch", None),
        (re.compile("abcd$", re.I), None, "fullmatch", None),
        (re.compile("^abcd$"), None, "fullmatch", "abc"),
        (re.compile("^abcd$", re.I), None, "fullmatch", "abc"),
        (re.compile("^abcd$"), None, "fullmatch", "foo"),
        (re.compile("^abcd$", re.I), None, "fullmatch", "foo"),
        (re.compile("^abcd$"), None, "fullmatch", None),
        (re.compile("^abcd$", re.I), None, "fullmatch", None),
        # search mode
        ("^a", None, "search", "foo"),
        ("^a", re.I, "search", "foo"),
        ("^a", None, "search", None),
        ("^a", re.I, "search", None),
        ("bc", None, "search", "foo"),
        ("bc", re.I, "search", "foo"),
        ("bc", None, "search", None),
        ("bc", re.I, "search", None),
        ("cd$", None, "search", "foo"),
        ("cd$", re.I, "search", "foo"),
        ("cd$", None, "search", None),
        ("cd$", re.I, "search", None),
        (re.compile("^a"), None, "search", "foo"),
        (re.compile("^a", re.I), None, "search", "foo"),
        (re.compile("^a"), None, "search", None),
        (re.compile("^a", re.I), None, "search", None),
        (re.compile("bc"), None, "search", "foo"),
        (re.compile("bc", re.I), None, "search", "foo"),
        (re.compile("bc"), None, "search", None),
        (re.compile("bc", re.I), None, "search", None),
        (re.compile(r"cd$"), None, "search", "foo"),
        (re.compile(r"cd$", re.I), None, "search", "foo"),
        (re.compile(r"cd$"), None, "search", None),
        (re.compile(r"cd$", re.I), None, "search", None),
    ],
)
def test_regex_raises(re_pattern, re_flags, re_mode, test_v, dummy_form, dummy_field):
    """
    Regex should raise ValidationError if there is no match
    Should work for compile regex too
    """
    kwargs = {
        "regex": re_pattern,
        "flags": re_flags or 0,
        "message": None,
        "mode": re_mode,
    }
    validator = regexp(**kwargs)
    dummy_field.data = test_v

    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


def test_regexp_message(dummy_form, dummy_field):
    """
    Regexp validator should return given message
    """
    validator = regexp("^a", message="foo")
    dummy_field.data = "f"
    assert grab_error_message(validator, dummy_form, dummy_field) == "foo"


@pytest.mark.parametrize(
    "re_mode",
    [
        "MATCH",
        "SEARCH",
        "FULLMATCH",
        "Match",
        "Search",
        "Fullmatch",
        "",
        "match ",
        " match",
        "search ",
        " search",
        "fullmatch ",
        " fullmatch",
        None,
        1,
        1.0,
        True,
        False,
        [],
        {},
        (),
    ],
)
def test_regex_invalid_mode(dummy_form, dummy_field, re_mode):
    """
    Regexp validator should raise ValidatorSetupError during an object instantiation,
    if mode is invalid (unsupported).
    """
    with pytest.raises(ValidatorSetupError) as e:
        regexp("^a", mode=re_mode)

    expected_msg_tmpl = (
        "Invalid mode value '{}'. Supported values: search, match, fullmatch"
    )

    assert e.value.args[0] == expected_msg_tmpl.format(re_mode)
