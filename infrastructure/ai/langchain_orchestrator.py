import logging
from typing import List, Dict, Any
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from application.dto.ai_analysis_result_dto import CodeAnalysisResult, PRMetadataResult
from application.dto.prompt_dto import RuleDTO

logger = logging.getLogger(__name__)

class LangchainOrchestrator:
    """
    Orquestador para interactuar con modelos de IA usando LangChain.
    Maneja la generación y estructuración de revisiones de código usando structured outputs.
    """

    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model_name="o1-mini",
            # model_name="gpt-4o-mini-2024-07-18",
            temperature=1,
            openai_api_key=openai_api_key
        )
        self.code_analysis_parser = PydanticOutputParser(pydantic_object=CodeAnalysisResult)
        self.metadata_parser = PydanticOutputParser(pydantic_object=PRMetadataResult)

    def _format_rules(self, rules: List[RuleDTO]) -> str:
        """
        Convierte una lista de reglas en una cadena formateada para incluir en el prompt.
        """
        return "\n".join(
            f"- {rule.name} (Priority {rule.priority}): {rule.rule_content}" 
            for rule in sorted(rules, key=lambda x: x.priority, reverse=True)
        )

    async def analyze_code(
            self,
            diff: str,
            prompt: str,
            rules: List[RuleDTO],
            context: Dict[str, Any]
    ) -> CodeAnalysisResult:
        """Analiza el código usando el prompt de análisis"""
        formatted_rules = self._format_rules(rules)
        prompt_template = ChatPromptTemplate.from_template(prompt)
        
        messages = prompt_template.format_messages(
            diff=diff,
            rules=formatted_rules,
            context=str(context),
            format_instructions=self.code_analysis_parser.get_format_instructions()
        )
        logger.info(f"------messages_analyze_code------------: {messages}")
        response = await self.llm.agenerate([messages])
        llm_response = self.code_analysis_parser.parse(response.generations[0][0].text)
        logger.info(f"------analyze_code_ll_response------------: {llm_response}")

        return llm_response

    async def generate_metadata(
            self,
            context: Dict[str, Any],
            prompt: str,
            title_guidelines: str,
            description_template: str,
            label_guidelines: str
    ) -> PRMetadataResult:
        """Genera metadata usando el prompt de metadata"""
        prompt_template = ChatPromptTemplate.from_template(prompt)
        
        messages = prompt_template.format_messages(
            pr_title=context["pr_title"],
            pr_body=context["pr_body"],
            repository=context["repository"],
            pr_number=context["pr_number"],
            title_guidelines=title_guidelines,
            description_template=description_template,
            label_guidelines=label_guidelines,
            format_instructions=self.metadata_parser.get_format_instructions()
        )
        
        response = await self.llm.agenerate([messages])
        llm_response = self.metadata_parser.parse(response.generations[0][0].text)
        logger.info(f"------metadata_llm_response------------: {llm_response}")
        return llm_response
