from datetime import datetime
from domain.models.pull_request import PullRequest
from domain.exceptions import PRMetadataGenerationException
from infrastructure.database.repositories.pr_guidelines_repository import PRGuidelinesRepository


class GeneratePRMetadataUseCase:
    """
    Caso de uso para generar metadatos (título, descripción y etiquetas)
    para un Pull Request utilizando las configuraciones almacenadas en la BD.
    """

    def __init__(self, pr_guidelines_repo: PRGuidelinesRepository):
        self.pr_guidelines_repo = pr_guidelines_repo

    async def execute(self, pull_request: PullRequest) -> PullRequest:
        """
        Genera y actualiza los metadatos sugeridos para el PR.

        Args:
            pull_request (PullRequest): Modelo de dominio del PR.

        Returns:
            PullRequest: El PR actualizado con metadatos generados.
        """
        try:
            # Recuperar configuraciones activas
            title_guidelines = self.pr_guidelines_repo.get_active_title_guidelines()
            template = self.pr_guidelines_repo.get_active_template()
            active_labels = self.pr_guidelines_repo.get_active_labels()

            # Validar el título actual con las guías
            valid_title = False
            for guideline in title_guidelines:
                if guideline.validate_title(pull_request.title):
                    valid_title = True
                    break
            if not valid_title:
                # Si no es válido, se puede optar por usar un título sugerido ya calculado por la IA
                # O bien, generar un nuevo título usando el prefijo del primer guideline activo
                if pull_request.suggested_title:
                    pull_request.title = pull_request.suggested_title
                else:
                    pull_request.title = f"{title_guidelines[0].prefix}: {pull_request.title}"

            # Aplicar la plantilla de descripción (si se define una)
            if template:
                context = {
                    "pr_number": pull_request.number,
                    "title": pull_request.title,
                    "author": pull_request.author,
                    "repository": pull_request.repository
                }
                pull_request.body = template.apply_template(context)

            # Actualizar etiquetas sugeridas
            if pull_request.suggested_labels:
                valid_label_names = {label.name for label in active_labels}
                pull_request.labels = [label for label in pull_request.suggested_labels if label in valid_label_names]
            else:
                # Si no se sugirieron etiquetas, asignar una etiqueta por defecto, por ejemplo "chore"
                pull_request.labels = ["chore"]

            pull_request.updated_at = datetime.utcnow()
            return pull_request
        except Exception as e:
            raise PRMetadataGenerationException(f"Error generando metadatos para el PR: {str(e)}")
