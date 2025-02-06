import jwt
import time
import httpx
from typing import Dict, List, Optional
from domain.models.review import Review
import unidiff  # Asegúrate de tener instalada la librería unidiff


def extract_diff_position(diff: str, file_path: str, target_line: int) -> int:
    """
    Utiliza la librería unidiff para parsear el diff y calcular la posición
    en el diff correspondiente a la línea objetivo (target_line) del archivo.

    Args:
        diff (str): El diff completo (en formato unified).
        file_path (str): La ruta del archivo (relativa a la raíz del repositorio).
        target_line (int): El número de línea (en el archivo) donde se debe colocar el comentario.

    Returns:
        int: La posición en el diff para ese comentario.
        Si no se encuentra un hunk correspondiente, se retorna target_line.
    """
    patch_set = unidiff.PatchSet(diff.splitlines(keepends=True))
    for patch in patch_set:
        if patch.target_file.endswith(file_path) or patch.source_file.endswith(file_path):
            for hunk in patch:
                if hunk.target_start <= target_line < (hunk.target_start + hunk.target_length):
                    # Calcula la posición como: (línea objetivo - inicio del hunk) + 1
                    return target_line - hunk.target_start + 1
    return target_line  # Valor por defecto si no se encuentra


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
        Crea comentarios en un Pull Request basados en una revisión y determina el evento
        de GitHub (APPROVE, COMMENT o REQUEST_CHANGES) según el score de la review.

        Args:
            repository: Nombre del repositorio.
            pr_number: Número del Pull Request.
            review: Revisión con los comentarios a publicar.
            diff: diff de repositorio.
        """
        token = await self._get_auth_token()

        # Determinar el tipo de evento según el score de la review
        if review.score >= 90:
            event = "APPROVE"
        elif review.score >= 70:
            event = "COMMENT"
        else:
            event = "REQUEST_CHANGES"

        # Construir el payload para los comentarios usando "position" (calculado)
        comments_payload = []
        for comment in review.comments:
            position = extract_diff_position(diff, comment.file_path, comment.line_number)
            comments_payload.append({
                "path": comment.file_path,
                "position": position,  # Posición calculada
                "body": (
                    f"{comment.content}\n\n"
                    f"```suggestion\n{comment.suggestion}\n```"
                    if comment.suggestion else comment.content
                )
            })

        review_data = {
            "body": review.summary,
            "event": event,
        }
        if comments_payload:
            review_data["comments"] = comments_payload

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/repos/{repository}/pulls/{pr_number}/reviews",
                headers={"Authorization": f"token {token}"},
                json=review_data
            )

            response.raise_for_status()

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
