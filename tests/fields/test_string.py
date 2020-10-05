from tests.common import DummyPostData

from wtforms.fields import StringField
from wtforms.form import Form


class F(Form):
    a = StringField()


def test_string_field():
    form = F()
    assert form.a.data is None
    assert form.a() == """<input id="a" name="a" type="text" value="">"""
    form = F(DummyPostData(a=["hello"]))
    assert form.a.data == "hello"
    assert form.a() == """<input id="a" name="a" type="text" value="hello">"""
    form = F(DummyPostData(b=["hello"]))
    assert form.a.data is None
