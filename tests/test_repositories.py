import pytest

from app import datatypes, providers, repositories


@pytest.mark.asyncio
async def test_bot_repo_broadcast(bot_adapter_mock, chat_factory):
    chat = chat_factory()
    bot_repo = repositories.BotRepository(bot_adapter=bot_adapter_mock)
    assert await bot_repo.broadcast(chats=[chat], text='') is None
    assert bot_adapter_mock.send_message.called


def test_property_repo_init():
    property_repo = repositories.PropertyRepository(providers=[])
    assert property_repo.providers == []


@pytest.mark.asyncio
async def test_property_repo_get_updates(amocker, property_factory):
    expected_property = property_factory()
    provider = amocker.Mock(spec=providers.Provider)
    provider.get_updates = amocker.CoroutineMock(return_value=[expected_property])

    property_repo = repositories.PropertyRepository(providers=[provider])

    get_updates = property_repo.get_updates(interval=0.1)
    assert await get_updates.__anext__() == expected_property
    assert await get_updates.__anext__() == expected_property  # run second iteration


@pytest.mark.asyncio
async def test_chat_repo_list(chat_factory, db_adapter_mock):
    chat = chat_factory()
    db_adapter_mock.select_chats.return_value = [chat]
    chat_repo = repositories.ChatRepository(db_adapter=db_adapter_mock)
    price = datatypes.Price(700)

    assert await chat_repo.list(with_price=price) == [chat]

    assert db_adapter_mock.select_chats.called


@pytest.mark.asyncio
async def test_chat_repo_get_or_create_gets_chat(chat_factory, db_adapter_mock):
    chat = chat_factory()
    db_adapter_mock.get_chat.return_value = chat
    chat_repo = repositories.ChatRepository(db_adapter=db_adapter_mock)
    assert await chat_repo.get_or_create(chat_id=chat.id) == chat

    assert db_adapter_mock.get_chat.called
    assert not db_adapter_mock.create_chat.called


@pytest.mark.asyncio
async def test_chat_repo_get_or_create_creates_chat(chat_factory, db_adapter_mock):
    chat = chat_factory()
    db_adapter_mock.get_chat.return_value = None
    db_adapter_mock.create_chat.return_value = chat
    chat_repo = repositories.ChatRepository(db_adapter=db_adapter_mock)
    assert await chat_repo.get_or_create(chat_id=chat.id) == chat

    assert db_adapter_mock.get_chat.called
    assert db_adapter_mock.create_chat.called


@pytest.mark.asyncio
async def test_chat_repo_update(chat_factory, db_adapter_mock):
    chat = chat_factory()
    chat_repo = repositories.ChatRepository(db_adapter=db_adapter_mock)

    await chat_repo.update(chat)

    assert db_adapter_mock.update_chat.called
