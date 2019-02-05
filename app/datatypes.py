import decimal
from typing import Optional, Union


class Price(decimal.Decimal):

    def __new__(cls, value: Union[str, int, decimal.Decimal] = "0"):
        self = super().__new__(cls, value)
        if self < 0:
            raise ValueError('Price cannot be negative')
        return self

    @classmethod
    def from_optional(cls, value: Optional[decimal.Decimal]) -> Optional['Price']:
        if not value:
            return None
        return cls(value)
