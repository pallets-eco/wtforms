import inspect

from wtforms import widgets
from wtforms.fields.choices import Choice

__all__ = ("DataList",)


class DataList:
    """A ``<datalist>`` of suggestions attached to a single field.

    Passed to a :class:`~wtforms.Field` via its ``datalist=`` parameter
    to add an autocomplete-style list of choices. See the WTForms
    fields documentation for usage.
    """

    widget = widgets.DataListWidget()

    def __init__(self, choices=None, *, render_kw=None, widget=None):
        self._raw_choices = choices
        self.render_kw = render_kw or {}
        if widget is not None:
            self.widget = widget
        self.id = None

    def _clone(self, id):
        clone = DataList.__new__(DataList)
        clone._raw_choices = self._raw_choices
        clone.render_kw = self.render_kw
        clone.widget = self.widget
        clone.id = id
        return clone

    def iter_choices(self, field=None):
        raw = self._raw_choices
        if callable(raw):
            n = len(inspect.signature(raw).parameters)
            raw = raw(field) if n >= 1 else raw()
        if raw is None:
            return []
        choices = [
            item if isinstance(item, Choice) else Choice(value=item) for item in raw
        ]
        value = field.data if field is not None else None
        if value is not None:
            for choice in choices:
                if choice.value == value:
                    choice._selected = True
        return choices

    def __call__(self, field=None, **kwargs):
        return self.widget(self, field=field, **kwargs)
