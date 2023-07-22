import pytest

from wtforms.validators import data_required
from wtforms.validators import StopValidation


def test_data_required(dummy_form, dummy_field):
    """
    Should pass if the required data are present
    """
    validator = data_required()
    dummy_field.data = "foobar"
    validator(dummy_form, dummy_field)
    assert validator.field_flags == {"required": True}


@pytest.mark.parametrize("bad_val", [None, "", " ", "\t\t"])
def test_data_required_raises(bad_val, dummy_form, dummy_field):
    """
    data_required should stop the validation chain if data are not present
    """
    validator = data_required()
    dummy_field.data = bad_val
    with pytest.raises(StopValidation):
        validator(dummy_form, dummy_field)


def test_data_required_clobber(dummy_form, dummy_field):
    """
    Data required should clobber the errors
    """
    validator = data_required()
    dummy_field.data = ""
    dummy_field.errors = ["Invalid Integer Value"]
    assert len(dummy_field.errors) == 1
    with pytest.raises(StopValidation):
        validator(dummy_form, dummy_field)

    assert len(dummy_field.errors) == 0


@pytest.mark.parametrize(
    ("validator", "message"),
    (
        (data_required(), "This field is required."),
        (data_required(message="foo"), "foo"),
    ),
)
def test_data_required_messages(dummy_form, dummy_field, validator, message):
    """
    Check data_required message and custom message
    """
    dummy_field.data = ""

    with pytest.raises(StopValidation) as e:
        validator(dummy_form, dummy_field)

    assert str(e.value) == message


def test_required_passes(dummy_form, dummy_field):
    """
    It should pass when required value is present
    """
    validator = data_required()
    dummy_field.data = "foobar"
    validator(dummy_form, dummy_field)


def test_required_stops_validation(dummy_form, dummy_field):
    """
    It should raise stop the validation chain if required value is not present
    """
    validator = data_required()
    dummy_field.data = ""
    with pytest.raises(StopValidation):
        validator(dummy_form, dummy_field)
