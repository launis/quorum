"""Blueprint Transformer Service for Server-Driven UI report compilation."""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from backend_v2.database.interfaces import (
    IComponentRepository,
    IExecutionRepository,
    IIdentityRepository,
    IOutputProfileRepository,
    IPromptBlockRepository,
    ISystemRepository,
    IWorkflowRepository,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import User
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock, PromptBlockAdapter
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.domain.system_config import AllowedMCPTool, MCPAuditTrace, SystemConfigMCPGateways
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.causal_discovery import CausalGraphPayloadDTO, CausalTdaFusionResultDTO
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.dtos.step_output import StepOutputDTO
from backend_v2.models.dtos.trace import StepTraceMetadataDTO, TraceEventMetadataEnvelope, TraceScoringPayloadDTO
from backend_v2.models.enums import (
    ExecutionStatus,
    TargetBlockType,
    VirtualSystemStepID,
)
from backend_v2.models.state import EvidenceOverrideDTO, StateProjector
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    SduiCausalGraphBlock,
    SduiMatrixTableBlock,
    SduiRadarChartBlock,
)
from backend_v2.services.matrix_parser import MatrixDomainParser
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.executive_summary_adapter import ExecutiveSummaryAdapter
from backend_v2.services.sdui.adapters.global_score_adapter import GlobalScoreAdapter
from backend_v2.services.sdui.adapters.matrix_graphs_adapter import MatrixGraphsAdapter
from backend_v2.services.sdui.adapters.matrix_summary_table_adapter import MatrixSummaryTableAdapter
from backend_v2.services.sdui.adapters.mcp_audit_adapter import McpAuditAdapter
from backend_v2.services.sdui.adapters.metadata_adapter import MetadataAdapter
from backend_v2.services.sdui.adapters.penalties_adapter import PenaltiesAdapter
from backend_v2.services.sdui.adapters.printable_sources_adapter import PrintableSourcesAdapter
from backend_v2.services.sdui.adapters.synthesis_text_adapter import SynthesisTextAdapter
from backend_v2.services.sdui.adapters.variance_adapter import VarianceAdapter
from backend_v2.services.sdui.adapters.warning_card_adapter import WarningCardAdapter
from backend_v2.services.sdui.adapters.xai_highlights_adapter import XaiHighlightsAdapter
from backend_v2.services.sdui.sanitizers import McpPresentationSanitizer

logger = logging.getLogger(__name__)

__all__ = ["BlueprintTransformer"]

_MCP_GATEWAY_ADAPTER: TypeAdapter[SystemConfigMCPGateways] = TypeAdapter(SystemConfigMCPGateways)
_SCORING_PAYLOAD_ADAPTER: TypeAdapter[TraceScoringPayloadDTO] = TypeAdapter(TraceScoringPayloadDTO)
_EVIDENCE_OVERRIDE_ADAPTER: TypeAdapter[EvidenceOverrideDTO] = TypeAdapter(EvidenceOverrideDTO)
_ATOM_RESULTS_ADAPTER: TypeAdapter[list[AtomResultDTO]] = TypeAdapter(list[AtomResultDTO])
_CAUSAL_RESULT_ADAPTER: TypeAdapter[CausalTdaFusionResultDTO | CausalGraphPayloadDTO] = TypeAdapter(
    CausalTdaFusionResultDTO | CausalGraphPayloadDTO
)
_USER_ADAPTER: TypeAdapter[User] = TypeAdapter(User)

_SUPPORTED_PENALTY_CODES: frozenset[str] = frozenset({"PENALTY_SECURITY", "PENALTY_POST_HOC", "PENALTY_PASSIVITY"})
_CAUSAL_BLOCK_IDS: frozenset[str] = frozenset({"fusion", "graph"})


class _HydratedReferencesEnvelope(V2CoreBase):
    """Boundary envelope validating hydrated atom reference mappings from folded step outputs."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    hydrated_references: Annotated[dict[str, HydratedAtomDTO], Field(default_factory=dict)]


class BlueprintTransformer:
    """Transforms persisted execution results and synthesis caches into ReportDataDTO.

    Attributes:
        exec_repo: Repository protocol for execution records.
        workflow_repo: Repository protocol for workflow definitions.
        comp_repo: Repository protocol for generic components.
        prompt_block_repo: Repository protocol for prompt block definitions.
        output_profile_repo: Repository protocol for output profile definitions.
        identity_repo: Repository protocol for user and organization identities.
        system_repo: Repository protocol for system configurations and MCP gateways.
        last_evaluative_matrices: Evaluative scorecard rows computed in the latest build.
        last_all_matrices: Complete parsed scorecard rows computed in the latest build.
    """

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        workflow_repo: IWorkflowRepository,
        comp_repo: IComponentRepository,
        prompt_block_repo: IPromptBlockRepository,
        output_profile_repo: IOutputProfileRepository,
        identity_repo: IIdentityRepository,
        system_repo: ISystemRepository,
    ) -> None:
        """Initialize BlueprintTransformer with required repository protocols.

        Args:
            exec_repo: Repository for execution data.
            workflow_repo: Repository for workflow definitions.
            comp_repo: Repository for component definitions.
            prompt_block_repo: Repository for prompt block definitions.
            output_profile_repo: Repository for output profile definitions.
            identity_repo: Repository for identity management.
            system_repo: Repository for system configurations.
        """
        self.exec_repo = exec_repo
        self.workflow_repo = workflow_repo
        self.comp_repo = comp_repo
        self.prompt_block_repo = prompt_block_repo
        self.output_profile_repo = output_profile_repo
        self.identity_repo = identity_repo
        self.system_repo = system_repo
        self.last_evaluative_matrices: list[MatrixScorecardRowDTO] = []
        self.last_all_matrices: list[MatrixScorecardRowDTO] = []

        self._target_block_hydrators: dict[TargetBlockType, Callable[[AdapterContext], list[AnySduiBlock]]] = {
            TargetBlockType.PENALTIES_BLOCK: PenaltiesAdapter.build,
            TargetBlockType.GLOBAL_SCORE_BLOCK: GlobalScoreAdapter.build,
            TargetBlockType.AUDIT_TRAIL_BLOCK: McpAuditAdapter.build,
            TargetBlockType.PRINTABLE_SOURCES_BLOCK: PrintableSourcesAdapter.build,
            TargetBlockType.GROUPED_EXTENSIONS_BLOCK: XaiHighlightsAdapter.build,
            TargetBlockType.EXECUTIVE_SUMMARY_BLOCK: ExecutiveSummaryAdapter.build,
            TargetBlockType.METADATA_BLOCK: MetadataAdapter.build,
            TargetBlockType.SYNTHESIS_TEXT_BLOCK: SynthesisTextAdapter.build,
            TargetBlockType.MATRIX_GRAPHS_BLOCK: MatrixGraphsAdapter.build,
            TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK: MatrixSummaryTableAdapter.build,
            TargetBlockType.VARIANCE_VALIDATION_BLOCK: VarianceAdapter.build,
        }

    @staticmethod
    def _log_blueprint_error(error_code: ErrorCodes, message: str) -> None:
        """Emit a structured RFC 7807 error log entry prior to raising AppException.

        Args:
            error_code: Canonical ErrorCodes member categorizing the failure.
            message: Diagnostic failure description.
        """
        logger.error(
            "[BlueprintTransformer] %s: %s",
            error_code.name,
            message,
            exc_info=True,
            extra={"error_code": error_code.value},
        )

    def _apply_pii_masking(self, text: str) -> str:
        """Apply regex-based PII masking to raw text.

        Args:
            text: Raw text string to sanitize.

        Returns:
            Redacted text string with email addresses and phone numbers masked.
        """
        masked = re.sub(r"[\w\.-]+@[\w\.-]+", "[REDACTED EMAIL]", text)
        return re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[REDACTED PHONE]", masked)

    async def _fetch_execution(self, execution_id: str) -> ExecutionRecord:
        """Fetch an ExecutionRecord by ID or raise a 404 AppException.

        Args:
            execution_id: Canonical execution identifier.

        Returns:
            Hydrated ExecutionRecord instance.

        Raises:
            AppException: If the execution does not exist (RESOURCE_NOT_FOUND).
        """
        execution = await self.exec_repo.get_execution(execution_id)
        if execution is None:
            msg = f"Execution {execution_id} not found."
            self._log_blueprint_error(ErrorCodes.RESOURCE_NOT_FOUND, msg)
            raise AppException(
                message=msg,
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
        return execution

    async def _fetch_workflow(self, workflow_id: str) -> Workflow:
        """Fetch a Workflow definition by ID or raise a 500 AppException.

        Args:
            workflow_id: Canonical workflow identifier.

        Returns:
            Hydrated Workflow domain model.

        Raises:
            AppException: If the workflow blueprint does not exist (VALIDATION_FAILED).
        """
        workflow_obj = await self.workflow_repo.get_workflow(workflow_id)
        if workflow_obj is None:
            msg = f"Executing workflow {workflow_id} not found."
            self._log_blueprint_error(ErrorCodes.VALIDATION_FAILED, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return workflow_obj

    @staticmethod
    def _register_gateway_tools(mcp_tools_map: dict[str, AllowedMCPTool], raw_gateway: object) -> None:
        """Validate an MCP gateway configuration and register its tools by canonical tool_id.

        Args:
            mcp_tools_map: Mutable tool registry indexed by canonical tool_id.
            raw_gateway: Gateway model or boundary payload from repository.
        """
        gateway_obj = (
            raw_gateway
            if isinstance(raw_gateway, SystemConfigMCPGateways)
            else _MCP_GATEWAY_ADAPTER.validate_python(raw_gateway)
        )
        for tool in gateway_obj.tools:
            mcp_tools_map[tool.tool_id] = tool

    async def _resolve_mcp_tools_map(self, mcp_gateway_id: str | None) -> dict[str, AllowedMCPTool]:
        """Resolve configured MCP gateway tools indexed by canonical tool_id.

        Args:
            mcp_gateway_id: Optional workflow-scoped MCP gateway identifier.

        Returns:
            Mapping of canonical tool_id strings to AllowedMCPTool models.

        Raises:
            AppException: If any MCP gateway payload fails schema validation (VALIDATION_FAILED).
        """
        mcp_tools_map: dict[str, AllowedMCPTool] = {}
        try:
            all_gateways_raw = await self.system_repo.get_all_mcp_gateways()
            if isinstance(all_gateways_raw, list):
                for raw_gw in all_gateways_raw:
                    self._register_gateway_tools(mcp_tools_map, raw_gw)

            if mcp_gateway_id:
                raw_gateway = await self.system_repo.get_mcp_gateways(id=mcp_gateway_id)
                if raw_gateway is not None:
                    self._register_gateway_tools(mcp_tools_map, raw_gateway)
        except (ValidationError, TypeError, AttributeError) as gw_err:
            msg = f"Failed to parse MCP gateway config for gateway '{mcp_gateway_id}': {gw_err}"
            self._log_blueprint_error(ErrorCodes.VALIDATION_FAILED, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from gw_err
        return mcp_tools_map

    def _resolve_locale(self, execution: ExecutionRecord, accept_language: str | None) -> str:
        """Resolve target report locale from request header or execution record.

        Args:
            execution: Persisted ExecutionRecord.
            accept_language: Optional explicit locale override.

        Returns:
            Non-empty locale code string.

        Raises:
            AppException: If neither accept_language nor target_locale is populated (VALIDATION_FAILED).
        """
        locale = accept_language if accept_language else execution.target_locale
        if not locale:
            msg = (
                "Strict Fail-Fast Enforced: 'locale' is mandatory "
                "(either via accept_language or execution target_locale) and cannot be resolved."
            )
            self._log_blueprint_error(ErrorCodes.VALIDATION_FAILED, msg)
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return locale

    async def _load_all_output_profiles(self) -> list[OutputProfile]:
        """Fetch and validate all persisted OutputProfile models.

        Returns:
            List of validated OutputProfile domain models.
        """
        raw_profiles = await self.output_profile_repo.get_all_output_profiles()
        return [OutputProfile.model_validate(p_item, strict=False) for p_item in raw_profiles]

    def _resolve_output_profile(
        self,
        all_profiles: list[OutputProfile],
        profile_id: str | None,
        default_profile_id: str | None,
    ) -> OutputProfile:
        """Select the target OutputProfile by explicit ID or workflow default ID.

        Args:
            all_profiles: Available OutputProfile models in storage.
            profile_id: Optional caller-requested OutputProfile ID.
            default_profile_id: Default OutputProfile ID declared on the workflow.

        Returns:
            Matching OutputProfile domain model.

        Raises:
            AppException: If the resolved profile ID does not exist (RESOURCE_NOT_FOUND).
        """
        resolved_pid_request = profile_id if profile_id and profile_id != "default" else default_profile_id
        profile = next((p for p in all_profiles if p.id == resolved_pid_request), None)
        if profile is None:
            msg = f"Output profile '{resolved_pid_request}' not found in the database. Failing fast."
            self._log_blueprint_error(ErrorCodes.RESOURCE_NOT_FOUND, msg)
            raise AppException(
                message=msg,
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
        return profile

    async def _load_prompt_blocks_by_id(self) -> dict[str, AnyPromptBlock]:
        """Fetch all prompt blocks and index them by canonical block ID.

        Returns:
            Dictionary mapping canonical block IDs to validated AnyPromptBlock instances.
        """
        all_blocks_raw = await self.prompt_block_repo.get_all_prompt_blocks()
        blocks_by_id: dict[str, AnyPromptBlock] = {}
        for b_item in all_blocks_raw:
            block = PromptBlockAdapter.validate_python(b_item)
            if block.id:
                blocks_by_id[block.id] = block
        return blocks_by_id

    def _resolve_profile_cache(
        self,
        execution: ExecutionRecord,
        resolved_pid: str,
    ) -> RenderedSynthesisCache | None:
        """Retrieve and validate the cached synthesis entry for the resolved profile.

        Args:
            execution: Persisted ExecutionRecord containing profile_syntheses.
            resolved_pid: Canonical OutputProfile ID.

        Returns:
            Validated RenderedSynthesisCache if present, otherwise None.

        Raises:
            AppException: If section_syntheses is None on a present cache entry (VALIDATION_FAILED).
        """
        if resolved_pid not in execution.profile_syntheses:
            return None
        profile_cache = execution.profile_syntheses[resolved_pid]
        if profile_cache.section_syntheses is None:
            msg = "Fail-Fast: section_syntheses cannot be None in profile_cache."
            self._log_blueprint_error(ErrorCodes.VALIDATION_FAILED, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return profile_cache

    def _extract_scoring_dto(self, results: list[StepOutputDTO]) -> TraceScoringPayloadDTO | None:
        """Extract the final TraceScoringPayloadDTO from folded step outputs.

        Args:
            results: Folded StepOutputDTO list from StateProjector.

        Returns:
            Validated TraceScoringPayloadDTO if emitted, otherwise None.

        Raises:
            AppException: If the scoring payload fails Pydantic validation (VALIDATION_FAILED).
        """
        scoring_dto: TraceScoringPayloadDTO | None = None
        for dto in results:
            if dto.block_id == VirtualSystemStepID.SCORING_RESULT.value and dto.payload:
                try:
                    scoring_dto = _SCORING_PAYLOAD_ADAPTER.validate_python(dto.payload)
                except ValidationError as val_err:
                    msg = f"Failed to parse TraceScoringPayloadDTO from scoring step: {val_err}"
                    self._log_blueprint_error(ErrorCodes.VALIDATION_FAILED, msg)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from val_err
        return scoring_dto

    @staticmethod
    def _has_trace_warning(results: list[StepOutputDTO]) -> bool:
        """Determine whether folded step outputs contain a system warning flag.

        Args:
            results: Folded StepOutputDTO list from StateProjector.

        Returns:
            True if VirtualSystemStepID.HAS_WARNING has a truthy payload, False otherwise.
        """
        return any(dto.block_id == VirtualSystemStepID.HAS_WARNING.value and bool(dto.payload) for dto in results)

    def _extract_validated_penalties(self, scoring_dto: TraceScoringPayloadDTO | None) -> list[str]:
        """Validate applied penalty entries against canonical penalty codes.

        Args:
            scoring_dto: Extracted TraceScoringPayloadDTO or None.

        Returns:
            Ordered list of validated penalty strings.

        Raises:
            AppException: If an unrecognized penalty code is encountered (VALIDATION_FAILED).
        """
        if scoring_dto is None or scoring_dto.penalties_applied is None:
            return []
        penalties_applied: list[str] = []
        for raw_penalty in scoring_dto.penalties_applied:
            penalty_str = str(raw_penalty)
            penalty_code, _, _ = penalty_str.partition(":")
            if penalty_code not in _SUPPORTED_PENALTY_CODES:
                msg = f"Zero-Compromise Check Failed: Legacy or unsupported penalty string: '{penalty_str}'"
                self._log_blueprint_error(ErrorCodes.VALIDATION_FAILED, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
            penalties_applied.append(penalty_str)
        return penalties_applied

    def _extract_rejected_evq_ids(self, execution: ExecutionRecord) -> set[str]:
        """Extract user-rejected evidence quote IDs from evidence_override trace events.

        Args:
            execution: Persisted ExecutionRecord.

        Returns:
            Set of rejected canonical evidence quote IDs.

        Raises:
            AppException: If an evidence_override event fails validation (VALIDATION_FAILED).
        """
        rejected_evq_ids: set[str] = set()
        for ev in execution.execution_trace:
            if ev.event_type == "evidence_override" and ev.content:
                try:
                    if isinstance(ev.content, EvidenceOverrideDTO):
                        override_dto = ev.content
                    else:
                        content_data = ev.content.model_dump() if isinstance(ev.content, BaseModel) else ev.content
                        override_dto = _EVIDENCE_OVERRIDE_ADAPTER.validate_python(content_data)
                    if override_dto.user_rejected and override_dto.evq_id:
                        rejected_evq_ids.add(override_dto.evq_id)
                except ValidationError as val_err:
                    msg = f"Failed to parse EvidenceOverrideDTO in execution trace: {val_err}"
                    self._log_blueprint_error(ErrorCodes.VALIDATION_FAILED, msg)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from val_err
        return rejected_evq_ids

    def _extract_atom_results(self, results: list[StepOutputDTO]) -> list[AtomResultDTO]:
        """Extract evaluated AtomResultDTO items from folded step outputs.

        Args:
            results: Folded StepOutputDTO list from StateProjector.

        Returns:
            Flattened list of validated AtomResultDTO records.

        Raises:
            AppException: If any results payload fails validation (VALIDATION_FAILED).
        """
        v2_results: list[AtomResultDTO] = []
        for dto in results:
            if dto.block_id == "results" and dto.payload:
                try:
                    v2_results.extend(_ATOM_RESULTS_ADAPTER.validate_python(dto.payload))
                except ValidationError as val_err:
                    msg = f"Failed to parse AtomResultDTO list in execution results: {val_err}"
                    self._log_blueprint_error(ErrorCodes.VALIDATION_FAILED, msg)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from val_err
        return v2_results

    def _extract_hydrated_references(self, results: list[StepOutputDTO]) -> dict[str, HydratedAtomDTO]:
        """Extract static HydratedAtomDTO reference mappings from folded step outputs.

        Args:
            results: Folded StepOutputDTO list from StateProjector.

        Returns:
            Dictionary mapping TDA assertion IDs to HydratedAtomDTO instances.

        Raises:
            AppException: If any hydrated_references payload fails validation (VALIDATION_FAILED).
        """
        v2_hydrated_refs: dict[str, HydratedAtomDTO] = {}
        for dto in results:
            if dto.block_id == "hydrated_references" and dto.payload:
                try:
                    envelope = _HydratedReferencesEnvelope.model_validate({"hydrated_references": dto.payload})
                    v2_hydrated_refs.update(envelope.hydrated_references)
                except (ValidationError, TypeError, AttributeError, ValueError) as val_err:
                    msg = f"Failed to parse HydratedAtomDTO in execution results: {val_err}"
                    self._log_blueprint_error(ErrorCodes.VALIDATION_FAILED, msg)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from val_err
        return v2_hydrated_refs

    def _parse_execution_matrices(
        self,
        execution: ExecutionRecord,
        workflow_obj: Workflow,
        profile: OutputProfile,
        profile_cache: RenderedSynthesisCache | None,
        results: list[StepOutputDTO],
        blocks_by_id: dict[str, AnyPromptBlock],
        locale: str,
    ) -> dict[str, MatrixScorecardRowDTO]:
        """Parse evaluative and non-evaluative matrix rows via MatrixDomainParser.

        Args:
            execution: Persisted ExecutionRecord.
            workflow_obj: Hydrated Workflow definition.
            profile: Active OutputProfile model.
            profile_cache: Cached synthesis entry if available.
            results: Folded StepOutputDTO list.
            blocks_by_id: Prompt blocks indexed by canonical ID.
            locale: Resolved target locale code.

        Returns:
            Dictionary of all parsed MatrixScorecardRowDTO items keyed by step/block ID.

        Raises:
            AppException: If evidence overrides or matrix payloads violate schema contracts (VALIDATION_FAILED).
        """
        workflow_ext_values: list[str] = []
        if profile.visible_workflow_extensions:
            workflow_ext_values = [v.value for v in profile.visible_workflow_extensions]

        mcp_audit_map: dict[str, MCPAuditTrace] = {}
        if execution.frozen_context and execution.frozen_context.mcp_tool_audit:
            mcp_audit_map = {trace.id: trace for trace in execution.frozen_context.mcp_tool_audit if trace.id}

        row_explanations_cache: dict[str, str] = {}
        row_curated_quotes_cache: dict[str, list[str]] = {}
        if profile_cache is not None:
            if profile_cache.row_explanations:
                row_explanations_cache = profile_cache.row_explanations
            if profile_cache.row_curated_quotes:
                row_curated_quotes_cache = profile_cache.row_curated_quotes

        parsed_result = MatrixDomainParser.parse_matrices(
            results=results,
            locale=locale,
            blocks_by_id=blocks_by_id,
            workflow_steps={s.id: s for s in workflow_obj.steps},
            profile=profile,
            row_explanations_cache=row_explanations_cache,
            workflow_ext_values=workflow_ext_values,
            row_curated_quotes_cache=row_curated_quotes_cache,
            has_synthesis_cache=profile_cache is not None,
            rejected_evq_ids=self._extract_rejected_evq_ids(execution),
            mcp_audit_map=mcp_audit_map,
            source_identity_manifest=None,
            execution=execution,
            expected_inputs_map={inp.input_key: inp for inp in workflow_obj.expected_inputs},
        )
        self.last_evaluative_matrices = parsed_result.evaluative_matrices
        self.last_all_matrices = list(parsed_result.all_parsed_matrices.values())
        return parsed_result.all_parsed_matrices

    def _extract_event_step_metadata(
        self,
        content: object,
        event_step_meta: StepTraceMetadataDTO | None,
    ) -> StepTraceMetadataDTO | None:
        """Extract StepTraceMetadataDTO from event metadata or polymorphic trace content.

        Args:
            content: TraceEvent content payload.
            event_step_meta: Typed step_metadata attached directly to TraceEvent.metadata.

        Returns:
            Validated StepTraceMetadataDTO if present, otherwise None.

        Raises:
            AppException: If a TraceEventMetadataEnvelope payload is corrupted (VALIDATION_FAILED).
        """
        if event_step_meta is not None:
            return event_step_meta
        if isinstance(content, TraceEventMetadataEnvelope):
            return content.step_metadata
        if content is not None and not isinstance(content, BaseModel | str | int | float | bool | list):
            try:
                return TraceEventMetadataEnvelope.model_validate(content).step_metadata
            except (ValidationError, ValueError) as val_err:
                msg = f"Corrupted TraceEventMetadataEnvelope in execution trace: {val_err}"
                self._log_blueprint_error(ErrorCodes.VALIDATION_FAILED, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from val_err
        return None

    def _resolve_execution_usage(self, execution: ExecutionRecord) -> TokenUsage:
        """Resolve DAG token usage and USD cost with trace-level recovery when top-level counters are zero.

        Args:
            execution: Persisted ExecutionRecord.

        Returns:
            Immutable TokenUsage summarizing DAG prompt, completion, reasoning, total tokens, and USD cost.

        Raises:
            AppException: If trace step_metadata is malformed (VALIDATION_FAILED).
        """
        p_tokens = int(execution.prompt_tokens)
        c_tokens = int(execution.completion_tokens)
        r_tokens = int(execution.reasoning_tokens)
        t_tokens = p_tokens + c_tokens + r_tokens
        total_exec_cost = float(execution.dag_cost_usd)

        if (total_exec_cost == 0.0 or t_tokens == 0) and execution.execution_trace:
            trace_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
            for ev in execution.execution_trace:
                step_meta = self._extract_event_step_metadata(ev.content, ev.metadata.step_metadata)
                if step_meta is not None and step_meta.token_usage is not None:
                    trace_usage = trace_usage + step_meta.token_usage

            if trace_usage.cost_usd > 0.0 or trace_usage.total_tokens > 0:
                if total_exec_cost == 0.0:
                    total_exec_cost = trace_usage.cost_usd
                if t_tokens == 0:
                    p_tokens = trace_usage.prompt_tokens
                    c_tokens = trace_usage.completion_tokens
                    r_tokens = trace_usage.reasoning_tokens
                    t_tokens = trace_usage.total_tokens

        return TokenUsage(
            prompt_tokens=p_tokens,
            completion_tokens=c_tokens,
            reasoning_tokens=r_tokens,
            total_tokens=t_tokens,
            cost_usd=total_exec_cost,
        )

    async def _resolve_organization_name(self, organization_id: str | None) -> str | None:
        """Resolve human-readable organization display name from identity repository.

        Args:
            organization_id: Optional canonical organization ID on the execution record.

        Returns:
            Resolved organization name, original organization_id if unfound, or None.

        Raises:
            AppException: If identity repository lookup fails (RESOURCE_NOT_FOUND).
        """
        if not organization_id:
            return organization_id
        try:
            org = await self.identity_repo.get_organization_model(organization_id)
            if org is not None:
                return org.name
            return organization_id
        except AppException:
            raise
        except Exception as org_err:
            msg = f"Failed to resolve org name for id {organization_id}"
            self._log_blueprint_error(ErrorCodes.RESOURCE_NOT_FOUND, msg)
            raise AppException(
                message=msg,
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            ) from org_err

    async def _resolve_user_name(self, created_by: str | None) -> str | None:
        """Resolve human-readable creator display name from identity repository.

        Args:
            created_by: Optional canonical user ID on the execution record.

        Returns:
            Resolved user display name or None.

        Raises:
            AppException: If identity repository lookup or user validation fails (RESOURCE_NOT_FOUND).
        """
        if not created_by:
            return None
        try:
            user_obj = await self.identity_repo.get_user(created_by)
            if user_obj is not None:
                return _USER_ADAPTER.validate_python(user_obj).name
            return None
        except AppException:
            raise
        except Exception as u_err:
            msg = f"Failed to resolve user name for id {created_by}"
            self._log_blueprint_error(ErrorCodes.RESOURCE_NOT_FOUND, msg)
            raise AppException(
                message=msg,
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            ) from u_err

    @staticmethod
    def _collect_evidence_to_axes(all_parsed_matrices: dict[str, MatrixScorecardRowDTO]) -> dict[str, set[str]]:
        """Build reverse mapping from MCP audit evidence IDs to impacted matrix block IDs.

        Args:
            all_parsed_matrices: Parsed MatrixScorecardRowDTO dictionary.

        Returns:
            Mapping from MCP evidence ID to set of matrix block IDs referencing it.
        """
        evidence_to_axes: dict[str, set[str]] = {}
        for matrix_row in all_parsed_matrices.values():
            for ev_id in matrix_row.used_evidence_ids:
                evidence_to_axes.setdefault(ev_id, set()).add(matrix_row.block_id)
            for atom in matrix_row.evaluated_atoms:
                for quote in atom.exact_quotes:
                    for src_id in quote.verified_source_ids:
                        evidence_to_axes.setdefault(src_id, set()).add(matrix_row.block_id)
        return evidence_to_axes

    def _build_enriched_mcp_audit_data(
        self,
        execution: ExecutionRecord,
        all_parsed_matrices: dict[str, MatrixScorecardRowDTO],
    ) -> list[MCPAuditTrace]:
        """Deduplicate external MCP audit traces and enrich with sanitized summaries and axis names.

        Args:
            execution: Persisted ExecutionRecord.
            all_parsed_matrices: Parsed MatrixScorecardRowDTO dictionary.

        Returns:
            Deduplicated, sanitized list of MCPAuditTrace items.
        """
        mcp_audit_data: list[MCPAuditTrace] = []
        if execution.frozen_context and execution.frozen_context.mcp_tool_audit:
            seen_audits: set[str] = set()
            for audit in execution.frozen_context.mcp_tool_audit:
                if audit.tool_id == "internal_source":
                    continue
                audit_hash = f"{audit.tool_id}::{audit.query}"
                if audit_hash not in seen_audits:
                    seen_audits.add(audit_hash)
                    mcp_audit_data.append(audit)

        if not mcp_audit_data:
            return mcp_audit_data

        evidence_to_axes = self._collect_evidence_to_axes(all_parsed_matrices)
        block_to_axis = {row.block_id: row.name for row in all_parsed_matrices.values()}

        for idx, audit in enumerate(mcp_audit_data):
            sanitized = McpPresentationSanitizer.sanitize_finding(audit.response_summary)
            clean_summary = ""
            if sanitized is not None:
                clean_summary = sanitized
            if audit.id in evidence_to_axes:
                axis_names = {
                    block_to_axis[block_id] for block_id in evidence_to_axes[audit.id] if block_id in block_to_axis
                }
                mcp_audit_data[idx] = audit.model_copy(
                    update={
                        "response_summary": clean_summary,
                        "impacted_axis_names": sorted(axis_names),
                    }
                )
            elif clean_summary != audit.response_summary:
                mcp_audit_data[idx] = audit.model_copy(update={"response_summary": clean_summary})

        return mcp_audit_data

    def _resolve_causal_result(
        self,
        results: list[StepOutputDTO],
        execution: ExecutionRecord,
    ) -> CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None:
        """Resolve causal discovery fusion or graph payload from folded results, trace, or step_states.

        Args:
            results: Folded StepOutputDTO list from StateProjector.
            execution: Persisted ExecutionRecord.

        Returns:
            Validated CausalTdaFusionResultDTO or CausalGraphPayloadDTO if present, otherwise None.

        Raises:
            AppException: If a causal step output fails schema validation (VALIDATION_FAILED).
        """
        for dto in reversed(results):
            if isinstance(dto.payload, CausalTdaFusionResultDTO | CausalGraphPayloadDTO):
                return dto.payload
            if dto.block_id in _CAUSAL_BLOCK_IDS and dto.payload is not None:
                try:
                    return _CAUSAL_RESULT_ADAPTER.validate_python(dto.payload, strict=False)
                except ValidationError as val_err:
                    msg = f"Failed to parse causal payload for block '{dto.block_id}': {val_err}"
                    self._log_blueprint_error(ErrorCodes.VALIDATION_FAILED, msg)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from val_err

        for evt in reversed(execution.execution_trace):
            if isinstance(evt.content, CausalTdaFusionResultDTO | CausalGraphPayloadDTO):
                return evt.content

        for state_val in execution.step_states.values():
            if isinstance(state_val, StepOutputDTO):
                match state_val.payload:
                    case CausalTdaFusionResultDTO() | CausalGraphPayloadDTO():
                        return state_val.payload
            elif isinstance(state_val, CausalTdaFusionResultDTO | CausalGraphPayloadDTO):
                return state_val

        return None

    def _hydrate_sdui_blocks(
        self,
        adapter_context: AdapterContext,
        warning_blocks: list[AnySduiBlock],
    ) -> list[AnySduiBlock]:
        """Dispatch configured TargetBlockType hydrators to assemble ordered SDUI blocks.

        Args:
            adapter_context: Immutable AdapterContext shared across SDUI adapters.
            warning_blocks: Pre-built warning alert blocks from WarningCardAdapter.

        Returns:
            Ordered list of polymorphic AnySduiBlock components.

        Raises:
            AppException: If target_block_order references an unknown or unmapped block type (VALIDATION_FAILED).
        """
        inner_sdui_blocks: list[AnySduiBlock] = list(warning_blocks)
        dispatch_order = adapter_context.profile.target_block_order
        if adapter_context.is_data_starved:
            dispatch_order = [t for t in dispatch_order if t == TargetBlockType.METADATA_BLOCK.value]

        for target_k in dispatch_order:
            try:
                target_enum = TargetBlockType(target_k)
                hydrator = self._target_block_hydrators[target_enum]
            except (KeyError, ValueError) as err:
                msg = f"Strict Fail-Fast: Unknown or unmapped target block type '{target_k}' in target_block_order."
                self._log_blueprint_error(ErrorCodes.VALIDATION_FAILED, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from err

            hydrated_blocks = hydrator(adapter_context)
            if hydrated_blocks:
                inner_sdui_blocks.extend(hydrated_blocks)

        if not inner_sdui_blocks and not adapter_context.is_data_starved:
            inner_sdui_blocks = [SduiRadarChartBlock(axes=self.last_evaluative_matrices)]

        return inner_sdui_blocks

    @staticmethod
    def _collect_short_circuited_claims(
        v2_results: list[AtomResultDTO],
        v2_hydrated_refs: dict[str, HydratedAtomDTO],
        inner_sdui_blocks: list[AnySduiBlock],
    ) -> list[str]:
        """Collect deduplicated short-circuited claim descriptions across atoms and SDUI blocks.

        Args:
            v2_results: Evaluated AtomResultDTO items.
            v2_hydrated_refs: HydratedAtomDTO lookup indexed by TDA ID.
            inner_sdui_blocks: Hydrated SDUI blocks.

        Returns:
            Order-preserving deduplicated list of short-circuited claim strings.
        """
        atom_claims = [
            v2_hydrated_refs[sc_id].resolved_claim.strip()
            for res_item in v2_results
            if res_item.status == ExecutionStatus.N_A
            for sc_id in res_item.short_circuit_reason_tda_ids
            if sc_id in v2_hydrated_refs and v2_hydrated_refs[sc_id].resolved_claim.strip()
        ]
        block_claims = [
            sc
            for block in inner_sdui_blocks
            if isinstance(block, SduiMatrixTableBlock | SduiCausalGraphBlock)
            for sc in block.short_circuited_by_claims
        ]
        return list(dict.fromkeys(atom_claims + block_claims))

    @staticmethod
    def _collect_falsified_warrant_claims(inner_sdui_blocks: list[AnySduiBlock]) -> list[str]:
        """Collect deduplicated falsified warrant claims from matrix and causal SDUI blocks.

        Args:
            inner_sdui_blocks: Hydrated SDUI blocks.

        Returns:
            Order-preserving deduplicated list of falsified warrant claim strings.
        """
        return list(
            dict.fromkeys(
                fw
                for block in inner_sdui_blocks
                if isinstance(block, SduiMatrixTableBlock | SduiCausalGraphBlock)
                for fw in block.falsified_warrant_claims
            )
        )

    async def build_report_dto(
        self,
        execution_id: str,
        profile_id: str | None = None,
        accept_language: str | None = None,
        custom_preface_md: str | None = None,
        local_time_str: str | None = None,
    ) -> ReportDataDTO:
        """Build a strictly typed ReportDataDTO by projecting execution results through an OutputProfile.

        Args:
            execution_id: Canonical identifier of the execution record.
            profile_id: Optional OutputProfile ID overriding the workflow default.
            accept_language: Optional locale string for localized report text.
            custom_preface_md: Optional custom Markdown preface string.
            local_time_str: Optional pre-formatted local generation timestamp string.

        Returns:
            Validated ReportDataDTO ready for Flutter SDUI and Jinja PDF rendering.

        Raises:
            AppException: Triggered for RESOURCE_NOT_FOUND, VALIDATION_FAILED, or CONFIGURATION_ERROR.
        """
        execution = await self._fetch_execution(execution_id)
        workflow_obj = await self._fetch_workflow(execution.workflow_id)
        mcp_tools_map = await self._resolve_mcp_tools_map(workflow_obj.mcp_gateway_id)
        results = StateProjector().fold_trace(execution.execution_trace)
        locale = self._resolve_locale(execution, accept_language)

        all_profiles = await self._load_all_output_profiles()
        profile = self._resolve_output_profile(all_profiles, profile_id, workflow_obj.default_profile_id)
        resolved_pid = str(profile.id)
        blocks_by_id = await self._load_prompt_blocks_by_id()
        profile_cache = self._resolve_profile_cache(execution, resolved_pid)

        scoring_dto = self._extract_scoring_dto(results)
        global_score: float | None = None
        if scoring_dto is not None and scoring_dto.total_score is not None:
            global_score = float(round(float(scoring_dto.total_score), 1))

        penalties_applied = self._extract_validated_penalties(scoring_dto)
        v2_results = self._extract_atom_results(results)
        v2_hydrated_refs = self._extract_hydrated_references(results)

        all_parsed_matrices = self._parse_execution_matrices(
            execution=execution,
            workflow_obj=workflow_obj,
            profile=profile,
            profile_cache=profile_cache,
            results=results,
            blocks_by_id=blocks_by_id,
            locale=locale,
        )

        dag_usage = self._resolve_execution_usage(execution)
        combined_cost = dag_usage.cost_usd + execution.cumulative_synthesis_cost
        combined_tokens = dag_usage.total_tokens + execution.cumulative_synthesis_tokens
        if combined_tokens == 0 and execution.execution_trace:
            logger.warning("[BlueprintTransformer] ALARM: 0 tokens for %s. Telemetry missing.", execution.id)

        org_name = await self._resolve_organization_name(execution.organization_id)
        user_name = await self._resolve_user_name(execution.created_by)
        mcp_audit_data = self._build_enriched_mcp_audit_data(execution, all_parsed_matrices)

        adapter_mcp_audit_map: dict[str, MCPAuditTrace] | None = None
        if mcp_audit_data:
            adapter_mcp_audit_map = {t.id: t for t in mcp_audit_data if t.id}

        adapter_context = AdapterContext(
            execution=execution,
            locale=locale,
            penalties_applied=penalties_applied,
            mcp_audit_map=adapter_mcp_audit_map,
            global_score=global_score,
            profile=profile,
            profile_cache=profile_cache,
            user_name=user_name,
            org_name=org_name,
            parsed_matrices=all_parsed_matrices,
            mcp_tools_map=mcp_tools_map,
            local_time_str=local_time_str,
            scoring_engine="UNIFIED",
            strictness_level=workflow_obj.default_strictness_level,
            cost=combined_cost,
            tokens=combined_tokens,
            causal_result=self._resolve_causal_result(results, execution),
        )

        warning_blocks = WarningCardAdapter.build(adapter_context)
        has_warning = self._has_trace_warning(results) or bool(warning_blocks)
        inner_sdui_blocks = self._hydrate_sdui_blocks(adapter_context, warning_blocks)

        resolved_preface_md = custom_preface_md
        if profile.custom_preface:
            resolved_preface_md = profile.custom_preface.resolve(locale)

        visible_metadata: list[str] = []
        if profile.visible_metadata:
            visible_metadata = profile.visible_metadata

        return ReportDataDTO(
            strictness_level=workflow_obj.default_strictness_level,
            scoring_strategy="UNIFIED",
            scoring_engine_name="UNIFIED",
            user_name=user_name,
            workflow_id=execution.workflow_id,
            execution_id=execution_id,
            profile_id=resolved_pid,
            profile_name=profile.name,
            profile_description=profile.description,
            available_profiles={p.id: p.name for p in all_profiles},
            created_at=execution.created_at,
            local_time_str=local_time_str,
            custom_preface_md=resolved_preface_md,
            org_name=org_name,
            global_score=global_score,
            has_warning=has_warning,
            inner_sdui_blocks=inner_sdui_blocks,
            visible_metadata=visible_metadata,
            cost_estimate=combined_cost,
            total_tokens=combined_tokens,
            prompt_tokens=dag_usage.prompt_tokens,
            completion_tokens=dag_usage.completion_tokens,
            reasoning_tokens=dag_usage.reasoning_tokens,
            mcp_tool_audit=mcp_audit_data,
            results=v2_results,
            hydrated_references=v2_hydrated_refs,
            short_circuited_by_claims=self._collect_short_circuited_claims(
                v2_results, v2_hydrated_refs, inner_sdui_blocks
            ),
            falsified_warrant_claims=self._collect_falsified_warrant_claims(inner_sdui_blocks),
        )
