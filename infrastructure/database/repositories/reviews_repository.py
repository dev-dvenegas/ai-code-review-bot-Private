# Este módulo implementa el repositorio para gestionar las revisiones en la base de datos
# Sigue el patrón Repository para abstraer el acceso a datos

from typing import Optional, List
from datetime import datetime
from supabase import Client
from domain.models.review import Review, ReviewComment, ReviewStatus

class ReviewsRepository:
    """
    Repositorio para gestionar las revisiones de código.
    Maneja la persistencia de revisiones y sus comentarios.
    """

    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def save(self, review: Review) -> Review:
        """
        Guarda una revisión en la base de datos.
        Si la revisión ya existe, la actualiza.
        
        Args:
            review: Revisión a guardar
            
        Returns:
            Review: Revisión guardada con ID actualizado
        """
        # Preparar datos de la revisión
        review_data = {
            "pull_request_id": review.pull_request_id,
            "status": review.status.value,
            "summary": review.summary,
            "score": review.score,
            "suggested_title": review.suggested_title,
            "suggested_labels": review.suggested_labels,
            "updated_at": datetime.utcnow().isoformat()
        }

        if review.id:
            # Actualizar revisión existente
            result = self.supabase.table("tech_reviews") \
                .update(review_data) \
                .eq("id", review.id) \
                .execute()
        else:
            # Crear nueva revisión
            review_data["created_at"] = datetime.utcnow().isoformat()
            result = self.supabase.table("tech_reviews") \
                .insert(review_data) \
                .execute()

        review_id = result.data[0]["id"]
        review.id = review_id

        # Guardar comentarios
        if review.comments:
            comments_data = [
                {
                    "review_id": review_id,
                    "file_path": comment.file_path,
                    "line_number": comment.line_number,
                    "content": comment.content,
                    "suggestion": comment.suggestion
                }
                for comment in review.comments
            ]

            # Eliminar comentarios anteriores si existen
            if review.id:
                self.supabase.table("tech_review_comments") \
                    .delete() \
                    .eq("review_id", review_id) \
                    .execute()

            # Insertar nuevos comentarios
            self.supabase.table("tech_review_comments") \
                .insert(comments_data) \
                .execute()

        return review

    async def get_by_pr_id(self, pr_id: int) -> Optional[Review]:
        """
        Obtiene la última revisión para un Pull Request.
        
        Args:
            pr_id: ID del Pull Request
            
        Returns:
            Review: Última revisión encontrada o None
        """
        # Obtener revisión
        result = self.supabase.table("tech_reviews") \
            .select("*") \
            .eq("pull_request_id", pr_id) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()

        if not result.data:
            return None

        review_data = result.data[0]

        # Obtener comentarios
        comments_result = self.supabase.table("tech_review_comments") \
            .select("*") \
            .eq("review_id", review_data["id"]) \
            .execute()

        # Construir objeto Review
        comments = [
            ReviewComment(
                file_path=c["file_path"],
                line_number=c["line_number"],
                content=c["content"],
                suggestion=c.get("suggestion")
            )
            for c in comments_result.data
        ]

        return Review(
            id=review_data["id"],
            pull_request_id=review_data["pull_request_id"],
            status=ReviewStatus(review_data["status"]),
            summary=review_data["summary"],
            score=review_data["score"],
            comments=comments,
            created_at=datetime.fromisoformat(review_data["created_at"]),
            updated_at=datetime.fromisoformat(review_data["updated_at"]),
            suggested_title=review_data.get("suggested_title"),
            suggested_labels=review_data.get("suggested_labels", [])
        ) 