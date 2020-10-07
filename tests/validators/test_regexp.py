import re

import pytest
from tests.common import DummyPostData

from wtforms.fields import MultipleFileField
from wtforms.form import Form
from wtforms.validators import regexp
from wtforms.validators import ValidationError


@pytest.mark.parametrize(
    "re_pattern, re_flags, test_v, expected_v",
    [
        ("^a", None, "abcd", "a"),
        ("^a", re.I, "ABcd", "A"),
        (re.compile("^a"), None, "abcd", "a"),
        (re.compile("^a", re.I), None, "ABcd", "A"),
    ],
)
def test_regex_passes(
    re_pattern, re_flags, test_v, expected_v, dummy_form, dummy_field
):
    """
    Regex should pass if there is a match.
    Should work for complie regex too
    """
    validator = regexp(re_pattern, re_flags) if re_flags else regexp(re_pattern)
    dummy_field.data = test_v
    assert validator(dummy_form, dummy_field).group(0) == expected_v


@pytest.mark.parametrize(
    "re_pattern, re_flags, test_v",
    [
        ("^a", None, "ABC"),
        ("^a", re.I, "foo"),
        ("^a", None, None),
        (re.compile("^a"), None, "foo"),
        (re.compile("^a", re.I), None, None),
    ],
)
def test_regex_raises(re_pattern, re_flags, test_v, dummy_form, dummy_field):
    """
    Regex should raise ValidationError if there is no match
    Should work for complie regex too
    """
    validator = regexp(re_pattern, re_flags) if re_flags else regexp(re_pattern)
    dummy_field.data = test_v
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


def test_regexp_message(dummy_form, dummy_field, grab_error_message):
    """
    Regexp validator should return given message
    """
    validator = regexp("^a", message="foo")
    dummy_field.data = "f"
    assert grab_error_message(validator, dummy_form, dummy_field) == "foo"


def test_multiple_file_field():
    class F(Form):
        foo = MultipleFileField(validators=[regexp(r".*\.jpg$")])

    assert F(DummyPostData({"foo": ["foo.jpg", "bar.jpg"]})).validate()
    assert not F(DummyPostData({"foo": ["foo.jpg", "bar.png"]})).validate()
