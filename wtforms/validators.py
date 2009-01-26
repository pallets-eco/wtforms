"""
    wtforms.validators
    ~~~~~~~~~~~~~~~~~~

    Contains all built-in validators such as `required` and `optional`.
    
    :copyright: 2009 by James Crasta, Thomas Johansson.
    :license: MIT, see LICENSE.txt for details.
"""
import re

__all__ = (
    'Email', 'EqualTo', 'IPAddress', 'Length', 'Required', 'Optional', 'Regexp',
    'URL', 'email', 'equal_to', 'ip_address', 'length', 'required', 'optional',
    'regexp', 'url'
)

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

class Validator(object):
    """
    Validator base class
    """
    def __call__(self, form, field):
        """
        Calls `validate`. Do **NOT** override this.
        """
        return self.validate(form, field)

    def validate(self, form, field):
        """
        Validators should override this to implement their validation behaviour.
        
        `form`
            The form the field being validated belongs to.
        `field`
            The field to validate.
        """
        raise NotImplementedError

class EqualTo(Validator):
    """
    Compares the values of two fields.
    """
    def __init__(self, fieldname, message=None):
        """
        `fieldname`
            The name of the other field to compare to.
        `message`
            Error message to raise in case of a validation error.
        """
        self.fieldname = fieldname
        if message is not None:
            self.message = message
        else:
            self.message = u'Field must be equal to %s' % fieldname

    def validate(self, form, field):
        other = getattr(form, self.fieldname, None)
        if not other:
            raise ValidationError(u"Invalid field name '%s'" % self.fieldname)
        elif field.data != other.data:
            raise ValidationError(self.message)

class IPAddress(Validator):
    """
    Validates an IP(v4) address.
    """
    def __init__(self, message=u'Invalid IP address.'):
        """
        `message`
            Error message to raise in case of a validation error.
        """
        self.message = message
    
    def validate(self, form, field):
        if not re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', field.data):
            raise ValidationError(self.message)

class Length(Validator):
    """
    Validates the length of a string.
    """
    def __init__(self, min=-1, max=-1, message=None):
        """
        `min`
            The minimum required length of the string. If not provided, minimum
            length will not be checked.        
        `max`
            The maximum length of the string. If not provided, maximum length
            will not be checked.
        `message`
            Error message to raise in case of a validation error. A default
            containing min and max length is provided.
        """
        if message:
            self.message = message
        else:
            self.message = u'Field must be between %i and %i characters long.' % (min, max)
        self.min = min
        self.max = max
    
    def validate(self, form, field):
        l = field.data and len(field.data) or 0
        if l < self.min or self.max != -1 and l > self.max:
            raise ValidationError(self.message)

class Optional(Validator):
    """
    Allows empty input and stops the validation chain from continuing.
    """
    field_flags = ('optional', )

    def validate(self, form, field):
        if not field.data or isinstance(field.data, basestring) and not field.data.strip():
            raise StopValidation()

class Required(Validator):
    """
    Validates that the field contains data. This validator will stop the
    validation chain on error.
    """
    field_flags = ('required', )

    def __init__(self, message=u'This field is required.'):
        """
        `message`
            Error message to raise in case of a validation error.
        """
        self.message = message

    def validate(self, form, field):
        if not field.data or isinstance(field.data, basestring) and not field.data.strip():
            raise StopValidation(self.message)

class Regexp(Validator):
    """
    Validates the field against a user provided regexp.
    """
    def __init__(self, regex, flags=0, message=u'Invalid input.'):
        """
        `regex`
            The regular expression string to use. Can also be a compiled regular
            expression pattern.
        `flags`
            The regexp flags to use, for example re.IGNORECASE. Ignored if
            `regex` is not a string.  
        `message`
            Error message to raise in case of a validation error.
        """
        if isinstance(regex, basestring):
            self.regex = re.compile(regex, flags)
        else:
            self.regex = regex
        self.message = message
    
    def validate(self, form, field):
        data = field.data or ''
        result = self.regex.match(data)
        if not result:
            raise ValidationError(self.message)

class Email(Regexp):
    """
    Validates an email address. Note that this uses a very primitive regular
    expression and should only be used in instances where you later verify by
    other means, such as email activation or lookups.
    """
    def __init__(self, message=u'Invalid email address.'):
        """
        `message`
            Error message to raise in case of a validation error.
        """
        super(Email, self).__init__(r'^.+@[^.].*\.[a-z]{2,}$', re.IGNORECASE, message)

class URL(Regexp):
    """
    Simple regexp based url validation. Much like the email validator, you
    probably want to validate the url later by other means if the url must 
    resolve.
    """
    def __init__(self, require_tld=True, message=u'Invalid URL.'):
        """
        `require_tld`
            If true, then the domain-name portion of the URL must contain a .tld
            suffix.  Set this to false if you want to allow domains like 
            `localhost`.
        
        `message`
            Error message to raise in case of a validation error.
        """
        regex = r'^[a-z]+://([^/:]+%s|([0-9]{1,3}\.){3}[0-9]{1,3})(:[0-9]+)?(\/.*)?$' % (require_tld and r'\.[a-z]{2,}' or '')
        flags = re.IGNORECASE
        super(URL, self).__init__(regex, flags, message)

# Factory-style access - Mostly for backwards compatibility            
email = Email
equal_to = EqualTo
ip_address = IPAddress
length = Length
optional = Optional
required = Required
regexp = Regexp
url = URL
