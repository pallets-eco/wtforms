#!/usr/bin/env python
from unittest import TestCase

from wtforms.form import BaseForm, Form
from wtforms.fields import TextField, IntegerField
from wtforms.validators import ValidationError


class DummyPostData(dict):
    def getlist(self, key):
        return self[key]

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
        self.assert_('test' in form)
        self.assert_('abcd' not in form)

    def test_field_removal(self):
        form = self.get_form()
        del form['test']
        self.assertRaises(AttributeError, getattr, form, 'test')
        self.assert_('test' not in form)

    def test_field_adding(self):
        form = self.get_form()
        self.assertEqual(len(list(form)), 1)
        form['foo'] = TextField()
        self.assertEqual(len(list(form)), 2)
        form.process(DummyPostData(foo=[u'hello']))
        self.assertEqual(form['foo'].data, u'hello')
        form['test'] = IntegerField()
        self.assert_(isinstance(form['test'], IntegerField))
        self.assertEqual(len(list(form)), 2)
        self.assertRaises(AttributeError, getattr, form['test'], 'data')
        form.process(DummyPostData(test=[u'1']))
        self.assertEqual(form['test'].data, 1)
        self.assertEqual(form['foo'].data, u'')

    def test_populate_obj(self):
        m = type('Model', (object, ), {})
        form = self.get_form()
        form.process(test='foobar')
        form.populate_obj(m)
        self.assertEqual(m.test, 'foobar')
        self.assertEqual([k for k in dir(m) if not k.startswith('_')], ['test'])

    def test_prefixes(self):
        self.assertEqual(self.get_form(prefix='foo').test.name, 'foo-test')
        self.assertEqual(self.get_form(prefix='foo').test.short_name, 'test')
        self.assertEqual(self.get_form(prefix='foo').test.id, 'foo-test')
        form = self.get_form(prefix='foo.')
        form.process(DummyPostData({'foo.test': [u'hello'], 'test': [u'bye']}))
        self.assertEqual(form.test.data, u'hello')
        self.assertEqual(self.get_form(prefix='foo[')['test'].name, 'foo[-test')


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
        A(); B()
        self.assert_(A.a is B.a)
        self.assert_(A.c is not B.c)
        self.assertEqual(A._unbound_fields, [('a', A.a), ('c', A.c)])
        self.assertEqual(B._unbound_fields, [('a', B.a), ('b', B.b), ('c', B.c)])

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

    def test_field_removal(self):
        form = self.F()
        del form.test
        self.assert_('test' not in form)
        self.assertEqual(form.test, None)
        self.assertEqual(len(list(form)), 0)

    def test_ordered_fields(self):
        class MyForm(Form):
            strawberry = TextField()
            banana     = TextField()
            kiwi       = TextField()

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


if __name__ == '__main__':
    from unittest import main
    main()
