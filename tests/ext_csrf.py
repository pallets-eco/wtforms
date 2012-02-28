from unittest import TestCase

from wtforms.fields import TextField
from wtforms.ext.csrf import SecureForm
from wtforms.ext.csrf.session import SessionSecureForm

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


class SecureFormTest(TestCase):
    def test_base_class(self):
        self.assertRaises(NotImplementedError, SecureForm)

    def test_basic_impl(self):
        form = InsecureForm(csrf_context=42)
        self.assertEqual(form.csrf_token.current_token, 42)
        self.assert_(not form.validate())
        self.assertEqual(len(form.csrf_token.errors), 1)
        self.assertEqual(form.csrf_token._value(), 42)
        # Make sure csrf_token is taken out from .data
        self.assertEqual(form.data, {'a': None})

    def test_with_data(self):
        post_data = DummyPostData(csrf_token=u'test', a=u'hi')
        form = InsecureForm(post_data, csrf_context=u'test')
        self.assert_(form.validate())
        self.assertEqual(form.data, {'a': u'hi'})

        form = InsecureForm(post_data, csrf_context=u'something')
        self.assert_(not form.validate())

        # Make sure that value is still the current token despite
        # the posting of a different value
        self.assertEqual(form.csrf_token._value(), u'something')

        # Make sure populate_obj doesn't overwrite the token
        obj = StupidObject()
        form.populate_obj(obj)
        self.assertEqual(obj.a, u'hi')
        self.assertEqual(obj.csrf_token, None)

    def test_with_missing_token(self):
        post_data = DummyPostData(a='hi')
        form = InsecureForm(post_data, csrf_context=u'test')
        self.assert_(not form.validate())

        self.assertEqual(form.csrf_token.data, u'')
        self.assertEqual(form.csrf_token._value(), u'test')



class SessionSecureFormTest(TestCase):
    class SSF(SessionSecureForm):
        SECRET_KEY = 'abcdefghijklmnop'.encode('ascii')

    class BadTimeSSF(SessionSecureForm):
        SECRET_KEY = 'abcdefghijklmnop'.encode('ascii')
        TIME_LIMIT = datetime.timedelta(-1, 86300)

    class NoTimeSSF(SessionSecureForm):
        SECRET_KEY = 'abcdefghijklmnop'.encode('ascii')
        TIME_LIMIT = None

    def test_basic(self):
        self.assertRaises(Exception, SessionSecureForm)
        self.assertRaises(TypeError, self.SSF)
        session = {}
        form = self.SSF(csrf_context=FakeSessionRequest(session))
        assert 'csrf' in session

    def test_timestamped(self):
        session = {}
        postdata = DummyPostData(csrf_token=u'fake##fake')
        form = self.SSF(postdata, csrf_context=session)
        assert 'csrf' in session
        assert form.csrf_token._value()
        assert form.csrf_token._value() != session['csrf']
        assert not form.validate()
        self.assertEqual(form.csrf_token.errors[0], u'CSRF failed')
        good_token = form.csrf_token._value()

        # Now test a valid CSRF with invalid timestamp
        evil_form = self.BadTimeSSF(csrf_context=session)
        bad_token = evil_form.csrf_token._value()
        
        postdata = DummyPostData(csrf_token=bad_token)
        form = self.SSF(postdata, csrf_context=session)
        assert not form.validate()
        self.assertEqual(form.csrf_token.errors[0], u'CSRF token expired')


    def test_notime(self):
        session = {}
        form = self.NoTimeSSF(csrf_context=session)
        hmacced = hmac.new(form.SECRET_KEY, session['csrf'].encode('utf8'), digestmod=hashlib.sha1)
        self.assertEqual(form.csrf_token._value(), '##%s' % hmacced.hexdigest())
        assert not form.validate()
        self.assertEqual(form.csrf_token.errors[0], u'CSRF token missing') 

        # Test with pre-made values
        session = {'csrf': u'00e9fa5fe507251ac5f32b1608e9282f75156a05'}
        postdata = DummyPostData(csrf_token=u'##d21f54b7dd2041fab5f8d644d4d3690c77beeb14')

        form = self.NoTimeSSF(postdata, csrf_context=session)
        assert form.validate()
