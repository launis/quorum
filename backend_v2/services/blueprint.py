"""Blueprint Transformer Service for V3 Extreme MVC."""

import logging
import re
from collections.abc import Callable, Mapping

from pydantic import TypeAdapter, ValidationError

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
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock, PromptBlockAdapter
from backend_v2.models.domain.system_config import AllowedMCPTool, MCPAuditTrace, SystemConfigMCPGateways
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.dtos.trace import StepTraceMetadataDTO, TraceEventMetadataEnvelope, TraceScoringPayloadDTO
from backend_v2.models.enums import (
    TargetBlockType,
    VirtualSystemStepID,
)
from backend_v2.models.state import EvidenceOverrideDTO, StateProjector
from backend_v2.models.view.sdui import AnySduiBlock, SduiRadarChartBlock
from backend_v2.services.matrix_domain_parser import MatrixDomainParser
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

logger = logging.getLogger(__name__)

__all__ = ["BlueprintTransformer"]


class BlueprintTransformer:
    """The Universal Transformer Hub. Parses raw execution results into ReportDataDTO."""

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        workflow_repo: IWorkflowRepository,
        comp_repo: IComponentRepository,
        prompt_block_repo: IPromptBlockRepository,
        output_profile_repo: IOutputProfileRepository,
        identity_repo: IIdentityRepository,
        system_repo: ISystemRepository,
    ):
        """Initializes the BlueprintTransformer with required repository interfaces.

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

        self._target_block_hydrators: dict[TargetBlockType, Callable[[AdapterContext], list[AnySduiBlock]]] = {
            TargetBlockType.PENALTIES_BLOCK: lambda ctx: PenaltiesAdapter.build(ctx),
            TargetBlockType.GLOBAL_SCORE_BLOCK: lambda ctx: GlobalScoreAdapter.build(ctx),
            TargetBlockType.AUDIT_TRAIL_BLOCK: lambda ctx: McpAuditAdapter.build(ctx),
            TargetBlockType.PRINTABLE_SOURCES_BLOCK: lambda ctx: PrintableSourcesAdapter.build(ctx),
            TargetBlockType.GROUPED_EXTENSIONS_BLOCK: lambda ctx: XaiHighlightsAdapter.build(ctx),
            TargetBlockType.EXECUTIVE_SUMMARY_BLOCK: lambda ctx: ExecutiveSummaryAdapter.build(ctx),
            TargetBlockType.METADATA_BLOCK: lambda ctx: MetadataAdapter.build(ctx),
            TargetBlockType.SYNTHESIS_TEXT_BLOCK: lambda ctx: SynthesisTextAdapter.build(ctx),
            TargetBlockType.MATRIX_GRAPHS_BLOCK: lambda ctx: MatrixGraphsAdapter.build(ctx),
            TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK: lambda ctx: MatrixSummaryTableAdapter.build(ctx),
            TargetBlockType.VARIANCE_VALIDATION_BLOCK: lambda ctx: VarianceAdapter.build(ctx),
        }

    def _apply_pii_masking(self, text: str) -> str:
        """Applies regex-based PII masking to text.

        Args:
            text: The raw text string.

        Returns:
            The redacted string.
        """
        text = re.sub(r"[\w\.-]+@[\w\.-]+", "[REDACTED EMAIL]", text)
        text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[REDACTED PHONE]", text)
        return text

    async def build_report_dto(
        self,
        execution_id: str,
        profile_id: str | None = None,
        accept_language: str | None = None,
        custom_preface_md: str | None = None,
        local_time_str: str | None = None,
    ) -> ReportDataDTO:
        """Builds the strictly typed report payload by parsing results according to the selected profile.

        Args:
            execution_id: Identifier of the execution.
            profile_id: Optional Output Profile ID to override the workflow default.
            accept_language: Optional locale string for localized titles.
            custom_preface_md: Optional custom markdown preface string.
            local_time_str: Optional formatted string representing local time of generation.

        Returns:
            A strictly typed ReportDataDTO containing the synthesized execution report.

        Raises:
            AppException: Triggered for RESOURCE_NOT_FOUND, VALIDATION_FAILED, or CONFIGURATION_ERROR.
        """
        execution = await self.exec_repo.get_execution(execution_id)
        if not execution:
            msg = f"Execution {execution_id} not found."
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(
                message=msg, status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
            )

        workflow_obj = await self.workflow_repo.get_workflow(execution.workflow_id)
        if not workflow_obj:
            msg = f"Executing workflow {execution.workflow_id} not found."
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        mcp_tools_map: dict[str, AllowedMCPTool] = {}
        mcp_gw_id = workflow_obj.mcp_gateway_id
        if isinstance(mcp_gw_id, str) and mcp_gw_id:
            try:
                raw_gateway = await self.system_repo.get_mcp_gateways(id=mcp_gw_id)
                if isinstance(raw_gateway, SystemConfigMCPGateways):
                    mcp_tools_map = {tool.tool_id: tool for tool in raw_gateway.tools}
                elif raw_gateway is not None:
                    gateway_obj = TypeAdapter(SystemConfigMCPGateways).validate_python(raw_gateway)
                    mcp_tools_map = {tool.tool_id: tool for tool in gateway_obj.tools}
            except (ValidationError, TypeError, AttributeError) as gw_err:
                msg = f"Failed to parse MCP gateway config for gateway '{mcp_gw_id}': {gw_err}"
                logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from gw_err

        projector = StateProjector()
        results = projector.fold_trace(execution.execution_trace)

        locale = accept_language or execution.target_locale

        if not locale:
            msg = (
                "Strict Fail-Fast Enforced: 'locale' is mandatory "
                "(either via accept_language or execution target_locale) and cannot be resolved."
            )
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        default_profile_ref = workflow_obj.default_profile_id
        resolved_pid_request = profile_id if profile_id and profile_id != "default" else default_profile_ref

        all_profiles_dicts = await self.output_profile_repo.get_all_output_profiles()
        all_profiles = [OutputProfile.model_validate(p_dict, strict=False) for p_dict in all_profiles_dicts]

        profile = next((p for p in all_profiles if p.id == resolved_pid_request), None)

        if not profile:
            msg = f"Output profile '{resolved_pid_request}' not found in the database. Failing fast."
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(
                message=msg, status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
            )

        resolved_pid = str(profile.id)

        available_profiles_map = {p.id: p.name for p in all_profiles}
        if resolved_pid not in available_profiles_map:
            available_profiles_map[resolved_pid] = profile.name

        profile_name_dict = profile.name
        workflow_ext_values = (
            [v.value for v in profile.visible_workflow_extensions] if profile.visible_workflow_extensions else []
        )

        all_blocks_raw = await self.prompt_block_repo.get_all_prompt_blocks()
        blocks_by_id: dict[str, AnyPromptBlock] = {}
        for b_dict in all_blocks_raw:
            b = PromptBlockAdapter.validate_python(b_dict)
            if b.id:
                blocks_by_id[b.id] = b

        has_warning = False
        scoring_dto: TraceScoringPayloadDTO | None = None

        for dto in results:
            if dto.block_id == VirtualSystemStepID.SCORING_RESULT.value and dto.payload:
                try:
                    scoring_dto = TypeAdapter(TraceScoringPayloadDTO).validate_python(dto.payload)
                except ValidationError as val_err:
                    msg = f"Failed to parse TraceScoringPayloadDTO from scoring step: {val_err}"
                    logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from val_err
            if dto.block_id == VirtualSystemStepID.HAS_WARNING.value and dto.payload:
                has_warning = True

        profile_cache = (
            execution.profile_syntheses[resolved_pid] if resolved_pid in execution.profile_syntheses else None
        )
        section_syntheses: dict[str, list[AnySduiBlock]] = {}

        if profile_cache:
            section_syntheses = profile_cache.section_syntheses
            if section_syntheses is None:
                raise AppException(
                    message="Fail-Fast: section_syntheses cannot be None in profile_cache.",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

        if any(dto.block_id == VirtualSystemStepID.HAS_WARNING.value and dto.payload for dto in results):
            has_warning = True

        global_score = None
        penalties_applied: list[str] = []
        if scoring_dto is not None:
            try:
                t_score = scoring_dto.total_score
                global_score = float(round(float(t_score), 1)) if t_score is not None else None
                if scoring_dto.penalties_applied is not None:
                    for p in scoring_dto.penalties_applied:
                        p_str = str(p)
                        if (
                            p_str in ("PENALTY_SECURITY", "PENALTY_POST_HOC", "PENALTY_PASSIVITY")
                            or p_str.startswith("PENALTY_SECURITY:")
                            or p_str.startswith("PENALTY_POST_HOC:")
                            or p_str.startswith("PENALTY_PASSIVITY:")
                        ):
                            penalties_applied.append(p_str)
                        else:
                            msg_legacy = (
                                f"Zero-Compromise Check Failed: Legacy or unsupported penalty string: '{p_str}'"
                            )
                            logger.error("[BlueprintTransformer] %s", msg_legacy)
                            raise AppException(
                                message=msg_legacy,
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )
            except AppException:
                raise
            except Exception as e:
                logger.error(
                    "[BlueprintTransformer] %s: Scoring payload extraction failed: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    e,
                    exc_info=True,
                )
                raise AppException(
                    message=f"Scoring payload extraction failed: {e}",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e

        # Pass rejected_evq_ids to the matrix extractor
        rejected_evq_ids: set[str] = set()
        if execution.execution_trace:
            for ev in execution.execution_trace:
                if ev.event_type == "evidence_override" and ev.content:
                    try:
                        override_dto = TypeAdapter(EvidenceOverrideDTO).validate_python(ev.content)
                        if override_dto.user_rejected and override_dto.evq_id:
                            rejected_evq_ids.add(override_dto.evq_id)
                    except ValidationError as val_err:
                        msg = f"Failed to parse EvidenceOverrideDTO in execution trace: {val_err}"
                        logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                        raise AppException(
                            message=msg,
                            status_code=500,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        ) from val_err

        mcp_audit_map: dict[str, MCPAuditTrace] = {}
        if execution.frozen_context and execution.frozen_context.mcp_tool_audit:
            for trace in execution.frozen_context.mcp_tool_audit:
                if trace.id:
                    mcp_audit_map[trace.id] = trace

        v2_results: list[AtomResultDTO] = []
        v2_hydrated_refs: dict[str, HydratedAtomDTO] = {}

        for dto in results:
            if dto.block_id == "results" and dto.payload:
                try:
                    parsed_atoms = TypeAdapter(list[AtomResultDTO]).validate_python(dto.payload)
                    v2_results.extend(parsed_atoms)
                except ValidationError as val_err:
                    msg = f"Failed to parse AtomResultDTO list in execution results: {val_err}"
                    logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from val_err
            elif dto.block_id == "hydrated_references" and isinstance(dto.payload, Mapping):
                for k, v in dto.payload.items():
                    if isinstance(v, HydratedAtomDTO):
                        v2_hydrated_refs[str(k)] = v
                    elif isinstance(v, Mapping):
                        try:
                            v2_hydrated_refs[str(k)] = HydratedAtomDTO.model_validate(v)
                        except ValidationError as val_err:
                            msg = f"Failed to parse HydratedAtomDTO in execution results: {val_err}"
                            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                            raise AppException(
                                message=msg,
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            ) from val_err
                    else:
                        msg = f"Invalid hydrated reference format for key '{k}' in execution results."
                        logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                        raise AppException(
                            message=msg,
                            status_code=500,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        )

        workflow_steps_map = {s.id: s for s in workflow_obj.steps} if workflow_obj.steps else {}
        expected_inputs_list = workflow_obj.expected_inputs if workflow_obj.expected_inputs else []
        expected_inputs_map = {inp.input_key: inp for inp in expected_inputs_list} if expected_inputs_list else {}
        row_explanations_cache: dict[str, str] = {}
        row_curated_quotes_cache: dict[str, list[str]] = {}

        if profile_cache and profile_cache.row_explanations:
            row_explanations_cache = profile_cache.row_explanations
        if profile_cache and profile_cache.row_curated_quotes:
            row_curated_quotes_cache = profile_cache.row_curated_quotes

        parsed_result = MatrixDomainParser.parse_matrices(
            results=results,
            locale=locale,
            blocks_by_id=blocks_by_id,
            workflow_steps=workflow_steps_map,
            profile=profile,
            row_explanations_cache=row_explanations_cache,
            workflow_ext_values=workflow_ext_values,
            row_curated_quotes_cache=row_curated_quotes_cache,
            has_synthesis_cache=bool(profile_cache),
            rejected_evq_ids=rejected_evq_ids,
            mcp_audit_map=mcp_audit_map,
            source_identity_manifest=None,
            execution=execution,
            expected_inputs_map=expected_inputs_map,
        )
        evaluative_matrices = parsed_result.evaluative_matrices
        all_parsed_matrices = parsed_result.all_parsed_matrices

        p_tokens = int(execution.prompt_tokens)
        c_tokens = int(execution.completion_tokens)
        r_tokens = int(execution.reasoning_tokens)
        t_tokens = p_tokens + c_tokens + r_tokens
        total_exec_cost = float(execution.dag_cost_usd)

        # Fail-safe: If DAG cost or tokens are 0 on execution record, extract directly from execution_trace events
        if (total_exec_cost == 0.0 or t_tokens == 0) and execution.execution_trace:
            trace_p = 0
            trace_c = 0
            trace_r = 0
            trace_t = 0
            trace_cost = 0.0
            for ev in execution.execution_trace:
                if not ev.content:
                    continue
                step_meta: StepTraceMetadataDTO | None = None
                if isinstance(ev.content, TraceEventMetadataEnvelope):
                    step_meta = ev.content.step_metadata
                elif isinstance(ev.content, Mapping) and (
                    "_step_metadata" in ev.content or "step_metadata" in ev.content
                ):
                    try:
                        step_meta = TraceEventMetadataEnvelope.model_validate(ev.content).step_metadata
                    except (ValidationError, ValueError) as val_err:
                        msg = f"Corrupted TraceEventMetadataEnvelope in execution trace: {val_err}"
                        logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                        raise AppException(
                            message=msg,
                            status_code=500,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        ) from val_err
                if step_meta and step_meta.token_usage:
                    u = step_meta.token_usage
                    trace_p += u.prompt_tokens
                    trace_c += u.completion_tokens
                    trace_r += u.reasoning_tokens
                    trace_t += u.total_tokens
                    trace_cost += u.cost_usd

            if trace_cost > 0.0 or trace_t > 0:
                if total_exec_cost == 0.0:
                    total_exec_cost = trace_cost
                if t_tokens == 0:
                    p_tokens = trace_p
                    c_tokens = trace_c
                    r_tokens = trace_r
                    t_tokens = trace_t

        total_exec_tokens = t_tokens
        combined_cost = total_exec_cost + execution.cumulative_synthesis_cost
        combined_tokens = total_exec_tokens + execution.cumulative_synthesis_tokens

        scoring_engine_val = "UNIFIED"
        org_name = execution.organization_id
        if execution.organization_id:
            try:
                org = await self.identity_repo.get_organization_model(execution.organization_id)
                if org:
                    org_name = org.name
            except Exception as org_err:
                logger.error(
                    "[BlueprintTransformer] RESOURCE_NOT_FOUND: Failed to resolve org name "
                    f"for id {execution.organization_id}: {org_err}",
                    exc_info=True,
                )
                raise AppException(
                    message=f"Failed to resolve org name for id {execution.organization_id}",
                    status_code=404,
                    details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
                ) from org_err

        user_name = None
        if execution.created_by:
            try:
                user_obj = await self.identity_repo.get_user(execution.created_by)
                if user_obj:
                    user_model = TypeAdapter(User).validate_python(user_obj)
                    user_name = user_model.name
            except Exception as u_err:
                msg_err = f"Failed to resolve user name for id {execution.created_by}"
                logger.error(
                    "[BlueprintTransformer] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg_err, exc_info=True
                )
                raise AppException(
                    message=msg_err,
                    status_code=404,
                    details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
                ) from u_err

        try:
            if combined_tokens == 0 and execution.execution_trace:
                logger.warning("[BlueprintTransformer] ALARM: 0 tokens for %s. Telemetry missing.", execution.id)

            mcp_audit_data: list[MCPAuditTrace] = []
            if execution.frozen_context and execution.frozen_context.mcp_tool_audit:
                raw_audits: list[MCPAuditTrace] = execution.frozen_context.mcp_tool_audit
                seen_audits: set[str] = set()
                for audit in raw_audits:
                    if audit.tool_id == "internal_source":
                        continue

                    audit_hash = f"{audit.tool_id}::{audit.query}"
                    if audit_hash not in seen_audits:
                        seen_audits.add(audit_hash)
                        mcp_audit_data.append(audit)

            # Reverse Lookup Mapping for MCP Audit Traces
            if mcp_audit_data:
                evidence_to_axes: dict[str, set[str]] = {}
                block_to_axis = {matrix_row.block_id: matrix_row.name for matrix_row in all_parsed_matrices.values()}

                for matrix_row in all_parsed_matrices.values():
                    for ev_id in matrix_row.used_evidence_ids:
                        evidence_to_axes.setdefault(ev_id, set()).add(matrix_row.block_id)
                    for atom in matrix_row.evaluated_atoms:
                        for q in atom.exact_quotes:
                            for src_id in q.verified_source_ids:
                                evidence_to_axes.setdefault(src_id, set()).add(matrix_row.block_id)

                for idx, audit in enumerate(mcp_audit_data):
                    if audit.id in evidence_to_axes:
                        axis_names = {
                            block_to_axis[block_id]
                            for block_id in evidence_to_axes[audit.id]
                            if block_id in block_to_axis
                        }
                        mcp_audit_data[idx] = audit.model_copy(update={"impacted_axis_names": sorted(list(axis_names))})

            strictness_level = workflow_obj.default_strictness_level

            resolved_preface_md = custom_preface_md
            if profile.custom_preface:
                resolved_preface_md = profile.custom_preface.resolve(locale)
            visible_metadata = profile.visible_metadata if profile.visible_metadata else []
            inner_sdui_blocks: list[AnySduiBlock] = []

            adapter_context = AdapterContext(
                execution=execution,
                locale=locale,
                penalties_applied=penalties_applied,
                mcp_audit_map={t.id: t for t in mcp_audit_data if t.id} if mcp_audit_data else None,
                global_score=global_score,
                profile=profile,
                profile_cache=profile_cache,
                user_name=user_name,
                org_name=org_name,
                parsed_matrices=all_parsed_matrices,
                mcp_tools_map=mcp_tools_map,
                local_time_str=local_time_str,
                scoring_engine=scoring_engine_val,
                strictness_level=strictness_level,
                cost=combined_cost,
                tokens=combined_tokens,
            )

            warning_blocks = WarningCardAdapter.build(adapter_context)
            if warning_blocks:
                has_warning = True
                inner_sdui_blocks.extend(warning_blocks)

            dispatch_order = profile.target_block_order
            if adapter_context.is_data_starved:
                # In data starvation mode, ONLY the cover page/metadata is rendered.
                dispatch_order = [t for t in dispatch_order if t == TargetBlockType.METADATA_BLOCK.value]

            for target_k in dispatch_order:
                try:
                    target_enum = TargetBlockType(target_k)
                    hydrator = self._target_block_hydrators[target_enum]
                except (KeyError, ValueError) as e:
                    msg = f"Strict Fail-Fast: Unknown or unmapped target block type '{target_k}' in target_block_order."
                    logger.error(
                        "[BlueprintTransformer] %s: %s",
                        ErrorCodes.VALIDATION_FAILED.name,
                        msg,
                        exc_info=True,
                    )
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from e

                hydrated_blocks = hydrator(adapter_context)
                if hydrated_blocks:
                    inner_sdui_blocks.extend(hydrated_blocks)

            if not inner_sdui_blocks and not adapter_context.is_data_starved:
                inner_sdui_blocks = [SduiRadarChartBlock(axes=evaluative_matrices)]

            report_dto = ReportDataDTO(
                strictness_level=strictness_level,
                scoring_strategy=scoring_engine_val,
                scoring_engine_name=scoring_engine_val,
                user_name=user_name,
                workflow_id=execution.workflow_id,
                execution_id=execution_id,
                profile_id=resolved_pid,
                profile_name=profile_name_dict,
                profile_description=profile.description,
                available_profiles=available_profiles_map,
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
                prompt_tokens=p_tokens,
                completion_tokens=c_tokens,
                reasoning_tokens=r_tokens,
                mcp_tool_audit=mcp_audit_data,
                results=v2_results,
                hydrated_references=v2_hydrated_refs,
            )
            return report_dto
        except Exception as e:
            msg = f"Failed to map execution {execution.id} results to ReportDataDTO: {e}"
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
            ) from e
