import os
import warnings
from datetime import datetime

import pytest

from tests.common import DummyPostData
from wtforms.fields import DateField
from wtforms.fields import DateTimeField
from wtforms.fields import DateTimeLocalField
from wtforms.form import Form


def make_form(name="F", **fields):
    return type(str(name), (Form,), fields)


class F(Form):
    a = DateTimeField()
    b = DateTimeField(format="%Y-%m-%d %H:%M")
    c = DateTimeField(
        format="%#m/%#d/%Y %#I:%M" if os.name == "nt" else "%-m/%-d/%Y %-I:%M"
    )


def make_datetime_form(*args, **kwargs):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return F(*args, **kwargs)


def test_basic():
    d = datetime(2008, 5, 5, 4, 30, 0, 0)
    # Basic test with both inputs
    form = make_datetime_form(DummyPostData(a=["2008-05-05", "04:30:00"]))
    assert form.a.data == d
    assert (
        form.a()
        == """<input id="a" name="a" type="datetime" value="2008-05-05 04:30:00">"""
    )

    form = make_datetime_form(DummyPostData(b=["2008-05-05 04:30"]))
    assert form.b.data == d
    assert (
        form.b()
        == """<input id="b" name="b" type="datetime" value="2008-05-05 04:30">"""
    )

    form = make_datetime_form(DummyPostData(c=["5/5/2008 4:30"]))
    assert form.c.data == d
    assert (
        form.c() == """<input id="c" name="c" type="datetime" value="5/5/2008 4:30">"""
    )
    assert form.validate()

    # Test with a missing input
    form = make_datetime_form(DummyPostData(a=["2008-05-05"]))
    assert not form.validate()
    assert form.a.errors[0] == "Not a valid datetime value."

    form = make_datetime_form(a=d, b=d, c=d)
    assert form.validate()
    assert form.a._value() == "2008-05-05 04:30:00"
    assert form.b._value() == "2008-05-05 04:30"
    assert form.c._value() == "5/5/2008 4:30"


def test_microseconds():
    d = datetime(2011, 5, 7, 3, 23, 14, 424200)
    F = make_form(a=DateTimeField(format="%Y-%m-%d %H:%M:%S.%f"))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        form = F(DummyPostData(a=["2011-05-07 03:23:14.4242"]))
    assert d == form.a.data


def test_multiple_formats():
    d = datetime(2020, 3, 4, 5, 6)
    F = make_form(a=DateTimeField(format=["%Y-%m-%d %H:%M", "%Y%m%d%H%M"]))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        form = F(DummyPostData(a=["2020-03-04 05:06"]))
    assert d == form.a.data

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        form = F(DummyPostData(a=["202003040506"]))
    assert d == form.a.data


def test_datetimefield_warns():
    F = make_form(a=DateTimeField())

    with pytest.warns(
        DeprecationWarning,
        match=r"DateTimeField.*DateTimeLocalField.*WTForms 3\.4",
    ):
        F()


def test_datetimefield_subclasses_do_not_warn():
    F = make_form(a=DateField(), b=DateTimeLocalField())

    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        F()
