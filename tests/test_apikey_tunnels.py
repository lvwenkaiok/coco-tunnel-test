import pytest

@pytest.mark.asyncio
async def test_apikey_list_tunnels(apikey_client):
    """
    Test Case: List Tunnels
    Endpoint: GET /api/v1/manage/tunnels
    Description: Verify we can list tunnels using the API Key Secret.
    """
    response = await apikey_client.get("/api/v1/manage/tunnels")
    
    # Verify Status Code
    assert response.status_code == 200
    
    # Verify Response Structure
    data = response.json()
    assert "success" in data
    assert "data" in data
    
    # Data should be a list (or dict with pagination info depending on implementation, 
    # but OpenAPI says ApiEnvelope where data is nullable. 
    # However, for list endpoints, it's usually a list object or pagination object)
    # OpenAPI says: "tunnel list". Let's assume it's an object containing a list or just a list.
    # If it's empty, data might be [] or null.
    
    print(f"List Tunnels Response: {data}")

@pytest.mark.asyncio
async def test_apikey_stats_overview(apikey_client):
    """
    Test Case: Stats Overview
    Endpoint: GET /api/v1/manage/stats
    Description: Verify we can access stats using the API Key Secret.
    """
    response = await apikey_client.get("/api/v1/manage/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
