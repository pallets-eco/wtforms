#!/usr/bin/env python
from unittest import TestCase
from wtforms.widgets import html_params
from wtforms.widgets import *


class DummyField(object):
    def __init__(self, data, name='field', label='', id=''):
        self.data = data
        self.name = name
        self.label = label
        self.id = id

    _value       = lambda x: x.data
    __unicode__  = lambda x: x.data
    __call__     = lambda x, **k: x.data
    __iter__     = lambda x: iter(x.data)
    iter_choices = lambda x: iter(x.data)
    


class HTMLParamsTest(TestCase):
    def test(self):
        self.assertEqual(html_params(foo=9, k='wuuu'), u'foo="9" k="wuuu"')
        self.assertEqual(html_params(class_='foo'), u'class="foo"')
        self.assertEqual(html_params(class__='foo'), u'class_="foo"')
        self.assertEqual(html_params(for_='foo'), u'for="foo"')


class ListWidgetTest(TestCase):
    
    def test(self):
        # ListWidget just expects an iterable of field-like objects as its
        # 'field' so that is what we will give it
        field = DummyField([DummyField(x, label='l' + x) for x in ['foo', 'bar']], id='hai')

        self.assertEqual(ListWidget()(field), u'<ul id="hai"><li>lfoo: foo</li><li>lbar: bar</li></ul>')

        w = ListWidget(html_tag='ol', prefix_label=False)
        self.assertEqual(w(field), u'<ol id="hai"><li>foo lfoo</li><li>bar lbar</li></ol>')


class TableWidgetTest(TestCase):
    pass # TODO


class BasicWidgetsTest(TestCase):
    """Test most of the basic input widget types"""

    field = DummyField('foo', name='bar', label='label', id='id') 

    def test_text_input(self):
        self.assertEqual(TextInput()(self.field), u'<input id="id" name="bar" type="text" value="foo" />')

    def test_password_input(self):
        self.assert_(u'type="password"' in PasswordInput()(self.field))
        self.assert_(u'value=""' in PasswordInput()(self.field))
        self.assert_(u'value="foo"' in PasswordInput(hide_value=False)(self.field))

    def test_hidden_input(self):
        self.assert_(u'type="hidden"' in HiddenInput()(self.field))

    def test_checkbox_input(self):
        self.assertEqual(CheckboxInput()(self.field, value='v'), '<input checked="checked" id="id" name="bar" type="checkbox" value="v" />')
        field2 = DummyField(False)
        self.assert_(u'checked' not in CheckboxInput()(field2))

    def test_radio_input(self):
        pass

    def test_textarea(self):
        # Make sure textareas escape properly and render properly
        f = DummyField('hi<>bye')
        self.assertEqual(TextArea()(f), '<textarea id="" name="field">hi&lt;&gt;bye</textarea>')


class SelectTest(TestCase):
    pass # TODO
    

if __name__ == '__main__':
    from unittest import main
    main()
