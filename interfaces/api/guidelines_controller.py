import logging

from fastapi import APIRouter, HTTPException, status, Request
from typing import List
from domain.models.pr_guidelines import PRTitleGuideline, PRDescriptionTemplate, PRLabel

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/guidelines",
    tags=["guidelines"],
    responses={404: {"description": "No se encontró el recurso"}}
)

@router.get(
    "/titles",
    response_model=List[PRTitleGuideline],
    summary="Listar guías de título activas",
    description="Obtiene la lista de todas las guías de título que se encuentran activas en el sistema."
)
def list_title_guidelines(request: Request):
    """
    Obtiene la lista de todas las guías de título que se encuentran activas en el sistema.
    """
    repo = request.app.container.pr_guidelines_repository()
    try:
        return repo.get_active_title_guidelines()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/templates",
    response_model=PRDescriptionTemplate,
    summary="Obtener plantilla de descripción activa",
    description="Retorna la plantilla de descripción activa para los pull requests."
)
def get_description_template(request: Request):
    """
    Obtiene la plantilla de descripción activa para los pull requests.
    """
    repo = request.app.container.pr_guidelines_repository()
    template = repo.get_active_template()
    if not template:
        raise HTTPException(status_code=404, detail="No se encontró plantilla activa")
    return template

@router.get(
    "/labels",
    response_model=List[PRLabel],
    summary="Listar etiquetas activas",
    description="Obtiene la lista de etiquetas activas para los pull requests."
)
def list_labels(request: Request):
    """
    Obtiene la lista de etiquetas activas para los pull requests.
    """
    repo = request.app.container.pr_guidelines_repository()
    try:
        return repo.get_active_labels()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
