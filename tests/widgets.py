from __future__ import unicode_literals

from unittest import TestCase
from wtforms.widgets import html_params, Input
from wtforms.widgets import *
from wtforms.widgets import html5


class DummyField(object):
    def __init__(self, data, name='f', label='', id='', type='TextField'):
        self.data = data
        self.name = name
        self.label = label
        self.id = id
        self.type = type

    _value = lambda x: x.data
    __unicode__ = lambda x: x.data
    __str__ = lambda x: x.data
    __call__ = lambda x, **k: x.data
    __iter__ = lambda x: iter(x.data)
    iter_choices = lambda x: iter(x.data)


class HTMLParamsTest(TestCase):
    def test_basic(self):
        self.assertEqual(html_params(foo=9, k='wuuu'), 'foo="9" k="wuuu"')
        self.assertEqual(html_params(class_='foo'), 'class="foo"')
        self.assertEqual(html_params(class__='foo'), 'class_="foo"')
        self.assertEqual(html_params(for_='foo'), 'for="foo"')
        self.assertEqual(html_params(readonly=False, foo=9), 'foo="9"')

    def test_data_prefix(self):
        self.assertEqual(html_params(data_foo=22), 'data-foo="22"')
        self.assertEqual(html_params(data_foo_bar=1), 'data-foo_bar="1"')

    def test_quoting(self):
        self.assertEqual(html_params(foo='hi&bye"quot'), 'foo="hi&amp;bye&quot;quot"')


class ListWidgetTest(TestCase):
    def test(self):
        # ListWidget just expects an iterable of field-like objects as its
        # 'field' so that is what we will give it
        field = DummyField([DummyField(x, label='l' + x) for x in ['foo', 'bar']], id='hai')

        self.assertEqual(ListWidget()(field), '<ul id="hai"><li>lfoo foo</li><li>lbar bar</li></ul>')

        w = ListWidget(html_tag='ol', prefix_label=False)
        self.assertEqual(w(field), '<ol id="hai"><li>foo lfoo</li><li>bar lbar</li></ol>')


class TableWidgetTest(TestCase):
    def test(self):
        inner_fields = [
            DummyField('hidden1', type='HiddenField'),
            DummyField('foo', label='lfoo'),
            DummyField('bar', label='lbar'),
            DummyField('hidden2', type='HiddenField'),
        ]
        field = DummyField(inner_fields, id='hai')
        self.assertEqual(
            TableWidget()(field),
            '<table id="hai"><tr><th>lfoo</th><td>hidden1foo</td></tr><tr><th>lbar</th><td>bar</td></tr></table>hidden2'
        )


class BasicWidgetsTest(TestCase):
    """Test most of the basic input widget types"""

    def setUp(self):
        self.field = DummyField('foo', name='bar', label='label', id='id')

    def test_input_type(self):
        a = Input()
        self.assertRaises(AttributeError, getattr, a, 'input_type')
        b = Input(input_type='test')
        self.assertEqual(b.input_type, 'test')

    def test_html_marking(self):
        html = TextInput()(self.field)
        self.assertTrue(hasattr(html, '__html__'))
        self.assertTrue(html.__html__() is html)

    def test_text_input(self):
        self.assertEqual(TextInput()(self.field), '<input id="id" name="bar" type="text" value="foo">')

    def test_password_input(self):
        self.assertTrue('type="password"' in PasswordInput()(self.field))
        self.assertTrue('value=""' in PasswordInput()(self.field))
        self.assertTrue('value="foo"' in PasswordInput(hide_value=False)(self.field))

    def test_hidden_input(self):
        self.assertTrue('type="hidden"' in HiddenInput()(self.field))
        self.assertTrue('hidden' in HiddenInput().field_flags)

    def test_checkbox_input(self):
        self.assertEqual(CheckboxInput()(self.field, value='v'), '<input checked id="id" name="bar" type="checkbox" value="v">')
        field2 = DummyField(False)
        self.assertTrue('checked' not in CheckboxInput()(field2))

    def test_radio_input(self):
        self.field.checked = True
        expected = '<input checked id="id" name="bar" type="radio" value="foo">'
        self.assertEqual(RadioInput()(self.field), expected)
        self.field.checked = False
        self.assertEqual(RadioInput()(self.field), expected.replace(' checked', ''))

    def test_textarea(self):
        # Make sure textareas escape properly and render properly
        f = DummyField('hi<>bye')
        self.assertEqual(TextArea()(f), '<textarea id="" name="f">hi&lt;&gt;bye</textarea>')


class SelectTest(TestCase):
    field = DummyField([('foo', 'lfoo', True), ('bar', 'lbar', False)])

    def test(self):
        self.assertEqual(
            Select()(self.field),
            '<select id="" name="f"><option selected value="foo">lfoo</option><option value="bar">lbar</option></select>'
        )
        self.assertEqual(
            Select(multiple=True)(self.field),
            '<select id="" multiple name="f"><option selected value="foo">lfoo</option><option value="bar">lbar</option></select>'
        )

    def test_render_option(self):
        # value, label, selected
        self.assertEqual(
            Select.render_option('bar', 'foo', False),
            '<option value="bar">foo</option>'
        )
        self.assertEqual(
            Select.render_option(True, 'foo', True),
            '<option selected value="True">foo</option>'
        )


class HTML5Test(TestCase):
    field = DummyField('42', name='bar', id='id')

    def test_number(self):
        i1 = html5.NumberInput(step='any')
        self.assertEqual(i1(self.field), '<input id="id" name="bar" step="any" type="number" value="42">')
        i2 = html5.NumberInput(step=2)
        self.assertEqual(i2(self.field, step=3), '<input id="id" name="bar" step="3" type="number" value="42">')
        i3 = html5.NumberInput(min=10)
        self.assertEqual(i3(self.field), '<input id="id" min="10" name="bar" type="number" value="42">')
        self.assertEqual(i3(self.field, min=5), '<input id="id" min="5" name="bar" type="number" value="42">')
        i4 = html5.NumberInput(max=100)
        self.assertEqual(i4(self.field), '<input id="id" max="100" name="bar" type="number" value="42">')
        self.assertEqual(i4(self.field, max=50), '<input id="id" max="50" name="bar" type="number" value="42">')

    def test_range(self):
        i1 = html5.RangeInput(step='any')
        self.assertEqual(i1(self.field), '<input id="id" name="bar" step="any" type="range" value="42">')
        i2 = html5.RangeInput(step=2)
        self.assertEqual(i2(self.field, step=3), '<input id="id" name="bar" step="3" type="range" value="42">')
