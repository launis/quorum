"""Studio Lexicon Service."""

from __future__ import annotations

import logging

from backend_v2.database.interfaces import ISystemRepository
from backend_v2.exceptions import ErrorCodes, ResourceNotFoundError
from backend_v2.llm.client import LLMClient
from backend_v2.llm.directives import STUDIO_DISCOVER_SLOP_PHRASES, STUDIO_TRANSLATE_SLOP_PHRASES
from backend_v2.llm.prompt_builder import build_system_directive
from backend_v2.models.auth import SystemOrganizations, TokenData
from backend_v2.models.enums import SystemConfigID
from backend_v2.models.v2_core import (
    LexiconSuggestionListDTO,
    SystemConfigPerformativeLexicons,
)
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.studio.auth_validator import enforce_modification_rights

logger = logging.getLogger(__name__)


class StudioLexiconService:
    """Domain Service for Lexicon Config management."""

    def __init__(self, system_repo: ISystemRepository):
        """Initialize the service.

        Args:
            system_repo: The repository for system configuration data.
        """
        self.system_repo = system_repo

    async def get_performative_lexicons_config(self) -> SystemConfigPerformativeLexicons:
        """Get the performative lexicons configuration.

        Returns:
            The performative lexicons configuration data.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
        """
        config_data = await self.system_repo.get_system_config(SystemConfigID.PERFORMATIVE_LEXICONS.value)
        if not config_data:
            logger.error(
                "[StudioLexiconService] %s: Performative lexicons config %s not found.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                SystemConfigID.PERFORMATIVE_LEXICONS.value,
            )
            raise ResourceNotFoundError(
                resource_type="system_config", resource_id=SystemConfigID.PERFORMATIVE_LEXICONS.value
            )
        return SystemConfigPerformativeLexicons.model_validate(config_data, strict=False)

    async def save_performative_lexicons_config(
        self, initiator: TokenData, data: SystemConfigPerformativeLexicons
    ) -> SystemConfigPerformativeLexicons:
        """Save the performative lexicons configuration.

        Args:
            initiator: The user token data initiating the request.
            data: The performative lexicons configuration payload to save.

        Returns:
            The updated performative lexicons configuration.
        """
        enforce_modification_rights(initiator, SystemOrganizations.ROOT_SYSTEM, allow_system=True)
        dump = data.model_dump(mode="json")
        dump["id"] = SystemConfigID.PERFORMATIVE_LEXICONS.value
        await self.system_repo.create_system_config(dump)
        return await self.get_performative_lexicons_config()

    async def discover_new_performative_phrases(self, lang_code: str) -> LexiconSuggestionListDTO:
        """Discover new performative slop phrases via LLM.

        Args:
            lang_code: The target language code to generate phrases for.

        Returns:
            A list of new performative phrases in the requested language.
        """
        client = await LLMClient.from_strategy("fast", repository=self.system_repo, pipeline_name="studio_generation")
        compiler = PromptCompiler()
        executor = LLMTaskExecutor(prompt_compiler=compiler)

        _SYSTEM_INSTRUCTION = build_system_directive(
            objective="Identify new overused 'slop' or AI-generated corporate jargon phrases.",
            rules=STUDIO_DISCOVER_SLOP_PHRASES,
        )

        messages = [
            {"role": "system", "content": _SYSTEM_INSTRUCTION},
            {
                "role": "user",
                "content": (
                    f"<execution_parameters>\n<lang_code>{lang_code}</lang_code>\n</execution_parameters>\n"
                    "Generate 10 completely new performative phrases that sound like an AI wrote them."
                ),
            },
        ]

        result, _ = await executor.execute_structured_task(
            client=client, messages=messages, response_model=LexiconSuggestionListDTO
        )
        return result

    async def translate_performative_phrases(self, target_lang: str) -> LexiconSuggestionListDTO:
        """Translate missing phrases from the 'en' master lexicon.

        Args:
            target_lang: The target language code to translate into.

        Returns:
            A list of newly translated phrases.
        """
        try:
            config = await self.get_performative_lexicons_config()
            en_lexicon = config.lexicon_configs.get("en")
            if not en_lexicon or not en_lexicon.words:
                return LexiconSuggestionListDTO(suggested_phrases=[])
        except ResourceNotFoundError:
            return LexiconSuggestionListDTO(suggested_phrases=[])

        target_lexicon = config.lexicon_configs.get(target_lang)
        existing_words = target_lexicon.words if target_lexicon else []

        client = await LLMClient.from_strategy("fast", repository=self.system_repo, pipeline_name="studio_generation")
        compiler = PromptCompiler()
        executor = LLMTaskExecutor(prompt_compiler=compiler)

        _SYSTEM_INSTRUCTION = build_system_directive(
            objective="Translate the provided list of AI 'slop' corporate jargon into the target language.",
            rules=STUDIO_TRANSLATE_SLOP_PHRASES,
        )

        messages = [
            {"role": "system", "content": _SYSTEM_INSTRUCTION},
            {
                "role": "user",
                "content": (
                    f"<execution_parameters>\n<target_lang>{target_lang}</target_lang>\n</execution_parameters>\n"
                    f"<source_data>\n<master_english_words>\n{en_lexicon.words}\n</master_english_words>\n"
                    f"<existing_target_words>\n{existing_words}\n</existing_target_words>\n</source_data>\n"
                    "Translate the missing words."
                ),
            },
        ]

        result, _ = await executor.execute_structured_task(
            client=client, messages=messages, response_model=LexiconSuggestionListDTO
        )
        return result
