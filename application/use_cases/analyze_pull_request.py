# Este módulo implementa el caso de uso principal para analizar Pull Requests
# Coordina la interacción entre servicios y maneja el flujo de análisis

from typing import List
from datetime import datetime
import logging

from application.dto.ai_analysis_result_dto import AIAnalysisResult
from application.helpers.transformers import update_review_with_analysis
from application.use_cases.generate_pr_metadata import GeneratePRMetadataUseCase
from domain.models.pull_request import PullRequest
from domain.models.review import Review, ReviewStatus, ReviewComment
from domain.exceptions import ReviewFailedException
from infrastructure.database.repositories.reviews_repository import ReviewsRepository
from infrastructure.database.repositories.prompt_repository import PromptRepository
from infrastructure.github.github_service import GitHubService
from infrastructure.ai.langchain_orchestrator import LangchainOrchestrator
from infrastructure.database.repositories.pull_request_repository import PullRequestRepository
from infrastructure.database.repositories.pr_guidelines_repository import PRGuidelinesRepository

logger = logging.getLogger(__name__)

class AnalyzePullRequestUseCase:
    def __init__(
        self,
        reviews_repository: ReviewsRepository,
        pull_request_repository: PullRequestRepository,
        prompt_repository: PromptRepository,
        github_service: GitHubService,
        ai_service: LangchainOrchestrator,
        pr_guidelines_repository: PRGuidelinesRepository,
        metadata_generator: GeneratePRMetadataUseCase,  # Nueva dependencia inyectada

    ):
        """
        Inicializa el caso de uso con sus dependencias.

        Args:
            reviews_repository: Repositorio para gestionar revisiones
            pull_request_repository: Repositorio para gestionar Pull Requests
            prompt_repository: Repositorio para obtener prompts y reglas
            github_service: Servicio para interactuar con GitHub
            ai_service: Servicio para realizar análisis con IA
        """
        self.reviews_repo = reviews_repository
        self.pr_repo = pull_request_repository
        self.prompt_repo = prompt_repository
        self.github = github_service
        self.pr_guidelines_repo = pr_guidelines_repository
        self.metadata_generator = metadata_generator
        self.ai = ai_service

    """
    Caso de uso principal para analizar Pull Requests.
    Coordina el proceso completo de análisis y revisión.
    """

    async def execute(self, pull_request: PullRequest) -> Review:
        """
        Ejecuta el análisis completo de un Pull Request.
        
        Args:
            pull_request: Pull Request a analizar
            
        Returns:
            Review: Resultado del análisis
            
        Raises:
            ReviewFailedException: Si ocurre un error durante el análisis
        """
        try:
            # Guardar PR y obtener ID interno
            pr_internal_id = self.pr_repo.save(pull_request)

            # Crear review inicial con el ID interno de tech_prs
            review = Review(
                pull_request_id=pr_internal_id,  # Usar el ID interno, no el github_id
                status=ReviewStatus.IN_PROGRESS,
                summary="",
                score=0.0,
                comments=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Obtener cambios del PR
            diff = await self.github.get_pull_request_diff(
                pull_request.repository,
                pull_request.number
            )

            # Si el diff es bytes, decodificarlo a UTF-8
            if isinstance(diff, bytes):
                diff = diff.decode("utf-8")

            # Obtener prompt activo y reglas
            prompt_dto = self.prompt_repo.get_active_prompt()
            prompt_text = prompt_dto.prompt_text  # Extraemos el texto del prompt
            rules = self.prompt_repo.get_all_active_rules()

            # Recuperar guías de título, plantilla de descripción y lineamientos de etiquetas
            active_title_guidelines = self.pr_guidelines_repo.get_active_title_guidelines()
            title_guidelines_str = "\n".join(
                f"{tg.prefix}: {tg.description} (min: {tg.min_length}, max: {tg.max_length})"
                for tg in active_title_guidelines
            )

            active_description_template = self.pr_guidelines_repo.get_active_template()
            description_template_str = (
                active_description_template.template_content
                if active_description_template else ""
            )

            active_labels = self.pr_guidelines_repo.get_active_labels()
            label_guidelines_str = "\n".join(
                f"{label.name}: {label.description}" for label in active_labels
            )

            # Definir contexto adicional
            context = {
                "repository": pull_request.repository,
                "pr_number": pull_request.number,
                "pr_title": pull_request.title,
                "pr_body": pull_request.body
            }

            # Realizar análisis con IA
            analysis_result = await self.ai.analyze_code(
                diff=diff,
                prompt=prompt_text,
                rules=rules,
                context=context,
                title_guidelines=title_guidelines_str,
                description_template=description_template_str,
                label_guidelines=label_guidelines_str
            )

            pull_request = await self.metadata_generator.execute(pull_request)

            # Actualizar la instancia 'review' usando el transformer
            update_review_with_analysis(review, analysis_result)

            # Guardar en base de datos
            await self.reviews_repo.save(review)

            # Publicar comentarios en GitHub
            await self.github.create_review_comments(
                repository=pull_request.repository,
                pr_number=pull_request.number,
                review=review,
                diff=diff,
            )

            # Crear un comentario adicional con la metadata sugerida para que el usuario la revise
            metadata = {
                "suggested_title": review.suggested_title,
                "suggested_description": review.suggested_description,
                "suggested_labels": ", ".join(review.suggested_labels)
            }

            await self.github.create_metadata_comment(
                repository=pull_request.repository,
                pr_number=pull_request.number,
                metadata=metadata
            )
            return review

        except Exception as e:
            logger.error(f"Error analizando PR: {str(e)}", exc_info=True)
            if review:
                review.fail(str(e))
                await self.reviews_repo.save(review)
            raise ReviewFailedException(str(e))
