"""Synthesis hooks for Output Management V3.

Implements TextConsolidationHook for generating LLM-based markdown synthesis,
enforcing length constraints, preamble text, local PII masking, and structured output.
"""

import json
import logging
import re
from typing import Any

import logfire
from fastapi import status
from pydantic import BaseModel, ConfigDict, Field

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.context_mapper import ContextMapper
from backend_v2.llm.client import LLMClient

logger = logging.getLogger(__name__)


class SynthesisSectionDTO(BaseModel):
    layout_id: str = Field(..., description="The EXACT layout ID provided in the section instructions")
    synthesized_markdown: str = Field(..., description="The synthesized markdown content for this section")


class XaiHighlightItem(BaseModel):
    extension_type: str = Field(
        ..., description="Category of the insight (e.g. 'falsification', 'coaching', 'remediation', 'risk_flag')"
    )
    content: str = Field(..., description="The synthesized, deduplicated insight or tip. Max 2 sentences.")


class SynthesisOutputDTO(BaseModel):
    """Structured output expected from the Synthesis LLM."""

    synthesized_markdown: str = Field(..., description="The fully synthesized and deduplicated markdown content.")
    cited_sources: list[str] = Field(default_factory=list, description="List of references or citations found.")
    section_syntheses: list[SynthesisSectionDTO] = Field(
        default_factory=list, description="List of synthesized sections, mapped by their Layout ID."
    )
    xai_highlights: list[XaiHighlightItem] = Field(
        default_factory=list, description="Top 3 deduplicated items per extension category across all steps."
    )

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


def _mask_pii_local(text: str) -> str:
    """MVP Algorithmic PII Redaction.

    Masks sequences resembling emails or local phone numbers before sending to LLM.
    To be replaced by Presidio in the future.
    """
    if not text:
        return text
    # Mask emails
    text = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "[REDACTED EMAIL]", text)
    # Mask simple phone numbers
    pattern = r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}"
    text = re.sub(pattern, "[REDACTED PHONE]", text)
    return text


def _resolve_i18n_str(i18n_data: dict[str, str] | Any, language_code: str = "en") -> str:
    """Resolves Multilingual text."""
    if not i18n_data:
        return ""
    if hasattr(i18n_data, "root"):
        data = getattr(i18n_data, "root", {})
    elif isinstance(i18n_data, dict):
        data = i18n_data
    else:
        return str(i18n_data)

    if not isinstance(data, dict):
        return str(data)

    target_lang = language_code.split("-")[0].lower()
    if target_lang in data:
        return str(data[target_lang])
    if "en" in data:
        return str(data["en"])
    return str(next(iter(data.values()))) if data else ""


@hook_registry.register(name="text_consolidation_hook")
async def text_consolidation_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """HOOK: text_consolidation_hook.

    Executes LLM synthesis based on Output Profile configurations.

    Args:
        state: Immutable cognitive state including inputs.
        deps: HookDependencies providing data access.

    Returns:
        HookResult: Delta injected with synthesized markdown and tokens.
    """
    logger.debug("[SynthesisHook] Running text_consolidation_hook...")
    if not state:
        return HookResult(success=True, state_delta={})

    inputs = state.inputs
    if not isinstance(inputs, dict):
        msg = "Missing or invalid 'inputs'. Expected dict."
        logger.error("[SynthesisHook] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    # Resolve active workflow to determine the output profile bounds
    workflow_data = await deps.repository.get_workflow_by_id(state.workflow_id)
    if not workflow_data:
        msg = f"Workflow '{state.workflow_id}' not found."
        raise AppException(
            message=msg,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
        )

    execution_data = await deps.repository.get_execution(state.execution_id)
    output_profile_id = None
    if execution_data:
        output_profile_id = getattr(execution_data, "output_profile_id", None)
        if not output_profile_id and isinstance(execution_data, dict):
            output_profile_id = execution_data.get("output_profile_id")

    profile_to_use = output_profile_id

    if not profile_to_use:
        msg = f"Execution {state.execution_id} missing mandatory output_profile_id."
        logger.error("[SynthesisHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    # --- Epic 13 M1: Fetch Output Profile from SSOT ---
    all_profiles_data = await deps.repository.get_all_output_profiles()
    active_profile = {}
    for p_dict in all_profiles_data:
        if p_dict.get("id") == profile_to_use:
            active_profile = p_dict
            break

    if not active_profile:
        msg = f"Resolved output profile '{profile_to_use}' not found in SSOT database."
        logger.error("[SynthesisHook] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
        )

    synthesis_cfg = active_profile.get("synthesis", {}) or {}

    length_constraint = synthesis_cfg.get("length_constraint")
    preamble_dict = synthesis_cfg.get("preamble_text")
    omit_empty = synthesis_cfg.get("omit_empty_sections", True)
    enable_masking = synthesis_cfg.get("enable_pii_masking", False)
    include_historical_summary = synthesis_cfg.get("include_historical_summary", False)

    hook_metadata = state.metadata or {}
    raw_lang = str(hook_metadata.get("target_locale") or inputs.get("language") or "en")

    # Täydellinen sanitointi Accept-Language otsikoille (esim "fi-FI,fi;q=0.9")
    language = raw_lang.replace(",", ";").split(";")[0].split("-")[0].strip().lower()

    lang_map = {"fi": "Finnish", "en": "English", "sv": "Swedish", "et": "Estonian"}
    lang_name = lang_map.get(language, language.upper())

    preamble = _resolve_i18n_str(preamble_dict, "en")

    # --- Collect Target Blocks from UI Layouts ---
    layouts = active_profile.get("layouts", [])
    required_blocks = set()
    for layout in layouts:
        tb = layout.get("target_blocks", [])
        if isinstance(tb, list):
            for b in tb:
                required_blocks.add(b)

    # 1. Clean up inputs (Omit Empty Sections & Original Inputs)
    consolidated_inputs: dict[str, Any] = {}

    for k, v in inputs.items():
        is_requested = False
        if isinstance(v, dict):
            # Epic 14: UI provides PromptBlock IDs, inputs contains Step IDs -> step_data mapping.
            # We must check if any requested PromptBlock ID exists inside the step_data keys.
            if any(block_id in v for block_id in required_blocks):
                is_requested = True
        # Fallback if k happens to be a block ID
        if not is_requested and k in required_blocks:
            is_requested = True

        is_wildcard = ("*" in required_blocks) or not required_blocks

        if not is_requested:
            # Automaattinen kokoaminen (wildcard) tutkii pelkästään data-tyyppiä.
            # Jätetään mustat listat pois. Validin asiantuntijatuloksen tunnistaa reasoning_trace -kentästä.
            if not is_wildcard:
                continue
            if not (isinstance(v, dict) and "reasoning_trace" in v):
                continue

        empty_vals = ["null", "none", "n/a", "ei saatavilla"]
        if omit_empty and (
            v is None or v == "" or v == [] or str(v).strip() == "" or str(v).strip().lower() in empty_vals
        ):
            logger.debug("[SynthesisHook] Omitting empty section: %s", k)
            continue

        consolidated_inputs[k] = v

    if not consolidated_inputs:
        return HookResult(
            success=True,
            state_delta={
                "synthesized_markdown": "*No data available for synthesis.*",
                "cited_sources": [],
                "step_metadata_updates": {},
            },
        )

    # 1.5 Fetch Historical Framework Context
    historical_context_text = ""
    if include_historical_summary:
        user_id = inputs.get("user_id")
        org_id = inputs.get("organization_id")

        if user_id or org_id:
            logger.debug("[SynthesisHook] Fetching historical summary for org_id=%s, user_id=%s", org_id, user_id)
            all_execs = await deps.repository.get_all_executions(organization_id=org_id, user_id=user_id)

            valid_past = []
            for e in all_execs:
                if e.id == state.execution_id:
                    continue
                if e.status.value != "completed":
                    continue

                best_cache = None
                if e.profile_syntheses:
                    best_cache = e.profile_syntheses.get(profile_to_use)
                    if not best_cache:
                        best_cache = next(iter(e.profile_syntheses.values()))

                if not best_cache or not best_cache.synthesized_markdown:
                    continue

                valid_past.append((e, best_cache.synthesized_markdown))

            # Sort by completion date descending, take top 3
            valid_past.sort(key=lambda x: x[0].completed_at or x[0].created_at, reverse=True)
            top_3 = valid_past[:3]

            if top_3:
                historical_parts = []
                for past_e, past_md in reversed(top_3):
                    dt_str = past_e.completed_at.strftime("%Y-%m-%d") if past_e.completed_at else "Unknown Date"
                    historical_parts.append(f"--- Execution Date: {dt_str} ---\n{past_md}")

                historical_context_text = (
                    "<HistoricalContext>\n" + "\n\n".join(historical_parts) + "\n</HistoricalContext>\n\n"
                )

    # 2. Combine parts & PII mask
    combined_text_parts = []

    for k, v in consolidated_inputs.items():
        step_title = k
        if workflow_data and isinstance(workflow_data, dict):
            for step in workflow_data.get("steps", []):
                if str(step.get("id", "")).lower() == str(k).lower():
                    step_title = _resolve_i18n_str(step.get("name") or {}, "en") or k
                    break

        if isinstance(v, (dict, list)):
            v_str = json.dumps(v, ensure_ascii=False, indent=2)
        else:
            v_str = str(v)
        combined_text_parts.append(f"### Source: {step_title} (ID: {k})\n{v_str}")

    global_mapping = ContextMapper.build_global_mapping(workflow_data, layouts) if workflow_data else ""
    raw_input_text = historical_context_text + global_mapping + "\n\n".join(combined_text_parts)

    if enable_masking:
        raw_input_text = _mask_pii_local(raw_input_text)

    # --- Section-Level Synthesis Directives ---
    layouts = active_profile.get("layouts", [])
    section_instructions = []
    
    # Fetch all blocks to inject extrema scale bounds into the context mapper (V2 Architecture)
    all_blocks = []
    if hasattr(deps.repository, "get_all"):
        raw_blocks = await deps.repository.get_all("prompt_blocks")
        from backend_v2.models.v2_core import PromptBlock
        # FAIL-FAST: Map raw dicts to strict Pydantic Domain Models
        all_blocks = [PromptBlock.model_validate(rb) for rb in raw_blocks]

    for idx, layout in enumerate(layouts):
        l_synthesis = layout.get("synthesis")
        if not l_synthesis:
            continue

        l_system_prompt = l_synthesis.get("system_prompt")
        if not l_system_prompt or not str(l_system_prompt).strip():
            msg = (
                f"Layout '{idx}' has Section-Level Synthesis enabled but is missing the "
                "MANDATORY Cognitive Blueprint (system_prompt). Fallbacks are forbidden."
            )
            logger.error("[SynthesisHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        l_title = _resolve_i18n_str(layout.get("title") or {}, language) or f"Section {idx}"
        l_preamble = _resolve_i18n_str(l_synthesis.get("preamble_text") or {}, language)

        # Calculate a deterministic Layout ID matching BlueprintTransformer (using idx)
        l_view = layout.get("preset_view", layout.get("presetView", "default"))
        l_id = f"layout_{idx}_{l_view}"

        target_blocks = layout.get("target_blocks", [])

        instruction = f"LAYOUT ID: {l_id} | TITLE: {l_title}\n"
        instruction += f"SECTION-SPECIFIC COGNITIVE BLUEPRINT:\n{str(l_system_prompt).strip()}\n"

        if target_blocks and "*" not in target_blocks:
            instruction += ContextMapper.build_ordinal_mapping(target_blocks, all_blocks)
        else:
            instruction += "Target Data Filter: Synthesize all relevant information for this section.\n"

        if l_preamble:
            instruction += f"CRITICAL TONE/PREAMBLE FOR THIS SECTION: '{l_preamble}'\n"

        if l_synthesis.get("length_constraint"):
            instruction += f"LENGTH LIMIT: ~{l_synthesis.get('length_constraint')} chars.\n"

        section_instructions.append(instruction)

    custom_sys_prompt = synthesis_cfg.get("system_prompt")
    if not custom_sys_prompt or not str(custom_sys_prompt).strip():
        msg = (
            f"Profile '{profile_to_use}' is missing the MANDATORY Global Cognitive "
            "Blueprint (system_prompt). Fallbacks are forbidden."
        )
        logger.error("[SynthesisHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    sys_prompt = f"{str(custom_sys_prompt).strip()}\n\n"
    if length_constraint:
        sys_prompt += (
            f"GLOBAL SYNTHESIS LENGTH CONSTRAINT: The global output should be ~{length_constraint} characters.\n"
        )
    if preamble:
        sys_prompt += (
            "GLOBAL PREAMBLE INTRODUCTION: Start your global synthesis intuitively using the following "
            f"preamble tone/context: '{preamble}'\n"
        )

    if section_instructions:
        sys_prompt += "\n\n=== SECTION-LEVEL SYNTHESIS REQUIRED ===\n"
        sys_prompt += (
            "You MUST ALSO provide targeted synthesized summaries for the following "
            "distinct sections as an array in `section_syntheses`.\n\n"
        )
        sys_prompt += "\n\n".join(section_instructions)

    sys_prompt += (
        "\n\nOmit internal system identifiers or raw JSON keys. "
        "When referring to information, use inline numerical tags like [1], [2].\n"
        "CRITICAL RULE FOR CITATIONS: The numbers in your inline tags MUST perfectly correspond "
        "to the items in the `cited_sources` list (1-indexed). "
        "ONLY create a numerical citation tag AND add an entry to `cited_sources` if the source "
        "is an actual literary reference, empirical citation, methodology framework, or external "
        "document (e.g., 'Toulmin 2003', 'Sitra Report'). "
        "DO NOT use citation tags for general analysis sections, step titles, or internal data "
        "dumps. If you mention internal findings, state them directly without using it."
    )

    sys_prompt += (
        "\n\nCRITICAL XAI DEDUPLICATION RULE:\n"
        "Scan all raw inputs for specific outcome extensions (like 'falsification', 'coaching', "
        "'risk_flag', 'remediation_steps'). "
        "Because these may be generated repeatedly across multiple steps, you MUST deduplicate them globally. "
        "Group them logically, rank them descending by absolute criticality (impact/risk), and output ONLY "
        "the TOP 3 items per category into the `xai_highlights` array. Provide ONLY the core text, omitting "
        "any internal titles like 'Vasta-argumentti 1:'."
    )

    messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": raw_input_text}]

    # 4. LLM execution with telemetry
    try:
        # Fail-fast: Assuming the strategy for output formatting is named 'synthesis_strategy'
        client = await LLMClient.from_strategy("synthesis", repository=deps.repository)

        with logfire.span("text_consolidation_hook") as span:
            result, token_usage = await client.run_structured_task(
                messages=messages,
                response_model=SynthesisOutputDTO,
            )

            span.set_attribute("synthesized_markdown_length", len(result.synthesized_markdown))
            span.set_attribute("synthesis_token_usage", json.dumps(token_usage))

            step_metadata = state.metadata or {}
            current_usage = step_metadata.get("token_usage", {})
            for k, v in token_usage.items():
                current_usage[k] = current_usage.get(k, 0) + v

            section_dict = {}
            if result.section_syntheses:
                for s in result.section_syntheses:
                    section_dict[s.layout_id] = s.synthesized_markdown

            if language != "en":
                logger.info(f"[SynthesisHook] Synthesis completed in English. Translating to {lang_name.upper()}...")
                from backend_v2.hooks.translation_hook import translation_hook

                trans_state = HookState(
                    execution_id=state.execution_id,
                    workflow_id=state.workflow_id,
                    inputs={"language": language, "synthesized_markdown": result.synthesized_markdown, **section_dict},
                )
                trans_res = await translation_hook(trans_state, deps)  # type: ignore[misc]
                if trans_res.success and trans_res.state_delta:
                    logger.info("[SynthesisHook] Translation successful. Mapping back values.")
                    translated_global = trans_res.state_delta.get("synthesized_markdown", result.synthesized_markdown)

                    if result.cited_sources:
                        bib_title = "\n\n### Lähdeluettelo\n" if language == "fi" else "\n\n### References\n"
                        bib_items = [f"[{i + 1}] {src}" for i, src in enumerate(result.cited_sources)]
                        bib_text = bib_title + "\n".join(bib_items)
                        translated_global += bib_text

                    translated_sections = {}
                    for k in section_dict.keys():
                        translated_sections[k] = trans_res.state_delta.get(k, section_dict[k])

                    # Note: We do not translate xai_highlights right now (requires proper i18n mapping later)
                    # For now, pass them as raw dict strings which the UI will handle
                    raw_highlights = (
                        [h.model_dump() for h in result.xai_highlights]
                        if getattr(result, "xai_highlights", None)
                        else []
                    )

                    return HookResult(
                        success=True,
                        state_delta={
                            "synthesized_markdown": translated_global,
                            "section_syntheses": translated_sections,
                            "cited_sources": result.cited_sources,
                            "xai_highlights": raw_highlights,
                            "step_metadata_updates": {"token_usage": current_usage},
                        },
                    )

            # Return native English payload or fallback if translation failed
            global_md = result.synthesized_markdown
            if result.cited_sources:
                bib_title = "\n\n### Lähdeluettelo\n" if language == "fi" else "\n\n### References\n"
                bib_text = bib_title + "\n".join([f"[{i + 1}] {src}" for i, src in enumerate(result.cited_sources)])
                global_md += bib_text

            raw_highlights = (
                [h.model_dump() for h in result.xai_highlights] if getattr(result, "xai_highlights", None) else []
            )

            return HookResult(
                success=True,
                state_delta={
                    "synthesized_markdown": global_md,
                    "section_syntheses": section_dict,
                    "cited_sources": result.cited_sources,
                    "xai_highlights": raw_highlights,
                    "step_metadata_updates": {"token_usage": current_usage},
                },
            )

    except Exception as e:
        logger.error("Synthesis generation failed.", exc_info=True)
        raise AppException(
            message="Failed to execute TextConsolidationHook LLM synthesis.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.value},
        ) from e
