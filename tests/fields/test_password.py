from wtforms import widgets
from wtforms.fields import PasswordField
from wtforms.form import Form


class F(Form):
    a = PasswordField(
        widget=widgets.PasswordInput(hide_value=False), default="LE DEFAULT"
    )
    b = PasswordField(default="Hai")


def test_password_field():
    form = F()
    assert form.a() == """<input id="a" name="a" type="password" value="LE DEFAULT">"""
    assert form.b() == """<input id="b" name="b" type="password" value="">"""
