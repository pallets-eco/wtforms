import pytest

from wtforms.validators import data_required
from wtforms.validators import email
from wtforms.validators import equal_to
from wtforms.validators import ip_address
from wtforms.validators import length
from wtforms.validators import NumberRange
from wtforms.validators import regexp
from wtforms.validators import url


def test_lazy_proxy_raises(really_lazy_proxy):
    """
    Tests that the validators support lazy translation strings for messages.
    """
    with pytest.raises(
        Exception,
        match=(
            "Translator function called during form declaration: "
            "it should be called at response time."
        ),
    ):
        str(really_lazy_proxy)


def test_lazy_proxy_fixture(really_lazy_proxy):
    """
    Tests that the validators support lazy translation strings for messages.
    """
    equal_to("fieldname", message=really_lazy_proxy)
    length(min=1, message=really_lazy_proxy)
    NumberRange(1, 5, message=really_lazy_proxy)
    data_required(message=really_lazy_proxy)
    regexp(".+", message=really_lazy_proxy)
    email(message=really_lazy_proxy)
    ip_address(message=really_lazy_proxy)
    url(message=really_lazy_proxy)
