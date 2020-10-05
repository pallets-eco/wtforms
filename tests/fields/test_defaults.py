from wtforms.fields import StringField
from wtforms.form import Form
from wtforms.utils import unset_value


def test_defaults():
    expected = 42

    def default_callable():
        return expected

    test_value = StringField(default=expected).bind(Form(), "a")
    test_value.process(None)
    assert test_value.data == expected

    test_callable = StringField(default=default_callable).bind(Form(), "a")
    test_callable.process(None)
    assert test_callable.data == expected


def test_unset_value():
    assert str(unset_value) == "<unset value>"
    assert repr(unset_value) == "<unset value>"
    assert bool(unset_value) is False
    assert not unset_value
    assert unset_value.__nonzero__() is False
    assert unset_value.__bool__() is False
