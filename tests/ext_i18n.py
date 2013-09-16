from __future__ import unicode_literals

from unittest import TestCase
from wtforms import TextField, validators
from wtforms.ext.i18n.utils import get_translations
from wtforms.ext.i18n import form as i18n_form


class I18NTest(TestCase):
    def test_failure(self):
        self.assertRaises(IOError, get_translations, [])

    def test_us_translation(self):
        translations = get_translations(['en_US'])
        self.assertEqual(translations.gettext('Invalid Mac address.'), 'Invalid MAC address.')


class FormTest(TestCase):
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


if __name__ == '__main__':
    from unittest import main
    main()

