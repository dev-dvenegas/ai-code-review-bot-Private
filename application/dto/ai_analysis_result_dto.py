# Este módulo define los DTOs para los resultados del análisis de IA
# Los DTOs ayudan a mantener la separación entre capas de la aplicación

from typing import List, Optional
from pydantic import BaseModel, Field

class CodeAnalysisComment(BaseModel):
    """DTO para comentarios de análisis de código"""
    file_path: str = Field(..., description="Ruta del archivo")
    line_number: int = Field(..., description="Número de línea")
    content: str = Field(..., description="Contenido del comentario")
    suggestion: Optional[str] = Field(None, description="Sugerencia de código")
    type: str = Field(..., description="Tipo de comentario: style|security|performance|bug")
    severity: str = Field(..., description="Severidad: low|medium|high")

class CodeAnalysisResult(BaseModel):
    """DTO para el resultado del análisis de código"""
    summary: str = Field(..., description="Resumen del análisis")
    score: float = Field(..., ge=0, le=100, description="Puntuación de calidad")
    comments: List[CodeAnalysisComment] = Field(..., description="Comentarios detallados")
    security_concerns: List[str] = Field(default_factory=list)
    performance_issues: List[str] = Field(default_factory=list)

class PRMetadataResult(BaseModel):
    """DTO para el resultado de la generación de metadata"""
    suggested_title: str = Field(..., description="Título sugerido")
    suggested_description: str = Field(..., description="Descripción sugerida")
    suggested_labels: List[str] = Field(..., description="Etiquetas sugeridas")
    reasoning: str = Field(..., description="Razonamiento detrás de las sugerencias") 