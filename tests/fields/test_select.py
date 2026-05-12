import sys
from enum import Enum
from enum import IntEnum

import pytest

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    StrEnum = None

from tests.common import DummyPostData
from wtforms import StringField
from wtforms import validators
from wtforms import widgets
from wtforms.fields import Choice
from wtforms.fields import Field
from wtforms.fields import SelectChoice
from wtforms.fields import SelectField
from wtforms.form import Form


def make_form(name="F", **fields):
    return type(str(name), (Form,), fields)


def test_select_field_copies_choices():
    class F(Form):
        items = SelectField(choices=[])

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def add_choice(self, choice):
            self.items.choices.append(Choice(choice, choice))

    f1 = F()
    f2 = F()

    f1.add_choice("a")
    f2.add_choice("b")

    assert f1.items.choices == [Choice("a", "a")]
    assert f2.items.choices == [Choice("b", "b")]
    assert f1.items.choices is not f2.items.choices


class F(Form):
    a = SelectField(
        choices=[
            Choice("a", "hello"),
            Choice("btest", "bye"),
        ],
        default="a",
    )
    b = SelectField(
        choices=[
            Choice(1, "Item 1"),
            Choice(2, "Item 2"),
        ],
        coerce=int,
        option_widget=widgets.TextInput(),
    )


def test_defaults():
    form = F()
    assert form.a.data == "a"
    assert form.b.data is None
    assert form.validate() is False
    assert form.a() == (
        '<select id="a" name="a"><option selected value="a">hello</option>'
        '<option value="btest">bye</option></select>'
    )
    assert form.b() == (
        '<select id="b" name="b"><option value="1">Item 1</option>'
        '<option value="2">Item 2</option></select>'
    )


def test_with_data():
    form = F(DummyPostData(a=["btest"]))
    assert form.a.data == "btest"
    assert form.a() == (
        '<select id="a" name="a"><option value="a">hello</option>'
        '<option selected value="btest">bye</option></select>'
    )


def test_value_coercion():
    form = F(DummyPostData(b=["2"]))
    assert form.b.data == 2
    assert form.b.validate(form)
    form = F(DummyPostData(b=["b"]))
    assert form.b.data is None
    assert not form.b.validate(form)


def test_iterable_options():
    form = F()
    first_option = list(form.a)[0]
    assert isinstance(first_option, Field)
    assert list(str(x) for x in form.a) == [
        '<option selected value="a">hello</option>',
        '<option value="btest">bye</option>',
    ]
    assert isinstance(first_option.widget, widgets.Option)
    assert isinstance(list(form.b)[0].widget, widgets.TextInput)
    assert (
        first_option(disabled=True)
        == '<option disabled selected value="a">hello</option>'
    )


def test_option_subfields_carry_parent_form():
    """Option subfields yielded by ``__iter__`` expose the enclosing form,
    matching the propagation already done for ``_meta``."""
    F = make_form(a=SelectField(choices=[Choice("a", "Foo"), Choice("b", "Bar")]))
    form = F()
    for opt in form.a:
        assert opt._form is form


def test_default_coerce():
    F = make_form(a=SelectField(choices=[Choice("a", "Foo")]))
    form = F(DummyPostData(a=[]))
    assert not form.validate()
    assert form.a.data is None
    assert len(form.a.errors) == 1
    assert form.a.errors[0] == "Not a valid choice."


def test_validate_choices():
    F = make_form(a=SelectField(choices=[Choice("a", "Foo")]))
    form = F(DummyPostData(a=["b"]))
    assert not form.validate()
    assert form.a.data == "b"
    assert len(form.a.errors) == 1
    assert form.a.errors[0] == "Not a valid choice."


def test_validate_choices_when_empty():
    F = make_form(a=SelectField(choices=[]))
    form = F(DummyPostData(a=["b"]))
    assert not form.validate()
    assert form.a.data == "b"
    assert len(form.a.errors) == 1
    assert form.a.errors[0] == "Not a valid choice."


def test_invalid_value_message():
    F = make_form(
        a=SelectField(
            choices=[Choice(1, "Foo")],
            coerce=int,
            invalid_value_message="Submitted value could not be parsed.",
        )
    )
    form = F(DummyPostData(a=["x"]))
    assert not form.validate()
    assert form.a.errors == ["Submitted value could not be parsed."]


def test_invalid_choice_message():
    F = make_form(
        a=SelectField(
            choices=[Choice("a", "Foo")],
            invalid_choice_message="Pick one of the available options.",
        )
    )
    form = F(DummyPostData(a=["b"]))
    assert not form.validate()
    assert form.a.errors == ["Pick one of the available options."]


def test_validate_choices_when_none():
    F = make_form(a=SelectField())
    form = F(DummyPostData(a="b"))
    with pytest.raises(TypeError, match="Choices cannot be None"):
        form.validate()


def test_dont_validate_choices():
    F = make_form(a=SelectField(choices=[Choice("a", "Foo")], validate_choice=False))
    form = F(DummyPostData(a=["b"]))
    assert form.validate()
    assert form.a.data == "b"
    assert len(form.a.errors) == 0


def test_choices_can_be_none_when_choice_validation_is_disabled():
    F = make_form(a=SelectField(validate_choice=False))
    form = F(DummyPostData(a="b"))
    assert form.validate()


def test_choice_shortcut():
    F = make_form(a=SelectField(choices=["foo", "bar"], validate_choice=False))
    form = F(a="bar")
    assert '<option value="foo">foo</option>' in form.a()


def test_choice_shortcut_post():
    F = make_form(a=SelectField(choices=["foo", "bar"]))
    form = F(DummyPostData(a=["foo"]))
    assert form.validate()
    assert form.a.data == "foo"
    assert len(form.a.errors) == 0


@pytest.mark.parametrize("choices", [[], None])
def test_empty_choice(choices):
    F = make_form(a=SelectField(choices=choices, validate_choice=False))
    form = F(a="bar")
    assert form.a() == '<select id="a" name="a"></select>'


def test_callable_choices():
    def choices():
        return ["foo", "bar"]

    F = make_form(a=SelectField(choices=choices))
    form = F(a="bar")

    assert list(str(x) for x in form.a) == [
        '<option value="foo">foo</option>',
        '<option selected value="bar">bar</option>',
    ]


def test_callable_choices_receives_form_and_field():
    """A ``(form, field)`` callable receives the bound form and field."""
    captured = []

    def choices(form, field):
        captured.append((form, field))
        return ["foo", "bar"]

    F = make_form(a=SelectField(choices=choices))
    form = F(a="bar")

    assert list(str(x) for x in form.a) == [
        '<option value="foo">foo</option>',
        '<option selected value="bar">bar</option>',
    ]
    assert captured == [(form, form.a)]


def test_callable_choices_variadic_receives_form_and_field():
    """Variadic ``*args, **kwargs`` callables also receive ``(form, field)``."""
    captured = []

    def choices(*args, **kwargs):
        captured.append(args)
        return ["foo"]

    F = make_form(a=SelectField(choices=choices))
    form = F()

    list(form.a)
    assert captured[0] == (form, form.a)


def test_callable_choices_invoked_after_process():
    """The callable sees data from every field, regardless of declaration order."""
    captured = []

    def choices(form, field):
        captured.append((field.data, form.b.data))
        return ["foo", "bar"]

    F = make_form(a=SelectField(choices=choices), b=StringField())
    form = F(DummyPostData(a="foo", b="hello"))

    list(form.a)
    assert captured == [("foo", "hello")]


def test_requried_flag():
    F = make_form(
        c=SelectField(
            choices=[Choice("a", "hello"), Choice("b", "bye")],
            validators=[validators.InputRequired()],
        )
    )
    form = F(DummyPostData(c="a"))
    assert form.c() == (
        '<select id="c" name="c" required>'
        '<option selected value="a">hello</option>'
        '<option value="b">bye</option>'
        "</select>"
    )


def test_required_validator():
    F = make_form(
        c=SelectField(
            choices=[Choice("a", "hello"), Choice("b", "bye")],
            validators=[validators.InputRequired()],
        )
    )
    form = F(DummyPostData(c="b"))
    assert form.validate()
    assert form.c.errors == []
    form = F()
    assert form.validate() is False
    assert form.c.errors == ["This field is required."]


def test_render_kw_preserved():
    F = make_form(
        a=SelectField(choices=[("foo"), ("bar")], render_kw=dict(disabled=True))
    )
    form = F()
    assert form.a() == (
        '<select disabled id="a" name="a">'
        '<option value="foo">foo</option>'
        '<option value="bar">bar</option>'
        "</select>"
    )


def test_optgroup():
    F = make_form(a=SelectField(choices=[SelectChoice("a", "Foo", optgroup="hello")]))
    form = F(a="a")

    assert (
        '<optgroup label="hello">'
        '<option selected value="a">Foo</option>'
        "</optgroup>" in form.a()
    )
    assert list(form.a.iter_choices()) == [
        SelectChoice("a", "Foo", selected=True, optgroup="hello")
    ]


def test_optgroup_shortcut():
    F = make_form(
        a=SelectField(
            choices=[
                SelectChoice("foo", optgroup="hello"),
                SelectChoice("bar", optgroup="hello"),
            ]
        )
    )
    form = F(a="bar")

    assert (
        '<optgroup label="hello">'
        '<option value="foo">foo</option>'
        '<option selected value="bar">bar</option>'
        "</optgroup>" in form.a()
    )
    assert list(form.a.iter_choices()) == [
        SelectChoice("foo", selected=False, optgroup="hello"),
        SelectChoice("bar", selected=True, optgroup="hello"),
    ]


def test_option_render_kw():
    F = make_form(
        a=SelectField(
            choices=[
                Choice("a", "Foo", render_kw={"title": "foobar", "data-foo": "bar"})
            ]
        )
    )
    form = F(a="a")

    assert (
        '<option data-foo="bar" selected title="foobar" value="a">Foo</option>'
        in form.a()
    )
    assert list(form.a.iter_choices()) == [
        SelectChoice(
            "a",
            "Foo",
            selected=True,
            render_kw={"title": "foobar", "data-foo": "bar"},
        )
    ]


def test_optgroup_option_render_kw():
    F = make_form(
        a=SelectField(
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
        SelectChoice(
            "a",
            "Foo",
            selected=True,
            render_kw={"title": "foobar", "data-foo": "bar"},
            optgroup="hello",
        )
    ]


def test_tuple_choices_deprecation():
    F = make_form(a=SelectField(choices=[("a", "Foo")]))
    with pytest.warns(DeprecationWarning):
        form = F(a="a")

    assert '<option selected value="a">Foo</option>' in form.a()
    assert list(form.a.iter_choices()) == [SelectChoice("a", "Foo", selected=True)]


def test_dict_choices_deprecation_with_choice_object():
    F = make_form(a=SelectField(choices={"hello": [Choice("a", "Foo")]}))
    with pytest.warns(DeprecationWarning):
        form = F(a="a")

    assert (
        '<optgroup label="hello">'
        '<option selected value="a">Foo</option>'
        "</optgroup>" in form.a()
    )
    assert list(form.a.iter_choices()) == [
        SelectChoice("a", "Foo", selected=True, optgroup="hello")
    ]


def test_dict_choices_deprecation_with_tuple():
    F = make_form(a=SelectField(choices={"hello": [("a", "Foo")]}))
    with pytest.warns(DeprecationWarning):
        form = F(a="a")

    assert (
        '<optgroup label="hello">'
        '<option selected value="a">Foo</option>'
        "</optgroup>" in form.a()
    )
    assert list(form.a.iter_choices()) == [
        SelectChoice("a", "Foo", selected=True, optgroup="hello")
    ]


class _Plain(Enum):
    RED = 1
    GREEN = 2


class _Pretty(Enum):
    RED = 1
    GREEN = 2

    def __str__(self):
        return self.name.title()


class _Level(IntEnum):
    LOW = 1
    HIGH = 2


def test_choice_from_enum_plain():
    """Plain Enum without ``__str__`` falls back to ``member.name`` for the label."""
    assert Choice.from_enum(_Plain) == [
        Choice(value="RED", label="RED"),
        Choice(value="GREEN", label="GREEN"),
    ]


def test_choice_from_enum_with_dunder_str():
    """An Enum that overrides ``__str__`` uses ``str(member)`` as label."""
    assert Choice.from_enum(_Pretty) == [
        Choice(value="RED", label="Red"),
        Choice(value="GREEN", label="Green"),
    ]


@pytest.mark.skipif(sys.version_info < (3, 11), reason="StrEnum requires 3.11+")
def test_choice_from_enum_strenum():
    """StrEnum uses ``str(member)`` (the value) as label."""

    class _Status(StrEnum):
        ACTIVE = "active"
        INACTIVE = "inactive"

    assert Choice.from_enum(_Status) == [
        Choice(value="ACTIVE", label="active"),
        Choice(value="INACTIVE", label="inactive"),
    ]


def test_choice_from_enum_intenum():
    """IntEnum has no ``__str__`` injected; falls back to ``member.name``."""
    assert Choice.from_enum(_Level) == [
        Choice(value="LOW", label="LOW"),
        Choice(value="HIGH", label="HIGH"),
    ]


def test_choice_from_enum_custom_label():
    """A ``label=`` callable overrides the default."""
    assert Choice.from_enum(_Plain, label=lambda m: m.name.title()) == [
        Choice(value="RED", label="Red"),
        Choice(value="GREEN", label="Green"),
    ]


def test_select_field_enum_coerce_round_trip():
    """``coerce=EnumCls`` round-trips form data back to an Enum member."""
    F = make_form(a=SelectField(choices=Choice.from_enum(_Plain), coerce=_Plain))
    form = F(DummyPostData(a=["RED"]))
    assert form.a.data is _Plain.RED
    assert form.validate()


def test_select_field_enum_coerce_accepts_member():
    """``coerce=EnumCls`` accepts an already-coerced member without re-lookup."""
    F = make_form(a=SelectField(choices=Choice.from_enum(_Plain), coerce=_Plain))
    form = F(a=_Plain.GREEN)
    assert form.a.data is _Plain.GREEN


def test_select_field_enum_coerce_invalid():
    """An unknown name fails validation cleanly (KeyError → ValueError)."""
    F = make_form(a=SelectField(choices=Choice.from_enum(_Plain), coerce=_Plain))
    form = F(DummyPostData(a=["BAD"]))
    assert not form.validate()
    assert form.a.data is None
    assert "Invalid Choice: could not coerce." in form.a.errors


def test_select_choice_tuple_unpacking():
    """SelectChoice is a NamedTuple — tuple unpacking matches the 3.2 yield
    shape (value, label, selected, render_kw, ...)."""
    F = make_form(a=SelectField(choices=[Choice("a", "Foo"), Choice("b", "Bar")]))
    form = F(a="a")
    unpacked = [(v, lab, sel) for v, lab, sel, *_ in form.a.iter_choices()]
    assert unpacked == [("a", "Foo", True), ("b", "Bar", False)]


def test_select_field_enum_renders_selected():
    """Pre-selecting a member highlights the right option."""
    F = make_form(a=SelectField(choices=Choice.from_enum(_Plain), coerce=_Plain))
    form = F(a=_Plain.GREEN)
    assert '<option selected value="GREEN">GREEN</option>' in form.a()
