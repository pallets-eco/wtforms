import pytest

from wtforms.validators import digit_required
from wtforms.validators import ValidationError


@pytest.mark.parametrize("min_v", [2, 3, 4, 5, 6])
def test_correct_digit_required(min_v, dummy_form, dummy_field):
    """
    It should pass for the string with correct count of required digit.
    """
    dummy_field.data = "asdqwe872536"
    validator = digit_required(min_v)
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    ("validator", "message"),
    (
        (digit_required(2, "at least 2 digit."), "at least 2 digit."),
        (digit_required(2), "at least 2 digit"),
    ),
)
def test_digit_required_messages(dummy_form, dummy_field, validator, message):
    """
    It should raise ValidationError for string with incorect digit_required.
    """
    dummy_field.data = "FOObar"

    with pytest.raises(ValidationError) as e:
        validator(dummy_form, dummy_field)
        assert str(e.value) == message
