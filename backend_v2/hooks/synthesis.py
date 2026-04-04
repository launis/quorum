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
from backend_v2.llm.client import LLMClient

logger = logging.getLogger(__name__)


class SynthesisOutputDTO(BaseModel):
    """Structured output expected from the Synthesis LLM."""

    synthesized_markdown: str = Field(..., description="The fully synthesized and deduplicated markdown content.")
    cited_sources: list[str] = Field(default_factory=list, description="List of references or citations found.")
    section_syntheses: dict[str, str] = Field(
        default_factory=dict, description="Dictionary mapping Layout ID to its unique synthesized markdown content."
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

    default_pid = workflow_data.get("default_profile_id", "default")
    profile_to_use = output_profile_id or default_pid

    output_profiles = workflow_data.get("output_profiles", {})
    active_profile = output_profiles.get(profile_to_use, {})
    synthesis_cfg = active_profile.get("synthesis", {}) or {}

    length_constraint = synthesis_cfg.get("length_constraint")
    preamble_dict = synthesis_cfg.get("preamble_text")
    omit_empty = synthesis_cfg.get("omit_empty_sections", True)
    enable_masking = synthesis_cfg.get("enable_pii_masking", False)
    include_historical_summary = synthesis_cfg.get("include_historical_summary", False)

    language = str(state.global_context_vars.get("language") or inputs.get("language") or "en")
    language = language.split("-")[0].lower()

    preamble = _resolve_i18n_str(preamble_dict, language)

    # 1. Clean up inputs (Omit Empty Sections)
    consolidated_inputs = {}
    for k, v in inputs.items():
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
                if not e.synthesized_markdown:
                    continue
                valid_past.append(e)

            # Sort by completion date descending, take top 3
            valid_past.sort(key=lambda x: x.completed_at or x.created_at, reverse=True)
            top_3 = valid_past[:3]

            if top_3:
                historical_parts = []
                for past_e in reversed(top_3):
                    dt_str = past_e.completed_at.strftime("%Y-%m-%d") if past_e.completed_at else "Unknown Date"
                    historical_parts.append(f"--- Execution Date: {dt_str} ---\n{past_e.synthesized_markdown}")

                historical_context_text = (
                    "<HistoricalContext>\n" + "\n\n".join(historical_parts) + "\n</HistoricalContext>\n\n"
                )

    # 2. Combine parts & PII mask
    combined_text_parts = []
    for k, v in consolidated_inputs.items():
        combined_text_parts.append(f"### {k}\n{v}")

    raw_input_text = historical_context_text + "\n\n".join(combined_text_parts)

    if enable_masking:
        raw_input_text = _mask_pii_local(raw_input_text)

    # --- Section-Level Synthesis Directives ---
    layouts = active_profile.get("layouts", [])
    section_instructions = []

    for idx, layout in enumerate(layouts):
        l_synthesis = layout.get("synthesis")
        if not l_synthesis:
            continue

        l_title = _resolve_i18n_str(layout.get("title") or {}, language) or f"Section {idx}"
        l_preamble = _resolve_i18n_str(l_synthesis.get("preamble_text") or {}, language)

        # Calculate a deterministic Layout ID matching BlueprintTransformer
        l_view = layout.get("preset_view", "default")
        l_id = f"layout_{l_view}_{str(hash(l_title))}"

        target_blocks = layout.get("target_blocks", [])

        instruction = f"LAYOUT ID: {l_id} | TITLE: {l_title}\n"
        if target_blocks and "*" not in target_blocks:
            instruction += f"Only synthesize information regarding these keys: {', '.join(target_blocks)}\n"
        else:
            instruction += "Synthesize all relevant information for this section.\n"

        if l_preamble:
            instruction += f"CRITICAL TONE/PREAMBLE FOR THIS SECTION: '{l_preamble}'\n"

        if l_synthesis.get("length_constraint"):
            instruction += f"LENGTH LIMIT: ~{l_synthesis.get('length_constraint')} chars.\n"

        section_instructions.append(instruction)

    sys_prompt = f"TARGET LANGUAGE: {language.upper()}\n"
    sys_prompt += (
        "You are a professional report synthesizer. Merge, deduplicate, and seamlessly "
        "synthesize the provided information into cohesive markdown.\n"
    )
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
            "distinct sections in the `section_syntheses` dict, mapped by LAYOUT ID.\n\n"
        )
        sys_prompt += "\n\n".join(section_instructions)

    sys_prompt += (
        "\n\nOmit internal system identifiers or raw JSON keys. "
        "Cite your sources using inline tags [1], [2] if data originates from external tools."
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

            return HookResult(
                success=True,
                state_delta={
                    "synthesized_markdown": result.synthesized_markdown,
                    "section_syntheses": result.section_syntheses,
                    "cited_sources": result.cited_sources,
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
