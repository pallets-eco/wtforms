#!/usr/bin/env python

from __future__ import unicode_literals

import sys, os
TESTS_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, TESTS_DIR)

##########################################################################
# -- Django Initialization
#
# Unfortunately, we cannot do this in the setUp for a test case, as the
# settings.configure method cannot be called more than once, and we cannot
# control the order in which tests are run, so making a throwaway test won't
# work either.

from django.conf import settings
settings.configure(
    INSTALLED_APPS = ['ext_django', 'wtforms.ext.django'],
    # Django 1.0 to 1.3
    DATABASE_ENGINE = 'sqlite3',
    TEST_DATABASE_NAME = ':memory:',

    # Django 1.4
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    }
)

from django.db import connection
connection.creation.create_test_db(verbosity=0)

# -- End hacky Django initialization

import datetime
from django.template import Context, Template
from django.utils import timezone
from django.test import TestCase as DjangoTestCase
from django.test.utils import override_settings
from ext_django import models as test_models
from unittest import TestCase
from wtforms import Form, fields, validators
from wtforms.compat import text_type
from wtforms.ext.django.orm import model_form
from wtforms.ext.django.fields import QuerySetSelectField, ModelSelectField, DateTimeField

def contains_validator(field, v_type):
    for v in field.validators:
        if isinstance(v, v_type):
            return True
    return False

def lazy_select(field, **kwargs):
    output = []
    for val, label, selected in field.iter_choices():
        s = selected and 'Y' or 'N'
        output.append('%s:%s:%s' % (s, text_type(val), text_type(label)))
    return tuple(output)

class DummyPostData(dict):
    def getlist(self, key):
        return self[key]

class TemplateTagsTest(TestCase):
    load_tag = '{% load wtforms %}'

    class F(Form):
        a = fields.TextField('I r label')
        b = fields.SelectField(choices=[('a', 'hi'), ('b', 'bai')])

    def _render(self, source):
        t = Template(self.load_tag + source)
        return t.render(Context({'form': self.F(), 'a': self.F().a,  'someclass': "CLASSVAL>!"}))

    def test_simple_print(self):
        self.assertEqual(self._render('{% autoescape off %}{{ form.a }}{% endautoescape %}'), '<input id="a" name="a" type="text" value="">')
        self.assertEqual(self._render('{% autoescape off %}{{ form.a.label }}{% endautoescape %}'), '<label for="a">I r label</label>')
        self.assertEqual(self._render('{% autoescape off %}{{ form.a.name }}{% endautoescape %}'), 'a')

    def test_form_field(self):
        self.assertEqual(self._render('{% form_field form.a %}'), '<input id="a" name="a" type="text" value="">')
        self.assertEqual(self._render('{% form_field a class=someclass onclick="alert()" %}'),
                         '<input class="CLASSVAL&gt;!" id="a" name="a" onclick="alert()" type="text" value="">')

class ModelFormTest(TestCase):
    F = model_form(test_models.User, exclude=['id'], field_args = {
        'posts': {
            'validators': [validators.NumberRange(min=4, max=7)],
            'description': 'Test'
        }
    })
    form = F()
    form_with_pk = model_form(test_models.User)()

    def test_form_sanity(self):
        self.assertEqual(self.F.__name__, 'UserForm')
        self.assertEqual(len([x for x in self.form]), 14)
        self.assertEqual(len([x for x in self.form_with_pk]), 15)

    def test_label(self):
        self.assertEqual(self.form.reg_ip.label.text, 'IP Addy')
        self.assertEqual(self.form.posts.label.text, 'posts')

    def test_description(self):
        self.assertEqual(self.form.birthday.description, 'Teh Birthday')

    def test_max_length(self):
        self.assertTrue(contains_validator(self.form.username, validators.Length))
        self.assertFalse(contains_validator(self.form.posts, validators.Length))

    def test_optional(self):
        self.assertTrue(contains_validator(self.form.email, validators.Optional))

    def test_simple_fields(self):
        self.assertEqual(type(self.form.file), fields.FileField)
        self.assertEqual(type(self.form.file2), fields.FileField)
        self.assertEqual(type(self.form_with_pk.id), fields.IntegerField)
        self.assertEqual(type(self.form.slug), fields.TextField)
        self.assertEqual(type(self.form.birthday), fields.DateField)

    def test_custom_converters(self):
        self.assertEqual(type(self.form.email), fields.TextField)
        self.assertTrue(contains_validator(self.form.email, validators.Email))
        self.assertEqual(type(self.form.reg_ip), fields.TextField)
        self.assertTrue(contains_validator(self.form.reg_ip, validators.IPAddress))
        self.assertEqual(type(self.form.group_id), ModelSelectField)

    def test_us_states(self):
        self.assertTrue(len(self.form.state.choices) >= 50)

    def test_field_args(self):
        self.assertTrue(contains_validator(self.form.posts, validators.NumberRange))
        self.assertEqual(self.form.posts.description, 'Test')

    def test_nullbool(self):
        field = self.form.nullbool
        assert isinstance(field, fields.SelectField)
        self.assertEqual(len(field.choices), 3)

class QuerySetSelectFieldTest(DjangoTestCase):
    fixtures = ['ext_django.json']

    def setUp(self):
        from django.core.management import call_command
        self.queryset = test_models.Group.objects.all()
        class F(Form):
            a = QuerySetSelectField(allow_blank=True, get_label='name', widget=lazy_select)
            b = QuerySetSelectField(queryset=self.queryset, widget=lazy_select)

        self.F = F

    def test_queryset_freshness(self):
        form = self.F()
        self.assertTrue(form.b.queryset is not self.queryset)

    def test_with_data(self):
        form = self.F()
        form.a.queryset = self.queryset[1:]
        self.assertEqual(form.a(), ('Y:__None:', 'N:2:Admins'))
        self.assertEqual(form.a.data, None)
        self.assertEqual(form.a.validate(form), True)
        self.assertEqual(form.b.validate(form), False)
        form.b.data = test_models.Group.objects.get(pk=1)
        self.assertEqual(form.b.validate(form), True)
        self.assertEqual(form.b(), ('Y:1:Users(1)', 'N:2:Admins(2)'))

    def test_formdata(self):
        form = self.F(DummyPostData(a=['1'], b=['3']))
        form.a.queryset = self.queryset[1:]
        self.assertEqual(form.a.data, None)
        self.assertEqual(form.a.validate(form), True)
        self.assertEqual(form.b.data, None)
        self.assertEqual(form.b.validate(form), False)
        form = self.F(DummyPostData(a=['__None'], b=[2]))
        assert form.a.data is None
        self.assertEqual(form.b.data.pk, 2)
        self.assertEqual(form.b.validate(form), True)

    def test_get_label_alt(self):
        class TestForm(Form):
            a = QuerySetSelectField(queryset=self.queryset, widget=lazy_select, get_label=lambda x: x.name.upper())
        form = TestForm()
        self.assertEqual(form.a(), ('N:1:USERS', 'N:2:ADMINS'))

class ModelSelectFieldTest(DjangoTestCase):
    fixtures = ['ext_django.json']

    class F(Form):
        a = ModelSelectField(model=test_models.Group, widget=lazy_select)

    def test(self):
        form = self.F()
        self.assertEqual(form.a(), ('N:1:Users(1)', 'N:2:Admins(2)'))

class DateTimeFieldTimezoneTest(DjangoTestCase):

    class F(Form):
        a = DateTimeField()

    @override_settings(USE_TZ=True, TIME_ZONE='America/Los_Angeles')
    def test_convert_input_to_current_timezone(self):
        post_data = {'a': ['2013-09-24 00:00:00']}
        form = self.F(DummyPostData(post_data))
        self.assertTrue(form.validate())
        date = form.data['a']
        assert date.tzinfo
        self.assertEquals(
            timezone._get_timezone_name(date.tzinfo),
            timezone._get_timezone_name(timezone.get_current_timezone()))

    @override_settings(USE_TZ=True, TIME_ZONE='America/Los_Angeles')
    def test_stored_value_converted_to_current_timezone(self):
        utc_date = datetime.datetime(2013, 9, 25, 2, 15, tzinfo=timezone.utc)
        form = self.F(a=utc_date)
        self.assertTrue('2013-09-24 19:15:00' in form.a())


if __name__ == '__main__':
    import unittest
    unittest.main()
