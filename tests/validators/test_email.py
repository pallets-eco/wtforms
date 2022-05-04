import pytest

from wtforms.validators import email
from wtforms.validators import ValidationError


@pytest.mark.parametrize(
    "email_address",
    ["foo@bar.dk", "123@bar.dk", "foo@456.dk", "foo@bar456.info", "foo@bücher.中国"],
)
def test_valid_email_passes(email_address, dummy_form, dummy_field):
    """
    Valid email address should pass without raising
    """
    validator = email()
    dummy_field.data = email_address
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "email_address",
    [
        None,
        "",
        "  ",
        "foo",
        "bar.dk",
        "foo@",
        "@bar.dk",
        "foo@bar",
        "foo@bar.ab12",
        "foo@.bar.ab",
        "foo.@bar.co",
        "foo@foo@bar.co",
        "fo o@bar.co",
        "foo@bar.test",
    ],
)
def test_invalid_email_raises(email_address, dummy_form, dummy_field):
    """
    Bad email address should raise ValidationError
    """
    validator = email()
    dummy_field.data = email_address
    with pytest.raises(ValidationError) as e:
        validator(dummy_form, dummy_field)

    assert str(e.value) == "Invalid email address."


@pytest.mark.parametrize("email_address", ["foo@bar.test"])
def test_invalid_email_passes_in_test_environment(
    email_address, dummy_form, dummy_field
):
    """
    When test_environment=True email addresses with test domain should pass
    without raising
    """
    validator = email(test_environment=True)
    dummy_field.data = email_address
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "email_address,message",
    [
        ("foo@", "There must be something after the @-sign."),
        (
            "foo@bar.test",
            "The domain name bar.test is a special-use or reserved name"
            " that cannot be used with email.",
        ),
    ],
)
def test_invalid_email_raises_granular_message(
    email_address, message, dummy_form, dummy_field
):
    """
    When granular_message=True uses message from email_validator library.
    """
    validator = email(granular_message=True)
    dummy_field.data = email_address
    with pytest.raises(ValidationError) as e:
        validator(dummy_form, dummy_field)

    assert str(e.value) == message
