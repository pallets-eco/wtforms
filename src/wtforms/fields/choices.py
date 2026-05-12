import inspect
import warnings
from enum import Enum
from typing import NamedTuple

from wtforms import widgets
from wtforms.fields.core import Field
from wtforms.validators import ValidationError

try:
    from annotationlib import Format

    _signature_kwargs = {"annotation_format": Format.FORWARDREF}
except ImportError:
    _signature_kwargs = {}

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


class _Choice(NamedTuple):
    value: str
    label: str | None = None
    selected: bool = False
    render_kw: dict | None = None


class Choice(_Choice):
    """
    A named tuple representing an available choice for choice fields.

    :param value:
        The value that will be sent in the request.
    :param label:
        The label of the option. Defaults to ``value`` when omitted.
    :param selected:
        Whether the option is currently selected. Set by ``iter_choices``;
        you rarely set this yourself.
    :param render_kw:
        A dict containing HTML attributes that will be rendered
        with the option. Defaults to an empty dict when omitted.
    """

    __slots__ = ()

    def __new__(cls, value, label=None, selected=False, render_kw=None):
        if label is None:
            label = value
        if render_kw is None:
            render_kw = {}
        return _Choice.__new__(cls, value, label, selected, render_kw)

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


class _SelectChoice(NamedTuple):
    value: str
    label: str | None = None
    selected: bool = False
    render_kw: dict | None = None
    optgroup: str | None = None


class SelectChoice(_SelectChoice):
    """
    A :class:`Choice` augmented with an ``<optgroup>`` hint for
    :class:`SelectField`.

    :param optgroup:
        The ``<optgroup>`` HTML tag in which the option will be rendered.
    """

    __slots__ = ()

    def __new__(cls, value, label=None, selected=False, render_kw=None, optgroup=None):
        if label is None:
            label = value
        if render_kw is None:
            render_kw = {}
        return _SelectChoice.__new__(cls, value, label, selected, render_kw, optgroup)

    @classmethod
    def from_enum(cls, enum_cls, *, label=None):
        """Build a list of choices from an :class:`enum.Enum` class.

        See :meth:`Choice.from_enum` for details.
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
                return input._replace(optgroup=optgroup)
            return input

        if isinstance(input, Choice):
            return cls(
                value=input.value,
                label=input.label,
                selected=input.selected,
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

    @classmethod
    def _normalize_choice(cls, choice):
        """Coerce a value yielded by :meth:`SelectFieldBase.iter_choices`
        into a :class:`SelectChoice`.
        """
        if isinstance(choice, cls):
            return choice
        if isinstance(choice, Choice):
            return cls.from_input(choice)
        if isinstance(choice, tuple):
            warnings.warn(
                "Yielding raw tuples from iter_choices() is deprecated; "
                "yield SelectChoice instances instead. Will be removed in "
                "WTForms 4.0.",
                DeprecationWarning,
                stacklevel=3,
            )
            if len(choice) == 4:
                value, label, selected, render_kw = choice
            elif len(choice) == 3:
                value, label, selected = choice
                render_kw = None
            else:
                raise TypeError(
                    f"iter_choices() yielded a tuple of unsupported length: "
                    f"{len(choice)}"
                )
            return cls(value=value, label=label, selected=selected, render_kw=render_kw)
        raise TypeError(
            f"iter_choices() yielded an unsupported type: {type(choice).__name__}"
        )


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

        Should yield :class:`SelectChoice` instances.
        """
        raise NotImplementedError()

    def _iter_choices_normalized(self):
        """Wrap :meth:`iter_choices` to always yield :class:`SelectChoice`."""
        for choice in self.iter_choices():
            yield SelectChoice._normalize_choice(choice)

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
        for i, choice in enumerate(self._iter_choices_normalized()):
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

    @staticmethod
    def _warn_legacy_choices(choices):
        """Emit a one-shot ``DeprecationWarning`` for legacy ``choices`` shapes.

        Legacy shapes are raw tuples or ``dict``.
        """
        if isinstance(choices, dict):
            warnings.warn(
                "Passing SelectField choices in a dict deprecated and will be "
                "removed in wtforms 3.4. Please pass a list of SelectChoice "
                "objects with a custom optgroup attribute instead.",
                DeprecationWarning,
                stacklevel=3,
            )
            items = (i for v in choices.values() for i in v)
        else:
            items = choices
        for item in items:
            if isinstance(item, tuple) and not isinstance(item, (Choice, SelectChoice)):
                warnings.warn(
                    "Passing SelectField choices as tuples is deprecated and "
                    "will be removed in wtforms 3.4. Please use Choice or "
                    "SelectChoice instead.",
                    DeprecationWarning,
                    stacklevel=3,
                )
                return

    def _invoke_choices_callback(self, cb):
        try:
            sig = inspect.signature(cb, **_signature_kwargs)
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
            if choices is None:
                self.choices = None
            else:
                self._warn_legacy_choices(choices)
                self.choices = (
                    dict(choices) if isinstance(choices, dict) else list(choices)
                )
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
            choice._replace(selected=self.coerce(choice.value) == self.data)
            for choice in choices
        ]

    def has_groups(self):
        choices = self._choices_from_input(self.choices) or []
        return any(c.optgroup is not None for c in choices)

    def iter_groups(self):
        groups = {}
        ungrouped = []
        for c in self._iter_choices_normalized():
            item = Choice(c.value, c.label, c.selected, c.render_kw)
            if c.optgroup is None:
                ungrouped.append(item)
            else:
                groups.setdefault(c.optgroup, []).append(item)
        yield from groups.items()
        if ungrouped:
            yield None, ungrouped

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

        if not any(choice.selected for choice in self._iter_choices_normalized()):
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
        if not self.data:
            return choices
        return [
            choice._replace(selected=self.coerce(choice.value) in self.data)
            for choice in choices
        ]

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

        acceptable = {
            self.coerce(choice.value) for choice in self._iter_choices_normalized()
        }
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
