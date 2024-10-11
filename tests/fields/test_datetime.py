import os
from datetime import datetime

from tests.common import DummyPostData
from wtforms.fields import DateTimeField
from wtforms.form import Form


def make_form(name="F", **fields):
    return type(str(name), (Form,), fields)


class F(Form):
    a = DateTimeField()
    b = DateTimeField(format="%Y-%m-%d %H:%M")
    c = DateTimeField(
        format="%#m/%#d/%Y %#I:%M" if os.name == "nt" else "%-m/%-d/%Y %-I:%M"
    )


def test_basic():
    d = datetime(2008, 5, 5, 4, 30, 0, 0)
    # Basic test with both inputs
    form = F(DummyPostData(a=["2008-05-05", "04:30:00"]))
    assert form.a.data == d
    assert (
        form.a()
        == """<input id="a" name="a" type="datetime" value="2008-05-05 04:30:00">"""
    )

    form = F(DummyPostData(b=["2008-05-05 04:30"]))
    assert form.b.data == d
    assert (
        form.b()
        == """<input id="b" name="b" type="datetime" value="2008-05-05 04:30">"""
    )

    form = F(DummyPostData(c=["5/5/2008 4:30"]))
    assert form.c.data == d
    assert (
        form.c() == """<input id="c" name="c" type="datetime" value="5/5/2008 4:30">"""
    )
    assert form.validate()

    # Test with a missing input
    form = F(DummyPostData(a=["2008-05-05"]))
    assert not form.validate()
    assert form.a.errors[0] == "Not a valid datetime value."

    form = F(a=d, b=d, c=d)
    assert form.validate()
    assert form.a._value() == "2008-05-05 04:30:00"
    assert form.b._value() == "2008-05-05 04:30"
    assert form.c._value() == "5/5/2008 4:30"


def test_microseconds():
    d = datetime(2011, 5, 7, 3, 23, 14, 424200)
    F = make_form(a=DateTimeField(format="%Y-%m-%d %H:%M:%S.%f"))
    form = F(DummyPostData(a=["2011-05-07 03:23:14.4242"]))
    assert d == form.a.data


def test_multiple_formats():
    d = datetime(2020, 3, 4, 5, 6)
    F = make_form(a=DateTimeField(format=["%Y-%m-%d %H:%M", "%Y%m%d%H%M"]))

    form = F(DummyPostData(a=["2020-03-04 05:06"]))
    assert d == form.a.data

    form = F(DummyPostData(a=["202003040506"]))
    assert d == form.a.data
