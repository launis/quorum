"""Blueprint Transformer Service for V3 Extreme MVC."""

import logging
import re
from collections.abc import Callable
from typing import Any

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
from backend_v2.models.dtos.trace import TraceScoringPayloadDTO
from backend_v2.models.enums import (
    TargetBlockType,
    VirtualSystemStepID,
)
from backend_v2.models.state import StateProjector
from backend_v2.models.v2_core import (
    AtomResultDTO,
    HydratedAtomDTO,
    MCPAuditTrace,
    OutputProfile,
    PromptBlock,
    ReportDataDTO,
)
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    SduiRadarChartBlock,
)
from backend_v2.services.matrix_domain_parser import MatrixDomainParser
from backend_v2.services.sdui.adapters.authenticity_adapter import AuthenticityAdapter
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
            TargetBlockType.JARGON_RATIO_BLOCK: lambda ctx: [],
            TargetBlockType.PRINTABLE_SOURCES_BLOCK: lambda ctx: PrintableSourcesAdapter.build(ctx),
            TargetBlockType.GROUPED_EXTENSIONS_BLOCK: lambda ctx: XaiHighlightsAdapter.build(ctx),
            TargetBlockType.EXECUTIVE_SUMMARY_BLOCK: lambda ctx: ExecutiveSummaryAdapter.build(ctx),
            TargetBlockType.METADATA_BLOCK: lambda ctx: MetadataAdapter.build(ctx),
            TargetBlockType.SYNTHESIS_TEXT_BLOCK: lambda ctx: SynthesisTextAdapter.build(ctx),
            TargetBlockType.MATRIX_GRAPHS_BLOCK: lambda ctx: MatrixGraphsAdapter.build(ctx),
            TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK: lambda ctx: MatrixSummaryTableAdapter.build(ctx),
            TargetBlockType.VARIANCE_VALIDATION_BLOCK: lambda ctx: VarianceAdapter.build(ctx),
            TargetBlockType.AUTHENTICITY_EVALUATION_BLOCK: lambda ctx: AuthenticityAdapter.build(ctx),
        }

    def _apply_pii_masking(self, text: str) -> str:
        """Applies regex-based PII masking to text.

        Args:
            text: The raw text string.

        Returns:
            The redacted string.
        """
        # Basic regex fallbacks. Can be replaced with Presidio later.
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

        projector = StateProjector()
        results = projector.fold_trace(execution.execution_trace)

        locale = accept_language
        if not locale and isinstance(execution.metadata, dict):
            locale = execution.metadata.get("target_locale")

        if not locale:
            msg = "Strict Fail-Fast Enforced: 'locale' is mandatory (either via accept_language or execution metadata) and cannot be resolved."
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
        blocks_by_id: dict[str, PromptBlock] = {}
        for b_dict in all_blocks_raw:
            b = PromptBlock.model_validate(b_dict, strict=False)
            if b.id:
                blocks_by_id[b.id] = b

        has_warning = False
        scoring_out = None

        for dto in results:
            if dto.block_id == VirtualSystemStepID.SCORING_RESULT.value and isinstance(dto.payload, dict):
                scoring_out = dto.payload
            if dto.block_id == VirtualSystemStepID.HAS_WARNING.value and dto.payload:
                has_warning = True

        profile_cache = execution.profile_syntheses.get(resolved_pid)
        section_syntheses: dict[str, list[AnySduiBlock]] = {}

        if profile_cache:
            section_syntheses = profile_cache.section_syntheses
            if section_syntheses is None:
                raise AppException(
                    message="Fail-Fast: section_syntheses cannot be None in profile_cache.",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
            # Note: profile_cache.user_role_justification is internal English reasoning and should not be printed directly.

        if any(dto.block_id == VirtualSystemStepID.HAS_WARNING.value and dto.payload for dto in results):
            has_warning = True

        global_score = None
        penalties_applied: list[str] = []
        if isinstance(scoring_out, dict):
            try:
                score_dto = TraceScoringPayloadDTO.model_validate(scoring_out)
                t_score = score_dto.total_score
                global_score = float(round(float(t_score), 1)) if t_score is not None else None
                raw_penalties = score_dto.penalties_applied
                if isinstance(raw_penalties, list):
                    for p in raw_penalties:
                        p_str = str(p)
                        if p_str.startswith("PENALTY_SECURITY:") or p_str.startswith("PENALTY_POST_HOC:"):
                            penalties_applied.append(p_str)
                        else:
                            # Enforce Zero-Compromise Check: fail fast on legacy/unsupported penalty format
                            msg_legacy = f"Zero-Compromise Check Failed: Legacy or unsupported penalty string detected: '{p_str}'"
                            logger.error("[BlueprintTransformer] %s", msg_legacy)
                            raise AppException(
                                message=msg_legacy,
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )
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
                if ev.event_type == "evidence_override" and isinstance(ev.content, dict):
                    if ev.content.get("user_rejected") is True:
                        evq_id = ev.content.get("evq_id")
                        if isinstance(evq_id, str):
                            rejected_evq_ids.add(evq_id)

        mcp_audit_map: dict[str, MCPAuditTrace] = {}
        if execution.frozen_context and execution.frozen_context.mcp_tool_audit:
            for trace in execution.frozen_context.mcp_tool_audit:
                if trace.id:
                    mcp_audit_map[trace.id] = trace

        v2_results: list[Any] = []
        v2_hydrated_refs: dict[str, Any] = {}

        for dto in results:
            if isinstance(dto.payload, dict):
                if "results" in dto.payload and isinstance(dto.payload["results"], list):
                    for r_dict in dto.payload["results"]:
                        v2_results.append(AtomResultDTO.model_validate(r_dict))
                if "hydrated_references" in dto.payload and dto.payload["hydrated_references"]:
                    for k, v_dict in dto.payload["hydrated_references"].items():
                        v2_hydrated_refs[k] = HydratedAtomDTO.model_validate(v_dict)

        workflow_steps_map = {s.id: s for s in workflow_obj.steps} if workflow_obj.steps else {}
        row_explanations_cache: dict[str, str] = {}
        row_curated_quotes_cache: dict[str, list[str]] = {}

        if profile_cache and profile_cache.row_explanations:
            row_explanations_cache = profile_cache.row_explanations
        if profile_cache and profile_cache.row_curated_quotes:
            row_curated_quotes_cache = profile_cache.row_curated_quotes

        (
            evaluative_matrices,
            informational_matrices,
            all_parsed_matrices,
            step_scorecard_atoms,
        ) = MatrixDomainParser.parse_matrices(
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
        )

        modified_step_states = False
        new_step_states = dict(execution.step_states)
        for step_id, atoms_dict in step_scorecard_atoms.items():
            if step_id in new_step_states:
                updated_atoms = {}
                for atom_id, s_atom in atoms_dict.items():
                    existing_atom = new_step_states[step_id].scorecard_atoms.get(atom_id)
                    if existing_atom and existing_atom.human_override:
                        s_atom = s_atom.model_copy(update={"human_override": existing_atom.human_override})
                    updated_atoms[atom_id] = s_atom

                new_step_states[step_id] = new_step_states[step_id].model_copy(
                    update={"scorecard_atoms": updated_atoms}
                )
                modified_step_states = True

        if modified_step_states:
            execution = execution.model_copy(update={"step_states": new_step_states})
            await self.exec_repo.update_execution(
                execution.id, {"step_states": {k: v.model_dump(mode="json") for k, v in new_step_states.items()}}
            )

        total_exec_cost = 0.0
        total_exec_tokens = 0
        if isinstance(execution.metadata, dict):
            total_exec_cost = float(execution.metadata.get("dag_cost_usd", 0.0))
            agg_usage = execution.metadata.get("aggregated_usage", {})
            total_exec_tokens = int(
                agg_usage.get("prompt_tokens", 0)
                + agg_usage.get("completion_tokens", 0)
                + agg_usage.get("reasoning_tokens", 0)
            )

        combined_cost = total_exec_cost + getattr(execution, "cumulative_synthesis_cost", 0.0)
        combined_tokens = total_exec_tokens + getattr(execution, "cumulative_synthesis_tokens", 0)

        scoring_engine_val = (
            getattr(profile.scoring_strategy, "value", str(profile.scoring_strategy))
            if getattr(profile, "scoring_strategy", None)
            else (
                getattr(workflow_obj.default_scoring_strategy, "value", str(workflow_obj.default_scoring_strategy))
                if getattr(workflow_obj, "default_scoring_strategy", None)
                else "AVERAGE"
            )
        )

        try:
            adapter_ctx = AdapterContext(
                execution=execution,
                locale=locale,
                penalties_applied=penalties_applied,
                mcp_audit_map=mcp_audit_map,
                global_score=global_score,
                profile=profile,
                profile_cache=profile_cache,
                user_name=None,
                org_name=None,
                parsed_matrices=all_parsed_matrices,
                local_time_str=local_time_str,
                scoring_engine=scoring_engine_val,
                cost=combined_cost,
                tokens=combined_tokens,
            )

            # Phase 1: Build temp visualization blocks for slop scanner
            temp_visualization_blocks = []

            if not adapter_ctx.is_data_starved:
                # Map graph and table blocks via Adapters
                temp_visualization_blocks.extend(MatrixGraphsAdapter.build(adapter_ctx))
                temp_visualization_blocks.extend(MatrixSummaryTableAdapter.build(adapter_ctx))

                variance_sdui_blocks = VarianceAdapter.build(adapter_ctx)
                if variance_sdui_blocks:
                    temp_visualization_blocks.extend(variance_sdui_blocks)

                auth_sdui_blocks = AuthenticityAdapter.build(adapter_ctx)
                if auth_sdui_blocks:
                    temp_visualization_blocks.extend(auth_sdui_blocks)

                if not temp_visualization_blocks:
                    temp_visualization_blocks = [SduiRadarChartBlock(axes=evaluative_matrices)]

            visualization_blocks = temp_visualization_blocks
        except AppException:
            raise
        except Exception as e:
            msg = f"Failed to build layout DTO: {e}"
            logger.error("[BlueprintTransformer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

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
                user_dict = await self.identity_repo.get_user(execution.created_by)
                if user_dict and "name" in user_dict:
                    user_name = user_dict["name"]
                elif user_dict and "display_name" in user_dict:
                    user_name = user_dict["display_name"]
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

        s_strat = workflow_obj.default_scoring_strategy.value
        if profile.scoring_strategy is not None:
            s_strat = profile.scoring_strategy.value

        engine_str = str(s_strat)

        try:
            p_tokens = 0
            c_tokens = 0
            r_tokens = 0
            t_tokens = 0
            cost = 0.0

            if execution.execution_trace:
                for dto in results:
                    if dto.block_id == VirtualSystemStepID.STEP_METADATA.value and isinstance(dto.payload, dict):
                        usage = dto.payload.get("token_usage")
                        if isinstance(usage, dict):
                            p_tokens += int(usage.get("prompt_tokens") or 0)
                            c_tokens += int(usage.get("completion_tokens") or 0)
                            r_tokens += int(usage.get("reasoning_tokens") or 0)
                            t_tokens += int(usage.get("total_tokens") or 0)
                            cost += float(usage.get("cost_usd") or 0.0)

            if t_tokens == 0 and execution.execution_trace:
                logger.warning("[BlueprintTransformer] ALARM: 0 tokens for %s. Telemetry missing.", execution.id)

            if not visualization_blocks:
                logger.warning(
                    "[BlueprintTransformer] ALARM: 0 visualization blocks generated for execution %s. UI will render empty.",
                    execution.id,
                )

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

            # Phase 2.3: Reverse Lookup Mapping for MCP Audit Traces
            if mcp_audit_data:
                evidence_to_axes: dict[str, set[str]] = {}

                def extract_evidence_ids(payload_data: Any, b_id: str) -> None:
                    if isinstance(payload_data, dict):
                        if "source_id" in payload_data and isinstance(payload_data["source_id"], str):
                            evidence_to_axes.setdefault(payload_data["source_id"], set()).add(b_id)
                        if "used_evidence_ids" in payload_data and isinstance(payload_data["used_evidence_ids"], list):
                            for e_id in payload_data["used_evidence_ids"]:
                                if isinstance(e_id, str):
                                    evidence_to_axes.setdefault(e_id, set()).add(b_id)
                        if "used_mcp_ids" in payload_data and isinstance(payload_data["used_mcp_ids"], list):
                            for e_id in payload_data["used_mcp_ids"]:
                                if isinstance(e_id, str):
                                    evidence_to_axes.setdefault(e_id, set()).add(b_id)
                        for val in payload_data.values():
                            extract_evidence_ids(val, b_id)
                    elif isinstance(payload_data, list):
                        for item in payload_data:
                            extract_evidence_ids(item, b_id)

                for dto in results:
                    extract_evidence_ids(dto.payload, dto.block_id)

                block_to_axis = {matrix_row.block_id: matrix_row.name for matrix_row in all_parsed_matrices.values()}

                for idx, audit in enumerate(mcp_audit_data):
                    if audit.id in evidence_to_axes:
                        axis_names = set()
                        for block_id in evidence_to_axes[audit.id]:
                            if block_id in block_to_axis:
                                axis_names.add(block_to_axis[block_id])
                        mcp_audit_data[idx] = audit.model_copy(update={"impacted_axis_names": sorted(list(axis_names))})

            strictness_level = (
                profile.strictness_level
                if profile.strictness_level is not None
                else workflow_obj.default_strictness_level
            )
            scoring_strategy = (
                profile.scoring_strategy
                if profile.scoring_strategy is not None
                else workflow_obj.default_scoring_strategy
            ).value

            resolved_preface_md = custom_preface_md
            if profile.custom_preface:
                resolved_preface_md = profile.custom_preface.resolve(locale)
            visible_metadata = profile.visible_metadata if profile.visible_metadata else []

            if evaluative_matrices and not (profile_cache and profile_cache.data_starvation is not None):
                total_norm = sum(m.normalized_score for m in evaluative_matrices if m.normalized_score is not None)
                count_norm = sum(1 for m in evaluative_matrices if m.normalized_score is not None)
                if count_norm > 0:
                    base_avg = total_norm / count_norm

                    effective_penalty = 0.0
                    for penalty_str in penalties_applied:
                        if penalty_str.startswith("PENALTY_SECURITY:"):
                            pct = float(penalty_str.split(":")[1])
                            effective_penalty += pct / 100.0
                        elif penalty_str.startswith("PENALTY_POST_HOC:"):
                            pct = float(penalty_str.split(":")[1])
                            effective_penalty += pct / 100.0
                        else:
                            # Enforce Zero-Compromise Check: fail fast on legacy/unsupported penalty format
                            msg_fmt = (
                                f"Zero-Compromise Check Failed: Unsupported or legacy penalty format: '{penalty_str}'"
                            )
                            logger.error("[BlueprintTransformer] %s", msg_fmt)
                            raise AppException(
                                message=msg_fmt,
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )
                    effective_penalty = min(effective_penalty, 0.40)
                    recalc_final = base_avg * (1.0 - effective_penalty)
                    global_score = float(
                        round(max(0.0, recalc_final), 1)
                    )  # Phase 2: Assemble final visualization blocks
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
                local_time_str=local_time_str,
                scoring_engine=scoring_engine_val,
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
                scoring_strategy=scoring_strategy,
                scoring_engine_name=engine_str,
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
                cost_estimate=cost,
                total_tokens=t_tokens,
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
