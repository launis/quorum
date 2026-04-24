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
from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.llm.client import LLMClient

logger = logging.getLogger(__name__)

_SYSTEM_INSTRUCTION = """<system_directive>
  <objective>
    ROLE: You are an automatic JSON translator.
    TASK: Translate **ALL STRING VALUES** of the provided JSON object into: '{target_language}'.
  </objective>
  <rules>
    <rule>CRITICAL CONSTRAINT: NEVER TRANSLATE OR MODIFY JSON KEYS. Keys contain programmatic variables. Only translate the 'Values'.</rule>
    <rule>NEVER prepend language codes like 'fi - ' or 'en - ' to the translated text.</rule>
    <rule>Do not add any conversational text or markdown code blocks at the beginning or end of your response.</rule>
    <rule>Return pure, valid JSON.</rule>
  </rules>
</system_directive>"""  # noqa: E501


@hook_registry.register(name="translation_hook")
async def translation_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """HOOK: translation_hook.

    Translates the values of the AI output dictionary to the requested target language.
    If translation fails, it adheres to the Graceful Degradation protocol by logging
    the failure and returning the original English output, preventing an application crash.
    """
    logger.info("[TranslationHook] Running dynamic JSON translation...")

    try:
        from backend_v2.models.dtos.state import HookStateMetadata, I18nStatePayload

        meta = HookStateMetadata.model_validate(state.metadata)  # noqa: F841
        payload = I18nStatePayload.model_validate(state.inputs)
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

    repo = deps.repository
    if not repo:
        # Fallback if repository is missing - we cannot initialize LLMClient
        logger.warning("[TranslationHook] Missing repository context. Cannot translate to %s.", target_language)
        return HookResult(success=False, state_delta={})

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
        llm_client = await LLMClient.from_strategy("fast", repository=repo)
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

    system_content = _SYSTEM_INSTRUCTION.replace("{target_language}", target_lang_name)
    user_content = f"<SOURCE_JSON>\n{json.dumps(payload_to_translate, ensure_ascii=False)}\n</SOURCE_JSON>"

    messages = [{"role": "system", "content": system_content}, {"role": "user", "content": user_content}]

    try:
        # Call LLM for translation. We expect raw JSON back.
        logger.info("[TranslationHook] Translating %s fields to '%s'...", len(payload_to_translate), target_language)
        # A generic dict string output, not a Pydantic strict model since input is dynamic
        # SALLIVA ASETUS (User Preference): Odotetaan Enumissa määritelty (esim. 120s), jotta LiteLLM voi nukkua
        # 5 RPM doormanin vaatiman ajan ilman, että joudumme pakotettuun englanninkieliseen fallbackiin.
        response_text = await llm_client.run_chat(messages=messages)

        # Clean potential markdown formatting if LLM didn't listen
        if isinstance(response_text, dict):
            translated_payload = response_text
        else:
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            translated_payload = json.loads(response_text.strip())

        # Merge back with preserved fields
        final_data = {**preserved_fields, **translated_payload}
        logger.info("[TranslationHook] Translation successful.")
        return HookResult(success=True, state_delta=final_data)

    except json.JSONDecodeError as e:
        # 1. Log with STRUCTURED FORMAT
        logger.error(
            "[TranslationHook] %s: LLM returned invalid JSON on translation: %s",
            ErrorCodes.AGENT_RESPONSE_PARSING_FAILED.name,
            e,
            exc_info=True,
        )
        raise AppException(
            message="LLM returned invalid JSON on translation.",
            status_code=500,
            details={"error_code": ErrorCodes.AGENT_RESPONSE_PARSING_FAILED.value},
        ) from e
    except Exception as e:
        logger.error(
            "[TranslationHook] %s: LLM generation failed for translation: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            e,
            exc_info=True,
        )
        raise AppException(
            message="LLM generation failed for translation.",
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e


# A deterministic dictionary for translating English SDUI string fields into Finnish.
# Used by translate_sdui_payload to avoid the latency of an LLM call for static SDUI elements.
_SDUI_DICT = {
    "coaching": "Valmennus",
    "falsification": "Väärennys",
    "falsification audit": "Falsifikaatio",
    "missing_context": "Puuttuva Konteksti",
    "remediation_steps": "Korjaavat Toimenpiteet",
    "emotional_sentiment": "Tunnesävy",
    "theory_link": "Teoreettinen Linkki",
    "risk_flag": "Riskilippu",
    "confidence": "Luottamus",
    "justification": "Perustelu",
    "score": "Pisteet",
    "normalized": "Normalisoitu",
    "scaled": "Skaalattu",
}


async def translate_sdui_payload[TModel: BaseModel](
    obj: TModel, target_language: str, repo: AbstractWorkflowRepository
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
