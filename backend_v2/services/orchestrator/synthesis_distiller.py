"""Synthesis Distiller Hook for the Cognitive Quorum DAG Pipeline.

Replaces the legacy 'God Code' in synthesis.py by providing a deterministic
logic DAG node that distills evaluation data, fetches historical context,
and prepares the matrices_to_explain list for the downstream row explanations
LLM step.

Epic 93 Phase 2: Pipeline Unification — Milestone 1.
"""

import copy
import json
import logging
from typing import Any

from fastapi import status
from pydantic import BaseModel

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.synthesis import SynthesisStepDataDTO
from backend_v2.models.enums import HistoricalContextMode
from backend_v2.models.state import StepOutputDTO
from backend_v2.models.v2_core import ExecutionRecord, PromptBlock, Step, Workflow
from backend_v2.utils.alias_engine import AliasEngine

logger = logging.getLogger(__name__)


def _compress_synthesis_payload(v: dict[str, Any] | list[Any] | str | SynthesisStepDataDTO) -> str:
    """Deep copy and strip heavy Pydantic metadata and AI internal logs before sending to final synthesis.

    Args:
        v: The extracted JSON payload or DTO value to compress.

    Returns:
        A stringified JSON dump stripped of extraneous AI inference variables.
    """
    if isinstance(v, BaseModel):
        v = v.model_dump(mode="json")
    elif isinstance(v, list):
        v = [item.model_dump(mode="json") if isinstance(item, BaseModel) else item for item in v]

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
                                q_text = (
                                    (q.get("quote") or q.get("quote_text") or q.get("text", ""))
                                    if isinstance(q, dict)
                                    else str(q)
                                )
                                q_str = q_text.strip()
                                if (
                                    q_str
                                    and q_str not in ("None", "null", "N/A", "N/A - insufficient data")
                                    and not (q_str.startswith("[") and q_str.endswith("]"))
                                ):
                                    valid_quotes.append(q_str)

                            if valid_quotes:
                                lite_ev = {
                                    "atom_id": ev.get("atom_id"),
                                    "exact_quotes": [q[:300] for q in valid_quotes],
                                    "semantic_reasoning": str(sr)[:300] if sr else None,
                                }
                                if "extensions" in ev:
                                    lite_ev["extensions"] = ev["extensions"]
                                lite_evals.append(lite_ev)
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


async def _fetch_historical_context(
    mode: HistoricalContextMode, deps: HookDependencies, state: HookState, profile_to_use: str
) -> str:
    """Fetch and format historical execution summaries based on the selected mode.

    Args:
        mode: The requested historical context retrieval strategy.
        deps: Global hook dependencies.
        state: Executing context state.
        profile_to_use: Evaluated target output profile ID.

    Returns:
        Markdown structured historical context string or empty string if disabled.
    """
    # Epic 93 Phase 2, Milestone 1.3: Historical context fetch inside distiller hook
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
        "[SynthesisDistiller] Fetching historical summary for org_id=%s, user_id=%s, mode=%s",
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

        if not best_cache or not best_cache.section_syntheses:
            continue

        all_blocks = []
        for blocks in best_cache.section_syntheses.values():
            all_blocks.extend(blocks)

        if not all_blocks:
            continue

        valid_past.append((e, json.dumps([b.model_dump(mode="json") for b in all_blocks], ensure_ascii=False)))

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
    # Epic 93 Phase 2, Milestone 1.4: Title map migration
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
                logger.error("[SynthesisDistiller] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
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


def _assemble_matrices_to_explain(
    available_dtos: list[StepOutputDTO], title_map: dict[str, str], blocks_by_id: dict[str, PromptBlock]
) -> list[dict[str, Any]]:
    """Assemble the matrices_to_explain list by extracting quotes from Epic 94 evaluated_atoms.

    Epic 94 Enriched Atom Graph migration: Extracts directly from MatrixScorecardRowDTO structures.
    Epic 133A: Supports lightweight MatrixEvaluationResult dictionaries.

    Args:
        available_dtos: All step output DTOs from the execution state.
        title_map: Map of localized titles.
        blocks_by_id: Map of PromptBlock ID to PromptBlock model.

    Returns:
        List of dicts with keys: matrix_id, score, justification.
    """
    matrices_to_explain_map: dict[str, dict[str, Any]] = {}
    alias_engine = AliasEngine()

    # Epic 133A/133B Migration: Build global map of tda_id -> list of quotes
    global_quotes_map: dict[str, list[str]] = {}
    for dto in available_dtos:
        if isinstance(dto.payload, dict) and "results" in dto.payload:
            for atom_res in dto.payload["results"]:
                if isinstance(atom_res, dict) and "tda_id" in atom_res:
                    t_id = atom_res["tda_id"]
                    quotes = []

                    if "exact_quotes" in atom_res and isinstance(atom_res["exact_quotes"], list):
                        for eq in atom_res["exact_quotes"]:
                            if isinstance(eq, dict):
                                txt = eq.get("text") or eq.get("quote")
                                if txt:
                                    quotes.append(str(txt))
                    elif "extensions" in atom_res and isinstance(atom_res["extensions"], dict):
                        ext_quotes = atom_res["extensions"].get("exact_quotes", [])
                        if isinstance(ext_quotes, list):
                            for eq in ext_quotes:
                                if isinstance(eq, dict):
                                    txt = eq.get("text") or eq.get("quote")
                                    if txt:
                                        quotes.append(str(txt))
                                elif isinstance(eq, str):
                                    quotes.append(eq)

                    if not quotes and "source_quote" in atom_res and atom_res["source_quote"]:
                        quotes.append(str(atom_res["source_quote"]))

                    if quotes:
                        global_quotes_map[t_id] = quotes

    for step_dto_obj in available_dtos:
        payload = step_dto_obj.payload
        block_id = step_dto_obj.block_id

        pb = blocks_by_id.get(block_id)
        if not pb or pb.category_id != "matrix":
            continue

        if isinstance(payload, dict):
            quotes_list: list[str] = []
            evaluated_claims: list[str] = []

            # Map tda_id to its claim label for fallback explanation
            tda_to_claim = {}
            if pb.scales is not None:
                for scale in pb.scales:
                    if scale.claims is not None:
                        for claim in scale.claims:
                            try:
                                claim_text = claim.label.resolve("en") if hasattr(claim.label, "resolve") else ""
                            except Exception:
                                claim_text = ""
                            if claim_text and claim.tda_assertions is not None:
                                for tda in claim.tda_assertions:
                                    tda_to_claim[tda.tda_id] = claim_text

            # Epic 133A: Lightweight Matrix evaluates atoms as a dict
            atoms = payload.get("evaluated_atoms", {})

            if isinstance(atoms, dict):
                for tda_id, hit_status in atoms.items():
                    if hit_status is True or str(hit_status).upper() == "PASS":
                        if tda_id in global_quotes_map:
                            quotes_list.extend(global_quotes_map[tda_id])
                        if tda_id in tda_to_claim:
                            evaluated_claims.append(tda_to_claim[tda_id])

            elif isinstance(atoms, list):
                # Legacy extraction logic for MatrixScorecardRowDTO arrays
                for atom in atoms:
                    if isinstance(atom, dict):
                        a_id = atom.get("atom_id")
                        if a_id and a_id in tda_to_claim:
                            evaluated_claims.append(tda_to_claim[a_id])

                        exact_quotes = atom.get("exact_quotes", [])
                        if isinstance(exact_quotes, list):
                            for evidence in exact_quotes:
                                if isinstance(evidence, dict) and "quote" in evidence and evidence["quote"]:
                                    quotes_list.append(str(evidence["quote"]))

            if block_id not in matrices_to_explain_map:
                matrix_alias = alias_engine.register(block_id, prefix="MX-")
                # Deduplicate quotes to prevent redundant justifications
                unique_quotes = list(dict.fromkeys(quotes_list))

                level_breakdown_str = ""
                level_breakdown = payload.get("level_breakdown")
                if isinstance(level_breakdown, dict) and level_breakdown:
                    breakdowns = []
                    for lvl, stats in level_breakdown.items():
                        if isinstance(stats, dict):
                            hits = stats.get("hits", 0)
                            total = stats.get("total", 0)
                            breakdowns.append(f"Level {lvl}: {hits}/{total} hits")
                    if breakdowns:
                        level_breakdown_str = "[DISTRIBUTION CONTEXT: " + ", ".join(breakdowns) + "]\n\n"

                if unique_quotes:
                    justification_text = level_breakdown_str + "\n".join([f"- {q}" for q in unique_quotes])
                elif evaluated_claims:
                    unique_claims = list(dict.fromkeys(evaluated_claims))
                    justification_text = (
                        level_breakdown_str
                        + "Evaluation based on the targeted presence/absence of: "
                        + ", ".join(unique_claims)
                    )
                else:
                    justification_text = level_breakdown_str + "No direct evidence quotes extracted for this matrix."

                matrices_to_explain_map[block_id] = {
                    "real_matrix_id": block_id,
                    "matrix_id": matrix_alias,
                    "matrix_label": title_map.get(block_id.lower(), block_id),
                    "score": payload.get("normalized_score"),
                    "justification": justification_text,
                }

    return list(matrices_to_explain_map.values())


@hook_registry.register(name="synthesis_distiller_hook")
async def synthesis_distiller_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """HOOK: synthesis_distiller_hook.

    Logic DAG node that distills execution state data for downstream synthesis and
    row explanation LLM steps. Performs metadata stripping, historical context
    fetching, title map resolution, and matrices_to_explain assembly.

    Epic 93 Phase 2, Milestone 1.6: Hook registration.

    Args:
        state: Immutable cognitive state including inputs.
        deps: HookDependencies providing data access.

    Returns:
        HookResult with state_delta containing distilled_inputs, historical_context,
        title_map, and matrices_to_explain.

    Raises:
        AppException: If state or metadata validation fails.
    """
    logger.debug("[SynthesisDistiller] Running synthesis_distiller_hook...")

    if not state:
        msg = "Strict Fail-Fast Enforced: Missing HookState in synthesis_distiller_hook."
        logger.error("[SynthesisDistiller] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    inputs = state.inputs
    if not isinstance(inputs, dict):
        msg = "Missing or invalid 'inputs'. Expected dict."
        logger.error("[SynthesisDistiller] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    if "steps" not in inputs:
        msg = "Strict Fail-Fast Enforced: 'steps' key is missing from state inputs."
        logger.error("[SynthesisDistiller] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    # Phase 2, Milestone 1.6: Parse available DTOs from state
    available_dtos: list[StepOutputDTO] = []
    steps_list = inputs["steps"]
    if isinstance(steps_list, list):
        for item in steps_list:
            if isinstance(item, StepOutputDTO):
                available_dtos.append(item)
            elif isinstance(item, dict):
                available_dtos.append(StepOutputDTO.model_validate(item))

    # Phase 2, Milestone 1.6: Fetch workflow and execution for context resolution
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
    if not output_profile_id:
        msg = f"Execution {state.execution_id} missing mandatory output_profile_id."
        logger.error("[SynthesisDistiller] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    # Phase 2, Milestone 1.6: Resolve output profile for historical context mode
    p_dict = await deps.output_profile_repo.get_output_profile_by_id(output_profile_id)
    if not p_dict:
        msg = f"Resolved output profile '{output_profile_id}' not found in SSOT database."
        logger.error("[SynthesisDistiller] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
        )

    if not state.metadata or "target_locale" not in state.metadata:
        msg = "Strict Fail-Fast Enforced: 'target_locale' missing from execution metadata."
        logger.error("[SynthesisDistiller] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
    language = str(state.metadata["target_locale"]).strip().lower()

    historical_mode = workflow_data.historical_context_mode

    # Phase 2, Milestone 1.3: Fetch historical context inside distiller
    historical_context_text = await _fetch_historical_context(
        mode=historical_mode, deps=deps, state=state, profile_to_use=output_profile_id
    )

    # Phase 2, Milestone 1.4: Build title map
    raw_steps = await deps.workflow_repo.get_all_steps()
    all_steps = [Step.model_validate(rs) for rs in raw_steps]

    title_map = _build_title_map(workflow_data, all_steps, language)

    alias_engine = AliasEngine()

    uid_to_alias: dict[str, str] = {}
    for step_dto_obj in available_dtos:
        step_id = step_dto_obj.step_id
        block_id = step_dto_obj.block_id
        uid = f"{step_id}_{block_id}"
        uid_to_alias[uid] = alias_engine.register(uid, prefix="DOC-")

    consolidated_distilled_parts: list[str] = []

    for step_dto_obj in available_dtos:
        step_id = step_dto_obj.step_id
        block_id = step_dto_obj.block_id
        uid = f"{step_id}_{block_id}"

        short_alias = uid_to_alias.get(uid, uid)

        k_str = uid.lower()
        step_title = title_map[k_str] if k_str in title_map else str(uid)
        v_str = _compress_synthesis_payload(step_dto_obj.payload)

        # Inject the SHORT ALIAS instead of the long UID
        consolidated_distilled_parts.append(f'<source id="{short_alias}" title="{step_title}">\n{v_str}\n</source>')

    # Phase 2, Milestone 1.5: Assemble matrices_to_explain
    raw_blocks = await deps.prompt_block_repo.get_all_prompt_blocks()
    blocks_by_id = {str(b["id"]): PromptBlock.model_validate(b) for b in raw_blocks if "id" in b}
    matrices_to_explain = _assemble_matrices_to_explain(available_dtos, title_map, blocks_by_id)

    return HookResult(
        success=True,
        state_delta={
            "distilled_inputs": "\n\n".join(consolidated_distilled_parts),
            "historical_context": historical_context_text,
            "title_map": title_map,
            "matrices_to_explain": matrices_to_explain,
            "source_alias_map": alias_engine.alias_map,
            "output_profile_id": output_profile_id,
            "language": language,
            "alias_registry": alias_engine.alias_map,
            "max_extensions": p_dict.get("max_extension_items", 3),
        },
    )
