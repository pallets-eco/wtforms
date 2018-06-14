import pytest
from contextlib import contextmanager
from wtforms.validators import ValidationError, StopValidation


@pytest.fixture
def dummy_form():
    return DummyForm()


@pytest.fixture
def dummy_field():
    return DummyField()


@pytest.fixture
def really_lazy_proxy():
    return ReallyLazyProxy()


class DummyTranslations(object):

    def gettext(self, string):
        return string

    def ngettext(self, singular, plural, n):
        if n == 1:
            return singular

        return plural


class DummyField(object):
    _translations = DummyTranslations()

    def __init__(self, data=None, errors=(), raw_data=None):
        self.data = data
        self.errors = list(errors)
        self.raw_data = raw_data

    def gettext(self, string):
        return self._translations.gettext(string)

    def ngettext(self, singular, plural, n):
        return self._translations.ngettext(singular, plural, n)


class DummyForm(dict):
    pass


class ReallyLazyProxy(object):

    def __unicode__(self):
        raise Exception(
            'Translator function called during form declaration: it should be called at response time.')

    __str__ = __unicode__


def grab_error_message(callable, form, field):
    try:
        callable(form, field)
    except ValidationError as e:
        return e.args[0]


def grab_stop_message(callable, form, field):
    try:
        callable(form, field)
    except StopValidation as e:
        return e.args[0]


def contains_validator(field, v_type):
    for v in field.validators:
        if isinstance(v, v_type):
            return True
    return False


class DummyPostData(dict):

    def getlist(self, key):
        v = self[key]
        if not isinstance(v, (list, tuple)):
            v = [v]
        return v


@contextmanager
def assert_raises_text(e_type, text):
    import re
    try:
        yield
    except e_type as e:
        if not re.match(text, e.args[0]):
            raise AssertionError(
                'Exception raised: %r but text %r did not match pattern %r' % (e, e.args[0], text))
    else:
        raise AssertionError(
            'Expected Exception %r, did not get it' % (e_type,))
