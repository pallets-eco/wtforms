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

if __name__ == '__main__':
    from unittest import main
    main()
