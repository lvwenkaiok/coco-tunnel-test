"""
安全鉴权测试：验证三域隔离机制
Admin / Internal / API Key 三套凭证严格隔离，互不越权
"""
import pytest
import httpx

@pytest.mark.asyncio
async def test_admin_token_rejected_on_internal(base_url, admin_token):
    """使用 ADMIN_TOKEN 访问 Internal 接口 ➔ 401/403"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    async with httpx.AsyncClient(base_url=base_url, verify=False) as client:
        resp = await client.get("/api/v1/internal/jwt-public-key", headers=headers)
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"

@pytest.mark.asyncio
async def test_internal_token_rejected_on_admin(base_url, internal_token):
    """使用 INTERNAL_TOKEN 访问 Admin 接口 ➔ 401/403"""
    headers = {"Authorization": f"Bearer {internal_token}"}
    async with httpx.AsyncClient(base_url=base_url, verify=False) as client:
        resp = await client.get("/api/v1/manage/edges", headers=headers)
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"

@pytest.mark.asyncio
async def test_apikey_rejected_on_admin(base_url, api_key_secret):
    """使用 API_KEY_SECRET 访问 Admin 接口 ➔ 401/403"""
    headers = {"Authorization": f"Bearer {api_key_secret}"}
    async with httpx.AsyncClient(base_url=base_url, verify=False) as client:
        resp = await client.get("/api/v1/manage/edges", headers=headers)
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"

@pytest.mark.asyncio
async def test_no_auth_rejected(base_url):
    """无认证访问受保护接口 ➔ 401"""
    async with httpx.AsyncClient(base_url=base_url, verify=False) as client:
        resp = await client.get("/api/v1/manage/edges")
        assert resp.status_code == 401

@pytest.mark.asyncio
async def test_invalid_token_rejected(base_url):
    """无效 Token ➔ 401"""
    headers = {"Authorization": "Bearer invalid_token_12345"}
    async with httpx.AsyncClient(base_url=base_url, verify=False) as client:
        resp = await client.get("/api/v1/manage/edges", headers=headers)
        assert resp.status_code == 401
