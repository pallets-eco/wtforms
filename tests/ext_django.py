#!/usr/bin/env python
"""
    ext_django
    ~~~~~~~~~~
    
    Unittests for wtforms.ext.django
    
    :copyright: 2009 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""

##########################################################################
# -- Django Initialization
# 
# Unfortunately, we cannot do this in the setUp for a test case, as the
# settings.configure method cannot be called more than once, and we cannot
# control the order in which tests are run, so making a throwaway test won't
# work either.

import sys, types

from django.conf import settings
settings.configure(INSTALLED_APPS=['wtforms.ext.django'])

from django.db import models
from django.contrib.localflavor.us.models import USStateField

import wtforms.ext.django
wtforms.ext.django.models = sys.modules['wtforms.ext.django.models'] = types.ModuleType('wtforms.ext.django.models')

class Group(models.Model):
    __module__ = 'wtforms.ext.django.models'
    name = models.CharField(max_length=75)

class User(models.Model):
    __module__ = 'wtforms.ext.django.models'
    username = models.CharField(max_length=40)
    group    = models.ForeignKey(Group)
    birthday = models.DateField(help_text="Teh Birthday")
    email    = models.EmailField(blank=True)
    posts    = models.PositiveSmallIntegerField()
    state    = USStateField()
    reg_ip   = models.IPAddressField("IP Addy")
    url      = models.URLField()
    file     = models.FilePathField()
    file2    = models.FileField()
    bool     = models.BooleanField()
    time1    = models.TimeField()
    slug     = models.SlugField()


from wtforms.ext.django import models as test_models 
test_models.User = User
test_models.Group = Group

# -- End hacky Django initialization

from django.template import Context, Template
from unittest import TestCase
from wtforms import Form, fields, validators
from wtforms.ext.django.orm import model_form
from wtforms.ext.django.fields import QuerySetSelectField, ModelSelectField

def validator_names(field):
    return [x.func_name for x in field.validators]

class TemplateTagsTest(TestCase):
    TEST_TEMPLATE = """{% load wtforms %}
    {% autoescape off %}{{ form.a }}{% endautoescape %}
    {% form_field form.a %}
    {% for field in form %}{% form_field field class=someclass onclick="alert()" %}
    {% endfor %}
    """

    TEMPLATE_EXPECTED_OUTPUT = """
    <input id="a" name="a" type="text" value="" />
    <input id="a" name="a" type="text" value="" />
    <input class="CLASSVAL!" id="a" name="a" onclick="alert()" type="text" value="" />
    <select class="CLASSVAL!" id="b" name="b" onclick="alert()"><option value="a">hi</option><option value="b">bai</option></select>
    """
    class F(Form):
        a = fields.TextField()
        b = fields.SelectField(choices=[('a', 'hi'), ('b', 'bai')])

    def test_form_field(self):
        t = Template(self.TEST_TEMPLATE)
        output = t.render(Context({'form': self.F(), 'someclass': "CLASSVAL!"}))
        self.assertEqual(output.strip(), self.TEMPLATE_EXPECTED_OUTPUT.strip())

class ModelFormTest(TestCase):
    F = model_form(test_models.User)
    form = F()
    form_with_pk = model_form(test_models.User, include_pk=True)()

    def test_form_sanity(self):
        self.assertEqual(self.F.__name__, 'UserForm')
        self.assertEqual(len([x for x in self.form]), 13) 
        self.assertEqual(len([x for x in self.form_with_pk]), 14) 

    def test_label(self):
        self.assertEqual(self.form.reg_ip.label.text, 'IP Addy')
        self.assertEqual(self.form.posts.label.text, 'posts')

    def test_description(self):
        self.assertEqual(self.form.birthday.description, 'Teh Birthday')

    def test_max_length(self):
        self.assertTrue('_length' in validator_names(self.form.username))
        self.assertTrue('_length' not in validator_names(self.form.posts))

    def test_optional(self):
        self.assertTrue('_optional' in validator_names(self.form.email))

    def test_simple_fields(self):
        self.assertEqual(type(self.form.file), fields.FileField)
        self.assertEqual(type(self.form.file2), fields.FileField)
        self.assertEqual(type(self.form_with_pk.id), fields.IntegerField)
        self.assertEqual(type(self.form.slug), fields.TextField)

    def test_custom_converters(self):
        self.assertEqual(type(self.form.email), fields.TextField)
        self.assertTrue('_email' in validator_names(self.form.email))
        self.assertEqual(type(self.form.reg_ip), fields.TextField)
        self.assertTrue('_ip_address' in validator_names(self.form.reg_ip))

    def test_us_states(self):
        self.assertTrue(len(self.form.state.choices) >= 50)

class QuerySetSelectFieldTest(TestCase):
    def setUp(self):
        self.queryset = User.objects.all()
        class F(Form):
            a = QuerySetSelectField(allow_blank=True)
            b = QuerySetSelectField(queryset=self.queryset)

        self.F = F

    def test_queryset_freshness(self):
        form = self.F()
        self.assertTrue(form.b.queryset is not self.queryset)

class ModelSelectFieldTest(TestCase):
    class F(Form):
        a = ModelSelectField(model=User)

    def test_construction_worked(self):
        form = self.F()
        self.assertTrue(form.a.queryset is not None)

        
if __name__ == '__main__':
    import unittest
    unittest.main()
