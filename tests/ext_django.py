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
    bool     = models.BooleanField()

from wtforms.ext.django import models as _models 
_models.User = User
_models.Group = Group


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

from django.template import Context, Template
from unittest import TestCase
from wtforms import Form, fields, validators
from wtforms.ext.django.orm import model_form

def validator_names(field):
    return [x.func_name for x in field.validators]

class TemplateTagsTest(TestCase):
    class F(Form):
        a = fields.TextField()
        b = fields.SelectField(choices=[('a', 'hi'), ('b', 'bai')])

    def test_form_field(self):
        t = Template(TEST_TEMPLATE)
        output = t.render(Context({'form': self.F(), 'someclass': "CLASSVAL!"}))
        self.assertEqual(output.strip(), TEMPLATE_EXPECTED_OUTPUT.strip())

class ModelFormTest(TestCase):
    F = model_form(_models.User)
    form = F()
    form_with_pk = model_form(_models.User, include_pk=True)()

    def test_form_sanity(self):
        self.assertEqual(self.F.__name__, 'UserForm')
        self.assertEqual(len([x for x in self.form]), 10) 
        self.assertEqual(len([x for x in self.form_with_pk]), 11) 

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
        self.assertEqual(type(self.form_with_pk.id), fields.IntegerField)

    def test_custom_converters(self):
        self.assertEqual(type(self.form.email), fields.TextField)
        self.assertTrue('_email' in validator_names(self.form.email))
        self.assertEqual(type(self.form.reg_ip), fields.TextField)
        self.assertTrue('_ip_address' in validator_names(self.form.reg_ip))
        
        
if __name__ == '__main__':
    import unittest
    unittest.main()
