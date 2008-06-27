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

def email(form, field):
    if not re.match(r'^.+@[^.].+\.[a-z]{2,4}$', field.data, re.IGNORECASE):  # XXX better email regex?
        raise ValidationError(u'Invalid email address.')

def length(message=None, min=-1, max=None):
    fmt_args = {'min': min, 'max': max}
    def _length(form, field):
        L = field.data and len(field.data) or 0
        if L < min:
            raise ValidationError((message or u'Must be at least %(min)i characters.') % fmt_args)
        elif max is not None and L > max:
            raise ValidationError((message or u'May not be longer than %(max)i characters.') % fmt_args)
    return _length

def url(allow_blank=False):
    def _url(form, field):
        if allow_blank and not field.data:
            return
        match = re.match(r'[a-z]+://.*\.[a-z]{2,4}(\/.*)?', field.data, re.I)
        if not match:
            raise ValidationError(u'Is not a valid URL.')
    return _url

def not_empty(message=None):
    def _not_empty(form, field):
        if not field.data or not field.data.strip():
            raise ValidationError(message or u'Field must not be empty.')
    return _not_empty

def ip_address(form, field):
    if not re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', field.data):
        raise ValidationError(u'Invalid ip address.')
    

__all__ = ('ValidationError', 'email', 'length', 'url', 'not_empty', 'ip_address')
