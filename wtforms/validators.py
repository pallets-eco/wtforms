class IPList(object):
    """
    Validates an IP address list.
    Input must be of Type list.

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
        if type(value) is list:
            for ip in value:
                valid = (self.ipv4 and self.check_ipv4(ip)) or (self.ipv6 and self.check_ipv6(ip))

                if not valid:
                    message = self.message
                    if message is None:
                        message = field.gettext('Invalid IP address.')
                        raise ValidationError(message)
        else:
            message = field.gettext('Invalid Input.. Object Type must be list.')
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
