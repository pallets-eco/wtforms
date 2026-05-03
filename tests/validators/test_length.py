import pytest

from wtforms.validators import length
from wtforms.validators import ValidationError


@pytest.mark.parametrize("min_v, max_v", [(2, 6), (6, -1), (-1, 6), (6, 6)])
def test_correct_length_passes(min_v, max_v, dummy_form, dummy_field):
    """
    It should pass for the string with correct length
    """
    dummy_field.data = "foobar"
    validator = length(min_v, max_v)
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize("min_v, max_v", [(7, -1), (-1, 5)])
def test_bad_length_raises(min_v, max_v, dummy_form, dummy_field):
    """
    It should raise ValidationError for string with incorrect length
    """
    dummy_field.data = "foobar"
    validator = length(min_v, max_v)
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "min_v, max_v",
    [(-1, -1), (5, 2)],  # none of the values is specified  # max should be gt min
)
def test_bad_length_init_raises(min_v, max_v):
    """
    It should raise AssertionError if the validator constructor got wrong values
    """
    with pytest.raises(AssertionError):
        length(min_v, max_v)


@pytest.mark.parametrize(
    ("validator", "message"),
    (
        (length(2, 5, "%(min)d and %(max)d"), "2 and 5"),
        (length(8, -1), "at least 8"),
        (length(-1, 5), "longer than 5"),
        (length(2, 5), "between 2 and 5"),
        (length(5, 5), "exactly 5"),
    ),
)
def test_length_messages(dummy_form, dummy_field, validator, message):
    """
    It should raise ValidationError for string with incorrect length
    """
    dummy_field.data = "foobar"

    with pytest.raises(ValidationError) as e:
        validator(dummy_form, dummy_field)

    assert message in str(e.value)
