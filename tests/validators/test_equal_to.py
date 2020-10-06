import pytest

from wtforms import Label
from wtforms.validators import equal_to
from wtforms.validators import ValidationError


def test_equal_to_passes(dummy_form, dummy_field):
    """
    Equal values should pass
    """
    dummy_field.data = "test"
    dummy_form["foo"] = dummy_field
    validator = equal_to("foo")
    validator(dummy_form, dummy_form["foo"])


@pytest.mark.parametrize(
    "field_val,equal_val", [("test", "invalid_field_name"), ("bad_value", "foo")]
)
def test_equal_to_raises(
    field_val, equal_val, dummy_form, dummy_field, dummy_field_class
):
    """
    It should raise ValidationError if the values are not equal
    """
    dummy_form["foo"] = dummy_field_class("test", label=Label("foo", "foo"))
    dummy_field.data = field_val
    validator = equal_to(equal_val)
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)
