from unittest import TestCase

from wtforms import Form, TextField
from wtforms import validators as v


class Lower_Translator(object):
    """A fake translator that just converts everything to lowercase."""

    def gettext(self, s):
        return s.lower()

    def ngettext(self, singular, plural, n):
        if n == 1:
            return singular.lower()
        else:
            return plural.lower()


class MyFormBase(Form):
    def _get_translations(self):
        return Lower_Translator()


class TranslationsTest(TestCase):
    class F(MyFormBase):
        a = TextField('', [v.Length(max=5)])

    def test_validator_translation(self):
        form = self.F(a='hellobye')
        self.assert_(not form.validate())
        self.assertEquals(form.a.errors[0], u'field cannot be longer than 5 characters.')
