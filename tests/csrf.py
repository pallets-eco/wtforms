from __future__ import unicode_literals

from unittest import TestCase

from wtforms.fields import TextField
from wtforms.form import Form
from wtforms.ext.csrf import SecureForm
from wtforms.csrf.core import CSRF

import datetime
import hashlib
import hmac


class DummyPostData(dict):
    def getlist(self, key):
        v = self[key]
        if not isinstance(v, (list, tuple)):
            v = [v]
        return v


class InsecureForm(SecureForm):
    def generate_csrf_token(self, csrf_context):
        return csrf_context

    a = TextField()


class DummyCSRF(CSRF):
    def generate_csrf_token(self):
        return 'dummytoken'


class FakeSessionRequest(object):
    def __init__(self, session):
        self.session = session


class StupidObject(object):
    a = None
    csrf_token = None


class CSRFTest(TestCase):
    class F(Form):
        class Meta:
            csrf = True
            csrf_class = DummyCSRF

    def test_base_class(self):
        self.assertRaises(NotImplementedError, self.F, meta={'csrf_class': CSRF})

    def test_basic_impl(self):
        form = self.F()
        assert 'csrf_token' in form
        assert not form.validate()
        form = self.F(DummyPostData(csrf_token='dummytoken'))
        assert form.validate()

    def test_csrf_off(self):
        form = self.F(meta={'csrf': False})
        assert 'csrf_token' not in form

    def test_rename(self):
        form = self.F(meta={'csrf_field_name': 'mycsrf'})
        assert 'mycsrf' in form
        assert 'csrf_token' not in form

    # TODO: Do some real testing of CSRF working and not working.
