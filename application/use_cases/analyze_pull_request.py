# Este módulo implementa el caso de uso principal para analizar Pull Requests
# Coordina la interacción entre servicios y maneja el flujo de análisis

from typing import List
from datetime import datetime
import logging
from domain.models.pull_request import PullRequest
from domain.models.review import Review, ReviewStatus, ReviewComment
from domain.exceptions import ReviewFailedException
from infrastructure.database.repositories.reviews_repository import ReviewsRepository
from infrastructure.database.repositories.prompt_repository import PromptRepository
from infrastructure.github.github_service import GitHubService
from infrastructure.ai.langchain_orchestrator import LangchainOrchestrator
from application.dto.ai_analysis_result_dto import AIAnalysisResult

logger = logging.getLogger(__name__)

class AnalyzePullRequestUseCase:
    """
    Caso de uso principal para analizar Pull Requests.
    Coordina el proceso completo de análisis y revisión.
    """

    def __init__(
        self,
        reviews_repository: ReviewsRepository,
        prompt_repository: PromptRepository,
        github_service: GitHubService,
        ai_service: LangchainOrchestrator
    ):
        """
        Inicializa el caso de uso con sus dependencias.
        
        Args:
            reviews_repository: Repositorio para gestionar revisiones
            prompt_repository: Repositorio para obtener prompts y reglas
            github_service: Servicio para interactuar con GitHub
            ai_service: Servicio para realizar análisis con IA
        """
        self.reviews_repo = reviews_repository
        self.prompt_repo = prompt_repository
        self.github = github_service
        self.ai = ai_service

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
            # Crear review inicial
            review = Review(
                pull_request_id=pull_request.github_id,
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
            
            # Obtener prompt y reglas activas
            prompt = await self.prompt_repo.get_active_prompt("code_review_prompt")
            rules = await self.prompt_repo.get_all_active_rules()
            
            # Realizar análisis con IA
            analysis_result = await self.ai.analyze_code(
                diff=diff,
                prompt=prompt,
                rules=rules,
                context={
                    "repository": pull_request.repository,
                    "pr_number": pull_request.number,
                    "pr_title": pull_request.title,
                    "pr_body": pull_request.body
                }
            )
            
            # Actualizar review con resultados
            self._update_review_with_analysis(review, analysis_result)
            
            # Guardar en base de datos
            await self.reviews_repo.save(review)
            
            # Publicar comentarios en GitHub
            await self.github.create_review_comments(
                repository=pull_request.repository,
                pr_number=pull_request.number,
                review=review
            )
            
            return review
            
        except Exception as e:
            logger.error(f"Error analizando PR: {str(e)}", exc_info=True)
            if review:
                review.fail(str(e))
                await self.reviews_repo.save(review)
            raise ReviewFailedException(str(e))

    def _update_review_with_analysis(self, review: Review, analysis: AIAnalysisResult):
        """
        Actualiza una revisión con los resultados del análisis.
        
        Args:
            review: Revisión a actualizar
            analysis: Resultados del análisis de IA
        """
        review.summary = analysis.summary
        review.score = analysis.score
        review.suggested_title = analysis.suggested_title
        review.suggested_labels = analysis.suggested_labels
        
        for comment in analysis.comments:
            review.add_comment(
                file_path=comment.file_path,
                line_number=comment.line_number,
                content=comment.content,
                suggestion=comment.suggestion
            )
        
        review.complete(analysis.score) 