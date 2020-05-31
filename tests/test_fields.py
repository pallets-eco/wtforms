from collections import namedtuple
from datetime import date
from datetime import datetime
from decimal import Decimal
from decimal import ROUND_DOWN
from decimal import ROUND_UP

import pytest
from markupsafe import Markup
from tests.common import DummyPostData

from wtforms import meta
from wtforms import validators
from wtforms import widgets
from wtforms.fields import BooleanField
from wtforms.fields import DateField
from wtforms.fields import DateTimeField
from wtforms.fields import DateTimeLocalField
from wtforms.fields import DecimalField
from wtforms.fields import DecimalRangeField
from wtforms.fields import EmailField
from wtforms.fields import Field
from wtforms.fields import FieldList
from wtforms.fields import FileField
from wtforms.fields import FloatField
from wtforms.fields import FormField
from wtforms.fields import HiddenField
from wtforms.fields import IntegerField
from wtforms.fields import IntegerRangeField
from wtforms.fields import Label
from wtforms.fields import MonthField
from wtforms.fields import MultipleFileField
from wtforms.fields import PasswordField
from wtforms.fields import RadioField
from wtforms.fields import SearchField
from wtforms.fields import SelectField
from wtforms.fields import SelectFieldBase
from wtforms.fields import SelectMultipleField
from wtforms.fields import StringField
from wtforms.fields import SubmitField
from wtforms.fields import TelField
from wtforms.fields import TextAreaField
from wtforms.fields import TimeField
from wtforms.fields import URLField
from wtforms.form import Form
from wtforms.utils import unset_value
from wtforms.widgets import TextInput


class AttrDict:
    def __init__(self, *args, **kw):
        self.__dict__.update(*args, **kw)


def make_form(name="F", **fields):
    return type(str(name), (Form,), fields)


class TestDefaults:
    def test(self):
        expected = 42

        def default_callable():
            return expected

        test_value = StringField(default=expected).bind(Form(), "a")
        test_value.process(None)
        assert test_value.data == expected

        test_callable = StringField(default=default_callable).bind(Form(), "a")
        test_callable.process(None)
        assert test_callable.data == expected


class TestLabel:
    def test(self):
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

    def test_auto_label(self):
        t1 = StringField().bind(Form(), "foo_bar")
        assert t1.label.text == "Foo Bar"

        t2 = StringField("").bind(Form(), "foo_bar")
        assert t2.label.text == ""

    def test_override_for(self):
        label = Label("test", "Caption")
        assert label(for_="foo") == """<label for="foo">Caption</label>"""
        assert label(**{"for": "bar"}) == """<label for="bar">Caption</label>"""

    def test_escaped_label_text(self):
        label = Label("test", '<script>alert("test");</script>')
        assert label(for_="foo") == (
            '<label for="foo">&lt;script&gt;'
            "alert(&#34;test&#34;);&lt;/script&gt;</label>"
        )

        assert label(**{"for": "bar"}) == (
            '<label for="bar">&lt;script&gt;'
            "alert(&#34;test&#34;);&lt;/script&gt;</label>"
        )


@pytest.fixture()
def flags():
    return StringField(validators=[validators.DataRequired()]).bind(Form(), "a").flags


class TestFlags:
    def test_existing_values(self, flags):
        assert flags.required is True
        assert "required" in flags
        assert flags.optional is False
        assert "optional" not in flags

    def test_assignment(self, flags):
        assert "optional" not in flags
        flags.optional = True
        assert flags.optional is True
        assert "optional" in flags

    def test_unset(self, flags):
        flags.required = False
        assert flags.required is False
        assert "required" not in flags

    def test_repr(self, flags):
        assert repr(flags) == "<wtforms.fields.Flags: {required}>"

    def test_underscore_property(self, flags):
        with pytest.raises(AttributeError):
            flags._foo
        flags._foo = 42
        assert flags._foo == 42


class TestUnsetValue:
    def test(self):
        assert str(unset_value) == "<unset value>"
        assert repr(unset_value) == "<unset value>"
        assert bool(unset_value) is False
        assert not unset_value
        assert unset_value.__nonzero__() is False
        assert unset_value.__bool__() is False


class TestFilters:
    class F(Form):
        a = StringField(default=" hello", filters=[lambda x: x.strip()])
        b = StringField(default="42", filters=[int, lambda x: -x])

    def test_working(self):
        form = self.F()
        assert form.a.data == "hello"
        assert form.b.data == -42
        assert form.validate()

    def test_failure(self):
        form = self.F(DummyPostData(a=["  foo bar  "], b=["hi"]))
        assert form.a.data == "foo bar"
        assert form.b.data == "hi"
        assert len(form.b.process_errors) == 1
        assert not form.validate()

    def test_extra(self):
        class F(Form):
            a = StringField(default=" hello ")
            b = StringField(default="42")

        def filter_a(value):
            return value.strip()

        def filter_b(value):
            return -int(value)

        form = F(extra_filters={"a": [filter_a], "b": [filter_b]})
        assert "hello" == form.a.data
        assert -42 == form.b.data
        assert form.validate()

    def test_inline(self):
        class F(Form):
            a = StringField(default=" hello ")
            b = StringField(default="42")

            def filter_a(self, value):
                return value.strip()

            def filter_b(self, value):
                return -int(value)

        form = F()
        assert "hello" == form.a.data
        assert -42 == form.b.data
        assert form.validate()


class TestField:
    class F(Form):
        a = StringField(default="hello", render_kw={"readonly": True, "foo": "bar"})
        b = StringField(validators=[validators.InputRequired()])

    def test_unbound_field(self):
        unbound = self.F.a
        assert unbound.creation_counter != 0
        assert unbound.field_class is StringField
        assert unbound.args == ()
        assert unbound.kwargs == {
            "default": "hello",
            "render_kw": {"readonly": True, "foo": "bar"},
        }
        assert repr(unbound).startswith("<UnboundField(StringField")

    def test_htmlstring(self):
        assert isinstance(self.F().a.__html__(), Markup)

    def test_str_coerce(self):
        field = self.F().a
        assert isinstance(str(field), str)
        assert str(field) == str(field)

    def test_unicode_coerce(self):
        field = self.F().a
        assert str(field) == field()

    def test_process_formdata(self):
        field = self.F().a
        Field.process_formdata(field, [42])
        assert field.data == 42

    def test_meta_attribute(self):
        # Can we pass in meta via _form?
        form = self.F()
        assert form.a.meta is form.meta

        # Can we pass in meta via _meta?
        form_meta = meta.DefaultMeta()
        field = StringField(name="Foo", _form=None, _meta=form_meta)
        assert field.meta is form_meta

        # Do we fail if both _meta and _form are None?
        with pytest.raises(TypeError):
            StringField(name="foo", _form=None)

    def test_render_kw(self):
        form = self.F()
        assert (
            form.a()
            == '<input foo="bar" id="a" name="a" readonly type="text" value="hello">'
        )
        assert (
            form.a(foo="baz")
            == '<input foo="baz" id="a" name="a" readonly type="text" value="hello">'
        )
        assert form.a(foo="baz", readonly=False, other="hello") == (
            '<input foo="baz" id="a" name="a" other="hello" '
            'type="text" value="hello">'
        )

    def test_select_field_copies_choices(self):
        class F(Form):
            items = SelectField(choices=[])

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def add_choice(self, choice):
                self.items.choices.append((choice, choice))

        f1 = F()
        f2 = F()

        f1.add_choice("a")
        f2.add_choice("b")

        assert f1.items.choices == [("a", "a")]
        assert f2.items.choices == [("b", "b")]
        assert f1.items.choices is not f2.items.choices

    def test_required_flag(self):
        form = self.F()
        assert form.b() == '<input id="b" name="b" required type="text" value="">'

    def test_check_validators(self):
        v1 = "Not callable"
        v2 = validators.DataRequired

        with pytest.raises(
            TypeError,
            match=r"{} is not a valid validator because "
            "it is not callable".format(v1),
        ):
            Field(validators=[v1])

        with pytest.raises(
            TypeError,
            match=r"{} is not a valid validator because "
            "it is a class, it should be an "
            "instance".format(v2),
        ):
            Field(validators=[v2])

    def test_custom_name(self):
        class F(Form):
            foo = StringField(name="bar", default="default")
            x = StringField()

        class ObjFoo:
            foo = "obj"

        class ObjBar:
            bar = "obj"

        f = F(DummyPostData(foo="data"))
        assert f.foo.data == "default"
        assert 'value="default"' in f.foo()

        f = F(DummyPostData(bar="data"))
        assert f.foo.data == "data"
        assert 'value="data"' in f.foo()

        f = F(foo="kwarg")
        assert f.foo.data == "kwarg"
        assert 'value="kwarg"' in f.foo()

        f = F(bar="kwarg")
        assert f.foo.data == "default"
        assert 'value="default"' in f.foo()

        f = F(obj=ObjFoo())
        assert f.foo.data == "obj"
        assert 'value="obj"' in f.foo()

        f = F(obj=ObjBar())
        assert f.foo.data == "default"
        assert 'value="default"' in f.foo()


class PrePostTestField(StringField):
    def pre_validate(self, form):
        if self.data == "stoponly":
            raise validators.StopValidation()
        elif self.data.startswith("stop"):
            raise validators.StopValidation("stop with message")

    def post_validate(self, form, stopped):
        if self.data == "p":
            raise validators.ValidationError("Post")
        elif stopped and self.data == "stop-post":
            raise validators.ValidationError("Post-stopped")


class TestPrePostValidation:
    class F(Form):
        a = PrePostTestField(validators=[validators.Length(max=1, message="too long")])

    def _init_field(self, value):
        form = self.F(a=value)
        form.validate()
        return form.a

    def test_pre_stop(self):
        a = self._init_field("long")
        assert a.errors == ["too long"]

        stoponly = self._init_field("stoponly")
        assert stoponly.errors == []

        stopmessage = self._init_field("stopmessage")
        assert stopmessage.errors == ["stop with message"]

    def test_post(self):
        a = self._init_field("p")
        assert a.errors == ["Post"]
        stopped = self._init_field("stop-post")
        assert stopped.errors == ["stop with message", "Post-stopped"]


class TestSelectField:
    class F(Form):
        a = SelectField(choices=[("a", "hello"), ("btest", "bye")], default="a")
        b = SelectField(
            choices=[(1, "Item 1"), (2, "Item 2")],
            coerce=int,
            option_widget=widgets.TextInput(),
        )

    def test_defaults(self):
        form = self.F()
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

    def test_with_data(self):
        form = self.F(DummyPostData(a=["btest"]))
        assert form.a.data == "btest"
        assert form.a() == (
            '<select id="a" name="a"><option value="a">hello</option>'
            '<option selected value="btest">bye</option></select>'
        )

    def test_value_coercion(self):
        form = self.F(DummyPostData(b=["2"]))
        assert form.b.data == 2
        assert form.b.validate(form)
        form = self.F(DummyPostData(b=["b"]))
        assert form.b.data is None
        assert not form.b.validate(form)

    def test_iterable_options(self):
        form = self.F()
        first_option = list(form.a)[0]
        assert isinstance(first_option, form.a._Option)
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

    def test_default_coerce(self):
        F = make_form(a=SelectField(choices=[("a", "Foo")]))
        form = F(DummyPostData(a=[]))
        assert not form.validate()
        assert form.a.data is None
        assert len(form.a.errors) == 1
        assert form.a.errors[0] == "Not a valid choice"

    def test_validate_choices(self):
        F = make_form(a=SelectField(choices=[("a", "Foo")]))
        form = F(DummyPostData(a=["b"]))
        assert not form.validate()
        assert form.a.data == "b"
        assert len(form.a.errors) == 1
        assert form.a.errors[0] == "Not a valid choice"

    def test_validate_choices_when_empty(self):
        F = make_form(a=SelectField(choices=[]))
        form = F(DummyPostData(a=["b"]))
        assert not form.validate()
        assert form.a.data == "b"
        assert len(form.a.errors) == 1
        assert form.a.errors[0] == "Not a valid choice"

    def test_validate_choices_when_none(self):
        F = make_form(a=SelectField())
        form = F(DummyPostData(a="b"))
        with pytest.raises(TypeError, match="Choices cannot be None"):
            form.validate()

    def test_dont_validate_choices(self):
        F = make_form(a=SelectField(choices=[("a", "Foo")], validate_choice=False))
        form = F(DummyPostData(a=["b"]))
        assert form.validate()
        assert form.a.data == "b"
        assert len(form.a.errors) == 0

    def test_choice_shortcut(self):
        F = make_form(a=SelectField(choices=["foo", "bar"], validate_choice=False))
        form = F(a="bar")
        assert '<option value="foo">foo</option>' in form.a()

    @pytest.mark.parametrize("choices", [[], None])
    def test_empty_choice(self, choices):
        F = make_form(a=SelectField(choices=choices, validate_choice=False))
        form = F(a="bar")
        assert form.a() == '<select id="a" name="a"></select>'

    def test_callable_choices(self):
        def choices():
            return ["foo", "bar"]

        F = make_form(a=SelectField(choices=choices))
        form = F(a="bar")

        assert list(str(x) for x in form.a) == [
            '<option value="foo">foo</option>',
            '<option selected value="bar">bar</option>',
        ]


class TestSelectMultipleField:
    class F(Form):
        a = SelectMultipleField(
            choices=[("a", "hello"), ("b", "bye"), ("c", "something")], default=("a",)
        )
        b = SelectMultipleField(
            coerce=int, choices=[(1, "A"), (2, "B"), (3, "C")], default=("1", "3")
        )

    def test_defaults(self):
        form = self.F()
        assert form.a.data == ["a"]
        assert form.b.data == [1, 3]
        # Test for possible regression with null data
        form.a.data = None
        assert form.validate()
        assert list(form.a.iter_choices()) == [(v, l, False) for v, l in form.a.choices]

    def test_with_data(self):
        form = self.F(DummyPostData(a=["a", "c"]))
        assert form.a.data == ["a", "c"]
        assert list(form.a.iter_choices()) == [
            ("a", "hello", True),
            ("b", "bye", False),
            ("c", "something", True),
        ]
        assert form.b.data == []
        form = self.F(DummyPostData(b=["1", "2"]))
        assert form.b.data == [1, 2]
        assert form.validate()
        form = self.F(DummyPostData(b=["1", "2", "4"]))
        assert form.b.data == [1, 2, 4]
        assert not form.validate()

    def test_coerce_fail(self):
        form = self.F(b=["a"])
        assert form.validate()
        assert form.b.data is None
        form = self.F(DummyPostData(b=["fake"]))
        assert not form.validate()
        assert form.b.data == [1, 3]

    def test_callable_choices(self):
        def choices():
            return ["foo", "bar"]

        F = make_form(a=SelectField(choices=choices))
        form = F(a="bar")

        assert list(str(x) for x in form.a) == [
            '<option value="foo">foo</option>',
            '<option selected value="bar">bar</option>',
        ]

    def test_choice_shortcut(self):
        F = make_form(
            a=SelectMultipleField(choices=["foo", "bar"], validate_choice=False)
        )
        form = F(a="bar")
        assert '<option value="foo">foo</option>' in form.a()

    @pytest.mark.parametrize("choices", [[], None])
    def test_empty_choice(self, choices):
        F = make_form(a=SelectMultipleField(choices=choices, validate_choice=False))
        form = F(a="bar")
        assert form.a() == '<select id="a" multiple name="a"></select>'


class TestRadioField:
    class F(Form):
        a = RadioField(choices=[("a", "hello"), ("b", "bye")], default="a")
        b = RadioField(choices=[(1, "Item 1"), (2, "Item 2")], coerce=int)

    def test(self):
        form = self.F()
        assert form.a.data == "a"
        assert form.b.data is None
        assert form.validate() is False
        assert form.a() == (
            '<ul id="a">'
            '<li><input checked id="a-0" name="a" type="radio" value="a"> '
            '<label for="a-0">hello</label></li>'
            '<li><input id="a-1" name="a" type="radio" value="b"> '
            '<label for="a-1">bye</label></li>'
            "</ul>"
        )
        assert form.b() == (
            '<ul id="b">'
            '<li><input id="b-0" name="b" type="radio" value="1"> '
            '<label for="b-0">Item 1</label></li>'
            '<li><input id="b-1" name="b" type="radio" value="2"> '
            '<label for="b-1">Item 2</label></li>'
            "</ul>"
        )
        assert [str(x) for x in form.a] == [
            '<input checked id="a-0" name="a" type="radio" value="a">',
            '<input id="a-1" name="a" type="radio" value="b">',
        ]

    def test_text_coercion(self):
        # Regression test for text coercion scenarios where the value is a boolean.
        F = make_form(
            a=RadioField(
                choices=[(True, "yes"), (False, "no")],
                coerce=lambda x: False if x == "False" else bool(x),
            )
        )
        form = F()
        assert form.a() == (
            '<ul id="a">'
            '<li><input id="a-0" name="a" type="radio" value="True"> '
            '<label for="a-0">yes</label></li>'
            '<li><input id="a-1" name="a" type="radio" value="False"> '
            '<label for="a-1">no</label></li>'
            "</ul>"
        )

    def test_callable_choices(self):
        def choices():
            return [("a", "hello"), ("b", "bye")]

        class F(Form):
            a = RadioField(choices=choices, default="a")

        form = self.F()
        assert form.a.data == "a"
        assert form.a() == (
            '<ul id="a">'
            '<li><input checked id="a-0" name="a" type="radio" value="a"> '
            '<label for="a-0">hello</label></li>'
            '<li><input id="a-1" name="a" type="radio" value="b"> '
            '<label for="a-1">bye</label></li>'
            "</ul>"
        )


class TestStringField:
    class F(Form):
        a = StringField()

    def test(self):
        form = self.F()
        assert form.a.data is None
        assert form.a() == """<input id="a" name="a" type="text" value="">"""
        form = self.F(DummyPostData(a=["hello"]))
        assert form.a.data == "hello"
        assert form.a() == """<input id="a" name="a" type="text" value="hello">"""
        form = self.F(DummyPostData(b=["hello"]))
        assert form.a.data is None


class TestHiddenField:
    class F(Form):
        a = HiddenField(default="LE DEFAULT")

    def test(self):
        form = self.F()
        assert (
            form.a() == """<input id="a" name="a" type="hidden" value="LE DEFAULT">"""
        )
        assert form.a.flags.hidden


class TestTextAreaField:
    class F(Form):
        a = TextAreaField(default="LE DEFAULT")

    def test(self):
        form = self.F()
        assert form.a() == """<textarea id="a" name="a">\r\nLE DEFAULT</textarea>"""


class TestPasswordField:
    class F(Form):
        a = PasswordField(
            widget=widgets.PasswordInput(hide_value=False), default="LE DEFAULT"
        )
        b = PasswordField(default="Hai")

    def test(self):
        form = self.F()
        assert (
            form.a() == """<input id="a" name="a" type="password" value="LE DEFAULT">"""
        )
        assert form.b() == """<input id="b" name="b" type="password" value="">"""


class TestFileField:
    def test_file_field(self):
        class F(Form):
            file = FileField()

        assert F(DummyPostData(file=["test.txt"])).file.data == "test.txt"
        assert F(DummyPostData()).file.data is None
        assert (
            F(DummyPostData(file=["test.txt", "multiple.txt"])).file.data == "test.txt"
        )

    def test_multiple_file_field(self):
        class F(Form):
            files = MultipleFileField()

        assert F(DummyPostData(files=["test.txt"])).files.data == ["test.txt"]
        assert F(DummyPostData()).files.data == []
        assert F(DummyPostData(files=["test.txt", "multiple.txt"])).files.data == [
            "test.txt",
            "multiple.txt",
        ]

    def test_file_field_without_file_input(self):
        class F(Form):
            file = FileField(widget=TextInput())

        f = F(DummyPostData(file=["test.txt"]))
        assert f.file.data == "test.txt"
        assert f.file() == '<input id="file" name="file" type="text">'


class TestIntegerField:
    class F(Form):
        a = IntegerField()
        b = IntegerField(default=48)

    def test(self):
        form = self.F(DummyPostData(a=["v"], b=["-15"]))
        assert form.a.data is None
        assert form.a.raw_data == ["v"]
        assert form.a() == """<input id="a" name="a" type="number" value="v">"""
        assert form.b.data == -15
        assert form.b() == """<input id="b" name="b" type="number" value="-15">"""
        assert not form.a.validate(form)
        assert form.b.validate(form)
        form = self.F(DummyPostData(a=[], b=[""]))
        assert form.a.data is None
        assert form.a.raw_data == []
        assert form.b.data is None
        assert form.b.raw_data == [""]
        assert not form.validate()
        assert len(form.b.process_errors) == 1
        assert len(form.b.errors) == 1
        form = self.F(b=9)
        assert form.b.data == 9
        assert form.a._value() == ""
        assert form.b._value() == "9"
        form = self.F(DummyPostData(), data=dict(b="v"))
        assert form.b.data is None
        assert form.a._value() == ""
        assert form.b._value() == ""
        assert not form.validate()
        assert len(form.b.process_errors) == 1
        assert len(form.b.errors) == 1


class TestDecimalField:
    def test(self):
        F = make_form(a=DecimalField())
        form = F(DummyPostData(a="2.1"))
        assert form.a.data == Decimal("2.1")
        assert form.a._value() == "2.1"
        form.a.raw_data = None
        assert form.a._value() == "2.10"
        assert form.validate()
        form = F(DummyPostData(a="2,1"), a=Decimal(5))
        assert form.a.data is None
        assert form.a.raw_data == ["2,1"]
        assert not form.validate()
        form = F(DummyPostData(a="asdf"), a=Decimal(".21"))
        assert form.a._value() == "asdf"
        assert not form.validate()

    def test_quantize(self):
        F = make_form(
            a=DecimalField(places=3, rounding=ROUND_UP), b=DecimalField(places=None)
        )
        form = F(a=Decimal("3.1415926535"))
        assert form.a._value() == "3.142"
        form.a.rounding = ROUND_DOWN
        assert form.a._value() == "3.141"
        assert form.b._value() == ""
        form = F(a=3.14159265, b=72)
        assert form.a._value() == "3.142"
        assert isinstance(form.a.data, float)
        assert form.b._value() == "72"


class TestFloatField:
    class F(Form):
        a = FloatField()
        b = FloatField(default=48.0)

    def test(self):
        form = self.F(DummyPostData(a=["v"], b=["-15.0"]))
        assert form.a.data is None
        assert form.a.raw_data == ["v"]
        assert form.a() == """<input id="a" name="a" type="text" value="v">"""
        assert form.b.data == -15.0
        assert form.b() == """<input id="b" name="b" type="text" value="-15.0">"""
        assert not form.a.validate(form)
        assert form.b.validate(form)
        form = self.F(DummyPostData(a=[], b=[""]))
        assert form.a.data is None
        assert form.a._value() == ""
        assert form.b.data is None
        assert form.b.raw_data == [""]
        assert not form.validate()
        assert len(form.b.process_errors) == 1
        assert len(form.b.errors) == 1
        form = self.F(b=9.0)
        assert form.b.data == 9.0
        assert form.b._value() == "9.0"


class TestBooleanField:
    class BoringForm(Form):
        bool1 = BooleanField()
        bool2 = BooleanField(default=True, false_values=())

    obj = AttrDict(bool1=None, bool2=True)

    def test_defaults(self):
        # Test with no post data to make sure defaults work
        form = self.BoringForm()
        assert form.bool1.raw_data is None
        assert form.bool1.data is False
        assert form.bool2.data is True

    def test_rendering(self):
        form = self.BoringForm(DummyPostData(bool2="x"))
        assert (
            form.bool1() == '<input id="bool1" name="bool1" type="checkbox" value="y">'
        )
        assert (
            form.bool2()
            == '<input checked id="bool2" name="bool2" type="checkbox" value="x">'
        )
        assert form.bool2.raw_data == ["x"]

    def test_with_postdata(self):
        form = self.BoringForm(DummyPostData(bool1=["a"]))
        assert form.bool1.raw_data == ["a"]
        assert form.bool1.data is True
        form = self.BoringForm(DummyPostData(bool1=["false"], bool2=["false"]))
        assert form.bool1.data is False
        assert form.bool2.data is True

    def test_with_model_data(self):
        form = self.BoringForm(obj=self.obj)
        assert form.bool1.data is False
        assert form.bool1.raw_data is None
        assert form.bool2.data is True

    def test_with_postdata_and_model(self):
        form = self.BoringForm(DummyPostData(bool1=["y"]), obj=self.obj)
        assert form.bool1.data is True
        assert form.bool2.data is False


class TestDateField:
    class F(Form):
        a = DateField()
        b = DateField(format="%m/%d %Y")

    def test_basic(self):
        d = date(2008, 5, 7)
        form = self.F(DummyPostData(a=["2008-05-07"], b=["05/07", "2008"]))
        assert form.a.data == d
        assert form.a._value() == "2008-05-07"
        assert form.b.data == d
        assert form.b._value() == "05/07 2008"

    def test_failure(self):
        form = self.F(DummyPostData(a=["2008-bb-cc"], b=["hi"]))
        assert not form.validate()
        assert len(form.a.process_errors) == 1
        assert len(form.a.errors) == 1
        assert len(form.b.errors) == 1
        assert form.a.process_errors[0] == "Not a valid date value"


class TestMonthField:
    class F(Form):
        a = MonthField()
        b = MonthField(format="%m/%Y")

    def test_basic(self):
        d = date(2008, 5, 1)
        form = self.F(DummyPostData(a=["2008-05"], b=["05/2008"]))

        assert d == form.a.data
        assert "2008-05" == form.a._value()

        assert d == form.b.data

    def test_failure(self):
        form = self.F(DummyPostData(a=["2008-bb"]))

        assert not form.validate()
        assert 1 == len(form.a.process_errors)
        assert 1 == len(form.a.errors)
        assert "Not a valid date value" == form.a.process_errors[0]


class TestTimeField:
    class F(Form):
        a = TimeField()
        b = TimeField(format="%H:%M")

    def test_basic(self):
        d = datetime(2008, 5, 5, 4, 30, 0, 0).time()
        # Basic test with both inputs
        form = self.F(DummyPostData(a=["4:30"], b=["04:30"]))
        assert form.a.data == d
        assert form.a() == """<input id="a" name="a" type="time" value="4:30">"""
        assert form.b.data == d
        assert form.b() == """<input id="b" name="b" type="time" value="04:30">"""
        assert form.validate()

        # Test with a missing input
        form = self.F(DummyPostData(a=["04"]))
        assert not form.validate()
        assert form.a.errors[0] == "Not a valid time value"


class TestDateTimeField:
    class F(Form):
        a = DateTimeField()
        b = DateTimeField(format="%Y-%m-%d %H:%M")

    def test_basic(self):
        d = datetime(2008, 5, 5, 4, 30, 0, 0)
        # Basic test with both inputs
        form = self.F(
            DummyPostData(a=["2008-05-05", "04:30:00"], b=["2008-05-05 04:30"])
        )
        assert form.a.data == d
        assert (
            form.a()
            == """<input id="a" name="a" type="datetime" value="2008-05-05 04:30:00">"""
        )
        assert form.b.data == d
        assert (
            form.b()
            == """<input id="b" name="b" type="datetime" value="2008-05-05 04:30">"""
        )
        assert form.validate()

        # Test with a missing input
        form = self.F(DummyPostData(a=["2008-05-05"]))
        assert not form.validate()
        assert form.a.errors[0] == "Not a valid datetime value"

        form = self.F(a=d, b=d)
        assert form.validate()
        assert form.a._value() == "2008-05-05 04:30:00"

    def test_microseconds(self):
        d = datetime(2011, 5, 7, 3, 23, 14, 424200)
        F = make_form(a=DateTimeField(format="%Y-%m-%d %H:%M:%S.%f"))
        form = F(DummyPostData(a=["2011-05-07 03:23:14.4242"]))
        assert d == form.a.data


class TestSubmitField:
    class F(Form):
        a = SubmitField("Label")

    def test(self):
        assert self.F().a() == """<input id="a" name="a" type="submit" value="Label">"""


@pytest.fixture
def F1():
    F = make_form(
        a=StringField(validators=[validators.DataRequired()]), b=StringField()
    )
    return make_form("F1", a=FormField(F))


@pytest.fixture
def F2():
    F = make_form(
        a=StringField(validators=[validators.DataRequired()]), b=StringField()
    )
    return make_form("F2", a=FormField(F, separator="::"))


class TestFormField:
    def test_formdata(self, F1):
        form = F1(DummyPostData({"a-a": ["moo"]}))
        assert form.a.form.a.name == "a-a"
        assert form.a["a"].data == "moo"
        assert form.a["b"].data is None
        assert form.validate()

    def test_iteration(self, F1):
        assert [x.name for x in F1().a] == ["a-a", "a-b"]

    def test_with_obj(self, F1):
        obj = AttrDict(a=AttrDict(a="mmm"))
        form = F1(obj=obj)
        assert form.a.form.a.data == "mmm"
        assert form.a.form.b.data is None
        obj_inner = AttrDict(a=None, b="rawr")
        obj2 = AttrDict(a=obj_inner)
        form.populate_obj(obj2)
        assert obj2.a is obj_inner
        assert obj_inner.a == "mmm"
        assert obj_inner.b is None

    def test_widget(self, F1):
        assert F1().a() == (
            '<table id="a">'
            '<tr><th><label for="a-a">A</label></th>'
            '<td><input id="a-a" name="a-a" required type="text" value=""></td></tr>'
            '<tr><th><label for="a-b">B</label></th>'
            '<td><input id="a-b" name="a-b" type="text" value=""></td></tr>'
            "</table>"
        )

    def test_separator(self, F2):
        form = F2(DummyPostData({"a-a": "fake", "a::a": "real"}))
        assert form.a.a.name == "a::a"
        assert form.a.a.data == "real"
        assert form.validate()

    def test_no_validators_or_filters(self, F1):
        class A(Form):
            a = FormField(F1, validators=[validators.DataRequired()])

        with pytest.raises(TypeError):
            A()

        class B(Form):
            a = FormField(F1, filters=[lambda x: x])

        with pytest.raises(TypeError):
            B()

        class C(Form):
            a = FormField(F1)

            def validate_a(self, field):
                pass

        form = C()
        with pytest.raises(TypeError):
            form.validate()

    def test_populate_missing_obj(self, F1):
        obj = AttrDict(a=None)
        obj2 = AttrDict(a=AttrDict(a="mmm"))
        form = F1()
        with pytest.raises(TypeError):
            form.populate_obj(obj)
        form.populate_obj(obj2)


class TestFieldList:
    t = StringField(validators=[validators.DataRequired()])

    def test_form(self):
        F = make_form(a=FieldList(self.t))
        data = ["foo", "hi", "rawr"]
        a = F(a=data).a
        assert a.entries[1].data == "hi"
        assert a.entries[1].name == "a-1"
        assert a.data == data
        assert len(a.entries) == 3

        pdata = DummyPostData(
            {"a-0": ["bleh"], "a-3": ["yarg"], "a-4": [""], "a-7": ["mmm"]}
        )
        form = F(pdata)
        assert len(form.a.entries) == 4
        assert form.a.data == ["bleh", "yarg", "", "mmm"]
        assert not form.validate()

        form = F(pdata, a=data)
        assert form.a.data == ["bleh", "yarg", "", "mmm"]
        assert not form.validate()

        # Test for formdata precedence
        pdata = DummyPostData({"a-0": ["a"], "a-1": ["b"]})
        form = F(pdata, a=data)
        assert len(form.a.entries) == 2
        assert form.a.data == ["a", "b"]
        assert list(iter(form.a)) == list(form.a.entries)

    def test_enclosed_subform(self):
        def make_inner():
            return AttrDict(a=None)

        F = make_form(
            a=FieldList(FormField(make_form("FChild", a=self.t), default=make_inner))
        )
        data = [{"a": "hello"}]
        form = F(a=data)
        assert form.a.data == data
        assert form.validate()
        form.a.append_entry()
        assert form.a.data == data + [{"a": None}]
        assert not form.validate()

        pdata = DummyPostData({"a-0": ["fake"], "a-0-a": ["foo"], "a-1-a": ["bar"]})
        form = F(pdata, a=data)
        assert form.a.data == [{"a": "foo"}, {"a": "bar"}]

        inner_obj = make_inner()
        inner_list = [inner_obj]
        obj = AttrDict(a=inner_list)
        form.populate_obj(obj)
        assert obj.a is not inner_list
        assert len(obj.a) == 2
        assert obj.a[0] is inner_obj
        assert obj.a[0].a == "foo"
        assert obj.a[1].a == "bar"

        # Test failure on populate
        obj2 = AttrDict(a=42)
        with pytest.raises(TypeError):
            form.populate_obj(obj2)

    def test_enclosed_subform_custom_name(self):
        class Inside(Form):
            foo = StringField(name="bar", default="default")

        class Outside(Form):
            subforms = FieldList(FormField(Inside), min_entries=1)

        o = Outside()
        assert o.subforms[0].foo.data == "default"

        pdata = DummyPostData({"subforms-0-bar": "form"})
        o = Outside(pdata)
        assert o.subforms[0].foo.data == "form"

        pdata = DummyPostData({"subforms-0-foo": "form"})
        o = Outside(pdata)
        assert o.subforms[0].foo.data == "default"

    def test_entry_management(self):
        F = make_form(a=FieldList(self.t))
        a = F(a=["hello", "bye"]).a
        assert a.pop_entry().name == "a-1"
        assert a.data == ["hello"]
        a.append_entry("orange")
        assert a.data == ["hello", "orange"]
        assert a[-1].name == "a-1"
        assert a.pop_entry().data == "orange"
        assert a.pop_entry().name == "a-0"
        with pytest.raises(IndexError):
            a.pop_entry()

    def test_min_max_entries(self):
        F = make_form(a=FieldList(self.t, min_entries=1, max_entries=3))
        a = F().a
        assert len(a) == 1
        assert a[0].data is None
        big_input = ["foo", "flaf", "bar", "baz"]
        with pytest.raises(AssertionError):
            F(a=big_input)
        pdata = DummyPostData(("a-%d" % i, v) for i, v in enumerate(big_input))
        a = F(pdata).a
        assert a.data == ["foo", "flaf", "bar"]
        with pytest.raises(AssertionError):
            a.append_entry()

    def test_validators(self):
        def validator(form, field):
            if field.data and field.data[0] == "fail":
                raise validators.ValidationError("fail")
            elif len(field.data) > 2:
                raise validators.ValidationError("too many")

        F = make_form(a=FieldList(self.t, validators=[validator]))

        # Case 1: length checking validators work as expected.
        fdata = DummyPostData({"a-0": ["hello"], "a-1": ["bye"], "a-2": ["test3"]})
        form = F(fdata)
        assert not form.validate()
        assert form.a.errors == ["too many"]

        # Case 2: checking a value within.
        fdata["a-0"] = ["fail"]
        form = F(fdata)
        assert not form.validate()
        assert form.a.errors == ["fail"]

        # Case 3: normal field validator still works
        form = F(DummyPostData({"a-0": [""]}))
        assert not form.validate()
        assert form.a.errors == [["This field is required."]]

    def test_no_filters(self):
        with pytest.raises(TypeError):
            FieldList(self.t, filters=[lambda x: x], _form=Form(), name="foo")

    def test_process_prefilled(self):
        data = ["foo", "hi", "rawr"]
        Obj = namedtuple("Obj", "a")
        obj = Obj(data)
        F = make_form(a=FieldList(self.t))
        # fill form
        form = F(obj=obj)
        assert len(form.a.entries) == 3
        # pretend to submit form unchanged
        pdata = DummyPostData({"a-0": ["foo"], "a-1": ["hi"], "a-2": ["rawr"]})
        form.process(formdata=pdata)
        # check if data still the same
        assert len(form.a.entries) == 3
        assert form.a.data == data

    def test_errors(self):
        F = make_form(a=FieldList(self.t))
        form = F(DummyPostData({"a-0": ["a"], "a-1": ""}))
        assert not form.validate()
        assert form.a.errors == [[], ["This field is required."]]


class MyCustomField(StringField):
    def process_data(self, data):
        if data == "fail":
            raise ValueError("Contrived Failure")

        return super().process_data(data)


class TestCustomFieldQuirks:
    class F(Form):
        a = MyCustomField()
        b = SelectFieldBase()

    def test_processing_failure(self):
        form = self.F(a="42")
        assert form.validate()
        form = self.F(a="fail")
        assert not form.validate()

    def test_default_impls(self):
        f = self.F()
        with pytest.raises(NotImplementedError):
            f.b.iter_choices()


class TestHTML5Fields:
    class F(Form):
        search = SearchField()
        telephone = TelField()
        url = URLField()
        email = EmailField()
        datetime = DateTimeField()
        date = DateField()
        dt_local = DateTimeLocalField()
        integer = IntegerField()
        decimal = DecimalField()
        int_range = IntegerRangeField()
        decimal_range = DecimalRangeField()

    def _build_value(self, key, form_input, expected_html, data=unset_value):
        if data is unset_value:
            data = form_input
        if expected_html.startswith("type="):
            expected_html = '<input id="{}" name="{}" {} value="{}">'.format(
                key, key, expected_html, form_input
            )
        return {
            "key": key,
            "form_input": form_input,
            "expected_html": expected_html,
            "data": data,
        }

    def test_simple(self):
        b = self._build_value
        VALUES = (
            b("search", "search", 'type="search"'),
            b("telephone", "123456789", 'type="tel"'),
            b("url", "http://wtforms.simplecodes.com/", 'type="url"'),
            b("email", "foo@bar.com", 'type="email"'),
            b(
                "datetime",
                "2013-09-05 00:23:42",
                'type="datetime"',
                datetime(2013, 9, 5, 0, 23, 42),
            ),
            b("date", "2013-09-05", 'type="date"', date(2013, 9, 5)),
            b(
                "dt_local",
                "2013-09-05 00:23:42",
                'type="datetime-local"',
                datetime(2013, 9, 5, 0, 23, 42),
            ),
            b(
                "integer",
                "42",
                '<input id="integer" name="integer" type="number" value="42">',
                42,
            ),
            b(
                "decimal",
                "43.5",
                '<input id="decimal" name="decimal" '
                'step="any" type="number" value="43.5">',
                Decimal("43.5"),
            ),
            b(
                "int_range",
                "4",
                '<input id="int_range" name="int_range" type="range" value="4">',
                4,
            ),
            b(
                "decimal_range",
                "58",
                '<input id="decimal_range" name="decimal_range" '
                'step="any" type="range" value="58">',
                58,
            ),
        )
        formdata = DummyPostData()
        kw = {}
        for item in VALUES:
            formdata[item["key"]] = item["form_input"]
            kw[item["key"]] = item["data"]

        form = self.F(formdata)
        for item in VALUES:
            field = form[item["key"]]
            render_value = field()
            if render_value != item["expected_html"]:
                tmpl = (
                    "Field {key} render mismatch: {render_value!r} != {expected_html!r}"
                )
                raise AssertionError(tmpl.format(render_value=render_value, **item))
            if field.data != item["data"]:
                tmpl = "Field {key} data mismatch: {field.data!r} != {data!r}"
                raise AssertionError(tmpl.format(field=field, **item))
