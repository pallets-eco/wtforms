from tests.common import DummyPostData

from wtforms.fields import IntegerField
from wtforms.form import Form


class F(Form):
    a = IntegerField()
    b = IntegerField(default=48)


def test_integer_field():
    form = F(DummyPostData(a=["v"], b=["-15"]))
    assert form.a.data is None
    assert form.a.raw_data == ["v"]
    assert form.a() == """<input id="a" name="a" type="number" value="v">"""
    assert form.b.data == -15
    assert form.b() == """<input id="b" name="b" type="number" value="-15">"""
    assert not form.a.validate(form)
    assert form.b.validate(form)
    form = F(DummyPostData(a=[], b=[""]))
    assert form.a.data is None
    assert form.a.raw_data == []
    assert form.b.data is None
    assert form.b.raw_data == [""]
    assert not form.validate()
    assert len(form.b.process_errors) == 1
    assert len(form.b.errors) == 1
    form = F(b=9)
    assert form.b.data == 9
    assert form.a._value() == ""
    assert form.b._value() == "9"
    form = F(DummyPostData(), data=dict(b="v"))
    assert form.b.data is None
    assert form.a._value() == ""
    assert form.b._value() == ""
    assert not form.validate()
    assert len(form.b.process_errors) == 1
    assert len(form.b.errors) == 1
