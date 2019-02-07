import aiogram
from aiogram.contrib.fsm_storage import memory
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state as fsm
from aiogram.types import Message

from . import datatypes, services


class PriceState(fsm.StatesGroup):
    wait_for_min_price = fsm.State()
    wait_for_max_price = fsm.State()


class TelegramBot:

    def __init__(self, token: str, chat_service: services.ChatService):
        self.bot = aiogram.Bot(token)
        self.dp = aiogram.Dispatcher(self.bot, storage=memory.MemoryStorage())
        self.chat_service = chat_service

        self.dp.register_message_handler(self.welcome, commands=['start'])
        self.dp.register_message_handler(self.start_set_min_price, commands=['set_min_price'])
        self.dp.register_message_handler(self.set_min_price, state=PriceState.wait_for_min_price)
        self.dp.register_message_handler(self.start_set_max_price, commands=['set_max_price'])
        self.dp.register_message_handler(self.set_max_price, state=PriceState.wait_for_max_price)

    def start_polling(self) -> None:
        aiogram.executor.start_polling(self.dp, skip_updates=True)

    async def welcome(self, message: Message) -> None:
        await self.chat_service.get_or_create(message.chat.id)
        await message.reply(
            (
                'I can notify you about new advertisements '
                'for houses & apartments to rent in Limassol district.\n\n'

                'You can set price range using these commands:\n\n'

                '/set_min_price - sets minimum shown price\n'
                '/set_max_price - sets maximum shown price'
            ),
            reply=False
        )

    @staticmethod
    async def start_set_min_price(message: Message) -> None:
        await PriceState.wait_for_min_price.set()
        await message.reply('Enter preferable minimum price:', reply=False)

    async def set_min_price(self, message: Message, state: FSMContext) -> None:
        try:
            price = datatypes.Price(message.text)
        except (ArithmeticError, ValueError, TypeError):
            text = 'Please use numbers to set the price. For example: 700.0'
            await message.reply(text, reply=False)
            return None

        try:
            await self.chat_service.set_min_price(message.chat.id, price=price)
        except ValueError as error:
            await message.reply(f'{error}', reply=False)
            return None

        async with state.proxy() as data:
            await message.reply(f'Minimum shown price is set to €{price}', reply=False)
            data.state = None

    @staticmethod
    async def start_set_max_price(message: Message) -> None:
        await PriceState.wait_for_max_price.set()
        await message.reply('Enter preferable maximum price:', reply=False)

    async def set_max_price(self, message: Message, state: FSMContext) -> None:
        try:
            price = datatypes.Price(message.text)
        except (ArithmeticError, ValueError, TypeError):
            text = 'Please use numbers to set the price. For example: 700.0'
            await message.reply(text, reply=False)
            return None

        try:
            await self.chat_service.set_max_price(message.chat.id, price=price)
        except ValueError as error:
            await message.reply(f'{error}', reply=False)
            return None

        async with state.proxy() as data:
            await message.reply(f'Maximum shown price is set to €{price}', reply=False)
            data.state = None
