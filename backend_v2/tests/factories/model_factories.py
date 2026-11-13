"""Centralized Polyfactory model factories for strict Pydantic V2 models."""

from __future__ import annotations

import uuid
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel

from backend_v2.exceptions import AppException
from backend_v2.models.auth import TenantSecretDTO
from backend_v2.models.core_base import (
    I18nText,
    generate_opaque_id,
    generate_uuid7,
    parse_prefixed_uuid7,
)
from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.archival import PrecedentDTO
from backend_v2.models.domain.base import AuditLogRecord, UsageRecord
from backend_v2.models.domain.causal import CausalAnalysis
from backend_v2.models.domain.evaluation import EvaluationResult
from backend_v2.models.domain.execution import (
    ExecutionAssignment,
    ExecutionRecord,
    ExecutionStep,
    FrozenContext,
)
from backend_v2.models.domain.falsifier import (
    FalsifierData,
    ReasoningFidelity,
    WaltonStressTest,
)
from backend_v2.models.domain.hydration import HydrationInputSourceDTO
from backend_v2.models.domain.inputs import DomainInputValue, WorkflowInputs
from backend_v2.models.domain.interaction import InteractionAnalysisDTO
from backend_v2.models.domain.linguistics import LinguisticsResultDTO
from backend_v2.models.domain.logician import LogicianData
from backend_v2.models.domain.matrix import FlattenedAtom, MatrixRow, MatrixScale
from backend_v2.models.domain.metadata import StepMetadataDTO
from backend_v2.models.domain.metrics import ProfilerMetricsDTO
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.overseer import OverseerData
from backend_v2.models.domain.performativity import PerformativityAnalysis
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.domain.references import BibliographyResultDTO
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.domain.scoring import StepPanelDTO
from backend_v2.models.domain.step import ExpectedInput, Step, StepRule
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup, RenderedSynthesisCache
from backend_v2.models.domain.system_config import (
    AllowedMCPTool,
    MCPAuditTrace,
    ModelProfile,
    ProviderExtraParamsDTO,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.models.domain.task_brief import TaskAssignmentBriefDTO, TaskBrief
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.causal_discovery import (
    CausalEdgeDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
)
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
from backend_v2.models.dtos.lightweight_matrix import ScoringResultDTO
from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO
from backend_v2.models.dtos.mcp import MCPToolParamOverrides
from backend_v2.models.dtos.node_execution import (
    StepOutputContentDTO,
    StepOutputContentValue,
)
from backend_v2.models.dtos.report_artifact import (
    ReportMetadataDTO,
    ReportStatus,
    ReportStoragePathsDTO,
)
from backend_v2.models.dtos.schema_manifest import GeneratedSchemaManifestDTO
from backend_v2.models.dtos.step_output import StepPayloadValue
from backend_v2.models.dtos.synthesis import SynthesisDistillationDTO
from backend_v2.models.dtos.theory_manifest import InjectedTheoryManifestDTO
from backend_v2.models.dtos.trace import TraceEventMetadataDTO, TraceScoringPayloadDTO
from backend_v2.models.enums import (
    AssignmentResultVisibility,
    AssignmentStatus,
    BlockDataType,
    CognitiveTier,
    DisplayScale,
    EmailDeliveryStatus,
    EngineType,
    EntityPrefix,
    ExecutionStatus,
    FidelityLevel,
    HistoricalContextMode,
    LLMProvider,
    MCPAuthType,
    MCPTransportType,
    PromptBlockCategory,
    SecretScope,
    SecretStorageMode,
    StepType,
    StepZone,
    SystemLocale,
    TargetBlockType,
    UserRole,
    VisualIntent,
    XaiExtensionType,
)
from backend_v2.models.llm import LLMProviderConfig
from backend_v2.models.state import (
    ErrorTraceEvent,
    EvidenceOverrideDTO,
    ReasoningTrace,
    TombstoneEvent,
    TraceEvent,
)
from backend_v2.models.view.sdui import AnySduiBlock, ReportView

__all__ = [
    "AuditLogRecordFactory",
    "CausalGraphPayloadDTOFactory",
    "CausalNodeDTOFactory",
    "ErrorTraceEventFactory",
    "ExecutionAssignmentFactory",
    "ExecutionRecordFactory",
    "ExecutionStepFactory",
    "GlobalContextVarsDTOFactory",
    "I18nTextFactory",
    "LLMProviderConfigFactory",
    "MCPAuditTraceFactory",
    "MatrixPromptBlockFactory",
    "ModelProfileFactory",
    "OutputProfileFactory",
    "ReportArtifactFactory",
    "ReportViewFactory",
    "StepFactory",
    "StepPanelDTOFactory",
    "SystemConfigMCPGatewaysFactory",
    "SystemConfigModelRegistryFactory",
    "SystemRulePromptBlockFactory",
    "TaskBriefFactory",
    "TenantSecretDTOFactory",
    "TraceEventFactory",
    "UsageRecordFactory",
    "WorkflowFactory",
]


class I18nTextFactory(ModelFactory[I18nText]):
    """Polyfactory model factory for I18nText localization containers."""

    __model__ = I18nText
    __set_as_default_factory_for_type__ = True

    @classmethod
    def translations(cls) -> dict[str, str]:
        """Generate standard English and Finnish test translations.

        Returns:
            Dictionary mapping locale codes to localized test strings.
        """
        return {"en": "English test text", "fi": "Finnish test text"}


class WorkflowFactory(ModelFactory[Workflow]):
    """Polyfactory model factory for DAG Workflow orchestrator models."""

    __model__ = Workflow
    __set_as_default_factory_for_type__ = True

    status: str = "draft"
    version: int = 1
    is_public: bool = False
    historical_context_mode: HistoricalContextMode = HistoricalContextMode.DISABLED

    @classmethod
    def organization_id(cls) -> str:
        """Generate a valid organization Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'org_' prefix.
        """
        return generate_opaque_id(EntityPrefix.ORGANIZATION)

    @classmethod
    def expected_inputs(cls) -> list[ExpectedInput]:
        """Generate an empty expected inputs list.

        Returns:
            Empty list of ExpectedInput models.
        """
        return []

    @classmethod
    def steps(cls) -> list[StepRule]:
        """Generate an empty workflow steps list.

        Returns:
            Empty list of StepRule models.
        """
        return []

    @classmethod
    def id(cls) -> str:
        """Generate a valid Opaque Stripe ID with 'wf_' prefix.

        Returns:
            Canonical Opaque Stripe ID with 'wf_' prefix.
        """
        return generate_opaque_id(EntityPrefix.WORKFLOW)

    @classmethod
    def slug(cls) -> str:
        """Generate a unique test slug.

        Returns:
            Unique workflow slug identifier string.
        """
        return f"wf_slug_{generate_uuid7().hex[:8]}"

    @classmethod
    def name(cls) -> I18nText:
        """Generate a localized workflow name.

        Returns:
            I18nText instance containing localized workflow names.
        """
        return I18nText(translations={"en": "Test Workflow", "fi": "Testi Työnkulku"})

    @classmethod
    def description(cls) -> I18nText:
        """Generate a localized workflow description.

        Returns:
            I18nText instance containing localized workflow descriptions.
        """
        return I18nText(translations={"en": "Test Workflow Description", "fi": "Testi Työnkulun Kuvaus"})

    @classmethod
    def default_profile_id(cls) -> str:
        """Generate a valid default profile Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'prf_' prefix.
        """
        return generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)

    @classmethod
    def model_registry_id(cls) -> str:
        """Generate a valid model registry Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'mrg_' prefix.
        """
        return generate_opaque_id(EntityPrefix.MODEL_REGISTRY)

    @classmethod
    def mcp_gateway_id(cls) -> str:
        """Generate a valid MCP gateway Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'mcp_' prefix.
        """
        return generate_opaque_id(EntityPrefix.MCP_GATEWAY)


class StepFactory(ModelFactory[Step]):
    """Polyfactory model factory for Step domain models."""

    __model__ = Step
    __set_as_default_factory_for_type__ = True

    type: StepType = StepType.LLM
    cognitive_tier: CognitiveTier = CognitiveTier.FAST
    hook: str | None = None
    role_block_id: str | None = None
    execution_persona_block_id: str | None = None
    safety: Literal["safe", "unsafe"] = "safe"
    is_system_core: bool = False
    engine_type: EngineType = EngineType.PROMPT
    zone: StepZone = StepZone.ZONE_B

    @classmethod
    def organization_id(cls) -> str:
        """Generate a valid Opaque Stripe ID with 'org_' prefix.

        Returns:
            Canonical Opaque Stripe ID with 'org_' prefix.
        """
        return generate_opaque_id(EntityPrefix.ORGANIZATION)

    @classmethod
    def id(cls) -> str:
        """Generate a valid Opaque Stripe ID with 'stp_' prefix.

        Returns:
            Canonical Opaque Stripe ID with 'stp_' prefix.
        """
        return generate_opaque_id(EntityPrefix.STEP)

    @classmethod
    def slug(cls) -> str:
        """Generate a unique step slug.

        Returns:
            Unique step slug identifier string.
        """
        return f"step_slug_{generate_uuid7().hex[:8]}"

    @classmethod
    def name(cls) -> I18nText:
        """Generate a localized step name.

        Returns:
            I18nText instance containing localized step names.
        """
        return I18nText(translations={"en": "Test Step", "fi": "Testiaskel"})

    @classmethod
    def description(cls) -> I18nText:
        """Generate a localized step description.

        Returns:
            I18nText instance containing localized step descriptions.
        """
        return I18nText(translations={"en": "Test Step Description", "fi": "Testiaskeleen kuvaus"})

    @classmethod
    def extraction_protocol_block_id(cls) -> str:
        """Generate a valid extraction protocol block Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'blk_' prefix.
        """
        return generate_opaque_id(EntityPrefix.PROMPT_BLOCK)

    @classmethod
    def criteria_block_ids(cls) -> list[str]:
        """Generate a default single-element criteria block IDs list for LLM steps.

        Returns:
            List containing one canonical 'blk_' prompt block identifier.
        """
        return [generate_opaque_id(EntityPrefix.PROMPT_BLOCK)]

    @classmethod
    def pre_hooks(cls) -> list[str]:
        """Generate an empty pre-hooks list.

        Returns:
            Empty list of pre-hook identifiers.
        """
        return []

    @classmethod
    def post_hooks(cls) -> list[str]:
        """Generate an empty post-hooks list.

        Returns:
            Empty list of post-hook identifiers.
        """
        return []

    @classmethod
    def allowed_mcp_tools(cls) -> list[str]:
        """Generate an empty allowed MCP tools list.

        Returns:
            Empty list of MCP tool aliases.
        """
        return []

    @classmethod
    def mcp_tool_params(cls) -> dict[str, MCPToolParamOverrides]:
        """Generate an empty MCP tool parameter overrides mapping.

        Returns:
            Empty dictionary mapping MCP tool aliases to overrides.
        """
        return {}

    @classmethod
    def expected_inputs(cls) -> list[str]:
        """Generate an empty expected input keys list.

        Returns:
            Empty list of expected input key strings.
        """
        return []


class SystemRulePromptBlockFactory(ModelFactory[SystemRulePromptBlock]):
    """Polyfactory model factory for SystemRulePromptBlock domain models."""

    __model__ = SystemRulePromptBlock
    __set_as_default_factory_for_type__ = True

    category_id: PromptBlockCategory = PromptBlockCategory.SYSTEM_RULE
    type: BlockDataType = BlockDataType.INSTRUCTION
    is_evaluative: bool = False
    allow_decimals: bool = False
    is_lightweight_protocol: bool = False
    instruction_text: str | None = "System instruction text for test execution."

    @classmethod
    def organization_id(cls) -> str:
        """Generate a valid organization Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'org_' prefix.
        """
        return generate_opaque_id(EntityPrefix.ORGANIZATION)

    @classmethod
    def output_extensions(cls) -> list[str]:
        """Generate an empty output extensions list.

        Returns:
            Empty list of output extension strings.
        """
        return []

    @classmethod
    def id(cls) -> str:
        """Generate a valid Opaque Stripe ID with 'blk_' prefix.

        Returns:
            Canonical Opaque Stripe ID with 'blk_' prefix.
        """
        return generate_opaque_id(EntityPrefix.PROMPT_BLOCK)

    @classmethod
    def slug(cls) -> str:
        """Generate a unique block slug.

        Returns:
            Unique prompt block slug string.
        """
        return f"blk_slug_{generate_uuid7().hex[:8]}"

    @classmethod
    def label(cls) -> I18nText:
        """Generate a localized block label.

        Returns:
            I18nText instance containing localized block labels.
        """
        return I18nText(translations={"en": "Test Block Label", "fi": "Testilohkon Nimike"})

    @classmethod
    def description(cls) -> I18nText:
        """Generate a localized block description.

        Returns:
            I18nText instance containing localized block descriptions.
        """
        return I18nText(translations={"en": "Test Block Description", "fi": "Testilohkon Kuvaus"})


class TaskBriefFactory(ModelFactory[TaskBrief]):
    """Polyfactory model factory for TaskBrief domain models."""

    __model__ = TaskBrief
    __set_as_default_factory_for_type__ = True

    instruction_text: str = "Complete the task brief deliverables according to the instructions."
    source_url: str | None = "https://docs.example.com/task-brief.pdf"

    @classmethod
    def id(cls) -> str:
        """Generate a valid Opaque Stripe ID with 'tbr_' prefix.

        Returns:
            Canonical Opaque Stripe ID with 'tbr_' prefix.
        """
        return generate_opaque_id(EntityPrefix.TASK_BRIEF)

    @classmethod
    def slug(cls) -> str:
        """Generate a unique task brief slug.

        Returns:
            Unique task brief slug string.
        """
        return f"task_brief_{generate_uuid7().hex}"

    @classmethod
    def organization_id(cls) -> str:
        """Generate a valid organization Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'org_' prefix.
        """
        return generate_opaque_id(EntityPrefix.ORGANIZATION)

    @classmethod
    def label(cls) -> I18nText:
        """Generate a localized task brief label.

        Returns:
            I18nText instance containing localized task brief labels.
        """
        return I18nText(translations={"en": "Test Task Brief", "fi": "Testitehtävänanto"})

    @classmethod
    def description(cls) -> I18nText:
        """Generate a localized task brief description.

        Returns:
            I18nText instance containing localized task brief descriptions.
        """
        return I18nText(translations={"en": "Test Task Brief Description", "fi": "Testitehtävänannon kuvaus"})


class ExecutionAssignmentFactory(ModelFactory[ExecutionAssignment]):
    """Polyfactory model factory for ExecutionAssignment domain models."""

    __model__ = ExecutionAssignment
    __set_as_default_factory_for_type__ = True

    batch_id: str | None = None
    assigned_email: str = "candidate@quorum.ai"
    assigned_user_id: str | None = None
    invited_role: UserRole = UserRole.MEMBER
    output_profile_id: str | None = None
    task_brief_id: str | None = None
    task_brief_snapshot: TaskAssignmentBriefDTO | None = None
    target_locale: SystemLocale = SystemLocale.FI
    token_hash: str = "b" * 64
    status: AssignmentStatus = AssignmentStatus.PENDING
    email_delivery_status: EmailDeliveryStatus = EmailDeliveryStatus.PENDING
    result_visibility: AssignmentResultVisibility = AssignmentResultVisibility.CONFIRMATION_ONLY
    relative_duration_seconds: int | None = None
    activated_at: datetime | None = None
    submitted_at: datetime | None = None
    execution_id: str | None = None

    @classmethod
    def id(cls) -> str:
        """Generate a valid assignment Opaque Stripe ID with 'tsk_' prefix.

        Returns:
            Canonical Opaque Stripe ID with 'tsk_' prefix.
        """
        return generate_opaque_id(EntityPrefix.ASSIGNMENT)

    @classmethod
    def organization_id(cls) -> str:
        """Generate a valid organization Opaque Stripe ID with 'org_' prefix.

        Returns:
            Canonical Opaque Stripe ID with 'org_' prefix.
        """
        return generate_opaque_id(EntityPrefix.ORGANIZATION)

    @classmethod
    def workflow_id(cls) -> str:
        """Generate a valid workflow Opaque Stripe ID with 'wf_' prefix.

        Returns:
            Canonical Opaque Stripe ID with 'wf_' prefix.
        """
        return generate_opaque_id(EntityPrefix.WORKFLOW)

    @classmethod
    def created_by(cls) -> str:
        """Generate a valid creator user Opaque Stripe ID with 'usr_' prefix.

        Returns:
            Canonical Opaque Stripe ID with 'usr_' prefix.
        """
        return generate_opaque_id(EntityPrefix.USER)

    @classmethod
    def locked_inputs(cls) -> WorkflowInputs:
        """Generate an empty manager-locked workflow inputs container.

        Returns:
            Initialized WorkflowInputs model instance.
        """
        return WorkflowInputs(dynamic_inputs={})

    @classmethod
    def assignee_input_keys(cls) -> list[str]:
        """Generate an empty unlocked assignee input keys list.

        Returns:
            Empty list of input key strings.
        """
        return []

    @classmethod
    def draft_inputs(cls) -> WorkflowInputs:
        """Generate an empty draft workflow inputs container.

        Returns:
            Initialized WorkflowInputs model instance.
        """
        return WorkflowInputs(dynamic_inputs={})

    @classmethod
    def hard_deadline_at(cls) -> datetime:
        """Generate a future UTC hard deadline timestamp.

        Returns:
            UTC-aware datetime 24 hours in the future.
        """
        return datetime.now(UTC) + timedelta(hours=24)

    @classmethod
    def created_at(cls) -> datetime:
        """Generate a current UTC creation timestamp.

        Returns:
            UTC-aware current datetime.
        """
        return datetime.now(UTC)


class OutputProfileFactory(ModelFactory[OutputProfile]):
    """Polyfactory model factory for OutputProfile presentation configuration models."""

    __model__ = OutputProfile
    __set_as_default_factory_for_type__ = True

    display_scale: DisplayScale = DisplayScale.ORIGINAL
    variance_target_block: str | None = None
    user_role_target_block: str | None = None

    @classmethod
    def organization_id(cls) -> str:
        """Generate a valid organization Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'org_' prefix.
        """
        return generate_opaque_id(EntityPrefix.ORGANIZATION)

    @classmethod
    def target_block_order(cls) -> list[TargetBlockType]:
        """Generate standard target block ordering.

        Returns:
            Ordered list of TargetBlockType enum values.
        """
        return [
            TargetBlockType.METADATA_BLOCK,
            TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
            TargetBlockType.SYNTHESIS_TEXT_BLOCK,
        ]

    @classmethod
    def matrix_synthesis_groups(cls) -> list[MatrixSynthesisGroup]:
        """Generate an empty matrix synthesis groups list.

        Returns:
            Empty list of MatrixSynthesisGroup models.
        """
        return []

    @classmethod
    def layout(cls) -> list[AnySduiBlock]:
        """Generate a deterministic empty SDUI layout block list.

        Returns:
            Empty list of AnySduiBlock models.
        """
        return []

    @classmethod
    def content_blocks(cls) -> list[AnySduiBlock]:
        """Generate a deterministic empty SDUI content blocks list.

        Returns:
            Empty list of AnySduiBlock models.
        """
        return []

    @classmethod
    def visible_workflow_extensions(cls) -> list[XaiExtensionType]:
        """Generate a deterministic empty visible workflow extensions list.

        Returns:
            Empty list of XaiExtensionType enum values.
        """
        return []

    @classmethod
    def metadata_visible_fields(cls) -> list[str]:
        """Generate standard metadata visible fields.

        Returns:
            List of visible metadata field keys.
        """
        return ["date", "organization", "user", "scoring_engine", "strictness"]

    @classmethod
    def matrix_visible_columns(cls) -> list[str]:
        """Generate standard matrix visible columns.

        Returns:
            List of visible matrix column keys.
        """
        return [
            "label",
            "distribution",
            "row_explanation",
            "normalized_score",
            "raw_score",
        ]

    @classmethod
    def id(cls) -> str:
        """Generate a valid Opaque Stripe ID with 'prf_' prefix.

        Returns:
            Canonical Opaque Stripe ID with 'prf_' prefix.
        """
        return generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)

    @classmethod
    def slug(cls) -> str:
        """Generate a unique profile slug.

        Returns:
            Unique output profile slug string.
        """
        return f"prof_slug_{generate_uuid7().hex[:8]}"

    @classmethod
    def workflow_id(cls) -> str:
        """Generate an associated workflow Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'wf_' prefix.
        """
        return generate_opaque_id(EntityPrefix.WORKFLOW)

    @classmethod
    def name(cls) -> I18nText:
        """Generate a localized profile name.

        Returns:
            I18nText instance containing localized profile names.
        """
        return I18nText(translations={"en": "Executive Summary Profile", "fi": "Johdon Tiivistelmä"})

    @classmethod
    def description(cls) -> I18nText:
        """Generate a localized profile description.

        Returns:
            I18nText instance containing localized profile descriptions.
        """
        return I18nText(translations={"en": "Profile Description", "fi": "Profiilin Kuvaus"})


class MatrixPromptBlockFactory(ModelFactory[MatrixPromptBlock]):
    """Polyfactory model factory for MatrixPromptBlock domain models."""

    __model__ = MatrixPromptBlock
    __set_as_default_factory_for_type__ = True

    category_id: PromptBlockCategory = PromptBlockCategory.MATRIX
    type: BlockDataType = BlockDataType.FLOAT
    is_evaluative: bool = True
    allow_decimals: bool = False
    allow_contextual_override: bool = False
    is_lightweight_protocol: bool = False
    ai_description: str | None = "Evaluate target dimension against BARS criteria."
    columns: list[I18nText] | None = None
    computed_min: int | None = None
    computed_max: int | None = None

    @classmethod
    def organization_id(cls) -> str:
        """Generate a valid organization Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'org_' prefix.
        """
        return generate_opaque_id(EntityPrefix.ORGANIZATION)

    @classmethod
    def id(cls) -> str:
        """Generate a valid Opaque Stripe ID with 'blk_' prefix.

        Returns:
            Canonical Opaque Stripe ID with 'blk_' prefix.
        """
        return generate_opaque_id(EntityPrefix.PROMPT_BLOCK)

    @classmethod
    def slug(cls) -> str:
        """Generate a unique matrix block slug.

        Returns:
            Unique matrix block slug string.
        """
        return f"mat_{generate_uuid7().hex[:8]}"

    @classmethod
    def label(cls) -> I18nText:
        """Generate a localized matrix block label.

        Returns:
            I18nText instance containing localized matrix block labels.
        """
        return I18nText(translations={"en": "Test Matrix Block", "fi": "Testimatriisilohko"})

    @classmethod
    def description(cls) -> I18nText:
        """Generate a localized matrix block description.

        Returns:
            I18nText instance containing localized matrix block descriptions.
        """
        return I18nText(translations={"en": "Test Matrix Description", "fi": "Testimatriisin Kuvaus"})

    @classmethod
    def scales(cls) -> list[MatrixScale]:
        """Generate standard BARS scale bounds.

        Returns:
            List of MatrixScale instances defining minimum and maximum score anchors.
        """
        return [
            MatrixScale(
                score=1,
                ai_label="POOR",
                name=I18nText(translations={"en": "Poor", "fi": "Heikko"}),
                claims=[],
            ),
            MatrixScale(
                score=5,
                ai_label="EXCELLENT",
                name=I18nText(translations={"en": "Excellent", "fi": "Erinomainen"}),
                claims=[],
            ),
        ]

    @classmethod
    def rows(cls) -> list[MatrixRow]:
        """Generate target evaluation dimensions.

        Returns:
            List of MatrixRow instances defining evaluation rows.
        """
        return [
            MatrixRow(
                label=I18nText(translations={"en": "dim_target", "fi": "dim_target"}),
                ai_description="Evaluate target dimension",
            )
        ]


class ExecutionStepFactory(ModelFactory[ExecutionStep]):
    """Polyfactory model factory for ExecutionStep DAG node state models."""

    __model__ = ExecutionStep
    __set_as_default_factory_for_type__ = True

    label: str = "Test Execution Step"
    status: ExecutionStatus = ExecutionStatus.PENDING
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0
    reasoning_tokens: int = 0
    cost_usd: float = 0.0
    duration_ms: int = 0
    chunk_count: int = 1

    @classmethod
    def scorecard_atoms(cls) -> dict[str, ScorecardAtomDTO]:
        """Generate an empty scorecard atoms mapping.

        Returns:
            Empty dictionary mapping atom keys to ScorecardAtomDTO instances.
        """
        return {}

    @classmethod
    def id(cls) -> str:
        """Generate a valid step identifier.

        Returns:
            Canonical Opaque Stripe ID with 'stp_' prefix.
        """
        return generate_opaque_id(EntityPrefix.STEP)


def _extract_factory_uuid7_timestamp(prefixed_id: str, prefix: EntityPrefix) -> datetime:
    """Derive the UTC timestamp embedded in a canonical UUIDv7 Opaque Stripe ID.

    Args:
        prefixed_id: Canonical Opaque Stripe ID carrying a version 7 UUID.
        prefix: Expected EntityPrefix enum member.

    Returns:
        UTC-aware datetime decoded from the top 48 bits of the UUIDv7 identifier.
    """
    parsed = parse_prefixed_uuid7(prefixed_id, prefix)
    timestamp_ms = (parsed.int >> 80) & ((1 << 48) - 1)
    return datetime.fromtimestamp(timestamp_ms / 1000.0, tz=UTC)


class ExecutionRecordFactory(ModelFactory[ExecutionRecord]):
    """Polyfactory model factory for ExecutionRecord persistent execution records."""

    __model__ = ExecutionRecord
    __set_as_default_factory_for_type__ = True

    target_locale: str = "en"
    status: ExecutionStatus = ExecutionStatus.PENDING
    workflow_version: int = 1
    organization_id = Use(generate_opaque_id, EntityPrefix.ORGANIZATION)
    output_profile_id: str | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0
    reasoning_tokens: int = 0

    @classmethod
    def created_by(cls) -> str:
        """Generate a valid creator user Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'usr_' prefix.
        """
        return generate_opaque_id(EntityPrefix.USER)

    @classmethod
    def build(cls, factory_use_construct: bool = False, **kwargs: Any) -> ExecutionRecord:
        """Build an ExecutionRecord aligning default created_at with UUIDv7 id timestamp.

        Args:
            factory_use_construct: Whether to bypass Pydantic validation via model_construct.
            **kwargs: Explicit field overrides for the generated ExecutionRecord.

        Returns:
            Validated ExecutionRecord instance.
        """
        if "created_at" not in kwargs:
            resolved_id = kwargs["id"] if "id" in kwargs else None
            if not isinstance(resolved_id, str):
                resolved_id = cls.id()
                kwargs["id"] = resolved_id
            try:
                kwargs["created_at"] = _extract_factory_uuid7_timestamp(resolved_id, EntityPrefix.EXECUTION)
            except AppException, ValueError:
                pass
        return super().build(factory_use_construct=factory_use_construct, **kwargs)

    @classmethod
    def execution_trace(cls) -> list[ErrorTraceEvent | TombstoneEvent | TraceEvent]:
        """Generate an empty execution trace list.

        Returns:
            Empty list of typed execution trace events.
        """
        return []

    @classmethod
    def steps(cls) -> list[ExecutionStep]:
        """Generate an empty execution steps list.

        Returns:
            Empty list of ExecutionStep models.
        """
        return []

    @classmethod
    def profile_syntheses(cls) -> dict[str, RenderedSynthesisCache]:
        """Generate an empty profile syntheses dictionary.

        Returns:
            Empty dictionary mapping profile IDs to RenderedSynthesisCache instances.
        """
        return {}

    @classmethod
    def source_identity_manifest(cls) -> dict[str, str]:
        """Generate an empty source identity manifest dictionary.

        Returns:
            Empty dictionary mapping source IDs to display names.
        """
        return {}

    @classmethod
    def models_used(cls) -> dict[str, int]:
        """Generate an empty models used dictionary.

        Returns:
            Empty dictionary mapping model identifiers to token/call counts.
        """
        return {}

    @classmethod
    def id(cls) -> str:
        """Generate a valid Opaque Stripe ID with 'exe_' prefix.

        Returns:
            Canonical Opaque Stripe ID with 'exe_' prefix.
        """
        return generate_opaque_id(EntityPrefix.EXECUTION)

    @classmethod
    def workflow_id(cls) -> str:
        """Generate an associated workflow ID.

        Returns:
            Canonical Opaque Stripe ID with 'wf_' prefix.
        """
        return generate_opaque_id(EntityPrefix.WORKFLOW)

    @classmethod
    def initiator_id(cls) -> str:
        """Generate a valid initiator user Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'usr_' prefix.
        """
        return generate_opaque_id(EntityPrefix.USER)

    @classmethod
    def raw_inputs(cls) -> WorkflowInputs:
        """Generate a clean workflow inputs container.

        Returns:
            Initialized WorkflowInputs model instance.
        """
        return WorkflowInputs(dynamic_inputs={})

    @classmethod
    def context_variables(cls) -> ContextVariablesDTO:
        """Generate an initialized context variables container.

        Returns:
            ContextVariablesDTO instance with empty variables dictionary.
        """
        return ContextVariablesDTO(variables={})

    @classmethod
    def frozen_context(cls) -> FrozenContext:
        """Generate an empty frozen context manifest.

        Returns:
            Initialized FrozenContext model instance.
        """
        return FrozenContext(
            compiled_prompts={},
            injected_theory=InjectedTheoryManifestDTO(theories={}),
            generated_schemas=GeneratedSchemaManifestDTO(schemas={}),
            ui_hints_snapshot={},
            mcp_tool_audit=[],
        )


class ReportArtifactFactory(ModelFactory[ReportArtifact]):
    """Polyfactory model factory for ReportArtifact materialized report models."""

    __model__ = ReportArtifact
    __set_as_default_factory_for_type__ = True

    locale: str = "en"
    title: str = "Test Report Artifact"
    status: ReportStatus = ReportStatus.READY
    custom_preface_md: str | None = None
    error_message: str | None = None

    @classmethod
    def build(cls, factory_use_construct: bool = False, **kwargs: Any) -> ReportArtifact:
        """Build a ReportArtifact aligning default created_at with UUIDv7 id timestamp.

        Args:
            factory_use_construct: Whether to bypass Pydantic validation via model_construct.
            **kwargs: Explicit field overrides for the generated ReportArtifact.

        Returns:
            Validated ReportArtifact instance.
        """
        if "created_at" not in kwargs:
            resolved_id = kwargs["id"] if "id" in kwargs else None
            if not isinstance(resolved_id, str):
                resolved_id = cls.id()
                kwargs["id"] = resolved_id
            try:
                kwargs["created_at"] = _extract_factory_uuid7_timestamp(resolved_id, EntityPrefix.REPORT)
            except AppException, ValueError:
                pass
        return super().build(factory_use_construct=factory_use_construct, **kwargs)

    @classmethod
    def id(cls) -> str:
        """Generate a valid Opaque Stripe ID with 'rep_' prefix.

        Returns:
            Canonical Opaque Stripe ID with 'rep_' prefix.
        """
        return generate_opaque_id(EntityPrefix.REPORT)

    @classmethod
    def execution_id(cls) -> str:
        """Generate an associated execution Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'exe_' prefix.
        """
        return generate_opaque_id(EntityPrefix.EXECUTION)

    @classmethod
    def workflow_id(cls) -> str:
        """Generate an associated workflow Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'wf_' prefix.
        """
        return generate_opaque_id(EntityPrefix.WORKFLOW)

    @classmethod
    def profile_id(cls) -> str:
        """Generate an associated presentation profile Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'prf_' prefix.
        """
        return generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)

    @classmethod
    def storage_paths(cls) -> ReportStoragePathsDTO:
        """Generate an empty report storage paths container.

        Returns:
            Initialized ReportStoragePathsDTO instance.
        """
        return ReportStoragePathsDTO()

    @classmethod
    def metadata(cls) -> ReportMetadataDTO:
        """Generate an empty report telemetry metadata container.

        Returns:
            Initialized ReportMetadataDTO instance.
        """
        return ReportMetadataDTO()


class StepPanelDTOFactory(ModelFactory[StepPanelDTO]):
    """Polyfactory model factory for StepPanelDTO scoring hook panel outputs."""

    __model__ = StepPanelDTO
    __set_as_default_factory_for_type__ = True

    overseer_data: OverseerData | None = None
    logician_data: LogicianData | None = None
    performativity_analysis: PerformativityAnalysis | None = None
    causal_analysis: CausalAnalysis | None = None

    @classmethod
    def falsifier_data(cls) -> FalsifierData:
        """Generate valid FalsifierData payload satisfying the at-least-one invariant.

        Returns:
            Populated FalsifierData instance with stress test and fidelity audit.
        """
        return FalsifierData(
            stress_test_findings=[
                WaltonStressTest(
                    question="Is the evidence supported?",
                    evidence_held=True,
                    observation="Valid analytical evidence.",
                )
            ],
            fidelity_audit=ReasoningFidelity(
                fidelity_score=FidelityLevel.HIGH,
                fidelity_numeric=2.0,
                abductive_score=2.0,
                plausibility_score=2.0,
                justification="Valid justification adhering to score bounds.",
            ),
        )


class GlobalContextVarsDTOFactory(ModelFactory[GlobalContextVarsDTO]):
    """Polyfactory model factory for GlobalContextVarsDTO hook pipeline variables."""

    __model__ = GlobalContextVarsDTO
    __set_as_default_factory_for_type__ = True

    language: str = "en"
    target_locale: str = "en"
    system_locale: str = "en"
    profile_id: str | None = None
    organization_id: str | None = None
    initiator_id: str | None = None
    step_coach: None = None
    knowledge_base: None = None
    hydration_results: HydrationInputSourceDTO | None = None
    step_linguistics: LinguisticsResultDTO | None = None
    external_evidence: str | None = None
    evaluative_matrices: dict[str, float] | None = None
    passivity_detected: bool = False
    archivist_precedents: list[PrecedentDTO] | None = None
    shuffled_atoms: list[FlattenedAtom] | None = None
    profiler_metrics: ProfilerMetricsDTO | None = None
    distillation: SynthesisDistillationDTO | None = None
    scoring: ScoringResultDTO | TraceScoringPayloadDTO | None = None
    interaction_analysis: InteractionAnalysisDTO | None = None
    bibliography: BibliographyResultDTO | None = None
    llm_anomaly_retry_requested: bool = False
    input_control_ratio: float | None = None
    integrity_verified_output: AnalystOutput | EvaluationResult | None = None
    step_metadata: StepMetadataDTO | None = None


class CausalNodeDTOFactory(ModelFactory[CausalNodeDTO]):
    """Polyfactory model factory for CausalNodeDTO argument nodes."""

    __model__ = CausalNodeDTO
    __set_as_default_factory_for_type__ = True

    claim: str = "Verifiable claim premise."
    source_quotes: tuple[str, ...] | None = ("Verbatim quote.",)
    paragraph_ref: str | None = "B0"
    status: ExecutionStatus = ExecutionStatus.PASSED
    tda_score: float | None = None
    tda_level_key: str | None = None

    @classmethod
    def node_id(cls) -> str:
        """Generate a valid causal node Opaque Stripe ID with 'tda_' prefix.

        Returns:
            Canonical Opaque Stripe ID with 'tda_' prefix.
        """
        return generate_opaque_id(EntityPrefix.TDA)

    @classmethod
    def blame_parent_ids(cls) -> list[str]:
        """Generate an empty blame parent IDs list.

        Returns:
            Empty list of upstream parent node ID strings.
        """
        return []

    @classmethod
    def dependent_child_ids(cls) -> list[str]:
        """Generate an empty dependent child IDs list.

        Returns:
            Empty list of downstream child node ID strings.
        """
        return []


class CausalGraphPayloadDTOFactory(ModelFactory[CausalGraphPayloadDTO]):
    """Polyfactory model factory for CausalGraphPayloadDTO with referential integrity."""

    __model__ = CausalGraphPayloadDTO
    __set_as_default_factory_for_type__ = True

    cycle_detected: bool = False

    @classmethod
    def nodes(cls) -> list[CausalNodeDTO]:
        """Generate valid interconnected argument nodes.

        Returns:
            List of two interconnected CausalNodeDTO instances.
        """
        return [
            CausalNodeDTO(
                node_id="tda_0195f3a0000070008000000000000001",
                claim="Premise claim statement.",
                source_quotes=("Verbatim quote 1.",),
                paragraph_ref="B0",
                status=ExecutionStatus.PASSED,
                blame_parent_ids=[],
                dependent_child_ids=["tda_0195f3a0000070008000000000000002"],
                short_circuited_by_claims=[],
                falsified_warrant_claims=[],
            ),
            CausalNodeDTO(
                node_id="tda_0195f3a0000070008000000000000002",
                claim="Conclusion claim statement.",
                source_quotes=("Verbatim quote 2.",),
                paragraph_ref="B1",
                status=ExecutionStatus.PASSED,
                blame_parent_ids=[],
                dependent_child_ids=[],
                short_circuited_by_claims=[],
                falsified_warrant_claims=[],
            ),
        ]

    @classmethod
    def edges(cls) -> list[CausalEdgeDTO]:
        """Generate directed dependency edges satisfying referential integrity.

        Returns:
            List containing a valid CausalEdgeDTO linking the generated nodes.
        """
        return [
            CausalEdgeDTO(
                source_id="tda_0195f3a0000070008000000000000001",
                target_id="tda_0195f3a0000070008000000000000002",
                reasoning="Logical premise to conclusion dependency.",
            )
        ]

    @classmethod
    def root_cause_node_ids(cls) -> list[str]:
        """Generate an empty root cause node IDs list.

        Returns:
            Empty list of root cause node ID strings.
        """
        return []

    @classmethod
    def isolated_node_ids(cls) -> list[str]:
        """Generate an empty isolated node IDs list.

        Returns:
            Empty list of isolated node ID strings.
        """
        return []

    @classmethod
    def partition_node_ids(cls) -> dict[str, list[str]]:
        """Generate an empty partition node IDs mapping.

        Returns:
            Empty dictionary mapping partition keys to node ID lists.
        """
        return {}

    @classmethod
    def edge_root_causes(cls) -> list[str]:
        """Generate an empty edge root causes list.

        Returns:
            Empty list of serialized edge root cause strings.
        """
        return []


class TenantSecretDTOFactory(ModelFactory[TenantSecretDTO]):
    """Polyfactory model factory for TenantSecretDTO with explicit storage_mode and updated_by."""

    __model__ = TenantSecretDTO
    __set_as_default_factory_for_type__ = True

    scope: SecretScope = SecretScope.LLM_PROVIDER
    target_identifier: str = "google"
    storage_mode: SecretStorageMode = SecretStorageMode.ENVELOPE_KMS
    kek_version: str = "kek-v1"
    masked_hint: str = "...1234"

    @classmethod
    def id(cls) -> str:
        """Generate a valid Tenant Secret Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'sec_' prefix.
        """
        return generate_opaque_id(EntityPrefix.TENANT_SECRET)

    @classmethod
    def organization_id(cls) -> str:
        """Generate a valid Organization Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'org_' prefix.
        """
        return generate_opaque_id(EntityPrefix.ORGANIZATION)

    @classmethod
    def updated_by(cls) -> str:
        """Generate a valid User Opaque Stripe ID for updated_by.

        Returns:
            Canonical Opaque Stripe ID with 'usr_' prefix.
        """
        return generate_opaque_id(EntityPrefix.USER)


class ReportViewFactory(ModelFactory[ReportView]):
    """Polyfactory model factory for ReportView with explicit title."""

    __model__ = ReportView
    __set_as_default_factory_for_type__ = True

    title: str = "Audit Report"
    status_theme: VisualIntent = VisualIntent.SUCCESS

    @classmethod
    def view_id(cls) -> str:
        """Generate a valid Execution Opaque Stripe ID for view_id.

        Returns:
            Canonical Opaque Stripe ID with 'exe_' prefix.
        """
        return generate_opaque_id(EntityPrefix.EXECUTION)

    @classmethod
    def inner_sdui_blocks(cls) -> list[AnySduiBlock]:
        """Generate an empty inner SDUI blocks list.

        Returns:
            Empty list of AnySduiBlock instances.
        """
        return []


class AuditLogRecordFactory(ModelFactory[AuditLogRecord]):
    """Polyfactory model factory for immutable AuditLogRecord compliance entries."""

    __model__ = AuditLogRecord
    __set_as_default_factory_for_type__ = True

    event_type: str = "EXECUTION_STARTED"
    resource_type: str = "execution"
    resource_id: str = "exe_0195f3a0000070008000000000000001"

    @classmethod
    def id(cls) -> str:
        """Generate a valid AuditLogRecord Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'aud_' prefix.
        """
        return generate_opaque_id(EntityPrefix.AUDIT_LOG)

    @classmethod
    def organization_id(cls) -> str:
        """Generate a valid Organization Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'org_' prefix.
        """
        return generate_opaque_id(EntityPrefix.ORGANIZATION)

    @classmethod
    def actor_id(cls) -> str:
        """Generate a valid User Opaque Stripe ID for actor_id.

        Returns:
            Canonical Opaque Stripe ID with 'usr_' prefix.
        """
        return generate_opaque_id(EntityPrefix.USER)

    @classmethod
    def execution_id(cls) -> str:
        """Generate a valid Execution Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'exe_' prefix.
        """
        return generate_opaque_id(EntityPrefix.EXECUTION)

    @classmethod
    def details(cls) -> dict[str, str | int | float | bool | list[str]]:
        """Generate typed scalar audit details metadata.

        Returns:
            Typed scalar audit metadata dictionary.
        """
        return {"source": "unit_test"}


class UsageRecordFactory(ModelFactory[UsageRecord]):
    """Polyfactory model factory for immutable FinOps UsageRecord entries."""

    __model__ = UsageRecord
    __set_as_default_factory_for_type__ = True

    model: str = "gemini-2.5-pro"
    input_tokens: int = 1200
    output_tokens: int = 450
    cached_tokens: int = 300
    cache_creation_input_tokens: int = 100
    reasoning_tokens: int = 50
    latency_ms: int = 420
    finish_reason: str = "stop"
    system_fingerprint: str = "fp_quorum_v2"
    cost_usd: float = 0.05
    estimated_savings_usd: float = 0.01

    @classmethod
    def id(cls) -> str:
        """Generate a valid UsageRecord Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'usg_' prefix.
        """
        return generate_opaque_id(EntityPrefix.USAGE_RECORD)

    @classmethod
    def org_id(cls) -> str:
        """Generate a valid Organization Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'org_' prefix.
        """
        return generate_opaque_id(EntityPrefix.ORGANIZATION)

    @classmethod
    def user_id(cls) -> str:
        """Generate a valid User Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'usr_' prefix.
        """
        return generate_opaque_id(EntityPrefix.USER)

    @classmethod
    def execution_id(cls) -> str:
        """Generate a valid Execution Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'exe_' prefix.
        """
        return generate_opaque_id(EntityPrefix.EXECUTION)


class ModelProfileFactory(ModelFactory[ModelProfile]):
    """Polyfactory model factory for ModelProfile configurations."""

    __model__ = ModelProfile
    __set_as_default_factory_for_type__ = True

    provider: str = LLMProvider.AI_STUDIO.value
    model_name: str = "gemini-2.5-flash"
    temperature: float | None = 0.0
    top_p: float | None = None
    top_k: int | None = None
    tpm_limit: int | None = 1000000
    rpm_limit: int | None = 60
    max_tokens: int | None = 8192
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    supports_grounding: bool = False
    caching_strategy: str | None = None
    thinking_budget_tokens: int | None = None
    is_active: bool = True

    @classmethod
    def allowed_tools(cls) -> list[str]:
        """Generate an empty enabled tools list.

        Returns:
            Empty list of tool identifiers.
        """
        return []

    @classmethod
    def additional_params(cls) -> ProviderExtraParamsDTO:
        """Generate default provider extra parameters.

        Returns:
            ProviderExtraParamsDTO instance with default None overrides.
        """
        return ProviderExtraParamsDTO()


class SystemConfigModelRegistryFactory(ModelFactory[SystemConfigModelRegistry]):
    """Polyfactory model factory for SystemConfigModelRegistry domain models."""

    __model__ = SystemConfigModelRegistry
    __set_as_default_factory_for_type__ = True

    name: str = "Test Model Registry"
    default_provider: LLMProvider = LLMProvider.AI_STUDIO

    @classmethod
    def id(cls) -> str:
        """Generate a valid Model Registry Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'mrg_' prefix.
        """
        return generate_opaque_id(EntityPrefix.MODEL_REGISTRY)

    @classmethod
    def slug(cls) -> str:
        """Generate a unique model registry slug.

        Returns:
            Unique model registry slug string.
        """
        return f"mrg_slug_{generate_uuid7().hex[:8]}"

    @classmethod
    def tier_definitions(cls) -> dict[CognitiveTier, ModelProfile]:
        """Generate all four required CognitiveTier profiles.

        Returns:
            Mapping covering FAST, BALANCED, DEEP, and REASONING tiers.
        """
        return {
            CognitiveTier.FAST: ModelProfileFactory.build(model_name="gemini-2.5-flash"),
            CognitiveTier.BALANCED: ModelProfileFactory.build(model_name="gemini-2.5-pro"),
            CognitiveTier.DEEP: ModelProfileFactory.build(model_name="gemini-2.5-pro"),
            CognitiveTier.REASONING: ModelProfileFactory.build(model_name="gemini-2.5-pro"),
        }


class SystemConfigMCPGatewaysFactory(ModelFactory[SystemConfigMCPGateways]):
    """Polyfactory model factory for SystemConfigMCPGateways domain models."""

    __model__ = SystemConfigMCPGateways
    __set_as_default_factory_for_type__ = True

    name: str = "Test MCP Gateway"
    endpoint_url: str = "https://mcp.example.com/mcp"
    transport_type: MCPTransportType = MCPTransportType.STREAMABLE_HTTP
    auth_type: MCPAuthType = MCPAuthType.BEARER
    auth_header_name: str | None = None
    auth_env_var: str | None = None
    timeout_seconds: int = 30

    @classmethod
    def id(cls) -> str:
        """Generate a valid MCP Gateway Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'mcp_' prefix.
        """
        return generate_opaque_id(EntityPrefix.MCP_GATEWAY)

    @classmethod
    def organization_id(cls) -> str:
        """Generate a valid Organization Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'org_' prefix.
        """
        return generate_opaque_id(EntityPrefix.ORGANIZATION)

    @classmethod
    def slug(cls) -> str:
        """Generate a collision-free MCP gateway slug without double underscores.

        Returns:
            Valid MCP gateway slug matching single-underscore pattern.
        """
        return f"mcp_gw_{generate_uuid7().hex[:8]}"

    @classmethod
    def tools(cls) -> list[AllowedMCPTool]:
        """Generate an empty MCP tools registry list.

        Returns:
            Empty list of AllowedMCPTool models.
        """
        return []


class MCPAuditTraceFactory(ModelFactory[MCPAuditTrace]):
    """Polyfactory model factory for MCPAuditTrace domain models."""

    __model__ = MCPAuditTrace
    __set_as_default_factory_for_type__ = True

    id: str | None = None
    tool_id: str = "tavily_search"
    gateway_slug: str | None = "default_mcp_gateway"
    namespaced_alias: str | None = "default_mcp_gateway__tavily_search"
    step_name: str = "step_analyst"
    claim_text: str | None = "Test claim text"
    query: str = "test search query"
    knowledge_gap: str = "Verify test claim"
    search_rationale: str = "Ground claim in external evidence"
    reasoning: str = "Verification check"
    response_summary: str = "Verified result summary"
    duration_ms: int = 120

    @classmethod
    def gateway_id(cls) -> str:
        """Generate a valid MCP Gateway Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'mcp_' prefix.
        """
        return generate_opaque_id(EntityPrefix.MCP_GATEWAY)

    @classmethod
    def source_urls(cls) -> list[str]:
        """Generate sample verified source URLs.

        Returns:
            List of HTTPS source URL strings.
        """
        return ["https://example.com/evidence"]

    @classmethod
    def impacted_axis_names(cls) -> list[str]:
        """Generate sample impacted matrix axis names.

        Returns:
            List of matrix axis name strings.
        """
        return ["Strategic Alignment"]


class LLMProviderConfigFactory(ModelFactory[LLMProviderConfig]):
    """Polyfactory model factory for LLMProviderConfig DTOs."""

    __model__ = LLMProviderConfig
    __set_as_default_factory_for_type__ = True

    provider: str = LLMProvider.AI_STUDIO.value
    model_name: str = "gemini-2.5-flash"
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0.2
    top_p: float | None = 0.95
    top_k: int | None = 40
    tpm_limit: int = 1000000
    rpm_limit: int = 60
    default_max_tokens: int | None = 8192
    frequency_penalty: float | None = 0.0
    presence_penalty: float | None = 0.0
    caching_strategy: str | None = None
    vertex_location: str | None = None
    supports_grounding: bool = False
    is_active: bool = True

    @classmethod
    def id(cls) -> str:
        """Generate a valid provider configuration Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'mrg_' prefix.
        """
        return generate_opaque_id(EntityPrefix.MODEL_REGISTRY)

    @classmethod
    def additional_params(cls) -> ProviderExtraParamsDTO:
        """Generate default provider extra parameters.

        Returns:
            ProviderExtraParamsDTO instance with default None overrides.
        """
        return ProviderExtraParamsDTO()


class TraceEventFactory:
    """Deterministic builder for TraceEvent avoiding Polyfactory recursion on recursive JsonValue."""

    @classmethod
    def build(
        cls,
        *,
        event_id: uuid.UUID | None = None,
        v: int = 1,
        timestamp: datetime | None = None,
        step_name: str = "step_test",
        event_type: Literal[
            "input",
            "reasoning",
            "decision",
            "error",
            "output",
            "tombstone",
            "evidence_override",
            "progress",
        ] = "output",
        content: EvidenceOverrideDTO
        | StepPayloadValue
        | DomainInputValue
        | StepOutputContentDTO
        | Mapping[str, StepOutputContentValue]
        | BaseModel
        | None = None,
        reasoning: ReasoningTrace | None = None,
        metadata: TraceEventMetadataDTO | None = None,
        mcp_audit_traces: list[MCPAuditTrace] | None = None,
    ) -> TraceEvent:
        """Construct a validated TraceEvent instance with deterministic defaults.

        Args:
            event_id: Explicit UUIDv7 event identifier override.
            v: Trace event schema version.
            timestamp: Explicit UTC timestamp override.
            step_name: Originating step identifier.
            event_type: Trace event discriminator literal.
            content: Typed trace payload content.
            reasoning: Associated reasoning trace.
            metadata: Trace event metadata container.
            mcp_audit_traces: Associated MCP tool audit traces.

        Returns:
            Validated TraceEvent domain model instance.
        """
        return TraceEvent(
            event_id=event_id if event_id is not None else generate_uuid7(),
            v=v,
            timestamp=timestamp if timestamp is not None else datetime.now(UTC),
            step_name=step_name,
            event_type=event_type,
            content=content,
            reasoning=reasoning,
            metadata=metadata if metadata is not None else TraceEventMetadataDTO(mcp_audit_traces=[]),
            mcp_audit_traces=mcp_audit_traces if mcp_audit_traces is not None else [],
        )


class ErrorTraceEventFactory:
    """Deterministic builder for ErrorTraceEvent avoiding Polyfactory recursion on recursive JsonValue."""

    @classmethod
    def build(
        cls,
        *,
        event_id: uuid.UUID | None = None,
        v: int = 1,
        timestamp: datetime | None = None,
        step_name: str = "step_test",
        event_type: Literal["error"] = "error",
        error_code: str = "EXECUTION_ERROR",
        error_message: str = "Test execution error",
        content: EvidenceOverrideDTO
        | StepPayloadValue
        | DomainInputValue
        | StepOutputContentDTO
        | Mapping[str, StepOutputContentValue]
        | BaseModel
        | None = None,
        reasoning: ReasoningTrace | None = None,
        metadata: TraceEventMetadataDTO | None = None,
        mcp_audit_traces: list[MCPAuditTrace] | None = None,
    ) -> ErrorTraceEvent:
        """Construct a validated ErrorTraceEvent instance with deterministic defaults.

        Args:
            event_id: Explicit UUIDv7 event identifier override.
            v: Trace event schema version.
            timestamp: Explicit UTC timestamp override.
            step_name: Originating step identifier.
            event_type: Constant 'error' event discriminator.
            error_code: Standard ErrorCodes value string.
            error_message: Human-readable error message.
            content: Optional typed error payload content.
            reasoning: Optional associated reasoning trace.
            metadata: Trace event metadata container.
            mcp_audit_traces: Associated MCP tool audit traces.

        Returns:
            Validated ErrorTraceEvent domain model instance.
        """
        return ErrorTraceEvent(
            event_id=event_id if event_id is not None else generate_uuid7(),
            v=v,
            timestamp=timestamp if timestamp is not None else datetime.now(UTC),
            step_name=step_name,
            event_type=event_type,
            error_code=error_code,
            error_message=error_message,
            content=content,
            reasoning=reasoning,
            metadata=metadata if metadata is not None else TraceEventMetadataDTO(mcp_audit_traces=[]),
            mcp_audit_traces=mcp_audit_traces if mcp_audit_traces is not None else [],
        )
