# Este módulo define los modelos relacionados con las revisiones de código
# Incluye la revisión principal y sus comentarios asociados

from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel

class ReviewStatus(Enum):
    """Estados posibles de una revisión"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class ReviewComment(BaseModel):
    """
    Modelo para los comentarios individuales en una revisión.
    Corresponde a la tabla tech_review_comments.
    """
    id: Optional[int] = None
    review_id: Optional[int] = None
    file_path: str
    line_number: int
    content: str
    suggestion: Optional[str] = None

class Review(BaseModel):
    """
    Modelo principal de una revisión de código.
    Corresponde a la tabla tech_reviews.
    """
    id: Optional[int] = None
    pull_request_id: int
    status: ReviewStatus
    summary: str
    score: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    suggested_title: Optional[str] = None
    suggested_labels: List[str] = []
    comments: List[ReviewComment] = []  # Relación con tech_review_comments

    def add_comment(self, file_path: str, line_number: int, content: str, suggestion: Optional[str] = None):
        """
        Agrega un nuevo comentario a la revisión.
        
        Args:
            file_path: Ruta del archivo comentado
            line_number: Número de línea del comentario
            content: Contenido del comentario
            suggestion: Sugerencia de código (opcional)
        """
        self.comments.append(
            ReviewComment(
                review_id=self.id,
                file_path=file_path,
                line_number=line_number,
                content=content,
                suggestion=suggestion
            )
        )

    def complete(self, score: float):
        """
        Marca la revisión como completada y asigna una puntuación.
        
        Args:
            score: Puntuación de la revisión (0-100)
        """
        self.status = ReviewStatus.COMPLETED
        self.score = score
        self.updated_at = datetime.utcnow()

    def fail(self, error_message: str):
        """
        Marca la revisión como fallida.
        
        Args:
            error_message: Mensaje de error que causó la falla
        """
        self.status = ReviewStatus.FAILED
        self.summary = f"Review failed: {error_message}"
        self.updated_at = datetime.utcnow() 