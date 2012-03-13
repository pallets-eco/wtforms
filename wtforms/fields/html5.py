import wtforms.widgets.html5 as widgets

import core


class SearchField(core.StringField):
    """
    Represents an ``<input type="search">``.
    """
    widget = widgets.SearchInput()


class TelField(core.StringField):
    """
    Represents an ``<input type="tel">``.
    """
    widget = widgets.TelInput()


class URLField(core.StringField):
    """
    Represents an ``<input type="url">``.
    """
    widget = widgets.URLInput()


class EmailField(core.StringField):
    """
    Represents an ``<input type="email">``.
    """
    widget = widgets.EmailInput()


class DateTimeField(core.DateTimeField):
    """
    Represents an ``<input type="datetime">``.
    """
    widget = widgets.DateTimeInput()


class DateField(core.DateField):
    """
    Represents an ``<input type="date">``.
    """
    widget = widgets.DateInput()


class DateTimeLocalField(core.DateTimeField):
    """
    Represents an ``<input type="datetime-local">``.
    """
    widget = widgets.DateTimeLocalInput()


class IntegerField(core.IntegerField):
    """
    Represents an ``<input type="number">``.
    """
    widget = widgets.NumberInput()


class DecimalField(core.DecimalField):
    """
    Represents an ``<input type="number">``.
    """
    widget = widgets.NumberInput()


class IntegerRangeField(core.IntegerField):
    """
    Represents an ``<input type="range">``.
    """
    widget = widgets.RangeInput()


class DecimalRangeField(core.DecimalField):
    """
    Represents an ``<input type="range">``.
    """
    widget = widgets.RangeInput()

