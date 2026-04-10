import os
import pytest
import httpx
from dotenv import load_dotenv

# Load .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

@pytest.fixture(scope="session")
def base_url():
    """API Base URL"""
    return os.getenv("BASE_URL", "https://pasctl.kunkunji.com")

@pytest.fixture(scope="session")
def admin_token():
    """Admin Bearer Token"""
    return os.getenv("ADMIN_TOKEN", "")

@pytest.fixture(scope="session")
def internal_token():
    """Internal Bearer Token"""
    return os.getenv("INTERNAL_TOKEN", "")

@pytest.fixture(scope="session")
def api_key_secret():
    """API Key Secret (Used as Bearer Token for Tunnels)"""
    return os.getenv("API_KEY_SECRET", "")

@pytest.fixture
def admin_client(base_url, admin_token):
    """HTTPX Async Client for Admin Endpoints"""
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    return httpx.AsyncClient(base_url=base_url, headers=headers, verify=False)

@pytest.fixture
def internal_client(base_url, internal_token):
    """HTTPX Async Client for Internal Endpoints"""
    headers = {
        "Authorization": f"Bearer {internal_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    return httpx.AsyncClient(base_url=base_url, headers=headers, verify=False)

@pytest.fixture
def apikey_client(base_url, api_key_secret):
    """HTTPX Async Client for API Key Endpoints (Tunnels)"""
    headers = {
        "Authorization": f"Bearer {api_key_secret}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    return httpx.AsyncClient(base_url=base_url, headers=headers, verify=False)
