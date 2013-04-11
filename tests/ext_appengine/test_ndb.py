from __future__ import unicode_literals

# This needs to stay as the first import, it sets up paths.
from gaetest_common import DummyPostData, fill_authors

from google.appengine.ext import ndb
from unittest import TestCase
from wtforms import Form, TextField, IntegerField, BooleanField
from wtforms.compat import text_type
from wtforms.ext.appengine.fields import KeyPropertyField
from wtforms.ext.appengine.ndb import model_form


class Author(ndb.Model):
    name = ndb.StringProperty(required=True)
    city = ndb.StringProperty()
    age = ndb.IntegerProperty(required=True)
    is_admin = ndb.BooleanProperty(default=False)


class Book(ndb.Model):
    author = ndb.KeyProperty(Author)


class TestKeyPropertyField(TestCase):
    class F(Form):
        author = KeyPropertyField(reference_class=Author)

    def setUp(self):
        self.authors = fill_authors(Author)
        self.first_author_id = self.authors[0].key.id()

    def tearDown(self):
        for author in Author.query():
            author.key.delete()

    def test_no_data(self):
        form = self.F()
        form.author.query = Author.query().order(Author.name)

        assert not form.validate()
        ichoices = list(form.author.iter_choices())
        self.assertEqual(len(ichoices), len(self.authors))
        for author, (key, label, selected) in zip(self.authors, ichoices):
            self.assertEqual(key, text_type(author.key.id()))

    def test_form_data(self):
        # Valid data
        form = self.F(DummyPostData(author=text_type(self.first_author_id)))
        form.author.query = Author.query().order(Author.name)
        assert form.validate()
        ichoices = list(form.author.iter_choices())
        self.assertEqual(len(ichoices), len(self.authors))
        self.assertEqual(list(x[2] for x in ichoices), [True, False, False])

        # Bogus Data
        form = self.F(DummyPostData(author='fooflaf'))
        assert not form.validate()
        print list(form.author.iter_choices())
        assert all(x[2] is False for x in form.author.iter_choices())


class TestModelForm(TestCase):
    EXPECTED_AUTHOR = [('name', TextField), ('city', TextField), ('age', IntegerField), ('is_admin', BooleanField)]

    def test(self):
        form = model_form(Author)
        for (expected_name, expected_type), field in zip(self.EXPECTED_AUTHOR, form()):
            self.assertEqual(field.name, expected_name)
            self.assertEqual(type(field), expected_type)
