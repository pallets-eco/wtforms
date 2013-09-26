

class lazy_property(object):
    """
    Allows an instance method to become a property that is evaluated only once.

        >>> @lazy_property
        ... def foobar(self):
        ...     return expensive_calculation()

    The lazy_property evaluates the function it is passed once per instantiation
    of the enclosing class.
    """
    def __init__(self, func, prop_name=None):
        self._func = func
        self.__name__ = prop_name or func.__name__
        self.__doc__ = func.__doc__

    def __get__(self, obj, klass=None):
        if obj is None:
            return self
        if self.__name__ in obj.__dict__:
            result = obj.__dict__[self.__name__]
        else:
            result = obj.__dict__[self.__name__] = self._func(obj)
        return result
