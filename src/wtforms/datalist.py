import warnings
from dataclasses import dataclass
from dataclasses import field

from wtforms import widgets
from wtforms._compat import get_signature
from wtforms.fields.choices import Choice

__all__ = ("DataList", "DataListChoice")


@dataclass
class DataListChoice:
    """
    An option declared via :class:`~wtforms.DataList`'s ``choices=``
    parameter.

    :param value:
        The value rendered as the ``<option>``'s ``value`` attribute.
    :param label:
        The label of the option. Defaults to ``value`` when omitted.
    :param render_kw:
        A dict containing HTML attributes that will be rendered
        with the option. Defaults to an empty dict when omitted.
    """

    value: str
    label: str | None = None
    render_kw: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.label is None:
            self.label = self.value

    def __iter__(self):
        return iter((self.value, self.label, self.render_kw))

    @classmethod
    def from_enum(cls, enum_cls, *, label=None):
        """Build a list of choices from an :class:`enum.Enum` class.

        See :meth:`SelectChoice.from_enum` for details.
        """
        if label is None:
            label = str if "__str__" in enum_cls.__dict__ else lambda m: m.name
        return [cls(value=m.name, label=label(m)) for m in enum_cls]

    @classmethod
    def from_input(cls, input):
        """Coerce a value passed by the user into a :class:`DataListChoice`."""
        if isinstance(input, DataListChoice):
            return input

        if isinstance(input, Choice):
            warnings.warn(
                "Passing Choice to a DataList is deprecated; Choice is the "
                "output type returned by iter_choices(). Use DataListChoice "
                "instead. Support for Choice as input will be removed in "
                "WTForms 4.0.",
                DeprecationWarning,
                stacklevel=4,
            )
            return cls(
                value=input.value,
                label=input.label,
                render_kw=input.render_kw,
            )

        if isinstance(input, str):
            return cls(value=input)

        if isinstance(input, tuple):
            return cls(*input)


class DataList:
    """A ``<datalist>`` of suggestions attached to a single field.

    Passed to a :class:`~wtforms.Field` via its ``datalist=`` parameter
    to add an autocomplete-style list of choices. See the WTForms
    fields documentation for usage.
    """

    widget = widgets.DataListWidget()

    def __init__(self, choices=None, *, render_kw=None, widget=None):
        self._raw_choices = choices
        self._choices = None if callable(choices) else choices
        self.render_kw = render_kw or {}
        if widget is not None:
            self.widget = widget
        self.id = None

    def _clone(self, id):
        clone = DataList.__new__(DataList)
        clone._raw_choices = self._raw_choices
        clone._choices = None if callable(self._raw_choices) else self._raw_choices
        clone.render_kw = self.render_kw
        clone.widget = self.widget
        clone.id = id
        return clone

    def _resolve(self, field):
        raw = self._raw_choices
        if not callable(raw):
            return
        try:
            sig = get_signature(raw)
            sig.bind(field._form, field)
        except TypeError:
            self._choices = raw()
            return
        self._choices = raw(field._form, field)

    def iter_choices(self, field=None):
        raw = self._choices
        if raw is None:
            return []
        return [DataListChoice.from_input(item) for item in raw]

    def __call__(self, field=None, **kwargs):
        return self.widget(self, field=field, **kwargs)
