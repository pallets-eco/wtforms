from tests.common import DummyPostData

from wtforms.fields import StringField
from wtforms.form import Form


class F(Form):
    a = StringField(default=" hello", filters=[lambda x: x.strip()])
    b = StringField(default="42", filters=[int, lambda x: -x])


def test_working():
    form = F()
    assert form.a.data == "hello"
    assert form.b.data == -42
    assert form.validate()


def test_failure():
    form = F(DummyPostData(a=["  foo bar  "], b=["hi"]))
    assert form.a.data == "foo bar"
    assert form.b.data == "hi"
    assert len(form.b.process_errors) == 1
    assert not form.validate()


def test_extra():
    class F(Form):
        a = StringField(default=" hello ")
        b = StringField(default="42")

    def filter_a(value):
        return value.strip()

    def filter_b(value):
        return -int(value)

    form = F(extra_filters={"a": [filter_a], "b": [filter_b]})
    assert "hello" == form.a.data
    assert -42 == form.b.data
    assert form.validate()


def test_inline():
    class F(Form):
        a = StringField(default=" hello ")
        b = StringField(default="42")

        def filter_a(self, value):
            return value.strip()

        def filter_b(self, value):
            return -int(value)

    form = F()
    assert "hello" == form.a.data
    assert -42 == form.b.data
    assert form.validate()
