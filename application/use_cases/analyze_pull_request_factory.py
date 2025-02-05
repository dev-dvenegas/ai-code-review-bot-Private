# Este módulo ha sido eliminado, ya que ahora se utiliza el contenedor para inyectar
# la instancia de AnalyzePullRequestUseCase mediante:
#     app.container.analyze_pull_request_use_case()

# import logging

# from fastapi import Depends

# from application.use_cases.generate_pr_metadata import GeneratePRMetadataUseCase
# from infrastructure.config.settings import get_settings, Settings
# from infrastructure.database.supabase_client import get_client
# from infrastructure.database.repositories.reviews_repository import ReviewsRepository
# from infrastructure.database.repositories.prompt_repository import PromptRepository
# from infrastructure.database.repositories.pull_request_repository import PullRequestRepository
# from infrastructure.database.repositories.pr_guidelines_repository import PRGuidelinesRepository
# from infrastructure.github.github_service import GitHubService
# from infrastructure.ai.langchain_orchestrator import LangchainOrchestrator
# from application.use_cases.analyze_pull_request import AnalyzePullRequestUseCase

# logger = logging.getLogger(__name__)

# def get_analyze_pr_use_case(
#     settings: Settings = Depends(get_settings)
# ) -> AnalyzePullRequestUseCase:
#     """
#     Factory function para crear una instancia del caso de uso AnalyzePullRequest.
#     Inyecta todas las dependencias necesarias.
    
#     Args:
#         settings: Configuración de la aplicación (inyectada por FastAPI)
        
#     Returns:
#         AnalyzePullRequestUseCase: Instancia configurada del caso de uso
#     """
#     # Crear cliente de base de datos
#     supabase = get_client(settings)
    
#     # Inicializar repositorios
#     reviews_repo = ReviewsRepository(supabase)
#     pr_repo = PullRequestRepository(supabase)
#     prompt_repo = PromptRepository(supabase)
#     pr_guidelines_repository = PRGuidelinesRepository(supabase)

#     # Inicializar servicios
#     github_service = GitHubService(
#         app_id=settings.GITHUB_APP_ID,
#         private_key=settings.GITHUB_APP_PRIVATE_KEY
#     )
    
#     ai_service = LangchainOrchestrator(
#         openai_api_key=settings.OPENAI_API_KEY
#     )

#     # Crear el caso de uso de generación de metadatos
#     metadata_generator = GeneratePRMetadataUseCase(pr_guidelines_repository)

#     # Crear y retornar el caso de uso con todas sus dependencias
#     return AnalyzePullRequestUseCase(
#         reviews_repository=reviews_repo,
#         pull_request_repository=pr_repo,
#         prompt_repository=prompt_repo,
#         github_service=github_service,
#         ai_service=ai_service,
#         pr_guidelines_repository=pr_guidelines_repository,
#         metadata_generator=metadata_generator
#     )