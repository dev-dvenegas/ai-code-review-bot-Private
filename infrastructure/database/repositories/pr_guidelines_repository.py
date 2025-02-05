import logging
from typing import List, Optional
from datetime import datetime
from supabase import Client
from domain.models.pr_guidelines import (
    PRTitleGuideline,
    PRDescriptionTemplate,
    PRLabel
)

logger = logging.getLogger(__name__)

class PRGuidelinesRepository:
    """Repositorio para gestionar guías y configuraciones de PR"""

    def __init__(self, supabase: Client):
        self.supabase = supabase

    def get_active_title_guidelines(self) -> List[PRTitleGuideline]:
        """Obtiene todas las guías de título activas"""
        result = self.supabase.table("tech_pr_title_guidelines")\
            .select("*")\
            .eq("is_active", True)\
            .execute()
            
        return [PRTitleGuideline(**data) for data in result.data]

    def get_active_template(self) -> Optional[PRDescriptionTemplate]:
        """Obtiene la plantilla de descripción activa"""
        result = self.supabase.table("tech_pr_description_templates")\
            .select("*")\
            .eq("is_active", True)\
            .limit(1)\
            .execute()
            
        return PRDescriptionTemplate(**result.data[0]) if result.data else None

    def get_active_labels(self) -> List[PRLabel]:
        """Obtiene todas las etiquetas activas"""
        result = self.supabase.table("tech_pr_labels")\
            .select("*")\
            .eq("is_active", True)\
            .execute()
            
        return [PRLabel(**data) for data in result.data]

    def save_title_guideline(self, guideline: PRTitleGuideline) -> PRTitleGuideline:
        """Guarda o actualiza una guía de título"""
        data = guideline.dict(exclude={'id', 'created_at', 'updated_at'})
        data['updated_at'] = datetime.utcnow().isoformat()

        if guideline.id:
            result = self.supabase.table("tech_pr_title_guidelines")\
                .update(data)\
                .eq("id", guideline.id)\
                .execute()
        else:
            data['created_at'] = data['updated_at']
            result = self.supabase.table("tech_pr_title_guidelines")\
                .insert(data)\
                .execute()

        return PRTitleGuideline(**result.data[0]) 