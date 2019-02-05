import asyncio
import ssl
from typing import Optional

import aiohttp
import certifi


class Client:

    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None):
        self.session: aiohttp.ClientSession = aiohttp.ClientSession(loop=loop)
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

    async def __aenter__(self) -> 'Client':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self.session.close()

    async def get(self, url: str) -> str:
        async with self.session.get(url, ssl=self.ssl_context) as response:
            return await response.text()
