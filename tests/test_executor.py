import pytest

from app import executor, parsers


@pytest.mark.asyncio
async def test_application_init(amocker, application: executor.Application):
    application.db_adapter.create_tables = amocker.CoroutineMock()
    await application.init()

    assert application.db_adapter.create_tables.called


@pytest.mark.asyncio
async def test_application_shutdown(amocker, application: executor.Application):
    application.db_adapter.close = amocker.CoroutineMock()
    application.bot_adapter.close = amocker.CoroutineMock()
    application.webclient.close = amocker.CoroutineMock()

    await application.shutdown()

    assert application.db_adapter.close.called
    assert application.bot_adapter.close.called
    assert application.webclient.close.called


@pytest.mark.asyncio
async def test_application_run(event_loop, amocker, application: executor.Application):
    application.bot.start_polling = amocker.CoroutineMock()
    application.send_service.start_sending = amocker.CoroutineMock()

    application.run(event_loop)

    assert application.bot.start_polling.called
    assert application.send_service.start_sending.called


@pytest.mark.asyncio
async def test_application_providers(amocker, application: executor.Application):
    parser_classes = {'https://real.estates.com': parsers.BazarakiParser}
    with amocker.patch('app.registry.list_parsers', return_value=parser_classes) as registry_mock:
        provider_list = application.provider_list

    assert len(provider_list) == 1
    assert registry_mock.called


def test_run(amocker, application_mock: executor.Application):
    with amocker.patch('app.executor.Application', return_value=application_mock):
        executor.run()

    assert application_mock.init.called
    assert application_mock.run.called
    assert application_mock.shutdown.called
