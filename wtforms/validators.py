import re


__all__ = (
    'Email', 'email', 'EqualTo', 'equal_to', 'IPAddress', 'ip_address',
    'Length', 'length', 'Optional', 'optional', 'Required', 'required',
    'Regexp', 'regexp', 'URL', 'url',
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


class EqualTo(object):
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
        self.message = message or u'Field must be equal to %s' % fieldname

    def __call__(self, form, field):
        other = getattr(form, self.fieldname, None)
        if not other:
            raise ValidationError(u"Invalid field name '%s'" % self.fieldname)
        elif field.data != other.data:
            raise ValidationError(self.message)


class IPAddress(object):
    """
    Validates an IP(v4) address.
    """
    def __init__(self, message=u'Invalid IP address.'):
        """
        `message`
            Error message to raise in case of a validation error.
        """
        self.message = message
    
    def __call__(self, form, field):
        if not re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', field.data):
            raise ValidationError(self.message)


class Length(object):
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
        self.min = min
        self.max = max
        self.message = message or u'Field must be between %i and %i characters long.' % (min, max)
    
    def __call__(self, form, field):
        l = field.data and len(field.data) or 0
        if l < self.min or self.max != -1 and l > self.max:
            raise ValidationError(self.message)


class Optional(object):
    """
    Allows empty input and stops the validation chain from continuing.
    """
    field_flags = ('optional', )

    def __call__(self, form, field):
        if not field.data or isinstance(field.data, basestring) and not field.data.strip():
            raise StopValidation()


class Required(object):
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

    def __call__(self, form, field):
        if not field.data or isinstance(field.data, basestring) and not field.data.strip():
            raise StopValidation(self.message)


class Regexp(object):
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
        self.regex = isinstance(regex, basestring) and re.compile(regex, flags) or regex
        self.message = message
    
    def __call__(self, form, field):
        if not self.regex.match(field.data or ''):
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
        super(URL, self).__init__(regex, re.IGNORECASE, message)


email = Email
equal_to = EqualTo
ip_address = IPAddress
length = Length
optional = Optional
required = Required
regexp = Regexp
url = URL
