# -*- coding: utf-8 -*-
from unittest import TestCase
from wtforms.compat import text_type
from wtforms.validators import (
    StopValidation, ValidationError, email, equal_to,
    ip_address, length, required, optional, regexp,
    url, NumberRange, AnyOf, NoneOf, mac_address, UUID,
    input_required, data_required
)
from functools import partial
from tests.common import DummyField, grab_error_message, grab_stop_message


class DummyForm(dict):
    pass


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
        self.assertRaises(ValidationError, email(), self.form, DummyField('  '))
        self.assertRaises(ValidationError, email(), self.form, DummyField('foo'))
        self.assertRaises(ValidationError, email(), self.form, DummyField('bar.dk'))
        self.assertRaises(ValidationError, email(), self.form, DummyField('foo@'))
        self.assertRaises(ValidationError, email(), self.form, DummyField('@bar.dk'))
        self.assertRaises(ValidationError, email(), self.form, DummyField('foo@bar'))
        self.assertRaises(ValidationError, email(), self.form, DummyField('foo@bar.ab12'))
        self.assertRaises(ValidationError, email(), self.form, DummyField('foo@.bar.ab'))

        # Test IDNA domains
        self.assertEqual(email()(self.form, DummyField(u'foo@bücher.中国')), None)

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
        self.assertRaises(ValidationError, ip_address(), self.form, DummyField('900.200.100.75'))
        for bad_address in ('abc.0.0.1', 'abcd:1234::123::1', '1:2:3:4:5:6:7:8:9', 'abcd::1ffff'):
            self.assertRaises(ValidationError, ip_address(ipv6=True), self.form, DummyField(bad_address))

        for good_address in ('::1', 'dead:beef:0:0:0:0:42:1', 'abcd:ef::42:1'):
            self.assertEqual(ip_address(ipv6=True)(self.form, DummyField(good_address)), None)

        # Test ValueError on ipv6=False and ipv4=False
        self.assertRaises(ValueError, ip_address, ipv4=False, ipv6=False)

    def test_mac_address(self):
        self.assertEqual(mac_address()(self.form,
                                       DummyField('01:23:45:67:ab:CD')), None)

        check_fail = partial(
            self.assertRaises, ValidationError,
            mac_address(), self.form
        )

        check_fail(DummyField('00:00:00:00:00'))
        check_fail(DummyField('01:23:45:67:89:'))
        check_fail(DummyField('01:23:45:67:89:gh'))
        check_fail(DummyField('123:23:45:67:89:00'))

    def test_uuid(self):
        self.assertEqual(
            UUID()(self.form, DummyField('2bc1c94f-0deb-43e9-92a1-4775189ec9f8')),
            None
        )
        self.assertRaises(ValidationError, UUID(), self.form,
                          DummyField('2bc1c94f-deb-43e9-92a1-4775189ec9f8'))
        self.assertRaises(ValidationError, UUID(), self.form,
                          DummyField('2bc1c94f-0deb-43e9-92a1-4775189ec9f'))
        self.assertRaises(ValidationError, UUID(), self.form,
                          DummyField('gbc1c94f-0deb-43e9-92a1-4775189ec9f8'))
        self.assertRaises(ValidationError, UUID(), self.form,
                          DummyField('2bc1c94f 0deb-43e9-92a1-4775189ec9f8'))

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
        grab = lambda **k: grab_error_message(length(**k), self.form, field)
        self.assertEqual(grab(min=2, max=5, message='%(min)d and %(max)d'), '2 and 5')
        self.assertTrue('at least 8' in grab(min=8))
        self.assertTrue('longer than 5' in grab(max=5))
        self.assertTrue('between 2 and 5' in grab(min=2, max=5))

    def test_required(self):
        self.assertEqual(required()(self.form, DummyField('foobar')), None)
        self.assertRaises(StopValidation, required(), self.form, DummyField(''))

    def test_data_required(self):
        # Make sure we stop the validation chain
        self.assertEqual(data_required()(self.form, DummyField('foobar')), None)
        self.assertRaises(StopValidation, data_required(), self.form, DummyField(''))
        self.assertRaises(StopValidation, data_required(), self.form, DummyField(' '))
        self.assertEqual(data_required().field_flags, ('required', ))

        # Make sure we clobber errors
        f = DummyField('', ['Invalid Integer Value'])
        self.assertEqual(len(f.errors), 1)
        self.assertRaises(StopValidation, data_required(), self.form, f)
        self.assertEqual(len(f.errors), 0)

        # Check message and custom message
        grab = lambda **k: grab_stop_message(data_required(**k), self.form, DummyField(''))
        self.assertEqual(grab(), 'This field is required.')
        self.assertEqual(grab(message='foo'), 'foo')

    def test_input_required(self):
        self.assertEqual(input_required()(self.form, DummyField('foobar', raw_data=['foobar'])), None)
        self.assertRaises(StopValidation, input_required(), self.form, DummyField('', raw_data=['']))
        self.assertEqual(input_required().field_flags, ('required', ))

        # Check message and custom message
        grab = lambda **k: grab_stop_message(input_required(**k), self.form, DummyField('', raw_data=['']))
        self.assertEqual(grab(), 'This field is required.')
        self.assertEqual(grab(message='foo'), 'foo')

    def test_optional(self):
        self.assertEqual(optional()(self.form, DummyField('foobar', raw_data=['foobar'])), None)
        self.assertRaises(StopValidation, optional(), self.form, DummyField('', raw_data=['']))
        self.assertEqual(optional().field_flags, ('optional', ))
        f = DummyField('', ['Invalid Integer Value'], raw_data=[''])
        self.assertEqual(len(f.errors), 1)
        self.assertRaises(StopValidation, optional(), self.form, f)
        self.assertEqual(len(f.errors), 0)

        # Test for whitespace behavior.
        whitespace_field = DummyField(' ', raw_data=[' '])
        self.assertRaises(StopValidation, optional(), self.form, whitespace_field)
        self.assertEqual(optional(strip_whitespace=False)(self.form, whitespace_field), None)

    def test_regexp(self):
        import re
        # String regexp
        self.assertEqual(regexp('^a')(self.form, DummyField('abcd')).group(0), 'a')
        self.assertEqual(regexp('^a', re.I)(self.form, DummyField('ABcd')).group(0), 'A')
        self.assertRaises(ValidationError, regexp('^a'), self.form, DummyField('foo'))
        self.assertRaises(ValidationError, regexp('^a'), self.form, DummyField(None))
        # Compiled regexp
        self.assertEqual(regexp(re.compile('^a'))(self.form, DummyField('abcd')).group(0), 'a')
        self.assertEqual(regexp(re.compile('^a', re.I))(self.form, DummyField('ABcd')).group(0), 'A')
        self.assertRaises(ValidationError, regexp(re.compile('^a')), self.form, DummyField('foo'))
        self.assertRaises(ValidationError, regexp(re.compile('^a')), self.form, DummyField(None))

        # Check custom message
        self.assertEqual(grab_error_message(regexp('^a', message='foo'), self.form, DummyField('f')), 'foo')

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
        # Test IDNA
        IDNA_TESTS = (
            u'http://\u0645\u062b\u0627\u0644.\u0625\u062e\u062a\u0628\u0627\u0631/foo.com',  # Arabic test
            u'http://उदाहरण.परीक्षा/',  # Hindi test
            u'http://실례.테스트',  # Hangul test
        )
        for s in IDNA_TESTS:
            self.assertEqual(url()(self.form, DummyField(s)), None)

    def test_number_range(self):
        v = NumberRange(min=5, max=10)
        self.assertEqual(v(self.form, DummyField(7)), None)
        self.assertRaises(ValidationError, v, self.form, DummyField(None))
        self.assertRaises(ValidationError, v, self.form, DummyField(0))
        self.assertRaises(ValidationError, v, self.form, DummyField(12))
        self.assertRaises(ValidationError, v, self.form, DummyField(-5))

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
        self.assertRaises(Exception, text_type, message)
        self.assertTrue(equal_to('fieldname', message=message))
        self.assertTrue(length(min=1, message=message))
        self.assertTrue(NumberRange(1, 5, message=message))
        self.assertTrue(required(message=message))
        self.assertTrue(regexp('.+', message=message))
        self.assertTrue(email(message=message))
        self.assertTrue(ip_address(message=message))
        self.assertTrue(url(message=message))

    def test_any_of(self):
        self.assertEqual(AnyOf(['a', 'b', 'c'])(self.form, DummyField('b')), None)
        self.assertRaises(ValueError, AnyOf(['a', 'b', 'c']), self.form, DummyField(None))

        # Anyof in 1.0.1 failed on numbers for formatting the error with a TypeError
        check_num = AnyOf([1, 2, 3])
        self.assertEqual(check_num(self.form, DummyField(2)), None)
        self.assertRaises(ValueError, check_num, self.form, DummyField(4))

        # Test values_formatter
        formatter = lambda values: '::'.join(text_type(x) for x in reversed(values))
        checker = AnyOf([7, 8, 9], message='test %(values)s', values_formatter=formatter)
        self.assertEqual(grab_error_message(checker, self.form, DummyField(4)), 'test 9::8::7')

    def test_none_of(self):
        self.assertEqual(NoneOf(['a', 'b', 'c'])(self.form, DummyField('d')), None)
        self.assertRaises(ValueError, NoneOf(['a', 'b', 'c']), self.form, DummyField('a'))
