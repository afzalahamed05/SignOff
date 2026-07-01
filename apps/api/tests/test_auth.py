import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_auth_flow(client: AsyncClient):
    """Tests the complete registration, login, and protected route flow."""
    unique_email = "test_ci_user@signoff.ai"
    
    # 1. Register
    res = await client.post("/api/v1/auth/register", json={
        "email": unique_email,
        "password": "securepassword123",
        "full_name": "CI Test User"
    })
    assert res.status_code in [201, 400] # 400 if the test was run previously and user exists
    
    # 2. Login (OAuth2 form data)
    res = await client.post("/api/v1/auth/login", data={
        "username": unique_email,
        "password": "securepassword123"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    token = data["access_token"]
    
    # 3. Access Protected Route
    res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == unique_email