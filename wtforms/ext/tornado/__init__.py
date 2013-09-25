# -*- coding: utf-8 -*-
import re

from tornado import escape
from wtforms.compat import text_type


class TornadoInputWrapper(object):

    def __init__(self, multidict):
        self._wrapped = multidict

    def __iter__(self):
        return iter(self._wrapped)

    def __len__(self):
        return len(self._wrapped)

    def __contains__(self, name):
        return (name in self._wrapped)

    def __getitem__(self, name):
        return self._wrapped[name]

    def __getattr__(self, name):
        return self.__getitem__(name)

    def getlist(self, name):
        try:
            values = []
            for value in self._wrapped[name]:
                value = escape.to_unicode(value)
                if isinstance(value, text_type):
                    value = re.sub(r'[\x00-\x08\x0e-\x1f]', ' ', value)
                values.append(value)
            return values
        except KeyError:
            return []