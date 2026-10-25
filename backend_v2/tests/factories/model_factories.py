"""Centralized Polyfactory model factories for strict Pydantic V2 models."""

from __future__ import annotations

import uuid
from typing import Any, Literal

from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.models.core_base import I18nText
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
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.matrix import MatrixRow, MatrixScale
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.domain.scoring import StepPanelDTO
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.causal_discovery import (
    CausalEdgeDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
)
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
from backend_v2.models.dtos.schema_manifest import GeneratedSchemaManifestDTO
from backend_v2.models.dtos.theory_manifest import InjectedTheoryManifestDTO
from backend_v2.models.enums import (
    BlockDataType,
    DisplayScale,
    ExecutionStatus,
    FidelityLevel,
    PromptBlockCategory,
    TargetBlockType,
)

__all__ = [
    "CausalGraphPayloadDTOFactory",
    "CausalNodeDTOFactory",
    "ExecutionRecordFactory",
    "ExecutionStepFactory",
    "GlobalContextVarsDTOFactory",
    "I18nTextFactory",
    "MatrixPromptBlockFactory",
    "OutputProfileFactory",
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
        """Generates standard English and Finnish test translations."""
        return {"en": "English test text", "fi": "Finnish test text"}


class WorkflowFactory(ModelFactory[Workflow]):
    """Polyfactory model factory for DAG Workflow orchestrator models."""

    __model__ = Workflow
    __set_as_default_factory_for_type__ = True

    status: str = "draft"
    version: int = 1
    is_public: bool = False
    organization_id: str | None = "org_testorg123"
    historical_context_mode: Literal["DISABLED"] = "DISABLED"

    @classmethod
    def expected_inputs(cls) -> list[Any]:
        """Generates an empty expected inputs list."""
        return []

    @classmethod
    def steps(cls) -> list[Any]:
        """Generates an empty workflow steps list."""
        return []

    @classmethod
    def id(cls) -> str:
        """Generates a valid Opaque Stripe ID with 'wf_' prefix."""
        return f"wf_{uuid.uuid4().hex[:16]}"

    @classmethod
    def slug(cls) -> str:
        """Generates a unique test slug."""
        return f"wf_slug_{uuid.uuid4().hex[:8]}"

    @classmethod
    def name(cls) -> I18nText:
        """Generates a localized name."""
        return I18nText(translations={"en": "Test Workflow", "fi": "Testi Työnkulku"})

    @classmethod
    def description(cls) -> I18nText:
        """Generates a localized description."""
        return I18nText(translations={"en": "Test Workflow Description", "fi": "Testi Työnkulun Kuvaus"})

    @classmethod
    def default_profile_id(cls) -> str:
        """Generates a valid default profile Opaque Stripe ID."""
        return f"prof_{uuid.uuid4().hex[:16]}"


class SystemRulePromptBlockFactory(ModelFactory[SystemRulePromptBlock]):
    """Polyfactory model factory for SystemRulePromptBlock domain models."""

    __model__ = SystemRulePromptBlock
    __set_as_default_factory_for_type__ = True

    category_id: PromptBlockCategory = PromptBlockCategory.SYSTEM_RULE
    type: BlockDataType = BlockDataType.INSTRUCTION
    is_evaluative: bool = False
    allow_decimals: bool = False
    is_lightweight_protocol: bool = False
    organization_id: str | None = "org_testorg123"
    instruction_text: str | None = "System instruction text for test execution."

    @classmethod
    def output_extensions(cls) -> list[str]:
        """Generates an empty output extensions list."""
        return []

    @classmethod
    def id(cls) -> str:
        """Generates a valid Opaque Stripe ID with 'blk_' prefix."""
        return f"blk_{uuid.uuid4().hex[:16]}"

    @classmethod
    def slug(cls) -> str:
        """Generates a unique block slug."""
        return f"blk_slug_{uuid.uuid4().hex[:8]}"

    @classmethod
    def label(cls) -> I18nText:
        """Generates a localized label."""
        return I18nText(translations={"en": "Test Block Label", "fi": "Testilohkon Nimike"})

    @classmethod
    def description(cls) -> I18nText:
        """Generates a localized description."""
        return I18nText(translations={"en": "Test Block Description", "fi": "Testilohkon Kuvaus"})


class OutputProfileFactory(ModelFactory[OutputProfile]):
    """Polyfactory model factory for OutputProfile presentation configuration models."""

    __model__ = OutputProfile
    __set_as_default_factory_for_type__ = True

    organization_id: str | None = "org_testorg123"
    display_scale: DisplayScale = DisplayScale.ORIGINAL

    @classmethod
    def target_block_order(cls) -> list[TargetBlockType]:
        """Generates standard target block ordering."""
        return [
            TargetBlockType.METADATA_BLOCK,
            TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
            TargetBlockType.SYNTHESIS_TEXT_BLOCK,
        ]

    @classmethod
    def matrix_synthesis_groups(cls) -> list[MatrixSynthesisGroup]:
        """Generates an empty matrix synthesis groups list."""
        return []

    @classmethod
    def metadata_visible_fields(cls) -> list[str]:
        """Generates standard metadata visible fields."""
        return ["date", "organization", "user", "scoring_engine", "strictness"]

    @classmethod
    def matrix_visible_columns(cls) -> list[str]:
        """Generates standard matrix visible columns."""
        return [
            "label",
            "distribution",
            "row_explanation",
            "normalized_score",
            "raw_score",
        ]

    @classmethod
    def id(cls) -> str:
        """Generates a valid Opaque Stripe ID with 'prof_' prefix."""
        return f"prof_{uuid.uuid4().hex[:16]}"

    @classmethod
    def slug(cls) -> str:
        """Generates a unique profile slug."""
        return f"prof_slug_{uuid.uuid4().hex[:8]}"

    @classmethod
    def workflow_id(cls) -> str:
        """Generates an associated workflow Opaque Stripe ID."""
        return f"wf_{uuid.uuid4().hex[:16]}"

    @classmethod
    def name(cls) -> I18nText:
        """Generates a localized name."""
        return I18nText(translations={"en": "Executive Summary Profile", "fi": "Johdon Tiivistelmä"})

    @classmethod
    def description(cls) -> I18nText:
        """Generates a localized description."""
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
    organization_id: str | None = "org_testorg123"
    ai_description: str | None = "Evaluate target dimension against BARS criteria."
    columns: list[I18nText] | None = None

    @classmethod
    def id(cls) -> str:
        """Generates a valid Opaque Stripe ID with 'blk_' prefix."""
        return f"blk_{uuid.uuid4().hex[:16]}"

    @classmethod
    def slug(cls) -> str:
        """Generates a unique block slug."""
        return f"mat_{uuid.uuid4().hex[:8]}"

    @classmethod
    def label(cls) -> I18nText:
        """Generates a localized label."""
        return I18nText(translations={"en": "Test Matrix Block", "fi": "Testimatriisilohko"})

    @classmethod
    def description(cls) -> I18nText:
        """Generates a localized description."""
        return I18nText(translations={"en": "Test Matrix Description", "fi": "Testimatriisin Kuvaus"})

    @classmethod
    def scales(cls) -> list[MatrixScale]:
        """Generates standard BARS scale bounds."""
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
        """Generates target evaluation dimensions."""
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
    def scorecard_atoms(cls) -> dict[str, str]:
        """Generates an empty scorecard atoms mapping."""
        return {}

    @classmethod
    def id(cls) -> str:
        """Generates a valid step identifier."""
        return f"st_{uuid.uuid4().hex[:12]}"


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
    def execution_trace(cls) -> list[Any]:
        """Generates an empty execution trace list."""
        return []

    @classmethod
    def steps(cls) -> list[Any]:
        """Generates an empty steps list."""
        return []

    @classmethod
    def step_states(cls) -> dict[str, str]:
        """Generates an empty step states dictionary."""
        return {}

    @classmethod
    def profile_syntheses(cls) -> dict[str, str]:
        """Generates an empty profile syntheses dictionary."""
        return {}

    @classmethod
    def source_identity_manifest(cls) -> dict[str, str]:
        """Generates an empty source identity manifest dictionary."""
        return {}

    @classmethod
    def models_used(cls) -> dict[str, str]:
        """Generates an empty models used dictionary."""
        return {}

    @classmethod
    def id(cls) -> str:
        """Generates a valid Opaque Stripe ID with 'exec_' prefix."""
        return f"exec_{uuid.uuid4().hex[:16]}"

    @classmethod
    def workflow_id(cls) -> str:
        """Generates an associated workflow ID."""
        return f"wf_{uuid.uuid4().hex[:16]}"

    @classmethod
    def raw_inputs(cls) -> WorkflowInputs:
        """Generates clean workflow inputs container."""
        return WorkflowInputs()

    @classmethod
    def context_variables(cls) -> ContextVariablesDTO:
        """Generates initialized context variables container."""
        return ContextVariablesDTO(variables={})

    @classmethod
    def frozen_context(cls) -> FrozenContext:
        """Generates empty frozen context manifest."""
        return FrozenContext(
            compiled_prompts={},
            injected_theory=InjectedTheoryManifestDTO(),
            generated_schemas=GeneratedSchemaManifestDTO(),
            ui_hints_snapshot={},
            mcp_tool_audit=[],
        )


class StepPanelDTOFactory(ModelFactory[StepPanelDTO]):
    __model__ = StepPanelDTO
    __set_as_default_factory_for_type__ = True

    overseer_data: Any = None
    logician_data: Any = None
    performativity_analysis: Any = None
    causal_analysis: Any = None

    @classmethod
    def falsifier_data(cls) -> FalsifierData:
        """Generates valid FalsifierData payload satisfying at-least-one invariant."""
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
    step_coach: Any = None
    knowledge_base: Any = None
    hydration_results: Any = None
    step_linguistics: Any = None
    external_evidence: Any = None
    evaluative_matrices: Any = None
    passivity_detected: bool = False
    archivist_precedents: Any = None
    shuffled_atoms: Any = None
    profiler_metrics: Any = None
    distillation: Any = None
    scoring: Any = None
    interaction_analysis: Any = None
    bibliography: Any = None
    sanitization: Any = None
    llm_anomaly_retry_requested: bool = False
    input_control_ratio: float | None = None
    integrity_verified_output: Any = None
    step_metadata: Any = None


class CausalNodeDTOFactory(ModelFactory[CausalNodeDTO]):
    """Polyfactory model factory for CausalNodeDTO argument nodes."""

    __model__ = CausalNodeDTO
    __set_as_default_factory_for_type__ = True

    node_id: str = "tda_0000000000000001"
    claim: str = "Verifiable claim premise."
    source_quotes: tuple[str, ...] | None = ("Verbatim quote.",)
    paragraph_ref: str | None = "B0"
    status: ExecutionStatus = ExecutionStatus.PASSED
    tda_score: float | None = None
    tda_level_key: str | None = None

    @classmethod
    def blame_parent_ids(cls) -> list[str]:
        """Generates an empty blame parent IDs list."""
        return []

    @classmethod
    def dependent_child_ids(cls) -> list[str]:
        """Generates an empty dependent child IDs list."""
        return []


class CausalGraphPayloadDTOFactory(ModelFactory[CausalGraphPayloadDTO]):
    """Polyfactory model factory for CausalGraphPayloadDTO with referential integrity."""

    __model__ = CausalGraphPayloadDTO
    __set_as_default_factory_for_type__ = True

    cycle_detected: bool = False

    @classmethod
    def nodes(cls) -> list[CausalNodeDTO]:
        """Generates valid interconnected argument nodes."""
        return [
            CausalNodeDTO(
                node_id="tda_0000000000000001",
                claim="Premise claim statement.",
                source_quotes=("Verbatim quote 1.",),
                paragraph_ref="B0",
                status=ExecutionStatus.PASSED,
                blame_parent_ids=[],
                dependent_child_ids=["tda_0000000000000002"],
            ),
            CausalNodeDTO(
                node_id="tda_0000000000000002",
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
        """Generates directed dependency edges satisfying referential integrity."""
        return [
            CausalEdgeDTO(
                source_id="tda_0000000000000001",
                target_id="tda_0000000000000002",
                reasoning="Logical premise to conclusion dependency.",
            )
        ]

    @classmethod
    def root_cause_node_ids(cls) -> list[str]:
        """Generates an empty root cause node IDs list."""
        return []

    @classmethod
    def isolated_node_ids(cls) -> list[str]:
        """Generates an empty isolated node IDs list."""
        return []
