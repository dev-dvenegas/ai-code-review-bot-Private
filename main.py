# FastAPI es un framework moderno para construir APIs con Python
# Está basado en Starlette para el manejo web y Pydantic para la validación de datos
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Para manejar CORS (Cross-Origin Resource Sharing)
from fastapi.openapi.utils import get_openapi  # Para personalizar la documentación OpenAPI
from interfaces.api.webhook_controller import router as webhook_router
from interfaces.api.prompt_controller import router as prompt_router
from interfaces.api.metrics_controller import router as metrics_router
from interfaces.api.guidelines_controller import router as guidelines_router
from domain.exceptions import DomainException
from infrastructure.api.error_handlers import (
    domain_exception_handler,
    supabase_error_handler,
    general_exception_handler
)

# Importamos las excepciones que queremos manejar de forma específica
from postgrest import APIError as PostgrestAPIError  # Errores de la base de datos
from gotrue.errors import AuthApiError  # Errores de autenticación
from supabase._sync.client import SupabaseException  # Errores generales de Supabase

# Importar e inicializar el logging
from infrastructure.logging.logging_config import setup_logging
from infrastructure.config.container import Container

setup_logging()
logger = logging.getLogger(__name__)

# Crear y configurar el contenedor de dependencias
container = Container()

# Configurar el wire para inyección automática en los módulos
container.wire(
    modules=[
        'interfaces.api.webhook_controller',
        'interfaces.api.prompt_controller',
        'interfaces.api.guidelines_controller',
        'application.use_cases.analyze_pull_request',
        'application.use_cases.generate_pr_metadata'
    ]
)

# Creamos la aplicación FastAPI con metadata
# Esta metadata se usa para generar la documentación automática
app = FastAPI(
    title="AI Pull Request Review Bot",
    description="""
    Un bot que analiza Pull Requests usando IA para proporcionar revisiones de código automáticas.
    
    ## Características
    
    * Análisis automático de Pull Requests
    * Gestión de prompts y reglas personalizables
    * Integración con GitHub Apps
    * Almacenamiento en Supabase
    """,
    version="1.0.0",
    docs_url="/docs",  # URL para la documentación Swagger UI
    redoc_url="/redoc"  # URL para la documentación ReDoc
)

# Asignar el contenedor a la aplicación
app.container = container

# Función para personalizar el esquema OpenAPI
# OpenAPI (anteriormente Swagger) es una especificación para documentar APIs REST
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="AI Pull Request Review Bot",
        version="1.0.0",
        description="API para gestionar revisiones automáticas de código",
        routes=app.routes
    )

    # Personalizamos los tags que se usan para agrupar endpoints
    openapi_schema["tags"] = [
        {
            "name": "prompts",
            "description": "Operaciones con prompts y reglas de revisión"
        },
        {
            "name": "webhook",
            "description": "Endpoints para webhooks de GitHub"
        }
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Asignamos nuestra función personalizada
app.openapi = custom_openapi

# Configuramos CORS para permitir peticiones desde otros dominios
# Esto es importante para APIs que serán consumidas desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, esto debería ser más restrictivo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registramos manejadores de excepciones personalizados
# Esto nos permite dar respuestas consistentes cuando ocurren errores
app.add_exception_handler(DomainException, domain_exception_handler)  # Errores de dominio
app.add_exception_handler(SupabaseException, supabase_error_handler)  # Errores de Supabase
app.add_exception_handler(PostgrestAPIError, supabase_error_handler)  # Errores de BD
app.add_exception_handler(AuthApiError, supabase_error_handler)  # Errores de auth
app.add_exception_handler(Exception, general_exception_handler)  # Otros errores

# Incluimos los routers que contienen nuestros endpoints
# Los routers nos permiten organizar endpoints relacionados
app.include_router(webhook_router, prefix="/webhook", tags=["webhook"])
app.include_router(prompt_router)
app.include_router(metrics_router)
app.include_router(guidelines_router)

@app.on_event("startup")
async def startup_event():
    """
    Se ejecuta cuando inicia la aplicación.
    Configura servicios necesarios.
    """
    # Inicializar contenedor y sus dependencias
    container.init_resources()
    logger.info("Aplicación iniciada correctamente")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Se ejecuta cuando se detiene la aplicación.
    Limpia recursos.
    """
    # Limpiar recursos del contenedor
    container.shutdown_resources()
    logger.info("Aplicación detenida correctamente")

# Endpoint simple para verificar que la API está funcionando
@app.get("/health")
async def health_check():
    return {"status": "healthy"} 