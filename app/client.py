import ssl

import aiohttp
import certifi


class Client:

    def __init__(self):
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

    async def close(self) -> None:
        await self.session.close()

    async def get(self, url: str) -> str:
        async with self.session.get(url, ssl=self.ssl_context) as response:
            return await response.text()
