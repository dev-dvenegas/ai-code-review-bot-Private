# Este módulo define los DTOs para los resultados del análisis de Pull Requests
# Estructura los resultados para ser consumidos por la capa de presentación

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class FileAnalysisDTO(BaseModel):
    """
    DTO para representar el análisis de un archivo específico.
    Contiene los hallazgos y sugerencias para un archivo.
    """
    file_path: str = Field(..., description="Ruta del archivo analizado")
    issues_found: int = Field(..., description="Número de problemas encontrados")
    suggestions: List[str] = Field(default_factory=list, description="Lista de sugerencias")
    risk_level: str = Field(..., description="Nivel de riesgo (low, medium, high)")

class PRAnalysisResultDTO(BaseModel):
    """
    DTO para el resultado completo del análisis de un Pull Request.
    Incluye tanto el resumen como los detalles por archivo.
    """
    pr_number: int = Field(..., description="Número del Pull Request")
    repository: str = Field(..., description="Nombre del repositorio")
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    overall_score: float = Field(..., description="Puntuación general (0-100)")
    summary: str = Field(..., description="Resumen del análisis")
    files_analyzed: List[FileAnalysisDTO] = Field(
        default_factory=list,
        description="Análisis por archivo"
    )
    suggested_changes: List[str] = Field(
        default_factory=list,
        description="Cambios sugeridos"
    )
    critical_issues: List[str] = Field(
        default_factory=list,
        description="Problemas críticos encontrados"
    )
    performance_impact: Optional[str] = Field(
        None,
        description="Impacto estimado en rendimiento"
    )
    security_concerns: List[str] = Field(
        default_factory=list,
        description="Preocupaciones de seguridad identificadas"
    )

    class Config:
        """Configuración adicional del modelo"""
        schema_extra = {
            "example": {
                "pr_number": 123,
                "repository": "owner/repo",
                "overall_score": 85.5,
                "summary": "El PR muestra buena calidad general con algunas mejoras sugeridas",
                "files_analyzed": [
                    {
                        "file_path": "src/main.py",
                        "issues_found": 2,
                        "suggestions": ["Considerar usar type hints"],
                        "risk_level": "low"
                    }
                ]
            }
        } 