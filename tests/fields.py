from __future__ import unicode_literals

import sys

from datetime import date, datetime
from decimal import Decimal, ROUND_UP, ROUND_DOWN
from unittest import TestCase

from wtforms import validators, widgets, meta
from wtforms.fields import *
from wtforms.fields import Label, Field, SelectFieldBase, html5
from wtforms.form import Form
from wtforms.compat import text_type
from wtforms.utils import unset_value
from tests.common import DummyPostData

PYTHON_VERSION = sys.version_info


class AttrDict(object):
    def __init__(self, *args, **kw):
        self.__dict__.update(*args, **kw)


def make_form(_name='F', **fields):
    return type(str(_name), (Form, ), fields)


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
        expected = """<label for="test">Caption</label>"""
        label = Label('test', 'Caption')
        self.assertEqual(label(), expected)
        self.assertEqual(str(label), expected)
        self.assertEqual(text_type(label), expected)
        self.assertEqual(label.__html__(), expected)
        self.assertEqual(label().__html__(), expected)
        self.assertEqual(label('hello'), """<label for="test">hello</label>""")
        self.assertEqual(TextField('hi').bind(Form(), 'a').label.text, 'hi')
        if PYTHON_VERSION < (3,):
            self.assertEqual(repr(label), "Label(u'test', u'Caption')")
        else:
            self.assertEqual(repr(label), "Label('test', 'Caption')")
            self.assertEqual(label.__unicode__(), expected)

    def test_auto_label(self):
        t1 = TextField().bind(Form(), 'foo_bar')
        self.assertEqual(t1.label.text, 'Foo Bar')

        t2 = TextField('').bind(Form(), 'foo_bar')
        self.assertEqual(t2.label.text, '')

    def test_override_for(self):
        label = Label('test', 'Caption')
        self.assertEqual(label(for_='foo'), """<label for="foo">Caption</label>""")
        self.assertEqual(label(**{'for': 'bar'}), """<label for="bar">Caption</label>""")


class FlagsTest(TestCase):
    def setUp(self):
        t = TextField(validators=[validators.Required()]).bind(Form(), 'a')
        self.flags = t.flags

    def test_existing_values(self):
        self.assertEqual(self.flags.required, True)
        self.assertTrue('required' in self.flags)
        self.assertEqual(self.flags.optional, False)
        self.assertTrue('optional' not in self.flags)

    def test_assignment(self):
        self.assertTrue('optional' not in self.flags)
        self.flags.optional = True
        self.assertEqual(self.flags.optional, True)
        self.assertTrue('optional' in self.flags)

    def test_unset(self):
        self.flags.required = False
        self.assertEqual(self.flags.required, False)
        self.assertTrue('required' not in self.flags)

    def test_repr(self):
        self.assertEqual(repr(self.flags), '<wtforms.fields.Flags: {required}>')

    def test_underscore_property(self):
        self.assertRaises(AttributeError, getattr, self.flags, '_foo')
        self.flags._foo = 42
        self.assertEqual(self.flags._foo, 42)


class UnsetValueTest(TestCase):
    def test(self):
        self.assertEqual(str(unset_value), '<unset value>')
        self.assertEqual(repr(unset_value), '<unset value>')
        self.assertEqual(bool(unset_value), False)
        assert not unset_value
        self.assertEqual(unset_value.__nonzero__(), False)
        self.assertEqual(unset_value.__bool__(), False)


class FiltersTest(TestCase):
    class F(Form):
        a = TextField(default=' hello', filters=[lambda x: x.strip()])
        b = TextField(default='42', filters=[int, lambda x: -x])

    def test_working(self):
        form = self.F()
        self.assertEqual(form.a.data, 'hello')
        self.assertEqual(form.b.data, -42)
        assert form.validate()

    def test_failure(self):
        form = self.F(DummyPostData(a=['  foo bar  '], b=['hi']))
        self.assertEqual(form.a.data, 'foo bar')
        self.assertEqual(form.b.data, 'hi')
        self.assertEqual(len(form.b.process_errors), 1)
        assert not form.validate()


class FieldTest(TestCase):
    class F(Form):
        a = TextField(default='hello', render_kw={'readonly': True, 'foo': u'bar'})

    def setUp(self):
        self.field = self.F().a

    def test_unbound_field(self):
        unbound = self.F.a
        assert unbound.creation_counter != 0
        assert unbound.field_class is TextField
        self.assertEqual(unbound.args, ())
        self.assertEqual(unbound.kwargs, {'default': 'hello', 'render_kw': {'readonly': True, 'foo': u'bar'}})
        assert repr(unbound).startswith('<UnboundField(TextField')

    def test_htmlstring(self):
        self.assertTrue(isinstance(self.field.__html__(), widgets.HTMLString))

    def test_str_coerce(self):
        self.assertTrue(isinstance(str(self.field), str))
        self.assertEqual(str(self.field), str(self.field()))

    def test_unicode_coerce(self):
        self.assertEqual(text_type(self.field), self.field())

    def test_process_formdata(self):
        Field.process_formdata(self.field, [42])
        self.assertEqual(self.field.data, 42)

    def test_meta_attribute(self):
        # Can we pass in meta via _form?
        form = self.F()
        assert form.a.meta is form.meta

        # Can we pass in meta via _meta?
        form_meta = meta.DefaultMeta()
        field = TextField(_name='Foo', _form=None, _meta=form_meta)
        assert field.meta is form_meta

        # Do we fail if both _meta and _form are None?
        self.assertRaises(TypeError, TextField, _name='foo', _form=None)

    def test_render_kw(self):
        form = self.F()
        self.assertEqual(form.a(), u'<input foo="bar" id="a" name="a" readonly type="text" value="hello">')
        self.assertEqual(form.a(foo=u'baz'), u'<input foo="baz" id="a" name="a" readonly type="text" value="hello">')
        self.assertEqual(
            form.a(foo=u'baz', readonly=False, other='hello'),
            u'<input foo="baz" id="a" name="a" other="hello" type="text" value="hello">'
        )


class PrePostTestField(TextField):
    def pre_validate(self, form):
        if self.data == "stoponly":
            raise validators.StopValidation()
        elif self.data.startswith("stop"):
            raise validators.StopValidation("stop with message")

    def post_validate(self, form, stopped):
        if self.data == "p":
            raise ValueError("Post")
        elif stopped and self.data == "stop-post":
            raise ValueError("Post-stopped")


class PrePostValidationTest(TestCase):
    class F(Form):
        a = PrePostTestField(validators=[validators.Length(max=1, message="too long")])

    def _init_field(self, value):
        form = self.F(a=value)
        form.validate()
        return form.a

    def test_pre_stop(self):
        a = self._init_field("long")
        self.assertEqual(a.errors, ["too long"])

        stoponly = self._init_field("stoponly")
        self.assertEqual(stoponly.errors, [])

        stopmessage = self._init_field("stopmessage")
        self.assertEqual(stopmessage.errors, ["stop with message"])

    def test_post(self):
        a = self._init_field("p")
        self.assertEqual(a.errors, ["Post"])
        stopped = self._init_field("stop-post")
        self.assertEqual(stopped.errors, ["stop with message", "Post-stopped"])


class SelectFieldTest(TestCase):
    class F(Form):
        a = SelectField(choices=[('a', 'hello'), ('btest', 'bye')], default='a')
        b = SelectField(choices=[(1, 'Item 1'), (2, 'Item 2')], coerce=int, option_widget=widgets.TextInput())

    def test_defaults(self):
        form = self.F()
        self.assertEqual(form.a.data, 'a')
        self.assertEqual(form.b.data, None)
        self.assertEqual(form.validate(), False)
        self.assertEqual(form.a(), """<select id="a" name="a"><option selected value="a">hello</option><option value="btest">bye</option></select>""")
        self.assertEqual(form.b(), """<select id="b" name="b"><option value="1">Item 1</option><option value="2">Item 2</option></select>""")

    def test_with_data(self):
        form = self.F(DummyPostData(a=['btest']))
        self.assertEqual(form.a.data, 'btest')
        self.assertEqual(form.a(), """<select id="a" name="a"><option value="a">hello</option><option selected value="btest">bye</option></select>""")

    def test_value_coercion(self):
        form = self.F(DummyPostData(b=['2']))
        self.assertEqual(form.b.data, 2)
        self.assertTrue(form.b.validate(form))
        form = self.F(DummyPostData(b=['b']))
        self.assertEqual(form.b.data, None)
        self.assertFalse(form.b.validate(form))

    def test_iterable_options(self):
        form = self.F()
        first_option = list(form.a)[0]
        self.assertTrue(isinstance(first_option, form.a._Option))
        self.assertEqual(
            list(text_type(x) for x in form.a),
            ['<option selected value="a">hello</option>', '<option value="btest">bye</option>']
        )
        self.assertTrue(isinstance(first_option.widget, widgets.Option))
        self.assertTrue(isinstance(list(form.b)[0].widget, widgets.TextInput))
        self.assertEqual(first_option(disabled=True), '<option disabled selected value="a">hello</option>')

    def test_default_coerce(self):
        F = make_form(a=SelectField(choices=[('a', 'Foo')]))
        form = F(DummyPostData(a=[]))
        assert not form.validate()
        self.assertEqual(form.a.data, 'None')
        self.assertEqual(len(form.a.errors), 1)
        self.assertEqual(form.a.errors[0], 'Not a valid choice')


class SelectMultipleFieldTest(TestCase):
    class F(Form):
        a = SelectMultipleField(choices=[('a', 'hello'), ('b', 'bye'), ('c', 'something')], default=('a', ))
        b = SelectMultipleField(coerce=int, choices=[(1, 'A'), (2, 'B'), (3, 'C')], default=("1", "3"))

    def test_defaults(self):
        form = self.F()
        self.assertEqual(form.a.data, ['a'])
        self.assertEqual(form.b.data, [1, 3])
        # Test for possible regression with null data
        form.a.data = None
        self.assertTrue(form.validate())
        self.assertEqual(list(form.a.iter_choices()), [(v, l, False) for v, l in form.a.choices])

    def test_with_data(self):
        form = self.F(DummyPostData(a=['a', 'c']))
        self.assertEqual(form.a.data, ['a', 'c'])
        self.assertEqual(list(form.a.iter_choices()), [('a', 'hello', True), ('b', 'bye', False), ('c', 'something', True)])
        self.assertEqual(form.b.data, [])
        form = self.F(DummyPostData(b=['1', '2']))
        self.assertEqual(form.b.data, [1, 2])
        self.assertTrue(form.validate())
        form = self.F(DummyPostData(b=['1', '2', '4']))
        self.assertEqual(form.b.data, [1, 2, 4])
        self.assertFalse(form.validate())

    def test_coerce_fail(self):
        form = self.F(b=['a'])
        assert form.validate()
        self.assertEqual(form.b.data, None)
        form = self.F(DummyPostData(b=['fake']))
        assert not form.validate()
        self.assertEqual(form.b.data, [1, 3])


class RadioFieldTest(TestCase):
    class F(Form):
        a = RadioField(choices=[('a', 'hello'), ('b', 'bye')], default='a')
        b = RadioField(choices=[(1, 'Item 1'), (2, 'Item 2')], coerce=int)

    def test(self):
        form = self.F()
        self.assertEqual(form.a.data, 'a')
        self.assertEqual(form.b.data, None)
        self.assertEqual(form.validate(), False)
        self.assertEqual(
            form.a(),
            (
                """<ul id="a">"""
                """<li><input checked id="a-0" name="a" type="radio" value="a"> <label for="a-0">hello</label></li>"""
                """<li><input id="a-1" name="a" type="radio" value="b"> <label for="a-1">bye</label></li></ul>"""
            )
        )
        self.assertEqual(
            form.b(),
            (
                """<ul id="b">"""
                """<li><input id="b-0" name="b" type="radio" value="1"> <label for="b-0">Item 1</label></li>"""
                """<li><input id="b-1" name="b" type="radio" value="2"> <label for="b-1">Item 2</label></li></ul>"""
            )
        )
        self.assertEqual(
            [text_type(x) for x in form.a],
            ['<input checked id="a-0" name="a" type="radio" value="a">', '<input id="a-1" name="a" type="radio" value="b">']
        )

    def test_text_coercion(self):
        # Regression test for text coercsion scenarios where the value is a boolean.
        coerce_func = lambda x: False if x == 'False' else bool(x)
        F = make_form(a=RadioField(choices=[(True, 'yes'), (False, 'no')], coerce=coerce_func))
        form = F()
        self.assertEqual(
            form.a(),
            '''<ul id="a">'''
            '''<li><input id="a-0" name="a" type="radio" value="True"> <label for="a-0">yes</label></li>'''
            '''<li><input checked id="a-1" name="a" type="radio" value="False"> <label for="a-1">no</label></li></ul>'''
        )


class TextFieldTest(TestCase):
    class F(Form):
        a = TextField()

    def test(self):
        form = self.F()
        self.assertEqual(form.a.data, None)
        self.assertEqual(form.a(), """<input id="a" name="a" type="text" value="">""")
        form = self.F(DummyPostData(a=['hello']))
        self.assertEqual(form.a.data, 'hello')
        self.assertEqual(form.a(), """<input id="a" name="a" type="text" value="hello">""")
        form = self.F(DummyPostData(b=['hello']))
        self.assertEqual(form.a.data, '')


class HiddenFieldTest(TestCase):
    class F(Form):
        a = HiddenField(default="LE DEFAULT")

    def test(self):
        form = self.F()
        self.assertEqual(form.a(), """<input id="a" name="a" type="hidden" value="LE DEFAULT">""")
        self.assertTrue(form.a.flags.hidden)


class TextAreaFieldTest(TestCase):
    class F(Form):
        a = TextAreaField(default="LE DEFAULT")

    def test(self):
        form = self.F()
        self.assertEqual(form.a(), """<textarea id="a" name="a">LE DEFAULT</textarea>""")


class PasswordFieldTest(TestCase):
    class F(Form):
        a = PasswordField(widget=widgets.PasswordInput(hide_value=False), default="LE DEFAULT")
        b = PasswordField(default="Hai")

    def test(self):
        form = self.F()
        self.assertEqual(form.a(), """<input id="a" name="a" type="password" value="LE DEFAULT">""")
        self.assertEqual(form.b(), """<input id="b" name="b" type="password" value="">""")


class FileFieldTest(TestCase):
    class F(Form):
        a = FileField(default="LE DEFAULT")

    def test(self):
        form = self.F()
        self.assertEqual(form.a(), """<input id="a" name="a" type="file">""")


class IntegerFieldTest(TestCase):
    class F(Form):
        a = IntegerField()
        b = IntegerField(default=48)

    def test(self):
        form = self.F(DummyPostData(a=['v'], b=['-15']))
        self.assertEqual(form.a.data, None)
        self.assertEqual(form.a.raw_data, ['v'])
        self.assertEqual(form.a(), """<input id="a" name="a" type="text" value="v">""")
        self.assertEqual(form.b.data, -15)
        self.assertEqual(form.b(), """<input id="b" name="b" type="text" value="-15">""")
        self.assertTrue(not form.a.validate(form))
        self.assertTrue(form.b.validate(form))
        form = self.F(DummyPostData(a=[], b=['']))
        self.assertEqual(form.a.data, None)
        self.assertEqual(form.a.raw_data, [])
        self.assertEqual(form.b.data, None)
        self.assertEqual(form.b.raw_data, [''])
        self.assertTrue(not form.validate())
        self.assertEqual(len(form.b.process_errors), 1)
        self.assertEqual(len(form.b.errors), 1)
        form = self.F(b=9)
        self.assertEqual(form.b.data, 9)
        self.assertEqual(form.a._value(), '')
        self.assertEqual(form.b._value(), '9')


class DecimalFieldTest(TestCase):
    def test(self):
        F = make_form(a=DecimalField())
        form = F(DummyPostData(a='2.1'))
        self.assertEqual(form.a.data, Decimal('2.1'))
        self.assertEqual(form.a._value(), '2.1')
        form.a.raw_data = None
        self.assertEqual(form.a._value(), '2.10')
        self.assertTrue(form.validate())
        form = F(DummyPostData(a='2,1'), a=Decimal(5))
        self.assertEqual(form.a.data, None)
        self.assertEqual(form.a.raw_data, ['2,1'])
        self.assertFalse(form.validate())
        form = F(DummyPostData(a='asdf'), a=Decimal('.21'))
        self.assertEqual(form.a._value(), 'asdf')
        assert not form.validate()

    def test_quantize(self):
        F = make_form(a=DecimalField(places=3, rounding=ROUND_UP), b=DecimalField(places=None))
        form = F(a=Decimal('3.1415926535'))
        self.assertEqual(form.a._value(), '3.142')
        form.a.rounding = ROUND_DOWN
        self.assertEqual(form.a._value(), '3.141')
        self.assertEqual(form.b._value(), '')
        form = F(a=3.14159265, b=72)
        self.assertEqual(form.a._value(), '3.142')
        self.assertTrue(isinstance(form.a.data, float))
        self.assertEqual(form.b._value(), '72')


class FloatFieldTest(TestCase):
    class F(Form):
        a = FloatField()
        b = FloatField(default=48.0)

    def test(self):
        form = self.F(DummyPostData(a=['v'], b=['-15.0']))
        self.assertEqual(form.a.data, None)
        self.assertEqual(form.a.raw_data, ['v'])
        self.assertEqual(form.a(), """<input id="a" name="a" type="text" value="v">""")
        self.assertEqual(form.b.data, -15.0)
        self.assertEqual(form.b(), """<input id="b" name="b" type="text" value="-15.0">""")
        self.assertFalse(form.a.validate(form))
        self.assertTrue(form.b.validate(form))
        form = self.F(DummyPostData(a=[], b=['']))
        self.assertEqual(form.a.data, None)
        self.assertEqual(form.a._value(), '')
        self.assertEqual(form.b.data, None)
        self.assertEqual(form.b.raw_data, [''])
        self.assertFalse(form.validate())
        self.assertEqual(len(form.b.process_errors), 1)
        self.assertEqual(len(form.b.errors), 1)
        form = self.F(b=9.0)
        self.assertEqual(form.b.data, 9.0)
        self.assertEqual(form.b._value(), "9.0")


class BooleanFieldTest(TestCase):
    class BoringForm(Form):
        bool1 = BooleanField()
        bool2 = BooleanField(default=True, false_values=())

    obj = AttrDict(bool1=None, bool2=True)

    def test_defaults(self):
        # Test with no post data to make sure defaults work
        form = self.BoringForm()
        self.assertEqual(form.bool1.raw_data, None)
        self.assertEqual(form.bool1.data, False)
        self.assertEqual(form.bool2.data, True)

    def test_rendering(self):
        form = self.BoringForm(DummyPostData(bool2="x"))
        self.assertEqual(form.bool1(), '<input id="bool1" name="bool1" type="checkbox" value="y">')
        self.assertEqual(form.bool2(), '<input checked id="bool2" name="bool2" type="checkbox" value="x">')
        self.assertEqual(form.bool2.raw_data, ['x'])

    def test_with_postdata(self):
        form = self.BoringForm(DummyPostData(bool1=['a']))
        self.assertEqual(form.bool1.raw_data, ['a'])
        self.assertEqual(form.bool1.data, True)
        form = self.BoringForm(DummyPostData(bool1=['false'], bool2=['false']))
        self.assertEqual(form.bool1.data, False)
        self.assertEqual(form.bool2.data, True)

    def test_with_model_data(self):
        form = self.BoringForm(obj=self.obj)
        self.assertEqual(form.bool1.data, False)
        self.assertEqual(form.bool1.raw_data, None)
        self.assertEqual(form.bool2.data, True)

    def test_with_postdata_and_model(self):
        form = self.BoringForm(DummyPostData(bool1=['y']), obj=self.obj)
        self.assertEqual(form.bool1.data, True)
        self.assertEqual(form.bool2.data, False)


class DateFieldTest(TestCase):
    class F(Form):
        a = DateField()
        b = DateField(format='%m/%d %Y')

    def test_basic(self):
        d = date(2008, 5, 7)
        form = self.F(DummyPostData(a=['2008-05-07'], b=['05/07', '2008']))
        self.assertEqual(form.a.data, d)
        self.assertEqual(form.a._value(), '2008-05-07')
        self.assertEqual(form.b.data, d)
        self.assertEqual(form.b._value(), '05/07 2008')

    def test_failure(self):
        form = self.F(DummyPostData(a=['2008-bb-cc'], b=['hi']))
        assert not form.validate()
        self.assertEqual(len(form.a.process_errors), 1)
        self.assertEqual(len(form.a.errors), 1)
        self.assertEqual(len(form.b.errors), 1)
        self.assertEqual(form.a.process_errors[0], 'Not a valid date value')


class DateTimeFieldTest(TestCase):
    class F(Form):
        a = DateTimeField()
        b = DateTimeField(format='%Y-%m-%d %H:%M')

    def test_basic(self):
        d = datetime(2008, 5, 5, 4, 30, 0, 0)
        # Basic test with both inputs
        form = self.F(DummyPostData(a=['2008-05-05', '04:30:00'], b=['2008-05-05 04:30']))
        self.assertEqual(form.a.data, d)
        self.assertEqual(form.a(), """<input id="a" name="a" type="text" value="2008-05-05 04:30:00">""")
        self.assertEqual(form.b.data, d)
        self.assertEqual(form.b(), """<input id="b" name="b" type="text" value="2008-05-05 04:30">""")
        self.assertTrue(form.validate())

        # Test with a missing input
        form = self.F(DummyPostData(a=['2008-05-05']))
        self.assertFalse(form.validate())
        self.assertEqual(form.a.errors[0], 'Not a valid datetime value')

        form = self.F(a=d, b=d)
        self.assertTrue(form.validate())
        self.assertEqual(form.a._value(), '2008-05-05 04:30:00')

    def test_microseconds(self):
        d = datetime(2011, 5, 7, 3, 23, 14, 424200)
        F = make_form(a=DateTimeField(format='%Y-%m-%d %H:%M:%S.%f'))
        form = F(DummyPostData(a=['2011-05-07 03:23:14.4242']))
        self.assertEqual(d, form.a.data)


class SubmitFieldTest(TestCase):
    class F(Form):
        a = SubmitField('Label')

    def test(self):
        self.assertEqual(self.F().a(), """<input id="a" name="a" type="submit" value="Label">""")


class FormFieldTest(TestCase):
    def setUp(self):
        F = make_form(
            a=TextField(validators=[validators.required()]),
            b=TextField(),
        )
        self.F1 = make_form('F1', a=FormField(F))
        self.F2 = make_form('F2', a=FormField(F, separator='::'))

    def test_formdata(self):
        form = self.F1(DummyPostData({'a-a': ['moo']}))
        self.assertEqual(form.a.form.a.name, 'a-a')
        self.assertEqual(form.a['a'].data, 'moo')
        self.assertEqual(form.a['b'].data, '')
        self.assertTrue(form.validate())

    def test_iteration(self):
        self.assertEqual([x.name for x in self.F1().a], ['a-a', 'a-b'])

    def test_with_obj(self):
        obj = AttrDict(a=AttrDict(a='mmm'))
        form = self.F1(obj=obj)
        self.assertEqual(form.a.form.a.data, 'mmm')
        self.assertEqual(form.a.form.b.data, None)
        obj_inner = AttrDict(a=None, b='rawr')
        obj2 = AttrDict(a=obj_inner)
        form.populate_obj(obj2)
        self.assertTrue(obj2.a is obj_inner)
        self.assertEqual(obj_inner.a, 'mmm')
        self.assertEqual(obj_inner.b, None)

    def test_widget(self):
        self.assertEqual(
            self.F1().a(),
            '''<table id="a">'''
            '''<tr><th><label for="a-a">A</label></th><td><input id="a-a" name="a-a" type="text" value=""></td></tr>'''
            '''<tr><th><label for="a-b">B</label></th><td><input id="a-b" name="a-b" type="text" value=""></td></tr>'''
            '''</table>'''
        )

    def test_separator(self):
        form = self.F2(DummyPostData({'a-a': 'fake', 'a::a': 'real'}))
        self.assertEqual(form.a.a.name, 'a::a')
        self.assertEqual(form.a.a.data, 'real')
        self.assertTrue(form.validate())

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

    def test_populate_missing_obj(self):
        obj = AttrDict(a=None)
        obj2 = AttrDict(a=AttrDict(a='mmm'))
        form = self.F1()
        self.assertRaises(TypeError, form.populate_obj, obj)
        form.populate_obj(obj2)


class FieldListTest(TestCase):
    t = TextField(validators=[validators.Required()])

    def test_form(self):
        F = make_form(a=FieldList(self.t))
        data = ['foo', 'hi', 'rawr']
        a = F(a=data).a
        self.assertEqual(a.entries[1].data, 'hi')
        self.assertEqual(a.entries[1].name, 'a-1')
        self.assertEqual(a.data, data)
        self.assertEqual(len(a.entries), 3)

        pdata = DummyPostData({'a-0': ['bleh'], 'a-3': ['yarg'], 'a-4': [''], 'a-7': ['mmm']})
        form = F(pdata)
        self.assertEqual(len(form.a.entries), 4)
        self.assertEqual(form.a.data, ['bleh', 'yarg', '', 'mmm'])
        self.assertFalse(form.validate())

        form = F(pdata, a=data)
        self.assertEqual(form.a.data, ['bleh', 'yarg', '', 'mmm'])
        self.assertFalse(form.validate())

        # Test for formdata precedence
        pdata = DummyPostData({'a-0': ['a'], 'a-1': ['b']})
        form = F(pdata, a=data)
        self.assertEqual(len(form.a.entries), 2)
        self.assertEqual(form.a.data, ['a', 'b'])
        self.assertEqual(list(iter(form.a)), list(form.a.entries))

    def test_enclosed_subform(self):
        make_inner = lambda: AttrDict(a=None)
        F = make_form(
            a=FieldList(FormField(make_form('FChild', a=self.t), default=make_inner))
        )
        data = [{'a': 'hello'}]
        form = F(a=data)
        self.assertEqual(form.a.data, data)
        self.assertTrue(form.validate())
        form.a.append_entry()
        self.assertEqual(form.a.data, data + [{'a': None}])
        self.assertFalse(form.validate())

        pdata = DummyPostData({'a-0': ['fake'], 'a-0-a': ['foo'], 'a-1-a': ['bar']})
        form = F(pdata, a=data)
        self.assertEqual(form.a.data, [{'a': 'foo'}, {'a': 'bar'}])

        inner_obj = make_inner()
        inner_list = [inner_obj]
        obj = AttrDict(a=inner_list)
        form.populate_obj(obj)
        self.assertTrue(obj.a is not inner_list)
        self.assertEqual(len(obj.a), 2)
        self.assertTrue(obj.a[0] is inner_obj)
        self.assertEqual(obj.a[0].a, 'foo')
        self.assertEqual(obj.a[1].a, 'bar')

        # Test failure on populate
        obj2 = AttrDict(a=42)
        self.assertRaises(TypeError, form.populate_obj, obj2)

    def test_entry_management(self):
        F = make_form(a=FieldList(self.t))
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
        F = make_form(a=FieldList(self.t, min_entries=1, max_entries=3))
        a = F().a
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0].data, None)
        big_input = ['foo', 'flaf', 'bar', 'baz']
        self.assertRaises(AssertionError, F, a=big_input)
        pdata = DummyPostData(('a-%d' % i, v) for i, v in enumerate(big_input))
        a = F(pdata).a
        self.assertEqual(a.data, ['foo', 'flaf', 'bar'])
        self.assertRaises(AssertionError, a.append_entry)

    def test_validators(self):
        def validator(form, field):
            if field.data and field.data[0] == 'fail':
                raise ValueError('fail')
            elif len(field.data) > 2:
                raise ValueError('too many')

        F = make_form(a=FieldList(self.t, validators=[validator]))

        # Case 1: length checking validators work as expected.
        fdata = DummyPostData({'a-0': ['hello'], 'a-1': ['bye'], 'a-2': ['test3']})
        form = F(fdata)
        assert not form.validate()
        self.assertEqual(form.a.errors, ['too many'])

        # Case 2: checking a value within.
        fdata['a-0'] = ['fail']
        form = F(fdata)
        assert not form.validate()
        self.assertEqual(form.a.errors, ['fail'])

        # Case 3: normal field validator still works
        form = F(DummyPostData({'a-0': ['']}))
        assert not form.validate()
        self.assertEqual(form.a.errors, [['This field is required.']])

    def test_no_filters(self):
        my_filter = lambda x: x
        self.assertRaises(TypeError, FieldList, self.t, filters=[my_filter], _form=Form(), _name='foo')

    def test_process_prefilled(self):
        data = ['foo', 'hi', 'rawr']

        class A(object):
            def __init__(self, a):
                self.a = a
        obj = A(data)
        F = make_form(a=FieldList(self.t))
        # fill form
        form = F(obj=obj)
        self.assertEqual(len(form.a.entries), 3)
        # pretend to submit form unchanged
        pdata = DummyPostData({
            'a-0': ['foo'],
            'a-1': ['hi'],
            'a-2': ['rawr']})
        form.process(formdata=pdata)
        # check if data still the same
        self.assertEqual(len(form.a.entries), 3)
        self.assertEqual(form.a.data, data)


class MyCustomField(TextField):
    def process_data(self, data):
        if data == 'fail':
            raise ValueError('Contrived Failure')

        return super(MyCustomField, self).process_data(data)


class CustomFieldQuirksTest(TestCase):
    class F(Form):
        a = MyCustomField()
        b = SelectFieldBase()

    def test_processing_failure(self):
        form = self.F(a='42')
        assert form.validate()
        form = self.F(a='fail')
        assert not form.validate()

    def test_default_impls(self):
        f = self.F()
        self.assertRaises(NotImplementedError, f.b.iter_choices)


class HTML5FieldsTest(TestCase):
    class F(Form):
        search = html5.SearchField()
        telephone = html5.TelField()
        url = html5.URLField()
        email = html5.EmailField()
        datetime = html5.DateTimeField()
        date = html5.DateField()
        dt_local = html5.DateTimeLocalField()
        integer = html5.IntegerField()
        decimal = html5.DecimalField()
        int_range = html5.IntegerRangeField()
        decimal_range = html5.DecimalRangeField()

    def _build_value(self, key, form_input, expected_html, data=unset_value):
        if data is unset_value:
            data = form_input
        if expected_html.startswith('type='):
            expected_html = '<input id="%s" name="%s" %s value="%s">' % (key, key, expected_html, form_input)
        return {
            'key': key,
            'form_input': form_input,
            'expected_html': expected_html,
            'data': data
        }

    def test_simple(self):
        b = self._build_value
        VALUES = (
            b('search', 'search', 'type="search"'),
            b('telephone', '123456789', 'type="tel"'),
            b('url', 'http://wtforms.simplecodes.com/', 'type="url"'),
            b('email', 'foo@bar.com', 'type="email"'),
            b('datetime', '2013-09-05 00:23:42', 'type="datetime"', datetime(2013, 9, 5, 0, 23, 42)),
            b('date', '2013-09-05', 'type="date"', date(2013, 9, 5)),
            b('dt_local', '2013-09-05 00:23:42', 'type="datetime-local"', datetime(2013, 9, 5, 0, 23, 42)),
            b('integer', '42', '<input id="integer" name="integer" step="1" type="number" value="42">', 42),
            b('decimal', '43.5', '<input id="decimal" name="decimal" step="any" type="number" value="43.5">', Decimal('43.5')),
            b('int_range', '4', '<input id="int_range" name="int_range" step="1" type="range" value="4">', 4),
            b('decimal_range', '58', '<input id="decimal_range" name="decimal_range" step="any" type="range" value="58">', 58),
        )
        formdata = DummyPostData()
        kw = {}
        for item in VALUES:
            formdata[item['key']] = item['form_input']
            kw[item['key']] = item['data']

        form = self.F(formdata)
        for item in VALUES:
            field = form[item['key']]
            render_value = field()
            if render_value != item['expected_html']:
                tmpl = 'Field {key} render mismatch: {render_value!r} != {expected_html!r}'
                raise AssertionError(tmpl.format(render_value=render_value, **item))
            if field.data != item['data']:
                tmpl = 'Field {key} data mismatch: {field.data!r} != {data!r}'
                raise AssertionError(tmpl.format(field=field, **item))
