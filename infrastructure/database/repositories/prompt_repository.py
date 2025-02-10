import logging
from typing import Optional, List
from datetime import datetime
from supabase import Client
from pydantic import BaseModel
from application.dto.prompt_dto import CreatePromptDTO, UpdatePromptDTO, CreateRuleDTO, UpdateRuleDTO, PromptDTO, RuleDTO
from infrastructure.database.supabase_client import get_client
from infrastructure.config.settings import get_settings
from domain.exceptions import (
    PromptNotFoundException,
    DuplicatePromptVersionException
)

logger = logging.getLogger(__name__)

class Prompt(BaseModel):
    id: str
    name: str
    version: str
    prompt_text: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    metadata: dict = {}

class PromptRepository:
    """
    Repositorio para gestionar prompts y reglas de análisis.
    Maneja la persistencia y recuperación de la configuración.
    """

    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = "tech_analysis_prompts"
        self.rules_table = "tech_analysis_rules"

    def get_active_prompt(self) -> PromptDTO:
        """
        Obtiene el único prompt activo en el sistema.
        
        Returns:
            PromptDTO: Prompt activo encontrado
            
        Raises:
            PromptNotFoundException: Si no hay un prompt activo
        """
        result = self.supabase.table(self.table)\
            .select("*")\
            .eq("is_active", True)\
            .execute()

        if not result.data:
            raise PromptNotFoundException("No active prompt found")

        data = result.data[0]
        return PromptDTO(**data)

    def get_all_active_rules(self) -> List[RuleDTO]:
        """
        Obtiene todas las reglas activas ordenadas por prioridad.
        
        Returns:
            List[RuleDTO]: Lista de reglas activas
        """
        result = self.supabase.table(self.rules_table)\
            .select("*")\
            .eq("is_active", True)\
            .order("priority")\
            .execute()

        return [RuleDTO(**rule) for rule in result.data]

    def create_prompt(self, dto: CreatePromptDTO) -> Prompt:
        """Crea un nuevo prompt"""
        data = {
            "name": dto.name,
            "version": dto.version,
            "prompt_text": dto.prompt_text,
            "metadata": dto.metadata,
            "is_active": True
        }
        
        result = self.supabase.table(self.table)\
            .insert(data)\
            .execute()
            
        return Prompt(**result.data[0])

    def update_prompt(self, prompt_id: str, dto: UpdatePromptDTO) -> Optional[Prompt]:
        """Actualiza un prompt existente"""
        data = {
            "prompt_text": dto.prompt_text,
            "is_active": dto.is_active,
            "metadata": dto.metadata,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = self.supabase.table(self.table)\
            .update(data)\
            .eq("id", prompt_id)\
            .execute()
            
        if not result.data:
            return None
            
        return Prompt(**result.data[0])

    def create_rule(self, dto: CreateRuleDTO) -> dict:
        """Crea una nueva regla"""
        data = {
            "name": dto.name,
            "description": dto.description,
            "rule_type": dto.rule_type,
            "rule_content": dto.rule_content,
            "priority": dto.priority,
            "metadata": dto.metadata,
            "is_active": True
        }
        
        result = self.supabase.table(self.rules_table)\
            .insert(data)\
            .execute()
            
        return result.data[0]

    def update_rule(self, rule_id: str, dto: UpdateRuleDTO) -> Optional[dict]:
        """Actualiza una regla existente"""
        data = {k: v for k, v in dto.dict().items() if v is not None}
        data["updated_at"] = datetime.utcnow().isoformat()
        
        result = self.supabase.table(self.rules_table)\
            .update(data)\
            .eq("id", rule_id)\
            .execute()
            
        if not result.data:
            return None
            
        return result.data[0]

    def get_prompts_by_name(self, name: str) -> List[Prompt]:
        """Obtiene todos los prompts con un nombre específico"""
        result = self.supabase.table(self.table)\
            .select("*")\
            .eq("name", name)\
            .order("created_at", desc=True)\
            .execute()
            
        return [Prompt(**data) for data in result.data]

    def get_rules_by_type(self, rule_type: str) -> List[dict]:
        """Obtiene todas las reglas de un tipo específico"""
        result = self.supabase.table(self.rules_table)\
            .select("*")\
            .eq("rule_type", rule_type)\
            .order("priority", desc=True)\
            .execute()
            
        return result.data

    def save_prompt(self, prompt: PromptDTO) -> PromptDTO:
        """
        Guarda un prompt en la base de datos.
        Si el prompt es activo, desactiva todos los demás.
        
        Args:
            prompt: Prompt a guardar
            
        Returns:
            PromptDTO: Prompt guardado con ID actualizado
        """
        # Si el prompt será activo, desactivar todos los demás
        if prompt.is_active:
            self.supabase.table(self.table)\
                .update({"is_active": False})\
                .neq("id", prompt.id if prompt.id else "")\
                .execute()

        # Preparar datos
        prompt_data = {
            "name": prompt.name,
            "version": prompt.version,
            "prompt_text": prompt.prompt_text,
            "is_active": prompt.is_active,
            "metadata": prompt.metadata,
            "updated_at": datetime.utcnow().isoformat()
        }

        if prompt.id:
            # Actualizar existente
            result = self.supabase.table(self.table)\
                .update(prompt_data)\
                .eq("id", prompt.id)\
                .execute()
        else:
            # Crear nuevo
            prompt_data["created_at"] = datetime.utcnow().isoformat()
            result = self.supabase.table(self.table)\
                .insert(prompt_data)\
                .execute()

        prompt.id = result.data[0]["id"]
        return prompt

    def get_latest_prompt_by_category(self, category: str) -> PromptDTO:
        """Obtiene el prompt más reciente de una categoría específica"""
        result = self.supabase.table(self.table)\
            .select("*")\
            .eq("category", category)\
            .order("version", desc=True)\
            .limit(1)\
            .execute()

        if not result.data:
            raise PromptNotFoundException(f"No prompt found for category: {category}")

        return PromptDTO(**result.data[0]) 