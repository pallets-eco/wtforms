from .. import widgets
from .core import StringField, BooleanField

__all__ = (
    'BooleanField', 'TextAreaField', 'PasswordField', 'FileField',
    'HiddenField', 'SubmitField'
)


class TextAreaField(StringField):
    """
    This field represents an HTML ``<textarea>`` and can be used to take
    multi-line input.
    """
    widget = widgets.TextArea()


class PasswordField(StringField):
    """
    A StringField, except renders an ``<input type="password">``.

    Also, whatever value is accepted by this field is not rendered back
    to the browser like normal fields.
    """
    widget = widgets.PasswordInput()


class FileField(StringField):
    """
    Can render a file-upload field.  Will take any passed filename value, if
    any is sent by the browser in the post params.  This field will NOT
    actually handle the file upload portion, as wtforms does not deal with
    individual frameworks' file handling capabilities.
    """
    widget = widgets.FileInput()


class HiddenField(StringField):
    """
    HiddenField is a convenience for a StringField with a HiddenInput widget.

    It will render as an ``<input type="hidden">`` but otherwise coerce to a string.
    """
    widget = widgets.HiddenInput()


class SubmitField(BooleanField):
    """
    Represents an ``<input type="submit">``.  This allows checking if a given
    submit button has been pressed.
    """
    widget = widgets.SubmitInput()
