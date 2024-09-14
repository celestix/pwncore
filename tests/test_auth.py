import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_auth(client: AsyncClient):
    # Send a GET response to the specified endpoint
    response = await client.post("/api/auth/signup")
    # Evaluate the response against expected values
    assert response.text == "[]"
