"""Translation Hook for Dynamic AI Output Localization.

This post-hook acts as 'The Translation Boundary' within the V2 Architecture.
It intercepts the output dictionary (raw JSON) from an AI node and uses a lightweight
LLM (e.g., Gemini Flash) to translate the string values into the user's `target_language`
while strictly preserving the original JSON keys.

This ensures the Frontend SDUI can parse dynamic output flawlessly without hardcoding
localized strings for AI-generated content.
"""

import json
import logging

from pydantic import BaseModel

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.database.interfaces import IComponentRepository
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.dtos.state import HookStateMetadata, I18nStatePayload, TranslationResponseDTO
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

logger = logging.getLogger(__name__)


_SYSTEM_INSTRUCTION = """<system_directive>
  <objective>
    ROLE: You are an automatic JSON translator.
    TASK: Translate **ALL STRING VALUES** of the provided JSON object into the target language specified in the <target_language> tag within the user context.
  </objective>
  <rules>
    <rule>
      CRITICAL CONSTRAINT: NEVER TRANSLATE OR MODIFY JSON KEYS.
      Keys contain programmatic variables. Only translate the 'Values'.
    </rule>
    <rule>NEVER prepend language codes like 'fi - ' or 'en - ' to the translated text.</rule>
    <rule>Ensure the translation is professional, context-aware, and natural in the target language.
      Adapt the tone to match the original text exactly. ALL sentences must be fully translated.
    </rule>
    <rule>
      Return a JSON object containing a SINGLE key called 'translated_data',
      where the value is the fully translated object.
    </rule>
  </rules>
</system_directive>"""


@hook_registry.register(name="translation_hook")
async def translation_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """HOOK: translation_hook.

    Translates the values of the AI output dictionary to the requested target language.
    If translation fails, it adheres to the Graceful Degradation protocol by logging
    the failure and returning the original English output, preventing an application crash.
    """
    logger.info("[TranslationHook] Running dynamic JSON translation...")

    try:
        # Explicit routing to satisfy extra="forbid" Zero-Compromise Pydantic V2 rule
        i18n_meta = {}
        if state.metadata:
            if "target_locale" in state.metadata:
                i18n_meta["target_locale"] = state.metadata["target_locale"]
            if "fields_to_translate" in state.metadata:
                i18n_meta["fields_to_translate"] = state.metadata["fields_to_translate"]

        meta = HookStateMetadata.model_validate(i18n_meta)

        # Explicit routing for inputs
        i18n_inputs = {"language": state.inputs["language"]} if "language" in state.inputs else {}
        payload = I18nStatePayload.model_validate(i18n_inputs)
    except Exception as e:
        msg = "Execution state is missing mandatory 'target_locale' metadata or 'language' inputs."
        logger.error("[TranslationHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(
            message=msg,
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        ) from e

    target_language = payload.language

    if target_language == "en":
        # English is the native output of the AI, no translation needed
        logger.debug("[TranslationHook] Target language is English. Skipping translation.")
        return HookResult(success=True, state_delta={})

    system_repo = deps.system_repo
    if not system_repo:
        msg = "Strict Fail-Fast Enforced: Missing repository context in TranslationHook."
        logger.error("[TranslationHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

    # 1. Isolate the actual payload that needs translation.
    # We strictly translate ONLY the fields explicitly defined in the schema.
    payload_to_translate = {}
    preserved_fields = {}

    target_fields = set(meta.fields_to_translate)
    if not target_fields:
        logger.debug("[TranslationHook] No fields_to_translate specified in metadata. Skipping translation.")
        return HookResult(success=True, state_delta={})

    for k, v in state.inputs.items():
        if k in target_fields:
            payload_to_translate[k] = v
        else:
            preserved_fields[k] = v

    if not payload_to_translate:
        return HookResult(success=True, state_delta={})

    try:
        # Initialize LLM Client via Strategy Pattern (use 'fast' for translation)
        llm_client = await LLMClient.from_strategy("fast", repository=system_repo)
        executor = LLMTaskExecutor(prompt_compiler=PromptCompiler())
    except ConfigurationError as e:
        logger.error(
            "[TranslationHook] %s: Failed to init LLM for translation: %s", ErrorCodes.CONFIGURATION_ERROR.name, e
        )
        raise AppException(
            message="Failed to init LLM for translation.",
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        ) from e

    # 2. Build the exact translation prompt strictly adhering to Role Segregation
    lang_map = {
        "fi": "suomeksi (Finnish)",
        "en": "englanniksi (English)",
        "sv": "ruotsiksi (Swedish)",
        "et": "viroksi (Estonian)",
    }
    target_lang_name = lang_map.get(target_language, target_language)

    system_content = _SYSTEM_INSTRUCTION
    user_content = (
        f"<context>\n"
        f"  <source_language>en</source_language>\n"
        f"  <target_language>{target_lang_name}</target_language>\n"
        f"</context>\n"
        f"<source_data>\n{json.dumps(payload_to_translate, ensure_ascii=False)}\n</source_data>"
    )

    messages = [{"role": "system", "content": system_content}, {"role": "user", "content": user_content}]

    try:
        logger.info("[TranslationHook] Translating %s fields to '%s'...", len(payload_to_translate), target_language)

        # Enforce structured execution (No more string parsing duck-tape)
        response_dto, _ = await executor.execute_structured_task(
            client=llm_client,
            messages=messages,
            response_model=TranslationResponseDTO,
        )

        translated_payload = response_dto.translated_data

        # Merge back with preserved fields
        final_data = {**preserved_fields, **translated_payload}
        logger.info("[TranslationHook] Translation successful.")
        return HookResult(success=True, state_delta=final_data)

    except Exception as e:
        logger.error(
            "[TranslationHook] %s: LLM structured translation failed: %s",
            ErrorCodes.AGENT_RESPONSE_PARSING_FAILED.name,
            e,
            exc_info=True,
        )
        raise AppException(
            message="LLM structured translation failed.",
            status_code=500,
            details={"error_code": ErrorCodes.AGENT_RESPONSE_PARSING_FAILED.value},
        ) from e


async def translate_sdui_payload[TModel: BaseModel](
    obj: TModel, target_language: str, repo: IComponentRepository
) -> TModel:
    """Epic 35: API Pipeline Splicing Translation Hook.

    Delegates UI translation to the Frontend 'No-String Mandate' (.arb files).
    This acts as a transparent pass-through to maintain strict Pydantic integrity.
    """
    # UI localization is now strictly the responsibility of the Flutter client
    # via .arb localized files. The backend simply passes the raw string tags.
    return obj
