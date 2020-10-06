import decimal

import pytest

from wtforms.validators import NumberRange
from wtforms.validators import ValidationError


@pytest.mark.parametrize(
    "min_v, max_v, test_v", [(5, 10, 7), (5, None, 7), (None, 100, 70)]
)
def test_number_range_passes(min_v, max_v, test_v, dummy_form, dummy_field):
    """
    It should pass if the test_v is between min_v and max_v
    """
    dummy_field.data = test_v
    validator = NumberRange(min_v, max_v)
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "min_v, max_v, test_v",
    [
        (5, 10, None),
        (5, 10, 0),
        (5, 10, 12),
        (5, 10, -5),
        (5, None, 4),
        (None, 100, 500),
    ],
)
def test_number_range_raises(min_v, max_v, test_v, dummy_form, dummy_field):
    """
    It should raise ValidationError if the test_v is not between min_v and max_v
    """
    dummy_field.data = test_v
    validator = NumberRange(min_v, max_v)
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


@pytest.mark.parametrize("nan", [float("NaN"), decimal.Decimal("NaN")])
def test_number_range_nan(nan, dummy_form, dummy_field):
    validator = NumberRange(0, 10)
    dummy_field.data = nan
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)
