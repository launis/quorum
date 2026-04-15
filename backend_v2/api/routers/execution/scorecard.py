import json
import logging
from typing import Any

from fastapi import APIRouter, status

from backend_v2.api.dependencies import CurrentUserDep, ExecutionServiceDep, RepositoryDep
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.scorecard import MatrixScorecardRowDTO, ScorecardResponseDTO
from backend_v2.models.v2_core import ExecutionStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scorecard", tags=["Scorecard"])


def _find_matrices(data: dict[str, Any] | list[Any], results: dict[str, Any], prompt_blocks: dict[str, Any]) -> None:
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(k, str) and isinstance(v, (int, float)):
                # Ignore metadata keys
                if any(k.endswith(suffix) for suffix in ["_is_evaluative", "_scaled", "_normalized", "_atoms"]):
                    continue

                # Must exist in prompt_blocks to resolve names and max targets safely
                pb_meta = prompt_blocks.get(k)
                if pb_meta and pb_meta.get("category_id") == "matrix":
                    justification = data.get(f"{k}_justification", "Ei perusteluja saatavilla.")
                    missing = data.get(f"{k}_missing_context", "")
                    
                    t_atoms = data.get(f"{k}_total_atoms")
                    t_true = data.get(f"{k}_true_atoms")
                    t_false = data.get(f"{k}_false_atoms")
                    norm_val = data.get(f"{k}_normalized")
                    is_eval = data.get(f"{k}_is_evaluative", pb_meta.get("is_evaluative", True))
                    breakdown = data.get(f"{k}_level_breakdown")
                    
                    # One-sentence justification
                    short_reason = justification.split('\n')[0].strip()
                    if '.' in short_reason:
                        short_reason = short_reason.split('.')[0] + "."

                    results[k] = {
                        "score": v,
                        "just": short_reason,
                        "missing": missing,
                        "normalized": norm_val,
                        "total_atoms": t_atoms,
                        "true_atoms": t_true,
                        "false_atoms": t_false,
                        "level_breakdown": breakdown,
                        "is_eval": is_eval,
                        "pb_meta": pb_meta
                    }
            elif isinstance(v, (dict, list)):
                _find_matrices(v, results, prompt_blocks)
    elif isinstance(data, list):
        for item in data:
            _find_matrices(item, results, prompt_blocks)


@router.get("/{execution_id}", response_model=ScorecardResponseDTO, status_code=status.HTTP_200_OK)
async def get_diagnostic_scorecard(
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
    repository: RepositoryDep,
) -> ScorecardResponseDTO:
    """Epic 24: Fetch an independent Diagnostic Scorecard directly from frozen evaluation trace."""
    execution = await execution_service.get_execution(initiator=current_user, execution_id=execution_id)

    if not execution.execution_trace_storage_path:
        raise AppException(
            message="Execution trace not available. The execution may not have completed successfully or trace is lost.",
            status_code=404,
            details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
        )
        
    try:
        from backend_v2.services.storage import get_storage_driver
        storage = get_storage_driver()
        raw_bytes = await storage.read(execution.execution_trace_storage_path)
        trace_data = json.loads(raw_bytes)
    except Exception as e:
        logger.error("[ScorecardRouter] Failed to load execution trace for %s", execution_id, exc_info=True)
        raise AppException(
            message="Failed to load execution trace.",
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
        ) from e

    # Harvest PromptBlocks for resolution safely
    workflow_dict = await repository.get_workflow_by_id(execution.workflow_id)
    if not workflow_dict:
        raise AppException(
            message="Workflow metadata missing. Cannot hydrate scorecard.",
            status_code=500,
            details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
        )

    all_blocks = {}
    steps = workflow_dict.get("steps", [])
    for step in steps:
        step_task = step.get("task_blueprint")
        # Optimization: cache the fetch since we might reuse them. But this is an isolated API call.
        if step_task:
            step_obj = await repository.get_step_by_id(step_task)
            if step_obj:
                pb_ids = step_obj.get("prompt_blocks", [])
                for pb_id in pb_ids:
                    if pb_id not in all_blocks:
                        pb_dict = await repository.get_prompt_block_by_id(pb_id)
                        if pb_dict:
                            all_blocks[pb_id] = pb_dict

    found_matrices: dict[str, Any] = {}
    _find_matrices(trace_data, found_matrices, all_blocks)

    eval_matrices: list[MatrixScorecardRowDTO] = []
    info_matrices: list[MatrixScorecardRowDTO] = []
    global_scores: list[float] = []

    for block_id, data in found_matrices.items():
        pb_meta = data["pb_meta"]
        
        label_obj = pb_meta.get("label", {})
        translations = label_obj.get("translations", {})
        fi_name = translations.get("fi", block_id)
        en_name = translations.get("en", block_id)
        
        scale_max = None
        scales = pb_meta.get("scales", [])
        if scales:
            valid_scores = [float(s.get("score", 0)) for s in scales]
            if valid_scores:
                scale_max = max(valid_scores)

        row = MatrixScorecardRowDTO(
            block_id=block_id,
            label_fi=fi_name,
            label_en=en_name,
            score=data["score"],
            scale_max=scale_max,
            normalized_score=data["normalized"],
            true_atoms=data["true_atoms"],
            total_atoms=data["total_atoms"],
            justification=data["just"],
            missing_context=data["missing"],
            level_breakdown=data["level_breakdown"],
            is_evaluative=data["is_eval"]
        )

        if data["is_eval"]:
            eval_matrices.append(row)
            if data["normalized"] is not None:
                global_scores.append(data["normalized"])
        else:
            info_matrices.append(row)

    global_avg = None
    if global_scores:
        global_avg = round(sum(global_scores) / len(global_scores), 2)

    return ScorecardResponseDTO(
        execution_id=execution_id,
        workflow_id=execution.workflow_id,
        global_average=global_avg,
        evaluative_matrices=eval_matrices,
        informational_matrices=info_matrices
    )
