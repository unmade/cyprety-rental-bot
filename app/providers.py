import calendar
import datetime
from typing import List

from . import client, entities, parsers


class Provider:

    def __init__(self, url: str, parser: parsers.Parser, webclient: client.Client):
        self.client = webclient
        self.url = url
        self.parser = parser
        self.latest_created_at: float = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
        self.recently_seen: List[str] = []

    async def get_updates(self) -> List[entities.Property]:
        content = await self.client.get(self.url)
        properties = self.parser.parse(content)
        properties = [p for p in properties if p.created_at > self.latest_created_at]
        properties = [p for p in properties if p.url not in self.recently_seen]
        if properties:
            self.latest_created_at = max(p.created_at for p in properties)
            self.recently_seen = ([p.url for p in properties] + self.recently_seen)[:10]
        return properties
