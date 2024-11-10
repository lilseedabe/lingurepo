import os
from fastapi.testclient import TestClient
from api.main import app
from lingustruct.license_manager import LicenseManager
from dotenv import load_dotenv

# .env ファイルのロード
load_dotenv()

# LicenseManager インスタンス
license_manager = LicenseManager()

# テスト用APIキー
TEST_API_KEY = os.getenv("TEST_LICENSE_KEY")

client = TestClient(app)

HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": TEST_API_KEY
}

def test_generate_master():
    """Test the /lingu_struct/generate_master endpoint."""
    user_info = license_manager.validate_api_key(TEST_API_KEY)
    assert user_info is not None, "API Key validation failed."

    payload = {"project_id": "test_project", "version": "1.0"}
    response = client.post("/lingu_struct/generate_master", json=payload, headers=HEADERS)
    assert response.status_code == 200

def test_get_module():
    """Test the /lingu_struct/modules/{module_id} endpoint."""
    user_info = license_manager.validate_api_key(TEST_API_KEY)
    assert user_info is not None, "API Key validation failed."

    response = client.get("/lingu_struct/modules/1", headers=HEADERS)
    assert response.status_code == 200

def test_rate_limit():
    """Test the rate limit with multiple requests."""
    user_info = license_manager.validate_api_key(TEST_API_KEY)
    assert user_info is not None, "API Key validation failed."

    last_response = None
    for _ in range(10):
        last_response = client.get("/lingu_struct/modules/1", headers=HEADERS)
    assert last_response.status_code in (200, 429)
