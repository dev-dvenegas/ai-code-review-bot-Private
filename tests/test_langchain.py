import pytest
from infrastructure.ai.langchain_orchestrator import LangchainOrchestrator
from domain.models.review import Review, ReviewStatus


@pytest.fixture
def mock_openai(mocker):
    # Se parchea el ChatOpenAI que se usa dentro de LangchainOrchestrator.
    mock = mocker.patch('langchain_community.chat_models.ChatOpenAI')
    mock_instance = mock.return_value
    mock_instance.agenerate.return_value = [[
        mocker.Mock(
            text="""
            {
                "summary": "Good PR with minor improvements needed",
                "score": 80,
                "comments": [
                    {
                        "file_path": "test.py",
                        "line_number": 10,
                        "content": "Consider using a more descriptive name",
                        "suggestion": "user_id instead of id"
                    }
                ],
                "suggested_title": "feat: better title",
                "suggested_description": "",
                "suggested_labels": ["enhancement"]
            }
            """
        )
    ]]
    return mock


@pytest.mark.asyncio
async def test_analyze_code(mock_openai):
    # Se crea una instancia del orquestador usando una API key dummy.
    orchestrator = LangchainOrchestrator(openai_api_key="dummy_api_key")

    # Preparar los parámetros de prueba
    diff = "test diff"
    prompt = (
        "Review the code diff:\n{diff}\n"
        "Company rules:\n{company_rules}\n"
        "Format instructions:\n{format_instructions}"
    )
    rules = []  # Para este test se usan reglas vacías
    context = {
        "repository": "owner/repo",
        "pr_number": 1,
        "pr_title": "Test PR",
        "pr_body": "Test description"
    }
    title_guidelines = ""
    description_template = ""
    label_guidelines = ""

    result = await orchestrator.analyze_code(
        diff=diff,
        prompt=prompt,
        rules=rules,
        context=context,
        title_guidelines=title_guidelines,
        description_template=description_template,
        label_guidelines=label_guidelines
    )

    # Se verifican los resultados esperados
    assert result.summary == "Good PR with minor improvements needed"
    assert result.score == 80
    assert len(result.comments) == 1
    assert result.suggested_title == "feat: better title"
    assert result.suggested_labels == ["enhancement"]
