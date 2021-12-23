from datetime import datetime

from tests.common import DummyPostData

from wtforms.fields import DateTimeLocalField
from wtforms.form import Form


def make_form(name="F", **fields):
    return type(str(name), (Form,), fields)


class F(Form):
    a = DateTimeLocalField()
    b = DateTimeLocalField(format="%Y-%m-%d %H:%M")
    c = DateTimeLocalField(format="%-m/%-d/%Y %-I:%M")


def test_basic():
    d = datetime(2008, 5, 5, 4, 30, 0, 0)
    # Basic test with both inputs
    form = F(
        DummyPostData(
            a=["2008-05-05", "04:30:00"], b=["2008-05-05 04:30"], c=["5/5/2008 4:30"]
        )
    )
    assert form.a.data == d
    assert (
        form.a()
        == '<input id="a" name="a" type="datetime-local" value="2008-05-05 04:30:00">'
    )
    assert form.b.data == d
    assert (
        form.b()
        == '<input id="b" name="b" type="datetime-local" value="2008-05-05 04:30">'
    )
    assert form.c.data == d
    assert (
        form.c()
        == '<input id="c" name="c" type="datetime-local" value="5/5/2008 4:30">'
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
    F = make_form(a=DateTimeLocalField(format="%Y-%m-%d %H:%M:%S.%f"))
    form = F(DummyPostData(a=["2011-05-07 03:23:14.4242"]))
    assert d == form.a.data


def test_separators():
    dt = datetime(2008, 5, 5, 4, 30, 0, 0)

    form = F(DummyPostData(a=["2008-05-05 04:30:00"]))
    assert form.a.data == dt
    assert form.validate()

    form = F(DummyPostData(a=["2008-05-05T04:30:00"]))
    assert form.a.data == dt
    assert form.validate()
