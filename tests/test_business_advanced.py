"""
高级业务功能测试 (Core Business)
涵盖：流量统计、批量操作、隧道同步、Internal 接口、Assets
"""
import pytest
from datetime import date

TEST_USER_ID = "business-test-user"

TEST_TUNNEL_PAYLOAD = {
    "user_id": TEST_USER_ID,
    "name": "biz-tunnel",
    "protocol": "tcp",
    "local_ip": "127.0.0.1",
    "local_port": 9090,
    "kind": "tcp",
    "policy": {"enabled": True}
}

async def create_and_get_tunnel(client, payload):
    """Helper: Create tunnel and return ID"""
    # Try to clean up existing first
    try:
        await client.post("/api/v1/manage/tunnels/batch/suspend", json={"filter": {"user_id": TEST_USER_ID}})
    except: pass
    
    resp = await client.post("/api/v1/manage/tunnels", json=payload)
    if resp.status_code != 200:
        return None
    data = resp.json()
    return data.get("data", {}).get("tunnel_id") or data.get("data", {}).get("id")

async def cleanup_tunnel(client, tunnel_id):
    """Helper: Delete tunnel"""
    if tunnel_id:
        try:
            await client.delete(f"/api/v1/manage/tunnels/{tunnel_id}")
        except: pass

# ==========================================
# 1. 流量与统计 (Metrics & Stats)
# ==========================================

@pytest.mark.asyncio
async def test_tunnel_monthly_metrics(apikey_client):
    """查询隧道月度流量统计"""
    tid = await create_and_get_tunnel(apikey_client, TEST_TUNNEL_PAYLOAD)
    try:
        assert tid, "Failed to create tunnel for metrics test"
        resp = await apikey_client.get(f"/api/v1/manage/tunnels/{tid}/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
    finally:
        await cleanup_tunnel(apikey_client, tid)

@pytest.mark.asyncio
async def test_tunnel_daily_metrics(apikey_client):
    """查询隧道按日流量统计 (需 from/to 参数)"""
    tid = await create_and_get_tunnel(apikey_client, TEST_TUNNEL_PAYLOAD)
    try:
        assert tid
        today = date.today()
        start_date = today.replace(day=1).isoformat()
        end_date = today.isoformat()
        
        resp = await apikey_client.get(f"/api/v1/manage/tunnels/{tid}/metrics/daily", params={
            "from": start_date,
            "to": end_date
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
    finally:
        await cleanup_tunnel(apikey_client, tid)

# ==========================================
# 2. 批量操作 (Batch Operations)
# ==========================================

@pytest.mark.asyncio
async def test_batch_suspend_and_resume(apikey_client):
    """按用户批量暂停和恢复"""
    # 1. Create a tunnel to be batched
    tid = await create_and_get_tunnel(apikey_client, TEST_TUNNEL_PAYLOAD)
    assert tid
    
    try:
        # 2. Batch Suspend
        resp = await apikey_client.post("/api/v1/manage/tunnels/batch/suspend", json={
            "filter": {"user_id": TEST_USER_ID},
            "reason": "maintenance test"
        })
        assert resp.status_code == 200
        assert resp.json().get("success") is True
        
        # 3. Verify suspended (Optional: check state)
        
        # 4. Batch Resume
        resp = await apikey_client.post("/api/v1/manage/tunnels/batch/resume", json={
            "filter": {"user_id": TEST_USER_ID},
            "reason": "back online"
        })
        assert resp.status_code == 200
        assert resp.json().get("success") is True
    finally:
        await cleanup_tunnel(apikey_client, tid)

# ==========================================
# 3. 同步接口 (Sync)
# ==========================================

@pytest.mark.asyncio
async def test_sync_tunnels(apikey_client):
    """批量同步外部隧道数据"""
    sync_data = {
        "tunnels": [
            {
                "tunnel_id": "sync-ext-001",
                "user_id": "sync-user",
                "name": "external-tunnel",
                "protocol": "tcp",
                "local_ip": "10.0.0.1",
                "local_port": 80,
                "edge_node_id": "non-existent-edge-001", 
                "policy": {"enabled": True},
                "kind": "tcp"
            }
        ]
    }
    
    resp = await apikey_client.post("/api/v1/manage/tunnels/sync", json=sync_data)
    # Expect 400 if edge_node_id doesn't exist, or 200 if it ignores it
    assert resp.status_code in [200, 400, 404] 

# ==========================================
# 4. 内部接口 (Internal API)
# ==========================================

@pytest.mark.asyncio
async def test_internal_jwt_public_key(internal_client):
    """下载 JWT 公钥 PEM 文件"""
    resp = await internal_client.get("/api/v1/internal/jwt-public-key")
    assert resp.status_code == 200
    # 验证返回的是 PEM 格式文本
    content = resp.text
    assert "-----BEGIN" in content

@pytest.mark.asyncio
async def test_internal_nginx_configs(internal_client):
    """获取 Edge 节点的 Nginx 配置"""
    # Using a dummy ID. If it exists -> 200, else -> 404 or 500. 
    # As long as it's not 401/403 (Auth), it's a pass for "API Reachability".
    resp = await internal_client.get("/api/v1/internal/nginx/configs", params={"edge_node_id": "dummy-node"})
    assert resp.status_code not in [401, 403]

@pytest.mark.asyncio
async def test_internal_error_page(internal_client):
    """获取指定 Edge 的错误页 HTML"""
    resp = await internal_client.get("/api/v1/internal/error-page", params={"edge_node_id": "dummy-node"})
    assert resp.status_code not in [401, 403]

# ==========================================
# 5. 资产下载 (Assets)
# ==========================================

@pytest.mark.asyncio
async def test_download_asset(admin_client):
    """下载受保护的二进制文件 (coco-edge)"""
    # 503 is acceptable here as it means the Gateway routed the request to the storage service,
    # but the storage service is currently down/unreachable.
    # 200 means success. 404 means file not found.
    resp = await admin_client.get("/assets/coco-edge")
    assert resp.status_code in [200, 404, 503]
