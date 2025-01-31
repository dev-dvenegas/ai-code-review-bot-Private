# Este módulo define los DTOs relacionados con prompts y reglas de análisis
# Implementa la estructura de datos para la configuración del análisis de código

from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime

class PromptDTO(BaseModel):
    """
    DTO para representar un prompt de análisis.
    Contiene el texto y metadatos del prompt.
    """
    id: Optional[str] = None
    name: str = Field(..., description="Nombre identificador del prompt")
    version: str = Field(..., description="Versión del prompt")
    prompt_text: str = Field(..., description="Texto del prompt")
    is_active: bool = Field(True, description="Si el prompt está activo")
    metadata: Dict = Field(default_factory=dict, description="Metadatos adicionales")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class RuleDTO(BaseModel):
    """
    DTO para representar una regla de análisis.
    Define criterios específicos para revisar código.
    """
    id: Optional[str] = None
    name: str = Field(..., description="Nombre de la regla")
    description: Optional[str] = Field(None, description="Descripción detallada")
    rule_type: str = Field(..., description="Tipo de regla (style, security, etc)")
    rule_content: str = Field(..., description="Contenido/definición de la regla")
    priority: int = Field(1, description="Prioridad de aplicación")
    is_active: bool = Field(True, description="Si la regla está activa")
    metadata: Dict = Field(default_factory=dict, description="Metadatos adicionales")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class CreatePromptDTO(BaseModel):
    """
    DTO para crear un nuevo prompt.
    Contiene los campos necesarios para la creación inicial.
    """
    name: str = Field(..., description="Nombre identificador del prompt")
    version: str = Field(..., description="Versión del prompt")
    prompt_text: str = Field(..., description="Texto del prompt")
    metadata: Dict = Field(default_factory=dict, description="Metadatos adicionales")

class UpdatePromptDTO(BaseModel):
    """
    DTO para actualizar un prompt existente.
    Permite modificar solo ciertos campos del prompt.
    """
    prompt_text: str = Field(..., description="Nuevo texto del prompt")
    is_active: bool = Field(True, description="Estado de activación del prompt")
    metadata: Dict = Field(default_factory=dict, description="Nuevos metadatos")

class CreateRuleDTO(BaseModel):
    """
    DTO para crear una nueva regla.
    Incluye todos los campos necesarios para definir una regla.
    """
    name: str = Field(..., description="Nombre de la regla")
    description: Optional[str] = Field(None, description="Descripción de la regla")
    rule_type: str = Field(..., description="Tipo de regla")
    rule_content: str = Field(..., description="Contenido de la regla")
    priority: int = Field(1, description="Prioridad (1-5)")
    metadata: Dict = Field(default_factory=dict, description="Metadatos")

class UpdateRuleDTO(BaseModel):
    """
    DTO para actualizar una regla existente.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    """
    description: Optional[str] = None
    rule_content: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict] = None

class PromptWithRulesDTO(BaseModel):
    """
    DTO que combina un prompt con sus reglas asociadas.
    Representa la configuración completa para el análisis de código.
    """
    prompt: PromptDTO
    rules: List[RuleDTO] = Field(
        default_factory=list,
        description="Lista de reglas asociadas al prompt"
    ) 