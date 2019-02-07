import aiosqlite
import pytest

from app import adapters, datatypes, entities


@pytest.mark.asyncio
async def test_sqlite_db_adapter_close_without_opening_connection(amocker):
    db_adapter = adapters.SqliteDBAdapter(':memory:')
    with amocker.patch('aiosqlite.Connection.__aexit__') as close_mock:
        await db_adapter.close()
    assert close_mock.called is False


@pytest.mark.asyncio
async def test_sqlite_db_adapter_close(amocker):
    db_adapter = adapters.SqliteDBAdapter(':memory:')
    connect = amocker.CoroutineMock(__aexit__=amocker.CoroutineMock())
    db_adapter.connect = connect

    await db_adapter.close()

    assert db_adapter.connect is None
    assert connect.__aexit__.called


@pytest.mark.asyncio
async def test_get_connection(amocker):
    db_adapter = adapters.SqliteDBAdapter(':memory:')
    connection_mock = amocker.MagicMock(spec=aiosqlite.Connection)
    with amocker.patch('aiosqlite.connect', return_value=connection_mock) as connect_mock:
        connection = await db_adapter.get_connection()

    assert connection == connection_mock
    assert connect_mock.called


@pytest.mark.asyncio
async def test_get_connection_returns_already_initialized_one(amocker):
    connection_mock = amocker.MagicMock(spec=aiosqlite.Connection)
    db_adapter = adapters.SqliteDBAdapter(':memory:')
    db_adapter.connect = connection_mock

    with amocker.patch('aiosqlite.connect') as connect_mock:
        connection = await db_adapter.get_connection()

    assert connection == connection_mock
    assert connect_mock.called is False


@pytest.mark.asyncio
async def test_sqlite_db_adapter_select_chats(sqlite_db_adapter: adapters.SqliteDBAdapter):
    price = datatypes.Price(700)

    await sqlite_db_adapter.connect.execute('''
        INSERT INTO
            chat (id, min_price, max_price)
        VALUES
            (1, 550.0, 700.0),
            (2, 700.0, 1000.0),
            (3, 400.0, 600.0),
            (4, 800.0, 1300.0),
            (5, null, 1000.0),
            (6, 550.0, null),
            (7, null, null)
    ''')

    chats = await sqlite_db_adapter.select_chats(interested_in_price=price)
    chat_id_list = [chat.id for chat in chats]
    assert chat_id_list == [1, 2, 5, 6, 7]


@pytest.mark.asyncio
async def test_sqlite_db_adapter_create_tables(sqlite_db_adapter: adapters.SqliteDBAdapter):
    assert await sqlite_db_adapter.create_tables() is None

    statement = 'SELECT * FROM chat'
    async with sqlite_db_adapter.connect.execute(statement) as cursor:
        assert await cursor.fetchall() == []


@pytest.mark.asyncio
async def test_sqlite_db_adapter_create_chat(sqlite_db_adapter: adapters.SqliteDBAdapter):
    chat_id = 1
    result = await sqlite_db_adapter.create_chat(chat_id=chat_id)
    assert result == entities.Chat(id=chat_id)

    statement = 'SELECT * FROM chat WHERE id=?'
    async with sqlite_db_adapter.connect.execute(statement, (chat_id, )) as cursor:
        row = await cursor.fetchone()
        assert row['id'] == chat_id


@pytest.mark.asyncio
async def test_sqlite_db_adapter_get_chat_return_chat(sqlite_db_adapter: adapters.SqliteDBAdapter):
    chat_id = 1
    statement = 'INSERT INTO chat (id) VALUES (?)'
    await sqlite_db_adapter.connect.execute(statement, (chat_id, ))

    chat = await sqlite_db_adapter.get_chat(chat_id=chat_id)
    assert chat.id == chat_id


@pytest.mark.asyncio
async def test_sqlite_db_adapter_get_chat_return_none(sqlite_db_adapter: adapters.SqliteDBAdapter):
    chat = await sqlite_db_adapter.get_chat(chat_id=1)
    assert chat is None


@pytest.mark.asyncio
async def test_sqlite_db_adapter_update_chat(
        chat_factory, sqlite_db_adapter: adapters.SqliteDBAdapter
):
    min_price = datatypes.Price(700)
    chat = chat_factory(min_price=min_price)
    await sqlite_db_adapter.create_chat(chat_id=chat.id)

    await sqlite_db_adapter.update_chat(chat)

    updated_chat = await sqlite_db_adapter.get_chat(chat_id=chat.id)
    assert updated_chat.min_price == min_price
    assert updated_chat.max_price is None


@pytest.mark.asyncio
async def test_sqlite_db_adapter_row_to_chat(
        chat_factory, sqlite_db_adapter: adapters.SqliteDBAdapter
):
    chat = chat_factory(max_price=datatypes.Price(700))
    row = {'id': chat.id, 'min_price': None, 'max_price': 700}
    assert sqlite_db_adapter.row_to_chat(row) == chat


@pytest.mark.asyncio
@pytest.mark.parametrize('committed', [False, True])
async def test_sqlite_db_adapter_execute(
        amocker, sqlite_db_adapter: adapters.SqliteDBAdapter, committed
):
    connect = amocker.CoroutineMock(spec=aiosqlite.Connection)
    sqlite_db_adapter.get_connection = amocker.CoroutineMock(return_value=connect)

    async with sqlite_db_adapter.execute('SELECT 1', commit=committed):
        pass

    assert connect.execute.called
    assert connect.commit.called is committed


def test_bot_adapter_init(bot_adapter: adapters.BotAdapter):
    import aiogram
    assert isinstance(bot_adapter.bot, aiogram.Bot)
    assert isinstance(bot_adapter.dp, aiogram.Dispatcher)


@pytest.mark.asyncio
async def test_bot_adapter_close(amocker, bot_adapter: adapters.BotAdapter):
    with amocker.patch.object(bot_adapter.bot, 'close') as close_mock:
        assert await bot_adapter.close() is None

    assert close_mock.called
    assert close_mock.call_args == amocker.call()


@pytest.mark.asyncio
async def test_bot_adapter_broadcast(chat_factory, bot_adapter: adapters.BotAdapter):
    chat = chat_factory()
    assert await bot_adapter.broadcast(chats=[chat], text='') is None
    assert bot_adapter.bot.send_message.called
