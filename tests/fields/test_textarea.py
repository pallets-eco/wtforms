from wtforms.fields import TextAreaField
from wtforms.form import Form


class F(Form):
    a = TextAreaField(default="LE DEFAULT")


def test_textarea_field():
    form = F()
    assert form.a() == """<textarea id="a" name="a">\r\nLE DEFAULT</textarea>"""
