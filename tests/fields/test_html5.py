import warnings
from datetime import date
from datetime import datetime
from decimal import Decimal

from tests.common import DummyPostData
from wtforms import validators
from wtforms.fields import Choice
from wtforms.fields import DateField
from wtforms.fields import DateTimeField
from wtforms.fields import DateTimeLocalField
from wtforms.fields import DecimalField
from wtforms.fields import DecimalRangeField
from wtforms.fields import EmailField
from wtforms.fields import FloatField
from wtforms.fields import IntegerField
from wtforms.fields import IntegerRangeField
from wtforms.fields import PasswordField
from wtforms.fields import SearchField
from wtforms.fields import StringField
from wtforms.fields import TelField
from wtforms.fields import TextAreaField
from wtforms.fields import URLField
from wtforms.form import Form
from wtforms.utils import unset_value


class F(Form):
    search = SearchField()
    telephone = TelField()
    url = URLField()
    email = EmailField()
    datetime = DateTimeField()
    date = DateField()
    dt_local = DateTimeLocalField()
    integer = IntegerField()
    float = FloatField()
    decimal = DecimalField()
    int_range = IntegerRangeField()
    decimal_range = DecimalRangeField()


def _build_value(key, form_input, expected_html, data=unset_value):
    if data is unset_value:
        data = form_input
    if expected_html.startswith("type="):
        expected_html = (
            f'<input id="{key}" name="{key}" {expected_html} value="{form_input}">'
        )
    return {
        "key": key,
        "form_input": form_input,
        "expected_html": expected_html,
        "data": data,
    }


def test_simple():
    b = _build_value
    VALUES = (
        b("search", "search", 'type="search"'),
        b("telephone", "123456789", 'type="tel"'),
        b("url", "http://wtforms.simplecodes.com/", 'type="url"'),
        b("email", "foo@bar.com", 'type="email"'),
        b(
            "datetime",
            "2013-09-05 00:23:42",
            'type="datetime"',
            datetime(2013, 9, 5, 0, 23, 42),
        ),
        b("date", "2013-09-05", 'type="date"', date(2013, 9, 5)),
        b(
            "dt_local",
            "2013-09-05 00:23:42",
            'type="datetime-local"',
            datetime(2013, 9, 5, 0, 23, 42),
        ),
        b(
            "integer",
            "42",
            '<input id="integer" name="integer" type="number" value="42">',
            42,
        ),
        b(
            "float",
            "1.234",
            '<input id="float" name="float" step="any" type="number" value="1.234">',
            1.234,
        ),
        b(
            "decimal",
            "43.5",
            '<input id="decimal" name="decimal" step="any" type="number" value="43.5">',
            Decimal("43.5"),
        ),
        b(
            "int_range",
            "4",
            '<input id="int_range" name="int_range" type="range" value="4">',
            4,
        ),
        b(
            "decimal_range",
            "58",
            '<input id="decimal_range" name="decimal_range" '
            'step="any" type="range" value="58">',
            58,
        ),
    )
    formdata = DummyPostData()
    kw = {}
    for item in VALUES:
        formdata[item["key"]] = item["form_input"]
        kw[item["key"]] = item["data"]

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        form = F(formdata)
    for item in VALUES:
        field = form[item["key"]]
        render_value = field()
        assert render_value == item["expected_html"], (
            f"Field {item['key']} render mismatch: "
        )
        "{render_value} != {item['expected_html']}"
        assert field.data == item["data"], (
            "Field {item['key']} data mismatch: {field.data} != {item['data']}"
        )


class G(Form):
    v1 = [validators.Length(min=1)]
    v2 = [validators.Length(min=1, max=3)]
    string1 = StringField(validators=v1)
    string2 = StringField(validators=v2)
    password1 = PasswordField(validators=v1)
    password2 = PasswordField(validators=v2)
    textarea1 = TextAreaField(validators=v1)
    textarea2 = TextAreaField(validators=v2)
    search1 = SearchField(validators=v1)
    search2 = SearchField(validators=v2)

    v3 = [validators.NumberRange(min=1)]
    v4 = [validators.NumberRange(min=1, max=3)]
    integer1 = IntegerField(validators=v3)
    integer2 = IntegerField(validators=v4)
    integerrange1 = IntegerRangeField(validators=v3)
    integerrange2 = IntegerRangeField(validators=v4)
    decimal1 = DecimalField(validators=v3)
    decimal2 = DecimalField(validators=v4)
    decimalrange1 = DecimalRangeField(validators=v3)
    decimalrange2 = DecimalRangeField(validators=v4)


def test_minlength_maxlength():
    form = G()
    assert (
        form.string1()
        == '<input id="string1" minlength="1" name="string1" type="text" value="">'
    )

    assert (
        form.string2() == '<input id="string2" maxlength="3" minlength="1"'
        ' name="string2" type="text" value="">'
    )

    assert (
        form.password1() == '<input id="password1" minlength="1"'
        ' name="password1" type="password" value="">'
    )

    assert (
        form.password2() == '<input id="password2" maxlength="3" minlength="1"'
        ' name="password2" type="password" value="">'
    )

    assert (
        form.textarea1() == '<textarea id="textarea1" minlength="1"'
        ' name="textarea1">\r\n</textarea>'
    )

    assert (
        form.textarea2() == '<textarea id="textarea2" maxlength="3" minlength="1"'
        ' name="textarea2">\r\n</textarea>'
    )

    assert (
        form.search1() == '<input id="search1" minlength="1"'
        ' name="search1" type="search" value="">'
    )

    assert (
        form.search2() == '<input id="search2" maxlength="3" minlength="1"'
        ' name="search2" type="search" value="">'
    )


def test_min_max():
    form = G()
    assert (
        form.integer1()
        == '<input id="integer1" min="1" name="integer1" type="number" value="">'
    )
    assert (
        form.integer2() == '<input id="integer2" max="3" min="1"'
        ' name="integer2" type="number" value="">'
    )

    assert (
        form.integerrange1() == '<input id="integerrange1" min="1"'
        ' name="integerrange1" type="range" value="">'
    )

    assert (
        form.integerrange2() == '<input id="integerrange2" max="3" min="1"'
        ' name="integerrange2" type="range" value="">'
    )

    assert (
        form.decimal1() == '<input id="decimal1" min="1"'
        ' name="decimal1" step="any" type="number" value="">'
    )

    assert (
        form.decimal2() == '<input id="decimal2" max="3" min="1"'
        ' name="decimal2" step="any" type="number" value="">'
    )

    assert (
        form.decimalrange1() == '<input id="decimalrange1" min="1"'
        ' name="decimalrange1" step="any" type="range" value="">'
    )

    assert (
        form.decimalrange2() == '<input id="decimalrange2" max="3" min="1"'
        ' name="decimalrange2" step="any" type="range" value="">'
    )


class H(Form):
    pattern_validators = [validators.Regexp(r"^[A-Z]+$", html_pattern=True)]
    string = StringField(validators=pattern_validators)
    password = PasswordField(validators=pattern_validators)
    search = SearchField(validators=pattern_validators)
    telephone = TelField(validators=pattern_validators)
    url = URLField(validators=pattern_validators)
    email = EmailField(validators=pattern_validators)


def test_pattern():
    form = H()
    assert form.string() == (
        '<input id="string" name="string" pattern="^[A-Z]+$" type="text" value="">'
    )
    assert form.password() == (
        '<input id="password" name="password" pattern="^[A-Z]+$"'
        ' type="password" value="">'
    )
    assert form.search() == (
        '<input id="search" name="search" pattern="^[A-Z]+$" type="search" value="">'
    )
    assert form.telephone() == (
        '<input id="telephone" name="telephone" pattern="^[A-Z]+$" type="tel" value="">'
    )
    assert form.url() == (
        '<input id="url" name="url" pattern="^[A-Z]+$" type="url" value="">'
    )
    assert form.email() == (
        '<input id="email" name="email" pattern="^[A-Z]+$" type="email" value="">'
    )


def test_pattern_disabled_by_default():
    """Without ``html_pattern``, the regex source is not exposed in HTML."""

    class I(Form):  # noqa: E742
        string = StringField(validators=[validators.Regexp(r"^[A-Z]+$")])

    form = I()
    assert "pattern" not in form.string()


class J(Form):
    string5 = StringField(
        datalist="languages",
        choices=[
            Choice("deu", "German"),
            Choice("eng", "English"),
            Choice("fra", "French"),
            Choice("jpn", "Japanese"),
            Choice("nld", "Dutch"),
            Choice("spa", "Spanish"),
        ],
    )
    search5 = SearchField(datalist="languages")  # Reusing choices of string5
    email5 = EmailField(
        datalist="emails",
        choices=[
            Choice("support@example.org", "Support Team"),
            Choice("noreply@example.org", "No Reply"),
            Choice("finance@example.org", "Financial Department"),
        ],
    )
    tel5 = TelField(
        datalist="tels",
        choices=[
            Choice("+316 1234 5678", "Dutch Office"),
            Choice("+326 1234 5678", "Belgium Office"),
            Choice("+346 1234 5678", "Spanish Office"),
        ],
    )
    url5 = URLField(
        datalist="urls",
        choices=[
            Choice("https://example.org", "Generic Website"),
            Choice("https://example.org/issues", "Issues Website"),
            Choice("https://example.org/docs", "Documentation Website"),
        ],
    )


def test_datalist():
    form = J()
    assert (
        form.string5()
        == """<input id="string5" list="languages" name="string5" type="text" value=""><datalist id="languages"><option value="deu" label="German"><option value="eng" label="English"><option value="fra" label="French"><option value="jpn" label="Japanese"><option value="nld" label="Dutch"><option value="spa" label="Spanish"></datalist>"""
    )
    assert (
        form.search5()
        == """<input id="search5" list="languages" name="search5" type="search" value="">"""
    )
    assert (
        form.email5()
        == """<input id="email5" list="emails" name="email5" type="email" value=""><datalist id="emails"><option value="support@example.org" label="Support Team"><option value="noreply@example.org" label="No Reply"><option value="finance@example.org" label="Financial Department"></datalist>"""
    )
    assert (
        form.tel5()
        == """<input id="tel5" list="tels" name="tel5" type="tel" value=""><datalist id="tels"><option value="+316 1234 5678" label="Dutch Office"><option value="+326 1234 5678" label="Belgium Office"><option value="+346 1234 5678" label="Spanish Office"></datalist>"""
    )
    assert (
        form.url5()
        == """<input id="url5" list="urls" name="url5" type="url" value=""><datalist id="urls"><option value="https://example.org" label="Generic Website"><option value="https://example.org/issues" label="Issues Website"><option value="https://example.org/docs" label="Documentation Website"></datalist>"""
    )
