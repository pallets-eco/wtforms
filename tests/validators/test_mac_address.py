import pytest

from wtforms.validators import mac_address
from wtforms.validators import ValidationError


@pytest.mark.parametrize("mac_addr_val", ["01:23:45:67:ab:CD"])
def test_valid_mac_passes(mac_addr_val, dummy_form, dummy_field):
    """
    Valid MAC address should pass without raising
    """
    validator = mac_address()
    dummy_field.data = mac_addr_val
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "mac_addr_val",
    ["00:00:00:00:00", "01:23:45:67:89:", "01:23:45:67:89:gh", "123:23:45:67:89:00"],
)
def test_bad_mac_raises(mac_addr_val, dummy_form, dummy_field):
    """
    Bad MAC address should raise ValidatioError
    """
    validator = mac_address()
    dummy_field.data = mac_addr_val
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)
