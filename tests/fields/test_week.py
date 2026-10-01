from datetime import date

from tests.common import DummyPostData
from wtforms.fields import WeekField
from wtforms.form import Form


class F(Form):
    a = WeekField()
    b = WeekField(format="W%W %Y")
    c = WeekField(format="%Y-W%W-%w")


def test_basic():
    form = F(DummyPostData(a=["2023-W03"], b=["W03 2023"], c=["2023-W03-0"]))

    assert form.a.data == date(2023, 1, 16)
    assert "2023-W03" == form.a._value()
    assert form.a() == '<input id="a" name="a" type="week" value="2023-W03">'

    assert form.b.data == date(2023, 1, 16)
    assert form.b() == '<input id="b" name="b" type="week" value="W03 2023">'

    # %W makes the week count on the first monday of the year
    assert form.c.data == date(2023, 1, 22)
    assert form.c() == '<input id="c" name="c" type="week" value="2023-W03-0">'


def test_iso_week():
    class G(Form):
        a = WeekField()

    # HTML type=week is an ISO week. 2015-W01 starts on Monday 2014-12-29.
    # %Y-W%W counted the first Monday of 2015 and returned January 5.
    form = G(DummyPostData(a=["2015-W01"]))
    assert form.a.data == date(2014, 12, 29)
    assert form.a._value() == "2015-W01"

    form = G(DummyPostData(a=["2026-W53"]))
    assert form.a.data == date(2026, 12, 28)
    assert form.a._value() == "2026-W53"

    form = G(DummyPostData(a=["2020-W01"]))
    assert form.a.data == date(2019, 12, 30)
    assert form.a._value() == "2020-W01"


def test_invalid_data():
    form = F(DummyPostData(a=["2008-Wbb"]))

    assert not form.validate()
    assert 1 == len(form.a.process_errors)
    assert 1 == len(form.a.errors)
    assert "Not a valid week value." == form.a.process_errors[0]


def test_invalid_value_message():
    class G(Form):
        a = WeekField(invalid_value_message="Enter a week as YYYY-Www.")

    form = G(DummyPostData(a=["bogus"]))
    assert not form.validate()
    assert form.a.errors == ["Enter a week as YYYY-Www."]
