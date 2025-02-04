from typing import List, Dict, Any
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from application.dto.ai_analysis_result_dto import AIAnalysisResult
from application.dto.prompt_dto import RuleDTO  # Asegúrate de tener esta importación


class LangchainOrchestrator:
    """
    Orquestador para interactuar con modelos de IA usando LangChain.
    Maneja la generación y estructuración de revisiones de código usando structured outputs.
    """

    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini-2024-07-18",
            temperature=0.2,
            openai_api_key=openai_api_key
        )
        # El output parser se encarga de validar y extraer la respuesta estructurada
        self.output_parser = PydanticOutputParser(pydantic_object=AIAnalysisResult)

    def _format_rules(self, rules: List[RuleDTO]) -> str:
        """
        Convierte una lista de reglas en una cadena formateada para incluir en el prompt.
        """
        return "\n".join(
            f"- {rule.name}: {rule.rule_content}" for rule in rules
        )

    async def analyze_code(
            self,
            diff: str,
            prompt: str,
            rules: List[RuleDTO],
            context: Dict[str, Any],
            title_guidelines: str,
            description_template: str,
            label_guidelines: str
    ) -> AIAnalysisResult:
        """
        Analiza un diff de código usando IA y devuelve un objeto AIAnalysisResult.

        Args:
            diff (str): Diff del código a analizar.
            prompt (str): Texto base del prompt para el análisis.
            rules (List[RuleDTO]): Lista de reglas a aplicar.
            context (Dict[str, Any]): Contexto adicional del PR.
            title_guidelines (str): Contenido formateado de las guías de título.
            description_template (str): Plantilla de descripción de PR.
            label_guidelines (str): Lineamientos de etiquetas.

        Returns:
            AIAnalysisResult: Resultado estructurado del análisis.
        """
        if not isinstance(diff, str):
            raise ValueError("El diff debe ser una cadena de texto.")

        # Formatear las reglas
        formatted_rules = self._format_rules(rules)

        # Obtener las instrucciones estructuradas que espera el output parser
        structured_output_instructions = self.output_parser.get_format_instructions()

        # Construir el prompt completo, inyectando los placeholders incluidos las instrucciones
        prompt_template = ChatPromptTemplate.from_template(prompt)
        formatted_prompt = prompt_template.format_messages(
            diff=diff,
            company_rules=formatted_rules,
            title_guidelines=title_guidelines,
            description_template=description_template,
            label_guidelines=label_guidelines,
            format_instructions=structured_output_instructions,
            context=str(context),
            **context
        )

        # Para debug: imprime el prompt final que se enviará

        # Obtener respuesta del modelo
        response = await self.llm.agenerate([formatted_prompt])
        result = response.generations[0][0].text

        try:
            # Parsear la respuesta a la estructura definida por AIAnalysisResult
            parsed_output = self.output_parser.parse(result)
            return parsed_output
        except Exception as parse_error:
            print("Error parsing structured output:", parse_error)
            raise parse_error
