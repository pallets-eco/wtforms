from markupsafe import Markup

from tests.common import DummyPostData
from wtforms.fields import ButtonField
from wtforms.form import Form


class F(Form):
    a = ButtonField("Label")
    b = ButtonField("Save", default="save")
    c = ButtonField("Delete", render_kw={"formaction": "/delete", "value": "delete"})


def test_button_field():
    """Default rendering uses the field label as visible text and an empty value."""
    assert F().a() == '<button id="a" name="a" type="submit" value="">Label</button>'


def test_button_field_default_value():
    """``default`` populates the rendered ``value`` attribute, not ``data``."""
    form = F()
    assert form.b.data is None
    assert (
        form.b() == '<button id="b" name="b" type="submit" value="save">Save</button>'
    )


def test_button_field_render_kw():
    """``render_kw`` attributes flow through to the rendered button."""
    assert F().c() == (
        '<button formaction="/delete" id="c" name="c" type="submit"'
        ' value="delete">Delete</button>'
    )


def test_button_field_label_override():
    """``label=`` at render time overrides the visible button text."""
    assert F().a(label="Override") == (
        '<button id="a" name="a" type="submit" value="">Override</button>'
    )


def test_button_field_with_postdata():
    """A clicked button stores its submitted value as ``data``."""
    form = F(DummyPostData(a="save-add"))
    assert form.a.raw_data == ["save-add"]
    assert form.a.data == "save-add"


def test_button_field_with_empty_value():
    """A clicked button with empty value stores an empty string, not ``None``."""
    form = F(DummyPostData(a=""))
    assert form.a.raw_data == [""]
    assert form.a.data == ""


def test_button_field_not_pressed():
    """An unclicked button has ``data is None`` and no raw data."""
    form = F(DummyPostData(other="x"))
    assert form.a.raw_data == []
    assert form.a.data is None


def test_button_field_label_markup_at_render():
    """``Markup`` passed as render-time ``label`` is preserved unescaped."""
    assert F().a(label=Markup('<i class="icon"></i> Save')) == (
        '<button id="a" name="a" type="submit" value="">'
        '<i class="icon"></i> Save</button>'
    )


def test_button_field_label_markup_at_declaration():
    """``Markup`` passed as field label at declaration is preserved unescaped."""

    class G(Form):
        a = ButtonField(Markup("<i></i> Save"))

    assert G().a() == (
        '<button id="a" name="a" type="submit" value=""><i></i> Save</button>'
    )


def test_button_field_label_str_is_escaped():
    """A plain ``str`` label is HTML-escaped at render time."""
    assert F().a(label="<script>x</script>") == (
        '<button id="a" name="a" type="submit" value="">'
        "&lt;script&gt;x&lt;/script&gt;</button>"
    )
