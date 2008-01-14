"""
    wtforms.validators
    ~~~~~~~~~~~~~~~~~~
    
    TODO
    
    :copyright: 2007 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
import re

class ValidationError(ValueError):
    pass

def email(form, field):
    if not re.match(r'^.+@[^.].+\.[a-z]{2,4}$', field.data, re.IGNORECASE):  # XXX better email regex?
        raise ValidationError("Invalid email address.")

def length(message=None, min=-1, max=None):
    fmt_args = {'min': min, 'max': max}
    def _length(form, field):
        L = len(field.data) if field.data else 0
        if L < min:
            raise ValidationError((message if message else u'Must be at least %(min)i characters.') % fmt_args)
        elif max is not None and L > max:
            raise ValidationError((message if message else u'May not be longer than %(max)i characters.') % fmt_args)
    return _length

def url(allow_blank=False):
    def _url(form, field):
        if allow_blank and not field.data:
            return
        match = re.match(r'[a-z]+://.*', field.data, re.I)
        if not match:
            raise ValidationError("Is not a valid URL.")
    return _url

def not_empty(message=None):
    def _not_empty(form, field):
        if not field.data or not field.data.strip():
            raise ValidationError(message if message else u'Field must not be empty.')
    return _not_empty

__all__ = ('ValidationError', 'email', 'length', 'url', 'not_empty')
