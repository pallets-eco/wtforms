try:
    from html import escape
    from html.parser import HTMLParser
except ImportError:
    from cgi import escape
    from HTMLParser import HTMLParser

from wtforms.utils import WebobInputWrapper
from wtforms.widgets.core import HTMLString
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

        The default implementation detects webob-style multidicts and wraps
        them, otherwise passes formdata back un-changed.

        :param form: The form.
        :param formdata: Form data.
        :return: A form-input wrapper compatible with WTForms.
        """
        if formdata is not None and not hasattr(formdata, 'getlist'):
            if hasattr(formdata, 'getall'):
                return WebobInputWrapper(formdata)
            else:
                raise TypeError("formdata should be a multidict-type wrapper that supports the 'getlist' method")
        return formdata

    def render_field(self, field, render_kw):
        """
        render_field allows customization of how widget rendering is done.

        The default implementation calls ``field.widget(field, **render_kw)``
        """
        return field.widget(field, **render_kw)

    # -- CSRF

    csrf = False
    csrf_field_name = 'csrf_token'
    csrf_secret = None
    csrf_context = None
    csrf_class = None

    def build_csrf(self, form):
        """
        Build a CSRF implementation. This is called once per form instance.

        The default implementation builds the class referenced to by
        :attr:`csrf_class` with zero arguments. If `csrf_class` is ``None``,
        will instead use the default implementation
        :class:`wtforms.csrf.session.SessionCSRF`.

        :param form: The form.
        :return: A CSRF implementation.
        """
        if self.csrf_class is not None:
            return self.csrf_class()

        from wtforms.csrf.session import SessionCSRF
        return SessionCSRF()

    # -- i18n

    locales = False
    cache_translations = True
    translations_cache = {}

    def get_translations(self, form):
        """
        Override in subclasses to provide alternate translations factory.
        See the i18n documentation for more.

        :param form: The form.
        :return: An object that provides gettext() and ngettext() methods.
        """
        locales = self.locales
        if locales is False:
            return None

        if self.cache_translations:
            # Make locales be a hashable value
            locales = tuple(locales) if locales else None

            translations = self.translations_cache.get(locales)
            if translations is None:
                translations = self.translations_cache[locales] = i18n.get_translations(locales)

            return translations

        return i18n.get_translations(locales)

    # -- General

    def update_values(self, values):
        """
        Given a dictionary of values, update values on this `Meta` instance.
        """
        for key, value in values.items():
            setattr(self, key, value)


class PolyglotHTMLParser(HTMLParser):
    """This simplified ``HTMLParser`` converts its input to polyglot HTML.

    It works by making sure that stand-alone tags like ``<input>`` have a
    slash before the closing angle bracket, that attribute values are always
    quoted, and that boolean attributes have their value set to the attribute
    name (e.g., ``checked="checked"``).

    Note: boolean attributes are simply identified as attributes with no value
    at all.  Specifically, an attribute with an empty string (e.g.,
    ``checked=""``) will *not* be identified as boolean attribute, i.e., there
    is no semantic intelligence involved.

    >>> parser = PolyglotHTMLParser()
    >>> parser.feed('''<input type=checkbox name=foo value=y checked>''')
    >>> print(parser.get_output())
    <input type="checkbox" name="foo" value="y" checked="checked" />

    """

    def __init__(self):
        super(PolyglotHTMLParser, self).__init__()
        self.reset()
        self.output = []

    def html_params(self, attrs):
        output = []
        for key, value in attrs:
            if value is None:
                value = key
            output.append(' {}="{}"'.format(key, escape(value, quote=True)))
        return ''.join(output)

    def handle_starttag(self, tag, attrs):
        if tag == 'input':
            return self.handle_startendtag(tag, attrs)
        self.output.append('<{}{}>'.format(tag, self.html_params(attrs)))

    def handle_endtag(self, tag):
        self.output.append('</{}>'.format(tag))

    def handle_startendtag(self, tag, attrs):
        self.output.append('<{}{} />'.format(tag, self.html_params(attrs)))

    def handle_data(self, data):
        self.output.append(data)

    def handle_entityref(self, name):
        self.output.append('&{};'.format(name))

    def handle_charref(self, name):
        self.output.append('&#{};'.format(name))

    def get_output(self):
        return ''.join(self.output)


class PolyglotMeta(DefaultMeta):
    """
    This meta class works exactly like ``DefaultMeta``, except that fields of
    forms using this meta class will output polyglot markup.
    """

    def render_field(self, field, render_kw):
        """
        Render a widget, and convert its output to polyglot HTML.
        """
        html = field.widget(field, **render_kw)
        parser = PolyglotHTMLParser()
        parser.feed(html)
        output = HTMLString(parser.get_output())
        return output
