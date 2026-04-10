"""
隧道完整生命周期测试
创建 ➔ 查询 ➔ 暂停 ➔ 恢复 ➔ 轮换Token ➔ 删除
"""
import pytest

TEST_TUNNEL_PAYLOAD = {
    "user_id": "test-user-lifecycle",
    "name": "pytest-tcp-tunnel",
    "protocol": "tcp",
    "local_ip": "127.0.0.1",
    "local_port": 2222,
    "kind": "tcp",
    "policy": {
        "enabled": True,
        "allowed_protocols": ["tcp"],
        "bandwidth_limit_bps": 0,
        "max_concurrent_streams": 0,
        "monthly_traffic_limit_bytes": 0,
        "idle_timeout_secs": 0,
        "rate_limit_algorithm": "token_bucket"
    }
}

async def _create_tunnel(client):
    """Helper: create tunnel and return tunnel_id"""
    resp = await client.post("/api/v1/manage/tunnels", json=TEST_TUNNEL_PAYLOAD)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("success") is True
    tunnel_data = data.get("data", {})
    tid = tunnel_data.get("tunnel_id") or tunnel_data.get("id")
    assert tid, f"No tunnel_id in response: {data}"
    return tid

async def _delete_tunnel(client, tunnel_id):
    """Helper: delete tunnel"""
    try:
        await client.delete(f"/api/v1/manage/tunnels/{tunnel_id}")
    except Exception:
        pass

@pytest.mark.asyncio
async def test_create_tunnel_returns_token(apikey_client):
    """创建隧道应返回 client_token"""
    tid = await _create_tunnel(apikey_client)
    try:
        resp = await apikey_client.post("/api/v1/manage/tunnels", json=TEST_TUNNEL_PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        tunnel_data = data.get("data", {})
        assert "client_token" in tunnel_data or "tunnel_id" in tunnel_data
    finally:
        await _delete_tunnel(apikey_client, tid)

@pytest.mark.asyncio
async def test_get_tunnel_detail(apikey_client):
    """查询单个隧道详情"""
    tid = await _create_tunnel(apikey_client)
    try:
        resp = await apikey_client.get(f"/api/v1/manage/tunnels/{tid}")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
    finally:
        await _delete_tunnel(apikey_client, tid)

@pytest.mark.asyncio
async def test_list_tunnels_with_filter(apikey_client):
    """分页查询隧道 + 按用户过滤"""
    tid = await _create_tunnel(apikey_client)
    try:
        resp = await apikey_client.get("/api/v1/manage/tunnels", params={
            "user_id": "test-user-lifecycle",
            "page": 1,
            "size": 10
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
    finally:
        await _delete_tunnel(apikey_client, tid)

@pytest.mark.asyncio
async def test_suspend_then_resume_tunnel(apikey_client):
    """暂停 ➔ 恢复隧道"""
    tid = await _create_tunnel(apikey_client)
    try:
        # Suspend
        resp = await apikey_client.post(f"/api/v1/manage/tunnels/{tid}/suspend")
        assert resp.status_code == 200
        assert resp.json().get("success") is True
        
        # Resume
        resp = await apikey_client.post(f"/api/v1/manage/tunnels/{tid}/resume")
        assert resp.status_code == 200
        assert resp.json().get("success") is True
    finally:
        await _delete_tunnel(apikey_client, tid)

@pytest.mark.asyncio
async def test_rotate_tunnel_token(apikey_client):
    """管理员轮换隧道 Token"""
    tid = await _create_tunnel(apikey_client)
    try:
        payload = {"expires_in_secs": 3600}
        resp = await apikey_client.post(f"/api/v1/manage/tunnels/{tid}/token/rotate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        assert "client_token" in data.get("data", {}) or "token" in data.get("data", {})
    finally:
        await _delete_tunnel(apikey_client, tid)

@pytest.mark.asyncio
async def test_get_tunnel_state(apikey_client):
    """查询隧道实时状态"""
    tid = await _create_tunnel(apikey_client)
    try:
        resp = await apikey_client.get(f"/api/v1/manage/tunnels/{tid}/state")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
    finally:
        await _delete_tunnel(apikey_client, tid)

@pytest.mark.asyncio
async def test_delete_tunnel(apikey_client):
    """创建并删除隧道"""
    tid = await _create_tunnel(apikey_client)
    resp = await apikey_client.delete(f"/api/v1/manage/tunnels/{tid}")
    assert resp.status_code == 200
    assert resp.json().get("success") is True

@pytest.mark.asyncio
async def test_get_deleted_tunnel_404(apikey_client):
    """查询已删除隧道 ➔ 404"""
    tid = await _create_tunnel(apikey_client)
    await apikey_client.delete(f"/api/v1/manage/tunnels/{tid}")
    
    resp = await apikey_client.get(f"/api/v1/manage/tunnels/{tid}")
    assert resp.status_code in [404, 400]
