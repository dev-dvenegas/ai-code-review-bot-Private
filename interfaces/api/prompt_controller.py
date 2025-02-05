import logging
from fastapi import APIRouter, HTTPException, status, Request
from typing import List
from application.dto.prompt_dto import (
    CreatePromptDTO, UpdatePromptDTO,
    CreateRuleDTO, UpdateRuleDTO
)
from infrastructure.database.repositories.prompt_repository import Prompt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["prompts"])

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
async def create_prompt(request: Request, dto: CreatePromptDTO):
    """
    Crea un nuevo prompt con las siguientes reglas:
    - No puede existir un prompt con el mismo nombre y versión
    - El prompt se crea inicialmente como activo
    """
    repo = request.app.container.prompt_repository()
    return await repo.create_prompt(dto)

@router.put("/prompts/{prompt_id}", response_model=Prompt)
async def update_prompt(request: Request, prompt_id: str, dto: UpdatePromptDTO):
    """
    Actualiza un prompt existente con las siguientes reglas:
    - No puede existir un prompt con el mismo nombre y versión
    - El prompt se crea inicialmente como activo
    """
    repo = request.app.container.prompt_repository()
    prompt = await repo.update_prompt(prompt_id, dto)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    return prompt

@router.get("/prompts/{name}", response_model=List[Prompt])
async def get_prompts_by_name(request: Request, name: str):
    """
    Obtiene todos los prompts que coinciden con el nombre proporcionado.
    """
    repo = request.app.container.prompt_repository()
    return await repo.get_prompts_by_name(name)

@router.post("/rules")
async def create_rule(request: Request, dto: CreateRuleDTO):
    """
    Crea una nueva regla para un prompt existente.
    """
    repo = request.app.container.prompt_repository()
    return await repo.create_rule(dto)

@router.put("/rules/{rule_id}")
async def update_rule(request: Request, rule_id: str, dto: UpdateRuleDTO):
    """
    Actualiza una regla existente.
    """
    repo = request.app.container.prompt_repository()
    rule = await repo.update_rule(rule_id, dto)
    if not rule:
        raise HTTPException(status_code=404, detail="Regla no encontrada")
    return rule

@router.get("/rules/type/{rule_type}")
async def get_rules_by_type(request: Request, rule_type: str):
    """
    Obtiene todas las reglas de un tipo específico.
    """
    repo = request.app.container.prompt_repository()
    return await repo.get_rules_by_type(rule_type)

@router.get("/rules/active")
async def get_active_rules(request: Request):
    """
    Obtiene todas las reglas activas.
    """
    repo = request.app.container.prompt_repository()
    return await repo.get_all_active_rules() 