from __future__ import unicode_literals

import warnings

from unittest import TestCase
from wtforms import TextField, validators
from wtforms.i18n import get_translations
from wtforms import form
from wtforms.ext.i18n import form as i18n_form


class I18NTest(TestCase):
    def test_failure(self):
        self.assertRaises(IOError, get_translations, [])

    def test_us_translation(self):
        translations = get_translations(['en_US'])
        self.assertEqual(translations.gettext('Invalid Mac address.'), 'Invalid MAC address.')


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
        self.assertEquals(len(tcache), 2)
        assert not form.validate()
        self.assertEqual(form.a.errors[0], 'Este campo es obligatorio.')


class CoreFormTest(TestCase):
    class F(form.Form):
        LANGUAGES = ['en_US', 'en']
        a = TextField(validators=[validators.Required()])

    class F2(form.Form):
        a = TextField(validators=[validators.Required()])

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
        assert form.LANGUAGES is False
        self.assertEqual(form.a.gettext(''), '')

    def test_fallback(self):
        form = self._common_test('This field is required.', dict(LANGUAGES=False))
        self.assertEqual(form.a.gettext(''), '')

    def test_override_languages(self):
        self._common_test('Este campo es obligatorio.', dict(LANGUAGES=['es_ES']))


if __name__ == '__main__':
    from unittest import main
    main()
