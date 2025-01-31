# Este módulo implementa el patrón Factory para crear instancias del caso de uso
# de análisis de Pull Requests con todas sus dependencias

from fastapi import Depends
from infrastructure.config.settings import get_settings, Settings
from infrastructure.database.supabase_client import get_client
from infrastructure.database.repositories.reviews_repository import ReviewsRepository
from infrastructure.database.repositories.prompt_repository import PromptRepository
from infrastructure.github.github_service import GitHubService
from infrastructure.ai.langchain_orchestrator import LangchainOrchestrator
from .analyze_pull_request import AnalyzePullRequestUseCase

def get_analyze_pr_use_case(
    settings: Settings = Depends(get_settings)
) -> AnalyzePullRequestUseCase:
    """
    Factory function para crear una instancia del caso de uso AnalyzePullRequest.
    Inyecta todas las dependencias necesarias.
    
    Args:
        settings: Configuración de la aplicación (inyectada por FastAPI)
        
    Returns:
        AnalyzePullRequestUseCase: Instancia configurada del caso de uso
    """
    # Crear cliente de base de datos
    supabase = get_client(settings)
    
    # Inicializar repositorios
    reviews_repo = ReviewsRepository(supabase)
    prompt_repo = PromptRepository(supabase)
    
    # Inicializar servicios
    github_service = GitHubService(
        app_id=settings.GITHUB_APP_ID,
        private_key=settings.GITHUB_APP_PRIVATE_KEY
    )
    
    ai_service = LangchainOrchestrator(
        openai_api_key=settings.OPENAI_API_KEY
    )
    
    # Crear y retornar el caso de uso con todas sus dependencias
    return AnalyzePullRequestUseCase(
        reviews_repository=reviews_repo,
        prompt_repository=prompt_repo,
        github_service=github_service,
        ai_service=ai_service
    ) 