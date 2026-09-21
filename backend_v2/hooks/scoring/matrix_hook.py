"""Matrix scoring and atom evaluation hook module."""

from __future__ import annotations

import json
import logging
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError

from backend_v2.core.hook_registry import (
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PromptBlockAdapter,
)
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_result import AtomResultDTO, EvaluationFactsDTO
from backend_v2.models.dtos.hook_delta import MatrixHookResultDTO
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO, LightweightMatrixOutput
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.enums import (
    ExecutionStatus,
    LaxXaiExtensionType,
    XaiExtensionType,
)
from backend_v2.services.orchestrator.ast_evaluator import ASTEvaluator
from backend_v2.utils.scoring import get_scoring_engine

logger = logging.getLogger(__name__)

__all__ = ["AtomScoringRuleDTO", "BlockMetaDTO", "matrix_scoring_hook"]


class BlockMetaDTO(BaseModel):
    """Metadata and extrema bounds for PromptBlock scoring scales.

    Attributes:
        scales: List of numeric score thresholds.
        math_min: Absolute minimum scale value.
        math_max: Absolute maximum scale value.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    scales: list[float]
    math_min: float
    math_max: float


class AtomScoringRuleDTO(BaseModel):
    """Encapsulates matrix scoring criteria and attribution rules for a single TDA atom.

    Attributes:
        block_id: Prompt block identifier.
        scale_value: Numeric score scale target.
        concept_description: Description of evaluated assertion concept.
        aggregation_mode: Logic aggregation mode.
        is_inverse_assertion: Whether the assertion represents inverse evidence.
        allow_contextual_override: Whether contextual override is permitted.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    block_id: str
    scale_value: float
    concept_description: str
    aggregation_mode: str
    is_inverse_assertion: bool
    allow_contextual_override: bool


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
        logger.error("[ScoringHook] %s: %s", ErrorCodes.HOOK_EXECUTION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED.value})

    raw_inputs = state.inputs.dynamic_inputs if state.inputs.dynamic_inputs else state.inputs.raw_inputs

    blueprint_id = state.task_blueprint or state.step_id
    if not blueprint_id:
        msg = "Strict Fail-Fast Enforced: No blueprint_id or step_id provided to matrix_scoring_hook."
        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    try:
        step_obj = await repository.get_step_by_id(blueprint_id)
        if not step_obj:
            msg = f"Strict Fail-Fast Enforced: Step blueprint '{blueprint_id}' not found in database."
            logger.error("[ScoringHook] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
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
            return HookResult(success=True, state_delta=HookDeltaDTO(delta={}))

        if not state.execution_id or not deps.exec_repo:
            msg = "Strict Fail-Fast Enforced: Missing execution_id or exec_repo in matrix_scoring_hook."
            logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
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

        # Dynamic Orchestration & Scoring Resolution (Phase 1, Step 1: Anti-Duct-Tape)
        strictness_level = workflow.default_strictness_level
        visible_block_extensions = []

        profile_id = execution_data.output_profile_id
        if profile_id:
            profile_dict = await deps.output_profile_repo.get_output_profile_by_id(profile_id)
            if not profile_dict:
                msg = f"Strict Fail-Fast Enforced: Missing mandatory output profile '{profile_id}'."
                logger.error("[ScoringHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                )
            profile_model = OutputProfile.model_validate(profile_dict, strict=False)
            visible_block_extensions = profile_model.visible_block_extensions

        if strictness_level is None:
            wf_id = execution_data.workflow_id
            msg = f"Strict Fail-Fast Enforced: Missing mandatory scoring configuration in workflow '{wf_id}'."
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

        atom_mapping: dict[str, AtomScoringRuleDTO] = {}
        blocks_meta: dict[str, BlockMetaDTO] = {}

        # 1. Reverse extraction of Atom Hashes
        for pb_id, pb_model in matrix_blocks:
            scales = pb_model.scales
            if not scales:
                msg = f"Strict Fail-Fast Enforced: PromptBlock '{pb_id}' has no scales."
                logger.error("[ScoringHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                )

            scales_list: list[float] = []

            for scale in scales:
                s_val = float(scale.score)
                scales_list.append(s_val)
                claims = scale.claims
                for claim in claims:
                    tda_assertions = claim.tda_assertions
                    if tda_assertions:
                        for tda in tda_assertions:
                            aid = str(tda.tda_id)
                            atom_mapping[aid] = AtomScoringRuleDTO(
                                block_id=pb_id,
                                scale_value=s_val,
                                concept_description=tda.concept_description,
                                aggregation_mode=str(tda.aggregation_mode),
                                is_inverse_assertion=bool(tda.inverse_evidence),
                                allow_contextual_override=bool(pb_model.allow_contextual_override),
                            )

            if not scales_list:
                msg = f"PromptBlock '{pb_id}' scales array failed to provide numeric values for waterfall bounds."
                logger.error("[ScoringHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

            blocks_meta[pb_id] = BlockMetaDTO(
                scales=scales_list,
                math_min=min(scales_list),
                math_max=max(scales_list),
            )

        block_scale_stats: dict[str, dict[float, LevelStatsDTO]] = {}
        missing_atoms_by_block: dict[str, list[str]] = {}
        evaluated_atoms_by_block: dict[str, dict[str, ExecutionStatus]] = {}
        atom_quotes_by_block: dict[str, list[QuoteEvidenceDTO]] = {}
        matrix_extensions_by_block: dict[str, dict[str, list[str]]] = {}

        # 2. Iterate evaluations using whitelisted ASTEvaluator for 3-State Logic
        dlq_evals = 0
        infra_dlqs = 0
        total_evals = len(evaluations)
        validated_evaluations: list[AtomResultDTO] = []
        for ev in evaluations:
            if isinstance(ev, AtomResultDTO):
                ev_dto = ev
            elif isinstance(ev, BaseModel):
                ev_dto = AtomResultDTO.model_validate(ev.model_dump())
            else:
                try:
                    ev_dto = AtomResultDTO.model_validate(ev)
                except (ValidationError, TypeError, ValueError) as err:
                    msg = f"Strict Fail-Fast Enforced: Evaluation item malformed: {err}"
                    logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                    ) from err

            validated_evaluations.append(ev_dto)
            if ev_dto.status in (ExecutionStatus.SYSTEM_ERROR, "DLQ"):
                dlq_evals += 1
                infra_dlqs += 1

        # Get merged facts dictionary from dynamic EvaluationFactsDTO context
        merged_facts: dict[str, bool | str] = {}
        if "extracted_facts" in content_payload:
            facts_val = content_payload["extracted_facts"]
            if isinstance(facts_val, EvaluationFactsDTO):
                merged_facts = facts_val.facts
            elif isinstance(facts_val, BaseModel):
                merged_facts = EvaluationFactsDTO.model_validate({"facts": facts_val.model_dump()}).facts
            elif isinstance(facts_val, str):
                try:
                    parsed = json.loads(facts_val)
                    merged_facts = EvaluationFactsDTO.model_validate({"facts": parsed}).facts
                except (json.JSONDecodeError, ValueError, ValidationError) as err:
                    msg = f"Strict Fail-Fast Enforced: extracted_facts must be a dictionary (invalid JSON: {facts_val})"
                    logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                    ) from err
            else:
                try:
                    merged_facts = EvaluationFactsDTO.model_validate({"facts": facts_val}).facts
                except (ValidationError, TypeError, ValueError) as err:
                    msg = f"Strict Fail-Fast Enforced: extracted_facts must be a dictionary or model: {facts_val}"
                    logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                    ) from err

        for pb_id, pb_model in matrix_blocks:
            scales = pb_model.scales
            block_scale_stats[pb_id] = {}
            missing_atoms_by_block[pb_id] = []
            evaluated_atoms_by_block[pb_id] = {}
            atom_quotes_by_block[pb_id] = []
            matrix_extensions_by_block[pb_id] = {}

            for scale in scales:
                s_val = float(scale.score)
                block_scale_stats[pb_id][s_val] = LevelStatsDTO(hits=0, total=0, dlqs=0)

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
                                    total_chunks=max(1, total_evals),
                                    dlq_chunks=dlq_evals,
                                )
                                final_state = ast_res
                            else:
                                # Fallback or cognitive track: look up chunk evaluations by atom_id
                                final_state = "FALSE"
                                for ev_dto in validated_evaluations:
                                    if ev_dto.tda_id == aid:
                                        if ev_dto.matrix_id is not None and ev_dto.matrix_id != pb_id:
                                            continue

                                        rule = atom_mapping[aid]
                                        allow_override = rule.allow_contextual_override
                                        effective_override = enable_contextual_overrides and allow_override
                                        is_inverse = ev_dto.is_inverse_evidence or rule.is_inverse_assertion

                                        status_str = ev_dto.status.name

                                        if status_str == "DLQ" or ev_dto.status == ExecutionStatus.SYSTEM_ERROR:
                                            final_state = "DLQ"
                                        elif status_str == "PASSED" or ev_dto.status == ExecutionStatus.PASSED:
                                            if is_inverse:
                                                final_state = "TRUE"
                                            elif ev_dto.contextual_override:
                                                final_state = "TRUE" if effective_override else "FALSE"
                                            else:
                                                final_state = "TRUE"
                                        else:
                                            if (
                                                not is_inverse
                                                and effective_override
                                                and ev_dto.contextual_override
                                                and status_str != "FAILED"
                                                and ev_dto.status != ExecutionStatus.FAILED
                                            ):
                                                final_state = "TRUE"
                                            else:
                                                final_state = "FALSE"

                                        if ev_dto.source_quote:
                                            eq_dto = QuoteEvidenceDTO(
                                                quote=ev_dto.source_quote,
                                                verified_source_ids=[],
                                            )
                                            atom_quotes_by_block[pb_id].append(eq_dto)
                                        elif (ev_dto.contextual_override and effective_override) or (
                                            is_inverse
                                            and (status_str == "PASSED" or ev_dto.status == ExecutionStatus.PASSED)
                                        ):
                                            loc = "Unknown location"
                                            rsn = "No reasoning provided"
                                            if (
                                                ev_dto.evaluation_reasoning is not None
                                                and ev_dto.evaluation_reasoning.strip()
                                            ):
                                                rsn = ev_dto.evaluation_reasoning
                                            atom_quotes_by_block[pb_id].append(
                                                QuoteEvidenceDTO(
                                                    quote=f"[OVERRIDE] {loc}: {rsn}",
                                                    verified_source_ids=[],
                                                )
                                            )

                                        extensions_dict = ev_dto.extensions
                                        if extensions_dict:
                                            visible_ext_set = {
                                                e.value if isinstance(e, Enum) else str(e)
                                                for e in visible_block_extensions
                                            }
                                            for ext_k, ext_v in extensions_dict.items():
                                                ext_key_str = ext_k.value if isinstance(ext_k, Enum) else str(ext_k)
                                                if ext_key_str in visible_ext_set and ext_v:
                                                    atom_quotes_by_block[pb_id].append(
                                                        QuoteEvidenceDTO(
                                                            quote=f"[{ext_key_str.upper()}]: {ext_v}",
                                                            verified_source_ids=[],
                                                        )
                                                    )
                                                    if ext_key_str not in matrix_extensions_by_block[pb_id]:
                                                        matrix_extensions_by_block[pb_id][ext_key_str] = []
                                                    matrix_extensions_by_block[pb_id][ext_key_str].append(str(ext_v))

                                        break

                            # Record the logic outcomes
                            cur_stat = block_scale_stats[pb_id][s_val]
                            if final_state == "DLQ":
                                evaluated_atoms_by_block[pb_id][aid] = ExecutionStatus.SYSTEM_ERROR
                                block_scale_stats[pb_id][s_val] = cur_stat.model_copy(
                                    update={"total": cur_stat.total + 1, "dlqs": cur_stat.dlqs + 1}
                                )
                                missing_atoms_by_block[pb_id].append(f"{text} (DLQ - Unscorable)")
                            elif final_state == "TRUE":
                                evaluated_atoms_by_block[pb_id][aid] = ExecutionStatus.PASSED
                                block_scale_stats[pb_id][s_val] = cur_stat.model_copy(
                                    update={"total": cur_stat.total + 1, "hits": cur_stat.hits + 1}
                                )
                            else:
                                evaluated_atoms_by_block[pb_id][aid] = ExecutionStatus.FAILED
                                block_scale_stats[pb_id][s_val] = cur_stat.model_copy(
                                    update={"total": cur_stat.total + 1}
                                )
                                missing_atoms_by_block[pb_id].append(text)

        # 3. Calculation via UnifiedScoringEngine
        matrix_outputs: dict[str, LightweightMatrixOutput] = {}
        missing_contexts: dict[str, str] = {}
        atom_quotes: dict[str, list[QuoteEvidenceDTO]] = {}

        for pb_id, pb_model in matrix_blocks:
            raw_stats = block_scale_stats[pb_id]
            scale_values = [float(s.score) for s in pb_model.scales]
            math_min = min(scale_values)
            math_max = max(scale_values)

            global_total = sum(d.total for d in raw_stats.values())
            global_dlqs = sum(d.dlqs for d in raw_stats.values())

            is_indeterminate = global_total > 0 and (global_dlqs / global_total) > 0.10

            if is_indeterminate:
                raw_score = math_min
                formatted_breakdown = None
                xai_log = None
                justification = (
                    f"[INDETERMINATE] Matrix score invalidated because the DLQ ratio "
                    f"({global_dlqs / global_total:.2%}) exceeded the 10.00% threshold."
                )
            else:
                engine = get_scoring_engine()
                stats = {float(k): v for k, v in raw_stats.items()}
                scoring_result = engine.calculate(
                    stats=stats,
                    math_min=math_min,
                    math_max=math_max,
                    strictness_level=strictness_level,
                )
                raw_score = scoring_result.score
                xai_log = scoring_result.xai_log
                formatted_breakdown = scoring_result.breakdown
                justification = "Calculated via UnifiedScoringEngine."

            block_allowed_extensions: list[LaxXaiExtensionType] | None = None
            if pb_model.output_extensions:
                block_allowed_extensions = []
                for ext_str in pb_model.output_extensions:
                    try:
                        block_allowed_extensions.append(LaxXaiExtensionType(ext_str))
                    except ValueError as e:
                        msg = f"Strict Fail-Fast Enforced: Unsupported LaxXaiExtensionType '{ext_str}' in '{pb_id}'"
                        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                        raise AppException(
                            message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                        ) from e

            final_exts = {
                XaiExtensionType(k): "\n\n".join(v)
                for k, v in matrix_extensions_by_block[pb_id].items()
                if k in {e.value for e in XaiExtensionType}
            }

            matrix_output = LightweightMatrixOutput(
                raw_score=raw_score,
                normalized_score=None,
                level_breakdown=formatted_breakdown,
                justification=justification,
                xai_log=xai_log,
                evaluated_atoms=evaluated_atoms_by_block[pb_id],
                extensions=final_exts,
                allowed_extensions=block_allowed_extensions,
            )
            matrix_outputs[pb_id] = matrix_output

            if missing_atoms_by_block[pb_id]:
                missing_contexts[pb_id] = "\n".join(missing_atoms_by_block[pb_id])

            if atom_quotes_by_block[pb_id]:
                atom_quotes[pb_id] = atom_quotes_by_block[pb_id]

        matrix_hook_result = MatrixHookResultDTO(
            matrix_outputs=matrix_outputs,
            missing_contexts=missing_contexts,
            atom_quotes=atom_quotes,
        )

        return HookResult(success=True, state_delta=HookDeltaDTO(delta=matrix_hook_result))

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
