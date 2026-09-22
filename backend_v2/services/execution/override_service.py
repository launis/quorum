"""Execution Override Service for human modifications and evidence rejections."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone

from backend_v2.core.hook_registry import HookDependencies
from backend_v2.database.interfaces import (
    IComponentRepository,
    IExecutionRepository,
    IIdentityRepository,
    IOutputProfileRepository,
    IPromptBlockRepository,
    ISystemRepository,
    IWorkflowRepository,
)
from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.hooks import scoring
from backend_v2.models.auth import TokenData
from backend_v2.models.domain.execution import EvaluatedMatrixContextDTO, ExecutionRecord
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.context_variables import ContextVariableValue
from backend_v2.models.dtos.matrix_scorecard import HumanOverrideDTO, HumanOverrideRequest
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.state import EvidenceOverrideDTO, TraceEvent
from backend_v2.services import storage
from backend_v2.services.file_driver import FileDriver

logger = logging.getLogger(__name__)

__all__ = ["ExecutionOverrideService"]


class ExecutionOverrideService:
    """Service managing human overrides, evidence quote rejection, and synthesis invalidation."""

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        workflow_repo: IWorkflowRepository,
        comp_repo: IComponentRepository | None = None,
        prompt_block_repo: IPromptBlockRepository | None = None,
        output_profile_repo: IOutputProfileRepository | None = None,
        identity_repo: IIdentityRepository | None = None,
        system_repo: ISystemRepository | None = None,
        storage_driver: FileDriver | None = None,
        get_execution_fn: Callable[..., Awaitable[ExecutionRecord]] | None = None,
    ) -> None:
        """Initialize ExecutionOverrideService with required repositories and dependencies.

        Args:
            exec_repo: Repository for execution records.
            workflow_repo: Repository for workflows.
            comp_repo: Optional repository for components.
            prompt_block_repo: Optional repository for prompt blocks.
            output_profile_repo: Optional repository for output profiles.
            identity_repo: Optional repository for identities.
            system_repo: Optional repository for system configuration.
            storage_driver: Optional file storage driver.
            get_execution_fn: Optional callable to retrieve an execution record.
        """
        self.exec_repo, self.workflow_repo, self.comp_repo = exec_repo, workflow_repo, comp_repo
        self.prompt_block_repo, self.output_profile_repo = prompt_block_repo, output_profile_repo
        self.identity_repo, self.system_repo = identity_repo, system_repo
        self.storage: FileDriver = storage_driver if storage_driver is not None else storage.get_storage_driver()
        self._get_execution = get_execution_fn or self._default_get_execution

    async def _default_get_execution(self, initiator: TokenData, execution_id: str) -> ExecutionRecord:
        record = await self.exec_repo.get_execution(execution_id, hydrate=True)
        if not record:
            raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)
        if (
            initiator.role != "ROOT"
            and record.organization_id != initiator.organization_id
            and record.created_by != initiator.id
        ):
            raise PermissionDeniedError("You do not have permission to access this execution.")
        return record

    async def clear_profile_synthesis(self, initiator: TokenData, execution_id: str, profile_id: str) -> None:
        """Removes the synthesized data for a specific profile to force re-render via LLM Hook."""
        execution_rec = await self._get_execution(initiator=initiator, execution_id=execution_id)

        if execution_rec.profile_syntheses and profile_id in execution_rec.profile_syntheses:
            new_syntheses = dict(execution_rec.profile_syntheses)
            del new_syntheses[profile_id]
            execution_rec = execution_rec.model_copy(update={"profile_syntheses": new_syntheses})

        workflow_data = await self.workflow_repo.get_workflow_by_id(execution_rec.workflow_id)
        if not workflow_data:
            raise ResourceNotFoundError(resource_type="workflow", resource_id=execution_rec.workflow_id)

        workflow_obj = Workflow.model_validate(workflow_data)
        default_pid = workflow_obj.default_profile_id
        target_pdf_path = execution_rec.pdf_report_path

        if profile_id == default_pid and execution_rec.pdf_report_path:
            try:
                await self.storage.delete(execution_rec.pdf_report_path)
            except AppException as e:
                if e.status_code == 404:
                    logger.warning(
                        "[ExecutionOverrideService] Old PDF blob %s not found, ignoring.", execution_rec.pdf_report_path
                    )
                elif e.status_code == 409:
                    raise e
                else:
                    raise AppException(
                        message="Failed to delete old PDF blob",
                        status_code=500,
                        details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                    ) from e
            except Exception as e:
                raise AppException(
                    message="Failed to delete old PDF blob",
                    status_code=500,
                    details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                ) from e

            target_pdf_path = None

        await self.exec_repo.update_execution(
            execution_id,
            ExecutionUpdateDTO(
                profile_syntheses=execution_rec.profile_syntheses,
                pdf_report_path=target_pdf_path,
                updated_at=datetime.now(timezone.utc),
            ),
        )
        logger.info(
            "[ExecutionOverrideService] Cleared profile synthesis",
            extra={"execution_id": execution_id, "profile_id": profile_id},
        )

    async def override_atom(
        self,
        initiator: TokenData,
        execution_id: str,
        atom_id: str,
        payload: HumanOverrideRequest,
    ) -> None:
        """Apply a human override to a specific ScorecardAtomDTO."""
        record = await self._get_execution(initiator, execution_id)
        if (
            initiator.role != "ROOT"
            and record.organization_id != initiator.organization_id
            and record.created_by != initiator.id
        ):
            raise PermissionDeniedError("You do not have permission to modify this execution.")

        found_step_id = None
        for step_id, state in record.step_states.items():
            if atom_id in state.scorecard_atoms:
                found_step_id = step_id
                break

        if not found_step_id:
            msg = f"Atom '{atom_id}' not found in any step_states"
            logger.error("[ExecutionOverrideService] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(
                message=msg, status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
            )

        override_dto = HumanOverrideDTO(
            new_status=payload.new_status,
            reason=payload.reason,
            evidence_quotes=payload.evidence_quotes,
            overridden_by=initiator.id,
            overridden_at=datetime.now(timezone.utc),
        )

        updated_atoms = dict(record.step_states[found_step_id].scorecard_atoms)
        updated_atoms[atom_id] = updated_atoms[atom_id].model_copy(update={"human_override": override_dto})

        new_step_states = dict(record.step_states)
        new_step_states[found_step_id] = new_step_states[found_step_id].model_copy(
            update={"scorecard_atoms": updated_atoms}
        )
        record = record.model_copy(update={"step_states": new_step_states})

        cv_updates: dict[str, ContextVariableValue] = {}
        for k, v in record.context_variables.variables.items():
            if isinstance(v, EvaluatedMatrixContextDTO):
                matrix_ctx = v
                if atom_id in matrix_ctx.evaluated_atoms:
                    new_evaluated_atoms = dict(matrix_ctx.evaluated_atoms)
                    new_evaluated_atoms[atom_id] = payload.new_status
                    updated_raw_atoms = [
                        ra.model_copy(update={"human_override": payload.new_status})
                        if (ra.tda_id == atom_id or ra.atom_id == atom_id)
                        else ra
                        for ra in matrix_ctx.raw_atoms
                    ]
                    cv_updates[k] = matrix_ctx.model_copy(
                        update={"evaluated_atoms": new_evaluated_atoms, "raw_atoms": updated_raw_atoms}
                    )
        if cv_updates:
            updated_context_vars = record.context_variables.with_update(**cv_updates)
            record = record.model_copy(update={"context_variables": updated_context_vars})

        if (
            self.comp_repo is None
            or self.prompt_block_repo is None
            or self.output_profile_repo is None
            or self.identity_repo is None
            or self.system_repo is None
        ):
            raise AppException(
                message="Repositories required for override hook dependencies are missing",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        deps = HookDependencies(
            exec_repo=self.exec_repo,
            workflow_repo=self.workflow_repo,
            comp_repo=self.comp_repo,
            prompt_block_repo=self.prompt_block_repo,
            output_profile_repo=self.output_profile_repo,
            identity_repo=self.identity_repo,
            audit_repo=None,
            system_repo=self.system_repo,
        )
        recalculated_vars = await scoring.recalculate(record.context_variables, record.active_profile_id, deps)
        record = record.model_copy(update={"context_variables": recalculated_vars})
        await self.exec_repo.update_execution(
            execution_id, ExecutionUpdateDTO(step_states=record.step_states, context_variables=record.context_variables)
        )
        event = TraceEvent(
            step_name="manual_override",
            event_type="evidence_override",
            content={"atom_id": atom_id, "override": override_dto.model_dump(mode="json")},
        )
        await self.exec_repo.append_trace_event(execution_id, event)

    async def reject_evidence_quote(self, initiator: TokenData, execution_id: str, evq_id: str, reason: str) -> None:
        """Reject an evidence quote and append the event to the execution trace."""
        record = await self._get_execution(initiator, execution_id)
        if (
            initiator.role != "ROOT"
            and record.organization_id != initiator.organization_id
            and record.created_by != initiator.id
        ):
            raise PermissionDeniedError("You do not have permission to modify this execution.")

        dto = EvidenceOverrideDTO(
            evq_id=evq_id,
            user_rejected=True,
            rejection_reason=reason,
            rejected_by=initiator.id,
            rejected_at=datetime.now(timezone.utc),
        )
        event = TraceEvent(
            step_name="manual_override", event_type="evidence_override", content=dto.model_dump(mode="json")
        )
        await self.exec_repo.append_trace_event(execution_id, event)
