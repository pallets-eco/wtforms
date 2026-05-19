from enum import Enum

import pytest

from tests.common import DummyPostData
from wtforms import validators
from wtforms.fields import Choice
from wtforms.fields import SelectChoice
from wtforms.fields import SelectField
from wtforms.fields import SelectMultipleField
from wtforms.form import Form


def make_form(name="F", **fields):
    return type(str(name), (Form,), fields)


class F(Form):
    a = SelectMultipleField(
        choices=[
            SelectChoice("a", "hello"),
            SelectChoice("b", "bye"),
            SelectChoice("c", "something"),
        ],
        default=("a",),
    )
    b = SelectMultipleField(
        coerce=int,
        choices=[SelectChoice(1, "A"), SelectChoice(2, "B"), SelectChoice(3, "C")],
        default=("1", "3"),
    )


def test_defaults():
    form = F()
    assert form.a.data == ["a"]
    assert form.b.data == [1, 3]
    # Test for possible regression with null data
    form.a.data = None
    assert form.validate()
    assert list(form.a.iter_choices()) == [
        Choice("a", "hello", selected=False),
        Choice("b", "bye", selected=False),
        Choice("c", "something", selected=False),
    ]


def test_with_data():
    form = F(DummyPostData(a=["a", "c"]))
    assert form.a.data == ["a", "c"]
    assert list(form.a.iter_choices()) == [
        Choice("a", "hello", selected=True),
        Choice("b", "bye", selected=False),
        Choice("c", "something", selected=True),
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


def test_invalid_value_message():
    F = make_form(
        a=SelectMultipleField(
            choices=[SelectChoice(1, "Foo")],
            coerce=int,
            invalid_value_message="One or more submitted values could not be parsed.",
        )
    )
    form = F(DummyPostData(a=["x"]))
    assert not form.validate()
    assert form.a.errors == ["One or more submitted values could not be parsed."]


def test_invalid_choice_message():
    F = make_form(
        a=SelectMultipleField(
            choices=[SelectChoice("a", "Foo")],
            invalid_choice_message="Pick only the available options.",
        )
    )
    form = F(DummyPostData(a=["b"]))
    assert not form.validate()
    assert form.a.errors == ["Pick only the available options."]


def test_invalid_choice_message_callable():
    F = make_form(
        a=SelectMultipleField(
            choices=[SelectChoice("a", "Foo")],
            invalid_choice_message=lambda n: (
                f"Pick {n} available option."
                if n == 1
                else f"Pick only {n} available options."
            ),
        )
    )

    form = F(DummyPostData(a=["b"]))
    assert not form.validate()
    assert form.a.errors == ["Pick 1 available option."]

    form = F(DummyPostData(a=["b", "c"]))
    assert not form.validate()
    assert form.a.errors == ["Pick only 2 available options."]


def test_validate_choices_when_none():
    F = make_form(a=SelectMultipleField())
    form = F(DummyPostData(a="b"))
    with pytest.raises(TypeError, match="Choices cannot be None"):
        form.validate()


def test_dont_validate_choices():
    F = make_form(
        a=SelectMultipleField(choices=[SelectChoice("a", "Foo")], validate_choice=False)
    )
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
            choices=[SelectChoice("a", "hello"), SelectChoice("b", "bye")],
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
            choices=[SelectChoice("a", "hello"), SelectChoice("b", "bye")],
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
            choices=[
                SelectChoice(
                    "a", "Foo", render_kw={"title": "foobar", "data-foo": "bar"}
                )
            ]
        )
    )
    form = F(a="a")

    assert (
        '<option data-foo="bar" selected title="foobar" value="a">Foo</option>'
        in form.a()
    )
    assert list(form.a.iter_choices()) == [
        Choice(
            "a",
            "Foo",
            selected=True,
            render_kw={"title": "foobar", "data-foo": "bar"},
        )
    ]


def test_optgroup_option_render_kw():
    F = make_form(
        a=SelectMultipleField(
            choices=[
                SelectChoice(
                    "a",
                    "Foo",
                    render_kw={"title": "foobar", "data-foo": "bar"},
                    optgroup="hello",
                )
            ]
        )
    )
    form = F(a="a")

    assert (
        '<optgroup label="hello">'
        '<option data-foo="bar" selected title="foobar" value="a">Foo</option>'
        "</optgroup>" in form.a()
    )
    assert list(form.a.iter_choices()) == [
        Choice(
            "a",
            "Foo",
            selected=True,
            render_kw={"title": "foobar", "data-foo": "bar"},
        )
    ]


def test_can_supply_coercable_values_as_options():
    F = make_form(
        a=SelectMultipleField(
            choices=[SelectChoice("1", "One"), SelectChoice("2", "Two")],
            coerce=int,
        )
    )
    post_data = DummyPostData(a=["1", "2"])
    form = F(post_data)
    assert form.validate()
    assert form.a.data == [1, 2]


class _Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


def test_select_multiple_enum_round_trip():
    """``coerce=EnumCls`` works for SelectMultipleField too."""
    F = make_form(
        a=SelectMultipleField(choices=SelectChoice.from_enum(_Color), coerce=_Color)
    )
    form = F(DummyPostData(a=["RED", "BLUE"]))
    assert form.validate()
    assert form.a.data == [_Color.RED, _Color.BLUE]
