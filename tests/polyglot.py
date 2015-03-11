from unittest import TestCase

from wtforms import (PolyglotForm, StringField, TextAreaField, BooleanField,
                     SelectField, SelectMultipleField)
from wtforms.meta import PolyglotHTMLParser


class PolyglotHTMLParserTest(TestCase):

    def setUp(self):
        self.parser = PolyglotHTMLParser()

    def test(self):
        self.parser.feed('<input type=checkbox name=foo value=y checked>')
        self.assertEqual(self.parser.get_output(),
                         '<input type="checkbox" name="foo" value="y"'
                         ' checked="checked" />')

    def test_bad_standalone_tag(self):
        self.parser.feed('<input>')
        self.assertEqual(self.parser.get_output(), '<input />')

    def test_good_standalone_tag(self):
        self.parser.feed('<input />')
        self.assertEqual(self.parser.get_output(), '<input />')

    def test_bad_standalone_tag_with_unquoted_attribute(self):
        self.parser.feed('<input name=foo>')
        self.assertEqual(self.parser.get_output(), '<input name="foo" />')

    def test_good_standalone_tag_with_unquoted_attribute(self):
        self.parser.feed('<input name=foo />')
        self.assertEqual(self.parser.get_output(), '<input name="foo" />')

    def test_bad_standalone_tag_with_quoted_attribute(self):
        self.parser.feed('<input name="foo">')
        self.assertEqual(self.parser.get_output(), '<input name="foo" />')

    def test_good_standalone_tag_with_quoted_attribute(self):
        self.parser.feed('<input name="foo" />')
        self.assertEqual(self.parser.get_output(), '<input name="foo" />')

    def test_bad_standalone_tag_with_bad_boolean_attribute(self):
        self.parser.feed('<input checked>')
        self.assertEqual(self.parser.get_output(),
                         '<input checked="checked" />')

    def test_good_standalone_tag_with_bad_boolean_attribute(self):
        self.parser.feed('<input checked />')
        self.assertEqual(self.parser.get_output(),
                         '<input checked="checked" />')

    def test_non_standalone_tag(self):
        self.parser.feed('<ol></ol>')
        self.assertEqual(self.parser.get_output(), '<ol></ol>')

    def test_non_standalone_tag_with_unquoted_attribute(self):
        self.parser.feed('<ol type=a></ol>')
        self.assertEqual(self.parser.get_output(), '<ol type="a"></ol>')

    def test_non_standalone_tag_with_quoted_attribute(self):
        self.parser.feed('<ol type="a"></ol>')
        self.assertEqual(self.parser.get_output(), '<ol type="a"></ol>')

    def test_non_standalone_tag_with_boolean_attribute(self):
        self.parser.feed('<ol reversed></ol>')
        self.assertEqual(self.parser.get_output(),
                         '<ol reversed="reversed"></ol>')


class PolyglotFormTest(TestCase):

    def test_string_field(self):
        class MyForm(PolyglotForm):
            foo = StringField('foo')
        form = MyForm()
        self.assertEqual(form.foo(),
                         '<input id="foo" name="foo" type="text" value="" />')

    def test_empty_textarea(self):
        class MyForm(PolyglotForm):
            foo = TextAreaField('foo')
        form = MyForm()
        self.assertEqual(form.foo(),
                         '<textarea id="foo" name="foo"></textarea>')

    def test_filled_textarea(self):
        class MyForm(PolyglotForm):
            foo = TextAreaField('foo', default='bar')
        form = MyForm()
        self.assertEqual(form.foo(),
                         '<textarea id="foo" name="foo">bar</textarea>')

    def test_checked_checkbox(self):
        class MyForm(PolyglotForm):
            foo = BooleanField('foo', default=True)
        form = MyForm()
        self.assertEqual(form.foo(),
                         '<input checked="checked" id="foo" name="foo"'
                         ' type="checkbox" value="y" />')

    def test_selected_option(self):
        class MyForm(PolyglotForm):
            foo = SelectField('foo', choices=[('1', '1'), ('2', '2')],
                              default='2')
        form = MyForm()
        self.assertEqual(form.foo(),
                         '<select id="foo" name="foo">'
                         '<option value="1">1</option>'
                         '<option selected="selected" value="2">2</option>'
                         '</select>')

    def test_multiselect(self):
        class MyForm(PolyglotForm):
            foo = SelectMultipleField('foo', choices=[('1', '1'), ('2', '2')])
        form = MyForm()
        self.assertEqual(form.foo(),
                         '<select id="foo" multiple="multiple" name="foo">'
                         '<option value="1">1</option>'
                         '<option value="2">2</option>'
                         '</select>')
