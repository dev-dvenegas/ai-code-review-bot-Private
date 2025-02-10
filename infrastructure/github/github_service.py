import jwt
import time
import httpx
from typing import Dict, List, Optional
from domain.models.review import Review
import unidiff  # Asegúrate de tener instalada la librería unidiff
import logging

logger = logging.getLogger(__name__)


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
        current_time = time.time()
        if not self._installation_token or current_time >= self._token_expires_at:
            jwt_token = jwt.encode(
                {
                    "iat": int(current_time),
                    "exp": int(current_time + 600),
                    "iss": self.app_id
                },
                self.private_key,
                algorithm="RS256"
            )
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/app/installations",
                    headers={"Authorization": f"Bearer {jwt_token}"}
                )
                response.raise_for_status()
                installation_id = response.json()[0]["id"]
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

    async def create_review_comments(self, repository: str, pr_number: int, review: Review, diff: str) -> None:
        """
        Crea una revisión en GitHub con comentarios.
        
        Args:
            repository: Nombre del repositorio
            pr_number: Número del Pull Request
            review: Objeto Review con los comentarios
            diff: Contenido del diff del PR
        """
        token = await self._get_auth_token()

        # Determinar el evento según el score
        if review.score >= 90:
            event = "APPROVE"
        elif review.score >= 70:
            event = "COMMENT"
        else:
            event = "REQUEST_CHANGES"

        # # Construir los comentarios con el formato correcto de GitHub
        # comments = []
        
        # Construir el comentario general con el formato estructurado
        general_comment = (
            f"# Pull Request Analysis\n\n"
            f"## Summary\n{review.summary}\n\n"
            f"## Score: {review.score}/100\n\n"
            f"## Security Concerns\n"
            + "\n".join(f"- {issue}" for issue in review.security_concerns or [])
            + "\n\n## Performance Issues\n"
            + "\n".join(f"- {issue}" for issue in review.performance_issues or [])
        )

        # Agregar el comentario general como parte del body principal del review
        review_data = {
            "commit_id": await self._get_latest_commit_sha(repository, pr_number),
            "body": general_comment,
            "event": event,
            "comments": []
        }
        # Luego agregar los comentarios específicos
        for comment in review.comments:
            if comment.file_path:  # Solo procesar comentarios con archivo asociado
                try:
                    # Obtener el diff específico del archivo
                    patch_set = unidiff.PatchSet(diff.splitlines(keepends=True))
                    target_file = None
                    for patched_file in patch_set:
                        if patched_file.path == comment.file_path:
                            target_file = patched_file
                            break

                    if target_file:
                        # Encontrar el hunk correcto y la posición
                        for hunk in target_file:
                            if hunk.target_start <= comment.line_number <= (hunk.target_start + hunk.target_length):
                                comment_body = f"{comment.content}"
                                
                                if comment.suggestion:
                                    comment_body += "\n\n```suggestion\n" + comment.suggestion + "\n```"
                                
                                comment_data = {
                                    "path": comment.file_path,
                                    "line": comment.line_number,
                                    "body": comment_body
                                }
                                review_data["comments"].append(comment_data)
                                break

                except Exception as e:
                    logger.error(f"Error procesando comentario para {comment.file_path}: {str(e)}")
                    continue


        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/repos/{repository}/pulls/{pr_number}/reviews",
                    headers={
                        "Authorization": f"token {token}",
                        "Accept": "application/vnd.github.v3+json"
                    },
                    json=review_data
                )
        
                if not response.is_success:
                    logger.error(f"GitHub API Error: {response.status_code}")
                    logger.error(f"Response body: {response.text}")
        
                response.raise_for_status()
        
            except httpx.HTTPError as e:
                logger.error(f"Error creating review: {str(e)}")
                raise

    async def _get_latest_commit_sha(self, repository: str, pr_number: int) -> str:
        """
        Obtiene el SHA del último commit en el PR.
        """
        token = await self._get_auth_token()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{repository}/pulls/{pr_number}/commits",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            response.raise_for_status()
            commits = response.json()
            return commits[-1]["sha"] if commits else None

    async def create_metadata_comment(self, repository: str, pr_number: int, metadata: Dict[str, str]):
        """
        Crea un comentario en el PR con la metadata sugerida (título, descripción y etiquetas)
        para que el usuario pueda revisarla y, si lo desea, modificar el PR.

        Args:
            repository: Nombre del repositorio.
            pr_number: Número del Pull Request.
            metadata: Diccionario con keys 'suggested_title', 'suggested_description', y 'suggested_labels'
                      (este último es una cadena que se puede formatear, por ejemplo, separada por comas).
        """
        token = await self._get_auth_token()

        # Construir el cuerpo del comentario con la metadata sugerida
        metadata_body = (
            f"**Suggested Title:** {metadata.get('suggested_title', '')}\n\n"
            f"**Suggested Description:** {metadata.get('suggested_description', '')}\n\n"
            f"**Suggested Labels:** {metadata.get('suggested_labels', '')}"
        )

        comment_data = {
            "body": metadata_body
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/repos/{repository}/issues/{pr_number}/comments",
                headers={"Authorization": f"token {token}"},
                json=comment_data
            )
            print(f"Debug: Metadata comment response body:", response.text)
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
