"""Execution Management Service."""

from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import BackgroundTasks

from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData
from backend_v2.models.v2_core import ExecutionCreate, ExecutionRecord, ExecutionStatus, FrozenContext, Workflow
from backend_v2.services.orchestrator.dag_executor import DAGExecutor

logger = logging.getLogger(__name__)

class ExecutionService:
    """Domain Service for Orchestration Executions enforcing Tenant Isolation and Authorization."""

    def __init__(self, repo: AbstractWorkflowRepository, executor: DAGExecutor):
        self.repo = repo
        self.executor = executor

    async def list_executions(self, initiator: TokenData) -> list[ExecutionRecord]:
        """Fetch executions securely based on Tenant/Role."""
        try:
            executions = await self.repo.get_all_executions()

            # SSOT MANDATE: Tenant Isolation Check
            if initiator.role != "ROOT":
                org_id = getattr(initiator, "organization_id", None)
                # Filtering logic to only show executions that belong to this organization or user
                # Currently simple filtering, will evolve as data schema strictly bounds executions to orgs
                executions = [e for e in executions if e.get("organization_id") == org_id or e.get("created_by") == initiator.uid]

            return [ExecutionRecord.model_validate(x) for x in executions]
        except Exception as e:
            logger.error(f"[ExecutionService] Failed to list executions: {e}")
            raise AppException(
                message=f"Failed to list executions: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
            ) from e

    async def get_execution(self, initiator: TokenData, execution_id: str) -> ExecutionRecord:
        """Fetch single execution securely."""
        data = await self.repo.get_execution(execution_id)
        if not data:
             logger.error(f"[ExecutionService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: Execution {execution_id} not found.")
             raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)

        # SSOT MANDATE: Tenant Isolation Check
        org_id = getattr(initiator, "organization_id", None)
        if initiator.role != "ROOT" and data.get("organization_id") != org_id and data.get("created_by") != initiator.uid:
            logger.error(f"[ExecutionService] {ErrorCodes.UNAUTHORIZED.name}: User {initiator.uid} attempted to access foreign execution {execution_id}.")
            raise PermissionDeniedError("You do not have permission to view this execution.")

        return ExecutionRecord.model_validate(data)

    async def start_execution(self, initiator: TokenData, payload: ExecutionCreate, background_tasks: BackgroundTasks) -> ExecutionRecord:
        """Initialize and trigger workflow securely."""
        workflow_dict = await self.repo.get_workflow_by_id(payload.workflow_id)
        if not workflow_dict:
            logger.error(f"[ExecutionService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: Workflow {payload.workflow_id} not found.")
            raise ResourceNotFoundError(resource_type="workflow", resource_id=payload.workflow_id)

        workflow = Workflow.model_validate(workflow_dict)

        # Auth Check
        org_id = getattr(initiator, "organization_id", None)
        if initiator.role != "ROOT" and workflow.organization_id not in [org_id, "system", None]:
            logger.error(f"[ExecutionService] PERMISSION_DENIED: {initiator.uid} tried to start foreign workflow.")
            raise PermissionDeniedError("You do not have permission to execute this workflow.")

        execution_id = str(uuid4())
        initial_record = ExecutionRecord(
            id=execution_id,
            workflow_id=workflow.id,
            status=ExecutionStatus.PENDING,
            raw_inputs=payload.raw_inputs,
            frozen_context=FrozenContext(),
            results={},
        )
        # We append temporary creator tracking using model_dump bypass for now
        dump = initial_record.model_dump(mode="json")
        dump["created_by"] = initiator.uid
        dump["organization_id"] = getattr(initiator, "organization_id", None)

        await self.repo.create_execution(dump)

        # Fire Async Process
        background_tasks.add_task(
            self.executor.execute_workflow,
            execution_id=execution_id,
            workflow=workflow,
            raw_inputs=payload.raw_inputs
        )

        return initial_record
