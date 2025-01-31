import asyncio
import json
import hmac
import hashlib
from fastapi.testclient import TestClient
from main import app
import pytest
from datetime import datetime, timezone

client = TestClient(app)

def test_github_webhook():
    # Simular payload de GitHub
    payload = {
        "action": "opened",
        "pull_request": {
            "id": 123456,
            "number": 1,
            "title": "feat: add new feature",
            "body": "This PR adds a new feature",
            "state": "open",
            "user": {
                "login": "testuser"
            },
            "base": {
                "ref": "main"
            },
            "head": {
                "ref": "feature-branch",
                "sha": "abc123"
            },
            "created_at": "2024-03-20T10:00:00Z",
            "updated_at": "2024-03-20T10:00:00Z",
            "labels": []
        },
        "repository": {
            "full_name": "owner/repo"
        }
    }

    # Calcular firma del webhook
    secret = "your_webhook_secret"
    signature = hmac.new(
        secret.encode(),
        json.dumps(payload).encode(),
        hashlib.sha256
    ).hexdigest()

    # Enviar request
    response = client.post(
        "/webhook/github",
        json=payload,
        headers={
            "X-Hub-Signature-256": f"sha256={signature}",
            "X-GitHub-Event": "pull_request"
        }
    )

    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Analysis completed"

def test_valid_webhook(test_client, mock_supabase, mocker):
    # Mock GitHub service
    mock_github = mocker.patch('infrastructure.github.github_service.GitHubService')
    mock_github.return_value.get_pr_diff.return_value = "test diff"
    
    # Mock AI service
    mock_ai = mocker.patch('infrastructure.ai.langchain_orchestrator.LangChainOrchestrator')
    mock_ai.return_value.analyze_pr.return_value = {
        "status": "completed",
        "comments": [],
        "summary": "Test review"
    }

    # Crear payload
    payload = {
        "action": "opened",
        "pull_request": {
            "id": 123456,
            "number": 1,
            "title": "Test PR",
            "body": "Test description",
            "state": "open",
            "user": {"login": "testuser"},
            "base": {"ref": "main"},
            "head": {
                "ref": "feature",
                "sha": "abc123"
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "labels": []
        },
        "repository": {
            "full_name": "test/repo"
        }
    }

    # Calcular firma
    secret = "test_secret"
    signature = hmac.new(
        secret.encode(),
        json.dumps(payload).encode(),
        hashlib.sha256
    ).hexdigest()

    # Enviar request
    response = test_client.post(
        "/webhook/github",
        json=payload,
        headers={
            "X-Hub-Signature-256": f"sha256={signature}",
            "X-GitHub-Event": "pull_request"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Analysis completed"

def test_invalid_signature(test_client):
    response = test_client.post(
        "/webhook/github",
        json={"action": "opened"},
        headers={
            "X-Hub-Signature-256": "invalid",
            "X-GitHub-Event": "pull_request"
        }
    )
    
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_SIGNATURE" 