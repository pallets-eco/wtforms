import pytest

from wtforms.i18n import DummyTranslations


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
