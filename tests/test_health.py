import pytest
import httpx

@pytest.mark.asyncio
async def test_health_check(admin_client):
    """
    Test Case: Health Check
    Endpoint: GET /health
    Description: Verify the API server is reachable and returns 'ok'.
    """
    # Note: /health might not need auth, but we use admin_client for base_url convenience
    # We'll strip auth headers for this specific request if needed, 
    # but usually sending auth to a public endpoint doesn't hurt unless it rejects it.
    # The OpenAPI spec doesn't list security for /health.
    
    # Let's create a client without auth for this test to be precise
    client_no_auth = httpx.AsyncClient(base_url=admin_client.base_url, verify=False)
    
    try:
        response = await client_no_auth.get("/health")
        assert response.status_code == 200
        assert response.text.strip().lower() == "ok"
    finally:
        await client_no_auth.aclose()
