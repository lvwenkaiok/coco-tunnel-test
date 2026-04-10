import pytest

@pytest.mark.asyncio
async def test_admin_list_edges(admin_client):
    """
    Test Case: List Edge Nodes
    Endpoint: GET /api/v1/manage/edges
    Description: Verify we can list edge nodes using the Admin Token.
    """
    response = await admin_client.get("/api/v1/manage/edges")
    
    # Verify Status Code
    assert response.status_code == 200
    
    # Verify Response Structure (based on OpenAPI ApiEnvelope)
    data = response.json()
    assert "success" in data
    assert "data" in data
    
    # If successful, data should be a list of edges
    if data["success"]:
        assert isinstance(data["data"], list)

@pytest.mark.asyncio
async def test_admin_create_edge_fail(admin_client):
    """
    Test Case: Create Edge Node (Negative Test - Missing Fields)
    Endpoint: POST /api/v1/manage/edges
    Description: Sending incomplete data should return 422 Validation Error.
    """
    payload = {
        "node_id": "test-edge-fail" 
        # Missing: region, public_ip, quic_port
    }
    response = await admin_client.post("/api/v1/manage/edges", json=payload)
    
    # Should fail validation
    assert response.status_code in [400, 422, 409] # 422 is standard for pydantic/fastapi
