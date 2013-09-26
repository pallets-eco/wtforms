from wtforms import i18n
from wtforms.utils import lazy_property


class DefaultMeta(object):
    """
    This is the default Meta class which defines all the default values and
    therefore also the 'API' of the class Meta interface.
    """

    # -- Basic form primitives

    def bind_field(self, form, unbound_field, options):
        """
        bind_field allows potential customization of how fields are bound.

        The default implementation simply passes the options to
        :meth:`UnboundField.bind`.

        :param form: The form.
        :param unbound_field: The unbound field.
        :param options:

        :return A bound field
        """
        return unbound_field.bind(form=form, **options)

    def wrap_formdata(self, form, formdata):
        """
        wrap_formdata allows doing custom wrappers of WTForms formdata.

        The default implementation simply passes back `formdata`.

        :param form: The form.
        :param formdata: Form data.
        """
        return formdata

    # -- CSRF

    csrf = False

    @lazy_property
    def csrf_class(self):
        # FIXME TODO fix import
        from wtforms.csrf import SessionCSRF
        return SessionCSRF

    # -- i18n

    locales = False

    def get_translations(self, form):
        """
        Override in subclasses to provide alternate translations factory.

        Must return an object that provides gettext() and ngettext() methods.

        See the i18n documentation for more.
        """
        locales = self.locales or form.LOCALES
        if locales is False:
            return None
        else:
            return i18n.get_translations(locales)
