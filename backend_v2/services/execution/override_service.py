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
from backend_v2.models.dtos.context_variables import ContextVariablesDTO, ContextVariableValue
from backend_v2.models.dtos.matrix_scorecard import HumanOverrideDTO, HumanOverrideRequest
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.state import EvidenceOverrideDTO, TraceEvent
from backend_v2.services import storage
from backend_v2.services.file_driver import FileDriver

logger = logging.getLogger(__name__)

__all__ = ["ExecutionOverrideService"]


class ExecutionOverrideService:
    """Service managing human overrides, evidence quote rejection, and synthesis invalidation.

    Attributes:
        exec_repo: Repository for execution records.
        workflow_repo: Repository for workflow blueprints.
        comp_repo: Optional repository for workflow components.
        prompt_block_repo: Optional repository for prompt blocks.
        output_profile_repo: Optional repository for output profiles.
        identity_repo: Optional repository for user and organization identities.
        system_repo: Optional repository for system configuration.
        storage: File storage driver for report artifact blobs.
    """

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
        """Fetch an execution record by ID and enforce tenant access permissions.

        Args:
            initiator: Authenticated user token data.
            execution_id: Canonical Opaque Stripe ID of the target execution.

        Returns:
            Hydrated ExecutionRecord domain model.

        Raises:
            ResourceNotFoundError: If the execution record does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If the initiator lacks permission to access the execution
                (ErrorCodes.PERMISSION_DENIED).
        """
        record = await self.exec_repo.get_execution(execution_id, hydrate=True)
        if not record:
            logger.error(
                "[ExecutionOverrideService] %s: Execution '%s' not found",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                execution_id,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
            raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)
        if (
            initiator.role != "ROOT"
            and record.organization_id != initiator.organization_id
            and record.created_by != initiator.id
        ):
            logger.error(
                "[ExecutionOverrideService] %s: User '%s' denied access to execution '%s'",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                execution_id,
                exc_info=True,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )
            raise PermissionDeniedError("You do not have permission to access this execution.")
        return record

    async def clear_profile_synthesis(self, initiator: TokenData, execution_id: str, profile_id: str) -> None:
        """Remove synthesized data for a specific profile to force re-render via LLM Hook.

        Args:
            initiator: Authenticated user token data.
            execution_id: Canonical Opaque Stripe ID of the target execution.
            profile_id: Canonical Opaque Stripe ID of the output profile to clear.

        Raises:
            ResourceNotFoundError: If the execution or workflow does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If the initiator lacks access to the execution (ErrorCodes.PERMISSION_DENIED).
            AppException: If deleting the old PDF report blob fails with a conflict or storage error
                (ErrorCodes.INTERNAL_SERVER_ERROR).
        """
        execution_rec = await self._get_execution(initiator=initiator, execution_id=execution_id)

        if execution_rec.profile_syntheses and profile_id in execution_rec.profile_syntheses:
            new_syntheses = {k: v for k, v in execution_rec.profile_syntheses.items() if k != profile_id}
            execution_rec = execution_rec.model_copy(update={"profile_syntheses": new_syntheses})

        workflow_obj = await self.workflow_repo.get_workflow_by_id(execution_rec.workflow_id)
        if not workflow_obj:
            logger.error(
                "[ExecutionOverrideService] %s: Workflow '%s' not found",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                execution_rec.workflow_id,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
            raise ResourceNotFoundError(resource_type="workflow", resource_id=execution_rec.workflow_id)

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
                    logger.error(
                        "[ExecutionOverrideService] Conflict deleting PDF blob %s",
                        execution_rec.pdf_report_path,
                        exc_info=True,
                    )
                    raise e
                else:
                    logger.error(
                        "[ExecutionOverrideService] %s: Failed to delete old PDF blob %s",
                        ErrorCodes.INTERNAL_SERVER_ERROR.name,
                        execution_rec.pdf_report_path,
                        exc_info=True,
                        extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                    )
                    raise AppException(
                        message="Failed to delete old PDF blob",
                        status_code=500,
                        details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                    ) from e
            except Exception as e:
                logger.error(
                    "[ExecutionOverrideService] %s: Unexpected error deleting old PDF blob %s",
                    ErrorCodes.INTERNAL_SERVER_ERROR.name,
                    execution_rec.pdf_report_path,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                )
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

    def _apply_atom_override_to_record(
        self,
        record: ExecutionRecord,
        found_step_id: str,
        atom_id: str,
        payload: HumanOverrideRequest,
        override_dto: HumanOverrideDTO,
    ) -> ExecutionRecord:
        """Apply human override to step_states and evaluated matrix context variables on the record.

        Args:
            record: Target execution record to update.
            found_step_id: Step state key containing the target atom.
            atom_id: Identifier of the atom being overridden.
            payload: Incoming human override request payload.
            override_dto: Constructed HumanOverrideDTO to attach to the atom.

        Returns:
            Updated ExecutionRecord with modified step_states and context_variables.
        """
        target_state = record.step_states[found_step_id]
        updated_atoms = {
            **target_state.scorecard_atoms,
            atom_id: target_state.scorecard_atoms[atom_id].model_copy(update={"human_override": override_dto}),
        }
        new_step_states = {
            **record.step_states,
            found_step_id: target_state.model_copy(update={"scorecard_atoms": updated_atoms}),
        }
        record = record.model_copy(update={"step_states": new_step_states})

        cv_updates: dict[str, ContextVariableValue] = {}
        for k, v in record.context_variables.variables.items():
            if isinstance(v, EvaluatedMatrixContextDTO) and atom_id in v.evaluated_atoms:
                new_evaluated_atoms = {**v.evaluated_atoms, atom_id: payload.new_status}
                updated_raw_atoms = [
                    ra.model_copy(update={"human_override": payload.new_status})
                    if (ra.tda_id == atom_id or ra.atom_id == atom_id)
                    else ra
                    for ra in v.raw_atoms
                ]
                cv_updates[k] = v.model_copy(
                    update={"evaluated_atoms": new_evaluated_atoms, "raw_atoms": updated_raw_atoms}
                )
        if cv_updates:
            updated_context_vars = record.context_variables.with_update(**cv_updates)
            record = record.model_copy(update={"context_variables": updated_context_vars})
        return record

    async def _recalculate_scores(self, record: ExecutionRecord) -> ContextVariablesDTO:
        """Validate hook repository dependencies and recalculate matrix scores.

        Args:
            record: Execution record containing updated context variables.

        Returns:
            Recalculated ContextVariablesDTO from the scoring hook.

        Raises:
            AppException: If required repositories for hook dependencies are missing
                (ErrorCodes.CONFIGURATION_ERROR).
        """
        if (
            self.comp_repo is None
            or self.prompt_block_repo is None
            or self.output_profile_repo is None
            or self.identity_repo is None
            or self.system_repo is None
        ):
            msg = "Repositories required for override hook dependencies are missing"
            logger.error(
                "[ExecutionOverrideService] %s: %s",
                ErrorCodes.CONFIGURATION_ERROR.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
            raise AppException(
                message=msg,
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
        return await scoring.recalculate(record.context_variables, record.active_profile_id, deps)

    async def override_atom(
        self,
        initiator: TokenData,
        execution_id: str,
        atom_id: str,
        payload: HumanOverrideRequest,
    ) -> None:
        """Apply a human override to a specific ScorecardAtomDTO and recalculate scores.

        Args:
            initiator: Authenticated user token data.
            execution_id: Canonical Opaque Stripe ID of the target execution.
            atom_id: Target atom identifier to override.
            payload: Human override verdict, reason, and evidence quotes.

        Raises:
            ResourceNotFoundError: If the execution record does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If the initiator lacks permission to modify the execution
                (ErrorCodes.PERMISSION_DENIED).
            AppException: If the target atom is not found in any step state (ErrorCodes.RESOURCE_NOT_FOUND)
                or required hook repositories are missing (ErrorCodes.CONFIGURATION_ERROR).
        """
        record = await self._get_execution(initiator, execution_id)
        if (
            initiator.role != "ROOT"
            and record.organization_id != initiator.organization_id
            and record.created_by != initiator.id
        ):
            logger.error(
                "[ExecutionOverrideService] %s: User '%s' denied modification of execution '%s'",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                execution_id,
                exc_info=True,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )
            raise PermissionDeniedError("You do not have permission to modify this execution.")

        found_step_id = next(
            (step_id for step_id, state in record.step_states.items() if atom_id in state.scorecard_atoms),
            None,
        )
        if not found_step_id:
            msg = f"Atom '{atom_id}' not found in any step_states"
            logger.error(
                "[ExecutionOverrideService] %s: %s",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
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
        record = self._apply_atom_override_to_record(record, found_step_id, atom_id, payload, override_dto)
        recalculated_vars = await self._recalculate_scores(record)
        record = record.model_copy(update={"context_variables": recalculated_vars})

        await self.exec_repo.update_execution(
            execution_id, ExecutionUpdateDTO(step_states=record.step_states, context_variables=record.context_variables)
        )
        event = TraceEvent(
            step_name="manual_override",
            event_type="evidence_override",
            content={"atom_id": atom_id, "override": override_dto.model_dump(mode="json", exclude_none=True)},
        )
        await self.exec_repo.append_trace_event(execution_id, event)

    async def reject_evidence_quote(self, initiator: TokenData, execution_id: str, evq_id: str, reason: str) -> None:
        """Reject an evidence quote and append the event to the execution trace.

        Args:
            initiator: Authenticated user token data.
            execution_id: Canonical Opaque Stripe ID of the target execution.
            evq_id: Opaque evidence quote identifier to reject.
            reason: User-provided reason for rejecting the evidence quote.

        Raises:
            ResourceNotFoundError: If the execution record does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If the initiator lacks permission to modify the execution
                (ErrorCodes.PERMISSION_DENIED).
        """
        record = await self._get_execution(initiator, execution_id)
        if (
            initiator.role != "ROOT"
            and record.organization_id != initiator.organization_id
            and record.created_by != initiator.id
        ):
            logger.error(
                "[ExecutionOverrideService] %s: User '%s' denied quote rejection on execution '%s'",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                execution_id,
                exc_info=True,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )
            raise PermissionDeniedError("You do not have permission to modify this execution.")

        dto = EvidenceOverrideDTO(
            evq_id=evq_id,
            user_rejected=True,
            rejection_reason=reason,
            rejected_by=initiator.id,
            rejected_at=datetime.now(timezone.utc),
        )
        event = TraceEvent(
            step_name="manual_override",
            event_type="evidence_override",
            content=dto.model_dump(mode="json", exclude_none=True),
        )
        await self.exec_repo.append_trace_event(execution_id, event)
