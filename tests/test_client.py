import aiohttp
import pytest

from app import client


@pytest.mark.asyncio
async def test_client_init():
    webclient = client.Client()
    assert isinstance(webclient.session, aiohttp.ClientSession)
    await webclient.close()


@pytest.mark.asyncio
async def test_client_close(amocker):
    webclient = client.Client()

    with amocker.patch.object(webclient.session, 'close') as close_mock:
        assert await webclient.close() is None

    assert close_mock.called
    assert close_mock.call_args == amocker.call()


@pytest.mark.asyncio
async def test_client_get(aresponses):
    host = 'realestates.com'
    path = '/list'
    aresponses.add(host, path, 'get', response='')

    webclient = client.Client()
    assert await webclient.get(f'https://{host}{path}') == ''
    await webclient.close()
