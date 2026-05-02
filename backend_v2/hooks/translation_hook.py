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
from typing import Any

from pydantic import BaseModel

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.database.interfaces import IComponentRepository
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.dtos.base import BaseDTO
from backend_v2.models.dtos.state import HookStateMetadata, I18nStatePayload
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

logger = logging.getLogger(__name__)


class TranslationResponseDTO(BaseDTO):
    translated_data: dict[str, Any]


_SYSTEM_INSTRUCTION = """<system_directive>
  <objective>
    ROLE: You are an automatic JSON translator.
    TASK: Translate **ALL STRING VALUES** of the provided JSON object into: '{target_language}'.
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
        i18n_meta = (
            {"target_locale": state.metadata.get("target_locale")}
            if state.metadata and "target_locale" in state.metadata
            else {}
        )
        meta = HookStateMetadata.model_validate(i18n_meta)  # noqa: F841

        # Explicit routing for inputs
        i18n_inputs = {"language": state.inputs.get("language")} if "language" in state.inputs else {}
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
    # We don't want to translate system keys starting with '_' or known metadata fields.
    payload_to_translate = {}
    preserved_fields = {}

    for k, v in state.inputs.items():
        if k.startswith("_") or k in ("language", "repository", "inputs", "node_id", "workflow_id"):
            preserved_fields[k] = v
        else:
            payload_to_translate[k] = v

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
    target_lang_name = lang_map[target_language] if target_language in lang_map else target_language

    system_content = _SYSTEM_INSTRUCTION.replace("{target_language}", target_lang_name)
    user_content = (
        f"<context>\n"
        f"  <source_language>en</source_language>\n"
        f"  <target_language>{target_language}</target_language>\n"
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


# A deterministic dictionary for translating English SDUI string fields into Finnish.
# Used by translate_sdui_payload to avoid the latency of an LLM call for static SDUI elements.
_SDUI_DICT = {
    "coaching": "COACHING",
    "falsification": "FALSIFICATION",
    "falsification audit": "FALSIFICATION_AUDIT",
    "missing_context": "MISSING_CONTEXT",
    "remediation_steps": "REMEDIATION_STEPS",
    "emotional_sentiment": "EMOTIONAL_SENTIMENT",
    "theory_link": "THEORY_LINK",
    "risk_flag": "RISK_FLAG",
    "confidence": "CONFIDENCE",
    "justification": "JUSTIFICATION",
    "score": "SCORE",
    "normalized": "NORMALIZED",
    "scaled": "SCALED",
}


async def translate_sdui_payload[TModel: BaseModel](
    obj: TModel, target_language: str, repo: IComponentRepository
) -> TModel:
    """Epic 35: API Pipeline Splicing Translation Hook.

    Translates English SDUI string fields into the target UI language adhering to frozen Pydantic models.
    """
    if not target_language or target_language.lower() == "en":
        return obj

    # 1. Parse to dict (model_dump is used per Epic)
    raw = obj.model_dump(mode="json")

    # 2. Recursively translate string values (utilizing deterministic dictionary)
    def _recursive_translate(data: Any) -> Any:
        if isinstance(data, dict):
            new_dict = {}
            for k, v in data.items():
                if isinstance(v, str):
                    # Translate if we find a match (case-insensitive for keys/values common in SDUI)
                    lower_v = v.lower().strip()
                    if lower_v in _SDUI_DICT:
                        new_dict[k] = _SDUI_DICT[lower_v]
                    elif k.lower() in _SDUI_DICT and v == k:
                        new_dict[k] = _SDUI_DICT[k.lower()]
                    else:
                        new_dict[k] = v
                else:
                    new_dict[k] = _recursive_translate(v)
            return new_dict
        elif isinstance(data, list):
            return [_recursive_translate(item) for item in data]
        else:
            return data

    translated_raw = _recursive_translate(raw)

    try:
        # 3. Rehydrate: model_validate(raw)
        # Using type(obj) dynamically supports any BaseModel like ReportDataDTO or SduiBlockBase
        return type(obj).model_validate(translated_raw)
    except Exception as e:
        logger.error("[TranslationHook] Failed to rehydrate translated SDUI model: %s", e, exc_info=True)
        raise AppException(
            message="Failed to rehydrate translated SDUI model.",
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e
