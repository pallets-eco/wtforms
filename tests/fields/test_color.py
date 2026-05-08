from wtforms import widgets
from wtforms.fields import ColorField
from wtforms.form import Form


class F(Form):
    a = ColorField(widget=widgets.ColorInput(), default="#ff0000")
    b = ColorField(default="#00ff00")


def test_color_field():
    form = F()
    assert form.a() == """<input id="a" name="a" type="color" value="#ff0000">"""
    assert form.b() == """<input id="b" name="b" type="color" value="#00ff00">"""
