import asyncio
import dataclasses
import itertools
from typing import AsyncGenerator, List

from . import datatypes, entities, protocols
from . import providers as providers_module


@dataclasses.dataclass
class SendService:
    bot_adapter: protocols.BotAdapter
    db_adapter: protocols.DBAdapter
    providers: List[providers_module.Provider]

    async def start_sending(self) -> None:
        async for update in self.get_updates(interval=2):
            chats = await self.db_adapter.select_chats(interested_in_price=update.price)
            text = f'[{update.title} €{update.price}]({update.telegram_link})'
            await self.bot_adapter.broadcast(chats=chats, text=text)

    async def get_updates(self, interval: float) -> AsyncGenerator[entities.Property, None]:
        while True:
            futures = [provider.get_updates() for provider in self.providers]
            result = await asyncio.gather(*futures)
            properties = itertools.chain.from_iterable(result)
            for real_property in properties:
                yield real_property
            await asyncio.sleep(interval)


@dataclasses.dataclass
class ChatService:
    db_adapter: protocols.DBAdapter

    async def get_or_create(self, chat_id: int) -> entities.Chat:
        chat = await self.db_adapter.get_chat(chat_id)
        if not chat:
            chat = await self.db_adapter.create_chat(chat_id)
        return chat

    async def set_min_price(self, chat_id: int, price: datatypes.Price) -> None:
        chat = await self.get_or_create(chat_id)
        if chat.max_price and chat.max_price < price:
            raise ValueError('Min price must be lesser than max price')
        chat.min_price = price
        await self.db_adapter.update_chat(chat)

    async def set_max_price(self, chat_id: int, price: datatypes.Price) -> None:
        chat = await self.get_or_create(chat_id)
        if chat.min_price and chat.min_price > price:
            raise ValueError('Max price must be greater than min price')
        chat.max_price = price
        await self.db_adapter.update_chat(chat)
