"""Centralized Polyfactory model factories for strict Pydantic V2 models."""

from __future__ import annotations

from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.models.core_base import I18nText, generate_opaque_id, generate_uuid7
from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.archival import PrecedentDTO
from backend_v2.models.domain.causal import CausalAnalysis
from backend_v2.models.domain.evaluation import EvaluationResult
from backend_v2.models.domain.execution import (
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
from backend_v2.models.domain.inputs import WorkflowInputs
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
from backend_v2.models.domain.step import ExpectedInput, StepRule
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup, RenderedSynthesisCache
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
from backend_v2.models.dtos.report_artifact import (
    ReportMetadataDTO,
    ReportStatus,
    ReportStoragePathsDTO,
)
from backend_v2.models.dtos.schema_manifest import GeneratedSchemaManifestDTO
from backend_v2.models.dtos.synthesis import SynthesisDistillationDTO
from backend_v2.models.dtos.theory_manifest import InjectedTheoryManifestDTO
from backend_v2.models.dtos.trace import TraceScoringPayloadDTO
from backend_v2.models.enums import (
    BlockDataType,
    DisplayScale,
    EntityPrefix,
    ExecutionStatus,
    FidelityLevel,
    HistoricalContextMode,
    PromptBlockCategory,
    TargetBlockType,
    XaiExtensionType,
)
from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent
from backend_v2.models.view.sdui import AnySduiBlock

__all__ = [
    "CausalGraphPayloadDTOFactory",
    "CausalNodeDTOFactory",
    "ExecutionRecordFactory",
    "ExecutionStepFactory",
    "GlobalContextVarsDTOFactory",
    "I18nTextFactory",
    "MatrixPromptBlockFactory",
    "OutputProfileFactory",
    "ReportArtifactFactory",
    "StepPanelDTOFactory",
    "SystemRulePromptBlockFactory",
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
        # Phase 3, Step 3: Use RFC 9562 UUIDv7 hex for unique test slug
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
            Canonical Opaque Stripe ID with 'sys_' prefix.
        """
        return generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)

    @classmethod
    def mcp_gateway_id(cls) -> str:
        """Generate a valid MCP gateway Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'sys_' prefix.
        """
        return generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)


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


class OutputProfileFactory(ModelFactory[OutputProfile]):
    """Polyfactory model factory for OutputProfile presentation configuration models."""

    __model__ = OutputProfile
    __set_as_default_factory_for_type__ = True

    display_scale: DisplayScale = DisplayScale.ORIGINAL

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
            ),
            MatrixScale(
                score=5,
                ai_label="EXCELLENT",
                name=I18nText(translations={"en": "Excellent", "fi": "Erinomainen"}),
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


class ExecutionRecordFactory(ModelFactory[ExecutionRecord]):
    """Polyfactory model factory for ExecutionRecord persistent execution records."""

    __model__ = ExecutionRecord
    __set_as_default_factory_for_type__ = True

    target_locale: str = "en"
    status: ExecutionStatus = ExecutionStatus.PENDING
    workflow_version: int = 1
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0
    reasoning_tokens: int = 0

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
    def step_states(cls) -> dict[str, ExecutionStep]:
        """Generate an empty step states dictionary.

        Returns:
            Empty dictionary mapping step IDs to ExecutionStep instances.
        """
        return {}

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
    def organization_id(cls) -> str:
        """Generate a valid organization Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'org_' prefix.
        """
        return generate_opaque_id(EntityPrefix.ORGANIZATION)

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
        return WorkflowInputs()

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
            injected_theory=InjectedTheoryManifestDTO(),
            generated_schemas=GeneratedSchemaManifestDTO(),
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
            ),
            CausalNodeDTO(
                node_id="tda_0195f3a0000070008000000000000002",
                claim="Conclusion claim statement.",
                source_quotes=("Verbatim quote 2.",),
                paragraph_ref="B1",
                status=ExecutionStatus.PASSED,
                blame_parent_ids=[],
                dependent_child_ids=[],
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
