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
    def __init__(self, client: Client = None):
        self.supabase = client or get_client(get_settings())
        self.table = "tech_analysis_prompts"
        self.rules_table = "tech_analysis_rules"

    async def get_active_prompt(self, name: str) -> PromptDTO:
        """
        Obtiene el prompt activo más reciente por nombre.
        
        Args:
            name: Nombre del prompt
            
        Returns:
            PromptDTO: Prompt activo encontrado
            
        Raises:
            PromptNotFoundException: Si no se encuentra el prompt
        """
        result = await self.supabase.table(self.table)\
            .select("*")\
            .eq("name", name)\
            .eq("is_active", True)\
            .order("version", desc=True)\
            .limit(1)\
            .execute()

        if not result.data:
            raise PromptNotFoundException(name)

        data = result.data[0]
        return PromptDTO(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            prompt_text=data["prompt_text"],
            is_active=data["is_active"],
            metadata=data["metadata"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )

    async def get_all_active_rules(self) -> List[RuleDTO]:
        """
        Obtiene todas las reglas activas ordenadas por prioridad.
        
        Returns:
            List[RuleDTO]: Lista de reglas activas
        """
        result = await self.supabase.table(self.rules_table)\
            .select("*")\
            .eq("is_active", True)\
            .order("priority")\
            .execute()

        return [
            RuleDTO(
                id=rule["id"],
                name=rule["name"],
                description=rule["description"],
                rule_type=rule["rule_type"],
                rule_content=rule["rule_content"],
                priority=rule["priority"],
                is_active=rule["is_active"],
                metadata=rule["metadata"],
                created_at=datetime.fromisoformat(rule["created_at"]),
                updated_at=datetime.fromisoformat(rule["updated_at"])
            )
            for rule in result.data
        ]

    async def create_prompt(self, dto: CreatePromptDTO) -> Prompt:
        """Crea un nuevo prompt"""
        data = {
            "name": dto.name,
            "version": dto.version,
            "prompt_text": dto.prompt_text,
            "metadata": dto.metadata,
            "is_active": True
        }
        
        result = await self.supabase.table(self.table)\
            .insert(data)\
            .execute()
            
        return Prompt(**result.data[0])

    async def update_prompt(self, prompt_id: str, dto: UpdatePromptDTO) -> Optional[Prompt]:
        """Actualiza un prompt existente"""
        data = {
            "prompt_text": dto.prompt_text,
            "is_active": dto.is_active,
            "metadata": dto.metadata,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = await self.supabase.table(self.table)\
            .update(data)\
            .eq("id", prompt_id)\
            .execute()
            
        if not result.data:
            return None
            
        return Prompt(**result.data[0])

    async def create_rule(self, dto: CreateRuleDTO) -> dict:
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
        
        result = await self.supabase.table(self.rules_table)\
            .insert(data)\
            .execute()
            
        return result.data[0]

    async def update_rule(self, rule_id: str, dto: UpdateRuleDTO) -> Optional[dict]:
        """Actualiza una regla existente"""
        data = {k: v for k, v in dto.dict().items() if v is not None}
        data["updated_at"] = datetime.utcnow().isoformat()
        
        result = await self.supabase.table(self.rules_table)\
            .update(data)\
            .eq("id", rule_id)\
            .execute()
            
        if not result.data:
            return None
            
        return result.data[0]

    async def get_prompts_by_name(self, name: str) -> List[Prompt]:
        """Obtiene todos los prompts con un nombre específico"""
        result = await self.supabase.table(self.table)\
            .select("*")\
            .eq("name", name)\
            .order("created_at", desc=True)\
            .execute()
            
        return [Prompt(**data) for data in result.data]

    async def get_rules_by_type(self, rule_type: str) -> List[dict]:
        """Obtiene todas las reglas de un tipo específico"""
        result = await self.supabase.table(self.rules_table)\
            .select("*")\
            .eq("rule_type", rule_type)\
            .order("priority", desc=True)\
            .execute()
            
        return result.data

    async def save_prompt(self, prompt: PromptDTO) -> PromptDTO:
        """
        Guarda un prompt en la base de datos.
        
        Args:
            prompt: Prompt a guardar
            
        Returns:
            PromptDTO: Prompt guardado con ID actualizado
            
        Raises:
            DuplicatePromptVersionException: Si ya existe la versión
        """
        # Verificar duplicados
        existing = self.supabase.table("tech_analysis_prompts") \
            .select("id") \
            .eq("name", prompt.name) \
            .eq("version", prompt.version) \
            .execute()

        if existing.data and (not prompt.id or existing.data[0]["id"] != prompt.id):
            raise DuplicatePromptVersionException(prompt.name, prompt.version)

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
            result = self.supabase.table("tech_analysis_prompts") \
                .update(prompt_data) \
                .eq("id", prompt.id) \
                .execute()
        else:
            # Crear nuevo
            prompt_data["created_at"] = datetime.utcnow().isoformat()
            result = self.supabase.table("tech_analysis_prompts") \
                .insert(prompt_data) \
                .execute()

        prompt.id = result.data[0]["id"]
        return prompt 