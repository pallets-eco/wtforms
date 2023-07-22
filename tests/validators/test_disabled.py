from tests.common import DummyPostData

from wtforms import Form
from wtforms import StringField
from wtforms.validators import Disabled


def test_disabled():
    class F(Form):
        disabled = StringField(validators=[Disabled()])

    form = F(disabled="foobar")
    assert "disabled" in form.disabled.flags
    assert (
        form.disabled()
        == '<input disabled id="disabled" name="disabled" type="text" value="foobar">'
    )
    assert form.validate()

    form = F(DummyPostData(disabled=["foobar"]))
    assert not form.validate()
