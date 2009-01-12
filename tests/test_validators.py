#!/usr/bin/python
"""
    test_validators
    ~~~~~~~~~~~~~~~
    
    Unittests for bundled validators.
    
    :copyright: 2007-2008 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""

from unittest import TestCase
from wtforms.validators import StopValidation, ValidationError, email, equal_to, ip_address, length, required, optional, regexp, url

class DummyForm(object):
    pass

class DummyField(object):
    def __init__(self, data):
        self.data = data

class test_validators(TestCase):
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
        self.form.foo = DummyField('test')
        self.assertEqual(equal_to('foo')(self.form, self.form.foo), None)
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
        self.assertRaises(ValidationError, length(max=5), self.form, field)
    
    def test_required(self):
        self.assertEqual(required()(self.form, DummyField('foobar')), None)
        self.assertRaises(StopValidation, required(), self.form, DummyField(''))
        self.assertRaises(StopValidation, required(), self.form, DummyField(' '))
        self.assertEqual(required().field_flags, ('required', ))

    def test_optional(self):
        self.assertEqual(optional()(self.form, DummyField('foobar')), None)
        self.assertRaises(StopValidation, optional(), self.form, DummyField(''))
        self.assertRaises(StopValidation, optional(), self.form, DummyField(' '))
        self.assertEqual(optional().field_flags, ('optional', ))

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

if __name__ == '__main__':
    from unittest import main
    main()
