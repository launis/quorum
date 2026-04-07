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

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import ConfigurationError, ErrorCodes
from backend_v2.llm.client import LLMClient

logger = logging.getLogger(__name__)

_SYSTEM_INSTRUCTION = """SÄÄNTÖ: Toimit automaattisena JSON-kääntäjänä.
TEHTÄVÄ: Käännä alla olevan JSON-objektin **KAIKKI MERKKIJONOARVOT** kielelle: '{target_language}'.

KRIITTINEN RAJOITE: ÄLÄ KOSKAAN KÄÄNNÄ TAI MUUTA JSON-AVAIMIA (Keys).
Ne sisältävät ohjelmoitavia muuttujia. Vain "Values" käännetään.
ÄLÄ KOSKAAN lisää kielikoodeja, kuten "fi - " tai "en - ", käännettyjen tekstien alkuun.
Älä lisää mitään ylimääräistä tekstiä tai markdown-koodiblokkeja vasuksesesi alkuun tai loppuun.
Palauta puhdasta, validia JSONia."""


@hook_registry.register(name="translation_hook")
async def translation_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """HOOK: translation_hook.

    Translates the values of the AI output dictionary to the requested target language.
    If translation fails, it adheres to the Graceful Degradation protocol by logging
    the failure and returning the original English output, preventing an application crash.
    """
    logger.info("[TranslationHook] Running dynamic JSON translation...")

    # Data is expected to be a dict (the flattened output of the node)
    # The original inputs (including target_language and repository) should be passed in kwargs or accessible

    # Check if this is the generic flat data payload or if we have full kwargs context
    # Usually hooks receive the merged dict, so we need to find the target_language

    target_language = state.inputs.get("language")
    if not target_language:
        # If no language is specified, we assume no translation is needed
        logger.debug("[TranslationHook] No 'language' found in payload. Skipping translation.")
        return HookResult(success=True, state_delta={})

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
        # Graceful Degradation: return original data
        return HookResult(success=False, state_delta={})

    # 2. Build the exact translation prompt strictly adhering to Role Segregation
    lang_map = {"fi": "suomeksi (Finnish)", "en": "englanniksi (English)", "sv": "ruotsiksi (Swedish)", "et": "viroksi (Estonian)"}
    target_lang_name = lang_map.get(target_language, target_language)

    system_content = _SYSTEM_INSTRUCTION.replace("{target_language}", target_lang_name)
    user_content = f"Lähde JSON:\n{json.dumps(payload_to_translate, ensure_ascii=False)}"

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
        # 1. Log with STRUCTURED FORMAT even for non-fatal errors
        logger.error(
            "[TranslationHook] %s: LLM returned invalid JSON on translation: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            e,
            exc_info=True,
        )
        # 2. Graceful Degradation: Return original untranslated data to prevent UI crash
        return HookResult(success=False, state_delta={})
    except Exception as e:
        logger.error(
            "[TranslationHook] %s: LLM generation failed for translation: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            e,
            exc_info=True,
        )
        return HookResult(success=False, state_delta={})
