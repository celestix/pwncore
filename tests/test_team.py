import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_team(client: AsyncClient):
    # Send a GET response to the specified endpoint
    response = await client.get("/api/team/list")
    # Evaluate the response against expected values
    assert response.text == "[]"

@pytest.mark.anyio
async def test_members(client: AsyncClient):
    # Send a GET response to the specified endpoint
    response = await client.get("/api/team/members")
    # Evaluate the response against expected values
    assert response.status_code == 422