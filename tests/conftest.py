# pylint: disable=redefined-outer-name

import pytest


@pytest.fixture
def amocker():
    import asynctest
    return asynctest


@pytest.fixture
def fake_bot_token():
    return '123456789:ABC0D12efGHi3J4klMNOP5QRstUvWxYZabC'


@pytest.fixture
def conf_mock(amocker, fake_bot_token):
    return amocker.Mock(bot_token=fake_bot_token, database=':memory:')


@pytest.fixture
def property_factory(faker):
    def wrapper(**kwargs):
        from app import datatypes, entities
        defaults = {
            'title': faker.sentence(),
            'price': datatypes.Price(faker.pydecimal(positive=True)),
            'url': faker.url(),
            'created_at': faker.unix_time(),
        }
        defaults.update(kwargs)
        return entities.Property(**defaults)
    return wrapper


@pytest.fixture
def chat_factory(faker):
    def wrapper(**kwargs):
        from app import entities
        defaults = {
            'id': faker.pyint(),
        }
        defaults.update(kwargs)
        return entities.Chat(**defaults)
    return wrapper


@pytest.fixture
def parser_mock(amocker):
    from app import parsers
    parser = amocker.Mock(spec=parsers.Parser)
    return parser


@pytest.fixture
def client_mock(amocker):
    from app import client
    webclient = amocker.Mock(spec=client.Client)
    return webclient


@pytest.fixture
async def sqlite_db_adapter():
    from app import adapters
    db_adapter = adapters.SqliteDBAdapter(':memory:')
    await db_adapter.create_tables()
    yield db_adapter
    await db_adapter.close()


@pytest.fixture
def db_adapter_mock(amocker):
    from app import protocols
    db_adapter = amocker.Mock(spec=protocols.DBAdapter)
    return db_adapter


@pytest.fixture
async def bot_adapter(amocker, fake_bot_token):
    import aiogram
    from app import adapters
    bot_mock = amocker.CoroutineMock(spec=aiogram.Bot)
    dp_mock = amocker.CoroutineMock(spec=aiogram.Dispatcher)
    with amocker.patch('aiogram.Bot', return_value=bot_mock):
        with amocker.patch('aiogram.Dispatcher', return_value=dp_mock):
            return adapters.BotAdapter(fake_bot_token)


@pytest.fixture
def bot_adapter_mock(amocker):
    from app import protocols
    bot_adapter = amocker.Mock(spec=protocols.BotAdapter)
    return bot_adapter


@pytest.fixture
def send_service(amocker, bot_adapter_mock, db_adapter_mock):
    from app import services
    db_adapter_mock.select_chats = amocker.CoroutineMock(return_value=[])
    return services.SendService(
        bot_adapter=bot_adapter_mock,
        db_adapter=db_adapter_mock,
        providers=[],
    )


@pytest.fixture
def async_gen_mock():
    def wrapper(return_value):
        async def async_gen(*args, **kwargs):
            del args, kwargs
            yield return_value
        return async_gen
    return wrapper


@pytest.fixture
def chat_service(db_adapter_mock):
    from app import services
    return services.ChatService(db_adapter=db_adapter_mock)


@pytest.fixture
def chat_service_mock(amocker):
    from app import services
    service = amocker.Mock(spec=services.ChatService)
    service.list = amocker.CoroutineMock(return_value=[])
    return service


@pytest.fixture
def telegram_bot(amocker, chat_service_mock):
    import aiogram
    from app import bots
    bot_mock = amocker.CoroutineMock(spec=aiogram.Bot)
    dp_mock = amocker.CoroutineMock(spec=aiogram.Dispatcher)
    with amocker.patch('aiogram.Bot', return_value=bot_mock):
        with amocker.patch('aiogram.Dispatcher', return_value=dp_mock):
            return bots.TelegramBot(fake_bot_token, chat_service=chat_service_mock)


@pytest.fixture
def telegram_bot_mock(amocker):
    from app import bots
    return amocker.Mock(spec=bots.TelegramBot)


@pytest.fixture
async def application(amocker, request):
    from app import executor
    gfv = request.getfixturevalue
    with amocker.patch('app.config.Config', return_value=gfv('conf_mock')):
        with amocker.patch('app.adapters.SqliteDBAdapter', return_value=gfv('db_adapter_mock')):
            with amocker.patch('app.adapters.BotAdapter', return_value=gfv('bot_adapter_mock')):
                with amocker.patch('app.bots.TelegramBot', return_value=gfv('telegram_bot_mock')):
                    with amocker.patch('app.client.Client', return_value=gfv('client_mock')):
                        application = executor.Application()
                        yield application
                        await application.shutdown()


@pytest.fixture
def application_mock(amocker):
    from app import executor
    return amocker.Mock(spec=executor.Application)


@pytest.fixture(scope='session')
def bazaraki_soup():
    import bs4
    from importlib import resources
    content = resources.read_text('tests.data', 'bazaraki_list.html')
    return bs4.BeautifulSoup(content, 'html.parser')


@pytest.fixture
def bazaraki_item(bazaraki_soup):
    return bazaraki_soup.find_all('li', class_='announcement-container')[0]


@pytest.fixture
def bazaraki_full_date_item(bazaraki_soup):
    return bazaraki_soup.find_all('li', class_='announcement-container')[-1]


@pytest.fixture
def bazaraki_today_date_item(bazaraki_soup):
    return bazaraki_soup.find_all('li', class_='announcement-container')[0]


@pytest.fixture
def bazaraki_end_of_today_date_item(bazaraki_soup):
    return bazaraki_soup.find_all('li', class_='announcement-container')[1]


@pytest.fixture
def bazaraki_yesterday_date_item(bazaraki_soup):
    return bazaraki_soup.find_all('li', class_='announcement-container')[-2]
