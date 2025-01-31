from typing import List, Dict, Any
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from domain.models.review import ReviewComment
from application.dto.ai_analysis_result_dto import AIAnalysisResult

class LangchainOrchestrator:
    """
    Orquestador para interactuar con modelos de IA usando LangChain.
    Maneja la generación y estructuración de revisiones de código.
    """
    
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.2,
            openai_api_key=openai_api_key
        )
        self.output_parser = PydanticOutputParser(pydantic_object=AIAnalysisResult)

    async def analyze_code(
        self,
        diff: str,
        prompt: str,
        rules: List[dict],
        context: Dict[str, Any]
    ) -> AIAnalysisResult:
        """
        Analiza un diff de código usando IA.
        
        Args:
            diff: Diff del código a analizar
            prompt: Prompt base para el análisis
            rules: Lista de reglas a aplicar
            context: Contexto adicional del PR
            
        Returns:
            AIAnalysisResult: Resultado estructurado del análisis
        """
        # Formatear reglas para el prompt
        formatted_rules = "\n".join(
            f"- {rule['name']}: {rule['rule_content']}"
            for rule in rules
        )
        
        # Crear prompt completo
        prompt_template = ChatPromptTemplate.from_template(prompt)
        formatted_prompt = prompt_template.format_messages(
            diff=diff,
            company_rules=formatted_rules,
            format_instructions=self.output_parser.get_format_instructions(),
            **context
        )
        
        # Obtener respuesta del modelo
        response = await self.llm.agenerate([formatted_prompt])
        result = response.generations[0][0].text
        
        # Parsear respuesta a estructura definida
        return self.output_parser.parse(result) 