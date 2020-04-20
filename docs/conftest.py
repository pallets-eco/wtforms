import pytest
import wtforms


@pytest.fixture(autouse=True)
def add_doctest_namespace(doctest_namespace):
    doctest_namespace["wtforms"] = wtforms
