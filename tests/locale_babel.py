from __future__ import unicode_literals
import babel

from decimal import Decimal, ROUND_UP
from unittest import TestCase
from wtforms import Form
from wtforms.fields import DecimalField
from wtforms.utils import unset_value
from tests.common import DummyPostData


class TestLocaleDecimal(TestCase):
    class F(Form):
        class Meta:
            locales = ['hi_IN', 'en_US']
        a = DecimalField(use_locale=True)

    def _format_test(self, expected, val, locales=unset_value):
        meta = None
        if locales is not unset_value:
            meta = {'locales': locales}
        form = self.F(meta=meta, a=Decimal(val))
        self.assertEqual(form.a._value(), expected)

    def test_typeerror(self):
        def build(**kw):
            form = self.F()
            DecimalField(
                use_locale=True,
                _form=form,
                _name='a',
                _translations=form._get_translations(),
                **kw
            )

        self.assertRaises(TypeError, build, places=2)
        self.assertRaises(TypeError, build, rounding=ROUND_UP)

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

    def _parse_test(self, raw_val, expected, locales=unset_value):
        meta = None
        if locales is not unset_value:
            meta = {'locales': locales}
        form = self.F(DummyPostData(a=raw_val), meta=meta)
        if not form.validate():
            raise AssertionError(
                'Expected value %r to parse as a decimal, instead got %r' % (
                    raw_val, form.a.errors,
                )
            )
        self.assertEqual(form.a.data, expected)

    def _fail_parse(self, raw_val, expected_error, locales=unset_value):
        meta = None
        if locales is not unset_value:
            meta = {'locales': locales}
        form = self.F(DummyPostData(a=raw_val), meta=meta)
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
