"""Matrix scoring and atom evaluation hook module."""

import logging
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, TypeAdapter, ValidationError

from backend_v2.core.hook_registry import (
    GlobalContextVarsDTO,
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.scoring.normalization_hook import recalculate
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PromptBlockAdapter,
)
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.enums import (
    ExecutionStatus,
    XaiExtensionType,
)
from backend_v2.models.v2_core import AtomResultDTO, ExecutionRecord, OutputProfile, Step, Workflow
from backend_v2.services.orchestrator.ast_evaluator import ASTEvaluator

logger = logging.getLogger(__name__)

__all__ = ["matrix_scoring_hook"]


@hook_registry.register(name="matrix_scoring_hook")
async def matrix_scoring_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Post-Hook to calculate Matrix scores from blind atom evaluations.

    Calculates final matrix scores based on the mathematical engine mapped to the
    workflow's execution output profile.

    Args:
        state: The execution state of the workflow step.
        deps: Dependency container with repositories.

    Returns:
        The hook execution result with state_delta containing computed matrix scores.

    Raises:
        AppException: With ErrorCodes.HOOK_EXECUTION_FAILED if dependencies fail.
        AppException: With ErrorCodes.VALIDATION_FAILED if inputs are not dictionaries.
        AppException: With ErrorCodes.RESOURCE_NOT_FOUND if step, execution, or workflow is missing.
        AppException: With ErrorCodes.CONFIGURATION_ERROR if prompt blocks lack valid scales.
    """
    logger.info("[ScoringHook] Running matrix_scoring_hook...")

    repository = deps.workflow_repo
    if not repository:
        msg = "Strict Fail-Fast Enforced: No repository provided in HookDependencies for matrix_scoring_hook."
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED.value})

    raw_inputs = state.inputs.dynamic_inputs if state.inputs.dynamic_inputs else state.inputs.raw_inputs

    blueprint_id = state.task_blueprint or state.step_id
    if not blueprint_id:
        msg = "Strict Fail-Fast Enforced: No blueprint_id or step_id provided to matrix_scoring_hook."
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    try:
        step_obj = await repository.get_step_by_id(blueprint_id)
        if not step_obj:
            msg = f"Strict Fail-Fast Enforced: Step blueprint '{blueprint_id}' not found in database."
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
            )

        try:
            step_model = Step.model_validate(step_obj)
            prompt_block_ids = step_model.criteria_block_ids
        except ValidationError as e:
            msg = f"Strict Fail-Fast Enforced: Step blueprint '{blueprint_id}' validation failed."
            logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
            ) from e

        # Determine if this step actually contains matrix blocks
        matrix_blocks = []
        for pb_id in prompt_block_ids:
            pb_data = await deps.prompt_block_repo.get_prompt_block_by_id(pb_id)
            if pb_data:
                try:
                    pb_model = PromptBlockAdapter.validate_python(pb_data, strict=False)
                    if isinstance(pb_model, MatrixPromptBlock):
                        matrix_blocks.append((pb_id, pb_model))
                except ValidationError as e:
                    msg = f"Strict Fail-Fast Enforced: PromptBlock '{pb_id}' validation failed."
                    logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                    ) from e

        # If no matrix blocks exist, then waterfall scoring natively skips without demanding evaluations
        if not matrix_blocks:
            logger.debug("[ScoringHook] Step '%s' contains no matrix blocks. Skipping waterfall scoring.", blueprint_id)
            return HookResult(success=True, state_delta=HookDeltaDTO())

        if not state.execution_id or not deps.exec_repo:
            msg = "Strict Fail-Fast Enforced: Missing execution_id or exec_repo in matrix_scoring_hook."
            raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        raw_exec_data = await deps.exec_repo.get_execution(state.execution_id)
        if not raw_exec_data:
            msg = f"Strict Fail-Fast Enforced: Execution {state.execution_id} missing from database."
            logger.error("[ScoringHook] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(
                message=msg, status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
            )

        execution_data = ExecutionRecord.model_validate(raw_exec_data, strict=False)

        raw_workflow = await repository.get_workflow_by_id(execution_data.workflow_id)
        if not raw_workflow:
            msg = f"Strict Fail-Fast Enforced: Workflow {execution_data.workflow_id} missing from database."
            logger.error("[ScoringHook] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(
                message=msg, status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
            )
        workflow = Workflow.model_validate(raw_workflow, strict=False)
        enable_contextual_overrides = workflow.enable_contextual_overrides

        # Dynamic Orchestration & Scoring Resolution
        strictness_level = None
        scoring_strategy = None
        visible_block_extensions = []
        locale = execution_data.target_locale

        profile_id = execution_data.output_profile_id
        if profile_id:
            profile_dict = await deps.output_profile_repo.get_output_profile_by_id(profile_id)
            if profile_dict:
                profile_model = OutputProfile.model_validate(profile_dict, strict=False)
                strictness_level = profile_model.strictness_level
                scoring_strategy = profile_model.scoring_strategy
                visible_block_extensions = profile_model.visible_block_extensions

        if strictness_level is None or scoring_strategy is None:
            msg = f"Strict Fail-Fast Enforced: Missing mandatory scoring configuration in profile '{profile_id}'."
            logger.error("[ScoringHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
            )

        content_payload = raw_inputs

        if "results" in content_payload:
            evaluations = content_payload["results"]
        else:
            msg = (
                f"Strict Fail-Fast Enforced: 'results' array is completely missing from state.inputs "
                f"for step '{blueprint_id}'. Upstream atomization payload failed."
            )
            logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        if not isinstance(evaluations, list):
            msg = f"Strict Fail-Fast Enforced: 'evaluations' array is not a list for step '{blueprint_id}'."
            logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        atom_mapping: dict[str, tuple[str, float, str, str, bool, bool]] = {}
        blocks_meta: dict[str, dict[str, Any]] = {}

        # 1. Reverse extraction of Atom Hashes
        for pb_id, pb_model in matrix_blocks:
            scales = pb_model.scales
            if not scales:
                msg = f"Strict Fail-Fast Enforced: PromptBlock '{pb_id}' has no scales."
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                )

            blocks_meta[pb_id] = {"scales": []}

            for scale in scales:
                s_val = float(scale.score)
                blocks_meta[pb_id]["scales"].append(s_val)
                claims = scale.claims
                for claim in claims:
                    tda_assertions = claim.tda_assertions
                    if tda_assertions:
                        for tda in tda_assertions:
                            aid = str(tda.tda_id)
                            atom_mapping[aid] = (
                                pb_id,
                                s_val,
                                tda.concept_description,
                                str(tda.aggregation_mode),
                                tda.inverse_evidence,
                                pb_model.allow_contextual_override,
                            )

            if not blocks_meta[pb_id]["scales"]:
                msg = f"PromptBlock '{pb_id}' scales array failed to provide numeric values for waterfall bounds."
                logger.error("[ScoringHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

            blocks_meta[pb_id]["math_min"] = min(blocks_meta[pb_id]["scales"])
            blocks_meta[pb_id]["math_max"] = max(blocks_meta[pb_id]["scales"])

        block_scale_stats: dict[str, dict[float, dict[str, int]]] = {}
        missing_atoms_by_block: dict[str, list[str]] = {}
        evaluated_atoms_by_block: dict[str, dict[str, ExecutionStatus]] = {}
        atom_quotes_by_block: dict[str, list[Any]] = {}
        matrix_extensions_by_block: dict[str, dict[str, list[str]]] = {}

        # 2. Iterate evaluations using whitelisted ASTEvaluator for 3-State Logic
        dlq_evals = 0
        infra_dlqs = 0
        total_evals = len(evaluations)
        for ev in evaluations:
            is_infra = False
            is_val = False
            try:
                ev_dto_check = AtomResultDTO.model_validate(ev) if not isinstance(ev, AtomResultDTO) else ev
                if str(ev_dto_check.status) == "DLQ" or ev_dto_check.status == ExecutionStatus.SYSTEM_ERROR:
                    is_val = True
            except ValidationError:
                # Check for infra DLQ envelope
                try:
                    ev_dict_check = TypeAdapter(dict[str, Any]).validate_python(ev)
                    if ev_dict_check.get("_dlq_status") == "FAILED/DLQ":
                        is_infra = True
                    elif str(ev_dict_check.get("status")) == "DLQ":
                        is_val = True
                except ValidationError:
                    pass

            if is_infra or is_val:
                dlq_evals += 1
            if is_infra:
                infra_dlqs += 1

        # Get merged facts dictionary from dynamic MergedFactsDTO context
        merged_facts_raw = content_payload["extracted_facts"] if "extracted_facts" in content_payload else {}
        try:
            merged_facts = (
                merged_facts_raw.model_dump(mode="json")
                if isinstance(merged_facts_raw, BaseModel)
                else TypeAdapter(dict[str, Any]).validate_python(merged_facts_raw)
            )
        except ValidationError as e:
            msg = f"Strict Fail-Fast Enforced: extracted_facts must be a dictionary or model: {e}"
            logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
            ) from e

        for pb_id, pb_model in matrix_blocks:
            scales = pb_model.scales or []
            block_scale_stats[pb_id] = {}
            missing_atoms_by_block[pb_id] = []
            evaluated_atoms_by_block[pb_id] = {}
            atom_quotes_by_block[pb_id] = []
            matrix_extensions_by_block[pb_id] = {}

            for scale in scales:
                s_val = float(scale.score)
                s_name = scale.name.resolve(locale) if scale.name else str(scale.score)
                block_scale_stats[pb_id][s_val] = {"hits": 0, "total": 0, "dlqs": 0}

                claims = scale.claims
                for claim in claims:
                    tda_assertions = claim.tda_assertions
                    if tda_assertions:
                        for tda in tda_assertions:
                            aid = tda.tda_id
                            text = tda.concept_description

                            # Determine evaluation track
                            final_state: Literal["TRUE", "FALSE", "DLQ"]
                            if tda.evaluation_track == "EXTRACTIVE_SENSOR" and tda.logical_expression:
                                # Deterministic AST boolean evaluation on merged facts with DLQ tolerance
                                ast_res = ASTEvaluator.evaluate(
                                    expression=tda.logical_expression,
                                    facts=merged_facts,
                                    total_chunks=total_evals or 1,
                                    dlq_chunks=dlq_evals,
                                )
                                final_state = ast_res
                            else:
                                # Fallback or cognitive track: look up chunk evaluations by atom_id
                                final_state = "FALSE"
                                for ev in evaluations:
                                    # Skip Infra-DLQ items to prevent ValidationErrors
                                    is_ev_infra_dlq = False
                                    try:
                                        ev_dict_tmp = (
                                            ev.model_dump(mode="json")
                                            if isinstance(ev, BaseModel)
                                            else TypeAdapter(dict[str, Any]).validate_python(ev)
                                        )
                                        is_ev_infra_dlq = ev_dict_tmp.get("_dlq_status") == "FAILED/DLQ"
                                    except ValidationError:
                                        pass

                                    if is_ev_infra_dlq:
                                        continue

                                    val_context = (
                                        state.global_context_vars.vars
                                        if isinstance(state.global_context_vars, GlobalContextVarsDTO)
                                        else (state.global_context_vars or {})
                                    )

                                    try:
                                        ev_dto = (
                                            ev
                                            if isinstance(ev, AtomResultDTO)
                                            else AtomResultDTO.model_validate(ev, strict=True, context=val_context)
                                        )
                                    except ValidationError as e:
                                        logger.error("[ScoringHook] Invalid AtomResultDTO: %s", e)
                                        raise AppException(
                                            message=f"Strict Fail-Fast: Invalid AtomResultDTO: {e}",
                                            status_code=500,
                                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                                        ) from e

                                    if ev_dto.tda_id == aid:
                                        if ev_dto.matrix_id is not None and ev_dto.matrix_id != pb_id:
                                            continue

                                        allow_override = atom_mapping[aid][5]
                                        effective_override = enable_contextual_overrides and allow_override

                                        status_str = ev_dto.status.name

                                        if status_str == "DLQ":
                                            final_state = "DLQ"
                                        elif status_str == "PASSED" and ev_dto.contextual_override:
                                            if effective_override:
                                                final_state = "TRUE"
                                            else:
                                                final_state = "FALSE"
                                        else:
                                            if status_str == "PASSED":
                                                is_satisfied = not tda.inverse_evidence
                                            elif status_str == "FAILED":
                                                is_satisfied = bool(tda.inverse_evidence)
                                            else:
                                                is_satisfied = False

                                            if (
                                                (not is_satisfied)
                                                and effective_override
                                                and ev_dto.contextual_override
                                                and status_str != "FAILED"
                                            ):
                                                is_satisfied = True

                                            final_state = "TRUE" if is_satisfied else "FALSE"

                                        if ev_dto.source_quote:
                                            eq_dto = QuoteEvidenceDTO.model_validate(
                                                {
                                                    "quote": ev_dto.source_quote,
                                                    "source_alias": [],
                                                },
                                                context=val_context,
                                            ).model_dump(mode="json")

                                            atom_quotes_by_block[pb_id].append(
                                                {
                                                    "level": s_val,
                                                    "level_name": s_name,
                                                    "quote": eq_dto,
                                                }
                                            )
                                        elif ev_dto.contextual_override and effective_override:
                                            loc = "Unknown location"
                                            rsn = (
                                                ev_dto.evaluation_reasoning
                                                if ev_dto.evaluation_reasoning
                                                else "No reasoning provided"
                                            )
                                            atom_quotes_by_block[pb_id].append(f"\U0001f4cd {loc}: {rsn}")

                                        extensions_dict = ev_dto.extensions
                                        if extensions_dict:
                                            allowed_exts = {
                                                e.value if isinstance(e, Enum) else str(e)
                                                for e in visible_block_extensions
                                            }
                                            for ext_k, ext_v in extensions_dict.items():
                                                ext_key_str = ext_k.value if isinstance(ext_k, Enum) else str(ext_k)
                                                if ext_key_str in allowed_exts and ext_v:
                                                    prefix = (
                                                        "\U0001f4a1"
                                                        if ext_key_str == "coaching"
                                                        else "\u26a0\ufe0f"
                                                        if ext_key_str == "falsification"
                                                        else "\U0001f6e0\ufe0f"
                                                    )
                                                    atom_quotes_by_block[pb_id].append(
                                                        f"{prefix} {ext_key_str.upper()}: {ext_v}"
                                                    )
                                                    if ext_key_str not in matrix_extensions_by_block[pb_id]:
                                                        matrix_extensions_by_block[pb_id][ext_key_str] = []
                                                    matrix_extensions_by_block[pb_id][ext_key_str].append(str(ext_v))

                                        break

                            # Record the logic outcomes
                            if final_state == "DLQ":
                                evaluated_atoms_by_block[pb_id][aid] = ExecutionStatus.SYSTEM_ERROR
                                block_scale_stats[pb_id][s_val]["total"] += 1
                                block_scale_stats[pb_id][s_val]["dlqs"] += 1
                                missing_atoms_by_block[pb_id].append(f"- {text} (DLQ - Unscorable)")
                            elif final_state == "TRUE":
                                evaluated_atoms_by_block[pb_id][aid] = ExecutionStatus.PASSED
                                block_scale_stats[pb_id][s_val]["total"] += 1
                                block_scale_stats[pb_id][s_val]["hits"] += 1
                            else:
                                evaluated_atoms_by_block[pb_id][aid] = ExecutionStatus.FAILED
                                block_scale_stats[pb_id][s_val]["total"] += 1
                                missing_atoms_by_block[pb_id].append(f"- {text}")

        # 3. Hybrid Calculation
        new_payload = content_payload.copy()

        if "atom_quotes" not in new_payload:
            new_payload["atom_quotes"] = {}
        for pb_id, quotes in atom_quotes_by_block.items():
            if quotes:
                new_payload["atom_quotes"][pb_id] = quotes

        # Inject dummy matrices so recalculate() can discover and compute them
        for pb_id, evaluated_atoms in evaluated_atoms_by_block.items():
            exts_for_block = matrix_extensions_by_block[pb_id] if pb_id in matrix_extensions_by_block else {}
            final_exts = {XaiExtensionType(k): "\n\n".join(v) for k, v in exts_for_block.items()}
            dummy = LightweightMatrixOutput(
                raw_score=0.0,
                normalized_score=None,
                level_breakdown=None,
                justification="[INITIALIZING]",
                evaluated_atoms=evaluated_atoms,
                extensions=final_exts,
            )
            new_payload[pb_id] = dummy.model_dump(mode="json", exclude_none=True)

            if pb_id in missing_atoms_by_block and missing_atoms_by_block[pb_id]:
                new_payload[f"{pb_id}_missing_context"] = "\n".join(missing_atoms_by_block[pb_id])

        # 4. Decoupled Hybrid Calculation
        await recalculate(
            payload=new_payload,
            profile_id=profile_id,
            deps=deps,
        )

        return HookResult(success=True, state_delta=HookDeltaDTO(delta=new_payload))

    except Exception as e:
        if isinstance(e, AppException):
            raise
        msg = f"Hybrid waterfall scoring failed for step '{blueprint_id}': {e}"
        logger.error("[ScoringHook] %s: %s", ErrorCodes.HOOK_EXECUTION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED.value},
        ) from e
