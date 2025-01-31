# Este módulo proporciona una interfaz unificada para interactuar con Supabase
# Implementa el patrón Singleton para la conexión a la base de datos

from supabase import create_client, Client
from infrastructure.config.settings import Settings
from functools import lru_cache

@lru_cache()
def get_supabase_client(url: str, key: str) -> Client:
    """
    Obtiene un cliente de Supabase cacheado.
    El cache se basa en la URL y key de Supabase.
    
    Args:
        url (str): URL de la instancia de Supabase
        key (str): Clave de servicio de Supabase
    
    Returns:
        Client: Cliente de Supabase configurado y cacheado
    """
    return create_client(url, key)

def get_client(settings: Settings) -> Client:
    """
    Obtiene un cliente de Supabase usando la configuración.
    Esta función es el punto principal de acceso al cliente.
    
    Args:
        settings (Settings): Configuración de la aplicación
    
    Returns:
        Client: Cliente de Supabase listo para usar
    """
    return get_supabase_client(
        url=settings.SUPABASE_URL,
        key=settings.SUPABASE_SERVICE_KEY
    ) 