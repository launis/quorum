"""Execution Resumption Service for validating and resuming failed executions."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from backend_v2.database.interfaces import IExecutionRepository, IWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.usage_service import UsageService

logger = logging.getLogger(__name__)

__all__ = ["ExecutionResumptionService"]


class ExecutionResumptionService:
    """Service evaluating execution resumability and resuming failed DAG executions."""

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        workflow_repo: IWorkflowRepository,
        usage_service: UsageService | None = None,
        get_execution_fn: Callable[..., Awaitable[ExecutionRecord]] | None = None,
        check_resumability_fn: Callable[..., Awaitable[bool]] | None = None,
    ) -> None:
        """Initialize the execution resumption service.

        Args:
            exec_repo: Repository providing access to execution records.
            workflow_repo: Repository providing access to workflow blueprints.
            usage_service: Optional service for evaluating organization quotas.
            get_execution_fn: Optional callable overriding execution fetching.
            check_resumability_fn: Optional callable overriding resumability check.
        """
        self.exec_repo = exec_repo
        self.workflow_repo = workflow_repo
        self.usage_service = usage_service
        self._get_execution = get_execution_fn or self._default_get_execution
        self._check_resumability = check_resumability_fn

    async def _default_get_execution(self, initiator: TokenData, execution_id: str) -> ExecutionRecord:
        record = await self.exec_repo.get_execution(execution_id, hydrate=True)
        if not record:
            raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)
        org_id = initiator.organization_id
        if initiator.role != "ROOT" and record.organization_id != org_id and record.created_by != initiator.id:
            raise PermissionDeniedError("You do not have permission to access this execution.")
        return record

    async def check_resumability(self, record: ExecutionRecord) -> bool:
        """Evaluates whether an execution record can be resumed based on strict invariants.

        Rules for is_resumable = True:
        1. Execution status must be FAILED.
        2. DAG workflow blueprint exists, step IDs match step_states, and version hasn't drifted.
        3. Tenant organization has sufficient FinOps quota.
        """
        if record.status != ExecutionStatus.FAILED:
            return False

        workflow_dict = await self.workflow_repo.get_workflow_by_id(record.workflow_id)
        if not workflow_dict:
            return False

        workflow = Workflow.model_validate(workflow_dict)
        workflow_step_ids = {step.id for step in workflow.steps}
        if not workflow_step_ids.issubset(record.step_states.keys()):
            return False

        orig_version: int | None = None
        if isinstance(record.metadata, ExecutionMetadata):
            orig_version = record.metadata.workflow_version
        elif record.workflow_version is not None:
            orig_version = record.workflow_version
        if orig_version is not None and workflow.version != orig_version:
            return False

        org_id = record.organization_id
        if org_id and self.usage_service is not None:
            is_quota_safe = await self.usage_service.check_quota(org_id)
            if not is_quota_safe:
                return False

        return True

    async def resume_execution(self, initiator: TokenData, execution_id: str, arq_pool: Any) -> ExecutionRecord:
        """Securely resume an existing FAILED execution."""
        record = await self._get_execution(initiator, execution_id)

        evaluator = self._check_resumability or self.check_resumability
        is_resumable = await evaluator(record)
        if not is_resumable:
            msg = (
                f"Execution {execution_id} cannot be resumed due to unresumable state, "
                "missing checkpoint history, workflow blueprint drift, or insufficient quota."
            )
            logger.error("[ExecutionResumptionService] %s: %s", ErrorCodes.UNRESUMABLE_STATE_ERROR.name, msg)
            raise AppException(
                message=msg, status_code=400, details={"error_code": ErrorCodes.UNRESUMABLE_STATE_ERROR.value}
            )

        org_id = initiator.organization_id
        if org_id and self.usage_service is not None:
            is_quota_safe = await self.usage_service.check_quota(org_id)
            if not is_quota_safe:
                msg = f"Organization '{org_id}' has exceeded its execution quota. Resumption blocked."
                logger.warning("[ExecutionResumptionService] Circuit Breaker Tripped: %s", msg)
                raise AppException(
                    message=msg,
                    status_code=402,
                    details={"error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value},
                )

        record = record.model_copy(update={"status": ExecutionStatus.RUNNING})
        await self.exec_repo.update_execution(execution_id, ExecutionUpdateDTO(status=ExecutionStatus.RUNNING))

        await arq_pool.enqueue_job(
            "execute_workflow_job",
            workflow_id=record.workflow_id,
            inputs=record.raw_inputs.model_dump(mode="json"),
            execution_id=execution_id,
            organization_id=initiator.organization_id,
            user_id=initiator.id,
        )

        return record
