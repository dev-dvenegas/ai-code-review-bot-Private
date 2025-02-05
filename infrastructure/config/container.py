from dependency_injector import containers, providers
from infrastructure.config.settings import get_settings
from infrastructure.database.supabase_client import get_client
from infrastructure.database.repositories.prompt_repository import PromptRepository
from infrastructure.database.repositories.reviews_repository import ReviewsRepository
from infrastructure.database.repositories.pull_request_repository import PullRequestRepository
from infrastructure.database.repositories.pr_guidelines_repository import PRGuidelinesRepository
from infrastructure.github.github_service import GitHubService
from infrastructure.ai.langchain_orchestrator import LangchainOrchestrator
from application.use_cases.generate_pr_metadata import GeneratePRMetadataUseCase
from application.use_cases.analyze_pull_request import AnalyzePullRequestUseCase

class Container(containers.DeclarativeContainer):
    """
    Contenedor de dependencias centralizado para la aplicación.
    Se utiliza para inyectar configuraciones y servicios en diferentes capas.
    """

    # Proveedor Singleton para la configuración de la aplicación.
    config = providers.Singleton(get_settings)

    # Proveedor Singleton para el cliente de Supabase,
    # utilizando la configuración proporcionada.
    supabase_client = providers.Singleton(get_client, settings=config)

    # Proveedores para los repositorios que se encargarán del acceso a datos.
    prompt_repository = providers.Factory(PromptRepository, supabase=supabase_client)
    reviews_repository = providers.Factory(ReviewsRepository, supabase=supabase_client)
    pull_request_repository = providers.Factory(PullRequestRepository, supabase=supabase_client)
    pr_guidelines_repository = providers.Factory(PRGuidelinesRepository, supabase=supabase_client)

    # Proveedor para el servicio de GitHub, inyectando el App ID y la llave privada.
    github_service = providers.Singleton(
        GitHubService,
        app_id=config.provided.GITHUB_APP_ID,
        private_key=config.provided.GITHUB_APP_PRIVATE_KEY,
    )

    # Proveedor para el servicio de IA, inyectando la API key de OpenAI.
    ai_service = providers.Singleton(
        LangchainOrchestrator,
        openai_api_key=config.provided.OPENAI_API_KEY,
    )

    # Proveedor para el caso de uso que genera metadatos para los PR,
    # usando el repositorio de guías.
    metadata_generator = providers.Singleton(
        GeneratePRMetadataUseCase,
        pr_guidelines_repo=pr_guidelines_repository,
    )

    # Proveedor para el caso de uso principal de análisis de Pull Requests,
    # inyectando todos los repositorios y servicios necesarios.
    analyze_pull_request_use_case = providers.Singleton(
        AnalyzePullRequestUseCase,
        reviews_repository=reviews_repository,
        pull_request_repository=pull_request_repository,
        prompt_repository=prompt_repository,
        github_service=github_service,
        ai_service=ai_service,
        pr_guidelines_repository=pr_guidelines_repository,
        metadata_generator=metadata_generator,
    )
