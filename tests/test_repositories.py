import pytest
from infrastructure.database.repositories.prompt_repository import PromptRepository
from infrastructure.database.repositories.reviews_repository import ReviewsRepository
from datetime import datetime

async def test_save_prompt(mock_supabase):
    repo = PromptRepository(mock_supabase)
    
    # Configurar mock
    mock_supabase.table().insert().execute.return_value.data = [{
        "id": "123",
        "name": "test",
        "version": "1.0",
        "prompt_text": "test",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }]

    result = await repo.create_prompt({
        "name": "test",
        "version": "1.0",
        "prompt_text": "test"
    })

    assert result.id == "123"
    assert result.name == "test"

async def test_get_active_prompt(mock_supabase):
    repo = PromptRepository(mock_supabase)
    
    # Configurar mock
    mock_supabase.table().select().eq().eq().order().limit().execute.return_value.data = [{
        "id": "123",
        "name": "test",
        "version": "1.0",
        "prompt_text": "test",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }]

    result = await repo.get_active_prompt("test")
    
    assert result is not None
    assert result.name == "test" 