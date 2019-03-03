import dataclasses
from typing import Optional

from . import datatypes


@dataclasses.dataclass
class Chat:
    id: int
    min_price: Optional[datatypes.Price] = None
    max_price: Optional[datatypes.Price] = None


@dataclasses.dataclass
class Property:
    title: str
    price: datatypes.Price
    url: str
    created_at: float

    @property
    def telegram_link(self) -> str:
        return f'https://t.me/iv?url={self.url}/&rhash=7849b4bb7a02f2'
