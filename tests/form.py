#!/usr/bin/env python
"""
    form
    ~~~~
    
    Unittests for Form.
    
    :copyright: 2009 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""

from unittest import TestCase
from wtforms import Form, TextField
from wtforms.validators import ValidationError

class FormMetaTest(TestCase):
    def test_monkeypatch(self):
        class F(Form):
            a = TextField()

        self.assertEqual(F._unbound_fields, None)
        F()
        self.assertEqual(F._unbound_fields, [(F.a, 'a')])
        F.b = TextField()
        self.assertEqual(F._unbound_fields, None)
        F()
        self.assertEqual(F._unbound_fields, [(F.a, 'a'), (F.b, 'b')])
        del F.a
        self.assertRaises(AttributeError, lambda: F.a)
        F()
        self.assertEqual(F._unbound_fields, [(F.b, 'b')])
        F._m = TextField()
        self.assertEqual(F._unbound_fields, [(F.b, 'b')])

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

    def test_data_proxy(self):
        form = self.F(test='foo')
        self.assertEqual(form.data, {'test': 'foo'})

    def test_errors_proxy(self):
        form = self.F(test='foobar')
        form.validate()
        self.assertEqual(form.errors, {})
        
        form = self.F()
        form.validate()
        self.assertEqual(form.errors, {'test': ['error']})

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

if __name__ == '__main__':
    from unittest import main
    main()
