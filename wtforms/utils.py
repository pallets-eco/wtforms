

class UnsetValue(object):
    """
    An unset value.

    This is used in situations where a blank value like `None` is acceptable
    usually as the default value of a class variable or function parameter
    (iow, usually when `None` is a valid value.)
    """
    def __str__(self):
        return '<unset value>'

    def __repr__(self):
        return '<unset value>'

    def __bool__(self):
        return False

    def __nonzero__(self):
        return False

unset_value = UnsetValue()
