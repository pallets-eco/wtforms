from wtforms.validators import ValidationError
from wtforms.fields import HiddenField


class CSRFTokenField(HiddenField):
    current_token = None

    def _value(self):
        """
        We want to always return the current token on render, regardless of
        whether a good or bad token was passed.
        """
        return self.current_token

    def populate_obj(self, *args):
        """
        Don't populate objects with the CSRF token
        """
        pass


class CSRF(object):
    field_class = CSRFTokenField

    def __init__(self, form=None):
        if form is not None:
            self.setup_form(form, form.meta)

    def setup_form(self, form):
        meta = form.meta
        field_name = meta.csrf_field_name
        return [(field_name, self.field_class())]

    def generate_csrf_token(self, csrf_context):
        """
        Implementations must override this to provide a method with which one
        can get a CSRF token for this form.

        A CSRF token should be a string which can be generated
        deterministically so that on the form POST, the generated string is
        (usually) the same assuming the user is using the site normally.

        :param csrf_context:
            A transparent object which can be used as contextual info for
            generating the token.
        """
        raise NotImplementedError()

    def validate_csrf_token(self, field):
        """
        Override this method to provide custom CSRF validation logic.

        The default CSRF validation logic simply checks if the recently
        generated token equals the one we received as formdata.
        """
        if field.current_token != field.data:
            raise ValidationError(field.gettext('Invalid CSRF Token'))
