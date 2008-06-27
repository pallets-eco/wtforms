"""
    test_validators
    ~~~~~~~~~~~~~~
    
    Unittests for bundled validators.
    
    :copyright: 2007-2008 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""

from py.test import raises
from wtforms.validators import ValidationError, length, url, not_empty, email, ip_address

class DummyForm(object):
    pass

class DummyField(object):
    def __init__(self, data):
        self.data = data

form = DummyForm()

def test_email():
    assert email(form, DummyField('foo@bar.dk')) == None
    assert email(form, DummyField('123@bar.dk')) == None
    assert email(form, DummyField('foo@456.dk')) == None
    assert email(form, DummyField('foo@bar456.info')) == None
    raises(ValidationError, email, form, DummyField('foo'))
    raises(ValidationError, email, form, DummyField('bar.dk'))
    raises(ValidationError, email, form, DummyField('foo@'))
    raises(ValidationError, email, form, DummyField('@bar.dk'))
    raises(ValidationError, email, form, DummyField('foo@bar'))
    raises(ValidationError, email, form, DummyField('foo@bar.ab12'))
    raises(ValidationError, email, form, DummyField('foo@bar.abcde'))

def test_length():
    field = DummyField('foobar')
    assert length(min=2, max=6)(form, field) == None
    raises(ValidationError, length(min=7), form, field)
    raises(ValidationError, length(max=5), form, field)
    
def test_url():
    assert url()(form, DummyField('http://foobar.dk')) == None
    assert url()(form, DummyField('http://foobar.dk/')) == None
    assert url()(form, DummyField('http://foobar.dk/foobar')) == None
    raises(ValidationError, url(), form, DummyField('http://foobar'))
    raises(ValidationError, url(), form, DummyField('foobar.dk'))
    raises(ValidationError, url(), form, DummyField('http://foobar.12'))

def test_not_empty():
    assert not_empty()(form, DummyField('foobar')) == None
    raises(ValidationError, not_empty(), form, DummyField(''))
    raises(ValidationError, not_empty(), form, DummyField(' '))

def test_ip_address():
    assert ip_address(form, DummyField('127.0.0.1')) == None
    raises(ValidationError, ip_address, form, DummyField('abc.0.0.1'))
    raises(ValidationError, ip_address, form, DummyField('1278.0.0.1'))
    raises(ValidationError, ip_address, form, DummyField('127.0.0.abc'))
 
