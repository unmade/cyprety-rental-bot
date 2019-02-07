import calendar
import datetime
import urllib.parse
from typing import List

import bs4
import pytz

from . import datatypes, entities, registry

BAZARAKI_BASE_URL = 'https://www.bazaraki.com'
BAZARAKI_URL = f'{BAZARAKI_BASE_URL}/real-estate/houses-and-villas-rent/lemesos-district-limassol/'


class Parser:

    def get_base_url(self) -> str:
        raise NotImplementedError('`get_base_url` must be implemented')

    def get_items(self, soup: bs4.BeautifulSoup) -> List[bs4.element.Tag]:
        raise NotImplementedError('`get_items()` must be implemented.')

    def get_item_title(self, item: bs4.element.Tag) -> str:
        raise NotImplementedError('`get_item_title()` must be implemented.')

    def get_item_price(self, item: bs4.element.Tag) -> datatypes.Price:
        raise NotImplementedError('`get_item_price()` must be implemented.')

    def get_item_url(self, item: bs4.element.Tag) -> str:
        raise NotImplementedError('`get_item_url()` must be implemented.')

    def get_item_created_at(self, item: bs4.element.Tag) -> float:
        raise NotImplementedError('`get_item_created_at()` must be implemented.')

    def build_absolute_url(self, url: str) -> str:
        base_url = self.get_base_url()
        return urllib.parse.urljoin(base_url, url)

    def build_property(self, item: bs4.element.Tag) -> entities.Property:
        return entities.Property(
            title=self.get_item_title(item),
            url=self.build_absolute_url(self.get_item_url(item)),
            price=self.get_item_price(item),
            created_at=self.get_item_created_at(item),
        )

    def parse(self, content: str) -> List[entities.Property]:
        soup = bs4.BeautifulSoup(content, 'html.parser')
        items = self.get_items(soup)
        return [self.build_property(item) for item in items]


@registry.add_parser(BAZARAKI_URL)
class BazarakiParser(Parser):
    TZ = pytz.timezone('Asia/Nicosia')

    def get_base_url(self) -> str:
        return BAZARAKI_BASE_URL

    def get_items(self, soup: bs4.BeautifulSoup) -> List[bs4.element.Tag]:
        items: List[bs4.element.Tag] = soup.find_all('li', class_='announcement-container')
        return items

    def get_item_title(self, item: bs4.element.Tag) -> str:
        title: str = item.find('a', class_='announcement-block__title').string.strip()
        return title

    def get_item_price(self, item: bs4.element.Tag) -> datatypes.Price:
        price_block = item.find('div', class_='announcement-block__price')
        price_tag = price_block.find('meta', attrs={'itemprop': 'price'})
        price = price_tag.attrs['content']
        return datatypes.Price(price)

    def get_item_url(self, item: bs4.element.Tag) -> str:
        url: str = item.find('a', class_='announcement-block__title').attrs['href']
        return url

    def get_item_created_at(self, item: bs4.element.Tag) -> float:
        dt_block = item.find('div', class_='announcement-block__date')
        dt_text = dt_block.string.partition(',')[0].strip()
        now = datetime.datetime.now(tz=self.TZ)
        if 'Today' in dt_text:
            today_str = now.strftime('%d.%m.%Y')
            dt_text = dt_text.replace('Today', today_str)
        if 'Yesterday' in dt_text:
            yesterday_dt = now.date() - datetime.timedelta(days=1)
            dt_text = dt_text.replace('Yesterday', yesterday_dt.strftime('%d.%m.%Y'))
        local_dt = datetime.datetime.strptime(dt_text, '%d.%m.%Y %H:%M')
        dt = self.TZ.normalize(self.TZ.localize(local_dt, is_dst=True))
        if dt > now:
            # some strange bug occurs at midnight: record has `Today` but it is tomorrow already
            dt -= datetime.timedelta(days=1)
        return calendar.timegm(dt.utctimetuple())
