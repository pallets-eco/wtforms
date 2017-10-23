from __future__ import unicode_literals

import re
import uuid

from wtforms.compat import string_types, text_type

__all__ = (
    'DataRequired', 'data_required', 'Email', 'email', 'EqualTo', 'equal_to',
    'IPAddress', 'ip_address', 'InputRequired', 'input_required', 'Length',
    'length', 'NumberRange', 'number_range', 'Optional', 'optional',
    'Regexp', 'regexp', 'URL', 'url', 'AnyOf',
    'any_of', 'NoneOf', 'none_of', 'MacAddress', 'mac_address', 'UUID'
)


class ValidationError(ValueError):
    """
    Raised when a validator fails to validate its input.
    """
    def __init__(self, message='', *args, **kwargs):
        ValueError.__init__(self, message, *args, **kwargs)


class StopValidation(Exception):
    """
    Causes the validation chain to stop.

    If StopValidation is raised, no more validators in the validation chain are
    called. If raised with a message, the message will be added to the errors
    list.
    """
    def __init__(self, message='', *args, **kwargs):
        Exception.__init__(self, message, *args, **kwargs)


class EqualTo(object):
    """
    Compares the values of two fields.

    :param fieldname:
        The name of the other field to compare to.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated with `%(other_label)s` and `%(other_name)s` to provide a
        more helpful error.
    """
    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.fieldname)
        if field.data != other.data:
            d = {
                'other_label': hasattr(other, 'label') and other.label.text or self.fieldname,
                'other_name': self.fieldname
            }
            message = self.message
            if message is None:
                message = field.gettext('Field must be equal to %(other_name)s.')

            raise ValidationError(message % d)


class Length(object):
    """
    Validates the length of a string.

    :param min:
        The minimum required length of the string. If not provided, minimum
        length will not be checked.
    :param max:
        The maximum length of the string. If not provided, maximum length
        will not be checked.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated using `%(min)d` and `%(max)d` if desired. Useful defaults
        are provided depending on the existence of min and max.
    """
    def __init__(self, min=-1, max=-1, message=None):
        assert min != -1 or max != -1, 'At least one of `min` or `max` must be specified.'
        assert max == -1 or min <= max, '`min` cannot be more than `max`.'
        self.min = min
        self.max = max
        self.message = message

    def __call__(self, form, field):
        l = field.data and len(field.data) or 0
        if l < self.min or self.max != -1 and l > self.max:
            message = self.message
            if message is None:
                if self.max == -1:
                    message = field.ngettext('Field must be at least %(min)d character long.',
                                             'Field must be at least %(min)d characters long.', self.min)
                elif self.min == -1:
                    message = field.ngettext('Field cannot be longer than %(max)d character.',
                                             'Field cannot be longer than %(max)d characters.', self.max)
                else:
                    message = field.gettext('Field must be between %(min)d and %(max)d characters long.')

            raise ValidationError(message % dict(min=self.min, max=self.max, length=l))


class NumberRange(object):
    """
    Validates that a number is of a minimum and/or maximum value, inclusive.
    This will work with any comparable number type, such as floats and
    decimals, not just integers.

    :param min:
        The minimum required value of the number. If not provided, minimum
        value will not be checked.
    :param max:
        The maximum value of the number. If not provided, maximum value
        will not be checked.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated using `%(min)s` and `%(max)s` if desired. Useful defaults
        are provided depending on the existence of min and max.
    """
    def __init__(self, min=None, max=None, message=None):
        self.min = min
        self.max = max
        self.message = message

    def __call__(self, form, field):
        data = field.data
        if data is None or (self.min is not None and data < self.min) or \
                (self.max is not None and data > self.max):
            message = self.message
            if message is None:
                # we use %(min)s interpolation to support floats, None, and
                # Decimals without throwing a formatting exception.
                if self.max is None:
                    message = field.gettext('Number must be at least %(min)s.')
                elif self.min is None:
                    message = field.gettext('Number must be at most %(max)s.')
                else:
                    message = field.gettext('Number must be between %(min)s and %(max)s.')

            raise ValidationError(message % dict(min=self.min, max=self.max))


class Optional(object):
    """
    Allows empty input and stops the validation chain from continuing.

    If input is empty, also removes prior errors (such as processing errors)
    from the field.

    :param strip_whitespace:
        If True (the default) also stop the validation chain on input which
        consists of only whitespace.
    """
    field_flags = ('optional', )

    def __init__(self, strip_whitespace=True):
        if strip_whitespace:
            self.string_check = lambda s: s.strip()
        else:
            self.string_check = lambda s: s

    def __call__(self, form, field):
        if not field.raw_data or isinstance(field.raw_data[0], string_types) and not self.string_check(field.raw_data[0]):
            field.errors[:] = []
            raise StopValidation()


class DataRequired(object):
    """
    Checks the field's data is 'truthy' otherwise stops the validation chain.

    This validator checks that the ``data`` attribute on the field is a 'true'
    value (effectively, it does ``if field.data``.) Furthermore, if the data
    is a string type, a string containing only whitespace characters is
    considered false.

    If the data is empty, also removes prior errors (such as processing errors)
    from the field.

    **NOTE** this validator used to be called `Required` but the way it behaved
    (requiring coerced data, not input data) meant it functioned in a way
    which was not symmetric to the `Optional` validator and furthermore caused
    confusion with certain fields which coerced data to 'falsey' values like
    ``0``, ``Decimal(0)``, ``time(0)`` etc. Unless a very specific reason
    exists, we recommend using the :class:`InputRequired` instead.

    :param message:
        Error message to raise in case of a validation error.
    """
    field_flags = ('required', )

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if not field.data or isinstance(field.data, string_types) and not field.data.strip():
            if self.message is None:
                message = field.gettext('This field is required.')
            else:
                message = self.message

            field.errors[:] = []
            raise StopValidation(message)


class InputRequired(object):
    """
    Validates that input was provided for this field.

    Note there is a distinction between this and DataRequired in that
    InputRequired looks that form-input data was provided, and DataRequired
    looks at the post-coercion data.
    """
    field_flags = ('required', )

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if not field.raw_data or not field.raw_data[0]:
            if self.message is None:
                message = field.gettext('This field is required.')
            else:
                message = self.message

            field.errors[:] = []
            raise StopValidation(message)


class Regexp(object):
    """
    Validates the field against a user provided regexp.

    :param regex:
        The regular expression string to use. Can also be a compiled regular
        expression pattern.
    :param flags:
        The regexp flags to use, for example re.IGNORECASE. Ignored if
        `regex` is not a string.
    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, regex, flags=0, message=None):
        if isinstance(regex, string_types):
            regex = re.compile(regex, flags)
        self.regex = regex
        self.message = message

    def __call__(self, form, field, message=None):
        match = self.regex.match(field.data or '')
        if not match:
            if message is None:
                if self.message is None:
                    message = field.gettext('Invalid input.')
                else:
                    message = self.message

            raise ValidationError(message)
        return match


class Email(Regexp):
    """
    Validates an email address. Note that this uses a very primitive regular
    expression and should only be used in instances where you later verify by
    other means, such as email activation or lookups.

    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        self.validate_hostname = HostnameValidation(
            require_tld=True,
        )
        super(Email, self).__init__(r'^.+@([^.@][^@]+)$', re.IGNORECASE, message)

    def __call__(self, form, field):
        message = self.message
        if message is None:
            message = field.gettext('Invalid email address.')

        match = super(Email, self).__call__(form, field, message)
        if not self.validate_hostname(match.group(1)):
            raise ValidationError(message)


class IPAddress(object):
    """
    Validates an IP address.

    :param ipv4:
        If True, accept IPv4 addresses as valid (default True)
    :param ipv6:
        If True, accept IPv6 addresses as valid (default False)
    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, ipv4=True, ipv6=False, message=None):
        if not ipv4 and not ipv6:
            raise ValueError('IP Address Validator must have at least one of ipv4 or ipv6 enabled.')
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.message = message

    def __call__(self, form, field):
        value = field.data
        valid = False
        if value:
            valid = (self.ipv4 and self.check_ipv4(value)) or (self.ipv6 and self.check_ipv6(value))

        if not valid:
            message = self.message
            if message is None:
                message = field.gettext('Invalid IP address.')
            raise ValidationError(message)

    @classmethod
    def check_ipv4(cls, value):
        parts = value.split('.')
        if len(parts) == 4 and all(x.isdigit() for x in parts):
            numbers = list(int(x) for x in parts)
            return all(num >= 0 and num < 256 for num in numbers)
        return False

    @classmethod
    def check_ipv6(cls, value):
        parts = value.split(':')
        if len(parts) > 8:
            return False

        num_blank = 0
        for part in parts:
            if not part:
                num_blank += 1
            else:
                try:
                    value = int(part, 16)
                except ValueError:
                    return False
                else:
                    if value < 0 or value >= 65536:
                        return False

        if num_blank < 2:
            return True
        elif num_blank == 2 and not parts[0] and not parts[1]:
            return True
        return False


class MacAddress(Regexp):
    """
    Validates a MAC address.

    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        pattern = r'^(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$'
        super(MacAddress, self).__init__(pattern, message=message)

    def __call__(self, form, field):
        message = self.message
        if message is None:
            message = field.gettext('Invalid Mac address.')

        super(MacAddress, self).__call__(form, field, message)


class URL(Regexp):
    """
    Simple regexp based url validation. Much like the email validator, you
    probably want to validate the url later by other means if the url must
    resolve.

    :param require_tld:
        If true, then the domain-name portion of the URL must contain a .tld
        suffix.  Set this to false if you want to allow domains like
        `localhost`.
    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, require_tld=True, message=None):
        regex = r'^[a-z]+://(?P<host>[^/:]+)(?P<port>:[0-9]+)?(?P<path>\/.*)?$'
        super(URL, self).__init__(regex, re.IGNORECASE, message)
        self.validate_hostname = HostnameValidation(
            require_tld=require_tld,
            allow_ip=True,
        )

    def __call__(self, form, field):
        message = self.message
        if message is None:
            message = field.gettext('Invalid URL.')

        match = super(URL, self).__call__(form, field, message)
        if not self.validate_hostname(match.group('host')):
            raise ValidationError(message)


class UUID(object):
    """
    Validates a UUID.

    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        message = self.message
        if message is None:
            message = field.gettext('Invalid UUID.')
        try:
            uuid.UUID(field.data)
        except ValueError:
            raise ValidationError(message)


class AnyOf(object):
    """
    Compares the incoming data to a sequence of valid inputs.

    :param values:
        A sequence of valid inputs.
    :param message:
        Error message to raise in case of a validation error. `%(values)s`
        contains the list of values.
    :param values_formatter:
        Function used to format the list of values in the error message.
    """
    def __init__(self, values, message=None, values_formatter=None):
        self.values = values
        self.message = message
        if values_formatter is None:
            values_formatter = self.default_values_formatter
        self.values_formatter = values_formatter

    def __call__(self, form, field):
        if field.data not in self.values:
            message = self.message
            if message is None:
                message = field.gettext('Invalid value, must be one of: %(values)s.')

            raise ValidationError(message % dict(values=self.values_formatter(self.values)))

    @staticmethod
    def default_values_formatter(values):
        return ', '.join(text_type(x) for x in values)


class NoneOf(object):
    """
    Compares the incoming data to a sequence of invalid inputs.

    :param values:
        A sequence of invalid inputs.
    :param message:
        Error message to raise in case of a validation error. `%(values)s`
        contains the list of values.
    :param values_formatter:
        Function used to format the list of values in the error message.
    """
    def __init__(self, values, message=None, values_formatter=None):
        self.values = values
        self.message = message
        if values_formatter is None:
            values_formatter = self.default_values_formatter
        self.values_formatter = values_formatter

    def __call__(self, form, field):
        if field.data in self.values:
            message = self.message
            if message is None:
                message = field.gettext('Invalid value, can\'t be any of: %(values)s.')

            raise ValidationError(message % dict(values=self.values_formatter(self.values)))

    @staticmethod
    def default_values_formatter(v):
        return ', '.join(text_type(x) for x in v)


class HostnameValidation(object):
    """
    Helper class for checking hostnames for validation.

    This is not a validator in and of itself, and as such is not exported.
    """
    hostname_part = re.compile(r'^(xn-|[a-z0-9]+)(-[a-z0-9]+)*$', re.IGNORECASE)
    tld_part = re.compile(r'^([a-z]{2,20}|xn--([a-z0-9]+-)*[a-z0-9]+)$', re.IGNORECASE)

    def __init__(self, require_tld=True, allow_ip=False):
        self.require_tld = require_tld
        self.allow_ip = allow_ip

    def __call__(self, hostname):
        if self.allow_ip:
            if IPAddress.check_ipv4(hostname) or IPAddress.check_ipv6(hostname):
                return True

        # Encode out IDNA hostnames. This makes further validation easier.
        hostname = hostname.encode('idna')

        # Turn back into a string in Python 3x
        if not isinstance(hostname, string_types):
            hostname = hostname.decode('ascii')

        if len(hostname) > 253:
            return False

        # Check that all labels in the hostname are valid
        parts = hostname.split('.')
        for part in parts:
            if not part or len(part) > 63:
                return False
            if not self.hostname_part.match(part):
                return False

        if self.require_tld:
            if len(parts) < 2 or not self.tld_part.match(parts[-1]):
                return False

        return True


class Zipcode(object):
    """
    Validates a field as zipcode
    """

    # regexes sourced from
    # http://unicode.org/cldr/trac/browser/tags/release-26-0-1/common/supplemental/postalCodeData.xml?rev=11071
    ZIPCODE_REGEXES = {
        "GB": ("^GIR[ ]?0AA|((AB|AL|B|BA|BB|BD|BH|BL|BN|BR|BS|BT|CA|CB|CF|CH|CM|CO|CR|CT|CV|CW|DA|DD|DE|DG|DH"
               "|DL|DN|DT|DY|E|EC|EH|EN|EX|FK|FY|G|GL|GY|GU|HA|HD|HG|HP|HR|HS|HU|HX|IG|IM|IP|IV|JE|KA|KT|KW|"
               "KY|L|LA|LD|LE|LL|LN|LS|LU|M|ME|MK|ML|N|NE|NG|NN|NP|NR|NW|OL|OX|PA|PE|PH|PL|PO|PR|RG|RH|RM|S|"
               "SA|SE|SG|SK|SL|SM|SN|SO|SP|SR|SS|ST|SW|SY|TA|TD|TF|TN|TQ|TR|TS|TW|UB|W|WA|WC|WD|WF|WN|WR|WS|"
               "WV|YO|ZE)(\d[\dA-Z]?[ ]?\d[ABD-HJLN-UW-Z]{2}))|BFPO[ ]?\d{1,4}$"
               ),
        "JE": "^JE\d[\dA-Z]?[ ]?\d[ABD-HJLN-UW-Z]{2}$",
        "GG": "^GY\d[\dA-Z]?[ ]?\d[ABD-HJLN-UW-Z]{2}$",
        "IM": "^IM\d[\dA-Z]?[ ]?\d[ABD-HJLN-UW-Z]{2}$",
        "US": "^\d{5}([ \-]\d{4})?$",
        "CA": "^[ABCEGHJKLMNPRSTVXY]\d[ABCEGHJ-NPRSTV-Z][ ]?\d[ABCEGHJ-NPRSTV-Z]\d$",
        "DE": "^\d{5}$",
        "JP": "^\d{3}-\d{4}$",
        "FR": "^\d{2}[ ]?\d{3}$",
        "AU": "^\d{4}$",
        "IT": "^\d{5}$",
        "CH": "^\d{4}$",
        "AT": "^\d{4}$",
        "ES": "^\d{5}$",
        "NL": "^\d{4}[ ]?[A-Z]{2}$",
        "BE": "^\d{4}$",
        "DK": "^\d{4}$",
        "SE": "^\d{3}[ ]?\d{2}$",
        "NO": "^\d{4}$",
        "BR": "^\d{5}[\-]?\d{3}$",
        "PT": "^\d{4}([\-]\d{3})?$",
        "FI": "^\d{5}$",
        "AX": "^22\d{3}$",
        "KR": "^\d{3}[\-]\d{3}$",
        "CN": "^\d{6}$",
        "TW": "^\d{3}(\d{2})?$",
        "SG": "^\d{6}$",
        "DZ": "^\d{5}$",
        "AD": "^AD\d{3}$",
        "AR": "^([A-HJ-NP-Z])?\d{4}([A-Z]{3})?$",
        "AM": "^(37)?\d{4}$",
        "AZ": "^\d{4}$",
        "BH": "^((1[0-2]|[2-9])\d{2})?$",
        "BD": "^\d{4}$",
        "BB": "^(BB\d{5})?$",
        "BY": "^\d{6}$",
        "BM": "^[A-Z]{2}[ ]?[A-Z0-9]{2}$",
        "BA": "^\d{5}$",
        "IO": "^BBND 1ZZ$",
        "BN": "^[A-Z]{2}[ ]?\d{4}$",
        "BG": "^\d{4}$",
        "KH": "^\d{5}$",
        "CV": "^\d{4}$",
        "CL": "^\d{7}$",
        "CR": "^\d{4,5}|\d{3}-\d{4}$",
        "HR": "^\d{5}$",
        "CY": "^\d{4}$",
        "CZ": "^\d{3}[ ]?\d{2}$",
        "DO": "^\d{5}$",
        "EC": "^([A-Z]\d{4}[A-Z]|(?:[A-Z]{2})?\d{6})?$",
        "EG": "^\d{5}$",
        "EE": "^\d{5}$",
        "FO": "^\d{3}$",
        "GE": "^\d{4}$",
        "GR": "^\d{3}[ ]?\d{2}$",
        "GL": "^39\d{2}$",
        "GT": "^\d{5}$",
        "HT": "^\d{4}$",
        "HN": "^(?:\d{5})?$",
        "HU": "^\d{4}$",
        "IS": "^\d{3}$",
        "IN": "^\d{6}$",
        "ID": "^\d{5}$",
        "IL": "^\d{5}$",
        "JO": "^\d{5}$",
        "KZ": "^\d{6}$",
        "KE": "^\d{5}$",
        "KW": "^\d{5}$",
        "LA": "^\d{5}$",
        "LV": "^\d{4}$",
        "LB": "^(\d{4}([ ]?\d{4})?)?$",
        "LI": "^(948[5-9])|(949[0-7])$",
        "LT": "^\d{5}$",
        "LU": "^\d{4}$",
        "MK": "^\d{4}$",
        "MY": "^\d{5}$",
        "MV": "^\d{5}$",
        "MT": "^[A-Z]{3}[ ]?\d{2,4}$",
        "MU": "^(\d{3}[A-Z]{2}\d{3})?$",
        "MX": "^\d{5}$",
        "MD": "^\d{4}$",
        "MC": "^980\d{2}$",
        "MA": "^\d{5}$",
        "NP": "^\d{5}$",
        "NZ": "^\d{4}$",
        "NI": "^((\d{4}-)?\d{3}-\d{3}(-\d{1})?)?$",
        "NG": "^(\d{6})?$",
        "OM": "^(PC )?\d{3}$",
        "PK": "^\d{5}$",
        "PY": "^\d{4}$",
        "PH": "^\d{4}$",
        "PL": "^\d{2}-\d{3}$",
        "PR": "^00[679]\d{2}([ \-]\d{4})?$",
        "RO": "^\d{6}$",
        "RU": "^\d{6}$",
        "SM": "^4789\d$",
        "SA": "^\d{5}$",
        "SN": "^\d{5}$",
        "SK": "^\d{3}[ ]?\d{2}$",
        "SI": "^\d{4}$",
        "ZA": "^\d{4}$",
        "LK": "^\d{5}$",
        "TJ": "^\d{6}$",
        "TH": "^\d{5}$",
        "TN": "^\d{4}$",
        "TR": "^\d{5}$",
        "TM": "^\d{6}$",
        "UA": "^\d{5}$",
        "UY": "^\d{5}$",
        "UZ": "^\d{6}$",
        "VA": "^00120$",
        "VE": "^\d{4}$",
        "ZM": "^\d{5}$",
        "AS": "^96799$",
        "CC": "^6799$",
        "CK": "^\d{4}$",
        "RS": "^\d{6}$",
        "ME": "^8\d{4}$",
        "CS": "^\d{5}$",
        "YU": "^\d{5}$",
        "CX": "^6798$",
        "ET": "^\d{4}$",
        "FK": "^FIQQ 1ZZ$",
        "NF": "^2899$",
        "FM": "^(9694[1-4])([ \-]\d{4})?$",
        "GF": "^9[78]3\d{2}$",
        "GN": "^\d{3}$",
        "GP": "^9[78][01]\d{2}$",
        "GS": "^SIQQ 1ZZ$",
        "GU": "^969[123]\d([ \-]\d{4})?$",
        "GW": "^\d{4}$",
        "HM": "^\d{4}$",
        "IQ": "^\d{5}$",
        "KG": "^\d{6}$",
        "LR": "^\d{4}$",
        "LS": "^\d{3}$",
        "MG": "^\d{3}$",
        "MH": "^969[67]\d([ \-]\d{4})?$",
        "MN": "^\d{6}$",
        "MP": "^9695[012]([ \-]\d{4})?$",
        "MQ": "^9[78]2\d{2}$",
        "NC": "^988\d{2}$",
        "NE": "^\d{4}$",
        "VI": "^008(([0-4]\d)|(5[01]))([ \-]\d{4})?$",
        "PF": "^987\d{2}$",
        "PG": "^\d{3}$",
        "PM": "^9[78]5\d{2}$",
        "PN": "^PCRN 1ZZ$",
        "PW": "^96940$",
        "RE": "^9[78]4\d{2}$",
        "SH": "^(ASCN|STHL) 1ZZ$",
        "SJ": "^\d{4}$",
        "SO": "^\d{5}$",
        "SZ": "^[HLMS]\d{3}$",
        "TC": "^TKCA 1ZZ$",
        "WF": "^986\d{2}$",
        "XK": "^\d{5}$",
        "YT": "^976\d{2}"
    }

    def __init__(self, country_code=None, country_code_field=None):
        if not country_code and not country_code_field:
            raise ValidationError(message='You must provide country_code or country_code_field when using Zipcode validator')
        self.country_code = country_code
        self.country_code_field = country_code_field

    def __call__(self, form, field):
        country_code = self.country_code or form.data.get(self.country_code_field, 'US')

        if country_code not in self.ZIPCODE_REGEXES.keys():
            raise ValidationError(message='Failed to validate zipcode against country code {0}'.format(country_code))

        p = re.compile(self.ZIPCODE_REGEXES.get(country_code), re.IGNORECASE)

        if not p.match(field.data):
            raise ValidationError(message='Invalid format for Country Code {0}'.format(country_code))


email = Email
equal_to = EqualTo
ip_address = IPAddress
mac_address = MacAddress
length = Length
number_range = NumberRange
optional = Optional
input_required = InputRequired
data_required = DataRequired
regexp = Regexp
url = URL
any_of = AnyOf
none_of = NoneOf
zipcode = Zipcode
