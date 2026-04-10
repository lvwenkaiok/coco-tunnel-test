"""
Edge 节点管理完整测试
创建 ➔ 查询 ➔ 更新 ➔ 生成安装脚本 ➔ 删除
"""
import pytest

TEST_EDGE_PAYLOAD = {
    "node_id": "pytest-edge-001",
    "region": "cn-shanghai",
    "public_ip": "192.0.2.1",
    "quic_port": 15001,
    "http_port": 18091,
    "agent_url": "http://192.0.2.1:19000",
    "domain_suffix": "pytest.example.com"
}

async def _ensure_edge_clean(client, node_id):
    """Ensure node doesn't exist before test"""
    try:
        await client.delete(f"/api/v1/manage/edges/{node_id}")
    except Exception:
        pass

async def _create_edge(client, payload):
    """Create edge and return node_id"""
    resp = await client.post("/api/v1/manage/edges", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("success") is True
    return payload["node_id"]

@pytest.mark.asyncio
async def test_create_and_list_edge(admin_client):
    """创建 Edge 节点并验证出现在列表中"""
    node_id = TEST_EDGE_PAYLOAD["node_id"]
    await _ensure_edge_clean(admin_client, node_id)
    try:
        await _create_edge(admin_client, TEST_EDGE_PAYLOAD)
        
        # Verify in list
        resp = await admin_client.get("/api/v1/manage/edges")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        edges = data.get("data", [])
        node_ids = [e.get("node_id") or e.get("id") for e in edges]
        assert node_id in node_ids
    finally:
        await _ensure_edge_clean(admin_client, node_id)

@pytest.mark.asyncio
async def test_create_edge_missing_fields(admin_client):
    """创建 Edge 节点缺少必填字段 ➔ 422/400"""
    payload = {"node_id": "test-incomplete"}
    resp = await admin_client.post("/api/v1/manage/edges", json=payload)
    assert resp.status_code in [400, 422]

@pytest.mark.asyncio
async def test_update_edge_node(admin_client):
    """更新 Edge 节点"""
    node_id = "pytest-edge-update"
    payload = {**TEST_EDGE_PAYLOAD, "node_id": node_id}
    await _ensure_edge_clean(admin_client, node_id)
    try:
        await _create_edge(admin_client, payload)
        
        update_payload = {
            "public_ip": "192.0.2.100",
            "domain_suffix": "updated.example.com"
        }
        resp = await admin_client.patch(f"/api/v1/manage/edges/{node_id}", json=update_payload)
        assert resp.status_code == 200
        assert resp.json().get("success") is True
    finally:
        await _ensure_edge_clean(admin_client, node_id)

@pytest.mark.asyncio
async def test_generate_install_script(admin_client):
    """生成 Edge 安装脚本"""
    node_id = "pytest-edge-script"
    payload = {**TEST_EDGE_PAYLOAD, "node_id": node_id}
    await _ensure_edge_clean(admin_client, node_id)
    try:
        await _create_edge(admin_client, payload)
        
        resp = await admin_client.get(f"/api/v1/manage/edges/{node_id}/install-script")
        assert resp.status_code == 200
        assert len(resp.text) > 0
    finally:
        await _ensure_edge_clean(admin_client, node_id)

@pytest.mark.asyncio
async def test_edge_error_page_crud(admin_client):
    """获取 ➔ 更新 Edge 错误页配置"""
    node_id = "pytest-edge-errpage"
    payload = {**TEST_EDGE_PAYLOAD, "node_id": node_id}
    await _ensure_edge_clean(admin_client, node_id)
    try:
        await _create_edge(admin_client, payload)
        
        # Get
        resp = await admin_client.get(f"/api/v1/manage/edges/{node_id}/error-page")
        assert resp.status_code == 200
        assert resp.json().get("success") is True
        
        # Update
        update_payload = {
            "not_found_html": "<html><body>Custom 404</body></html>",
            "offline_html": "<html><body>Service Offline</body></html>"
        }
        resp = await admin_client.put(f"/api/v1/manage/edges/{node_id}/error-page", json=update_payload)
        assert resp.status_code == 200
        assert resp.json().get("success") is True
    finally:
        await _ensure_edge_clean(admin_client, node_id)

@pytest.mark.asyncio
async def test_delete_edge_node(admin_client):
    """创建并删除 Edge 节点"""
    node_id = "pytest-edge-delete"
    payload = {**TEST_EDGE_PAYLOAD, "node_id": node_id}
    await _ensure_edge_clean(admin_client, node_id)
    await _create_edge(admin_client, payload)
    
    resp = await admin_client.delete(f"/api/v1/manage/edges/{node_id}")
    assert resp.status_code == 200
    assert resp.json().get("success") is True
