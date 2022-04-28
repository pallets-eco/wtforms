from contextlib import contextmanager

import pytest

from wtforms.validators import StopValidation
from wtforms.validators import ValidationError


@pytest.fixture
def dummy_form():
    return DummyForm()


@pytest.fixture
def dummy_field():
    return DummyField()


@pytest.fixture
def dummy_field_class():
    return DummyField


@pytest.fixture
def basic_widget_dummy_field(dummy_field_class):
    return dummy_field_class("foo", name="bar", label="label", id="id")


@pytest.fixture
def select_dummy_field(dummy_field_class):
    return dummy_field_class([("foo", "lfoo", True, {}), ("bar", "lbar", False, {})])


@pytest.fixture
def html5_dummy_field(dummy_field_class):
    return dummy_field_class("42", name="bar", id="id")


@pytest.fixture
def really_lazy_proxy():
    return ReallyLazyProxy()


@pytest.fixture
def grab_error_message():
    def grab_error_message(callable, form, field):
        try:
            callable(form, field)
        except ValidationError as e:
            return e.args[0]

    return grab_error_message


@pytest.fixture
def grab_stop_message():
    def grab_stop_message(callable, form, field):
        try:
            callable(form, field)
        except StopValidation as e:
            return e.args[0]

    return grab_stop_message


class DummyTranslations:
    def gettext(self, string):
        return string

    def ngettext(self, singular, plural, n):
        if n == 1:
            return singular

        return plural


class DummyField:
    _translations = DummyTranslations()

    def __init__(
        self,
        data=None,
        name=None,
        errors=(),
        raw_data=None,
        label=None,
        id=None,
        field_type="StringField",
    ):
        self.data = data
        self.name = name
        self.errors = list(errors)
        self.raw_data = raw_data
        self.label = label
        self.id = id if id else ""
        self.type = field_type

    def __call__(self, **other):
        return self.data

    def __str__(self):
        return self.data

    def __iter__(self):
        return iter(self.data)

    def _value(self):
        return self.data

    def iter_choices(self):
        return iter(self.data)

    def iter_groups(self):
        return []

    def has_groups(self):
        return False

    def gettext(self, string):
        return self._translations.gettext(string)

    def ngettext(self, singular, plural, n):
        return self._translations.ngettext(singular, plural, n)


class DummyForm(dict):
    pass


class ReallyLazyProxy:
    def __str__(self):
        raise Exception(
            "Translator function called during form declaration: it"
            " should be called at response time."
        )


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
                "Exception raised: %r but text %r did not match pattern %r"
                % (e, e.args[0], text)
            ) from e
    else:
        raise AssertionError(f"Expected Exception {e_type!r}, did not get it")
