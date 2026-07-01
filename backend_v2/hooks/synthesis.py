"""Synthesis hooks for Output Management V3.

Implements TextConsolidationHook for generating LLM-based markdown synthesis,
enforcing length constraints, preamble text, local PII masking, and structured output.
"""

import copy
import json
import logging
from typing import Any

import logfire
from fastapi import status
from pydantic import ValidationError

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.context_mapper import ContextMapper
from backend_v2.llm.client import LLMClient
from backend_v2.llm.prompt_builder import build_system_directive
from backend_v2.models.domain.synthesis import SynthesisMetadataDTO, SynthesisStepDataDTO
from backend_v2.models.dtos.output_profile import OutputProfileResponseDTO
from backend_v2.models.dtos.synthesis import MatrixExplanationsResult, SynthesisOutputDTO
from backend_v2.models.enums import HistoricalContextMode
from backend_v2.models.prompts.hook_prompts import (
    SYNTHESIS_CITATION_RULES,
    SYNTHESIS_LENGTH_CONSTRAINT,
    SYNTHESIS_SDUI_MANDATES,
    SYNTHESIS_SECTION_RULES_PREFIX,
    SYNTHESIS_STATE_ISOLATION_MANDATE,
)
from backend_v2.models.state import StepOutputDTO
from backend_v2.models.v2_core import ExecutionRecord, PromptBlock, Step, Workflow
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.mcp.mcp_tool_loop import execute_tool_loop
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.pii_analyzer import get_pii_service

logger = logging.getLogger(__name__)


async def _fetch_historical_context(
    mode: HistoricalContextMode, inputs: dict[str, Any], deps: HookDependencies, state: HookState, profile_to_use: str
) -> str:
    """Fetch and format historical execution summaries based on the selected mode.

    Args:
        mode: The requested historical context retrieval strategy.
        inputs: Current input mappings.
        deps: Global hook dependencies.
        state: Executing context state.
        profile_to_use: Evaluated target output profile ID.

    Returns:
        XML structured historical context string or empty string if disabled.
    """
    if mode == HistoricalContextMode.DISABLED:
        return ""

    try:
        user_id = state.global_context_vars["user_id"]
    except KeyError:
        user_id = None

    try:
        org_id = state.global_context_vars["organization_id"]
    except KeyError:
        org_id = None

    if not (user_id or org_id):
        return ""

    logger.debug(
        "[SynthesisHook] Fetching historical summary for org_id=%s, user_id=%s, mode=%s",
        org_id,
        user_id,
        mode.value,
    )
    all_execs = await deps.exec_repo.get_all_executions(organization_id=org_id, user_id=user_id)

    valid_past = []
    for e in all_execs:
        if e.id == state.execution_id:
            continue
        if e.status.value != "completed":
            continue

        best_cache = None
        if e.profile_syntheses:
            if profile_to_use in e.profile_syntheses:
                best_cache = e.profile_syntheses[profile_to_use]
            else:
                continue

        if not best_cache or not best_cache.content_blocks:
            continue

        valid_past.append((e, json.dumps(best_cache.content_blocks, ensure_ascii=False)))

    valid_past.sort(key=lambda x: x[0].completed_at or x[0].created_at, reverse=True)

    if mode == HistoricalContextMode.SLIDING_WINDOW_3:
        valid_past = valid_past[:3]

    if not valid_past:
        return ""

    historical_parts = []
    for past_e, past_md in reversed(valid_past):
        dt_str = past_e.completed_at.strftime("%Y-%m-%d") if past_e.completed_at else "Unknown Date"
        historical_parts.append(f"--- Execution Date: {dt_str} ---\n{past_md}")

    return "<HistoricalContext>\n" + "\n\n".join(historical_parts) + "\n</HistoricalContext>\n\n"


def _build_title_map(workflow_data: Workflow | None, all_steps: list[Step], language: str) -> dict[str, str]:
    """Build an O(1) lookup map for resolving localized step and input titles.

    Args:
        workflow_data: The SSOT workflow definition blueprint.
        all_steps: Master list of all steps from the registry.
        language: Target translation locale code.

    Returns:
        Dictionary mapping step/input keys to resolved title strings.

    Raises:
        AppException: If a step references a missing blueprint (VALIDATION_FAILED).
    """
    title_map: dict[str, str] = {}
    if not workflow_data:
        return title_map

    if workflow_data.steps:
        step_def_map = {s.id: s for s in all_steps}
        for step in workflow_data.steps:
            try:
                target_step = step_def_map[step.task_blueprint]
            except KeyError:
                target_step = None

            if not target_step:
                msg = (
                    f"Data integrity failure: StepRule '{step.id}' "
                    f"references missing Step (TaskBlueprint) '{step.task_blueprint}'."
                )
                logger.error("[SynthesisHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            title_map[str(step.id).lower()] = target_step.name.resolve(language)

    if workflow_data.expected_inputs:
        for exp_in in workflow_data.expected_inputs:
            title_map[str(exp_in.input_key).lower()] = exp_in.label.resolve(language)

    return title_map


def _compress_synthesis_payload(v: dict[str, Any] | list[Any] | str | SynthesisStepDataDTO) -> str:
    """Deep copy and strip heavy Pydantic metadata and AI internal logs before sending to final synthesis.

    Args:
        v: The extracted JSON payload or DTO value to compress.

    Returns:
        A stringified JSON dump stripped of extraneous AI inference variables.
    """
    if hasattr(v, "model_dump"):
        v = v.model_dump(mode="json")

    if not isinstance(v, (dict, list)):
        return str(v)

    clean_v = copy.deepcopy(v)

    def _strip_heavy_keys(obj: Any) -> None:
        if isinstance(obj, dict):
            obj.pop("shuffled_atoms", None)

            # EPIC 70 Lite: Preserve evidence from evaluations for synthesis grounding
            # ARCHITECTURE LOCK (Rule 82/83): This evaluations filtering algorithm is a
            # deliberate business logic change — NOT defensive programming. The .get() calls
            # and isinstance checks are required to safely traverse polymorphic evaluation
            # payloads from heterogeneous LLM step outputs. DO NOT refactor or simplify.
            if "evaluations" in obj:
                evals = obj["evaluations"]
                if isinstance(evals, list):
                    lite_evals = []
                    for ev in evals:
                        if isinstance(ev, dict):
                            eq_list = ev.get("exact_quotes", [])
                            sr = ev.get("semantic_reasoning")

                            if not isinstance(eq_list, list):
                                eq_list = [eq_list] if eq_list else []

                            valid_quotes = []
                            for q in eq_list:
                                if not q:
                                    continue
                                q_text = (q.get("quote_text") or q.get("text", "")) if isinstance(q, dict) else str(q)
                                q_str = q_text.strip()
                                if (
                                    q_str
                                    and q_str not in ("None", "null", "N/A", "N/A - insufficient data")
                                    and not (q_str.startswith("[") and q_str.endswith("]"))
                                ):
                                    valid_quotes.append(q_str)

                            if valid_quotes:
                                lite_evals.append(
                                    {
                                        "atom_id": ev.get("atom_id"),
                                        "exact_quotes": [q[:300] for q in valid_quotes],
                                        "semantic_reasoning": str(sr)[:300] if sr else None,
                                    }
                                )
                    # Cap evaluations to prevent token budget explosion (max 20)
                    lite_evals = lite_evals[:20]
                    obj["evaluations"] = lite_evals if lite_evals else None
                else:
                    # Non-list evaluations are not valid evidence — strip them
                    obj["evaluations"] = None
                if not obj.get("evaluations"):
                    obj.pop("evaluations", None)

            for _, val in list(obj.items()):
                _strip_heavy_keys(val)
        elif isinstance(obj, list):
            for item in obj:
                _strip_heavy_keys(item)

    _strip_heavy_keys(clean_v)
    return json.dumps(clean_v, ensure_ascii=False, indent=2)


def _build_section_instructions(layouts: list[Any], language: str, all_blocks: list[PromptBlock]) -> list[str]:
    """Compile section-level synthesis instructions for the LLM prompt.

    Args:
        layouts: Display layouts declared in the active OutputProfile.
        language: Translated target locale string.
        all_blocks: The master registry of prompt blocks for mapping.

    Returns:
        A list of constructed XML sections to dynamically orchestrate multi-part LLM rendering.

    Raises:
        AppException: If a layout requests synthesis without a cognitive blueprint.
    """
    section_instructions: list[str] = []
    for idx, layout in enumerate(layouts):
        l_synthesis = layout.synthesis
        if not l_synthesis:
            continue

        l_system_prompt = l_synthesis.system_prompt
        if not l_system_prompt or not str(l_system_prompt).strip():
            msg = (
                f"Layout '{idx}' has Section-Level Synthesis enabled but is missing the "
                "MANDATORY Cognitive Blueprint (system_prompt). Fallbacks are forbidden."
            )
            logger.error("[SynthesisHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        l_title_model = layout.title
        l_title = l_title_model.resolve(language) if l_title_model else f"Section {idx}"

        l_view = layout.preset_view
        l_id = f"layout_{idx}_{l_view}"
        target_blocks = layout.target_blocks or []

        instruction = (
            f"<section_instruction>\n"
            f"  <execution_parameters>\n"
            f"    <layout_id>{l_id}</layout_id>\n"
            f"    <title>{l_title}</title>\n"
        )

        if language:
            instruction += f"    <required_output_language>{language}</required_output_language>\n"

        if l_synthesis.length_constraint:
            instruction += f"    <length_constraint_chars>{l_synthesis.length_constraint}</length_constraint_chars>\n"

        instruction += "  </execution_parameters>\n"
        instruction += f"  <cognitive_blueprint>\n{str(l_system_prompt).strip()}\n  </cognitive_blueprint>\n"

        if target_blocks and "*" not in target_blocks:
            mapping = ContextMapper.build_ordinal_mapping(target_blocks, all_blocks)
            instruction += f"  <target_data_filter>\n{mapping}\n  </target_data_filter>\n"
        else:
            instruction += (
                "  <target_data_filter>Synthesize all relevant information for this section.</target_data_filter>\n"
            )

        instruction += "</section_instruction>"

        section_instructions.append(instruction)

    return section_instructions


@hook_registry.register(name="text_consolidation_hook")
async def text_consolidation_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """HOOK: text_consolidation_hook.

    Executes LLM synthesis based on Output Profile configurations.

    Args:
        state: Immutable cognitive state including inputs.
        deps: HookDependencies providing data access.

    Returns:
        HookResult: Delta injected with synthesized markdown and tokens.

    Raises:
        AppException: If parameters or state metadata validate incorrectly.
    """
    logger.debug("[SynthesisHook] Running text_consolidation_hook...")
    if not state:
        msg = "Strict Fail-Fast Enforced: Missing HookState in text_consolidation_hook."
        logger.error("[SynthesisHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    inputs = state.inputs
    if not isinstance(inputs, dict):
        msg = "Missing or invalid 'inputs'. Expected dict."
        logger.error("[SynthesisHook] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    if not state.metadata:
        msg = "Strict Fail-Fast Enforced: state.metadata is missing or None."
        logger.error("[SynthesisHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    try:
        hook_metadata_dto = SynthesisMetadataDTO.model_validate(state.metadata)
        language = hook_metadata_dto.target_locale.strip().lower()
    except ValidationError as e:
        msg = f"Strict Fail-Fast Enforced: Execution metadata failed validation: {e}"
        logger.error("[SynthesisHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(
            message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
        ) from e

    if not hook_metadata_dto.step_results:
        msg = "Fail-Fast: Execution metadata is missing step_results. Cannot synthesize an empty execution."
        logger.error("[SynthesisHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(
            message=msg,
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    raw_workflow_data = await deps.workflow_repo.get_workflow_by_id(state.workflow_id)
    if not raw_workflow_data:
        msg = f"Workflow '{state.workflow_id}' not found."
        raise AppException(
            message=msg,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
        )
    workflow_data = Workflow.model_validate(raw_workflow_data)

    raw_exec_data = await deps.exec_repo.get_execution(state.execution_id)
    execution_data = ExecutionRecord.model_validate(raw_exec_data) if raw_exec_data else None

    output_profile_id = execution_data.output_profile_id if execution_data else None

    profile_to_use = output_profile_id

    if not profile_to_use:
        msg = f"Execution {state.execution_id} missing mandatory output_profile_id."
        logger.error("[SynthesisHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    p_dict = await deps.comp_repo.get_output_profile_by_id(profile_to_use)
    active_profile_dto: OutputProfileResponseDTO | None = None
    if p_dict:
        active_profile_dto = OutputProfileResponseDTO.model_validate(p_dict)

    if not active_profile_dto:
        msg = f"Resolved output profile '{profile_to_use}' not found in SSOT database."
        logger.error("[SynthesisHook] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
        )

    synthesis_cfg = active_profile_dto.synthesis
    if not synthesis_cfg:
        msg = f"Strict Fail-Fast Enforced: 'synthesis' missing from active profile '{profile_to_use}'."
        logger.error("[SynthesisHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

    length_constraint = synthesis_cfg.length_constraint
    preamble_dict = synthesis_cfg.preamble_text
    omit_empty = synthesis_cfg.omit_empty_sections
    enable_masking = synthesis_cfg.enable_pii_masking
    historical_mode = synthesis_cfg.historical_context_mode
    active_exts = getattr(active_profile_dto, "visible_block_extensions", [])

    if active_profile_dto.max_extension_items is None:
        msg = f"Strict Fail-Fast Enforced: 'max_extension_items' missing from active profile '{profile_to_use}'."
        logger.error("[SynthesisHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})
    max_items = active_profile_dto.max_extension_items

    preamble = preamble_dict.resolve(language) if preamble_dict else ""
    tone_text = (
        synthesis_cfg.tone_instruction.resolve(language) if (synthesis_cfg and synthesis_cfg.tone_instruction) else ""
    )

    all_blocks = []
    all_steps = []
    if hasattr(deps.comp_repo, "get_all_prompt_blocks") and hasattr(deps.workflow_repo, "get_all_steps"):
        raw_blocks = await deps.comp_repo.get_all_prompt_blocks()
        all_blocks = [PromptBlock.model_validate(rb) for rb in raw_blocks]

        raw_steps = await deps.workflow_repo.get_all_steps()
        all_steps = [Step.model_validate(rs) for rs in raw_steps]

    matrix_step_ids = set()
    if workflow_data and workflow_data.steps:
        step_def_map = {str(s.id): s for s in all_steps}
        block_map = {str(b.id): b for b in all_blocks}
        for w_step in workflow_data.steps:
            try:
                target_step = step_def_map[str(w_step.task_blueprint)]
            except KeyError as e:
                msg = (
                    f"Data integrity failure: Workflow Step '{w_step.id}' references "
                    f"missing Step (TaskBlueprint) '{w_step.task_blueprint}'."
                )
                logger.error("[SynthesisHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e

            target_step_blocks = []
            if target_step.role_block_id:
                target_step_blocks.append(target_step.role_block_id)
            if target_step.extraction_protocol_block_id:
                target_step_blocks.append(target_step.extraction_protocol_block_id)
            if target_step.criteria_block_ids:
                target_step_blocks.extend(target_step.criteria_block_ids)

            if target_step_blocks:
                for b_id in target_step_blocks:
                    try:
                        p_block = block_map[str(b_id)]
                    except KeyError as e:
                        msg = (
                            f"Data integrity failure: Step '{target_step.id}' references missing PromptBlock '{b_id}'."
                        )
                        logger.error("[SynthesisHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                        raise AppException(
                            message=msg,
                            status_code=400,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        ) from e

                    if p_block.category_id == "matrix":
                        matrix_step_ids.add(str(w_step.id))
                        break

    layouts = active_profile_dto.layouts
    required_blocks: set[str] = set()
    for layout in layouts:
        tb = layout.target_blocks or []
        for blk_id in tb:
            required_blocks.add(blk_id)

    is_global_wildcard = ("*" in required_blocks) or not required_blocks

    consolidated_inputs: dict[str, Any] = {}
    available_dtos: list[StepOutputDTO] = []

    if "steps" not in inputs:
        msg = "Strict Fail-Fast Enforced: 'steps' key is missing from state inputs."
        logger.error("[SynthesisHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    steps_list = inputs["steps"]
    if isinstance(steps_list, list):
        for item in steps_list:
            if isinstance(item, StepOutputDTO):
                available_dtos.append(item)
            elif isinstance(item, dict):
                try:
                    available_dtos.append(StepOutputDTO.model_validate(item))
                except ValidationError as e:
                    msg = f"Strict Fail-Fast Enforced: Invalid StepOutputDTO in inputs: {e}"
                    logger.error("[SynthesisHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from e

    if hook_metadata_dto.step_results:
        for item in hook_metadata_dto.step_results:
            if isinstance(item, StepOutputDTO):
                available_dtos.append(item)

    for step_dto_obj in available_dtos:
        step_id = step_dto_obj.step_id
        block_id = step_dto_obj.block_id
        step_data = step_dto_obj.payload
        uid = f"{step_id}_{block_id}"

        is_wildcard = is_global_wildcard

        try:
            step_dto = None
            if isinstance(step_data, dict):
                step_dto = SynthesisStepDataDTO.model_validate(step_data)
                step_dict = step_data
            elif hasattr(step_data, "model_dump"):
                step_dict = step_data.model_dump(mode="json")
                step_dto = SynthesisStepDataDTO.model_validate(step_dict)
            else:
                step_dict = {"_value": step_data}
        except (ValidationError, TypeError, ValueError) as e:
            msg = f"Strict Fail-Fast Enforced: Invalid synthesis step data for {uid}: {e}"
            logger.error("[SynthesisHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

        inner_keys = set(step_dict.keys())
        is_requested = False

        if step_id in required_blocks or block_id in required_blocks:
            is_requested = True
        elif not required_blocks.isdisjoint(inner_keys):
            is_requested = True
        else:
            for inner_k in inner_keys:
                if f"{step_id}_{inner_k}" in required_blocks or f"{block_id}_{inner_k}" in required_blocks:
                    is_requested = True
                    break

        if not is_requested:
            if not is_wildcard:
                continue
            if step_dto and step_dto.reasoning_trace is None:
                is_matrix_or_ext = False
                for m_id in matrix_step_ids:
                    if str(step_id) == m_id or str(step_id).startswith(f"{m_id}_"):
                        is_matrix_or_ext = True
                        break
                    if str(block_id) == m_id or str(block_id).startswith(f"{m_id}_"):
                        is_matrix_or_ext = True
                        break
                if not is_matrix_or_ext:
                    continue

        v = step_data

        if omit_empty and (v is None or v == "" or v == [] or str(v).strip() == ""):
            logger.debug("[SynthesisHook] Omitting empty section: %s", uid)
            continue

        logger.debug(
            "[SynthesisHook] Adding to consolidated_inputs: %s (is_requested: %s, wildcard: %s)",
            uid,
            is_requested,
            is_wildcard,
        )
        consolidated_inputs[uid] = v

    if not consolidated_inputs:
        return HookResult(
            success=True,
            state_delta={
                "synthesized_markdown": "*NO_DATA_AVAILABLE*",
                "content_blocks": [],
                "cited_sources": [],
                "step_metadata_updates": {},
            },
        )

    historical_context_text = await _fetch_historical_context(
        mode=historical_mode, inputs=inputs, deps=deps, state=state, profile_to_use=profile_to_use
    )

    combined_text_parts = []
    title_map = _build_title_map(workflow_data, all_steps, language)

    for k, v in consolidated_inputs.items():
        k_str = str(k).lower()
        step_title = title_map[k_str] if k_str in title_map else str(k)
        v_str = _compress_synthesis_payload(v)
        combined_text_parts.append(f"### Source: {step_title} (ID: {k})\n{v_str}")

    # Pythonic XAI Highlights Harvesting
    raw_highlights = []
    if active_exts:
        active_ext_names = [x.value for x in active_exts] if isinstance(active_exts, list) else []
        for _, payload in consolidated_inputs.items():
            if isinstance(payload, dict) and "extensions" in payload:
                for ext_name, ext_items in payload["extensions"].items():
                    if ext_name in active_ext_names:
                        if isinstance(ext_items, list):
                            for item in ext_items:
                                raw_highlights.append({"extension_type": ext_name, "content": str(item)})
                        elif isinstance(ext_items, str) and ext_items.strip():
                            # Curation of Matrix Extensions, Step 1: Harvest string-based extensions
                            raw_highlights.append({"extension_type": ext_name, "content": ext_items.strip()})

    raw_ext_blocks = []
    for item in raw_highlights:
        ext_type = item["extension_type"]
        ext_content = item["content"]
        raw_ext_blocks.append(f'  <extension type="{ext_type}">{ext_content}</extension>')
    raw_ext_xml = ""
    if raw_ext_blocks:
        raw_ext_xml = "<raw_extensions>\n" + "\n".join(raw_ext_blocks) + "\n</raw_extensions>\n\n"

    global_mapping = ContextMapper.build_global_mapping(workflow_data, layouts) if workflow_data else ""
    raw_input_text = (
        f"{historical_context_text}\n"
        f"<source_data>\n{global_mapping}\n{chr(10).join(combined_text_parts)}\n</source_data>\n\n"
        f"{raw_ext_xml}"
    )

    if enable_masking:
        pii_service = get_pii_service()
        sanitized_text = pii_service.mask_pii(text=raw_input_text, language=language)
        if sanitized_text != raw_input_text:
            logger.warning("[SynthesisHook] PII redacted during synthesis.")
        raw_input_text = sanitized_text

    section_instructions = _build_section_instructions(active_profile_dto.layouts, language, all_blocks)

    custom_sys_prompt = synthesis_cfg.system_prompt
    if not custom_sys_prompt or not str(custom_sys_prompt).strip():
        msg = (
            f"Profile '{profile_to_use}' is missing the MANDATORY Global Cognitive "
            "Blueprint (system_prompt). Fallbacks are forbidden."
        )
        logger.error("[SynthesisHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    if not active_profile_dto or not active_profile_dto.scoring_strategy:
        msg = f"Strict Fail-Fast Enforced: 'scoring_strategy' missing from active profile '{profile_to_use}'."
        logger.error("[SynthesisHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

    scoring_strategy = active_profile_dto.scoring_strategy.value

    rules = list(SYNTHESIS_SDUI_MANDATES)

    if length_constraint:
        rules.append(SYNTHESIS_LENGTH_CONSTRAINT)

    if tone_text:
        rules.append(f"TONE INSTRUCTION: {tone_text}")

    if section_instructions:
        section_rules = SYNTHESIS_SECTION_RULES_PREFIX
        section_rules += "\n\n".join(section_instructions)
        rules.append(section_rules)

    rules.append(SYNTHESIS_CITATION_RULES)

    rules.append(SYNTHESIS_STATE_ISOLATION_MANDATE)

    exec_params = [
        f"  <scoring_strategy>{scoring_strategy}</scoring_strategy>",
        f"  <max_extension_items>{max_items}</max_extension_items>",
    ]
    if length_constraint:
        exec_params.append(f"  <global_length_constraint_chars>{length_constraint}</global_length_constraint_chars>")

    sys_prompt = build_system_directive(
        objective=str(custom_sys_prompt).strip(),
        rules=rules,
        execution_parameters="\n".join(exec_params),
    )

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": raw_input_text},
    ]

    strategy_name = synthesis_cfg.model_strategy
    client = await LLMClient.from_strategy(strategy_name, repository=deps.system_repo)
    executor = LLMTaskExecutor(prompt_compiler=PromptCompiler())
    allowed_tools = synthesis_cfg.allowed_mcp_tools

    with logfire.span("text_consolidation_hook") as span:
        tool_res = await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=messages,
            response_model=SynthesisOutputDTO,
            allowed_tools=allowed_tools,
            step_name="text_consolidation_hook",
            target_language=language,
        )
        result = SynthesisOutputDTO.model_validate(tool_res.result_data)
        raw_highlights = [h.model_dump(mode="json") for h in result.xai_highlights] if result.xai_highlights else []
        token_usage = tool_res.usage
        audit_traces = tool_res.audit_traces

        span.set_attribute("content_blocks_count", len(result.content_blocks))
        span.set_attribute("synthesis_token_usage", token_usage.model_dump_json())

        updated_usage = hook_metadata_dto.token_usage + token_usage

        raw_audits = [a.model_dump(mode="json") for a in audit_traces] if audit_traces else []

        section_dict = {}
        if result.section_syntheses:
            layout_defs = active_profile_dto.layouts if active_profile_dto and active_profile_dto.layouts else []
            for s in result.section_syntheses:
                safe_blocks = []

                for idx, layout in enumerate(layout_defs):
                    l_view = layout.preset_view
                    l_id = f"layout_{idx}_{l_view}"
                    if l_id == s.layout_id and layout.synthesis and layout.synthesis.preamble_text:
                        l_preamble_model = layout.synthesis.preamble_text
                        l_preamble = l_preamble_model.resolve(language) if l_preamble_model else ""
                        if l_preamble:
                            safe_blocks.append({"block_type": "markdown", "text": l_preamble})
                        break

                for b in s.content_blocks:
                    try:
                        safe_blocks.append(b.model_dump(mode="json"))
                    except Exception as e:
                        logger.error("[SynthesisHook] Block serialization failed in layout %s: %s", s.layout_id, e)
                section_dict[s.layout_id] = safe_blocks

        global_blocks = []
        if preamble:
            global_blocks.append({"block_type": "markdown", "text": preamble})

        for b in result.content_blocks:
            try:
                global_blocks.append(b.model_dump(mode="json"))
            except Exception as e:
                logger.error("[SynthesisHook] Global block serialization failed: %s", e)
        # Pythonic Extract Audit Trail
        all_audit_traces = audit_traces.copy() if audit_traces else []
        if (
            execution_data
            and getattr(execution_data, "frozen_context", None)
            and getattr(execution_data.frozen_context, "mcp_tool_audit", None)
        ):
            seen = {f"{t.tool_id}::{t.query}" for t in all_audit_traces}
            for t in execution_data.frozen_context.mcp_tool_audit:
                uid = f"{t.tool_id}::{t.query}"
                if uid not in seen:
                    all_audit_traces.append(t)
                    seen.add(uid)

        row_explanations_dict = {}
        row_curated_quotes_dict = {}
        row_exp_rule = "MAXIMUM LENGTH IS 30 WORDS. KEEP IT CONCISE BUT INFORMATIVE."

        row_rules = [
            "Focus strictly on the core reason for the score in row_explanation.",
        ]
        if tone_text:
            row_rules.append(f"TONE INSTRUCTION: {tone_text}")
        row_rules.extend(
            [
                "Do not use markdown, line breaks, or bullet points in row_explanation.",
                row_exp_rule,
            ]
        )

        row_exp_prompt = build_system_directive(
            objective=(
                "1. 'row_explanation': Summarize the justification into exactly ONE short sentence addressing the user directly.\n"
                "2. 'curated_quotes': Review the provided quotes. Select up to <max_extension_items> MOST CONCRETE quotes verbatim from the user's original input."
            ),
            rules=row_rules,
        )

        atom_quotes: dict[str, list[str]] = {}
        for step_dto_obj in available_dtos:
            if step_dto_obj.block_id == "atom_quotes" and isinstance(step_dto_obj.payload, dict):
                atom_quotes.update(step_dto_obj.payload)

        matrices_to_explain_map: dict[str, dict[str, Any]] = {}
        for step_dto_obj in available_dtos:
            payload = step_dto_obj.payload
            block_id = step_dto_obj.block_id

            if isinstance(payload, dict) and "normalized_score" in payload and block_id in atom_quotes:
                quotes_list = atom_quotes[block_id]
                if quotes_list and block_id not in matrices_to_explain_map:
                    justification_text = "\n".join([f"- {q}" for q in quotes_list])
                    matrices_to_explain_map[block_id] = {
                        "matrix_id": block_id,
                        "score": payload["normalized_score"],
                        "justification": justification_text,
                    }

        matrices_to_explain = list(matrices_to_explain_map.values())

        if matrices_to_explain:
            try:
                user_msg = (
                    "<execution_parameters>\n"
                    "  <task>generate_row_explanations</task>\n"
                    f"  <max_extension_items>{max_items}</max_extension_items>\n"
                    f"  <required_output_language>{language}</required_output_language>\n"
                    "</execution_parameters>\n"
                    "<source_data>\n"
                    f"{json.dumps(matrices_to_explain, indent=2)}\n"
                    "</source_data>"
                )
                exp_messages = [{"role": "system", "content": row_exp_prompt}, {"role": "user", "content": user_msg}]

                exp_client = await LLMClient.from_strategy("strict", repository=deps.system_repo)

                exp_res, exp_usage = await executor.execute_structured_task(
                    client=exp_client, messages=exp_messages, response_model=MatrixExplanationsResult
                )

                for item in exp_res.explanations:
                    row_explanations_dict[item.matrix_id] = item.row_explanation
                    row_curated_quotes_dict[item.matrix_id] = item.curated_quotes

                updated_usage = updated_usage + exp_usage
            except Exception as e:
                logger.error("[SynthesisHook] Row explanation generation failed: %s", e, exc_info=True)

        return HookResult(
            success=True,
            state_delta={
                "content_blocks": global_blocks,
                "section_syntheses": section_dict,
                "cited_sources": result.cited_sources,
                "xai_highlights": raw_highlights,
                "row_explanations": row_explanations_dict,
                "row_curated_quotes": row_curated_quotes_dict,
                "step_metadata_updates": {"token_usage": updated_usage.model_dump(mode="json")},
                "mcp_tool_audit": raw_audits,
            },
        )
