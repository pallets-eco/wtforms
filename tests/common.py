from wtforms.validators import ValidationError, StopValidation


class DummyTranslations(object):
    def gettext(self, string):
        return string

    def ngettext(self, singular, plural, n):
        if n == 1:
            return singular

        return plural


class DummyField(object):
    _translations = DummyTranslations()

    def __init__(self, data, errors=(), raw_data=None):
        self.data = data
        self.errors = list(errors)
        self.raw_data = raw_data

    def gettext(self, string):
        return self._translations.gettext(string)

    def ngettext(self, singular, plural, n):
        return self._translations.ngettext(singular, plural, n)


def grab_error_message(callable, form, field):
    try:
        callable(form, field)
    except ValidationError as e:
        return e.args[0]


def grab_stop_message(callable, form, field):
    try:
        callable(form, field)
    except StopValidation as e:
        return e.args[0]


class DummyPostData(dict):
    def getlist(self, key):
        v = self[key]
        if not isinstance(v, (list, tuple)):
            v = [v]
        return v
