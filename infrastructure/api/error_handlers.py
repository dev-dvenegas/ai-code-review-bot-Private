# Este módulo centraliza el manejo de errores de la aplicación
# Proporciona respuestas consistentes para diferentes tipos de errores

from fastapi import Request
from fastapi.responses import JSONResponse
from domain.exceptions import DomainException
from postgrest import APIError as PostgrestAPIError
from gotrue.errors import AuthApiError
from supabase._sync.client import SupabaseException

async def domain_exception_handler(request: Request, exc: DomainException):
    """
    Maneja errores específicos del dominio de la aplicación.
    Estos son errores esperados y controlados.
    
    Args:
        request: Petición HTTP que causó el error
        exc: Excepción de dominio que ocurrió
    """
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

async def supabase_error_handler(request: Request, exc: (SupabaseException, PostgrestAPIError, AuthApiError)):
    """
    Maneja errores relacionados con Supabase.
    Incluye errores de base de datos y autenticación.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "DATABASE_ERROR",
                "message": "Error en la base de datos",
                "details": str(exc)
            }
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """
    Maneja cualquier otro error no esperado.
    Proporciona una respuesta genérica para errores del servidor.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Error interno del servidor",
                "details": str(exc)
            }
        }
    ) 