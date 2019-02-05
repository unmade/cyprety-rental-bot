import asyncio
from typing import List

from . import adapters, bot, client, config, providers, registry, repositories, services


def run():
    loop = asyncio.get_event_loop()
    application = Application(loop)

    try:
        loop.run_until_complete(application.init())
        application.run()
    finally:
        loop.run_until_complete(application.shutdown())


class Application:

    def __init__(self, loop: asyncio.AbstractEventLoop):
        conf = config.Config()
        self.loop = loop

        self.bot_adapter = adapters.BotAdapter(token=conf.bot_token, loop=loop)
        self.db_adapter = adapters.SqliteDBAdapter(conf.database, loop=loop)
        self.webclient = client.Client(loop=loop)

        property_repo = repositories.PropertyRepository(providers=self.provider_list)
        bot_repo = repositories.BotRepository(bot_adapter=self.bot_adapter)
        chat_repo = repositories.ChatRepository(db_adapter=self.db_adapter)

        self.send_service = services.SendService(
            bot_repo=bot_repo, chat_repo=chat_repo, property_repo=property_repo,
        )

        bot_service = services.BotService(chat_repo=chat_repo)
        self.bot = bot.Bot(conf.bot_token, bot_service=bot_service)

    @property
    def provider_list(self) -> List[providers.Provider]:
        return [
            providers.Provider(url, parser=parser_class(), webclient=self.webclient)
            for url, parser_class in registry.list_parsers().items()
        ]

    async def init(self) -> None:
        await self.db_adapter.create_tables()

    async def shutdown(self) -> None:
        await self.db_adapter.close()
        await self.bot_adapter.close()
        await self.webclient.close()

    def run(self) -> None:
        self.loop.create_task(self.send_service.start_sending())
        self.bot.start_polling(loop=self.loop)
