"""
    wtforms.validators
    ~~~~~~~~~~~~~~~~~~
    
    TODO
    
    :copyright: 2007-2008 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
import re

class ValidationError(ValueError):
    """ Raised when a validator fails to validate it's input. """
    pass

class StopValidation(ValueError):
    def __init__(self, message=u'', *args, **kwargs):
        super(StopValidation, self).__init__(message, *args, **kwargs)

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
        if not re.match(r'^.+@[^.].*\.[a-z]{2,4}$', data, re.IGNORECASE):
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

def is_checked(message=u'Field must tbe checked.'):
    """
    Checks that the field is checked. Used with boolean fields.

    `message`
        Error message to raise in case of a validation error.
    """
    def _is_checked(form, field):
        if not field.data:
            raise ValidationError(message)
    return _is_checked

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

def optional(form=None, field=None):
    """
    Allows empty input and stops the validation chain from continuing.
    """
    if form is None and field is None:
        return optional
    elif not field.data or (isinstance(field.data, basestring) and not field.data.strip()):
        raise StopValidation()

def required(message=u'Field must not be empty.'):
    """
    Validates that the field is not empty.
    
    `message`
        Error message to raise in case of a validation error.
    """
    def _required(form, field):
        if not field.data or (isinstance(field.data, basestring) and not field.data.strip()):
            raise StopValidation(message)
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
    url_regexp = re.compile(BASE_REGEXP % (require_tld and r'\.[a-z]{2,4}' or ''), re.IGNORECASE)

    return regexp(url_regexp, message=message) 


__all__ = ('ValidationError', 'StopValidation', 'email', 'equal_to', 'ip_address', 'is_checked', 'length', 'required', 'optional', 'regexp', 'url')
