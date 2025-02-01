# Este módulo define el modelo de dominio para Pull Requests
# Encapsula la lógica y estructura de un PR en nuestra aplicación

from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel

class PullRequestStatus(str, Enum):
    """
    Estados posibles de un Pull Request.
    Usa str como base para facilitar la serialización.
    """
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"
    DRAFT = "draft"

class PullRequest(BaseModel):
    """
    Modelo que representa un Pull Request.
    Contiene toda la información necesaria para realizar el análisis.
    """
    github_id: int
    number: int
    title: str
    body: Optional[str]
    status: PullRequestStatus
    author: str
    repository: str
    base_branch: str
    head_branch: str
    created_at: datetime
    updated_at: datetime
    labels: List[str] = []
    suggested_labels: List[str] = []
    suggested_title: str

    @classmethod
    def from_github_payload(cls, payload: dict) -> "PullRequest":
        """
        Crea una instancia de PullRequest desde un webhook de GitHub.
        
        Args:
            payload: Datos del webhook de GitHub
            
        Returns:
            PullRequest: Nueva instancia con los datos del webhook
        """
        pr_data = payload["pull_request"]
        return cls(
            github_id=pr_data["id"],
            number=pr_data["number"],
            title=pr_data["title"],
            body=pr_data.get("body"),
            status=PullRequestStatus(pr_data["state"]),
            author=pr_data["user"]["login"],
            repository=payload["repository"]["full_name"],
            base_branch=pr_data["base"]["ref"],
            head_branch=pr_data["head"]["ref"],
            created_at=datetime.fromisoformat(pr_data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(pr_data["updated_at"].replace("Z", "+00:00")),
            labels=[label["name"] for label in pr_data.get("labels", [])],
            suggested_title='',
            suggested_labels=[],
        )

    def is_ready_for_review(self) -> bool:
        """
        Verifica si el PR está listo para ser revisado.
        
        Returns:
            bool: True si el PR está abierto y no es borrador
        """
        return self.status == PullRequestStatus.OPEN and not self.is_draft()

    def is_draft(self) -> bool:
        """
        Verifica si el PR está en estado borrador.
        
        Returns:
            bool: True si el PR es un borrador
        """
        return self.status == PullRequestStatus.DRAFT 