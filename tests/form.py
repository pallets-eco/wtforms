from __future__ import unicode_literals

from unittest import TestCase

from wtforms.form import BaseForm, Form
from wtforms.meta import DefaultMeta
from wtforms.fields import TextField, IntegerField
from wtforms.validators import ValidationError
from tests.common import DummyPostData


class BaseFormTest(TestCase):
    def get_form(self, **kwargs):
        def validate_test(form, field):
            if field.data != 'foobar':
                raise ValidationError('error')

        return BaseForm({'test': TextField(validators=[validate_test])}, **kwargs)

    def test_data_proxy(self):
        form = self.get_form()
        form.process(test='foo')
        self.assertEqual(form.data, {'test': 'foo'})

    def test_errors_proxy(self):
        form = self.get_form()
        form.process(test='foobar')
        form.validate()
        self.assertEqual(form.errors, {})

        form = self.get_form()
        form.process()
        form.validate()
        self.assertEqual(form.errors, {'test': ['error']})

    def test_contains(self):
        form = self.get_form()
        self.assertTrue('test' in form)
        self.assertTrue('abcd' not in form)

    def test_field_removal(self):
        form = self.get_form()
        del form['test']
        self.assertRaises(AttributeError, getattr, form, 'test')
        self.assertTrue('test' not in form)

    def test_field_adding(self):
        form = self.get_form()
        self.assertEqual(len(list(form)), 1)
        form['foo'] = TextField()
        self.assertEqual(len(list(form)), 2)
        form.process(DummyPostData(foo=['hello']))
        self.assertEqual(form['foo'].data, 'hello')
        form['test'] = IntegerField()
        self.assertTrue(isinstance(form['test'], IntegerField))
        self.assertEqual(len(list(form)), 2)
        self.assertRaises(AttributeError, getattr, form['test'], 'data')
        form.process(DummyPostData(test=['1']))
        self.assertEqual(form['test'].data, 1)
        self.assertEqual(form['foo'].data, '')

    def test_populate_obj(self):
        m = type(str('Model'), (object, ), {})
        form = self.get_form()
        form.process(test='foobar')
        form.populate_obj(m)
        self.assertEqual(m.test, 'foobar')
        self.assertEqual([k for k in dir(m) if not k.startswith('_')], ['test'])

    def test_prefixes(self):
        form = self.get_form(prefix='foo')
        self.assertEqual(form['test'].name, 'foo-test')
        self.assertEqual(form['test'].short_name, 'test')
        self.assertEqual(form['test'].id, 'foo-test')
        form = self.get_form(prefix='foo.')
        form.process(DummyPostData({'foo.test': ['hello'], 'test': ['bye']}))
        self.assertEqual(form['test'].data, 'hello')
        self.assertEqual(self.get_form(prefix='foo[')['test'].name, 'foo[-test')

    def test_formdata_wrapper_error(self):
        form = self.get_form()
        self.assertRaises(TypeError, form.process, [])


class FormMetaTest(TestCase):
    def test_monkeypatch(self):
        class F(Form):
            a = TextField()

        self.assertEqual(F._unbound_fields, None)
        F()
        self.assertEqual(F._unbound_fields, [('a', F.a)])
        F.b = TextField()
        self.assertEqual(F._unbound_fields, None)
        F()
        self.assertEqual(F._unbound_fields, [('a', F.a), ('b', F.b)])
        del F.a
        self.assertRaises(AttributeError, lambda: F.a)
        F()
        self.assertEqual(F._unbound_fields, [('b', F.b)])
        F._m = TextField()
        self.assertEqual(F._unbound_fields, [('b', F.b)])

    def test_subclassing(self):
        class A(Form):
            a = TextField()
            c = TextField()

        class B(A):
            b = TextField()
            c = TextField()
        A()
        B()

        self.assertTrue(A.a is B.a)
        self.assertTrue(A.c is not B.c)
        self.assertEqual(A._unbound_fields, [('a', A.a), ('c', A.c)])
        self.assertEqual(B._unbound_fields, [('a', B.a), ('b', B.b), ('c', B.c)])

    def test_class_meta_reassign(self):
        class MetaA:
            pass

        class MetaB:
            pass

        class F(Form):
            Meta = MetaA

        self.assertEqual(F._wtforms_meta, None)
        assert isinstance(F().meta, MetaA)
        assert issubclass(F._wtforms_meta, MetaA)
        F.Meta = MetaB
        self.assertEqual(F._wtforms_meta, None)
        assert isinstance(F().meta, MetaB)
        assert issubclass(F._wtforms_meta, MetaB)


class FormTest(TestCase):
    class F(Form):
        test = TextField()

        def validate_test(form, field):
            if field.data != 'foobar':
                raise ValidationError('error')

    def test_validate(self):
        form = self.F(test='foobar')
        self.assertEqual(form.validate(), True)

        form = self.F()
        self.assertEqual(form.validate(), False)

    def test_field_adding_disabled(self):
        form = self.F()
        self.assertRaises(TypeError, form.__setitem__, 'foo', TextField())

    def test_field_removal(self):
        form = self.F()
        del form.test
        self.assertTrue('test' not in form)
        self.assertEqual(form.test, None)
        self.assertEqual(len(list(form)), 0)
        # Try deleting a nonexistent field
        self.assertRaises(AttributeError, form.__delattr__, 'fake')

    def test_delattr_idempotency(self):
        form = self.F()
        del form.test
        self.assertEqual(form.test, None)

        # Make sure deleting a normal attribute works
        form.foo = 9
        del form.foo
        self.assertRaises(AttributeError, form.__delattr__, 'foo')

        # Check idempotency
        del form.test
        self.assertEqual(form.test, None)

    def test_ordered_fields(self):
        class MyForm(Form):
            strawberry = TextField()
            banana = TextField()
            kiwi = TextField()

        self.assertEqual([x.name for x in MyForm()], ['strawberry', 'banana', 'kiwi'])
        MyForm.apple = TextField()
        self.assertEqual([x.name for x in MyForm()], ['strawberry', 'banana', 'kiwi', 'apple'])
        del MyForm.banana
        self.assertEqual([x.name for x in MyForm()], ['strawberry', 'kiwi', 'apple'])
        MyForm.strawberry = TextField()
        self.assertEqual([x.name for x in MyForm()], ['kiwi', 'apple', 'strawberry'])
        # Ensure sort is stable: two fields with the same creation counter
        # should be subsequently sorted by name.
        MyForm.cherry = MyForm.kiwi
        self.assertEqual([x.name for x in MyForm()], ['cherry', 'kiwi', 'apple', 'strawberry'])

    def test_data_arg(self):
        data = {'test': 'foo'}
        form = self.F(data=data)
        self.assertEqual(form.test.data, 'foo')
        form = self.F(data=data, test='bar')
        self.assertEqual(form.test.data, 'bar')


class MetaTest(TestCase):
    class F(Form):
        class Meta:
            foo = 9

        test = TextField()

    class G(Form):
        class Meta:
            foo = 12
            bar = 8

    class H(F, G):
        class Meta:
            quux = 42

    class I(F, G):
        pass

    def test_basic(self):
        form = self.H()
        meta = form.meta
        self.assertEqual(meta.foo, 9)
        self.assertEqual(meta.bar, 8)
        self.assertEqual(meta.csrf, False)
        assert isinstance(meta, self.F.Meta)
        assert isinstance(meta, self.G.Meta)
        self.assertEqual(type(meta).__bases__, (
            self.H.Meta,
            self.F.Meta,
            self.G.Meta,
            DefaultMeta
        ))

    def test_missing_diamond(self):
        meta = self.I().meta
        self.assertEqual(type(meta).__bases__, (
            self.F.Meta,
            self.G.Meta,
            DefaultMeta
        ))
