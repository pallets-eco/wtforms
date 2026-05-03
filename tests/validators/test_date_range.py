from datetime import date
from datetime import datetime

import pytest

from wtforms.fields import DateField
from wtforms.fields import DateTimeLocalField
from wtforms.form import Form
from wtforms.validators import DateRange
from wtforms.validators import ValidationError


@pytest.mark.parametrize(
    ("min_v", "max_v", "test_v"),
    (
        (datetime(2023, 5, 23, 18), datetime(2023, 5, 25), date(2023, 5, 24)),
        (date(2023, 5, 24), datetime(2023, 5, 25), datetime(2023, 5, 24, 15)),
        (datetime(2023, 5, 24), None, date(2023, 5, 25)),
        (None, datetime(2023, 5, 25), datetime(2023, 5, 24)),
    ),
)
def test_date_range_passes(min_v, max_v, test_v, dummy_form, dummy_field):
    """Pass when data is within range."""
    dummy_field.data = test_v
    validator = DateRange(min_v, max_v)
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    ("min_v", "max_v", "test_v"),
    (
        (date(2023, 5, 24), date(2023, 5, 25), None),
        (datetime(2023, 5, 24, 18, 3), date(2023, 5, 25), None),
        (datetime(2023, 5, 24), datetime(2023, 5, 25), None),
        (datetime(2023, 5, 24), datetime(2023, 5, 25), datetime(2023, 5, 20)),
        (datetime(2023, 5, 24), datetime(2023, 5, 25), datetime(2023, 5, 26)),
        (datetime(2023, 5, 24), None, datetime(2023, 5, 23)),
        (None, datetime(2023, 5, 25), datetime(2023, 5, 26)),
    ),
)
def test_date_range_raises(min_v, max_v, test_v, dummy_form, dummy_field):
    """Raise when data is outside range."""
    dummy_field.data = test_v
    validator = DateRange(min_v, max_v)
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    ("min_v", "max_v", "min_flag", "max_flag"),
    (
        (
            datetime(2023, 5, 24),
            datetime(2023, 5, 25),
            datetime(2023, 5, 24),
            datetime(2023, 5, 25),
        ),
        (None, datetime(2023, 5, 25), None, datetime(2023, 5, 25)),
        (datetime(2023, 5, 24), None, datetime(2023, 5, 24), None),
    ),
)
def test_date_range_field_flags_are_set_date(min_v, max_v, min_flag, max_flag):
    """Keep static bounds in field flags."""
    validator = DateRange(min_v, max_v)
    assert validator.field_flags.get("min") == min_flag
    assert validator.field_flags.get("max") == max_flag


def test_date_range_sets_widget_attrs_using_field_format():
    """Render min and max using the field format."""

    class F(Form):
        date = DateField(
            validators=[DateRange(min=date(2023, 5, 24), max=date(2023, 5, 25))]
        )
        dt = DateTimeLocalField(
            format="%Y-%m-%dT%H:%M",
            validators=[
                DateRange(
                    min=datetime(2023, 5, 24, 15, 3),
                    max=datetime(2023, 5, 25, 0, 3),
                )
            ],
        )

    form = F()

    assert 'min="2023-05-24"' in form.date()
    assert 'max="2023-05-25"' in form.date()
    assert 'min="2023-05-24T15:03"' in form.dt()
    assert 'max="2023-05-25T00:03"' in form.dt()


def _dt_min():
    return datetime(2023, 5, 24, 15, 3)


def _d_min():
    return date(2023, 5, 24)


def _dt_max():
    return datetime(2023, 5, 25, 0, 3)


def _d_max():
    return date(2023, 5, 25)


@pytest.mark.parametrize(
    ("min_v", "max_v", "test_v"),
    (
        (_dt_min, _dt_max, datetime(2023, 5, 24, 15, 4)),
        (_d_min, _d_max, datetime(2023, 5, 24, 15, 4)),
        (_dt_min, None, datetime(2023, 5, 24, 15, 4)),
        (None, _dt_max, datetime(2023, 5, 24, 15, 2)),
        (None, _dt_max, date(2023, 5, 24)),
    ),
)
def test_date_range_passes_with_callable_bounds(
    min_v, max_v, test_v, dummy_form, dummy_field
):
    """Allow callable min and max bounds."""
    dummy_field.data = test_v
    validator = DateRange(min=min_v, max=max_v)
    validator(dummy_form, dummy_field)
