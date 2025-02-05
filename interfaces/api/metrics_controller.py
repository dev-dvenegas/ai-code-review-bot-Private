import logging

from fastapi import APIRouter
import time
import psutil  # Asegúrate de instalar psutil (pip install psutil)
import os

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
    responses={404: {"description": "No encontrado"}}
)

@router.get(
    "/",
    summary="Obtener métricas básicas",
    description="Retorna métricas básicas del sistema, como uso de CPU, memoria y tiempo de actividad."
)
async def get_metrics():
    uptime = time.time() - os.stat(".").st_ctime
    metrics = {
        "cpu_usage": psutil.cpu_percent(interval=1),
        "memory_usage": psutil.virtual_memory()._asdict(),
        "uptime_seconds": uptime
    }
    return metrics
