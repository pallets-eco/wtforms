import pytest

from wtforms.validators import url
from wtforms.validators import ValidationError


@pytest.mark.parametrize(
    "url_val",
    [
        "http://foobar.dk",
        "http://foobar.dk/",
        "http://foo-bar.dk/",
        "http://foo--bar.dk/",
        "http://foo_bar.dk/",
        "http://foobar.dk?query=param",
        "http://foobar.dk/path?query=param",
        "http://foobar.dk/path?query=param&foo=faa",
        "http://foobar.museum/foobar",
        "http://192.168.0.1/foobar",
        "http://192.168.0.1:9000/fake",
        "http://مثال.إختبار/foo.com",  # Arabic
        "http://उदाहरण.परीक्षा/",  # Hindi
        "http://실례.테스트",  # Hangul
    ],
)
def test_valid_url_passes(url_val, dummy_form, dummy_field):
    """Well-formed http(s) URLs without userinfo pass with default settings."""
    validator = url()
    dummy_field.data = url_val
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "url_val",
    [
        "http://localhost/foobar",
        "http://foobar",
        "http://foobar?query=param&foo=faa",
        "http://foobar:5000?query=param&foo=faa",
        "http://foobar/path?query=param&foo=faa",
        "http://foobar:1234/path?query=param&foo=faa",
    ],
)
def test_valid_url_notld_passes(url_val, dummy_form, dummy_field):
    """``require_tld=False`` accepts hosts without a dotted suffix."""
    validator = url(require_tld=False)
    dummy_field.data = url_val
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "url_val",
    [
        "http://foobar",
        "http://-foobar.dk/",
        "http://foobar-.dk/",
        "foobar.dk",
        "http://127.0.0/asdf",
        "http://foobar.d",
        "http://foobar.12",
        "http://localhost:abc/a",
    ],
)
def test_bad_url_raises(url_val, dummy_form, dummy_field):
    """Malformed URLs raise ValidationError."""
    validator = url()
    dummy_field.data = url_val
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


USERINFO_URLS = [
    "http://username:password@foobar.dk",
    "http://username@foobar.dk",
    "http://usern@me:p@ssword@foobar.dk",
    "http://username:password@foobar.dk:1234/path?query=parm",
]


@pytest.mark.parametrize("url_val", USERINFO_URLS)
def test_userinfo_rejected_by_default(url_val, dummy_form, dummy_field):
    """``user:password@host`` URLs are rejected unless explicitly allowed."""
    validator = url()
    dummy_field.data = url_val
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


@pytest.mark.parametrize("url_val", USERINFO_URLS)
def test_userinfo_passes_with_allow_userinfo(url_val, dummy_form, dummy_field):
    """``allow_userinfo=True`` opts into accepting ``user:password@host`` URLs."""
    validator = url(allow_userinfo=True)
    dummy_field.data = url_val
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "url_val",
    [
        "javascript://example.com/%0aalert(1)",
        "file:///etc/passwd",
        "data:text/plain,foo",
        "ftp://example.com/file.txt",
    ],
)
def test_non_http_schemes_rejected_by_default(url_val, dummy_form, dummy_field):
    """Only http(s) are accepted unless ``schemes`` is overridden."""
    validator = url()
    dummy_field.data = url_val
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


def test_custom_schemes_allowlist(dummy_form, dummy_field):
    """A custom ``schemes`` allowlist controls which schemes pass."""
    validator = url(schemes=("ftp",))
    dummy_field.data = "ftp://example.com/file.txt"
    validator(dummy_form, dummy_field)
    dummy_field.data = "http://example.com/"
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


def test_schemes_none_disables_allowlist(dummy_form, dummy_field):
    """``schemes=None`` disables the scheme allowlist entirely."""
    validator = url(schemes=None)
    dummy_field.data = "ftp://example.com/file.txt"
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "url_val",
    [
        "http://example.com:99999/",
        "http://example.com:abc/",
    ],
)
def test_invalid_port_raises(url_val, dummy_form, dummy_field):
    """Out-of-range or non-numeric ports raise ValidationError."""
    validator = url()
    dummy_field.data = url_val
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)
