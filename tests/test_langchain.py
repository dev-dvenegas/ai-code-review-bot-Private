import pytest
from infrastructure.ai.langchain_orchestrator import LangChainOrchestrator
from domain.models.review import Review, ReviewStatus

@pytest.fixture
def mock_openai(mocker):
    mock = mocker.patch('langchain.chat_models.ChatOpenAI')
    mock.return_value.agenerate.return_value.generations = [[
        mocker.Mock(
            text="""
            {
                "title_suggestion": "feat: better title",
                "suggested_labels": ["enhancement"],
                "code_comments": [
                    {
                        "file": "test.py",
                        "line": 10,
                        "comment": "Consider using a more descriptive name",
                        "suggestion": "user_id instead of id"
                    }
                ],
                "summary": "Good PR with minor improvements needed",
                "score": 0.8
            }
            """
        )
    ]]
    return mock

async def test_analyze_pr(test_settings, mock_openai, mock_supabase):
    orchestrator = LangChainOrchestrator(test_settings, mock_supabase)
    
    result = await orchestrator.analyze_pr(
        diff_content="test diff",
        title="Test PR",
        body="Test description",
        current_labels=[],
        last_review=None
    )

    assert result.status == ReviewStatus.COMPLETED
    assert len(result.comments) == 1
    assert result.score == 0.8 