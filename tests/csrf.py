from __future__ import unicode_literals

from unittest import TestCase

from wtforms.fields import TextField
from wtforms.form import Form
from wtforms.ext.csrf import SecureForm

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

    def test_basic_impl(self):
        form = self.F()
        assert 'csrf_token' in form
        form = self.F(meta={'csrf': False})
        assert 'csrf_token' not in form

    def test_rename(self):
        form = self.F(meta={'csrf_field_name': 'mycsrf'})
        assert 'mycsrf' in form
        assert 'csrf_token' not in form

    # TODO: Do some real testing of CSRF working and not working.
