# pylint: skip-file

from typing import List, Optional

from typing_extensions import Protocol

from . import datatypes, entities


class DBAdapter(Protocol):

    async def close(self) -> None: ...

    async def create_tables(self) -> None: ...

    async def select_chats(self, interested_in_price: datatypes.Price) -> List[entities.Chat]: ...

    async def create_chat(self, chat_id: int) -> entities.Chat: ...

    async def get_chat(self, chat_id: int) -> Optional[entities.Chat]: ...

    async def update_chat(self, chat: entities.Chat) -> None: ...


class BotAdapter(Protocol):

    async def close(self) -> None: ...

    async def broadcast(self, chats: List[entities.Chat], text: str) -> None: ...
