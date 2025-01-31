# Este módulo maneja la interacción con la API de GitHub
# Implementa las operaciones necesarias para revisar PRs

import jwt
import time
import httpx
from typing import Dict, List, Optional
from domain.models.review import Review

class GitHubService:
    """
    Servicio para interactuar con la API de GitHub.
    Maneja autenticación y operaciones sobre Pull Requests.
    """
    
    def __init__(self, app_id: str, private_key: str):
        self.app_id = app_id
        self.private_key = private_key
        self.base_url = "https://api.github.com"
        self._installation_token = None
        self._token_expires_at = 0

    async def _get_auth_token(self) -> str:
        """
        Obtiene un token de instalación para la GitHub App.
        Maneja la renovación automática del token.
        
        Returns:
            str: Token de acceso válido
        """
        # Verificar si necesitamos un nuevo token
        current_time = time.time()
        if not self._installation_token or current_time >= self._token_expires_at:
            # Generar JWT para autenticar como GitHub App
            jwt_token = jwt.encode(
                {
                    "iat": int(current_time),
                    "exp": int(current_time + 600),
                    "iss": self.app_id
                },
                self.private_key,
                algorithm="RS256"
            )
            
            # Obtener ID de instalación
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/app/installations",
                    headers={"Authorization": f"Bearer {jwt_token}"}
                )
                response.raise_for_status()
                installation_id = response.json()[0]["id"]
                
                # Obtener token de instalación
                response = await client.post(
                    f"{self.base_url}/app/installations/{installation_id}/access_tokens",
                    headers={"Authorization": f"Bearer {jwt_token}"}
                )
                response.raise_for_status()
                token_data = response.json()
                
                self._installation_token = token_data["token"]
                self._token_expires_at = time.time() + 3600  # Token válido por 1 hora
                
        return self._installation_token

    async def get_pull_request_diff(self, repository: str, pr_number: int) -> str:
        """
        Obtiene el diff de un Pull Request.
        
        Args:
            repository: Nombre del repositorio (formato: "owner/repo")
            pr_number: Número del Pull Request
            
        Returns:
            str: Contenido del diff
        """
        token = await self._get_auth_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{repository}/pulls/{pr_number}",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3.diff"
                }
            )
            response.raise_for_status()
            return response.text

    async def create_review_comments(self, repository: str, pr_number: int, review: Review):
        """
        Crea comentarios en un Pull Request basados en una revisión.
        
        Args:
            repository: Nombre del repositorio
            pr_number: Número del Pull Request
            review: Revisión con los comentarios a publicar
        """
        token = await self._get_auth_token()
        
        async with httpx.AsyncClient() as client:
            # Crear review en GitHub
            review_data = {
                "body": review.summary,
                "event": "COMMENT",
                "comments": [
                    {
                        "path": comment.file_path,
                        "line": comment.line_number,
                        "body": (
                            f"{comment.content}\n\n"
                            f"```suggestion\n{comment.suggestion}\n```"
                            if comment.suggestion else comment.content
                        )
                    }
                    for comment in review.comments
                ]
            }
            
            response = await client.post(
                f"{self.base_url}/repos/{repository}/pulls/{pr_number}/reviews",
                headers={"Authorization": f"token {token}"},
                json=review_data
            )
            response.raise_for_status()

    async def update_pr(
        self,
        repository: str,
        pr_number: int,
        title: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> None:
        token = await self._get_auth_token()
        headers = {"Authorization": f"token {token}"}
        
        data = {}
        if title:
            data["title"] = title
        if labels:
            data["labels"] = labels
            
        if data:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/repos/{repository}/pulls/{pr_number}",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()

    async def create_check_run(
        self,
        repository: str,
        head_sha: str,
        conclusion: str,
        output: Dict
    ) -> None:
        token = await self._get_auth_token()
        headers = {"Authorization": f"token {token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/repos/{repository}/check-runs",
                headers=headers,
                json={
                    "name": "AI Code Review",
                    "head_sha": head_sha,
                    "status": "completed",
                    "conclusion": conclusion,
                    "output": output
                }
            )
            response.raise_for_status() 