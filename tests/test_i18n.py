import pytest

from wtforms import form
from wtforms import StringField
from wtforms import validators
from wtforms.i18n import get_translations


def gettext_lower(self, s):
    return s.lower()


def ngettext_lower(self, singular, plural, n):
    if n == 1:
        return singular.lower()
    else:
        return plural.lower()


class Lower_Translator:
    """A fake translator that just converts everything to lowercase."""

    gettext = gettext_lower
    ngettext = ngettext_lower


def test_failure():
    with pytest.raises(IOError):
        get_translations([])


def test_us_translation():
    translations = get_translations(["en_US"])
    assert translations.gettext("Invalid Mac address.") == "Invalid MAC address."


def _test_converter(translator):
    translations = get_translations([], getter=lambda x: translator)
    assert translations.gettext("Foo") == "foo"
    assert translations.ngettext("Foo", "Foos", 1) == "foo"
    assert translations.ngettext("Foo", "Foos", 2) == "foos"
    return translations


def test_python3_nowrap():
    translator = Lower_Translator()
    translations = _test_converter(translator)
    assert translations is translator


class CoreForm1(form.Form):
    class Meta:
        locales = ["en_US", "en"]

    a = StringField(validators=[validators.DataRequired()])


class CoreForm2(form.Form):
    a = StringField(validators=[validators.DataRequired(), validators.Length(max=3)])


class CoreForm3(form.Form):
    a = StringField(validators=[validators.Length(max=1)])


def _common_test(expected_error, form_kwargs, form_class=None):
    if not form_class:
        form_class = CoreForm1
    form = form_class(**form_kwargs)
    assert not form.validate()
    assert form.a.errors[0] == expected_error
    return form


def test_core_defaults():
    # Test with the default language
    form = _common_test("This field is required.", {})
    # Make sure we have a gettext translations context
    assert form.a.gettext("") != ""

    form = _common_test("This field is required.", {}, CoreForm2)
    assert form.meta.get_translations(form) is None
    assert form.meta.locales is False
    assert form.a.gettext("") == ""


def test_core_fallback():
    form = _common_test("This field is required.", dict(meta=dict(locales=False)))
    assert form.a.gettext("") == ""


def test_core_override_languages():
    _common_test("Este campo es obligatorio.", dict(meta=dict(locales=["es_ES"])))


def test_core_ngettext():
    language_settings = [
        (
            ["en_US", "en"],
            "Field cannot be longer than 3 characters.",
            "Field cannot be longer than 1 character.",
        ),
        (
            ["de_DE", "de"],
            "Feld kann nicht l\xe4nger als 3 Zeichen sein.",
            "Feld kann nicht l\xe4nger als 1 Zeichen sein.",
        ),
        (
            ["et"],
            "V\xe4li ei tohi olla \xfcle 3 t\xe4hem\xe4rgi pikk.",
            "V\xe4li ei tohi olla \xfcle 1 t\xe4hem\xe4rgi pikk.",
        ),
    ]
    for languages, match1, match2 in language_settings:
        settings = dict(a="toolong", meta=dict(locales=languages))
        _common_test(match1, settings, CoreForm2)
        _common_test(match2, settings, CoreForm3)


def test_core_cache():
    settings = {"meta": {"locales": ["de_DE"], "cache_translations": True}}
    expected = "Dieses Feld wird ben\xf6tigt."
    form1 = _common_test(expected, settings)
    form2 = _common_test(expected, settings)
    assert form1.meta.get_translations(form1) is form2.meta.get_translations(form2)
    settings["meta"]["cache_translations"] = False
    form3 = _common_test(expected, settings)
    assert form2.meta.get_translations(form2) is not form3.meta.get_translations(form3)


class TranslationsForm1(form.Form):
    a = StringField(validators=[validators.Length(max=5)])


class TranslationsForm2(form.Form):
    class Meta:
        def get_translations(self, form):
            return Lower_Translator()

    a = StringField("", [validators.Length(max=5)])


def test_gettext():
    x = "foo"
    assert TranslationsForm1().a.gettext(x) is x


def test_translations_ngettext():
    def getit(n):
        return TranslationsForm1().a.ngettext("antelope", "antelopes", n)

    assert getit(0) == "antelopes"
    assert getit(1) == "antelope"
    assert getit(2) == "antelopes"


def test_translations_validator_translation():
    form = TranslationsForm2(a="hellobye")
    assert not form.validate()
    assert form.a.errors[0] == "field cannot be longer than 5 characters."
    form = TranslationsForm1(a="hellobye")
    assert not form.validate()
    assert form.a.errors[0] == "Field cannot be longer than 5 characters."
