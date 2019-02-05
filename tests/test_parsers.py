import calendar
import datetime

import pytest
import pytz

from app import datatypes, parsers


def test_parser_parse(amocker, property_factory):
    parsed_property = property_factory()
    tag = amocker.Mock()

    parser = parsers.Parser()
    parser.get_items = amocker.Mock(return_value=[tag])
    parser.build_property = amocker.Mock(return_value=parsed_property)

    assert parser.parse('') == [parsed_property]
    assert parser.get_items.called
    assert parser.build_property.called


def test_parser_get_base_url_raises_not_implemented():
    parser = parsers.Parser()

    with pytest.raises(NotImplementedError):
        parser.get_base_url()


def test_parser_get_items_raises_not_implemented(amocker):
    parser = parsers.Parser()

    with pytest.raises(NotImplementedError):
        soup = amocker.Mock()
        parser.get_items(soup)


def test_parser_get_item_title_raises_not_implemented(amocker):
    parser = parsers.Parser()

    with pytest.raises(NotImplementedError):
        item = amocker.Mock()
        parser.get_item_title(item)


def test_parser_get_item_price_raises_not_implemented(amocker):
    parser = parsers.Parser()

    with pytest.raises(NotImplementedError):
        item = amocker.Mock()
        parser.get_item_price(item)


def test_parser_get_item_url_raises_not_implemented(amocker):
    parser = parsers.Parser()

    with pytest.raises(NotImplementedError):
        item = amocker.Mock()
        parser.get_item_url(item)


def test_parser_get_item_created_at_raises_not_implemented(amocker):
    parser = parsers.Parser()

    with pytest.raises(NotImplementedError):
        item = amocker.Mock()
        parser.get_item_created_at(item)


def test_parser_build_property(amocker, property_factory):
    item = amocker.Mock()
    expected_property = property_factory()

    parser = parsers.Parser()
    parser.get_item_title = amocker.Mock(return_value=expected_property.title)
    parser.get_item_url = amocker.Mock(return_value=expected_property.url)
    parser.get_item_price = amocker.Mock(return_value=expected_property.price)
    parser.get_item_created_at = amocker.Mock(return_value=expected_property.created_at)
    parser.build_absolute_url = amocker.Mock(return_value=expected_property.url)

    assert parser.build_property(item) == expected_property
    assert parser.get_item_title.called
    assert parser.get_item_url.called
    assert parser.get_item_price.called
    assert parser.get_item_created_at.called
    assert parser.build_absolute_url.called


def test_parser_build_absolute_url(amocker):
    base_url = 'https://www.bazaraki.com'
    path = '/adv/2206100_panthea-near-grammar-school/'
    expected = f'{base_url}{path}'

    parser = parsers.Parser()
    parser.get_base_url = amocker.Mock(return_value=base_url)

    with amocker.patch('urllib.parse.urljoin', return_value=expected) as urljoin_mock:
        assert parser.build_absolute_url(path) == expected

    assert parser.get_base_url.called
    assert parser.get_base_url.call_args == amocker.call()
    assert urljoin_mock.called
    assert urljoin_mock.call_args == amocker.call(base_url, path)


def test_bazaraki_parser_get_base_url():
    parser = parsers.BazarakiParser()
    assert parser.get_base_url() == parsers.BAZARAKI_BASE_URL


def test_bazaraki_parser_get_items_calls_find_all(amocker):
    parser = parsers.BazarakiParser()
    soup = amocker.Mock()
    soup.find_all = amocker.Mock(return_value=[])
    assert parser.get_items(soup) == []
    assert soup.find_all.called
    assert soup.find_all.call_args == amocker.call('li', class_='announcement-container')


def test_bazaraki_parser_get_items(bazaraki_soup):
    parser = parsers.BazarakiParser()
    items = parser.get_items(bazaraki_soup)
    assert len(items) == 60


def test_bazaraki_parser_get_item_title(bazaraki_item):
    parser = parsers.BazarakiParser()
    assert parser.get_item_title(bazaraki_item) == 'Panthea near grammar school'


def test_bazaraki_parser_get_item_price(bazaraki_item):
    parser = parsers.BazarakiParser()
    assert parser.get_item_price(bazaraki_item) == datatypes.Price(3500)


def test_bazaraki_parser_get_item_url(bazaraki_item):
    parser = parsers.BazarakiParser()
    assert parser.get_item_url(bazaraki_item) == '/adv/2206100_panthea-near-grammar-school/'


def test_bazaraki_parser_get_item_created_at(bazaraki_full_date_item):
    parser = parsers.BazarakiParser()
    assert parser.get_item_created_at(bazaraki_full_date_item) == 1548675840.0


def test_bazaraki_parser_get_item_created_at_today_date(bazaraki_today_date_item):
    tz_info = pytz.timezone('Asia/Nicosia')
    parser = parsers.BazarakiParser()
    today = datetime.datetime.now(tz=tz_info)
    today_local_dt = datetime.datetime(today.year, today.month, today.day, 13, 44)
    today_dt = tz_info.normalize(tz_info.localize(today_local_dt, is_dst=True))
    today_ts = calendar.timegm(today_dt.utctimetuple())
    assert parser.get_item_created_at(bazaraki_today_date_item) == today_ts


def test_bazaraki_parser_get_item_created_at_yesterday_date(bazaraki_yesterday_date_item):
    tz_info = pytz.timezone('Asia/Nicosia')
    parser = parsers.BazarakiParser()
    today = datetime.datetime.now(tz=tz_info)
    today_dt = datetime.datetime(today.year, today.month, today.day, 23, 4)
    yesterday_local_dt = today_dt - datetime.timedelta(days=1)
    yesterday_dt = tz_info.normalize(tz_info.localize(yesterday_local_dt, is_dst=True))
    yesterday_ts = calendar.timegm(yesterday_dt.utctimetuple())
    assert parser.get_item_created_at(bazaraki_yesterday_date_item) == yesterday_ts
