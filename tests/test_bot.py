import pytest

from app import bot


def test_bot_init(rentbot: bot.Bot):
    assert rentbot


@pytest.mark.asyncio
async def test_bot_register_handler(amocker, rentbot: bot.Bot):
    handler = amocker.CoroutineMock(return_value='Welcome')
    rentbot.register_command_handler('start', handler)

    assert rentbot.dp.register_message_handler.called

    command_handler = rentbot.dp.register_message_handler.call_args[0][0]
    message = amocker.Mock(
        chat=amocker.Mock(id=1),
        get_args=amocker.Mock(return_value=None),
        reply=amocker.CoroutineMock(),
    )

    assert await command_handler(message) is None

    assert handler.called
    assert handler.call_args == amocker.call(message.chat.id, '')

    assert message.reply.called
    assert message.reply.call_args == amocker.call('Welcome', reply=False)


def test_bot_start_polling(event_loop, amocker, rentbot: bot.Bot):
    with amocker.patch('aiogram.executor.start_polling') as start_polling_mock:
        rentbot.start_polling(event_loop)

    assert start_polling_mock.called
    assert start_polling_mock.call_args == amocker.call(
        rentbot.dp, skip_updates=True, loop=event_loop
    )
