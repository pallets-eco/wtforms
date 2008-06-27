"""
    wtforms.validators
    ~~~~~~~~~~~~~~~~~~
    
    TODO
    
    :copyright: 2007-2008 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
import re

class ValidationError(ValueError):
    pass

def email(message=u'Invalid email address.'):
    def _email(form, field):
        if not re.match(r'^.+@[^.].+\.[a-z]{2,4}$', field.data, re.IGNORECASE):
            raise ValidationError(message)
    return _email

def ip_address(message=u'Invalid IP address.'):
    def _ip_address(form, field):
        if not re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', field.data):
            raise ValidationError(message)
    return _ip_address

def is_checked(message=u'Field must tbe checked.'):
    def _is_checked(form, field):
        if not field.data:
            raise ValidationError(message)
    return _is_checked

def length(message=u'Field must be between %(min)i and %(max)i characters long.', min=-1, max=-1):
    fmt_args = {'min': min, 'max': max}
    def _length(form, field):
        l = field.data and len(field.data) or 0
        if l < min or max != -1 and l > max:
            raise ValidationError(message % fmt_args)
    return _length

def not_empty(message=u'Field must not be empty.'):
    def _not_empty(form, field):
        if not field.data or not field.data.strip():
            raise ValidationError(message)
    return _not_empty

def url(message=u'Invalid URL.', allow_blank=False):
    def _url(form, field):
        if allow_blank and not field.data:
            return
        if not re.match(r'[a-z]+://.*\.[a-z]{2,4}(\/.*)?', field.data, re.I):
            raise ValidationError(message)
    return _url

__all__ = ('ValidationError', 'email', 'ip_address', 'is_checked', 'length', 'not_empty', 'url')
