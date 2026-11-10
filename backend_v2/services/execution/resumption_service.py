"""Execution Resumption Service for validating and resuming failed executions."""

from __future__ import annotations

import inspect
import logging
from collections.abc import Awaitable, Callable

from arq import ArqRedis

from backend_v2.database.interfaces import IExecutionRepository, IPromptBlockRepository, IWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.orchestrator.dag_executor.workflow_bootstrap_stage import (
    _fetch_referenced_prompt_blocks,
    invalidate_drifted_passed_steps,
)
from backend_v2.services.usage_service import UsageService

logger = logging.getLogger(__name__)

__all__ = ["ExecutionResumptionService"]


class ExecutionResumptionService:
    """Service evaluating execution resumability and resuming failed DAG executions.

    Attributes:
        exec_repo: Repository providing access to execution records.
        workflow_repo: Repository providing access to workflow blueprints.
        usage_service: Optional service for evaluating organization quotas.
        prompt_block_repo: Optional repository providing access to prompt blocks.
    """

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        workflow_repo: IWorkflowRepository,
        usage_service: UsageService | None = None,
        get_execution_fn: Callable[..., Awaitable[ExecutionRecord]] | None = None,
        check_resumability_fn: Callable[..., Awaitable[bool]] | None = None,
        prompt_block_repo: IPromptBlockRepository | None = None,
    ) -> None:
        """Initialize the execution resumption service.

        Args:
            exec_repo: Repository providing access to execution records.
            workflow_repo: Repository providing access to workflow blueprints.
            usage_service: Optional service for evaluating organization quotas.
            get_execution_fn: Optional callable overriding execution fetching.
            check_resumability_fn: Optional callable overriding resumability check.
            prompt_block_repo: Optional repository providing access to prompt blocks.
        """
        self.exec_repo = exec_repo
        self.workflow_repo = workflow_repo
        self.usage_service = usage_service
        self.prompt_block_repo = prompt_block_repo
        self._get_execution = get_execution_fn if get_execution_fn is not None else self._default_get_execution
        self._check_resumability = check_resumability_fn

    async def _default_get_execution(self, initiator: TokenData, execution_id: str) -> ExecutionRecord:
        """Fetch and authorize an execution record using default tenant isolation rules.

        Args:
            initiator: Authenticated user token claims.
            execution_id: Canonical Opaque Stripe ID of the target execution.

        Returns:
            Hydrated and authorized ExecutionRecord domain model.

        Raises:
            ResourceNotFoundError: If the execution record does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If the initiator lacks permission to access the execution
                (ErrorCodes.PERMISSION_DENIED).
        """
        record = await self.exec_repo.get_execution(execution_id, hydrate=True)
        if not record:
            logger.error(
                "[ExecutionResumptionService] %s: Execution '%s' not found",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                execution_id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "execution_id": execution_id},
            )
            raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)
        org_id = initiator.organization_id
        if initiator.role != "ROOT" and record.organization_id != org_id and record.created_by != initiator.id:
            logger.error(
                "[ExecutionResumptionService] %s: User '%s' denied access to execution '%s'",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                execution_id,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value, "execution_id": execution_id},
            )
            raise PermissionDeniedError("You do not have permission to access this execution.")
        return record

    async def check_resumability(self, record: ExecutionRecord) -> bool:
        """Evaluate whether an execution record can be resumed based on strict invariants.

        Rules for is_resumable = True:
        1. Execution status must be FAILED.
        2. DAG workflow blueprint exists, step IDs match step_states, and version has not drifted.
        3. Tenant organization has sufficient FinOps quota.

        Args:
            record: Execution record domain model to evaluate.

        Returns:
            True if all resumability invariants are satisfied, False otherwise.
        """
        if record.status != ExecutionStatus.FAILED:
            return False

        workflow = await self.workflow_repo.get_workflow_by_id(record.workflow_id)
        if workflow is None:
            return False

        workflow_step_ids = {step.id for step in workflow.steps}
        if not workflow_step_ids.issubset(record.step_states.keys()):
            return False

        orig_version = record.metadata.workflow_version if record.metadata is not None else record.workflow_version
        if workflow.version != orig_version:
            return False

        return await self._is_organization_quota_safe(record.organization_id)

    async def _is_organization_quota_safe(self, org_id: str | None) -> bool:
        """Evaluate whether the given organization is within its execution quota.

        Args:
            org_id: Canonical Opaque Stripe ID of the organization, or None.

        Returns:
            True if no quota limit is violated or usage evaluation is disabled, False otherwise.
        """
        if org_id and self.usage_service is not None:
            return await self.usage_service.check_quota(org_id)
        return True

    async def _invalidate_drifted_steps(self, record: ExecutionRecord) -> ExecutionRecord:
        """Invalidate previously passed steps whose Merkle input hashes have drifted.

        Args:
            record: Execution record domain model to inspect and update.

        Returns:
            Updated ExecutionRecord with drifted passed steps invalidated.
        """
        wf_res = self.workflow_repo.get_workflow_by_id(record.workflow_id)
        workflow = await wf_res if inspect.isawaitable(wf_res) else wf_res
        if not isinstance(workflow, Workflow):
            return record

        step_definitions: dict[str, Step] = {}
        for step_rule in workflow.steps:
            if step_rule.task_blueprint:
                step_res = self.workflow_repo.get_step_by_id(step_rule.task_blueprint)
                step_data = await step_res if inspect.isawaitable(step_res) else step_res
                if isinstance(step_data, Step):
                    step_definitions[step_rule.task_blueprint] = step_data
        pb_repo = self.prompt_block_repo if self.prompt_block_repo is not None else self.workflow_repo
        blocks_by_id = await _fetch_referenced_prompt_blocks(step_definitions, pb_repo)
        return invalidate_drifted_passed_steps(record, workflow, step_definitions, blocks_by_id)

    async def resume_execution(self, initiator: TokenData, execution_id: str, arq_pool: ArqRedis) -> ExecutionRecord:
        """Securely resume an existing FAILED execution and enqueue its background worker job.

        Args:
            initiator: Authenticated user token claims.
            execution_id: Canonical Opaque Stripe ID of the target execution.
            arq_pool: Redis worker connection pool for job dispatching.

        Returns:
            Updated ExecutionRecord domain model transitioned to RUNNING status.

        Raises:
            ResourceNotFoundError: If the execution record does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If the initiator lacks access to the execution (ErrorCodes.PERMISSION_DENIED).
            AppException: If the execution state is unresumable (ErrorCodes.UNRESUMABLE_STATE_ERROR) or
                organization quota is exceeded (ErrorCodes.RATE_LIMIT_EXCEEDED).
        """
        record = await self._get_execution(initiator, execution_id)

        evaluator = self._check_resumability if self._check_resumability is not None else self.check_resumability
        is_resumable = await evaluator(record)
        if not is_resumable:
            msg = (
                f"Execution {execution_id} cannot be resumed due to unresumable state, "
                "missing checkpoint history, workflow blueprint drift, or insufficient quota."
            )
            logger.error(
                "[ExecutionResumptionService] %s: %s",
                ErrorCodes.UNRESUMABLE_STATE_ERROR.name,
                msg,
                extra={"error_code": ErrorCodes.UNRESUMABLE_STATE_ERROR.value, "execution_id": execution_id},
            )
            raise AppException(
                message=msg, status_code=400, details={"error_code": ErrorCodes.UNRESUMABLE_STATE_ERROR.value}
            )

        org_id = initiator.organization_id
        if not await self._is_organization_quota_safe(org_id):
            msg = f"Organization '{org_id}' has exceeded its execution quota. Resumption blocked."
            logger.error(
                "[ExecutionResumptionService] Circuit Breaker Tripped: %s",
                msg,
                extra={"error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value, "organization_id": org_id},
            )
            raise AppException(
                message=msg,
                status_code=402,
                details={"error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value},
            )

        record = await self._invalidate_drifted_steps(record)

        record = record.model_copy(update={"status": ExecutionStatus.RUNNING})
        await self.exec_repo.update_execution(
            execution_id,
            ExecutionUpdateDTO(
                status=ExecutionStatus.RUNNING,
                steps=record.steps,
                step_states=record.step_states,
            ),
        )

        await arq_pool.enqueue_job(
            "execute_workflow_job",
            workflow_id=record.workflow_id,
            inputs=record.raw_inputs.model_dump(mode="json"),
            execution_id=execution_id,
            organization_id=initiator.organization_id,
            user_id=initiator.id,
        )

        return record
