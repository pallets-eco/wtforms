from __future__ import unicode_literals

from unittest import TestCase
from wtforms import form, TextField, validators
from wtforms.i18n import get_translations
from wtforms.ext.i18n import form as i18n_form


def gettext_lower(self, s):
    return s.lower()


def ngettext_lower(self, singular, plural, n):
    if n == 1:
        return singular.lower()
    else:
        return plural.lower()


class Lower_Translator(object):
    """A fake translator that just converts everything to lowercase."""

    gettext = gettext_lower
    ngettext = ngettext_lower


class Python2_Translator(object):
    """A mock translator which implements python2 ugettext methods."""

    ugettext = gettext_lower
    ungettext = ngettext_lower


class I18NTest(TestCase):
    def test_failure(self):
        self.assertRaises(IOError, get_translations, [])

    def test_us_translation(self):
        translations = get_translations(['en_US'])
        self.assertEqual(translations.gettext('Invalid Mac address.'), 'Invalid MAC address.')

    def _test_converter(self, translator):
        getter = lambda x: translator

        translations = get_translations([], getter=getter)
        self.assertEqual(translations.gettext('Foo'), 'foo')
        self.assertEqual(translations.ngettext('Foo', 'Foos', 1), 'foo')
        self.assertEqual(translations.ngettext('Foo', 'Foos', 2), 'foos')
        return translations

    def test_python2_wrap(self):
        translator = Python2_Translator()
        translations = self._test_converter(translator)
        assert translations is not translator

    def test_python3_nowrap(self):
        translator = Lower_Translator()
        translations = self._test_converter(translator)
        assert translations is translator


class ClassicI18nFormTest(TestCase):
    class F(i18n_form.Form):
        LANGUAGES = ['en_US', 'en']
        a = TextField(validators=[validators.Required()])

    def test_form(self):
        tcache = i18n_form.translations_cache
        tcache.clear()
        form = self.F()

        assert ('en_US', 'en') in tcache
        assert form._get_translations() is tcache[('en_US', 'en')]
        assert not form.validate()
        self.assertEqual(form.a.errors[0], 'This field is required.')

        form = self.F(LANGUAGES=['es'])
        assert ('es', ) in tcache
        self.assertEqual(len(tcache), 2)
        assert not form.validate()
        self.assertEqual(form.a.errors[0], 'Este campo es obligatorio.')


class CoreFormTest(TestCase):
    class F(form.Form):
        class Meta:
            locales = ['en_US', 'en']
        a = TextField(validators=[validators.Required()])

    class F2(form.Form):
        a = TextField(validators=[validators.Required(), validators.Length(max=3)])

    class F3(form.Form):
        a = TextField(validators=[validators.Length(max=1)])

    def _common_test(self, expected_error, form_kwargs, form_class=None):
        if not form_class:
            form_class = self.F
        form = form_class(**form_kwargs)
        assert not form.validate()
        self.assertEqual(form.a.errors[0], expected_error)
        return form

    def test_defaults(self):
        # Test with the default language
        form = self._common_test('This field is required.', {})
        # Make sure we have a gettext translations context
        self.assertNotEqual(form.a.gettext(''), '')

        form = self._common_test('This field is required.', {}, self.F2)
        assert form._get_translations() is None
        assert form.meta.locales is False
        self.assertEqual(form.a.gettext(''), '')

    def test_fallback(self):
        form = self._common_test('This field is required.', dict(meta=dict(locales=False)))
        self.assertEqual(form.a.gettext(''), '')

    def test_override_languages(self):
        self._common_test('Este campo es obligatorio.', dict(meta=dict(locales=['es_ES'])))

    def test_ngettext(self):
        language_settings = [
            (['en_US', 'en'], 'Field cannot be longer than 3 characters.', 'Field cannot be longer than 1 character.'),
            (['de_DE', 'de'], 'Feld kann nicht l\xe4nger als 3 Zeichen sein.', 'Feld kann nicht l\xe4nger als 1 Zeichen sein.'),
            (['et'], 'V\xe4li ei tohi olla \xfcle 3 t\xe4hem\xe4rgi pikk.', 'V\xe4li ei tohi olla \xfcle 1 t\xe4hem\xe4rgi pikk.'),
        ]
        for languages, match1, match2 in language_settings:
            settings = dict(a='toolong', meta=dict(locales=languages))
            self._common_test(match1, settings, self.F2)
            self._common_test(match2, settings, self.F3)

    def test_cache(self):
        settings = {'meta': {'locales': ['de_DE'], 'cache_translations': True}}
        expected = 'Dieses Feld wird ben\xf6tigt.'
        form1 = self._common_test(expected, settings)
        form2 = self._common_test(expected, settings)
        assert form1.meta.get_translations(form1) is form2.meta.get_translations(form2)
        settings['meta']['cache_translations'] = False
        form3 = self._common_test(expected, settings)
        assert form2.meta.get_translations(form2) is not form3.meta.get_translations(form3)


class TranslationsTest(TestCase):
    class F(form.Form):
        a = TextField(validators=[validators.Length(max=5)])

    class F2(form.Form):
        def _get_translations(self):
            return Lower_Translator()

        a = TextField('', [validators.Length(max=5)])

    def setUp(self):
        self.a = self.F().a

    def test_gettext(self):
        x = "foo"
        self.assertTrue(self.a.gettext(x) is x)

    def test_ngettext(self):
        getit = lambda n: self.a.ngettext("antelope", "antelopes", n)
        self.assertEqual(getit(0), "antelopes")
        self.assertEqual(getit(1), "antelope")
        self.assertEqual(getit(2), "antelopes")

    def test_validator_translation(self):
        form = self.F2(a='hellobye')
        self.assertFalse(form.validate())
        self.assertEqual(form.a.errors[0], 'field cannot be longer than 5 characters.')
        form = self.F(a='hellobye')
        self.assertFalse(form.validate())
        self.assertEqual(form.a.errors[0], 'Field cannot be longer than 5 characters.')
