import pytest
from tests.common import DummyPostData

from wtforms.fields import IntegerField
from wtforms.fields import StringField
from wtforms.form import BaseForm
from wtforms.form import Form
from wtforms.meta import DefaultMeta
from wtforms.validators import DataRequired
from wtforms.validators import ValidationError


def get_form(**kwargs):
    def validate_test(form, field):
        if field.data != "foobar":
            raise ValidationError("error")

    return BaseForm({"test": StringField(validators=[validate_test])}, **kwargs)


def test_baseform_data_proxy():
    form = get_form()
    form.process(test="foo")
    assert form.data == {"test": "foo"}


def test_baseform_errors_proxy():
    form = get_form()
    form.process(test="foobar")
    form.validate()
    assert form.errors == {}

    form = get_form()
    form.process()
    form.validate()
    assert form.errors == {"test": ["error"]}


def test_baseform_contains():
    form = get_form()
    assert "test" in form
    assert "abcd" not in form


def test_baseform_field_removal():
    form = get_form()
    del form["test"]
    with pytest.raises(AttributeError):
        form.test
    assert "test" not in form


def test_baseform_field_adding():
    form = get_form()
    assert len(list(form)) == 1
    form["foo"] = StringField()
    assert len(list(form)) == 2
    form.process(DummyPostData(foo=["hello"]))
    assert form["foo"].data == "hello"
    form["test"] = IntegerField()
    assert isinstance(form["test"], IntegerField)
    assert len(list(form)) == 2
    with pytest.raises(AttributeError):
        form["test"].data
    form.process(DummyPostData(test=["1"]))
    assert form["test"].data == 1
    assert form["foo"].data is None


def test_baseform_populate_obj():
    m = type("Model", (object,), {})
    form = get_form()
    form.process(test="foobar")
    form.populate_obj(m)
    assert m.test == "foobar"
    assert [k for k in dir(m) if not k.startswith("_")] == ["test"]


def test_baseform_prefixes():
    form = get_form(prefix="foo")
    assert form["test"].name == "foo-test"
    assert form["test"].short_name == "test"
    assert form["test"].id == "foo-test"
    form = get_form(prefix="foo.")
    form.process(DummyPostData({"foo.test": ["hello"], "test": ["bye"]}))
    assert form["test"].data == "hello"
    assert get_form(prefix="foo[")["test"].name == "foo[-test"


def test_baseform_formdata_wrapper_error():
    form = get_form()
    with pytest.raises(TypeError):
        form.process([])


def test_form_meta_monkeypatch():
    class F(Form):
        a = StringField()

    assert F._unbound_fields is None
    F()
    assert F._unbound_fields == [("a", F.a)]
    F.b = StringField()
    assert F._unbound_fields is None
    F()
    assert F._unbound_fields == [("a", F.a), ("b", F.b)]
    del F.a
    with pytest.raises(AttributeError):
        F.a
    F()
    assert F._unbound_fields == [("b", F.b)]
    F._m = StringField()
    assert F._unbound_fields == [("b", F.b)]


def test_form_meta_subclassing():
    class A(Form):
        a = StringField()
        c = StringField()

    class B(A):
        b = StringField()
        c = StringField()

    A()
    B()

    assert A.a is B.a
    assert A.c is not B.c
    assert A._unbound_fields == [("a", A.a), ("c", A.c)]
    assert B._unbound_fields == [("a", B.a), ("b", B.b), ("c", B.c)]


def test_form_meta_class_meta_reassign():
    class MetaA:
        pass

    class MetaB:
        pass

    class F(Form):
        Meta = MetaA

    assert F._wtforms_meta is None
    assert isinstance(F().meta, MetaA)
    assert issubclass(F._wtforms_meta, MetaA)
    F.Meta = MetaB
    assert F._wtforms_meta is None
    assert isinstance(F().meta, MetaB)
    assert issubclass(F._wtforms_meta, MetaB)


class F(Form):
    test = StringField()

    def validate_test(self, field):
        if field.data != "foobar":
            raise ValidationError("error")


def test_validate():
    form = F(test="foobar")
    assert form.validate() is True

    form = F()
    assert form.validate() is False


def test_validate_with_extra():
    class F2(F):
        other = StringField()

    def extra(form, field):
        if field.data != "extra":
            raise ValidationError("error")

    form = F2(test="foobar", other="extra")
    assert form.validate(extra_validators={"other": [extra]})

    form = F2(test="foobar", other="nope")
    assert not form.validate(extra_validators={"other": [extra]})

    form = F2(test="nope", other="extra")
    assert not form.validate(extra_validators={"other": [extra]})


def test_form_level_errors():
    class F(Form):
        a = IntegerField()
        b = IntegerField()

        def validate(self):
            if (self.a.data + self.b.data) % 2 != 0:
                self.form_errors.append("a + b should be even")
                return False

            return True

    f = F(a=1, b=1)
    assert f.validate()
    assert not f.form_errors
    assert not f.errors

    f = F(a=0, b=1)
    assert not f.validate()
    assert ["a + b should be even"] == f.form_errors
    assert ["a + b should be even"] == f.errors[None]


def test_field_adding_disabled():
    form = F()
    with pytest.raises(TypeError):
        form.__setitem__("foo", StringField())


def test_field_removal():
    form = F()
    del form.test
    assert "test" not in form
    assert form.test is None
    assert len(list(form)) == 0
    # Try deleting a nonexistent field
    with pytest.raises(AttributeError):
        form.__delattr__("fake")


def test_delattr_idempotency():
    form = F()
    del form.test
    assert form.test is None

    # Make sure deleting a normal attribute works
    form.foo = 9
    del form.foo
    with pytest.raises(AttributeError):
        form.__delattr__("foo")

    # Check idempotency
    del form.test
    assert form.test is None


def test_ordered_fields():
    class MyForm(Form):
        strawberry = StringField()
        banana = StringField()
        kiwi = StringField()

    assert [x.name for x in MyForm()] == ["strawberry", "banana", "kiwi"]
    MyForm.apple = StringField()
    assert [x.name for x in MyForm()], ["strawberry", "banana", "kiwi", "apple"]
    del MyForm.banana
    assert [x.name for x in MyForm()] == ["strawberry", "kiwi", "apple"]
    MyForm.strawberry = StringField()
    assert [x.name for x in MyForm()] == ["kiwi", "apple", "strawberry"]
    # Ensure sort is stable: two fields with the same creation counter
    # should be subsequently sorted by name.
    MyForm.cherry = MyForm.kiwi
    assert [x.name for x in MyForm()] == ["cherry", "kiwi", "apple", "strawberry"]


def test_data_arg():
    data = {"test": "foo"}
    form = F(data=data)
    assert form.test.data == "foo"
    form = F(data=data, test="bar")
    assert form.test.data == "bar"


def test_empty_formdata():
    """If formdata is empty, field.process_formdata should still
    run to handle empty data.
    """

    class EmptyStringField(StringField):
        def process_formdata(self, valuelist):
            self.data = valuelist[0] if valuelist else "processed"

    class F(Form):
        test = EmptyStringField()

    assert F().test.data is None
    assert F(test="test").test.data == "test"
    assert F(DummyPostData({"other": "other"})).test.data == "processed"
    assert F(DummyPostData()).test.data == "processed"
    assert F(DummyPostData(), test="test").test.data == "processed"
    assert F(DummyPostData({"test": "foo"}), test="test").test.data == "foo"


def test_errors_access_during_validation():
    class F(Form):
        foo = StringField(validators=[DataRequired()])

        def validate(self):
            super().validate()
            self.errors
            self.foo.errors.append("bar")
            return True

    form = F(foo="whatever")
    form.validate()

    assert {"foo": ["bar"]} == form.errors


class H(Form):
    class Meta:
        foo = 9

    test = StringField()


class G(Form):
    class Meta:
        foo = 12
        bar = 8


class Basic(H, G):
    class Meta:
        quux = 42


class MissingDiamond(H, G):
    pass


def test_meta_basic():
    form = Basic()
    meta = form.meta
    assert meta.foo == 9
    assert meta.bar == 8
    assert meta.csrf is False
    assert isinstance(meta, H.Meta)
    assert isinstance(meta, G.Meta)
    assert type(meta).__bases__ == (
        Basic.Meta,
        H.Meta,
        G.Meta,
        DefaultMeta,
    )


def test_meta_missing_diamond():
    meta = MissingDiamond().meta
    assert type(meta).__bases__ == (H.Meta, G.Meta, DefaultMeta)
