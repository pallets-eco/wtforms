import datetime
import hashlib
import hmac
from contextlib import contextmanager
from functools import partial

import pytest
from tests.common import DummyPostData

from wtforms.csrf.core import CSRF
from wtforms.csrf.session import SessionCSRF
from wtforms.fields import StringField
from wtforms.form import Form


class DummyCSRF(CSRF):
    def generate_csrf_token(self, csrf_token_field):
        return "dummytoken"


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


class SimplePopulateObject:
    a = None
    csrf_token = None


class F(Form):
    class Meta:
        csrf = True
        csrf_class = DummyCSRF

    a = StringField()


def test_dummy_csrf_base_class():
    with pytest.raises(NotImplementedError):
        F(meta={"csrf_class": CSRF})


def test_dummy_csrf_basic_impl():
    form = F()
    assert "csrf_token" in form
    assert not form.validate()
    assert form.csrf_token._value() == "dummytoken"
    form = F(DummyPostData(csrf_token="dummytoken"))
    assert form.validate()


def test_dummy_csrf_off():
    form = F(meta={"csrf": False})
    assert "csrf_token" not in form


def test_dummy_csrf_rename():
    form = F(meta={"csrf_field_name": "mycsrf"})
    assert "mycsrf" in form
    assert "csrf_token" not in form


def test_dummy_csrf_no_populate():
    obj = SimplePopulateObject()
    form = F(a="test", csrf_token="dummytoken")
    form.populate_obj(obj)
    assert obj.csrf_token is None
    assert obj.a == "test"


class H(Form):
    class Meta:
        csrf = True
        csrf_secret = b"foobar"

    a = StringField()


class NoTimeLimit(H):
    class Meta:
        csrf_time_limit = None


class Pinned(H):
    class Meta:
        csrf_class = TimePin


def test_session_csrf_various_failures():
    with pytest.raises(TypeError):
        H()
    with pytest.raises(
        Exception,
        match="must set `csrf_secret` on class Meta for SessionCSRF to work",
    ):
        H(meta={"csrf_secret": None})


def test_session_csrf_no_time_limit():
    session = {}
    form = _test_phase1(NoTimeLimit, session)
    expected_csrf = hmac.new(
        b"foobar", session["csrf"].encode("ascii"), digestmod=hashlib.sha1
    ).hexdigest()
    assert form.csrf_token.current_token == "##" + expected_csrf
    _test_phase2(NoTimeLimit, session, form.csrf_token.current_token)


def test_session_csrf_with_time_limit():
    session = {}
    form = _test_phase1(H, session)
    _test_phase2(H, session, form.csrf_token.current_token)


def test_session_csrf_detailed_expected_values():
    """
    A full test with the date and time pinned so we get deterministic output.
    """
    session = {"csrf": "93fed52fa69a2b2b0bf9c350c8aeeb408b6b6dfa"}
    dt = partial(datetime.datetime, 2013, 1, 15)
    with TimePin.pin_time(dt(8, 11, 12)):
        form = _test_phase1(Pinned, session)
        token = form.csrf_token.current_token
        assert token == "20130115084112##53812764d65abb8fa88384551a751ca590dff5fb"

    # Make sure that CSRF validates in a normal case.
    with TimePin.pin_time(dt(8, 18)):
        form = _test_phase2(Pinned, session, token)
        new_token = form.csrf_token.current_token
        assert new_token != token
        assert new_token == "20130115084800##e399e3a6a84860762723672b694134507ba21b58"

    # Make sure that CSRF fails when we're past time
    with TimePin.pin_time(dt(8, 43)):
        form = _test_phase2(Pinned, session, token, False)
        assert not form.validate()
        assert form.csrf_token.errors == ["CSRF token expired."]

        # We can succeed with a slightly newer token
        _test_phase2(Pinned, session, new_token)

    with TimePin.pin_time(dt(8, 44)):
        bad_token = "20130115084800##e399e3a6a84860762723672b694134507ba21b59"
        form = _test_phase2(Pinned, session, bad_token, False)
        assert not form.validate()


def _test_phase1(form_class, session):
    form = form_class(meta={"csrf_context": session})
    assert not form.validate()
    assert form.csrf_token.errors
    assert "csrf" in session
    return form


def _test_phase2(form_class, session, token, must_validate=True):
    form = form_class(
        formdata=DummyPostData(csrf_token=token), meta={"csrf_context": session}
    )
    if must_validate:
        assert form.validate()
    return form
