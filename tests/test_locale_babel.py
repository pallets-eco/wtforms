from decimal import Decimal
from decimal import ROUND_UP

import pytest
from tests.common import DummyPostData

from wtforms import Form
from wtforms.fields import DecimalField
from wtforms.utils import unset_value


class F(Form):
    class Meta:
        locales = ["hi_IN", "en_US"]

    a = DecimalField(use_locale=True)


def _format_test(expected, val, locales=unset_value):
    meta = None
    if locales is not unset_value:
        meta = {"locales": locales}
    form = F(meta=meta, a=Decimal(val))
    assert form.a._value() == expected


def test_typeerror():
    def build(**kw):
        form = F()
        DecimalField(
            use_locale=True,
            name="a",
            _form=form,
            _translations=form.meta.get_translations(form),
            **kw,
        )

    with pytest.raises(TypeError):
        build(places=2)

    with pytest.raises(TypeError):
        build(rounding=ROUND_UP)


def test_formatting():
    val = Decimal("123456.789")
    neg = Decimal("-5.2")
    _format_test("1,23,456.789", val)
    _format_test("-12,52,378.2", "-1252378.2")
    _format_test("123,456.789", val, ["en_US"])
    _format_test("-5.2", neg, ["en_US"])
    _format_test("123.456,789", val, ["es_ES"])
    _format_test("123.456,789", val, ["de_DE"])
    _format_test("-5,2", neg, ["de_DE"])
    _format_test("-12’345.2", "-12345.2", ["de_CH"])


def _parse_test(raw_val, expected, locales=unset_value):
    meta = None
    if locales is not unset_value:
        meta = {"locales": locales}
    form = F(DummyPostData(a=raw_val), meta=meta)
    assert (
        form.validate()
    ), f"Expected value {raw_val} to parse as a decimal, instead got {form.a.errors}"
    assert form.a.data == expected


def _fail_parse(raw_val, expected_error, locales=unset_value):
    meta = None
    if locales is not unset_value:
        meta = {"locales": locales}
    form = F(DummyPostData(a=raw_val), meta=meta)
    assert not form.validate()
    assert form.a.errors[0] == expected_error


def test_parsing():
    expected = Decimal("123456.789")
    _parse_test("1,23,456.789", expected)
    _parse_test("1,23,456.789", expected, ["en_US"])
    _parse_test("1.23.456,789", expected, ["de_DE"])
    _parse_test("1’23’456.789", expected, ["de_CH"])

    _fail_parse("1,23,456.5", "Keine g\xfcltige Dezimalzahl.", ["de_DE"])
    _fail_parse("1.234.567,5", "Not a valid decimal value.", ["en_US"])
