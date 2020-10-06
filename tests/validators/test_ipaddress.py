import pytest

from wtforms.validators import ip_address
from wtforms.validators import ValidationError


@pytest.mark.parametrize("address", ["147.230.23.25", "147.230.23.0", "127.0.0.1"])
def test_ip4address_passes(address, dummy_form, dummy_field):
    adr = ip_address()
    dummy_field.data = address
    adr(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "address",
    [
        "2001:718:1C01:1111::1111",
        "2001:718:1C01:1111::",
        "::1",
        "dead:beef:0:0:0:0:42:1",
        "abcd:ef::42:1",
    ],
)
def test_good_ip6address_passes(address, dummy_form, dummy_field):
    adr = ip_address(ipv6=True)
    dummy_field.data = address
    adr(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "address",
    [
        "2001:718:1C01:1111::1111",
        "2001:718:1C01:1111::",
        "abc.0.0.1",
        "abcd:1234::123::1",
        "1:2:3:4:5:6:7:8:9",
        "abcd::1ffff",
    ],
)
def test_bad_ip6address_raises(address, dummy_form, dummy_field):
    adr = ip_address()
    dummy_field.data = address
    with pytest.raises(ValidationError):
        adr(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "address",
    [
        "147.230.1000.25",
        "2001:718::::",
        "abc.0.0.1",
        "1278.0.0.1",
        "127.0.0.abc",
        "900.200.100.75",
    ],
)
def test_bad_ip4address_raises(address, dummy_form, dummy_field):
    adr = ip_address(ipv6=True)
    dummy_field.data = address
    with pytest.raises(ValidationError):
        adr(dummy_form, dummy_field)


def test_ip_address_raises_on_bad_init():
    """
    IpAddress validator should raise ValueError when ipv6=False and ipv4=False
    """
    with pytest.raises(ValueError):
        ip_address(ipv4=False, ipv6=False)
