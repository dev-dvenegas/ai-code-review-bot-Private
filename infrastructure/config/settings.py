# Este módulo maneja la configuración de la aplicación usando Pydantic
# Permite validar y cargar variables de entorno de forma segura

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic.
    Todas las variables son cargadas desde el ambiente o archivo .env
    """
    # Configuración de GitHub App
    GITHUB_APP_ID: str
    GITHUB_APP_PRIVATE_KEY: str
    GITHUB_WEBHOOK_SECRET: str

    # Configuración de OpenAI
    OPENAI_API_KEY: str

    # Configuración de Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str

    # Variables opcionales con valores por defecto
    ENVIRONMENT: str = "development"
    DB_HOST: str = "localhost"
    DB_USER: str = "postgres"
    DB_NAME: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"

    class Config:
        env_file = ".env"  # Archivo de variables de entorno
        case_sensitive = True  # Las variables son sensibles a mayúsculas/minúsculas

@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene una instancia cacheada de la configuración.
    El cache evita leer el archivo .env en cada llamada.
    
    Returns:
        Settings: Configuración de la aplicación
    """
    return Settings() 