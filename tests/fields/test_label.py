from wtforms.fields import Label
from wtforms.fields import StringField
from wtforms.form import Form


def test_label():
    expected = """<label for="test">Caption</label>"""
    label = Label("test", "Caption")
    assert label() == expected
    assert str(label) == expected
    assert str(label) == expected
    assert label.__html__() == expected
    assert label().__html__() == expected
    assert label("hello") == """<label for="test">hello</label>"""
    assert StringField("hi").bind(Form(), "a").label.text == "hi"
    assert repr(label) == "Label('test', 'Caption')"


def test_auto_label():
    t1 = StringField().bind(Form(), "foo_bar")
    assert t1.label.text == "Foo Bar"

    t2 = StringField("").bind(Form(), "foo_bar")
    assert t2.label.text == ""


def test_override_for():
    label = Label("test", "Caption")
    assert label(for_="foo") == """<label for="foo">Caption</label>"""
    assert label(**{"for": "bar"}) == """<label for="bar">Caption</label>"""


def test_escaped_label_text():
    label = Label("test", '<script>alert("test");</script>')
    assert label(for_="foo") == (
        '<label for="foo">&lt;script&gt;'
        "alert(&#34;test&#34;);&lt;/script&gt;</label>"
    )

    assert label(**{"for": "bar"}) == (
        '<label for="bar">&lt;script&gt;'
        "alert(&#34;test&#34;);&lt;/script&gt;</label>"
    )
