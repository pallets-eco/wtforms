from markupsafe import escape
from markupsafe import Markup

__all__ = (
    "CheckboxInput",
    "ColorInput",
    "DateInput",
    "DateTimeInput",
    "DateTimeLocalInput",
    "EmailInput",
    "FileInput",
    "HiddenInput",
    "ListWidget",
    "MonthInput",
    "NumberInput",
    "Option",
    "PasswordInput",
    "RadioInput",
    "RangeInput",
    "SearchInput",
    "Select",
    "SubmitInput",
    "TableWidget",
    "TextArea",
    "TextInput",
    "TelInput",
    "TimeInput",
    "URLInput",
    "WeekInput",
)


def clean_key(key):
    key = key.rstrip("_")
    if key.startswith("data_") or key.startswith("aria_"):
        key = key.replace("_", "-")
    return key


def html_params(**kwargs):
    """
    Generate HTML attribute syntax from inputted keyword arguments.

    The output value is sorted by the passed keys, to provide consistent output
    each time this function is called with the same parameters. Because of the
    frequent use of the normally reserved keywords `class` and `for`, suffixing
    these with an underscore will allow them to be used.

    In order to facilitate the use of ``data-`` and ``aria-`` attributes, if the
    name of the attribute begins with ``data_`` or ``aria_``, then every
    underscore will be replaced with a hyphen in the generated attribute.

    >>> html_params(data_attr='user.name', aria_labeledby='name')
    'data-attr="user.name" aria-labeledby="name"'

    In addition, the values ``True`` and ``False`` are special:
      * ``attr=True`` generates the HTML compact output of a boolean attribute,
        e.g. ``checked=True`` will generate simply ``checked``
      * ``attr=False`` will be ignored and generate no output.

    >>> html_params(name='text1', id='f', class_='text')
    'class="text" id="f" name="text1"'
    >>> html_params(checked=True, readonly=False, name="text1", abc="hello")
    'abc="hello" checked name="text1"'

    .. versionchanged:: 3.0
        ``aria_`` args convert underscores to hyphens like ``data_``
        args.

    .. versionchanged:: 2.2
        ``data_`` args convert all underscores to hyphens, instead of
        only the first one.
    """
    params = []
    for k, v in sorted(kwargs.items()):
        k = clean_key(k)
        if v is True:
            params.append(k)
        elif v is False:
            pass
        else:
            params.append(f'{str(k)}="{escape(v)}"')  # noqa: B907
    return " ".join(params)


class ListWidget:
    """
    Render a list of fields as a :mdn-tag:`ul` or :mdn-tag:`ol`.

    This is used for fields which encapsulate many inner fields as subfields.
    The widget will try to iterate the field to get access to the subfields and
    call them to render them.

    If `prefix_label` is set, the subfield's label is printed before the field,
    otherwise afterwards. The latter is useful for iterating radios or
    checkboxes.
    """

    def __init__(self, html_tag="ul", prefix_label=True):
        assert html_tag in ("ol", "ul")
        self.html_tag = html_tag
        self.prefix_label = prefix_label

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        html = [f"<{self.html_tag} {html_params(**kwargs)}>"]
        for subfield in field:
            if self.prefix_label:
                html.append(f"<li>{subfield.label} {subfield()}</li>")
            else:
                html.append(f"<li>{subfield()} {subfield.label}</li>")
        html.append(f"</{self.html_tag}>")
        return Markup("".join(html))


class TableWidget:
    """
    Render a list of fields as a :mdn-tag:`table`.

    If `with_table_tag` is True, then an enclosing :mdn-tag:`table` is placed
    around the rows.

    Hidden fields will not be displayed with a row, instead the field will be
    pushed into a subsequent table row to ensure XHTML validity. Hidden fields
    at the end of the field list will appear outside the table.
    """

    def __init__(self, with_table_tag=True):
        self.with_table_tag = with_table_tag

    def __call__(self, field, **kwargs):
        html = []
        if self.with_table_tag:
            kwargs.setdefault("id", field.id)
            table_params = html_params(**kwargs)
            html.append(f"<table {table_params}>")
        hidden = ""
        for subfield in field:
            if subfield.type in ("HiddenField", "CSRFTokenField"):
                hidden += str(subfield)
            else:
                html.append(
                    f"<tr><th>{subfield.label}</th><td>{hidden}{subfield}</td></tr>"
                )
                hidden = ""
        if self.with_table_tag:
            html.append("</table>")
        if hidden:
            html.append(hidden)
        return Markup("".join(html))


class Input:
    """
    Render a basic :mdn-tag:`input` field.

    This is used as the basis for most of the other input fields.

    By default, the `_value()` method will be called upon the associated field
    to provide the ``value=`` HTML attribute.
    """

    html_params = staticmethod(html_params)

    def __init__(self, input_type=None):
        if input_type is not None:
            self.input_type = input_type

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("type", self.input_type)
        if "value" not in kwargs:
            kwargs["value"] = field._value()
        flags = getattr(field, "flags", {})
        for k in dir(flags):
            if k in self.validation_attrs and k not in kwargs:
                kwargs[k] = getattr(flags, k)
        input_params = self.html_params(name=field.name, **kwargs)
        return Markup(f"<input {input_params}>")


class TextInput(Input):
    """
    Render a single-line :mdn-input:`text`.
    """

    input_type = "text"
    validation_attrs = [
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
        "pattern",
    ]


class PasswordInput(Input):
    """
    Render an :mdn-input:`password`.

    For security purposes, this field will not reproduce the value on a form
    submit by default. To have the value filled in, set `hide_value` to
    `False`.
    """

    input_type = "password"
    validation_attrs = [
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
        "pattern",
    ]

    def __init__(self, hide_value=True):
        self.hide_value = hide_value

    def __call__(self, field, **kwargs):
        if self.hide_value:
            kwargs["value"] = ""
        return super().__call__(field, **kwargs)


class HiddenInput(Input):
    """
    Render an :mdn-input:`hidden`.
    """

    input_type = "hidden"
    validation_attrs = ["disabled"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_flags = {"hidden": True}


class CheckboxInput(Input):
    """
    Render an :mdn-input:`checkbox`.

    The ``checked`` HTML attribute is set if the field's data is a non-false value.
    """

    input_type = "checkbox"
    validation_attrs = ["required", "disabled"]

    def __call__(self, field, **kwargs):
        if getattr(field, "checked", field.data):
            kwargs["checked"] = True
        return super().__call__(field, **kwargs)


class RadioInput(Input):
    """
    Render a single :mdn-input:`radio` button.

    This widget is most commonly used in conjunction with ListWidget or some
    other listing, as singular radio buttons are not very useful.
    """

    input_type = "radio"
    validation_attrs = ["required", "disabled"]

    def __call__(self, field, **kwargs):
        if field.checked:
            kwargs["checked"] = True
        return super().__call__(field, **kwargs)


class FileInput(Input):
    """Render an :mdn-input:`file`.

    :param multiple: allow choosing multiple files
    """

    input_type = "file"
    validation_attrs = ["required", "disabled", "accept"]

    def __init__(self, multiple=False):
        super().__init__()
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        # browser ignores value of file input for security
        kwargs["value"] = False

        if self.multiple:
            kwargs["multiple"] = True

        return super().__call__(field, **kwargs)


class SubmitInput(Input):
    """
    Renders an :mdn-input:`submit`.

    The field's label is used as the text of the submit button instead of the
    data on the field.
    """

    input_type = "submit"
    validation_attrs = ["required", "disabled"]

    def __call__(self, field, **kwargs):
        kwargs.setdefault("value", field.label.text)
        return super().__call__(field, **kwargs)


class TextArea:
    """
    Renders a multi-line :mdn-tag:`textarea`.

    `rows` and `cols` ought to be passed as keyword args when rendering.
    """

    validation_attrs = ["required", "disabled", "readonly", "maxlength", "minlength"]

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        flags = getattr(field, "flags", {})
        for k in dir(flags):
            if k in self.validation_attrs and k not in kwargs:
                kwargs[k] = getattr(flags, k)
        textarea_params = html_params(name=field.name, **kwargs)
        textarea_innerhtml = escape(field._value())
        return Markup(
            f"<textarea {textarea_params}>\r\n{textarea_innerhtml}</textarea>"
        )


class Select:
    """
    Renders a :mdn-tag:`select` field.

    If `multiple` is True, then the `size` property should be specified on
    rendering to make the field useful.

    The field must provide an `iter_choices()` method which the widget will
    call on rendering; this method must yield tuples of
    `(value, label, selected)` or `(value, label, selected, render_kw)`.
    It also must provide a `has_groups()` method which tells whether choices
    are divided into groups, and if they do, the field must have an
    `iter_groups()` method that yields tuples of `(label, choices)`, where
    `choices` is a iterable of `(value, label, selected)` tuples.
    """

    validation_attrs = ["required", "disabled"]

    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        if self.multiple:
            kwargs["multiple"] = True
        flags = getattr(field, "flags", {})
        for k in dir(flags):
            if k in self.validation_attrs and k not in kwargs:
                kwargs[k] = getattr(flags, k)
        select_params = html_params(name=field.name, **kwargs)
        html = [f"<select {select_params}>"]
        if field.has_groups():
            for group, choices in field.iter_groups():
                optgroup_params = html_params(label=group)
                html.append(f"<optgroup {optgroup_params}>")
                for choice in choices:
                    val, label, selected, render_kw = choice
                    html.append(self.render_option(val, label, selected, **render_kw))
                html.append("</optgroup>")
        else:
            for choice in field.iter_choices():
                val, label, selected, render_kw = choice
                html.append(self.render_option(val, label, selected, **render_kw))
        html.append("</select>")
        return Markup("".join(html))

    @classmethod
    def render_option(cls, value, label, selected, **kwargs):
        if value is True:
            # Handle the special case of a 'True' value.
            value = str(value)

        options = dict(kwargs, value=value)
        if selected:
            options["selected"] = True
        return Markup(f"<option {html_params(**options)}>{escape(label)}</option>")


class Option:
    """
    Render an individual :mdn-tag:`option` from a select field.

    This is just a convenience for various custom rendering situations, and an
    option by itself does not constitute an entire field.
    """

    def __call__(self, field, **kwargs):
        return Select.render_option(
            field._value(), field.label.text, field.checked, **kwargs
        )


class SearchInput(Input):
    """
    Render an :mdn-input:`search`.
    """

    input_type = "search"
    validation_attrs = [
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
        "pattern",
    ]


class TelInput(Input):
    """
    Render an :mdn-input:`tel`.
    """

    input_type = "tel"
    validation_attrs = [
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
        "pattern",
    ]


class URLInput(Input):
    """
    Render an :mdn-input:`url`.
    """

    input_type = "url"
    validation_attrs = [
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
        "pattern",
    ]


class EmailInput(Input):
    """
    Render an :mdn-input:`email`.
    """

    input_type = "email"
    validation_attrs = [
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
        "pattern",
    ]


class DateTimeInput(Input):
    """
    Render an ``<input type="datetime">`` control.

    This is a legacy HTML input type. For modern browser support, prefer
    :class:`DateTimeLocalInput`.
    """

    input_type = "datetime"
    validation_attrs = ["required", "disabled", "readonly", "max", "min", "step"]


class DateInput(Input):
    """
    Render a :mdn-input:`date`.
    """

    input_type = "date"
    validation_attrs = ["required", "disabled", "readonly", "max", "min", "step"]


class MonthInput(Input):
    """
    Render an :mdn-input:`month`.
    """

    input_type = "month"
    validation_attrs = ["required", "disabled", "readonly", "max", "min", "step"]


class WeekInput(Input):
    """
    Render an :mdn-input:`week`.
    """

    input_type = "week"
    validation_attrs = ["required", "disabled", "readonly", "max", "min", "step"]


class TimeInput(Input):
    """
    Render a :mdn-input:`time`.
    """

    input_type = "time"
    validation_attrs = ["required", "disabled", "readonly", "max", "min", "step"]


class DateTimeLocalInput(Input):
    """
    Render an :mdn-input:`datetime-local`.
    """

    input_type = "datetime-local"
    validation_attrs = ["required", "disabled", "readonly", "max", "min", "step"]


class NumberInput(Input):
    """
    Render an :mdn-input:`number`.
    """

    input_type = "number"
    validation_attrs = ["required", "disabled", "readonly", "max", "min", "step"]

    def __init__(self, step=None, min=None, max=None):
        self.step = step
        self.min = min
        self.max = max

    def __call__(self, field, **kwargs):
        if self.step is not None:
            kwargs.setdefault("step", self.step)
        if self.min is not None:
            kwargs.setdefault("min", self.min)
        if self.max is not None:
            kwargs.setdefault("max", self.max)
        return super().__call__(field, **kwargs)


class RangeInput(NumberInput):
    """
    Render an :mdn-input:`range`.
    """

    input_type = "range"
    validation_attrs = ["disabled", "max", "min", "step"]


class ColorInput(Input):
    """
    Render an :mdn-input:`color`.
    """

    input_type = "color"
    validation_attrs = ["disabled"]
