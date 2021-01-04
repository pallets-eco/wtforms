import pytest

from wtforms.validators import symbol_required
from wtforms.validators import ValidationError


@pytest.mark.parametrize("min_v", [2, 3, 4, 5, 6])
def test_correct_symbol_required(min_v, dummy_form, dummy_field):
    """
    It should pass for the string with correct count of required symbol.
    """
    dummy_field.data = "-A%s^D*f(G87KJ@hg8J.&"
    validator = symbol_required(min_v)
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    ("validator", "message"),
    (
        (
            symbol_required(2, "at least 2 symbol"),
            "at least 2 symbol letter",
        ),
        (symbol_required(2), "at least 2 symbol"),
    ),
)
def test_symbol_required_messages(dummy_form, dummy_field, validator, message):
    """
    It should raise ValidationError for string with incorect symbol_required.
    """
    dummy_field.data = "foo123Bar"

    with pytest.raises(ValidationError) as e:
        validator(dummy_form, dummy_field)
        assert str(e.value) == message
