import asyncio
from typing import Awaitable, Callable

import aiogram

from . import services

Handler = Callable[[int, str], Awaitable[str]]


class Bot:

    def __init__(self, token: str, bot_service: services.BotService):
        self.bot = aiogram.Bot(token)
        self.dp = aiogram.Dispatcher(self.bot)

        self.register_command_handler('start', bot_service.welcome)
        self.register_command_handler('set_min_price', bot_service.set_min_price)
        self.register_command_handler('set_max_price', bot_service.set_max_price)

    def register_command_handler(self, command: str, handler: Handler) -> None:
        async def wrapper(message: aiogram.types.Message) -> None:
            text = message.get_args() or ''
            response = await handler(message.chat.id, text)
            await message.reply(response, reply=False)
        self.dp.register_message_handler(wrapper, commands=[command])

    def start_polling(self, loop: asyncio.AbstractEventLoop) -> None:
        aiogram.executor.start_polling(self.dp, skip_updates=True, loop=loop)
