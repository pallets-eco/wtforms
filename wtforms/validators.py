"""
    wtforms.validators
    ~~~~~~~~~~~~~~~~~~

    Contains all built-in validators such as `required` and `optional`.
    
    :copyright: 2009 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
import re

class ValidationError(ValueError):
    """
    Raised when a validator fails to validate its input.
    """
    def __init__(self, message=u'', *args, **kwargs):
        ValueError.__init__(self, message, *args, **kwargs)

class StopValidation(ValidationError):
    """
    Causes the validation chain to stop.

    If StopValidation is raised, no more validators in the validation chain are
    called. If raised with a message, the message will be added to the errors
    list.
    """
    def __init__(self, message=u'', *args, **kwargs):
        ValidationError.__init__(self, message, *args, **kwargs)

def email(message=u'Invalid email address.'):
    """
    Validates an email address. Note that this uses a very primitive regular
    expression and should only be used in instances where you later verify by
    other means, such as email activation or lookups.
    
    `message`
        Error message to raise in case of a validation error.
    """
    def _email(form, field):
        data = field.data is not None and field.data or ''
        if not re.match(r'^.+@[^.].*\.[a-z]{2,}$', data, re.IGNORECASE):
            raise ValidationError(message)
    return _email

def equal_to(fieldname, message=None):
    """
    Compares the fields value with another fields. Useful for e.g. passwords.

    `fieldname`
        The name of the field to compare to.
    `message`
        Error message to raise in case of a validation error. A default
        containing the field name is provided.
    """
    if not message:
        message = u'Field must be equal to %s' % fieldname
    def _equal_to(form, field):
        other = getattr(form, fieldname, None)
        if not other:
            raise ValidationError(u"Invalid field name '%s'" % fieldname)
        elif field.data != other.data:
            raise ValidationError(message)
    return _equal_to

def ip_address(message=u'Invalid IP address.'):
    """
    Validates that the field contains a valid IPv4 format address.

    `message`
        Error message to raise in case of a validation error.
    """
    def _ip_address(form, field):
        if not re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', field.data):
            raise ValidationError(message)
    return _ip_address

def length(min=-1, max=-1, message=None):
    """
    Validates the length of a string.
    
    `min`
        The minimum required length of the string. If not provided, minimum
        length will not be checked.        
    `max`
        The maximum length of the string. If not provided, maximum length will
        not be checked.
    `message`
        Error message to raise in case of a validation error. A default
        containing min and max length is provided.
    """
    if not message:
        message = u'Field must be between %i and %i characters long.' % (min, max)
    def _length(form, field):
        l = field.data and len(field.data) or 0
        if l < min or max != -1 and l > max:
            raise ValidationError(message)
    return _length

def optional():
    """
    Allows empty input and stops the validation chain from continuing.
    """
    def _optional(form, field):
        if not field.data or isinstance(field.data, basestring) and not field.data.strip():
            raise StopValidation()
    _optional.field_flags = ('optional', )
    return _optional

def required(message=u'This field is required.'):
    """
    Validates that the field contains data. This validator will stop the
    validation chain on error.

    `message`
        Error message to raise in case of a validation error.
    """
    def _required(form, field):
        if not field.data or isinstance(field.data, basestring) and not field.data.strip():
            raise StopValidation(message)
    _required.field_flags = ('required', )
    return _required

def regexp(regex, flags=0, message=u'Invalid input.'):
    """
    Validates the field against a user provided regexp.

    `regex`
        The regular expression string to use. Can also be a compiled regular
        expression pattern.
    `flags`
        The regexp flags to use, for example re.IGNORECASE. Ignored if `regex`
        is not a string.  
    `message`
        Error message to raise in case of a validation error.
    """
    def _regexp(form, field):
        data = field.data or ''
        if isinstance(regex, basestring):
            result = re.match(regex, data, flags)
        else:
            result = regex.match(data)
        if not result:
            raise ValidationError(message)
    return _regexp

def url(require_tld=True, message=u'Invalid URL.'):
    """
    Simple regexp based url validation. Much like the email validator, you
    probably want to validate the url later by other means if the url must 
    resolve.

    `require_tld`
        If true, then the domain-name portion of the URL must contain a .tld
        suffix.  Set this to false if you want to allow domains like 
        `localhost`.
    
    `message`
        Error message to raise in case of a validation error.
    """
    BASE_REGEXP = r"""^[a-z]+://([^/:]+%s|([0-9]{1,3}\.){3}[0-9]{1,3})(:[0-9]+)?(\/.*)?$""" 
    url_regexp = re.compile(BASE_REGEXP % (require_tld and r'\.[a-z]{2,}' or ''), re.IGNORECASE)

    return regexp(url_regexp, message=message) 

__all__ = ('ValidationError', 'StopValidation', 'email', 'equal_to', 'ip_address', 'length', 'required', 'optional', 'regexp', 'url')
