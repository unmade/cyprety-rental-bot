import pytest

from app import datatypes, providers, services


@pytest.mark.asyncio
async def test_send_service_start_sending(amocker, async_gen_mock, property_factory, send_service):
    real_property = property_factory(
        title='Renovated house', price=datatypes.Price('700'), url='https://example.com/1'
    )
    send_service.get_updates = async_gen_mock(return_value=real_property)

    await send_service.start_sending()

    assert send_service.db_adapter.select_chats.called
    assert send_service.bot_adapter.broadcast.called
    assert send_service.bot_adapter.broadcast.call_args == amocker.call(
        chats=[], text=f'[Renovated house €700]({real_property.telegram_link})'
    )


@pytest.mark.asyncio
async def test_send_service_get_updates(amocker, property_factory, send_service):
    expected_property = property_factory()
    provider = amocker.Mock(spec=providers.Provider)
    provider.get_updates = amocker.CoroutineMock(return_value=[expected_property])
    send_service.providers = [provider]

    get_updates = send_service.get_updates(interval=0.1)
    assert await get_updates.__anext__() == expected_property
    assert await get_updates.__anext__() == expected_property  # run second iteration


@pytest.mark.asyncio
async def test_chat_service_get_or_create_gets_chat(chat_factory, db_adapter_mock):
    chat = chat_factory()
    db_adapter_mock.get_chat.return_value = chat
    chat_service = services.ChatService(db_adapter=db_adapter_mock)
    assert await chat_service.get_or_create(chat_id=chat.id) == chat

    assert db_adapter_mock.get_chat.called
    assert not db_adapter_mock.create_chat.called


@pytest.mark.asyncio
async def test_chat_service_get_or_create_creates_chat(chat_factory, db_adapter_mock):
    chat = chat_factory()
    db_adapter_mock.get_chat.return_value = None
    db_adapter_mock.create_chat.return_value = chat
    chat_service = services.ChatService(db_adapter=db_adapter_mock)
    assert await chat_service.get_or_create(chat_id=chat.id) == chat

    assert db_adapter_mock.get_chat.called
    assert db_adapter_mock.create_chat.called


@pytest.mark.asyncio
async def test_chat_service_set_min_price(
        amocker, chat_factory, chat_service: services.ChatService
):
    chat = chat_factory()
    chat_service.get_or_create = amocker.CoroutineMock(return_value=chat)

    min_price = datatypes.Price('700.0')
    await chat_service.set_min_price(chat_id=chat.id, price=min_price)

    assert chat_service.get_or_create.called
    assert chat_service.db_adapter.update_chat.called

    chat.min_price = min_price
    assert chat_service.db_adapter.update_chat.call_args == amocker.call(chat)


@pytest.mark.asyncio
async def test_chat_service_set_min_price_greater_than_max(
        amocker, chat_factory, chat_service: services.ChatService
):
    chat = chat_factory(min_price=datatypes.Price('700'), max_price=datatypes.Price('1000'))
    chat_service.get_or_create = amocker.CoroutineMock(return_value=chat)

    min_price = datatypes.Price('1001')
    with pytest.raises(ValueError):
        await chat_service.set_min_price(chat_id=chat.id, price=min_price)

    assert chat_service.get_or_create.called
    assert not chat_service.db_adapter.update_chat.called


@pytest.mark.asyncio
async def test_chat_service_set_max_price(
        amocker, chat_factory, chat_service: services.ChatService
):
    chat = chat_factory()
    chat_service.get_or_create = amocker.CoroutineMock(return_value=chat)

    max_price = datatypes.Price('700.0')
    await chat_service.set_max_price(chat_id=chat.id, price=max_price)

    assert chat_service.get_or_create.called
    assert chat_service.db_adapter.update_chat.called

    chat.max_price = max_price
    assert chat_service.db_adapter.update_chat.call_args == amocker.call(chat)


@pytest.mark.asyncio
async def test_chat_service_set_max_price_lesser_than_min(
        amocker, chat_factory, chat_service: services.ChatService
):
    chat = chat_factory(min_price=datatypes.Price('700'), max_price=datatypes.Price('1000'))
    chat_service.get_or_create = amocker.CoroutineMock(return_value=chat)

    max_price = datatypes.Price('699')
    with pytest.raises(ValueError):
        await chat_service.set_max_price(chat_id=chat.id, price=max_price)

    assert chat_service.get_or_create.called
    assert not chat_service.db_adapter.update_chat.called
