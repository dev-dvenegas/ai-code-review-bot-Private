# Este módulo maneja los endpoints relacionados con webhooks de GitHub
# Procesa los eventos y coordina las acciones correspondientes

import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, Depends
from domain.models.pull_request import PullRequest
from infrastructure.config.settings import get_settings
from application.use_cases.analyze_pull_request import AnalyzePullRequestUseCase
from application.use_cases.analyze_pull_request_factory import get_analyze_pr_use_case
from application.dto.webhook_dto import PullRequestWebhookDTO
import logging

# Configurar logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/github")
async def github_webhook(
    request: Request,
    settings = Depends(get_settings),
    analyze_pr: AnalyzePullRequestUseCase = Depends(get_analyze_pr_use_case),
):
    """
    Endpoint para recibir webhooks de GitHub.
    Verifica la firma y procesa eventos de Pull Request.
    
    Args:
        request: Petición HTTP con el webhook
        settings: Configuración de la aplicación
        analyze_pr: Caso de uso para analizar PRs
        
    Returns:
        dict: Resultado del procesamiento del webhook
        
    Raises:
        HTTPException: Si hay errores de validación o procesamiento
    """
    try:
        # Verificar firma del webhook si está configurada
        if settings.GITHUB_WEBHOOK_SECRET:
            signature = request.headers.get("X-Hub-Signature-256")
            if not signature:
                raise HTTPException(status_code=400, detail="No signature provided")
                
            body = await request.body()
            expected_signature = "sha256=" + hmac.new(
                settings.GITHUB_WEBHOOK_SECRET.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Obtener y validar payload
        payload = await request.json()
        event_type = request.headers.get("X-GitHub-Event")
        
        if event_type != "pull_request":
            logger.info(f"Evento ignorado: {event_type}")
            return {"message": "Event ignored"}

        # Parsear webhook
        webhook_data = PullRequestWebhookDTO(**payload)

        # Procesar solo eventos relevantes
        if webhook_data.action not in ["opened", "synchronize", "reopened", "labeled"]:
            logger.info(f"Acción ignorada: {webhook_data.action}")
            return {"message": f"Action {webhook_data.action} ignored"}

        # Convertir a modelo de dominio
        pull_request = PullRequest.from_github_payload(payload)

        # Ejecutar análisis
        logger.info(f"Iniciando análisis de PR #{pull_request.number}")
        result = await analyze_pr.execute(pull_request)

        return {
            "message": "Analysis completed",
            # "pull_request": pull_request.number,
            # "status": result.status
        }
        
    except Exception as e:
        logger.error(f"Error procesando webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))