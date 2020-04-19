from __future__ import unicode_literals

import pytest

from wtforms.form import BaseForm, Form
from wtforms.meta import DefaultMeta
from wtforms.fields import StringField, IntegerField
from wtforms.validators import ValidationError, DataRequired
from tests.common import DummyPostData


class TestBaseForm:
    def get_form(self, **kwargs):
        def validate_test(form, field):
            if field.data != "foobar":
                raise ValidationError("error")

        return BaseForm({"test": StringField(validators=[validate_test])}, **kwargs)

    def test_data_proxy(self):
        form = self.get_form()
        form.process(test="foo")
        assert form.data == {"test": "foo"}

    def test_errors_proxy(self):
        form = self.get_form()
        form.process(test="foobar")
        form.validate()
        assert form.errors == {}

        form = self.get_form()
        form.process()
        form.validate()
        assert form.errors == {"test": ["error"]}

    def test_contains(self):
        form = self.get_form()
        assert "test" in form
        assert "abcd" not in form

    def test_field_removal(self):
        form = self.get_form()
        del form["test"]
        with pytest.raises(AttributeError):
            form.test
        assert "test" not in form

    def test_field_adding(self):
        form = self.get_form()
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

    def test_populate_obj(self):
        m = type(str("Model"), (object,), {})
        form = self.get_form()
        form.process(test="foobar")
        form.populate_obj(m)
        assert m.test == "foobar"
        assert [k for k in dir(m) if not k.startswith("_")] == ["test"]

    def test_prefixes(self):
        form = self.get_form(prefix="foo")
        assert form["test"].name == "foo-test"
        assert form["test"].short_name == "test"
        assert form["test"].id == "foo-test"
        form = self.get_form(prefix="foo.")
        form.process(DummyPostData({"foo.test": ["hello"], "test": ["bye"]}))
        assert form["test"].data == "hello"
        assert self.get_form(prefix="foo[")["test"].name == "foo[-test"

    def test_formdata_wrapper_error(self):
        form = self.get_form()
        with pytest.raises(TypeError):
            form.process([])


class TestFormMeta:
    def test_monkeypatch(self):
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

    def test_subclassing(self):
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

    def test_class_meta_reassign(self):
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


class TestForm:
    class F(Form):
        test = StringField()

        def validate_test(self, field):
            if field.data != "foobar":
                raise ValidationError("error")

    def test_validate(self):
        form = self.F(test="foobar")
        assert form.validate() is True

        form = self.F()
        assert form.validate() is False

    def test_field_adding_disabled(self):
        form = self.F()
        with pytest.raises(TypeError):
            form.__setitem__("foo", StringField())

    def test_field_removal(self):
        form = self.F()
        del form.test
        assert "test" not in form
        assert form.test is None
        assert len(list(form)) == 0
        # Try deleting a nonexistent field
        with pytest.raises(AttributeError):
            form.__delattr__("fake")

    def test_delattr_idempotency(self):
        form = self.F()
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

    def test_ordered_fields(self):
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

    def test_data_arg(self):
        data = {"test": "foo"}
        form = self.F(data=data)
        assert form.test.data == "foo"
        form = self.F(data=data, test="bar")
        assert form.test.data == "bar"

    def test_empty_formdata(self):
        """"If formdata is empty, field.process_formdata should still
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

    def test_errors_access_during_validation(self):
        class F(Form):
            foo = StringField(validators=[DataRequired()])

            def validate(self):
                super(F, self).validate()
                self.errors
                self.foo.errors.append("bar")
                return True

        form = F(foo="whatever")
        form.validate()

        assert {"foo": ["bar"]} == form.errors


class TestMeta:
    class F(Form):
        class Meta:
            foo = 9

        test = StringField()

    class G(Form):
        class Meta:
            foo = 12
            bar = 8

    class Basic(F, G):
        class Meta:
            quux = 42

    class MissingDiamond(F, G):
        pass

    def test_basic(self):
        form = self.Basic()
        meta = form.meta
        assert meta.foo == 9
        assert meta.bar == 8
        assert meta.csrf is False
        assert isinstance(meta, self.F.Meta)
        assert isinstance(meta, self.G.Meta)
        assert type(meta).__bases__ == (
            self.Basic.Meta,
            self.F.Meta,
            self.G.Meta,
            DefaultMeta,
        )

    def test_missing_diamond(self):
        meta = self.MissingDiamond().meta
        assert type(meta).__bases__ == (self.F.Meta, self.G.Meta, DefaultMeta)
