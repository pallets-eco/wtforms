"""
    test_validators
    ~~~~~~~~~~~~~~~
    
    Unittests for bundled validators.
    
    :copyright: 2007-2008 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""

from py.test import raises
from wtforms.validators import StopValidation, ValidationError, email, equal_to, ip_address, is_checked, length, required, optional, regexp, url

class DummyForm(object):
    pass

class DummyField(object):
    def __init__(self, data):
        self.data = data

form = DummyForm()

def test_email():
    assert email()(form, DummyField('foo@bar.dk')) == None
    assert email()(form, DummyField('123@bar.dk')) == None
    assert email()(form, DummyField('foo@456.dk')) == None
    assert email()(form, DummyField('foo@bar456.info')) == None
    raises(ValidationError, email(), form, DummyField(None))
    raises(ValidationError, email(), form, DummyField(''))
    raises(ValidationError, email(), form, DummyField('foo'))
    raises(ValidationError, email(), form, DummyField('bar.dk'))
    raises(ValidationError, email(), form, DummyField('foo@'))
    raises(ValidationError, email(), form, DummyField('@bar.dk'))
    raises(ValidationError, email(), form, DummyField('foo@bar'))
    raises(ValidationError, email(), form, DummyField('foo@bar.ab12'))
    raises(ValidationError, email(), form, DummyField('foo@bar.abcde'))

def test_equal_to():
    form = DummyForm()
    form.foo = DummyField('test')
    assert equal_to('foo')(form, form.foo) == None
    raises(ValidationError, equal_to('invalid_field_name'), form, DummyField('test'))
    raises(ValidationError, equal_to('foo'), form, DummyField('different_value'))

def test_ip_address():
    assert ip_address()(form, DummyField('127.0.0.1')) == None
    raises(ValidationError, ip_address(), form, DummyField('abc.0.0.1'))
    raises(ValidationError, ip_address(), form, DummyField('1278.0.0.1'))
    raises(ValidationError, ip_address(), form, DummyField('127.0.0.abc'))

def test_is_checked():
    assert is_checked()(form, DummyField('foobar')) == None
    raises(ValidationError, is_checked(), form, DummyField(''))

def test_length():
    field = DummyField('foobar')
    assert length(min=2, max=6)(form, field) == None
    raises(ValidationError, length(min=7), form, field)
    raises(ValidationError, length(max=5), form, field)
    
def test_required():
    assert required()(form, DummyField('foobar')) == None
    raises(StopValidation, required(), form, DummyField(''))
    raises(StopValidation, required(), form, DummyField(' '))

def test_optional():
    assert optional(form, DummyField('foobar')) == None
    assert optional()(form, DummyField('foobar')) == None
    raises(StopValidation, optional(), form, DummyField(''))
    raises(StopValidation, optional(), form, DummyField(' '))

def test_regexp():
    import re
    # String regexp
    assert regexp('^a')(form, DummyField('abcd')) == None
    assert regexp('^a', re.I)(form, DummyField('ABcd')) == None
    raises(ValidationError, regexp('^a'), form, DummyField('foo'))
    raises(ValidationError, regexp('^a'), form, DummyField(None))
    # Compiled regexp
    assert regexp(re.compile('^a'))(form, DummyField('abcd')) == None
    assert regexp(re.compile('^a', re.I))(form, DummyField('ABcd')) == None
    raises(ValidationError, regexp(re.compile('^a')), form, DummyField('foo'))
    raises(ValidationError, regexp(re.compile('^a')), form, DummyField(None))

def test_url():
    assert url()(form, DummyField('http://foobar.dk')) == None
    assert url()(form, DummyField('http://foobar.dk/')) == None
    assert url()(form, DummyField('http://foobar.dk/foobar')) == None
    assert url()(form, DummyField('http://127.0.0.1/foobar')) == None
    assert url()(form, DummyField('http://127.0.0.1:9000/fake')) == None
    assert url(require_tld=False)(form, DummyField('http://localhost/foobar')) == None
    assert url(require_tld=False)(form, DummyField('http://foobar')) == None
    raises(ValidationError, url(), form, DummyField('http://foobar'))
    raises(ValidationError, url(), form, DummyField('foobar.dk'))
    raises(ValidationError, url(), form, DummyField('http://127.0.0/asdf'))
    raises(ValidationError, url(), form, DummyField('http://foobar.12'))
    raises(ValidationError, url(), form, DummyField('http://localhost:abc/a'))
