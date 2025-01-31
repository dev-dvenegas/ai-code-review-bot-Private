import pytest
from fastapi.testclient import TestClient
from supabase import create_client
import os
from main import app
from infrastructure.config.settings import Settings

@pytest.fixture
def test_settings():
    return Settings(
        GITHUB_APP_ID="test_app_id",
        GITHUB_APP_PRIVATE_KEY="test_key",
        GITHUB_WEBHOOK_SECRET="test_secret",
        OPENAI_API_KEY="test_openai_key",
        SUPABASE_URL="test_url",
        SUPABASE_SERVICE_KEY="test_key"
    )

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_supabase(mocker):
    mock_client = mocker.Mock()
    mocker.patch(
        'infrastructure.database.supabase_client.create_client',
        return_value=mock_client
    )
    return mock_client 