import asyncio
import itertools
from typing import AsyncGenerator, Awaitable, Callable, List

from . import adapters, datatypes, entities, protocols
from . import providers as providers_module

Handler = Callable[[int, str], Awaitable[str]]


class BotRepository:

    def __init__(self, bot_adapter: adapters.BotAdapter):
        self.bot_adapter = bot_adapter

    async def broadcast(self, chats: List[entities.Chat], text: str) -> None:
        for chat in chats:
            await self.bot_adapter.send_message(chat.id, text=text)
            await asyncio.sleep(.05)  # 20 messages per second


class PropertyRepository:

    def __init__(self, providers: List[providers_module.Provider]):
        self.providers = providers

    async def get_updates(self, interval: float) -> AsyncGenerator[entities.Property, None]:
        while True:
            futures = [provider.get_updates() for provider in self.providers]
            result = await asyncio.gather(*futures)
            properties = itertools.chain.from_iterable(result)
            for real_property in properties:
                yield real_property
            await asyncio.sleep(interval)


class ChatRepository:

    def __init__(self, db_adapter: protocols.DBAdapter):
        self.db_adapter = db_adapter

    async def list(self, with_price: datatypes.Price) -> List[entities.Chat]:
        return await self.db_adapter.select_chats(interested_in_price=with_price)

    async def get_or_create(self, chat_id: int) -> entities.Chat:
        chat = await self.db_adapter.get_chat(chat_id)
        if not chat:
            chat = await self.db_adapter.create_chat(chat_id)
        return chat

    async def update(self, chat: entities.Chat) -> None:
        await self.db_adapter.update_chat(chat)
