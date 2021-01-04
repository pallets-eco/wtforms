import pytest

from wtforms.validators import uppercase_required
from wtforms.validators import ValidationError


@pytest.mark.parametrize("min_v", [2, 3, 4, 5, 6])
def test_correct_uppercase_required(min_v, dummy_form, dummy_field):
    """
    It should pass for the string with correct count of required uppercase letter.
    """
    dummy_field.data = "AsDfG87KJhg8J"
    validator = uppercase_required(min_v)
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    ("validator", "message"),
    (
        (
            uppercase_required(2, "at least 2 uppercase letter"),
            "at least 2 uppercase letter",
        ),
        (uppercase_required(2), "at least 2 uppercase letter"),
    ),
)
def test_uppercase_required_messages(dummy_form, dummy_field, validator, message):
    """
    It should raise ValidationError for string with incorect uppercase_required.
    """
    dummy_field.data = "foo123"

    with pytest.raises(ValidationError) as e:
        validator(dummy_form, dummy_field)
        assert str(e.value) == message
