import pytest
from tests.common import DummyPostData

from wtforms import validators
from wtforms.fields import SelectField
from wtforms.fields import SelectMultipleField
from wtforms.form import Form


def make_form(name="F", **fields):
    return type(str(name), (Form,), fields)


class F(Form):
    a = SelectMultipleField(
        choices=[("a", "hello"), ("b", "bye"), ("c", "something")], default=("a",)
    )
    b = SelectMultipleField(
        coerce=int, choices=[(1, "A"), (2, "B"), (3, "C")], default=("1", "3")
    )


def test_defaults():
    form = F()
    assert form.a.data == ["a"]
    assert form.b.data == [1, 3]
    # Test for possible regression with null data
    form.a.data = None
    assert form.validate()
    assert list(form.a.iter_choices()) == [(v, l, False, {}) for v, l in form.a.choices]


def test_with_data():
    form = F(DummyPostData(a=["a", "c"]))
    assert form.a.data == ["a", "c"]
    assert list(form.a.iter_choices()) == [
        ("a", "hello", True, {}),
        ("b", "bye", False, {}),
        ("c", "something", True, {}),
    ]
    assert form.b.data == []
    form = F(DummyPostData(b=["1", "2"]))
    assert form.b.data == [1, 2]
    assert form.validate()
    form = F(DummyPostData(b=["1", "2", "4"]))
    assert form.b.data == [1, 2, 4]
    assert not form.validate()


def test_coerce_fail():
    form = F(b=["a"])
    assert form.validate()
    assert form.b.data is None
    form = F(DummyPostData(b=["fake"]))
    assert not form.validate()
    assert form.b.data == [1, 3]


def test_callable_choices():
    def choices():
        return ["foo", "bar"]

    F = make_form(a=SelectField(choices=choices))
    form = F(a="bar")

    assert list(str(x) for x in form.a) == [
        '<option value="foo">foo</option>',
        '<option selected value="bar">bar</option>',
    ]


def test_choice_shortcut():
    F = make_form(a=SelectMultipleField(choices=["foo", "bar"]))
    form = F(a=["bar"])
    assert form.validate()
    assert '<option value="foo">foo</option>' in form.a()


@pytest.mark.parametrize("choices", [[], None])
def test_empty_choice(choices):
    F = make_form(a=SelectMultipleField(choices=choices))
    form = F(a="bar")
    assert form.a() == '<select id="a" multiple name="a"></select>'


def test_validate_choices_when_empty():
    F = make_form(a=SelectMultipleField(choices=[]))
    form = F(DummyPostData(a=["b"]))
    assert not form.validate()
    assert form.a.data == ["b"]
    assert len(form.a.errors) == 1
    assert form.a.errors[0] == "'b' is not a valid choice for this field."


def test_validate_choices_when_none():
    F = make_form(a=SelectMultipleField())
    form = F(DummyPostData(a="b"))
    with pytest.raises(TypeError, match="Choices cannot be None"):
        form.validate()


def test_dont_validate_choices():
    F = make_form(a=SelectMultipleField(choices=[("a", "Foo")], validate_choice=False))
    form = F(DummyPostData(a=["b"]))
    assert form.validate()
    assert form.a.data == ["b"]
    assert len(form.a.errors) == 0


def test_choices_can_be_none_when_choice_validation_is_disabled():
    F = make_form(a=SelectMultipleField(validate_choice=False))
    form = F(DummyPostData(a="b"))
    assert form.validate()


def test_requried_flag():
    F = make_form(
        c=SelectMultipleField(
            choices=[("a", "hello"), ("b", "bye")],
            validators=[validators.InputRequired()],
        )
    )
    form = F(DummyPostData(c=["a"]))
    assert form.c() == (
        '<select id="c" multiple name="c" required>'
        '<option selected value="a">hello</option>'
        '<option value="b">bye</option>'
        "</select>"
    )


def test_required_validator():
    F = make_form(
        c=SelectMultipleField(
            choices=[("a", "hello"), ("b", "bye")],
            validators=[validators.InputRequired()],
        )
    )
    form = F(DummyPostData(c=["a"]))
    assert form.validate()
    assert form.c.errors == []
    form = F()
    assert form.validate() is False
    assert form.c.errors == ["This field is required."]


def test_render_kw_preserved():
    F = make_form(
        a=SelectMultipleField(choices=[("foo"), ("bar")], render_kw=dict(disabled=True))
    )
    form = F()
    assert form.a() == (
        '<select disabled id="a" multiple name="a">'
        '<option value="foo">foo</option>'
        '<option value="bar">bar</option>'
        "</select>"
    )


def test_option_render_kw():
    F = make_form(
        a=SelectMultipleField(
            choices=[("a", "Foo", {"title": "foobar", "data-foo": "bar"})]
        )
    )
    form = F(a="a")

    assert (
        '<option data-foo="bar" selected title="foobar" value="a">Foo</option>'
        in form.a()
    )
    assert list(form.a.iter_choices()) == [
        ("a", "Foo", True, {"title": "foobar", "data-foo": "bar"})
    ]


def test_optgroup_option_render_kw():
    F = make_form(
        a=SelectMultipleField(
            choices={"hello": [("a", "Foo", {"title": "foobar", "data-foo": "bar"})]}
        )
    )
    form = F(a="a")

    assert (
        '<optgroup label="hello">'
        '<option data-foo="bar" selected title="foobar" value="a">Foo</option>'
        "</optgroup>" in form.a()
    )
    assert list(form.a.iter_choices()) == [
        ("a", "Foo", True, {"title": "foobar", "data-foo": "bar"})
    ]


def test_can_supply_coercable_values_as_options():
    F = make_form(
        a=SelectMultipleField(
            choices=[("1", "One"), ("2", "Two")],
            coerce=int,
        )
    )
    post_data = DummyPostData(a=["1", "2"])
    form = F(post_data)
    assert form.validate()
    assert form.a.data == [1, 2]
