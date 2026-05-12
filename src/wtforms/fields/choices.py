import inspect
import warnings
from enum import Enum
from typing import NamedTuple

from wtforms import widgets
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
    A named tuple representing an available choice for choice fields.

    Field order matches the tuple shape yielded by ``iter_choices`` in
    WTForms 3.2 and earlier (``value, label, selected, render_kw``), so
    subclasses that unpack choices keep working.

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
    label: str | None = None
    selected: bool = False
    render_kw: dict | None = None

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


class SelectChoice(NamedTuple):
    """
    A :class:`Choice` augmented with an ``<optgroup>`` hint for
    :class:`SelectField`.

    :param optgroup:
        The ``<optgroup>`` HTML tag in which the option will be rendered.
    """

    value: str
    label: str | None = None
    selected: bool = False
    render_kw: dict | None = None
    optgroup: str | None = None

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
            warnings.warn(
                "Passing SelectField choices as tuples is deprecated and will be "
                "removed in wtforms 3.4. Please use Choice or SelectChoice instead.",
                DeprecationWarning,
                stacklevel=2,
            )
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
        """
        Provides data for choice widget rendering. Must return a sequence or
        iterable of SelectChoice.
        """
        raise NotImplementedError()

    def has_groups(self):
        """Whether the field's choices include any ``optgroup`` hint.

        Kept for compatibility with WTForms 3.2 subclasses that branch on
        grouped vs flat rendering. It will be removed in WTForms 4.0; new
        code should iterate :meth:`iter_choices` and inspect each
        :class:`SelectChoice` ``optgroup`` attribute directly.
        """
        return False

    def iter_groups(self):
        """Yield ``(group_label, [Choice, ...])`` pairs for grouped rendering.

        Kept for compatibility with WTForms 3.2 subclasses. It will be
        removed in WTForms 4.0; new code should iterate :meth:`iter_choices`
        and group on each :class:`SelectChoice` ``optgroup`` attribute.
        """
        raise NotImplementedError()

    def __iter__(self):
        opts = dict(
            widget=self.option_widget,
            validators=self.validators,
            name=self.name,
            render_kw=self.render_kw,
            _form=None,
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

    def choices_from_input(self, choices):
        if callable(choices):
            choices = self._invoke_choices_callback(choices)

        if choices is None:
            return None

        if isinstance(choices, dict):
            warnings.warn(
                "Passing SelectField choices in a dict deprecated and will be removed "
                "in wtforms 3.4. Please pass a list of SelectChoice objects with a "
                "custom optgroup attribute instead.",
                DeprecationWarning,
                stacklevel=2,
            )

            return [
                SelectChoice.from_input(input, optgroup)
                for optgroup, inputs in choices.items()
                for input in inputs
            ]

        return [SelectChoice.from_input(input) for input in choices]

    def _invoke_choices_callback(self, cb):
        try:
            sig = inspect.signature(cb)
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
            self.choices = self.choices_from_input(choices)
        self.validate_choice = validate_choice
        self.invalid_value_message = invalid_value_message or self.gettext(
            "Invalid Choice: could not coerce."
        )
        self.invalid_choice_message = invalid_choice_message or self.gettext(
            "Not a valid choice."
        )

    def iter_choices(self):
        choices = self.choices_from_input(self.choices) or []
        return [
            choice._replace(selected=self.coerce(choice.value) == self.data)
            for choice in choices
        ]

    def has_groups(self):
        choices = self.choices_from_input(self.choices) or []
        return any(c.optgroup is not None for c in choices)

    def iter_groups(self):
        groups = {}
        ungrouped = []
        for c in self.iter_choices():
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
            self.choices = self.choices_from_input(self._choices_callable)

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
        choices = self.choices_from_input(self.choices) or []
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
