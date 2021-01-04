import pytest

from wtforms.validators import lowercase_required
from wtforms.validators import ValidationError


@pytest.mark.parametrize("min_v", [2, 3, 4, 5, 6])
def test_correct_lowercase_required(min_v, dummy_form, dummy_field):
    """
    It should pass for the string with correct count of required lowercase letter.
    """
    dummy_field.data = "asdfghjkl"
    validator = lowercase_required(min_v)
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    ("validator", "message"),
    (
        (
            lowercase_required(2, "at least 2 lowercase letter"),
            "at least 2 lowercase letter",
        ),
        (lowercase_required(2), "at least 2 lowercase letter"),
    ),
)
def test_lowercase_required_messages(dummy_form, dummy_field, validator, message):
    """
    It should raise ValidationError for string with incorect lowercase_required.
    """
    dummy_field.data = "FOO123"

    with pytest.raises(ValidationError) as e:
        validator(dummy_form, dummy_field)
        assert str(e.value) == message
