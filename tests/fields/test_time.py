from datetime import datetime

from tests.common import DummyPostData

from wtforms.fields import TimeField
from wtforms.form import Form


class F(Form):
    a = TimeField()
    b = TimeField(format="%H:%M")


def test_basic():
    d = datetime(2008, 5, 5, 4, 30, 0, 0).time()
    # Basic test with both inputs
    form = F(DummyPostData(a=["4:30"], b=["04:30"]))
    assert form.a.data == d
    assert form.a() == """<input id="a" name="a" type="time" value="4:30">"""
    assert form.b.data == d
    assert form.b() == """<input id="b" name="b" type="time" value="04:30">"""
    assert form.validate()

    # Test with a missing input
    form = F(DummyPostData(a=["04"]))
    assert not form.validate()
    assert form.a.errors[0] == "Not a valid time value."
