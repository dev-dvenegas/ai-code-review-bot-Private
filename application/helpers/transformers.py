# application/helpers/transformers.py

from application.dto.ai_analysis_result_dto import CodeAnalysisResult, PRMetadataResult
from domain.models.review import Review
import logging

logger = logging.getLogger(__name__)

def update_review_with_analysis(review: Review, code_analysis: CodeAnalysisResult, metadata: PRMetadataResult) -> None:
    """
    Actualiza una instancia de Review con los resultados del análisis de código y metadata.

    Args:
        review (Review): Instancia de Review que se actualizará.
        code_analysis (CodeAnalysisResult): Resultado del análisis de código que incluye:
            - summary: Resumen del análisis.
            - score: Puntuación calculada (0-100).
            - comments: Lista de comentarios estructurados con file_path, line_number, content, etc.
            - security_concerns: Lista de problemas de seguridad identificados.
            - performance_issues: Lista de problemas de rendimiento identificados.
        metadata (PRMetadataResult): Resultado de la generación de metadata que incluye:
            - suggested_title: Título sugerido para el PR.
            - suggested_description: Descripción sugerida para el PR.
            - suggested_labels: Lista de etiquetas sugeridas.
            - reasoning: Explicación del razonamiento detrás de las sugerencias.
    """
    # Actualizar información del análisis de código
    review.summary = code_analysis.summary
    review.score = code_analysis.score
    review.security_concerns = code_analysis.security_concerns
    review.performance_issues = code_analysis.performance_issues

    # Validar y filtrar comentarios
    for comment in code_analysis.comments:
        if not comment.file_path or comment.line_number < 1:
            logger.warning(f"Skipping invalid comment: {comment}")
            continue

        review.add_comment(
            file_path=comment.file_path,
            line_number=comment.line_number,
            content=f"[{comment.type.upper()} - {comment.severity}] {comment.content}",
            suggestion=comment.suggestion if comment.suggestion else None
        )

    # Actualizar metadata del PR
    review.suggested_title = metadata.suggested_title
    review.suggested_description = metadata.suggested_description
    review.suggested_labels = metadata.suggested_labels

    # Añadir un comentario general con el razonamiento de la metadata
    review.add_comment(
        file_path="",  # Comentario general
        line_number=0,
        content=f"Razonamiento de las sugerencias de metadata:\n{metadata.reasoning}",
        suggestion=None
    )

    # Marcar la revisión como completada
    review.complete(code_analysis.score)
