import pytest

from tests.common import DummyPostData
from wtforms import validators
from wtforms.fields import FieldList
from wtforms.fields import FormField
from wtforms.fields import SelectField
from wtforms.fields import StringField
from wtforms.form import Form


class AttrDict:
    def __init__(self, *args, **kw):
        self.__dict__.update(*args, **kw)


class ClassWithProperty(AttrDict):
    @property
    def a(self):
        return AttrDict(self.a_) if getattr(self, "a_", None) else AttrDict()

    @a.setter
    def a(self, value):
        self.a_ = vars(value)


def make_form(name="F", **fields):
    return type(str(name), (Form,), fields)


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


def test_formdata(F1):
    form = F1(DummyPostData({"a-a": ["moo"]}))
    assert form.a.form.a.name == "a-a"
    assert form.a["a"].data == "moo"
    assert form.a["b"].data is None
    assert form.validate()


def test_iteration(F1):
    assert [x.name for x in F1().a] == ["a-a", "a-b"]


def test_with_obj(F1):
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


def test_widget(F1):
    assert F1().a() == (
        '<table id="a">'
        '<tr><th><label for="a-a">A</label></th>'
        '<td><input id="a-a" name="a-a" required type="text" value=""></td></tr>'
        '<tr><th><label for="a-b">B</label></th>'
        '<td><input id="a-b" name="a-b" type="text" value=""></td></tr>'
        "</table>"
    )


def test_separator(F2):
    form = F2(DummyPostData({"a-a": "fake", "a::a": "real"}))
    assert form.a.a.name == "a::a"
    assert form.a.a.data == "real"
    assert form.validate()


def test_no_validators_or_filters(F1):
    class A(Form):
        a = FormField(F1, validators=[validators.DataRequired()])

    with pytest.raises(TypeError):
        A()

    class B(Form):
        a = FormField(F1, filters=[str])

    with pytest.raises(TypeError):
        B()

    class C(Form):
        a = FormField(F1)

        def validate_a(self, field):
            pass

    form = C()
    with pytest.raises(TypeError):
        form.validate()


def test_post_process_propagates_through_form_field():
    """``post_process`` of a nested form runs before its enclosing ``FormField``."""
    captured = []

    class Inner(Form):
        x = StringField()

        def post_process(self):
            super().post_process()
            captured.append(("inner", self.x.data))

    class Outer(Form):
        block = FormField(Inner)

        def post_process(self):
            super().post_process()
            captured.append(("outer", self.block.form.x.data))

    Outer(DummyPostData({"block-x": "v"}))
    assert captured == [("inner", "v"), ("outer", "v")]


def test_post_process_runs_once_per_field():
    """The ``choices`` callable runs exactly once per processing cycle."""
    counter = {"n": 0}

    def choices(form, field):
        counter["n"] += 1
        return ["a", "b"]

    Inner = make_form(item=SelectField(choices=choices))
    Outer = make_form(block=FormField(Inner))

    form = Outer(DummyPostData({"block-item": "a"}))
    assert counter["n"] == 1
    assert form.block.form.item.choices is not None


def test_post_process_propagates_through_field_list():
    """``post_process`` is invoked on every ``FieldList`` entry."""
    counter = {"n": 0}

    def choices(form, field):
        counter["n"] += 1
        return ["a", "b"]

    Inner = make_form(item=SelectField(choices=choices))
    Outer = make_form(items=FieldList(FormField(Inner), min_entries=2))

    form = Outer()
    assert counter["n"] == 2
    for entry in form.items.entries:
        assert entry.form.item.choices is not None


def test_post_process_mutation_propagates_top_down():
    """A mutation done before super() in the root's post_process is visible
    to nested fields' post_process."""
    captured = []

    def choices(form, field):
        captured.append(form._parent_form.tenant.data)
        return ["a"]

    class Inner(Form):
        item = SelectField(choices=choices)

    class Outer(Form):
        tenant = StringField()
        block = FormField(Inner)

        def post_process(self):
            self.tenant.data = (self.tenant.data or "").upper()
            super().post_process()

    Outer(DummyPostData({"tenant": "acme", "block-item": "a"}))
    assert captured == ["ACME"]


def test_choices_callback_in_subform_can_read_parent():
    """A ``choices`` callable in a nested form can reach the parent form."""
    captured = []

    def choices(form, field):
        captured.append(form._parent_form.tenant.data)
        return ["a", "b"]

    Inner = make_form(group=SelectField(choices=choices))
    Outer = make_form(tenant=StringField(), block=FormField(Inner))

    form = Outer(DummyPostData({"tenant": "acme", "block-group": "a"}))
    list(form.block.form.group)

    assert captured == ["acme"]


def test_populate_missing_obj(F1):
    obj = AttrDict(a=None)
    obj2 = AttrDict(a=AttrDict(a="mmm"))
    form = F1()
    with pytest.raises(TypeError):
        form.populate_obj(obj)
    form.populate_obj(obj2)


def test_populate_property(F1):
    obj1 = ClassWithProperty(a_={"a": "old_a", "b": "old_b"})
    form = F1(DummyPostData({"a-a": "new_a", "a-b": "new_b"}))
    form.populate_obj(obj1)
    assert obj1.a_ == {"a": "new_a", "b": "new_b"}
    obj2 = ClassWithProperty()
    form.populate_obj(obj2)
    assert obj1.a_ == {"a": "new_a", "b": "new_b"}
