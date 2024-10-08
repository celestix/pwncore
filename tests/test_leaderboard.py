import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_leaderboard(client: AsyncClient):
    # Send a GET response to the specified endpoint
    response = await client.get("/api/leaderboard")
    # Evaluate the response against expected values
    assert response.text == "[]"
