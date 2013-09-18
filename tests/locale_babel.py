from __future__ import unicode_literals
import babel

from decimal import Decimal
from unittest import TestCase
from wtforms.form import _unset_value
from wtforms import Form
from wtforms.fields.core import DecimalField


class DummyPostData(dict):
    def getlist(self, key):
        v = self[key]
        if not isinstance(v, (list, tuple)):
            v = [v]
        return v


class TestLocaleDecimal(TestCase):
    class F(Form):
        LOCALES = ['hi_IN', 'en_US']
        a = DecimalField(use_locale=True)

    def _format_test(self, expected, val, LOCALES=_unset_value):
        form = self.F(LOCALES=LOCALES, a=Decimal(val))
        self.assertEqual(form.a._value(), expected)

    def test_formatting(self):
        val = Decimal('123456.789')
        neg = Decimal('-5.2')
        self._format_test('1,23,456.789', val)
        self._format_test('-12,52,378.2', '-1252378.2')
        self._format_test('123,456.789', val, ['en_US'])
        self._format_test('-5.2', neg, ['en_US'])
        self._format_test('123.456,789', val, ['es_ES'])
        self._format_test('123.456,789', val, ['de_DE'])
        self._format_test('-5,2', neg, ['de_DE'])
        self._format_test("-12'345.2", '-12345.2', ['de_CH'])

    def _parse_test(self, raw_val, expected, LOCALES=_unset_value):
        form = self.F(DummyPostData(a=raw_val), LOCALES=LOCALES)
        if not form.validate():
            raise AssertionError(
                'Expected value %r to parse as a decimal, instead got %r' % (
                    raw_val, form.a.errors,
                )
            )
        self.assertEqual(form.a.data, expected)

    def _fail_parse(self, raw_val, expected_error, LOCALES=_unset_value):
        form = self.F(DummyPostData(a=raw_val), LOCALES=LOCALES)
        assert not form.validate()
        self.assertEqual(form.a.errors[0], expected_error)

    def test_parsing(self):
        expected = Decimal('123456.789')
        self._parse_test('1,23,456.789', expected)
        self._parse_test('1,23,456.789', expected, ['en_US'])
        self._parse_test('1.23.456,789', expected, ['de_DE'])
        self._parse_test("1'23'456.789", expected, ['de_CH'])


        self._fail_parse('1,23,456.5', 'Keine g\xfcltige Dezimalzahl', ['de_DE'])
        self._fail_parse('1.234.567,5', 'Not a valid decimal value', ['en_US'])
