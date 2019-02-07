import time

import pytest

from app import providers


def test_provider_init(parser_mock, client_mock):
    url = 'https://real.estates.com'
    provider = providers.Provider(url, parser=parser_mock, webclient=client_mock)
    assert provider.url == url
    assert provider.parser == parser_mock


@pytest.mark.asyncio
async def test_provider_get_updates(amocker, parser_mock, client_mock):
    parser_mock.parse = amocker.Mock(return_value=[])
    provider = providers.Provider('https://example.com', parser=parser_mock, webclient=client_mock)

    properties = await provider.get_updates()

    assert properties == []


@pytest.mark.asyncio
async def test_provider_get_updates_calls_parse(amocker, parser_mock, client_mock):
    parser_mock.parse = amocker.Mock(return_value=[])
    client_mock.get = amocker.CoroutineMock(return_value='<div>test</div>')
    provider = providers.Provider('https://example.com', parser=parser_mock, webclient=client_mock)

    await provider.get_updates()

    assert provider.parser.parse.called
    assert provider.parser.parse.call_args == amocker.call('<div>test</div>')


@pytest.mark.asyncio
async def test_provider_get_updates_calls_client_get(amocker, parser_mock, client_mock):
    parser_mock.parse = amocker.Mock(return_value=[])
    provider = providers.Provider('https://example.com', parser=parser_mock, webclient=client_mock)

    await provider.get_updates()

    assert client_mock.get.called
    assert client_mock.get.call_args == amocker.call(provider.url)


@pytest.mark.asyncio
async def test_provider_get_updates_changes_latest_created_at(
        amocker, property_factory, parser_mock, client_mock
):
    created_at = time.time() + 10_000
    property_ = property_factory(created_at=created_at)
    parser_mock.parse = amocker.Mock(return_value=[property_])
    provider = providers.Provider('https://example.com', parser=parser_mock, webclient=client_mock)
    latest_created_at = provider.latest_created_at

    await provider.get_updates()

    assert provider.latest_created_at == property_.created_at
    assert latest_created_at != provider.latest_created_at


@pytest.mark.asyncio
async def test_provider_get_updates_does_not_change_latest_created_at(
        amocker, parser_mock, client_mock
):
    parser_mock.parse = amocker.Mock(return_value=[])
    provider = providers.Provider('https://example.com', parser=parser_mock, webclient=client_mock)
    latest_created_at = provider.latest_created_at

    await provider.get_updates()

    assert provider.latest_created_at == latest_created_at


@pytest.mark.asyncio
async def test_provider_get_updates_filters_newest(
        amocker, property_factory, parser_mock, client_mock
):
    seen_property = property_factory(created_at=time.time() - 10_000)
    new_property = property_factory(created_at=time.time() + 10_000)

    parser_mock.parse = amocker.Mock(return_value=[seen_property, new_property])
    provider = providers.Provider('https://example.com', parser=parser_mock, webclient=client_mock)

    properties = await provider.get_updates()

    assert properties == [new_property]


@pytest.mark.asyncio
async def test_provider_filter_duplicates(amocker, property_factory, parser_mock, client_mock):
    property1 = property_factory(url='https://ex.com/1', created_at=time.time() + 10_000)
    property2 = property_factory(created_at=time.time() + 10_000)

    parser_mock.parse = amocker.Mock(return_value=[property1, property2])
    provider = providers.Provider('https://example.com', parser=parser_mock, webclient=client_mock)

    await provider.get_updates()

    property1 = property_factory(url='https://ex.com/1', created_at=time.time() + 11_000)
    property2 = property_factory(created_at=time.time() + 11_000)
    parser_mock.parse = amocker.Mock(return_value=[property1, property2])
    properties = await provider.get_updates()

    assert properties == [property2]
