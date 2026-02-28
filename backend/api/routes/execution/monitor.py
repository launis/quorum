"""API Router for Execution Monitoring (GET and SSE)."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, status
from sse_starlette.sse import EventSourceResponse

from backend.api.bff_transformer import AssessmentTransformer
from backend.database.repository import AbstractWorkflowRepository
from backend.dependencies import get_async_repository
from backend.exceptions import AppException, ResourceNotFoundError
from backend.services.auth import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/executions", tags=["Executions"])


from backend.models.domain.execution import ExecutionRecord
from backend.models.dtos.execution import ExecutionResponse


@router.get("/recent", summary="Get Recent Executions", response_model=list[ExecutionResponse])
async def get_recent_executions(
    limit: int = 10,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: Any = Depends(AuthService.get_current_user()),
):
    """Get a list of recent executions."""
    try:
        user_id = current_user.id if current_user else None
        executions = await repository.get_all_executions(user_id=user_id)

        def get_time(e: ExecutionRecord):
            return e.created_at or e.started_at or ""

        executions.sort(key=get_time, reverse=True)

        results = []
        for e in executions[:limit]:
            # Use DTO to normalize
            try:
                # e is ExecutionRecord
                dto = ExecutionResponse.model_validate(e)
                results.append(dto)
            except Exception as validation_err:
                logger.warning(f"Skipping malformed execution in recent list: {validation_err}")
                continue

        return results

    except Exception as e:
        error_code = "EXECUTION_FETCH_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message="Failed to fetch recent executions",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code},
        ) from e


@router.get("/{execution_id}", summary="Get Execution Details", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: Any = Depends(AuthService.get_current_user()),
):
    """Get execution details by ID. Returns standardized ExecutionResponse."""
    try:
        execution = await repository.get_execution(execution_id)

        if not execution:
            raise ResourceNotFoundError(f"Execution '{execution_id}' not found.")

        # Normalize via DTO
        return ExecutionResponse.model_validate(execution)

    except ResourceNotFoundError as e:
        raise AppException(
            message=str(e), status_code=status.HTTP_404_NOT_FOUND, details={"error_code": "EXECUTION_NOT_FOUND"}
        ) from e
    except AppException:
        raise
    except Exception as e:
        error_code = "EXECUTION_FETCH_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code}
        ) from e


@router.get("/{execution_id}/events", summary="Monitor Execution (SSE)")
async def monitor_execution(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    view: str = "assessment",  # 'assessment' or 'raw'
    accept_language: Annotated[str | None, Header()] = "en",
):
    """Server-Sent Events alias for monitoring."""
    try:
        logger.info(f"[Monitor] Request for execution_id: {execution_id}, view: {view}")

        # Pre-check existence to fail fast with 404
        exists = await repository.get_execution(execution_id)
        if not exists:
            logger.warning(f"[Monitor] Execution {execution_id} NOT FOUND in repository.")
            raise ResourceNotFoundError(
                f"Execution '{execution_id}' not found.", details={"error_code": "EXECUTION_NOT_FOUND"}
            )

        # Fetch Workflow Definition (Strict SSOT)
        workflow_id = exists.workflow_id
        if not workflow_id and exists.results and isinstance(exists.results, dict):
            # Fallback if not in top-level but in results
            workflow_id = exists.results.get("workflow_id")

        workflow_definition = None
        if workflow_id:
            workflow_definition = await repository.get_workflow_definition(workflow_id)

        # Map step names out-of-band to prevent UI UUIDs
        step_names_map: dict[str, str] = {}
        step_slugs_map: dict[str, str] = {}
        if workflow_definition:
            steps_list = getattr(workflow_definition, "steps", [])
            if not steps_list and isinstance(workflow_definition, dict):
                steps_list = workflow_definition.get("steps", [])
            logger.info(f"[Monitor] workflow_definition steps: {steps_list}")
            
            for sid in steps_list:
                if isinstance(sid, str):
                    try:
                        step_doc = await repository.get_step_by_id(sid)
                        if not step_doc:
                            # Fallback: Is the step directly referring to a Component ID?
                            step_doc = await repository.get_component_by_id(sid)
                            
                        if step_doc:
                            # step_doc is generic dict. Extract 'name' (human readable)
                            # or 'slug' (fallback, e.g. 'step_analyst')
                            name = step_doc.get("name") or step_doc.get("slug")
                            if name:
                                step_names_map[sid] = name
                                
                            task_key = step_doc.get("task_key") or step_doc.get("component")
                            if task_key:
                                step_slugs_map[sid] = task_key
                    except Exception as e:
                        logger.warning(f"[Monitor] Failed to fetch step {sid} for mapping: {e}")
            logger.info(f"[Monitor] Resolved step_names_map: {step_names_map}")
            logger.info(f"[Monitor] Resolved step_slugs_map: {step_slugs_map}")

        import asyncio

        async def event_generator():
            last_payload = None
            # Simple polling simulator for now to satisfy contract without Redis
            try:
                # Poll more frequently for smoother UI updates (1s is fine for local)
                for _i in range(120):  # Increased to 2 min timeout
                    try:
                        exec_data = await repository.get_execution(execution_id)
                    except Exception as e:
                        # TinyDB Local Storage Workaround (Concurrent Read/Write Corruption)
                        # JSONDecodeError usually drops here as 'Extra data' when Arq worker writes
                        if "Extra data" in str(e) or "Expecting value" in str(e):
                            logger.warning(f"[Monitor] Transient JSON read error in local DB, retrying... ({e})")
                            await asyncio.sleep(0.5)
                            continue
                        else:
                            logger.error(f"[Monitor] Execution fetch failed: {e}")
                            yield {"event": "error", "data": "Database error while watching execution."}
                            break

                    if not exec_data:
                        yield {"event": "error", "data": "Execution not found"}
                        break

                    current_status = exec_data.status
                    payload = ""

                    # Dump to dict for Transformers compatibility
                    exec_dict = exec_data.model_dump()

                    if view == "raw":
                        # Option B: Explicit DTO Layer
                        # Normalize data using Pydantic Schema
                        try:
                            dto = ExecutionResponse.model_validate(exec_data)
                            payload = dto.model_dump_json(warnings=False)
                        except Exception as validation_err:
                            logger.error(f"[Monitor] DTO Validation Failed: {validation_err}")
                            # Fallback to rough dump if validation fails to keep stream alive?
                            # No, user requested NO fallbacks. But we should probably send error event.
                            yield {"event": "error", "data": f"Serialization Error: {validation_err}"}
                            break
                    else:
                        # Default: AssessmentTransformer for BFF (Frontend Compatibility)
                        try:
                            transformer = AssessmentTransformer(language=accept_language or "en")
                            assessment_view = transformer.transform(
                                exec_dict, workflow_definition, step_names=step_names_map, step_slugs=step_slugs_map
                            )
                            payload = assessment_view.model_dump_json()
                        except Exception as trans_err:
                            logger.error(f"[Monitor] Transformation Failed: {trans_err}", exc_info=True)
                            yield {"event": "error", "data": "Transformation Failed"}
                            break

                    if payload != last_payload:
                        logger.info(f"[Monitor] Yielding update for {execution_id}. Status: {current_status}. Payload len: {len(payload)}")
                        last_payload = payload
                        yield {"event": "update", "data": payload}

                    if current_status in ("completed", "failed", "cancelled", "rejected"):
                        logger.info(f"[Monitor] Execution {execution_id} finished ({current_status}). Closing stream.")
                        break

                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"[Monitor] Critical Generator Error: {e}", exc_info=True)
                yield {"event": "error", "data": str(e)}

        return EventSourceResponse(event_generator())

    except ResourceNotFoundError as e:
        raise AppException(
            message=str(e), status_code=status.HTTP_404_NOT_FOUND, details={"error_code": "EXECUTION_NOT_FOUND"}
        ) from e
    except Exception as e:
        logger.error(f"[Monitor] SSE Init Error: {e}", exc_info=True)
        raise AppException(str(e), 500) from e
