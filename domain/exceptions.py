from typing import Optional, Any

class DomainException(Exception):
    """
    Excepción base para errores del dominio.
    Proporciona una estructura común para todos los errores de negocio.
    """
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)

class PromptNotFoundException(DomainException):
    def __init__(self, prompt_id: str):
        super().__init__(
            code="PROMPT_NOT_FOUND",
            message=f"Prompt con ID {prompt_id} no encontrado"
        )

class RuleNotFoundException(DomainException):
    def __init__(self, rule_id: str):
        super().__init__(
            code="RULE_NOT_FOUND",
            message=f"Regla con ID {rule_id} no encontrada"
        )

class DuplicatePromptVersionException(DomainException):
    def __init__(self, name: str, version: str):
        super().__init__(
            code="DUPLICATE_PROMPT_VERSION",
            message=f"Ya existe un prompt con nombre {name} y versión {version}"
        )

class InvalidPromptDataException(DomainException):
    def __init__(self, details: str):
        super().__init__(
            code="INVALID_PROMPT_DATA",
            message="Datos de prompt inválidos",
            details={"details": details}
        )

class InvalidPullRequestException(DomainException):
    """Excepción para cuando un Pull Request no cumple con los requisitos"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            code="INVALID_PULL_REQUEST",
            message=message,
            details=details
        )

class InvalidPromptException(DomainException):
    """Excepción para cuando un prompt no es válido"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            code="INVALID_PROMPT",
            message=message,
            details=details
        )

class ReviewFailedException(DomainException):
    """Excepción para cuando falla el proceso de revisión"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            code="REVIEW_FAILED",
            message=message,
            details=details
        ) 