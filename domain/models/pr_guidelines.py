from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator

class PRTitleGuideline(BaseModel):
    """Modelo para las reglas de títulos de PR"""
    id: Optional[str] = None
    prefix: str
    description: str
    is_active: bool = True
    min_length: int = Field(default=10, ge=1)
    max_length: int = Field(default=72, ge=10)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('max_length')
    def validate_max_length(cls, v, values):
        if 'min_length' in values and v < values['min_length']:
            raise ValueError('max_length debe ser mayor o igual que min_length')
        return v

    def validate_title(self, title: str) -> bool:
        """Valida si un título cumple con las guías"""
        if not title.startswith(self.prefix + ":"):
            return False
        
        title_length = len(title)
        return self.min_length <= title_length <= self.max_length

class PRDescriptionTemplate(BaseModel):
    """Modelo para plantillas de descripción de PR"""
    id: Optional[str] = None
    name: str
    template_content: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def apply_template(self, context: dict) -> str:
        """Aplica la plantilla con el contexto proporcionado"""
        return self.template_content.format(**context)

class PRLabel(BaseModel):
    """Modelo para etiquetas de PR"""
    id: Optional[str] = None
    name: str
    description: str
    color: str = "#CCCCCC"
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('color')
    def validate_color(cls, v):
        if not v.startswith('#') or len(v) != 7:
            raise ValueError('El color debe estar en formato hexadecimal (#RRGGBB)')
        return v 