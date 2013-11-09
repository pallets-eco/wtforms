from __future__ import unicode_literals

from contextlib import contextmanager
from functools import partial
from unittest import TestCase

from wtforms.fields import TextField
from wtforms.form import Form
from wtforms.csrf.core import CSRF
from wtforms.csrf.session import SessionCSRF
from tests.common import DummyPostData

import datetime
import hashlib
import hmac


class DummyCSRF(CSRF):
    def generate_csrf_token(self, csrf_token_field):
        return 'dummytoken'


class FakeSessionRequest(object):
    def __init__(self, session):
        self.session = session


class TimePin(SessionCSRF):
    """
    CSRF with ability to pin times so that we can do a thorough test
    of expected values and keys.
    """
    pinned_time = None

    @classmethod
    @contextmanager
    def pin_time(cls, value):
        original = cls.pinned_time
        cls.pinned_time = value
        yield
        cls.pinned_time = original

    def now(self):
        return self.pinned_time


class SimplePopulateObject(object):
    a = None
    csrf_token = None


class DummyCSRFTest(TestCase):
    class F(Form):
        class Meta:
            csrf = True
            csrf_class = DummyCSRF
        a = TextField()

    def test_base_class(self):
        self.assertRaises(NotImplementedError, self.F, meta={'csrf_class': CSRF})

    def test_basic_impl(self):
        form = self.F()
        assert 'csrf_token' in form
        assert not form.validate()
        self.assertEqual(form.csrf_token._value(), 'dummytoken')
        form = self.F(DummyPostData(csrf_token='dummytoken'))
        assert form.validate()

    def test_csrf_off(self):
        form = self.F(meta={'csrf': False})
        assert 'csrf_token' not in form

    def test_rename(self):
        form = self.F(meta={'csrf_field_name': 'mycsrf'})
        assert 'mycsrf' in form
        assert 'csrf_token' not in form

    def test_no_populate(self):
        obj = SimplePopulateObject()
        form = self.F(a='test', csrf_token='dummytoken')
        form.populate_obj(obj)
        assert obj.csrf_token is None
        self.assertEqual(obj.a, 'test')


class SessionCSRFTest(TestCase):
    class F(Form):
        class Meta:
            csrf = True
            csrf_secret = b'foobar'

        a = TextField()

    class NoTimeLimit(F):
        class Meta:
            csrf_time_limit = None

    class Pinned(F):
        class Meta:
            csrf_class = TimePin

    def test_various_failures(self):
        self.assertRaises(TypeError, self.F)
        self.assertRaises(Exception, self.F, meta={'csrf_secret': None})

    def test_no_time_limit(self):
        session = {}
        form = self._test_phase1(self.NoTimeLimit, session)
        expected_csrf = hmac.new(b'foobar', session['csrf'].encode('ascii'), digestmod=hashlib.sha1).hexdigest()
        self.assertEqual(form.csrf_token.current_token, '##' + expected_csrf)
        self._test_phase2(self.NoTimeLimit, session, form.csrf_token.current_token)

    def test_with_time_limit(self):
        session = {}
        form = self._test_phase1(self.F, session)
        self._test_phase2(self.F, session, form.csrf_token.current_token)

    def test_detailed_expected_values(self):
        """
        A full test with the date and time pinned so we get deterministic output.
        """
        session = {'csrf': '93fed52fa69a2b2b0bf9c350c8aeeb408b6b6dfa'}
        dt = partial(datetime.datetime, 2013, 1, 15)
        with TimePin.pin_time(dt(8, 11, 12)):
            form = self._test_phase1(self.Pinned, session)
            token = form.csrf_token.current_token
            self.assertEqual(token, '20130115084112##53812764d65abb8fa88384551a751ca590dff5fb')

        # Make sure that CSRF validates in a normal case.
        with TimePin.pin_time(dt(8, 18)):
            form = self._test_phase2(self.Pinned, session, token)
            new_token = form.csrf_token.current_token
            self.assertNotEqual(new_token, token)
            self.assertEqual(new_token, '20130115084800##e399e3a6a84860762723672b694134507ba21b58')

        # Make sure that CSRF fails when we're past time
        with TimePin.pin_time(dt(8, 43)):
            form = self._test_phase2(self.Pinned, session, token, False)
            assert not form.validate()
            self.assertEqual(form.csrf_token.errors, ['CSRF token expired'])

            # We can succeed with a slightly newer token
            self._test_phase2(self.Pinned, session, new_token)

        with TimePin.pin_time(dt(8, 44)):
            bad_token = '20130115084800##e399e3a6a84860762723672b694134507ba21b59'
            form = self._test_phase2(self.Pinned, session, bad_token, False)
            assert not form.validate()

    def _test_phase1(self, form_class, session):
        form = form_class(meta={'csrf_context': session})
        assert not form.validate()
        assert form.csrf_token.errors
        assert 'csrf' in session
        return form

    def _test_phase2(self, form_class, session, token, must_validate=True):
        form = form_class(
            formdata=DummyPostData(csrf_token=token),
            meta={'csrf_context': session}
        )
        if must_validate:
            assert form.validate()
        return form
