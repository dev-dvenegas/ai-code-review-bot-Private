# Este módulo define los DTOs para los resultados del análisis de IA
# Los DTOs ayudan a mantener la separación entre capas de la aplicación

from typing import List, Optional
from pydantic import BaseModel, Field

class AICommentDTO(BaseModel):
    """
    DTO para representar un comentario de revisión de código.
    Contiene la información necesaria para crear un comentario en GitHub.
    """
    file_path: str = Field(..., description="Ruta del archivo comentado")
    line_number: int = Field(..., description="Número de línea del comentario")
    content: str = Field(..., description="Contenido del comentario")
    suggestion: Optional[str] = Field(None, description="Sugerencia de código (opcional)")

class AIAnalysisResult(BaseModel):
    """
    DTO para el resultado completo del análisis de IA.
    Estructura la respuesta del modelo para ser procesada por la aplicación.
    """
    summary: str = Field(
        ...,
        description="Resumen general de la revisión"
    )
    score: float = Field(
        ...,
        description="Puntuación de calidad (0-100)",
        ge=0,
        le=100
    )
    comments: List[AICommentDTO] = Field(
        ...,
        description="Lista de comentarios específicos"
    )
    suggested_title: Optional[str] = Field(
        None,
        description="Sugerencia de título para el PR"
    )
    suggested_labels: List[str] = Field(
        default_factory=list,
        description="Etiquetas sugeridas para el PR"
    ) 