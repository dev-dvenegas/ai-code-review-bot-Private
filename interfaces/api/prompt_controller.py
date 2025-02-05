import logging

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from application.dto.prompt_dto import (
    CreatePromptDTO, UpdatePromptDTO,
    CreateRuleDTO, UpdateRuleDTO
)
from infrastructure.database.repositories.prompt_repository import PromptRepository, Prompt
from infrastructure.config.settings import get_settings
from infrastructure.database.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["prompts"])

async def get_prompt_repository():
    settings = get_settings()
    supabase = get_supabase_client(settings)
    return PromptRepository(supabase)

@router.post(
    "/prompts",
    response_model=Prompt,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo prompt",
    description="""
    Crea un nuevo prompt para el análisis de código.
    - Requiere un nombre único y versión
    - El prompt_text debe contener las variables {company_rules} y {format_instructions}
    """
)
async def create_prompt(
    dto: CreatePromptDTO,
    repo: PromptRepository = Depends(get_prompt_repository)
):
    """
    Crea un nuevo prompt con las siguientes reglas:
    - No puede existir un prompt con el mismo nombre y versión
    - El prompt se crea inicialmente como activo
    """
    return await repo.create_prompt(dto)

@router.put("/prompts/{prompt_id}", response_model=Prompt)
async def update_prompt(
    prompt_id: str,
    dto: UpdatePromptDTO,
    repo: PromptRepository = Depends(get_prompt_repository)
):
    """Actualiza un prompt existente"""
    prompt = await repo.update_prompt(prompt_id, dto)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    return prompt

@router.get("/prompts/{name}", response_model=List[Prompt])
async def get_prompts_by_name(
    name: str,
    repo: PromptRepository = Depends(get_prompt_repository)
):
    """Obtiene todos los prompts con un nombre específico"""
    return await repo.get_prompts_by_name(name)

@router.post("/rules")
async def create_rule(
    dto: CreateRuleDTO,
    repo: PromptRepository = Depends(get_prompt_repository)
):
    """Crea una nueva regla"""
    return await repo.create_rule(dto)

@router.put("/rules/{rule_id}")
async def update_rule(
    rule_id: str,
    dto: UpdateRuleDTO,
    repo: PromptRepository = Depends(get_prompt_repository)
):
    """Actualiza una regla existente"""
    rule = await repo.update_rule(rule_id, dto)
    if not rule:
        raise HTTPException(status_code=404, detail="Regla no encontrada")
    return rule

@router.get("/rules/type/{rule_type}")
async def get_rules_by_type(
    rule_type: str,
    repo: PromptRepository = Depends(get_prompt_repository)
):
    """Obtiene todas las reglas de un tipo específico"""
    return await repo.get_rules_by_type(rule_type)

@router.get("/rules/active")
async def get_active_rules(
    repo: PromptRepository = Depends(get_prompt_repository)
):
    """Obtiene todas las reglas activas"""
    return await repo.get_all_active_rules() 