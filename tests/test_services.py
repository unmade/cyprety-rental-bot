import pytest

from app import datatypes, services


@pytest.mark.asyncio
async def test_send_service_start_sending_calls_broadcast(
        amocker, async_gen_mock, property_factory, send_service
):
    real_property = property_factory(
        title='Renovated house', price=datatypes.Price('700'), url='https://example.com/1'
    )
    send_service.property_repo.get_updates = async_gen_mock(return_value=real_property)

    await send_service.start_sending()

    assert send_service.bot_repo.broadcast.called
    assert send_service.bot_repo.broadcast.call_args == amocker.call(
        chats=[], text=f'[Renovated house €700]({real_property.telegram_link})'
    )


@pytest.mark.asyncio
async def test_send_service_start_sending_calls_get_updates(amocker, send_service):
    await send_service.start_sending()

    assert send_service.property_repo.get_updates.called
    assert send_service.property_repo.get_updates.call_args == amocker.call(interval=2)


@pytest.mark.asyncio
async def test_send_service_start_sending_calls_chat_repo_list(
        amocker, async_gen_mock, property_factory, send_service
):
    real_property = property_factory()
    send_service.property_repo.get_updates = async_gen_mock(return_value=real_property)

    await send_service.start_sending()

    assert send_service.chat_repo.list.called
    assert send_service.chat_repo.list.call_args == amocker.call(with_price=real_property.price)


@pytest.mark.asyncio
async def test_bot_service_welcome(bot_service: services.BotService):
    text = await bot_service.welcome(chat_id=1, text='/start')
    assert text.startswith('I can notify you')
    assert bot_service.chat_repo.get_or_create.called


@pytest.mark.asyncio
async def test_bot_service_set_min_price(chat_factory, bot_service: services.BotService):
    chat = chat_factory()
    bot_service.chat_repo.get_or_create.return_value = chat

    min_price = '700.0'
    text = await bot_service.set_min_price(chat_id=chat.id, text=min_price)
    assert min_price in text

    assert bot_service.chat_repo.get_or_create.called
    assert bot_service.chat_repo.update.called


@pytest.mark.asyncio
@pytest.mark.parametrize('price', ['seven hundred', -1])
async def test_bot_service_set_min_invalid_price(bot_service: services.BotService, price):
    text = await bot_service.set_min_price(chat_id=1, text=price)
    assert text == 'Please use numbers to set the price. For example: 700.0'

    assert not bot_service.chat_repo.get_or_create.called
    assert not bot_service.chat_repo.update.called


@pytest.mark.asyncio
async def test_bot_service_set_min_price_greater_than_max(
        amocker, chat_factory, bot_service: services.BotService
):
    chat = chat_factory(min_price=datatypes.Price('700'), max_price=datatypes.Price('1000'))
    bot_service.chat_repo.get_or_create = amocker.CoroutineMock(return_value=chat)

    text = await bot_service.set_min_price(chat_id=1, text='1001')
    assert text == 'Min price must be lesser than max price'

    assert bot_service.chat_repo.get_or_create.called
    assert not bot_service.chat_repo.update.called


@pytest.mark.asyncio
async def test_bot_service_set_max_price(chat_factory, bot_service: services.BotService):
    chat = chat_factory()
    bot_service.chat_repo.get_or_create.return_value = chat

    max_price = '700.0'
    text = await bot_service.set_max_price(chat_id=chat.id, text=max_price)
    assert max_price in text

    assert bot_service.chat_repo.get_or_create.called
    assert bot_service.chat_repo.update.called


@pytest.mark.asyncio
@pytest.mark.parametrize('price', ['seven hundred', -1])
async def test_bot_service_set_max_invalid_price(bot_service: services.BotService, price):
    text = await bot_service.set_max_price(chat_id=1, text=price)
    assert text == 'Please use numbers to set the price. For example: 700.0'

    assert not bot_service.chat_repo.get_or_create.called
    assert not bot_service.chat_repo.update.called


@pytest.mark.asyncio
async def test_bot_service_set_max_price_lesser_than_min(
        amocker, chat_factory, bot_service: services.BotService
):
    chat = chat_factory(min_price=datatypes.Price('700'), max_price=datatypes.Price('1000'))
    bot_service.chat_repo.get_or_create = amocker.CoroutineMock(return_value=chat)

    text = await bot_service.set_max_price(chat_id=1, text='699')
    assert text == 'Max price must be greater than min price'

    assert bot_service.chat_repo.get_or_create.called
    assert not bot_service.chat_repo.update.called
