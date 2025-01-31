import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from domain.exceptions import PromptNotFoundException, DuplicatePromptVersionException

def test_create_prompt(test_client, mock_supabase):
    # Configurar el mock
    mock_supabase.table().insert().execute.return_value.data = [{
        "id": "123",
        "name": "test_prompt",
        "version": "1.0.0",
        "prompt_text": "Test prompt",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "metadata": {}
    }]

    # Realizar la petición
    response = test_client.post(
        "/api/v1/prompts",
        json={
            "name": "test_prompt",
            "version": "1.0.0",
            "prompt_text": "Test prompt",
            "metadata": {}
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test_prompt"
    assert data["version"] == "1.0.0"

def test_create_duplicate_prompt(test_client, mock_supabase):
    # Simular error de duplicado
    mock_supabase.table().insert().execute.side_effect = DuplicatePromptVersionException(
        "test_prompt", "1.0.0"
    )

    response = test_client.post(
        "/api/v1/prompts",
        json={
            "name": "test_prompt",
            "version": "1.0.0",
            "prompt_text": "Test prompt"
        }
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "DUPLICATE_PROMPT_VERSION"

# ... más tests para prompts ... 