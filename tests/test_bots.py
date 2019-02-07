import pytest
from aiogram import dispatcher

from app import bots


def test_telegram_bot_start_polling(amocker, telegram_bot: bots.TelegramBot):
    with amocker.patch('aiogram.executor.start_polling') as start_polling_mock:
        telegram_bot.start_polling()

    assert start_polling_mock.called
    assert start_polling_mock.call_args == amocker.call(telegram_bot.dp, skip_updates=True)


@pytest.mark.asyncio
async def test_telegram_bot_welcome(amocker, telegram_bot: bots.TelegramBot):
    message = amocker.Mock(chat=amocker.Mock(id=1), reply=amocker.CoroutineMock())
    await telegram_bot.welcome(message)
    assert telegram_bot.chat_service.get_or_create.called
    assert message.reply.called


@pytest.mark.asyncio
async def test_telegram_bot_start_set_min_price(amocker, telegram_bot: bots.TelegramBot):
    message = amocker.Mock(reply=amocker.CoroutineMock())
    with amocker.patch('app.bots.PriceState') as state:
        state.wait_for_min_price.set = amocker.CoroutineMock()
        await telegram_bot.start_set_min_price(message)
    assert state.wait_for_min_price.set.called


@pytest.mark.asyncio
@pytest.mark.parametrize(['input_price', 'expected_message'], [
    ('700', 'Minimum shown price is set to €700'),
    (None, 'Please use numbers to set the price. For example: 700.0'),
])
async def test_telegram_bot_set_min_price(
        amocker, telegram_bot: bots.TelegramBot, input_price, expected_message
):
    message = amocker.Mock(text=input_price, reply=amocker.CoroutineMock())
    state = amocker.MagicMock(spec=dispatcher.FSMContext)
    await telegram_bot.set_min_price(message, state=state)
    assert message.reply.called
    assert message.reply.call_args == amocker.call(expected_message, reply=False)


@pytest.mark.asyncio
async def test_telegram_bot_set_min_price_chat_service_raise_value_error(
        amocker, telegram_bot: bots.TelegramBot
):
    message = amocker.Mock(text='700', reply=amocker.CoroutineMock())
    state = amocker.MagicMock(spec=dispatcher.FSMContext)
    telegram_bot.chat_service.set_min_price.side_effect = ValueError('Invalid Price')
    await telegram_bot.set_min_price(message, state=state)
    assert message.reply.called
    assert message.reply.call_args == amocker.call('Invalid Price', reply=False)


@pytest.mark.asyncio
async def test_telegram_bot_start_set_max_price(amocker, telegram_bot: bots.TelegramBot):
    message = amocker.Mock(reply=amocker.CoroutineMock())
    with amocker.patch('app.bots.PriceState') as state:
        state.wait_for_max_price.set = amocker.CoroutineMock()
        await telegram_bot.start_set_max_price(message)
    assert state.wait_for_max_price.set.called


@pytest.mark.asyncio
@pytest.mark.parametrize(['input_price', 'expected_message'], [
    ('700', 'Maximum shown price is set to €700'),
    (None, 'Please use numbers to set the price. For example: 700.0'),
])
async def test_telegram_bot_set_max_price(
        amocker, telegram_bot: bots.TelegramBot, input_price, expected_message
):
    message = amocker.Mock(text=input_price, reply=amocker.CoroutineMock())
    state = amocker.MagicMock(spec=dispatcher.FSMContext)
    await telegram_bot.set_max_price(message, state=state)
    assert message.reply.called
    assert message.reply.call_args == amocker.call(expected_message, reply=False)


@pytest.mark.asyncio
async def test_telegram_bot_set_max_price_chat_service_raise_value_error(
        amocker, telegram_bot: bots.TelegramBot
):
    message = amocker.Mock(text='700', reply=amocker.CoroutineMock())
    state = amocker.MagicMock(spec=dispatcher.FSMContext)
    telegram_bot.chat_service.set_max_price.side_effect = ValueError('Invalid Price')
    await telegram_bot.set_max_price(message, state=state)
    assert message.reply.called
    assert message.reply.call_args == amocker.call('Invalid Price', reply=False)
