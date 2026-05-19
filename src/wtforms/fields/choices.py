import warnings
from dataclasses import dataclass
from dataclasses import field
from dataclasses import replace
from enum import Enum
from itertools import groupby
from operator import attrgetter
from typing import NamedTuple

from wtforms import widgets
from wtforms._compat import get_signature
from wtforms.fields.core import Field
from wtforms.validators import ValidationError

__all__ = (
    "SelectField",
    "Choice",
    "SelectChoice",
    "SelectMultipleField",
    "RadioField",
)


def _enum_coerce(enum_cls):
    def coerce(v):
        if isinstance(v, enum_cls):
            return v
        try:
            return enum_cls[v]
        except KeyError as e:
            raise ValueError(str(e)) from e

    return coerce


class Choice(NamedTuple):
    """
    A rendered option yielded by
    :meth:`SelectFieldBase.iter_choices` and
    :meth:`SelectFieldBase.iter_groups`.

    ``selected`` is computed against the field's current data. To
    declare options on a :class:`SelectField`, use
    :class:`SelectChoice` instead.

    :param value:
        The value that will be sent in the request.
    :param label:
        The label of the option.
    :param selected:
        Whether the option is currently selected. Set by ``iter_choices``;
        you rarely set this yourself.
    :param render_kw:
        A dict containing HTML attributes that will be rendered
        with the option.
    """

    value: str
    label: str
    selected: bool
    render_kw: dict


@dataclass
class SelectChoice:
    """
    An option declared via :class:`SelectField` and
    :class:`SelectMultipleField`'s ``choices=`` parameter.

    :param value:
        The value that will be sent in the request.
    :param label:
        The label of the option. Defaults to ``value`` when omitted.
    :param render_kw:
        A dict containing HTML attributes that will be rendered
        with the option. Defaults to an empty dict when omitted.
    :param optgroup:
        The ``<optgroup>`` HTML tag in which the option will be rendered.
    """

    value: str
    label: str | None = None
    render_kw: dict = field(default_factory=dict)
    optgroup: str | None = None

    def __post_init__(self):
        if self.label is None:
            self.label = self.value

    def __iter__(self):
        return iter((self.value, self.label, self.render_kw, self.optgroup))

    @classmethod
    def from_enum(cls, enum_cls, *, label=None):
        """Build a list of choices from an :class:`enum.Enum` class.

        The HTML value of each option is the item ``name``. The label
        defaults to ``str(item)`` when the Enum defines its own
        ``__str__``, otherwise to ``item.name``. Pass ``label=`` (a
        callable taking an item) to override.
        """
        if label is None:
            label = str if "__str__" in enum_cls.__dict__ else lambda m: m.name
        return [cls(value=m.name, label=label(m)) for m in enum_cls]

    @classmethod
    def from_input(cls, input, optgroup=None):
        """Coerce a value passed by the user via ``choices=...`` into a
        :class:`SelectChoice`.
        """
        if isinstance(input, SelectChoice):
            if optgroup:
                return replace(input, optgroup=optgroup)
            return input

        if isinstance(input, Choice):
            warnings.warn(
                "Passing Choice to a SelectField is deprecated; Choice is the "
                "output type returned by iter_choices(). Use SelectChoice "
                "instead. Support for Choice as input will be removed in "
                "WTForms 4.0.",
                DeprecationWarning,
                stacklevel=4,
            )
            return cls(
                value=input.value,
                label=input.label,
                render_kw=input.render_kw,
                optgroup=optgroup,
            )

        if isinstance(input, str):
            return cls(value=input, optgroup=optgroup)

        if isinstance(input, tuple):
            if len(input) == 2:
                value, label = input
                return cls(value=value, label=label, optgroup=optgroup)
            if len(input) == 3:
                value, label, render_kw = input
                return cls(
                    value=value, label=label, render_kw=render_kw, optgroup=optgroup
                )
            return cls(*input, optgroup=optgroup)


class SelectFieldBase(Field):
    option_widget = widgets.Option()

    """
    Base class for fields which can be iterated to produce options.

    This isn't a field, but an abstract base class for fields which want to
    provide this functionality.
    """

    def __init__(self, label=None, validators=None, option_widget=None, **kwargs):
        super().__init__(label, validators, **kwargs)

        if option_widget is not None:
            self.option_widget = option_widget

    def iter_choices(self):
        """Provide data for choice widget rendering.

        Should yield :class:`Choice` instances.
        """
        raise NotImplementedError()

    def has_groups(self):
        """Whether the field's choices include any ``optgroup`` hint."""
        return False

    def iter_groups(self):
        """Yield ``(group_label, [Choice, ...])`` pairs for grouped rendering."""
        raise NotImplementedError()

    def __iter__(self):
        opts = dict(
            widget=self.option_widget,
            validators=self.validators,
            name=self.name,
            render_kw=self.render_kw,
            _form=self._form,
            _meta=self.meta,
        )
        for i, choice in enumerate(self.iter_choices()):
            opt = self._Option(
                id=f"{self.id}-{i}",
                label=choice.label or choice.value,
                **opts,
            )
            opt.choice = choice
            opt.checked = choice.selected
            opt.process(None, choice.value)
            yield opt

    def _choices_from_input(self, choices):
        """Parse the user-supplied ``choices`` into a list of :class:`SelectChoice`."""
        if callable(choices):
            choices = self._invoke_choices_callback(choices)

        if choices is None:
            return None

        if isinstance(choices, dict):
            return [
                SelectChoice.from_input(input, optgroup)
                for optgroup, inputs in choices.items()
                for input in inputs
            ]

        return [SelectChoice.from_input(input) for input in choices]

    def _invoke_choices_callback(self, cb):
        try:
            sig = get_signature(cb)
        except (ValueError, TypeError):
            return cb()
        try:
            sig.bind(self._form, self)
        except TypeError:
            return cb()
        return cb(self._form, self)

    class _Option(Field):
        def _value(self):
            return str(self.data)


class SelectField(SelectFieldBase):
    widget = widgets.Select()

    def __init__(
        self,
        label=None,
        validators=None,
        coerce=str,
        choices=None,
        validate_choice=True,
        invalid_value_message=None,
        invalid_choice_message=None,
        **kwargs,
    ):
        super().__init__(label, validators, **kwargs)
        if isinstance(coerce, type) and issubclass(coerce, Enum):
            coerce = _enum_coerce(coerce)
        self.coerce = coerce
        if callable(choices):
            self._choices_callable = choices
            self.choices = None
        else:
            self._choices_callable = None
            self.choices = self._choices_from_input(choices)
        self.validate_choice = validate_choice
        self.invalid_value_message = invalid_value_message or self.gettext(
            "Invalid Choice: could not coerce."
        )
        self.invalid_choice_message = invalid_choice_message or self.gettext(
            "Not a valid choice."
        )

    def iter_choices(self):
        choices = self._choices_from_input(self.choices) or []
        return [
            Choice(
                value=c.value,
                label=c.label,
                selected=self.coerce(c.value) == self.data,
                render_kw=c.render_kw,
            )
            for c in choices
        ]

    def has_groups(self):
        choices = self._choices_from_input(self.choices) or []
        return any(c.optgroup is not None for c in choices)

    def iter_groups(self):
        choices = self._choices_from_input(self.choices) or []
        for optgroup, group in groupby(choices, key=attrgetter("optgroup")):
            yield (
                optgroup,
                [
                    Choice(
                        value=c.value,
                        label=c.label,
                        selected=self.coerce(c.value) == self.data,
                        render_kw=c.render_kw,
                    )
                    for c in group
                ],
            )

    def post_process(self):
        super().post_process()
        if self._choices_callable is not None:
            self.choices = self._invoke_choices_callback(self._choices_callable)

    def process_data(self, value):
        try:
            # If value is None, don't coerce to a value
            self.data = self.coerce(value) if value is not None else None
        except (ValueError, TypeError):
            self.data = None

    def process_formdata(self, valuelist):
        if not valuelist:
            return

        try:
            self.data = self.coerce(valuelist[0])
        except ValueError as exc:
            raise ValueError(self.invalid_value_message) from exc

    def pre_validate(self, form):
        if self.process_errors:
            return

        if not self.validate_choice:
            return

        if self.choices is None:
            raise TypeError(self.gettext("Choices cannot be None."))

        if not any(choice.selected for choice in self.iter_choices()):
            raise ValidationError(self.invalid_choice_message)


class SelectMultipleField(SelectField):
    """
    No different from a normal select field, except this one can take (and
    validate) multiple choices. You'll need to specify the HTML
    :mdn-attr:`size` attribute on the :mdn-tag:`select` field when rendering.

    ``invalid_choice_message`` may be a string, or a callable taking the
    number of invalid submitted values and returning the message. The
    returned message must contain ``%(value)s``, which is replaced with the
    comma-separated list of unacceptable values.
    """

    widget = widgets.Select(multiple=True)

    def __init__(
        self,
        label=None,
        validators=None,
        coerce=str,
        choices=None,
        validate_choice=True,
        invalid_value_message=None,
        invalid_choice_message=None,
        **kwargs,
    ):
        super().__init__(
            label,
            validators,
            coerce=coerce,
            choices=choices,
            validate_choice=validate_choice,
            **kwargs,
        )
        self.invalid_value_message = invalid_value_message or self.gettext(
            "Invalid choice(s): one or more data inputs could not be coerced."
        )
        self.invalid_choice_message = invalid_choice_message

    def iter_choices(self):
        choices = self._choices_from_input(self.choices) or []
        data = self.data or ()
        return [
            Choice(
                value=c.value,
                label=c.label,
                selected=self.coerce(c.value) in data,
                render_kw=c.render_kw,
            )
            for c in choices
        ]

    def iter_groups(self):
        choices = self._choices_from_input(self.choices) or []
        data = self.data or ()
        for optgroup, group in groupby(choices, key=attrgetter("optgroup")):
            yield (
                optgroup,
                [
                    Choice(
                        value=c.value,
                        label=c.label,
                        selected=self.coerce(c.value) in data,
                        render_kw=c.render_kw,
                    )
                    for c in group
                ],
            )

    def process_data(self, value):
        try:
            self.data = list(self.coerce(v) for v in value)
        except (ValueError, TypeError):
            self.data = None

    def process_formdata(self, valuelist):
        try:
            self.data = list(self.coerce(x) for x in valuelist)
        except ValueError as exc:
            raise ValueError(self.invalid_value_message) from exc

    def pre_validate(self, form):
        if self.process_errors:
            return

        if not self.validate_choice or not self.data:
            return

        if self.choices is None:
            raise TypeError(self.gettext("Choices cannot be None."))

        acceptable = {self.coerce(choice.value) for choice in self.iter_choices()}
        if any(data not in acceptable for data in self.data):
            unacceptable = [
                str(data) for data in set(self.data) if data not in acceptable
            ]
            if callable(self.invalid_choice_message):
                message = self.invalid_choice_message(len(unacceptable))
            elif self.invalid_choice_message is not None:
                message = self.invalid_choice_message
            else:
                message = self.ngettext(
                    "'%(value)s' is not a valid choice for this field.",
                    "'%(value)s' are not valid choices for this field.",
                    len(unacceptable),
                )
            raise ValidationError(message % dict(value="', '".join(unacceptable)))


class RadioField(SelectField):
    """
    Like a SelectField, except displays a list of :mdn-input:`radio` buttons.

    Iterating the field will produce subfields (each containing a label as
    well) in order to allow custom rendering of the individual radio fields.
    """

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.RadioInput()

    def __init__(self, label=None, validators=None, **kwargs):
        super().__init__(label, validators, **kwargs)
        self.label.field_id = False
