import asyncio
import contextlib
from typing import Iterable, List, Mapping, Optional

import aiogram
import aiosqlite

from . import datatypes, entities


class SqliteDBAdapter:

    def __init__(self, database: str):
        self.database = database
        self.connect: Optional[aiosqlite.Connection] = None

    async def get_connection(self) -> aiosqlite.Connection:
        if self.connect is None:
            self.connect = aiosqlite.connect(self.database)
            await self.connect.__aenter__()
            self.connect.row_factory = aiosqlite.Row
        return self.connect

    async def close(self) -> None:
        if self.connect is not None:
            await self.connect.__aexit__(exc_type=None, exc_val=None, exc_tb=None)
            self.connect = None

    @contextlib.asynccontextmanager
    async def execute(
            self, statement: str, values: Optional[Iterable] = None, commit: bool = False
    ) -> aiosqlite.Cursor:
        connect = await self.get_connection()
        async with connect.execute(statement, values) as cursor:
            try:
                yield cursor
            finally:
                if commit:
                    await connect.commit()

    @classmethod
    def row_to_chat(cls, row: Mapping) -> entities.Chat:
        return entities.Chat(
            id=row['id'],
            min_price=datatypes.Price.from_optional(row['min_price']),
            max_price=datatypes.Price.from_optional(row['max_price']),
        )

    async def create_tables(self) -> None:
        statement = '''
            CREATE TABLE IF NOT EXISTS chat (
                id INTEGER PRIMARY KEY,
                min_price NUMERIC NULL CHECK(min_price > 0),
                max_price NUMERIC NULL CHECK(max_price > 0)
            )
        '''
        async with self.execute(statement, commit=True):
            return None

    async def select_chats(self, interested_in_price: datatypes.Price) -> List[entities.Chat]:
        statement = '''
            SELECT id, min_price, max_price FROM chat
            WHERE
              (min_price <= ? OR min_price is NULL) AND
              (? <= max_price OR max_price is NULL)
        '''
        values = (float(interested_in_price), float(interested_in_price))
        async with self.execute(statement, values) as cursor:
            rows = await cursor.fetchall()
            return [self.row_to_chat(row) for row in rows]

    async def create_chat(self, chat_id: int) -> entities.Chat:
        statement = 'INSERT INTO chat (id) VALUES (?)'
        values = (chat_id, )
        async with self.execute(statement, values, commit=True):
            return entities.Chat(id=chat_id)

    async def get_chat(self, chat_id: int) -> Optional[entities.Chat]:
        statement = 'SELECT id, min_price, max_price FROM chat WHERE id = ?'
        values = (chat_id, )
        async with self.execute(statement, values) as cursor:
            row = await cursor.fetchone()
            if row:
                return self.row_to_chat(row)
        return None

    async def update_chat(self, chat: entities.Chat) -> None:
        statement = 'UPDATE chat SET min_price = ?, max_price = ? WHERE id = ?'
        _min_price = float(chat.min_price) if chat.min_price else None
        _max_price = float(chat.max_price) if chat.max_price else None
        values = (_min_price, _max_price, chat.id)
        async with self.execute(statement, values, commit=True):
            return None


class BotAdapter:

    def __init__(self, token: str):
        self.bot = aiogram.Bot(token)
        self.dp = aiogram.Dispatcher(self.bot)

    async def close(self) -> None:
        await self.bot.close()

    async def broadcast(self, chats: List[entities.Chat], text: str) -> None:
        for chat in chats:
            try:
                await self.bot.send_message(chat.id, text=text, parse_mode='Markdown')
            except aiogram.exceptions.BotBlocked:
                pass
            await asyncio.sleep(.05)  # 20 messages per second
