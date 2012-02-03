#!/usr/bin/env python
"""
Unittests for wtforms.ext.appengine

To run the tests, use NoseGAE:

easy_install nose
easy_install nosegae

nosetests --with-gae --without-sandbox
"""
import sys, os
WTFORMS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, WTFORMS_DIR)

from unittest import TestCase

from google.appengine.ext import db

from wtforms import Form, fields as f, validators
from wtforms.ext.appengine.db import model_form
from wtforms.ext.appengine.fields import GeoPtPropertyField


class DummyPostData(dict):
    def getlist(self, key):
        v = self[key]
        if not isinstance(v, (list, tuple)):
            v = [v]
        return v


class Author(db.Model):
    name = db.StringProperty(required=True)
    city = db.StringProperty()
    age = db.IntegerProperty(required=True)
    is_admin = db.BooleanProperty(default=False)


class Book(db.Model):
    author = db.ReferenceProperty(Author)


class AllPropertiesModel(db.Model):
    """Property names are ugly, yes."""
    prop_string = db.StringProperty()
    prop_byte_string = db.ByteStringProperty()
    prop_boolean = db.BooleanProperty()
    prop_integer = db.IntegerProperty()
    prop_float = db.FloatProperty()
    prop_date_time = db.DateTimeProperty()
    prop_date = db.DateProperty()
    prop_time = db.TimeProperty()
    prop_list = db.ListProperty(int)
    prop_string_list = db.StringListProperty()
    prop_reference = db.ReferenceProperty()
    prop_self_refeference = db.SelfReferenceProperty()
    prop_user = db.UserProperty()
    prop_blob = db.BlobProperty()
    prop_text = db.TextProperty()
    prop_category = db.CategoryProperty()
    prop_link = db.LinkProperty()
    prop_email = db.EmailProperty()
    prop_geo_pt = db.GeoPtProperty()
    prop_im = db.IMProperty()
    prop_phone_number = db.PhoneNumberProperty()
    prop_postal_address = db.PostalAddressProperty()
    prop_rating = db.RatingProperty()


class DateTimeModel(db.Model):
    prop_date_time_1 = db.DateTimeProperty()
    prop_date_time_2 = db.DateTimeProperty(auto_now=True)
    prop_date_time_3 = db.DateTimeProperty(auto_now_add=True)

    prop_date_1 = db.DateProperty()
    prop_date_2 = db.DateProperty(auto_now=True)
    prop_date_3 = db.DateProperty(auto_now_add=True)

    prop_time_1 = db.TimeProperty()
    prop_time_2 = db.TimeProperty(auto_now=True)
    prop_time_3 = db.TimeProperty(auto_now_add=True)


class TestModelForm(TestCase):
    def tearDown(self):
        for entity in Author.all():
            db.delete(entity)

        for entity in Book.all():
            db.delete(entity)

    def test_model_form_basic(self):
        form_class = model_form(Author)

        self.assertEqual(hasattr(form_class, 'name'), True)
        self.assertEqual(hasattr(form_class, 'age'), True)
        self.assertEqual(hasattr(form_class, 'city'), True)
        self.assertEqual(hasattr(form_class, 'is_admin'), True)

        form = form_class()
        self.assertEqual(isinstance(form.name, f.TextField), True)
        self.assertEqual(isinstance(form.city, f.TextField), True)
        self.assertEqual(isinstance(form.age, f.IntegerField), True)
        self.assertEqual(isinstance(form.is_admin, f.BooleanField), True)

    def test_required_field(self):
        form_class = model_form(Author)

        form = form_class()
        self.assertEqual(form.name.flags.required, True)
        self.assertEqual(form.city.flags.required, False)
        self.assertEqual(form.age.flags.required, True)
        self.assertEqual(form.is_admin.flags.required, False)

    def test_default_value(self):
        form_class = model_form(Author)

        form = form_class()
        self.assertEqual(form.name.default, None)
        self.assertEqual(form.city.default, None)
        self.assertEqual(form.age.default, None)
        self.assertEqual(form.is_admin.default, False)

    def test_model_form_only(self):
        form_class = model_form(Author, only=['name', 'age'])

        self.assertEqual(hasattr(form_class, 'name'), True)
        self.assertEqual(hasattr(form_class, 'city'), False)
        self.assertEqual(hasattr(form_class, 'age'), True)
        self.assertEqual(hasattr(form_class, 'is_admin'), False)

        form = form_class()
        self.assertEqual(isinstance(form.name, f.TextField), True)
        self.assertEqual(isinstance(form.age, f.IntegerField), True)

    def test_model_form_exclude(self):
        form_class = model_form(Author, exclude=['is_admin'])

        self.assertEqual(hasattr(form_class, 'name'), True)
        self.assertEqual(hasattr(form_class, 'city'), True)
        self.assertEqual(hasattr(form_class, 'age'), True)
        self.assertEqual(hasattr(form_class, 'is_admin'), False)

        form = form_class()
        self.assertEqual(isinstance(form.name, f.TextField), True)
        self.assertEqual(isinstance(form.city, f.TextField), True)
        self.assertEqual(isinstance(form.age, f.IntegerField), True)

    def test_datetime_model(self):
        """Fields marked as auto_add / auto_add_now should not be included."""
        form_class = model_form(DateTimeModel)

        self.assertEqual(hasattr(form_class, 'prop_date_time_1'), True)
        self.assertEqual(hasattr(form_class, 'prop_date_time_2'), False)
        self.assertEqual(hasattr(form_class, 'prop_date_time_3'), False)

        self.assertEqual(hasattr(form_class, 'prop_date_1'), True)
        self.assertEqual(hasattr(form_class, 'prop_date_2'), False)
        self.assertEqual(hasattr(form_class, 'prop_date_3'), False)

        self.assertEqual(hasattr(form_class, 'prop_time_1'), True)
        self.assertEqual(hasattr(form_class, 'prop_time_2'), False)
        self.assertEqual(hasattr(form_class, 'prop_time_3'), False)

    def test_not_implemented_properties(self):
        # This should not raise NotImplementedError.
        form_class = model_form(AllPropertiesModel)

        # These should be set.
        self.assertEqual(hasattr(form_class, 'prop_string'), True)
        self.assertEqual(hasattr(form_class, 'prop_byte_string'), True)
        self.assertEqual(hasattr(form_class, 'prop_boolean'), True)
        self.assertEqual(hasattr(form_class, 'prop_integer'), True)
        self.assertEqual(hasattr(form_class, 'prop_float'), True)
        self.assertEqual(hasattr(form_class, 'prop_date_time'), True)
        self.assertEqual(hasattr(form_class, 'prop_date'), True)
        self.assertEqual(hasattr(form_class, 'prop_time'), True)
        self.assertEqual(hasattr(form_class, 'prop_string_list'), True)
        self.assertEqual(hasattr(form_class, 'prop_reference'), True)
        self.assertEqual(hasattr(form_class, 'prop_self_refeference'), True)
        self.assertEqual(hasattr(form_class, 'prop_blob'), True)
        self.assertEqual(hasattr(form_class, 'prop_text'), True)
        self.assertEqual(hasattr(form_class, 'prop_category'), True)
        self.assertEqual(hasattr(form_class, 'prop_link'), True)
        self.assertEqual(hasattr(form_class, 'prop_email'), True)
        self.assertEqual(hasattr(form_class, 'prop_geo_pt'), True)
        self.assertEqual(hasattr(form_class, 'prop_phone_number'), True)
        self.assertEqual(hasattr(form_class, 'prop_postal_address'), True)
        self.assertEqual(hasattr(form_class, 'prop_rating'), True)

        # These should NOT be set.
        self.assertEqual(hasattr(form_class, 'prop_list'), False)
        self.assertEqual(hasattr(form_class, 'prop_user'), False)
        self.assertEqual(hasattr(form_class, 'prop_im'), False)

    def test_populate_form(self):
        entity = Author(key_name='test', name='John', city='Yukon', age=25, is_admin=True)
        entity.put()

        obj = Author.get_by_key_name('test')
        form_class = model_form(Author)

        form = form_class(obj=obj)
        self.assertEqual(form.name.data, 'John')
        self.assertEqual(form.city.data, 'Yukon')
        self.assertEqual(form.age.data, 25)
        self.assertEqual(form.is_admin.data, True)

    def test_field_attributes(self):
        form_class = model_form(Author, field_args={
            'name': {
                'label': 'Full name',
                'description': 'Your name',
            },
            'age': {
                'label': 'Age',
                'validators': [validators.NumberRange(min=14, max=99)],
            },
            'city': {
                'label': 'City',
                'description': 'The city in which you live, not the one in which you were born.',
            },
            'is_admin': {
                'label': 'Administrative rights',
            },
        })
        form = form_class()

        self.assertEqual(form.name.label.text, 'Full name')
        self.assertEqual(form.name.description, 'Your name')

        self.assertEqual(form.age.label.text, 'Age')

        self.assertEqual(form.city.label.text, 'City')
        self.assertEqual(form.city.description, 'The city in which you live, not the one in which you were born.')

        self.assertEqual(form.is_admin.label.text, 'Administrative rights')

    def test_reference_property(self):
        keys = ['__None']
        for name in ['foo', 'bar', 'baz']:
            author = Author(name=name, age=26)
            author.put()
            keys.append(str(author.key()))

        form_class = model_form(Book)
        form = form_class()

        choices = []
        i = 0
        for key, name, value in form.author.iter_choices():
            self.assertEqual(key, keys[i])
            i += 1


class TestFields(TestCase):
    class GeoTestForm(Form):
        geo = GeoPtPropertyField()

    def test_geopt_property(self):
        form = self.GeoTestForm(DummyPostData(geo='5.0, -7.0'))
        self.assert_(form.validate())
        self.assertEquals(form.geo.data, u'5.0,-7.0')
        form = self.GeoTestForm(DummyPostData(geo='5.0,-f'))
        self.assert_(not form.validate())
