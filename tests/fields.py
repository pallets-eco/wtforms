#!/usr/bin/env python
from datetime import datetime
from decimal import Decimal
from unittest import TestCase

from wtforms import validators, widgets
from wtforms.fields import *
from wtforms.fields import Label
from wtforms.form import Form


class DummyPostData(dict):
    def getlist(self, key):
        v = self[key]
        if not isinstance(v, (list, tuple)):
            v = [v]
        return v

class AttrDict(dict):
    def __getattr__(self, attr):
        return self[attr]

def make_form(_name='F', **fields):
    return type(_name, (Form, ), fields)


class DefaultsTest(TestCase):
    def test(self):
        expected = 42

        def default_callable():
            return expected

        test_value = TextField(default=expected).bind(Form(), 'a')
        test_value.process(None)
        self.assertEqual(test_value.data, expected)

        test_callable = TextField(default=default_callable).bind(Form(), 'a')
        test_callable.process(None)
        self.assertEqual(test_callable.data, expected)


class LabelTest(TestCase):
    def test(self):
        expected = u"""<label for="test">Caption</label>"""
        label = Label('test', u'Caption')
        self.assertEqual(label(), expected)
        self.assertEqual(str(label), expected)
        self.assertEqual(unicode(label), expected)
        self.assertEqual(label('hello'), u"""<label for="test">hello</label>""")
        self.assertEqual(TextField(u'hi').bind(Form(), 'a').label.text, u'hi')


class FlagsTest(TestCase):
    def setUp(self):
        class F(Form):
            a = TextField(validators=[validators.required()])
        self.flags = F().a.flags

    def test_existing_values(self):
        self.assertEqual(self.flags.required, True)
        self.assert_('required' in self.flags)
        self.assertEqual(self.flags.optional, False)
        self.assert_('optional' not in self.flags)

    def test_assignment(self):
        self.flags.optional = True
        self.assertEqual(self.flags.optional, True)
        self.assert_('optional' in self.flags)

    def test_unset(self):
        self.flags.required = False
        self.assertEqual(self.flags.required, False)
        self.assert_('required' not in self.flags)


class FiltersTest(TestCase):
    class F(Form):
        a = TextField(default=' hello', filters=[lambda x: x.strip()])

    def test(self):
        self.assertEqual(self.F().a.data, 'hello')
        self.assertEqual(self.F(DummyPostData(a=['  foo bar  '])).a.data, 'foo bar')


class SelectFieldTest(TestCase):
    class F(Form):
        a = SelectField(choices=[('a', 'hello'), ('btest','bye')], default='a')
        b = SelectField(choices=[(1, 'Item 1'), (2, 'Item 2')], coerce=int)

    def test_defaults(self):
        form = self.F()
        self.assertEqual(form.a.data, u'a')
        self.assertEqual(form.b.data, None)
        self.assertEqual(form.validate(), False)
        self.assertEqual(form.a(), u"""<select id="a" name="a"><option selected="selected" value="a">hello</option><option value="btest">bye</option></select>""")
        self.assertEqual(form.b(), u"""<select id="b" name="b"><option value="1">Item 1</option><option value="2">Item 2</option></select>""")

    def test_with_data(self):
        form = self.F(DummyPostData(a=[u'btest']))
        self.assertEqual(form.a.data, u'btest')
        self.assertEqual(form.a(), u"""<select id="a" name="a"><option value="a">hello</option><option selected="selected" value="btest">bye</option></select>""")

    def test_value_coercion(self):
        form = self.F(DummyPostData(b=[u'2']))
        self.assertEqual(form.b.data, 2)
        self.assert_(form.b.validate(form))

    def test_id_attribute(self):
        form = self.F(obj=AttrDict(b=AttrDict(id=1)))
        self.assertEqual(form.b.data, 1)
        self.assertEqual(form.validate(), True)
        form.b.choices = [(3, 'false')]
        self.assertEqual(form.validate(), False)


class SelectMultipleFieldTest(TestCase):
    class F(Form):
        a = SelectMultipleField(choices=[('a', 'hello'), ('b','bye'), ('c', 'something')], default=('a', ))
        b = SelectMultipleField(coerce=int, choices=[(1, 'A'), (2, 'B'), (3, 'C')], default=("1", "3"))

    def test_defaults(self):
        form = self.F()
        self.assertEqual(form.a.data, ['a'])
        self.assertEqual(form.b.data, [1, 3])
        # Test for possible regression with null data
        form.a.data = None 
        self.assert_(form.validate())
        self.assertEqual(list(form.a.iter_choices()), [(v, l, False) for v, l in form.a.choices])

    def test_with_data(self):
        form = self.F(DummyPostData(a=['a', 'c']))
        self.assertEqual(form.a.data, ['a', 'c'])
        self.assertEqual(list(form.a.iter_choices()), [('a', 'hello', True), ('b', 'bye', False), ('c', 'something', True)])
        self.assertEqual(form.b.data, [])
        form = self.F(DummyPostData(b=['1', '2']))
        self.assertEqual(form.b.data, [1, 2])
        self.assert_(form.validate())
        form = self.F(DummyPostData(b=['1', '2', '4']))
        self.assertEqual(form.b.data, [1, 2, 4])
        self.assert_(not form.validate())


class RadioFieldTest(TestCase):
    class F(Form):
        a = RadioField(choices=[('a', 'hello'), ('b','bye')], default='a')
        b = RadioField(choices=[(1, 'Item 1'), (2, 'Item 2')], coerce=int)

    def test(self):
        form = self.F()
        self.assertEqual(form.a.data, u'a')
        self.assertEqual(form.b.data, None)
        self.assertEqual(form.validate(), False)
        self.assertEqual(form.a(), u"""<ul id="a"><li><input checked="checked" id="a_0" name="a" type="radio" value="a" /> <label for="a_0">hello</label></li><li><input id="a_1" name="a" type="radio" value="b" /> <label for="a_1">bye</label></li></ul>""")
        self.assertEqual(form.b(), u"""<ul id="b"><li><input id="b_0" name="b" type="radio" value="1" /> <label for="b_0">Item 1</label></li><li><input id="b_1" name="b" type="radio" value="2" /> <label for="b_1">Item 2</label></li></ul>""")
        self.assertEqual([unicode(x) for x in form.a], [u'<input checked="checked" id="a_0" name="a" type="radio" value="a" />', u'<input id="a_1" name="a" type="radio" value="b" />'])


class TextFieldTest(TestCase):
    class F(Form):
        a = TextField()

    def test(self):
        form = self.F()
        self.assertEqual(form.a.data, None)
        self.assertEqual(form.a(), u"""<input id="a" name="a" type="text" value="" />""")
        form = self.F(DummyPostData(a=['hello']))
        self.assertEqual(form.a.data, u'hello')
        self.assertEqual(form.a(), u"""<input id="a" name="a" type="text" value="hello" />""")


class HiddenFieldTest(TestCase):
    class F(Form):
        a = HiddenField(default="LE DEFAULT")

    def test(self):
        form = self.F()
        self.assertEqual(form.a(), u"""<input id="a" name="a" type="hidden" value="LE DEFAULT" />""")


class TextAreaFieldTest(TestCase):
    class F(Form):
        a = TextAreaField(default="LE DEFAULT")

    def test(self):
        form = self.F()
        self.assertEqual(form.a(), u"""<textarea id="a" name="a">LE DEFAULT</textarea>""")


class PasswordFieldTest(TestCase):
    class F(Form):
        a = PasswordField(widget=widgets.PasswordInput(hide_value=False), default="LE DEFAULT")
        b = PasswordField(default="Hai")

    def test(self):
        form = self.F()
        self.assertEqual(form.a(), u"""<input id="a" name="a" type="password" value="LE DEFAULT" />""")
        self.assertEqual(form.b(), u"""<input id="b" name="b" type="password" value="" />""")


class FileFieldTest(TestCase):
    class F(Form):
        a = FileField(default="LE DEFAULT")

    def test(self):
        form = self.F()
        self.assertEqual(form.a(), u"""<input id="a" name="a" type="file" value="LE DEFAULT" />""")


class IntegerFieldTest(TestCase):
    class F(Form):
        a = IntegerField()
        b = IntegerField(default=48)

    def test(self):
        form = self.F(DummyPostData(a=['v'], b=['-15']))
        self.assertEqual(form.a.data, None)
        self.assertEqual(form.a(), u"""<input id="a" name="a" type="text" value="v" />""")
        self.assertEqual(form.b.data, -15)
        self.assertEqual(form.b(), u"""<input id="b" name="b" type="text" value="-15" />""")
        self.assert_(not form.validate())
        form = self.F(DummyPostData(a=[], b=['']))
        self.assertEqual(form.a.data, None)
        self.assertEqual(form.b.data, 48)
        self.assertEqual(form.b.raw_data, '')
        self.assert_(form.validate())


class DecimalFieldTest(TestCase):
    class F(Form):
        a = DecimalField()

    def test(self):
        form = self.F(DummyPostData(a=['2.1']))
        self.assertEqual(form.a.data, Decimal('2.1'))
        self.assertEqual(form.a._value(), u'2.10')


class BooleanFieldTest(TestCase):
    class BoringForm(Form):
        bool1 = BooleanField()
        bool2 = BooleanField(default=True)

    obj = AttrDict(bool1=None, bool2=True)

    def test_defaults(self):
        # Test with no post data to make sure defaults work
        form = self.BoringForm()
        self.assertEqual(form.bool1.raw_data, None)
        self.assertEqual(form.bool1.data, False)
        self.assertEqual(form.bool2.data, True)

    def test_rendering(self):
        form = self.BoringForm()
        self.assertEqual(form.bool1(), u'<input id="bool1" name="bool1" type="checkbox" value="y" />')
        self.assertEqual(form.bool2(), u'<input checked="checked" id="bool2" name="bool2" type="checkbox" value="y" />')

    def test_with_postdata(self):
        form = self.BoringForm(DummyPostData(bool1=[u'a']))
        self.assertEqual(form.bool1.raw_data, u'a')
        self.assertEqual(form.bool1.data, True)

    def test_with_model_data(self):
        form = self.BoringForm(obj=self.obj)
        self.assertEqual(form.bool1.data, False)
        self.assertEqual(form.bool1.raw_data, None)
        self.assertEqual(form.bool2.data, True)

    def test_with_postdata_and_model(self):
        form = self.BoringForm(DummyPostData(bool1=[u'y']), obj=self.obj)
        self.assertEqual(form.bool1.data, True)
        self.assertEqual(form.bool2.data, False)


class DateTimeFieldTest(TestCase):
    class F(Form):
        a = DateTimeField()
        b = DateTimeField(format='%Y-%m-%d %H:%M')

    def test(self):
        d = datetime(2008, 5, 5, 4, 30, 0, 0)
        form = self.F(DummyPostData(a=['2008-05-05', '04:30:00'], b=['2008-05-05 04:30']))
        self.assertEqual(form.a.data, d)
        self.assertEqual(form.a(), u"""<input id="a" name="a" type="text" value="2008-05-05 04:30:00" />""")
        self.assertEqual(form.b.data, d)
        self.assertEqual(form.b(), u"""<input id="b" name="b" type="text" value="2008-05-05 04:30" />""")


class SubmitFieldTest(TestCase):
    class F(Form):
        a = SubmitField(u'Label')

    def test(self):
        self.assertEqual(self.F().a(), """<input id="a" name="a" type="submit" value="Label" />""")


class FormFieldTest(TestCase):
    def setUp(self):
        class F(Form):
            a = TextField(validators=[validators.required()])
            b = TextField()

        class F1(Form):
            a = FormField(F)
        self.F1 = F1

    def test_formdata(self):
        form = self.F1(DummyPostData({'a-a':[u'moo']}))
        self.assertEqual(form.a.form.a.name, 'a-a')
        self.assertEqual(form.a.form.a.data, u'moo')
        self.assertEqual(form.a.form.b.data, u'')
        self.assert_(form.validate())

    def test_iteration(self):
        self.assertEqual([x.name for x in self.F1().a], ['a-a', 'a-b'])

    def test_with_obj(self):
        obj = AttrDict(a=AttrDict(a=u'mmm'))
        form = self.F1(obj=obj)
        self.assertEqual(form.a.form.a.data, u'mmm')
        self.assertEqual(form.a.form.b.data, None)
        obj_inner = AttrDict(a=None, b='rawr')
        obj2 = AttrDict(a=obj_inner)
        form.populate_obj(obj2)
        self.assert_(obj2.a is obj_inner)
        self.assertEqual(obj_inner.a, u'mmm')
        self.assertEqual(obj_inner.b, None)

    def test_widget(self):
        self.assertEqual(self.F1().a(), u'''<table id="a"><tr><th><label for="a-a">A</label><th><td><input id="a-a" name="a-a" type="text" value="" /></td></tr><tr><th><label for="a-b">B</label><th><td><input id="a-b" name="a-b" type="text" value="" /></td></tr></table>''')

    def test_no_validators_or_filters(self):
        class A(Form):
            a = FormField(self.F1, validators=[validators.required()])
        self.assertRaises(TypeError, A)
        class B(Form):
            a = FormField(self.F1, filters=[lambda x: x])
        self.assertRaises(TypeError, B)

        class C(Form):
            a = FormField(self.F1)
            def validate_a(form, field):
                pass 
        form = C()
        self.assertRaises(TypeError, form.validate)


class FieldListTest(TestCase):
    t = TextField(validators=[validators.required()])

    def test_form(self):
        F = make_form(a = FieldList(self.t))
        data = ['foo', 'hi', 'rawr']
        a = F(a=data).a
        self.assertEqual(a.entries[1].data, 'hi')
        self.assertEqual(a.entries[1].name, 'a-1')
        self.assertEqual(a.data, data)
        self.assertEqual(len(a.entries), 3)

        pdata = DummyPostData({'a-0': ['bleh'], 'a-1': ['yarg'], 'a-3': ['mmm']})
        form = F(pdata)
        self.assertEqual(len(form.a.entries), 4)
        self.assertEqual(form.a.data, [u'bleh', u'yarg', u'', u'mmm'])
        self.assert_(not form.validate())

        form = F(pdata, a=data)
        self.assertEqual(form.a.data, [u'bleh', u'yarg', u'', u'mmm'])
        self.assert_(not form.validate())

    def test_enclosed_subform(self):
        F = make_form(
            a = FieldList(FormField(make_form('FChild', a=self.t)))
        )
        data = [{'a': 'hello'}]
        form = F(a=data)
        self.assertEqual(form.a.data, data)
        self.assert_(form.validate())
        form.a.append_entry()
        self.assertEqual(form.a.data, data + [{'a': None}])
        self.assert_(not form.validate())

        pdata = DummyPostData({'a-0': ['fake'], 'a-0-a': ['foo'], 'a-1-a': ['bar']})
        form = F(pdata, a=data)
        self.assertEqual(form.a.data, [{'a': 'foo'}, {'a': 'bar'}])

    def test_entry_management(self):
        F = make_form(a = FieldList(self.t))
        a = F(a=['hello', 'bye']).a
        self.assertEqual(a.pop_entry().name, 'a-1')
        self.assertEqual(a.data, ['hello'])
        a.append_entry('orange')
        self.assertEqual(a.data, ['hello', 'orange'])
        self.assertEqual(a[-1].name, 'a-1')
        self.assertEqual(a.pop_entry().data, 'orange')
        self.assertEqual(a.pop_entry().name, 'a-0')
        self.assertRaises(IndexError, a.pop_entry)

    def test_min_max_entries(self):
        F = make_form(a = FieldList(self.t, min_entries=1, max_entries=3))
        a = F().a
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0].data, None)
        big_input = ['foo',  'flaf', 'bar', 'baz']
        self.assertRaises(AssertionError, F, a=big_input)
        pdata = DummyPostData(('a-%d' % i, v) for i, v in enumerate(big_input))
        a = F(pdata).a
        self.assertEqual(a.data, ['foo', 'flaf', 'bar'])
        self.assertRaises(AssertionError, a.append_entry)



if __name__ == '__main__':
    from unittest import main
    main()
