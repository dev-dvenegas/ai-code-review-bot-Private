import logging
from typing import Optional
from datetime import datetime
from supabase import Client
from domain.models.pull_request import PullRequest, PullRequestStatus

logger = logging.getLogger(__name__)

class PullRequestRepository:
    """
    Repositorio para gestionar Pull Requests en la base de datos.
    """

    def __init__(self, supabase: Client):
        self.supabase = supabase

    def save(self, pull_request: PullRequest) -> int:
        """
        Guarda o actualiza un Pull Request en la base de datos.
        
        Args:
            pull_request: Pull Request a guardar
            
        Returns:
            int: ID interno del PR en la base de datos
        """
        pr_data = {
            "github_id": pull_request.github_id,
            "number": pull_request.number,
            "title": pull_request.title,
            "body": pull_request.body,
            "status": pull_request.status.value,
            "author": pull_request.author,
            "repository": pull_request.repository,
            "base_branch": pull_request.base_branch,
            "head_branch": pull_request.head_branch,
            "created_at": pull_request.created_at.isoformat(),
            "updated_at": pull_request.updated_at.isoformat(),
            "labels": pull_request.labels
        }

        # Intentar obtener PR existente primero
        existing = self.supabase.table("tech_prs")\
            .select("id")\
            .eq("github_id", pull_request.github_id)\
            .execute()

        if existing.data:
            # Actualizar existente
            self.supabase.table("tech_prs")\
                .update(pr_data)\
                .eq("id", existing.data[0]["id"])\
                .execute()
            return existing.data[0]["id"]
        else:
            # Crear nuevo
            result = self.supabase.table("tech_prs")\
                .insert(pr_data)\
                .execute()
            return result.data[0]["id"]

    def get_by_github_id(self, github_id: int) -> Optional[int]:
        """
        Obtiene el ID interno de un PR por su GitHub ID.
        
        Args:
            github_id: ID del PR en GitHub
            
        Returns:
            Optional[int]: ID interno del PR o None si no existe
        """
        result = self.supabase.table("tech_prs")\
            .select("id")\
            .eq("github_id", github_id)\
            .execute()
            
        return result.data[0]["id"] if result.data else None

    async def get_by_id(self, pr_id: int) -> Optional[PullRequest]:
        result = await self.supabase.table("tech_prs")\
            .select("*")\
            .eq("id", pr_id)\
            .execute()
            
        if not result.data:
            return None
            
        pr_data = result.data[0]
        return PullRequest(
            id=pr_data["github_id"],
            number=pr_data["number"],
            title=pr_data["title"],
            body=pr_data["body"],
            status=PullRequestStatus(pr_data["status"]),
            author=pr_data["author"],
            repository=pr_data["repository"],
            base_branch=pr_data["base_branch"],
            head_branch=pr_data["head_branch"],
            created_at=datetime.fromisoformat(pr_data["created_at"]),
            updated_at=datetime.fromisoformat(pr_data["updated_at"]),
            labels=pr_data["labels"]
        ) 