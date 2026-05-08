import re

import pytest

from wtforms.validators import regexp
from wtforms.validators import ValidationError


def grab_error_message(callable, form, field):
    try:
        callable(form, field)
    except ValidationError as e:
        return e.args[0]


@pytest.mark.parametrize(
    "pattern, matcher, value, expected",
    [
        ("^a", re.match, "abcd", "a"),
        (re.compile("^a", re.I), re.match, "ABcd", "A"),
        (r"\w+", re.search, "  abcd  ", "abcd"),
        ("bc", re.search, "abcd", "bc"),
        (r"\w+", re.fullmatch, "abcd", "abcd"),
        ("^abcd$", re.fullmatch, "abcd", "abcd"),
    ],
)
def test_regex_passes(pattern, matcher, value, expected, dummy_form, dummy_field):
    """Each matcher returns the expected Match group when the value matches."""
    validator = regexp(pattern, matcher=matcher)
    dummy_field.data = value
    assert validator(dummy_form, dummy_field).group(0) == expected


@pytest.mark.parametrize(
    "pattern, matcher, value",
    [
        ("^a", re.match, "ABC"),
        ("^a", re.match, None),
        (r"\w+", re.fullmatch, "abc!"),
        ("^abcd$", re.fullmatch, "foo"),
        ("bc", re.search, "xyz"),
        ("bc", re.search, None),
    ],
)
def test_regex_raises(pattern, matcher, value, dummy_form, dummy_field):
    """ValidationError is raised when the matcher returns no match."""
    validator = regexp(pattern, matcher=matcher)
    dummy_field.data = value
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


def test_regexp_message(dummy_form, dummy_field):
    """Custom message is forwarded as the ValidationError message."""
    validator = regexp("^a", message="foo")
    dummy_field.data = "f"
    assert grab_error_message(validator, dummy_form, dummy_field) == "foo"


def test_default_matcher_is_re_match(dummy_form, dummy_field):
    """Without a matcher, behaviour matches re.match (anchored at start only)."""
    validator = regexp(r"\d+")
    dummy_field.data = "123abc"
    assert validator(dummy_form, dummy_field).group(0) == "123"


def test_pattern_method_as_matcher(dummy_form, dummy_field):
    """Unbound Pattern methods are accepted as matchers."""
    validator = regexp(r"\d+", matcher=re.Pattern.fullmatch)
    dummy_field.data = "123"
    assert validator(dummy_form, dummy_field).group(0) == "123"
    dummy_field.data = "123abc"
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


def test_html_pattern_disabled_by_default():
    """No ``pattern`` field flag is emitted unless ``html_pattern`` is set."""
    assert regexp("^a").field_flags == {}


def test_html_pattern_true_emits_python_source():
    """``html_pattern=True`` emits the Python regex source as the HTML pattern."""
    assert regexp("^[A-Z]+$", html_pattern=True).field_flags == {"pattern": "^[A-Z]+$"}


def test_html_pattern_string_overrides_source():
    """A string ``html_pattern`` is emitted verbatim, independent of the regex."""
    validator = regexp(r"(?P<n>\d+)", html_pattern="^[0-9]+$")
    assert validator.field_flags == {"pattern": "^[0-9]+$"}


def test_html_pattern_callable_returning_bool():
    """A callable returning ``True``/``False`` toggles emission of the source."""
    enabled = regexp("^a", html_pattern=lambda r: True)
    assert enabled.field_flags == {"pattern": "^a"}
    disabled = regexp("^a", html_pattern=lambda r: False)
    assert disabled.field_flags == {}


def test_html_pattern_callable_returning_string():
    """A callable can return a custom string used as the HTML pattern."""
    validator = regexp(
        r"(?P<n>\d+)", html_pattern=lambda r: r.pattern.replace("?P", "?")
    )
    assert validator.field_flags == {"pattern": r"(?<n>\d+)"}
