from .. import widgets
from .core import Field

__all__ = (
    "ButtonField",
    "BooleanField",
    "TextAreaField",
    "PasswordField",
    "FileField",
    "MultipleFileField",
    "HiddenField",
    "SearchField",
    "SubmitField",
    "StringField",
    "TelField",
    "URLField",
    "EmailField",
    "ColorField",
)


class BooleanField(Field):
    """
    Represents an :mdn-input:`checkbox`. Set the ``checked``-status by using
    the ``default``-option. Any value for ``default``, e.g.
    ``default="checked"``, puts ``checked`` into the HTML element and sets
    the ``data`` to ``True``

    :param false_values:
        If provided, a sequence of strings each of which is an exact match
        string of what is considered a "false" value. Defaults to the tuple
        ``(False, "false", "")``
    """

    widget = widgets.CheckboxInput()
    false_values = (False, "false", "")

    def __init__(self, label=None, validators=None, false_values=None, **kwargs):
        super().__init__(label, validators, **kwargs)
        if false_values is not None:
            self.false_values = false_values

    def process_data(self, value):
        self.data = bool(value)

    def process_formdata(self, valuelist):
        if not valuelist or valuelist[0] in self.false_values:
            self.data = False
        else:
            self.data = True

    def _value(self):
        if self.raw_data:
            return str(self.raw_data[0])
        return "y"


class StringField(Field):
    """
    This field is the base for most of the more complicated fields, and
    represents an :mdn-input:`text`.

    An optional parameter called datelist can be provided. This string will be
    used as a value for the attribute ``list`` in the ``input`` element.

    Additionally, an optional parameter called choices can be provided. This
    is a list of Choice objects. After the ``input`` element, a ``datelist``
    element will be added with the value of its ``id`` attribute set to the
    same value of datelist string parameter. Inside the ``datelist`` element,
    for each Choice, an ``option`` element will be added.

    Note that sometimes another field already results in a ``datelist`` element
    in the HTML. In order to reuse that, only provide the identical string for
    the parameter called datelist and omit the choices parameter.

    Support for datalist is currently:
        - StringField
        - SearchField
        - EmailField
        - TelField
        - URLField
    """

    widget = widgets.TextInput()

    def __init__(self, *args, datalist=None, choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        if datalist is not None:
            self.datalist = datalist
            if choices is not None:
                self.choices = choices

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0]

    def _value(self):
        return str(self.data) if self.data is not None else ""


class ButtonField(StringField):
    """
    Represents a :mdn-tag:`button` with ``type="submit"``.

    The field's label is used as the visible text of the button, not as the
    submitted value. If the button is used to submit the form, the submitted
    value is stored as a string.

    The rendered ``value`` attribute comes from the field data passed at form
    construction time, or defaults to an empty string. If the button is not
    clicked, the field data is `None`. Pass ``label=`` when rendering to
    override the visible button text.

    The label is HTML-escaped at render time. To embed HTML in the button
    content (an icon, formatted text), pass a :class:`markupsafe.Markup`
    instance — at declaration or as the render-time ``label=``::

        from markupsafe import Markup

        class F(Form):
            save = ButtonField(Markup('<i class="icon-save"></i> Save'))

        # or at render time:
        form.save(label=Markup('<i class="icon-save"></i> Save'))
    """

    widget = widgets.Button()

    def process_data(self, value):
        self.data = None

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0]
        else:
            self.data = None

    def _value(self):
        if self.raw_data:
            return str(self.raw_data[0])
        if self.object_data is not None:
            return str(self.object_data)
        return ""


class TextAreaField(StringField):
    """
    This field represents an HTML :mdn-tag:`textarea` and can be used to take
    multi-line input.
    """

    widget = widgets.TextArea()


class PasswordField(StringField):
    """
    A StringField, except renders an :mdn-input:`password`.

    Also, whatever value is accepted by this field is not rendered back
    to the browser like normal fields.
    """

    widget = widgets.PasswordInput()


class FileField(Field):
    """Renders an :mdn-input:`file` field.

    By default, the value will be the filename sent in the form data.
    WTForms **does not** deal with frameworks' file handling capabilities.
    A WTForms extension for a framework may replace the filename value
    with an object representing the uploaded data.
    """

    widget = widgets.FileInput()

    def _value(self):
        # browser ignores value of file input for security
        return False


class MultipleFileField(FileField):
    """A :class:`FileField` that allows choosing multiple files."""

    widget = widgets.FileInput(multiple=True)

    def process_formdata(self, valuelist):
        self.data = valuelist


class HiddenField(StringField):
    """
    HiddenField is a convenience for a StringField with a
    :mdn-input:`hidden` widget.

    It will render as an :mdn-input:`hidden` but otherwise coerce to a string.
    """

    widget = widgets.HiddenInput()


class SubmitField(BooleanField):
    """
    Represents an :mdn-input:`submit`.

    The field's label is also used as the rendered HTML ``value`` of the submit
    control. Its WTForms data is boolean, following :class:`BooleanField`
    semantics: the field is ``True`` when the submitted value is not a falsy
    value, and ``False`` otherwise.
    """

    widget = widgets.SubmitInput()


class SearchField(StringField):
    """
    Represents an :mdn-input:`search`.
    """

    widget = widgets.SearchInput()


class TelField(StringField):
    """
    Represents an :mdn-input:`tel`.
    """

    widget = widgets.TelInput()


class URLField(StringField):
    """
    Represents an :mdn-input:`url`.
    """

    widget = widgets.URLInput()


class EmailField(StringField):
    """
    Represents an :mdn-input:`email`.
    """

    widget = widgets.EmailInput()


class ColorField(StringField):
    """
    Represents an :mdn-input:`color`.
    """

    widget = widgets.ColorInput()
