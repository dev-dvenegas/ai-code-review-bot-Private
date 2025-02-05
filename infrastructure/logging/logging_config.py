import logging
import logging.config

# Diccionario de configuración para el logging.
# Define formateadores, controladores (handlers) y la configuración raíz.
LOGGING_CONFIG = {
    "version": 1,  # Versión del esquema de configuración.
    "disable_existing_loggers": False,  # Permite que los loggers existentes sigan funcionando.
    "formatters": {
        # Formateador "standard" para definir el formato de salida.
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        # Handler para la consola, de nivel DEBUG.
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard"
        },
        # Handler para un archivo, de nivel INFO.
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "app.log",  # Archivo donde se guardarán los logs.
            "formatter": "standard",
        },
    },
    # Configuración del logger raíz, que utiliza ambos handlers.
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },
}

def setup_logging():
    """
    Inicializa la configuración de logging utilizando el diccionario LOGGING_CONFIG.
    Esta función debe llamarse al inicio de la aplicación para que todos los módulos
    utilicen la misma configuración de logging.
    """
    logging.config.dictConfig(LOGGING_CONFIG)
