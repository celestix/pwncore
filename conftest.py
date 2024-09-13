import pytest
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from pwncore import app

ClientManagerType = AsyncGenerator[AsyncClient, None]


@pytest.fixture(scope="module")
def anyio_backend() -> str:
    return "asyncio"


@asynccontextmanager
async def client_manager(app, base_url="http://test", **kw) -> ClientManagerType:
    app.state.testing = True
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url=base_url, **kw) as c:
            yield c


@pytest.fixture(scope="module")
async def client() -> ClientManagerType:
    async with client_manager(app) as c:
        yield c

# import sys

# def pytest_configure(config):
#     sys._is_a_test = True