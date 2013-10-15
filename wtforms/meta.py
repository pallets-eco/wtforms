from wtforms import i18n


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
            A dictionary of options which are typically passed to the field.

        :return: A bound field
        """
        return unbound_field.bind(form=form, **options)

    def wrap_formdata(self, form, formdata):
        """
        wrap_formdata allows doing custom wrappers of WTForms formdata.

        The default implementation simply passes back `formdata`.

        :param form: The form.
        :param formdata: Form data.
        :return: A form-input wrapper compatible with WTForms.
        """
        return formdata

    # -- CSRF

    csrf = False
    csrf_field_name = 'csrf_token'
    csrf_secret = None
    csrf_context = None
    csrf_class = None

    def build_csrf(self, form):
        """
        Build a CSRF implementation.
        """
        if self.csrf_class is not None:
            return self.csrf_class()

        # FIXME TODO fix import
        from wtforms.csrf.session import SessionCSRF
        return SessionCSRF()

    # -- i18n

    locales = False

    def get_translations(self, form):
        """
        Override in subclasses to provide alternate translations factory.

        Must return an object that provides gettext() and ngettext() methods.

        See the i18n documentation for more.
        """
        locales = self.locales
        if locales is False:
            return None
        else:
            return i18n.get_translations(locales)

    def update_values(self, values):
        """
        Given a dictionary of values, update values on this `Meta` instance.
        """
        for key, value in values.items():
            setattr(self, key, value)
