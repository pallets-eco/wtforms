import warnings
from dataclasses import dataclass
from dataclasses import field
from dataclasses import replace

from wtforms import widgets
from wtforms.fields.choices import _enum_options
from wtforms.fields.choices import _invoke_choices_callable
from wtforms.fields.choices import Choice

__all__ = ("DataList", "DataListChoice", "enum_datalist")


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


def enum_datalist(enum_cls, *, by="value", label=None):
    """Build a list of :class:`DataListChoice` from an :class:`enum.Enum` class.

    Same semantics as :func:`~wtforms.fields.enum_choices`: ``by`` selects
    which member attribute becomes the ``<option>`` value (``"value"`` by
    default, ``"name"`` otherwise) and ``label`` defaults to ``str(member)``
    when the Enum defines its own ``__str__`` or is a :class:`enum.StrEnum`,
    else ``member.name``.

    A ``<datalist>`` only suggests values for a free-text field, so there is
    no coercion counterpart — the field stores whatever string is submitted.
    """
    return _enum_options(enum_cls, by, label, DataListChoice)


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
        self._field = None
        self.render_kw = render_kw or {}
        if widget is not None:
            self.widget = widget
        self.id = None

    def _clone(self, id):
        clone = DataList.__new__(DataList)
        clone._raw_choices = self._raw_choices
        clone._choices = None if callable(self._raw_choices) else self._raw_choices
        clone._field = None
        clone.render_kw = dict(self.render_kw)
        clone.widget = self.widget
        clone.id = id
        return clone

    def _invalidate(self, field):
        """Mark the choices for a lazy refresh on the next :meth:`iter_choices`."""
        if callable(self._raw_choices):
            self._field = field

    def iter_choices(self, field=None):
        if (bound := self._field) is not None:
            self._field = None
            self._choices = _invoke_choices_callable(
                self._raw_choices, bound._form, bound
            )
        raw = self._choices
        if raw is None:
            return []
        if isinstance(raw, dict):
            return [
                DataListChoice(value=value, label=label) for value, label in raw.items()
            ]
        return [
            replace(choice, render_kw=dict(choice.render_kw or {}))
            for choice in map(DataListChoice.from_input, raw)
        ]

    def __call__(self, field=None, **kwargs):
        return self.widget(self, field=field, **kwargs)
