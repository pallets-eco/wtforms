#!/usr/bin/env python
from unittest import TestCase
from wtforms.validators import StopValidation, ValidationError, email, equal_to, ip_address, length, required, optional, regexp, url, NumberRange, AnyOf, NoneOf

class DummyTranslations(object):
    def gettext(self, string):
        return string

    def ngettext(self, singular, plural, n):
        if n == 1:
            return singular

        return plural

class DummyForm(dict):
    pass

class DummyField(object):
    _translations = DummyTranslations()
    def __init__(self, data, errors=(), raw_data=None):
        self.data = data
        self.errors = list(errors)
        self.raw_data = raw_data

    def gettext(self, string):
        return self._translations.gettext(string)

    def ngettext(self, singular, plural, n):
        return self._translations.ngettext(singular, plural, n)

def grab_error_message(callable, form, field):
    try:
        callable(form, field)
    except ValidationError, e:
        return e.args[0]

class ValidatorsTest(TestCase):
    def setUp(self):
        self.form = DummyForm()

    def test_email(self):
        self.assertEqual(email()(self.form, DummyField('foo@bar.dk')), None)
        self.assertEqual(email()(self.form, DummyField('123@bar.dk')), None)
        self.assertEqual(email()(self.form, DummyField('foo@456.dk')), None)
        self.assertEqual(email()(self.form, DummyField('foo@bar456.info')), None)
        self.assertRaises(ValidationError, email(), self.form, DummyField(None))
        self.assertRaises(ValidationError, email(), self.form, DummyField(''))
        self.assertRaises(ValidationError, email(), self.form, DummyField('foo'))
        self.assertRaises(ValidationError, email(), self.form, DummyField('bar.dk'))
        self.assertRaises(ValidationError, email(), self.form, DummyField('foo@'))
        self.assertRaises(ValidationError, email(), self.form, DummyField('@bar.dk'))
        self.assertRaises(ValidationError, email(), self.form, DummyField('foo@bar'))
        self.assertRaises(ValidationError, email(), self.form, DummyField('foo@bar.ab12'))
        self.assertRaises(ValidationError, email(), self.form, DummyField('foo@.bar.ab'))

    def test_equal_to(self):
        self.form['foo'] = DummyField('test')
        self.assertEqual(equal_to('foo')(self.form, self.form['foo']), None)
        self.assertRaises(ValidationError, equal_to('invalid_field_name'), self.form, DummyField('test'))
        self.assertRaises(ValidationError, equal_to('foo'), self.form, DummyField('different_value'))

    def test_ip_address(self):
        self.assertEqual(ip_address()(self.form, DummyField('127.0.0.1')), None)
        self.assertRaises(ValidationError, ip_address(), self.form, DummyField('abc.0.0.1'))
        self.assertRaises(ValidationError, ip_address(), self.form, DummyField('1278.0.0.1'))
        self.assertRaises(ValidationError, ip_address(), self.form, DummyField('127.0.0.abc'))

    def test_length(self):
        field = DummyField('foobar')
        self.assertEqual(length(min=2, max=6)(self.form, field), None)
        self.assertRaises(ValidationError, length(min=7), self.form, field)
        self.assertEqual(length(min=6)(self.form, field), None)
        self.assertRaises(ValidationError, length(max=5), self.form, field)
        self.assertEqual(length(max=6)(self.form, field), None)

        self.assertRaises(AssertionError, length)
        self.assertRaises(AssertionError, length, min=5, max=2)

        # Test new formatting features
        grab = lambda **k : grab_error_message(length(**k), self.form, field)
        self.assertEqual(grab(min=2, max=5, message='%(min)d and %(max)d'), '2 and 5')
        self.assert_('at least 8' in grab(min=8))
        self.assert_('longer than 5' in grab(max=5))
        self.assert_('between 2 and 5' in grab(min=2, max=5))

    def test_required(self):
        self.assertEqual(required()(self.form, DummyField('foobar')), None)
        self.assertRaises(StopValidation, required(), self.form, DummyField(''))
        self.assertRaises(StopValidation, required(), self.form, DummyField(' '))
        self.assertEqual(required().field_flags, ('required', ))
        f = DummyField('', ['Invalid Integer Value'])
        self.assertEqual(len(f.errors), 1)
        self.assertRaises(StopValidation, required(), self.form, f)
        self.assertEqual(len(f.errors), 0)

    def test_optional(self):
        self.assertEqual(optional()(self.form, DummyField('foobar', raw_data=['foobar'])), None)
        self.assertRaises(StopValidation, optional(), self.form, DummyField('', raw_data=['']))
        self.assertRaises(StopValidation, optional(), self.form, DummyField(' ', raw_data=[' ']))
        self.assertEqual(optional().field_flags, ('optional', ))
        f = DummyField('', ['Invalid Integer Value'], raw_data=[''])
        self.assertEqual(len(f.errors), 1)
        self.assertRaises(StopValidation, optional(), self.form, f)
        self.assertEqual(len(f.errors), 0)

    def test_regexp(self):
        import re
        # String regexp
        self.assertEqual(regexp('^a')(self.form, DummyField('abcd')), None)
        self.assertEqual(regexp('^a', re.I)(self.form, DummyField('ABcd')), None)
        self.assertRaises(ValidationError, regexp('^a'), self.form, DummyField('foo'))
        self.assertRaises(ValidationError, regexp('^a'), self.form, DummyField(None))
        # Compiled regexp
        self.assertEqual(regexp(re.compile('^a'))(self.form, DummyField('abcd')), None)
        self.assertEqual(regexp(re.compile('^a', re.I))(self.form, DummyField('ABcd')), None)
        self.assertRaises(ValidationError, regexp(re.compile('^a')), self.form, DummyField('foo'))
        self.assertRaises(ValidationError, regexp(re.compile('^a')), self.form, DummyField(None))

    def test_url(self):
        self.assertEqual(url()(self.form, DummyField('http://foobar.dk')), None)
        self.assertEqual(url()(self.form, DummyField('http://foobar.dk/')), None)
        self.assertEqual(url()(self.form, DummyField('http://foobar.museum/foobar')), None)
        self.assertEqual(url()(self.form, DummyField('http://127.0.0.1/foobar')), None)
        self.assertEqual(url()(self.form, DummyField('http://127.0.0.1:9000/fake')), None)
        self.assertEqual(url(require_tld=False)(self.form, DummyField('http://localhost/foobar')), None)
        self.assertEqual(url(require_tld=False)(self.form, DummyField('http://foobar')), None)
        self.assertRaises(ValidationError, url(), self.form, DummyField('http://foobar'))
        self.assertRaises(ValidationError, url(), self.form, DummyField('foobar.dk'))
        self.assertRaises(ValidationError, url(), self.form, DummyField('http://127.0.0/asdf'))
        self.assertRaises(ValidationError, url(), self.form, DummyField('http://foobar.d'))
        self.assertRaises(ValidationError, url(), self.form, DummyField('http://foobar.12'))
        self.assertRaises(ValidationError, url(), self.form, DummyField('http://localhost:abc/a'))

    def test_number_range(self):
        v = NumberRange(min=5, max=10)
        self.assertEqual(v(self.form, DummyField(7)), None)
        self.assertRaises(ValidationError, v, self.form, DummyField(None))
        self.assertRaises(ValidationError, v, self.form, DummyField(0))
        self.assertRaises(ValidationError, v, self.form, DummyField(12))

        onlymin = NumberRange(min=5)
        self.assertEqual(onlymin(self.form, DummyField(500)), None)
        self.assertRaises(ValidationError, onlymin, self.form, DummyField(4))

        onlymax = NumberRange(max=50)
        self.assertEqual(onlymax(self.form, DummyField(30)), None)
        self.assertRaises(ValidationError, onlymax, self.form, DummyField(75))

    def test_lazy_proxy(self):
        """Tests that the validators support lazy translation strings for messages."""

        class ReallyLazyProxy(object):
            def __unicode__(self):
                raise Exception('Translator function called during form declaration: it should be called at response time.')
            __str__ = __unicode__

        message = ReallyLazyProxy()
        self.assertRaises(Exception, str, message)
        self.assertRaises(Exception, unicode, message)
        self.assert_(equal_to('fieldname', message=message))
        self.assert_(length(min=1, message=message))
        self.assert_(NumberRange(1,5, message=message))
        self.assert_(required(message=message))
        self.assert_(regexp('.+', message=message))
        self.assert_(email(message=message))
        self.assert_(ip_address(message=message))
        self.assert_(url(message=message))

    def test_any_of(self):
        self.assertEqual(AnyOf(['a', 'b', 'c'])(self.form, DummyField('b')), None)
        self.assertRaises(ValueError, AnyOf(['a', 'b', 'c']), self.form, DummyField(None))

    def test_none_of(self):
        self.assertEqual(NoneOf(['a', 'b', 'c'])(self.form, DummyField('d')), None)
        self.assertRaises(ValueError, NoneOf(['a', 'b', 'c']), self.form, DummyField('a'))

if __name__ == '__main__':
    from unittest import main
    main()
