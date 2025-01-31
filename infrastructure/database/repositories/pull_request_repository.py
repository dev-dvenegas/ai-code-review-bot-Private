from typing import Optional
from datetime import datetime
from supabase import Client
from domain.models.pull_request import PullRequest, PullRequestStatus

class PullRequestRepository:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.table = "pull_requests"

    async def save(self, pull_request: PullRequest) -> PullRequest:
        data = {
            "github_id": pull_request.id,
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
        
        # Intentar actualizar primero
        result = await self.supabase.table(self.table)\
            .update(data)\
            .eq("github_id", pull_request.id)\
            .execute()
            
        # Si no existe, insertar
        if not result.data:
            result = await self.supabase.table(self.table)\
                .insert(data)\
                .execute()
        
        return pull_request

    async def get_by_id(self, pr_id: int) -> Optional[PullRequest]:
        result = await self.supabase.table(self.table)\
            .select("*")\
            .eq("github_id", pr_id)\
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