# application/helpers/transformers.py

from application.dto.ai_analysis_result_dto import AIAnalysisResult
from domain.models.review import Review

def update_review_with_analysis(review: Review, analysis: AIAnalysisResult) -> None:
    """
    Actualiza una instancia de Review con los resultados obtenidos del análisis de IA.

    Esta función realiza las siguientes tareas:
      - Actualiza el resumen y la puntuación de la revisión.
      - Actualiza las sugerencias de título, descripción y etiquetas.
      - Itera sobre cada comentario generado por la IA y lo añade a la revisión.

    Args:
        review (Review): Instancia de Review que se actualizará.
        analysis (AIAnalysisResult): Resultado del análisis de IA, que incluye:
            - summary: Resumen del análisis.
            - score: Puntuación calculada (0-100).
            - comments: Lista de comentarios estructurados con file_path, line_number, content y suggestion.
            - suggested_title: Título sugerido.
            - suggested_description: Descripción sugerida.
            - suggested_labels: Lista de etiquetas sugeridas.
    """
    # Actualizar el resumen y la puntuación
    review.summary = analysis.summary
    review.score = analysis.score

    # Actualizar sugerencias para título, descripción y etiquetas
    review.suggested_title = analysis.suggested_title
    review.suggested_description = analysis.suggested_description
    review.suggested_labels = analysis.suggested_labels

    # Iterar sobre los comentarios generados por la IA y añadirlos a la revisión
    for comment in analysis.comments:
        review.add_comment(
            file_path=comment.file_path,
            line_number=comment.line_number,
            content=comment.content,
            suggestion=comment.suggestion
        )

    # Marcar la revisión como completada utilizando la puntuación obtenida
    review.complete(analysis.score)
