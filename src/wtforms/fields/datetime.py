import datetime

from wtforms import widgets
from wtforms.fields.core import Field
from wtforms.utils import clean_datetime_format_for_strptime

__all__ = (
    "DateTimeField",
    "DateField",
    "TimeField",
    "MonthField",
    "DateTimeLocalField",
)


class DateTimeField(Field):
    """
    A text field which stores a `datetime.datetime` matching a format.
    """

    widget = widgets.DateTimeInput()

    def __init__(
        self, label=None, validators=None, format="%Y-%m-%d %H:%M:%S", **kwargs
    ):
        super().__init__(label, validators, **kwargs)
        self.format = format
        self.strptime_format = clean_datetime_format_for_strptime(format)

    def _value(self):
        if self.raw_data:
            return " ".join(self.raw_data)
        return self.data and self.data.strftime(self.format) or ""

    def process_formdata(self, valuelist):
        if not valuelist:
            return

        date_str = " ".join(valuelist)
        try:
            self.data = datetime.datetime.strptime(date_str, self.strptime_format)
        except ValueError as exc:
            self.data = None
            raise ValueError(self.gettext("Not a valid datetime value.")) from exc


class DateField(DateTimeField):
    """
    Same as DateTimeField, except stores a `datetime.date`.
    """

    widget = widgets.DateInput()

    def __init__(self, label=None, validators=None, format="%Y-%m-%d", **kwargs):
        super().__init__(label, validators, format, **kwargs)

    def process_formdata(self, valuelist):
        if not valuelist:
            return

        date_str = " ".join(valuelist)
        try:
            self.data = datetime.datetime.strptime(
                date_str, self.strptime_format
            ).date()
        except ValueError as exc:
            self.data = None
            raise ValueError(self.gettext("Not a valid date value.")) from exc


class TimeField(DateTimeField):
    """
    Same as DateTimeField, except stores a `time`.
    """

    widget = widgets.TimeInput()

    def __init__(self, label=None, validators=None, format="%H:%M", **kwargs):
        super().__init__(label, validators, format, **kwargs)

    def process_formdata(self, valuelist):
        if not valuelist:
            return

        time_str = " ".join(valuelist)
        try:
            self.data = datetime.datetime.strptime(
                time_str, self.strptime_format
            ).time()
        except ValueError as exc:
            self.data = None
            raise ValueError(self.gettext("Not a valid time value.")) from exc


class MonthField(DateField):
    """
    Same as DateField, except represents a month, stores a `datetime.date`
    with `day = 1`.
    """

    widget = widgets.MonthInput()

    def __init__(self, label=None, validators=None, format="%Y-%m", **kwargs):
        super().__init__(label, validators, format, **kwargs)


class DateTimeLocalField(DateTimeField):
    """
    Represents an ``<input type="datetime-local">``.
    """

    widget = widgets.DateTimeLocalInput()
