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
from backend_v2.core.security import sanitize_text
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.context_mapper import ContextMapper
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.synthesis import SynthesisMetadataDTO, SynthesisStepDataDTO
from backend_v2.models.dtos.output_profile import OutputProfileResponseDTO
from backend_v2.models.dtos.synthesis import SynthesisOutputDTO
from backend_v2.models.enums import HistoricalContextMode
from backend_v2.models.state import StepOutputDTO
from backend_v2.models.v2_core import ExecutionRecord, PromptBlock, Step, Workflow
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.mcp.mcp_tool_loop import execute_tool_loop
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

logger = logging.getLogger(__name__)


async def _fetch_historical_context(
    mode: HistoricalContextMode, inputs: dict[str, Any], deps: HookDependencies, state: HookState, profile_to_use: str
) -> str:
    """Fetch and format historical execution summaries based on the selected mode."""
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
            try:
                best_cache = e.profile_syntheses[profile_to_use]
            except KeyError:
                best_cache = next(iter(e.profile_syntheses.values()))

        if not best_cache or not best_cache.synthesized_markdown:
            continue

        valid_past.append((e, best_cache.synthesized_markdown))

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
    """Build an O(1) lookup map for resolving localized step and input titles."""
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
    """Deep copy and strip heavy Pydantic metadata and AI internal logs before sending to final synthesis."""
    if hasattr(v, "model_dump"):
        v = v.model_dump(mode="json")

    if not isinstance(v, (dict, list)):
        return str(v)

    clean_v = copy.deepcopy(v)

    def _strip_heavy_keys(obj: Any) -> None:
        if isinstance(obj, dict):
            obj.pop("shuffled_atoms", None)

            # Token Shield: Suodatetaan pois raskaat ruohonjuuritason evaluoinnit ja logit
            # jotta "Chief Editor" LLM voi keskittyä vain olennaisiin perusteluihin ja tuloksiin.
            obj.pop("evaluations", None)

            for _, val in list(obj.items()):
                _strip_heavy_keys(val)
        elif isinstance(obj, list):
            for item in obj:
                _strip_heavy_keys(item)

    _strip_heavy_keys(clean_v)
    return json.dumps(clean_v, ensure_ascii=False, indent=2)


def _build_section_instructions(layouts: list[Any], language: str, all_blocks: list[PromptBlock]) -> list[str]:
    """Compile section-level synthesis instructions for the LLM prompt."""
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

        l_preamble_model = l_synthesis.preamble_text
        l_preamble = l_preamble_model.resolve(language) if l_preamble_model else ""

        # Calculate a deterministic Layout ID matching BlueprintTransformer (using idx)
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
            instruction += f"    <target_language>{language}</target_language>\n"

        if l_synthesis.length_constraint:
            instruction += f"    <length_constraint_chars>{l_synthesis.length_constraint}</length_constraint_chars>\n"

        if l_preamble:
            instruction += f"    <preamble_tone>{l_preamble}</preamble_tone>\n"

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

    try:
        hook_metadata_dto = SynthesisMetadataDTO.model_validate(state.metadata or {})
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

    # Resolve active workflow to determine the output profile bounds

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

    # --- Epic 13 M1: Fetch Output Profile from SSOT ---
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
    length_constraint = synthesis_cfg.length_constraint
    preamble_dict = synthesis_cfg.preamble_text
    omit_empty = synthesis_cfg.omit_empty_sections
    enable_masking = synthesis_cfg.enable_pii_masking
    historical_mode = synthesis_cfg.historical_context_mode

    preamble = preamble_dict.resolve(language) if preamble_dict else ""

    # Fetch all blocks to inject extrema scale bounds and resolve titles (V2 Architecture)
    all_blocks = []
    all_steps = []
    if hasattr(deps.comp_repo, "get_all_prompt_blocks") and hasattr(deps.workflow_repo, "get_all_steps"):
        # Fetch blocks for the ContextMapper ordinal mapping
        raw_blocks = await deps.comp_repo.get_all_prompt_blocks()
        all_blocks = [PromptBlock.model_validate(rb) for rb in raw_blocks]

        # Fetch steps for Step title resolution
        raw_steps = await deps.workflow_repo.get_all_steps()
        all_steps = [Step.model_validate(rs) for rs in raw_steps]

    # Pre-calculate matrix step IDs based on strict schema routing to avoid duck-typing
    matrix_step_ids = set()
    if workflow_data and workflow_data.steps:
        step_def_map = {str(s.id): s for s in all_steps}
        block_map = {str(b.id): b for b in all_blocks}
        for w_step in workflow_data.steps:
            try:
                target_step = step_def_map[str(w_step.task_blueprint)]
            except KeyError:
                target_step = None

            if target_step and target_step.prompt_blocks:
                for b_id in target_step.prompt_blocks:
                    try:
                        p_block = block_map[str(b_id)]
                    except KeyError:
                        p_block = None

                    if p_block and p_block.category_id == "matrix":
                        matrix_step_ids.add(str(w_step.id))
                        break

    # --- Collect Target Blocks from UI Layouts ---
    layouts = active_profile_dto.layouts
    required_blocks: set[str] = set()
    for layout in layouts:
        tb = layout.target_blocks or []
        for blk_id in tb:
            required_blocks.add(blk_id)

    is_global_wildcard = ("*" in required_blocks) or not required_blocks

    # 1. Clean up inputs (Omit Empty Sections & Original Inputs)
    consolidated_inputs: dict[str, Any] = {}

    available_dtos: list[StepOutputDTO] = []

    # In V2, inputs.get("steps") is the definitive state source.
    steps_list = inputs.get("steps", [])
    if isinstance(steps_list, list):
        for item in steps_list:
            if isinstance(item, StepOutputDTO):
                available_dtos.append(item)
            elif isinstance(item, dict):
                try:
                    available_dtos.append(StepOutputDTO.model_validate(item))
                except ValidationError:
                    pass

    # Merge metadata injection
    if hook_metadata_dto.step_results:
        for item in hook_metadata_dto.step_results:
            if isinstance(item, StepOutputDTO):
                available_dtos.append(item)

    # Deduplicate and extract payload components
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
        except (ValidationError, TypeError, ValueError):
            step_dict = {"_value": step_data}

        # O(1) Set intersection logic replacing nested loops
        inner_keys = set(step_dict.keys())
        is_requested = False

        if step_id in required_blocks or block_id in required_blocks:
            is_requested = True
        elif not required_blocks.isdisjoint(inner_keys):
            is_requested = True
        else:
            # Final fallback for composite keys
            for inner_k in inner_keys:
                if f"{step_id}_{inner_k}" in required_blocks or f"{block_id}_{inner_k}" in required_blocks:
                    is_requested = True
                    break

        if not is_requested:
            if not is_wildcard:
                continue
            # reasoning_trace acts as a discriminator for LLM execution steps.
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

        consolidated_inputs[uid] = v

    if not consolidated_inputs:
        return HookResult(
            success=True,
            state_delta={
                "synthesized_markdown": "*NO_DATA_AVAILABLE*",
                "cited_sources": [],
                "step_metadata_updates": {},
            },
        )

    # 1.5 Fetch Historical Framework Context
    historical_context_text = await _fetch_historical_context(
        mode=historical_mode, inputs=inputs, deps=deps, state=state, profile_to_use=profile_to_use
    )

    # 2. Combine parts & PII mask
    combined_text_parts = []

    title_map = _build_title_map(workflow_data, all_steps, language)

    for k, v in consolidated_inputs.items():
        k_str = str(k).lower()
        step_title = title_map[k_str] if k_str in title_map else str(k)
        v_str = _compress_synthesis_payload(v)
        combined_text_parts.append(f"### Source: {step_title} (ID: {k})\n{v_str}")

    global_mapping = ContextMapper.build_global_mapping(workflow_data, layouts) if workflow_data else ""
    raw_input_text = (
        f"<source_data>\n{historical_context_text}{global_mapping}\n{chr(10).join(combined_text_parts)}\n</source_data>"
    )

    if enable_masking:
        raw_input_text, threats = sanitize_text(raw_input_text)
        if threats:
            logger.warning("[SynthesisHook] PII redacted during synthesis. Threat count: %d", len(threats))

    # --- Section-Level Synthesis Directives ---
    section_instructions = _build_section_instructions(active_profile_dto.layouts, language, all_blocks)

    custom_sys_prompt = synthesis_cfg.system_prompt
    if not custom_sys_prompt or not str(custom_sys_prompt).strip():
        msg = (
            f"Profile '{profile_to_use}' is missing the MANDATORY Global Cognitive "
            "Blueprint (system_prompt). Fallbacks are forbidden."
        )
        logger.error("[SynthesisHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    active_exts = active_profile_dto.visible_extensions
    max_items = active_profile_dto.max_extension_items or 2

    sys_prompt = "<system_directive>\n<execution_parameters>\n"
    sys_prompt += f"  <target_language>{language}</target_language>\n"

    if length_constraint:
        sys_prompt += f"  <global_length_constraint_chars>{length_constraint}</global_length_constraint_chars>\n"
    if preamble:
        sys_prompt += f"  <global_preamble_tone>{preamble}</global_preamble_tone>\n"
    if active_exts:
        ext_list = ", ".join([x.value for x in active_exts]) if isinstance(active_exts, list) else str(active_exts)
        sys_prompt += f"  <target_extensions_to_harvest>{ext_list}</target_extensions_to_harvest>\n"
        sys_prompt += f"  <max_extension_items_per_category>{max_items}</max_extension_items_per_category>\n"

    sys_prompt += "</execution_parameters>\n\n"

    sys_prompt += f"<objective>\n{str(custom_sys_prompt).strip()}\n</objective>\n<rules>\n"

    sys_prompt += (
        "  <rule>CRITICAL LANGUAGE MANDATE: You must process the input and generate all your output text, "
        "reasoning, and source justifications exclusively in the language specified in <target_language>.</rule>\n"
    )

    if length_constraint:
        sys_prompt += (
            "  <rule>GLOBAL SYNTHESIS LENGTH CONSTRAINT: The global output should be roughly the length "
            "specified in <global_length_constraint_chars>.</rule>\n"
        )
    if preamble:
        sys_prompt += (
            "  <rule>GLOBAL PREAMBLE INTRODUCTION: Start your global synthesis intuitively using the "
            "preamble tone/context specified in <global_preamble_tone>.</rule>\n"
        )

    sys_prompt += (
        "  <rule>TONE AND QUALITY MANDATE: Maintain a highly professional, analytical, and executive tone. "
        "Ensure the synthesis provides clear, actionable strategic value and avoids redundant "
        "or generic statements.</rule>\n"
    )

    if section_instructions:
        sys_prompt += "  <rule>=== SECTION-LEVEL SYNTHESIS REQUIRED ===\n"
        sys_prompt += (
            "You MUST ALSO provide targeted synthesized summaries for the following "
            "distinct sections as an array in `section_syntheses`.\n\n"
        )
        sys_prompt += "\n\n".join(section_instructions)
        sys_prompt += "\n  </rule>\n"

    sys_prompt += (
        "  <rule>Omit internal system identifiers or raw JSON keys. "
        "When referring to information, use inline numerical tags like [1], [2].\n"
        "CRITICAL RULE FOR CITATIONS: The numbers in your inline tags MUST perfectly correspond "
        "to the items in the `cited_sources` list (1-indexed). "
        "ONLY create a numerical citation tag AND add an entry to `cited_sources` if the source "
        "is an actual literary reference, empirical citation, methodology framework, or external "
        "document (e.g., 'Toulmin 2003', 'Sitra Report'). "
        "DO NOT use citation tags for general analysis sections, step titles, or internal data "
        "dumps. If you mention internal findings, state them directly without using it.</rule>\n"
    )

    if active_exts:
        sys_prompt += (
            "  <rule>CRITICAL XAI EXTENSION SYNTHESIS MANDATE:\n"
            "Your task is to act as the Chief Editor. Scan the flattened JSON outputs of the matrices for any "
            "localized extensions they produced. In the V2 schema, these extensions are always appended as suffixes "
            "to the matrix Stripe IDs (e.g., 'blk_22e3598e06414409_coaching', 'blk_80732a33fe1947ee_falsification').\n"
            "You must HARVEST these fragmented, atomized insights and SYNTHESIZE them into the most critical, "
            "high-impact global highlights per target extension category, limited to the count specified in "
            "<max_extension_items_per_category>. "
            "Do not simply copy-paste them blindly; elevate and merge overlapping insights to create a "
            "coherent executive summary. "
            "Output these items strictly into the `xai_highlights` array, "
            "using the EXACT target extension name from <target_extensions_to_harvest> in `extension_type`. "
            '(e.g. "coaching")\n'
            "Provide ONLY the core text, omitting any internal titles like 'Vasta-argumentti 1:'.</rule>\n"
        )

    sys_prompt += "</rules>\n</system_directive>"

    messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": raw_input_text}]

    # 4. LLM execution with telemetry
    # Fail-fast: Assuming the strategy for output formatting is named 'synthesis_strategy'
    client = await LLMClient.from_strategy("synthesis", repository=deps.system_repo)
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
        token_usage = tool_res.usage
        audit_traces = tool_res.audit_traces

        span.set_attribute("synthesized_markdown_length", len(result.synthesized_markdown))
        span.set_attribute("synthesis_token_usage", json.dumps(token_usage))

        current_usage = dict(hook_metadata_dto.token_usage)
        for k, v in token_usage.items():
            try:
                current_usage[k] = current_usage[k] + v
            except KeyError:
                current_usage[k] = v

        raw_audits = [a.model_dump(mode="json") for a in audit_traces] if audit_traces else []

        active_exts = active_profile_dto.visible_extensions
        if active_exts and not result.xai_highlights:
            msg = (
                "Fail-Fast: Synthesis LLM failed to produce any requested XAI "
                "Highlights (Context Exhaustion or Hallucination)."
            )
            logger.error("[SynthesisHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        section_dict = {}
        if result.section_syntheses:
            for s in result.section_syntheses:
                section_dict[s.layout_id] = s.synthesized_markdown

        # Synthesis is now natively generated in target_locale due to CRITICAL_LANGUAGE_MANDATE
        global_md = result.synthesized_markdown
        if result.cited_sources:
            bib_title = "\n\n### BIBLIOGRAPHY_HEADER\n"
            bib_text = bib_title + "\n".join([f"[{i + 1}] {src}" for i, src in enumerate(result.cited_sources)])
            global_md += bib_text

        raw_highlights = [h.model_dump() for h in result.xai_highlights] if result.xai_highlights else []

        # EPIC 13 M3: Save synthesis metrics directly to DB state
        return HookResult(
            success=True,
            state_delta={
                "synthesized_markdown": global_md,
                "section_syntheses": section_dict,
                "cited_sources": result.cited_sources,
                "xai_highlights": raw_highlights,
                "step_metadata_updates": {"token_usage": current_usage},
                "mcp_tool_audit": raw_audits,
            },
        )
