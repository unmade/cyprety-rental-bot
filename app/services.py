from . import datatypes, repositories


class SendService:

    def __init__(
            self,
            bot_repo: repositories.BotRepository,
            property_repo: repositories.PropertyRepository,
            chat_repo: repositories.ChatRepository,
    ):
        self.bot_repo = bot_repo
        self.property_repo = property_repo
        self.chat_repo = chat_repo

    async def start_sending(self) -> None:
        async for real_property in self.property_repo.get_updates(interval=2):
            chats = await self.chat_repo.list(with_price=real_property.price)
            text = f'[{real_property.title} €{real_property.price}]({real_property.telegram_link})'
            await self.bot_repo.broadcast(chats=chats, text=text)


class BotService:

    def __init__(self, chat_repo: repositories.ChatRepository):
        self.chat_repo = chat_repo

    async def welcome(self, chat_id: int, text: str) -> str:
        del text
        await self.chat_repo.get_or_create(chat_id)
        return (
            'I can notify you about new advertisements '
            'for houses & apartments to rent in Limassol district.\n\n'

            'You can set price range using these commands:\n\n'

            '/set_min_price - sets minimum shown price\n'
            '/set_max_price - sets maximum shown price'
        )

    async def set_min_price(self, chat_id: int, text: str) -> str:
        try:
            min_price = datatypes.Price(text)
        except (ArithmeticError, ValueError):
            return 'Please use numbers to set the price. For example: 700.0'

        chat = await self.chat_repo.get_or_create(chat_id)
        if chat.max_price and chat.max_price < min_price:
            return 'Min price must be lesser than max price'

        chat.min_price = min_price
        await self.chat_repo.update(chat)
        return f'Minimum shown price is set to €{chat.min_price}'

    async def set_max_price(self, chat_id: int, text: str) -> str:
        try:
            max_price = datatypes.Price(text)
        except (ArithmeticError, ValueError):
            return 'Please use numbers to set the price. For example: 700.0'

        chat = await self.chat_repo.get_or_create(chat_id)
        if chat.min_price and chat.min_price > max_price:
            return 'Max price must be greater than min price'

        chat.max_price = max_price
        await self.chat_repo.update(chat)
        return f'Maximum shown price is set to €{chat.max_price}'
