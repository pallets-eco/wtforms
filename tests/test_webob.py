import pytest

from wtforms.fields import Field
from wtforms.form import BaseForm
from wtforms.utils import unset_value
from wtforms.utils import WebobInputWrapper

try:
    from webob.multidict import MultiDict

    has_webob = True
except ImportError:
    has_webob = False


class MockMultiDict:
    def __init__(self, tuples):
        self.tuples = tuples

    def __len__(self):
        return len(self.tuples)

    def __iter__(self):
        for k, _ in self.tuples:
            yield k

    def __contains__(self, key):
        for k, _ in self.tuples:
            if k == key:
                return True
        return False

    def getall(self, key):
        result = []
        for k, v in self.tuples:
            if key == k:
                result.append(v)
        return result


class SneakyField(Field):
    def __init__(self, sneaky_callable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sneaky_callable = sneaky_callable

    def process(self, formdata, data=unset_value, **kwargs):
        self.sneaky_callable(formdata)


@pytest.fixture
def webob_class():
    return MultiDict if has_webob else MockMultiDict


@pytest.fixture
def test_values():
    return [("a", "Apple"), ("b", "Banana"), ("a", "Cherry")]


@pytest.fixture()
def empty_mdict(webob_class):
    return webob_class([])


@pytest.fixture()
def filled_mdict(webob_class, test_values):
    return webob_class(test_values)


def test_automatic_wrapping(filled_mdict):
    def _check(formdata):
        assert isinstance(formdata, WebobInputWrapper)

    form = BaseForm({"a": SneakyField(_check)})
    form.process(filled_mdict)


def test_empty(empty_mdict):
    formdata = WebobInputWrapper(empty_mdict)
    assert not formdata
    assert len(formdata) == 0
    assert list(formdata) == []
    assert formdata.getlist("fake") == []


def test_filled(filled_mdict):
    formdata = WebobInputWrapper(filled_mdict)
    assert formdata
    assert len(formdata) == 3
    assert list(formdata) == ["a", "b", "a"]
    assert "b" in formdata
    assert "fake" not in formdata
    assert formdata.getlist("a") == ["Apple", "Cherry"]
    assert formdata.getlist("b") == ["Banana"]
    assert formdata.getlist("fake") == []
