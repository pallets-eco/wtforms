from datetime import date

from tests.common import DummyPostData

from wtforms.fields import DateField
from wtforms.form import Form


class F(Form):
    a = DateField()
    b = DateField(format="%m/%d %Y")
    c = DateField(format="%-m/%-d %Y")


def test_basic():
    d = date(2008, 5, 7)
    form = F(DummyPostData(a=["2008-05-07"], b=["05/07", "2008"], c=["5/7 2008"]))
    assert form.a.data == d
    assert form.a._value() == "2008-05-07"
    assert form.b.data == d
    assert form.b._value() == "05/07 2008"
    assert form.c.data == d
    assert form.c._value() == "5/7 2008"


def test_failure():
    form = F(DummyPostData(a=["2008-bb-cc"], b=["hi"]))
    assert not form.validate()
    assert len(form.a.process_errors) == 1
    assert len(form.a.errors) == 1
    assert len(form.b.errors) == 1
    assert form.a.process_errors[0] == "Not a valid date value."
