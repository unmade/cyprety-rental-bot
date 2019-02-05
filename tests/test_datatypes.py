import pytest

from app import datatypes


def test_price():
    price = datatypes.Price()
    assert price == 0


def test_negative_price():
    with pytest.raises(ValueError):
        datatypes.Price('-1')


@pytest.mark.parametrize(['given', 'expected'], [
    (None, None),
    (700.0, datatypes.Price('700.0'))
])
def test_price_from_optional(given, expected):
    assert datatypes.Price.from_optional(given) == expected
