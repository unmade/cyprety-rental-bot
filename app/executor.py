import asyncio
from typing import List

import sentry_sdk

from . import adapters, bots, client, config, providers, registry, services


def run():
    loop = asyncio.get_event_loop()
    application = Application()

    try:
        loop.run_until_complete(application.init())
        application.run(loop)
    finally:
        loop.run_until_complete(application.shutdown())


class Application:

    def __init__(self):
        self.conf = config.Config()

        self.bot_adapter = adapters.BotAdapter(token=self.conf.bot_token)
        self.db_adapter = adapters.SqliteDBAdapter(self.conf.database)
        self.webclient = client.Client()

        self.send_service = services.SendService(
            bot_adapter=self.bot_adapter, db_adapter=self.db_adapter, providers=self.provider_list
        )

        chat_service = services.ChatService(db_adapter=self.db_adapter)
        self.bot = bots.TelegramBot(self.conf.bot_token, chat_service=chat_service)

    @property
    def provider_list(self) -> List[providers.Provider]:
        return [
            providers.Provider(url, parser=parser_class(), webclient=self.webclient)
            for url, parser_class in registry.list_parsers().items()
        ]

    async def init(self) -> None:
        await self.db_adapter.create_tables()
        if self.conf.sentry_dsn:
            sentry_sdk.init(self.conf.sentry_dsn, release=self.conf.sentry_release_version)

    def run(self, loop: asyncio.AbstractEventLoop) -> None:
        loop.create_task(self.send_service.start_sending())
        self.bot.start_polling()

    async def shutdown(self) -> None:
        await self.db_adapter.close()
        await self.bot_adapter.close()
        await self.webclient.close()
