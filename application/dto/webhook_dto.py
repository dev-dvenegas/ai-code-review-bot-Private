# Este módulo define los DTOs para manejar los webhooks de GitHub
# Estructura los datos recibidos en los eventos de webhook

from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class GitHubUserDTO(BaseModel):
    """
    DTO para representar un usuario de GitHub.
    Contiene información básica del usuario.
    """
    login: str = Field(..., description="Nombre de usuario en GitHub")
    id: int = Field(..., description="ID único del usuario")
    type: str = Field(..., description="Tipo de usuario (User, Bot, etc)")

class GitHubRepoDTO(BaseModel):
    """
    DTO para representar un repositorio de GitHub.
    Contiene información básica del repositorio.
    """
    id: int = Field(..., description="ID único del repositorio")
    name: str = Field(..., description="Nombre del repositorio")
    full_name: str = Field(..., description="Nombre completo (owner/repo)")
    private: bool = Field(..., description="Si el repositorio es privado")
    default_branch: str = Field(..., description="Rama principal")

class PullRequestWebhookDTO(BaseModel):
    """
    DTO para los eventos de webhook relacionados con Pull Requests.
    Estructura la información relevante del evento.
    """
    action: str = Field(..., description="Acción que disparó el evento")
    number: int = Field(..., description="Número del PR")
    pull_request: Dict = Field(..., description="Datos completos del PR")
    repository: GitHubRepoDTO
    sender: GitHubUserDTO
    installation: Optional[Dict] = Field(None, description="Datos de instalación de la GitHub App")

    class Config:
        """Configuración adicional del modelo"""
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "action": "opened",
                "number": 1,
                "pull_request": {
                    "id": 123,
                    "number": 1,
                    "title": "Feature: Add new functionality",
                    "state": "open"
                },
                "repository": {
                    "id": 456,
                    "name": "my-repo",
                    "full_name": "owner/my-repo",
                    "private": False,
                    "default_branch": "main"
                },
                "sender": {
                    "login": "username",
                    "id": 789,
                    "type": "User"
                }
            }
        } 