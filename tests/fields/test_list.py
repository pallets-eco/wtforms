from collections import namedtuple

import pytest
from tests.common import DummyPostData

from wtforms import validators
from wtforms.fields import FieldList
from wtforms.fields import FormField
from wtforms.fields import StringField
from wtforms.form import Form


class AttrDict:
    def __init__(self, *args, **kw):
        self.__dict__.update(*args, **kw)


def make_form(name="F", **fields):
    return type(str(name), (Form,), fields)


t = StringField(validators=[validators.DataRequired()])


def test_form():
    F = make_form(a=FieldList(t))
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


def test_enclosed_subform():
    def make_inner():
        return AttrDict(a=None)

    F = make_form(a=FieldList(FormField(make_form("FChild", a=t), default=make_inner)))
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


def test_enclosed_subform_custom_name():
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


def test_custom_separator():
    F = make_form(a=FieldList(t, separator="_"))

    pdata = DummyPostData({"a_0": "0_a", "a_1": "1_a"})
    f = F(pdata)
    assert f.a[0].data == "0_a"
    assert f.a[1].data == "1_a"


def test_enclosed_subform_list_separator():
    class Inside(Form):
        foo = StringField(default="default")

    class Outside(Form):
        subforms = FieldList(FormField(Inside), min_entries=1, separator="_")

    o = Outside()
    assert o.subforms[0].foo.data == "default"
    assert o.subforms[0].foo.name == "subforms_0-foo"

    pdata = DummyPostData({"subforms_0-foo": "0-foo", "subforms_1-foo": "1-foo"})
    o = Outside(pdata)
    assert o.subforms[0].foo.data == "0-foo"
    assert o.subforms[1].foo.data == "1-foo"


def test_enclosed_subform_uniform_separators():
    class Inside(Form):
        foo = StringField(default="default")

    class Outside(Form):
        subforms = FieldList(
            FormField(Inside, separator="_"), min_entries=1, separator="_"
        )

    o = Outside()
    assert o.subforms[0].foo.data == "default"
    assert o.subforms[0].foo.name == "subforms_0_foo"

    pdata = DummyPostData({"subforms_0_foo": "0_foo", "subforms_1_foo": "1_foo"})
    o = Outside(pdata)
    assert o.subforms[0].foo.data == "0_foo"
    assert o.subforms[1].foo.data == "1_foo"


def test_enclosed_subform_mixed_separators():
    class Inside(Form):
        foo = StringField(default="default")

    class Outside(Form):
        subforms = FieldList(FormField(Inside, separator="_"), min_entries=1)

    o = Outside()
    assert o.subforms[0].foo.data == "default"
    assert o.subforms[0].foo.name == "subforms-0_foo"

    pdata = DummyPostData({"subforms-0_foo": "0_foo", "subforms-1_foo": "1_foo"})
    o = Outside(pdata)
    assert o.subforms[0].foo.data == "0_foo"
    assert o.subforms[1].foo.data == "1_foo"


def test_entry_management():
    F = make_form(a=FieldList(t))
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


def test_min_max_entries():
    F = make_form(a=FieldList(t, min_entries=1, max_entries=3))
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


def test_validators():
    def validator(form, field):
        if field.data and field.data[0] == "fail":
            raise validators.ValidationError("fail")
        elif len(field.data) > 2:
            raise validators.ValidationError("too many")

    F = make_form(a=FieldList(t, validators=[validator]))

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


def test_no_filters():
    with pytest.raises(TypeError):
        FieldList(t, filters=[str], _form=Form(), name="foo")


def test_process_prefilled():
    data = ["foo", "hi", "rawr"]
    Obj = namedtuple("Obj", "a")
    obj = Obj(data)
    F = make_form(a=FieldList(t))
    # fill form
    form = F(obj=obj)
    assert len(form.a.entries) == 3
    # pretend to submit form unchanged
    pdata = DummyPostData({"a-0": ["foo"], "a-1": ["hi"], "a-2": ["rawr"]})
    form.process(formdata=pdata)
    # check if data still the same
    assert len(form.a.entries) == 3
    assert form.a.data == data


def test_errors():
    F = make_form(a=FieldList(t))
    form = F(DummyPostData({"a-0": ["a"], "a-1": ""}))
    assert not form.validate()
    assert form.a.errors == [[], ["This field is required."]]
