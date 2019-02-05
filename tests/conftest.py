# pylint: disable=redefined-outer-name

import pytest


@pytest.fixture
def amocker():
    import asynctest
    return asynctest


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
def bot_repo_mock(amocker):
    from app import repositories
    return amocker.MagicMock(spec=repositories.BotRepository)


@pytest.fixture
def chat_repo_mock(amocker):
    from app import repositories
    repo = amocker.MagicMock(spec=repositories.ChatRepository)
    repo.list = amocker.CoroutineMock(return_value=[])
    return repo


@pytest.fixture
def property_repo_mock(amocker):
    from app import repositories
    repo = amocker.MagicMock(spec=repositories.PropertyRepository)
    return repo


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
def fake_bot_token():
    return '123456789:ABC0D12efGHi3J4klMNOP5QRstUvWxYZabC'


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
    from app import adapters
    bot_adapter = amocker.Mock(spec=adapters.BotAdapter)
    return bot_adapter


@pytest.fixture
def send_service(bot_repo_mock, chat_repo_mock, property_repo_mock):
    from app import services
    return services.SendService(
        bot_repo=bot_repo_mock, chat_repo=chat_repo_mock, property_repo=property_repo_mock
    )


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
def bazaraki_yesterday_date_item(bazaraki_soup):
    return bazaraki_soup.find_all('li', class_='announcement-container')[-2]


@pytest.fixture
def bot_service(chat_repo_mock):
    from app import services
    return services.BotService(chat_repo=chat_repo_mock)


@pytest.fixture
def bot_service_mock(amocker):
    from app import services
    return amocker.Mock(spec=services.BotService)


@pytest.fixture
def rentbot(amocker, fake_bot_token, bot_service_mock):
    import aiogram
    from app import bot
    bot_mock = amocker.CoroutineMock(spec=aiogram.Bot)
    dp_mock = amocker.CoroutineMock(spec=aiogram.Dispatcher)
    with amocker.patch('aiogram.Bot', return_value=bot_mock):
        with amocker.patch('aiogram.Dispatcher', return_value=dp_mock):
            return bot.Bot(fake_bot_token, bot_service=bot_service_mock)


@pytest.fixture
def rentbot_mock(amocker):
    from app import bot
    return amocker.Mock(spec=bot.Bot)


@pytest.fixture
def conf_mock(amocker, fake_bot_token):
    return amocker.Mock(bot_token=fake_bot_token, database=':memory:')


@pytest.fixture
def async_gen_mock():
    def wrapper(return_value):
        async def async_gen(*args, **kwargs):
            del args, kwargs
            yield return_value
        return async_gen
    return wrapper


@pytest.fixture
async def application(event_loop, amocker, request):
    from app import executor
    gfv = request.getfixturevalue
    with amocker.patch('app.config.Config', return_value=gfv('conf_mock')):
        with amocker.patch('app.adapters.SqliteDBAdapter', return_value=gfv('db_adapter_mock')):
            with amocker.patch('app.adapters.BotAdapter', return_value=gfv('bot_adapter_mock')):
                with amocker.patch('app.client.Client', return_value=gfv('client_mock')):
                    with amocker.patch('app.bot.Bot', return_value=gfv('rentbot_mock')):
                        application = executor.Application(loop=event_loop)
                        yield application
                        await application.shutdown()


@pytest.fixture
def application_mock(amocker):
    from app import executor
    return amocker.Mock(spec=executor.Application)
