import pytest

from wtforms.validators import input_required
from wtforms.validators import StopValidation


def test_input_required(dummy_form, dummy_field):
    """
    it should pass if the required value is present
    """
    validator = input_required()
    dummy_field.data = "foobar"
    dummy_field.raw_data = ["foobar"]

    validator(dummy_form, dummy_field)
    assert validator.field_flags == {"required": True}


def test_input_required_raises(dummy_form, dummy_field):
    """
    It should stop the validation chain if the required value is not present
    """
    validator = input_required()
    dummy_field.data = ""
    dummy_field.raw_data = [""]
    with pytest.raises(StopValidation):
        validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    ("validator", "message"),
    (
        (input_required(), "This field is required."),
        (input_required(message="foo"), "foo"),
    ),
)
def test_input_required_error_message(dummy_form, dummy_field, validator, message):
    """
    It should return error message when the required value is not present
    """
    dummy_field.data = ""
    dummy_field.raw_data = [""]

    with pytest.raises(StopValidation) as e:
        validator(dummy_form, dummy_field)

    assert str(e.value) == message
