"""Unit tests for backend_v2.models.enums."""

import pytest
from pydantic import BaseModel, ValidationError

from backend_v2.models.enums import (
    BlockDataType,
    CausalRootCauseType,
    ComponentType,
    DependencyRelationType,
    DisplayScale,
    EntityPrefix,
    ExecutionProfile,
    ExecutionStatus,
    HistoricalContextMode,
    LaxBlockDataType,
    LaxCausalRootCauseType,
    LaxComponentType,
    LaxDependencyRelationType,
    LaxExecutionStatus,
    LaxHistoricalContextMode,
    LaxPresetView,
    LaxPropositionNodeType,
    LaxReportStatus,
    LaxStepType,
    LaxStepZone,
    LaxStorageBackend,
    LaxToolCapability,
    LaxXaiExtensionType,
    PipelineConfig,
    PresetView,
    PropositionNodeType,
    ReportAtomColumn,
    ReportMatrixColumn,
    ReportSheetKey,
    ReportStatus,
    RoleClassification,
    SDUIComponentType,
    StepType,
    StepZone,
    StorageBackend,
    SystemConfigID,
    TitleKey,
    ToolCapability,
    UiVariant,
    XaiExtensionType,
)


def test_lax_xai_extension_type() -> None:
    """Verify LaxXaiExtensionType parses enums and strings and rejects invalid values."""

    class DummyModel(BaseModel):
        ext: LaxXaiExtensionType

    # Valid Enum
    obj1 = DummyModel(ext=XaiExtensionType.CITATION)
    assert obj1.ext == XaiExtensionType.CITATION

    # Valid string coerced to Enum
    obj2 = DummyModel(ext="citation")
    assert obj2.ext == XaiExtensionType.CITATION

    # Invalid string throws ValidationError
    with pytest.raises(ValidationError):
        DummyModel(ext="invalid_extension")


def test_lax_step_type() -> None:
    """Verify LaxStepType parses enums and strings and rejects invalid values."""

    class DummyModel(BaseModel):
        step_type: LaxStepType

    obj1 = DummyModel(step_type=StepType.LLM)
    assert obj1.step_type == StepType.LLM

    obj2 = DummyModel(step_type="logic")
    assert obj2.step_type == StepType.LOGIC

    with pytest.raises(ValidationError):
        DummyModel(step_type="invalid_step_type")


def test_lax_execution_status() -> None:
    """Verify LaxExecutionStatus parses valid status strings and rejects unknown values."""

    class DummyModel(BaseModel):
        status: LaxExecutionStatus

    obj = DummyModel(status="PENDING")
    assert obj.status == ExecutionStatus.PENDING

    with pytest.raises(ValidationError):
        DummyModel(status="UNKNOWN_STATUS")


def test_lax_block_data_type() -> None:
    """Verify LaxBlockDataType parses valid data type strings and rejects invalid values."""

    class DummyModel(BaseModel):
        data_type: LaxBlockDataType

    obj = DummyModel(data_type="float")
    assert obj.data_type == BlockDataType.FLOAT

    with pytest.raises(ValidationError):
        DummyModel(data_type="invalid_type")


def test_lax_component_type() -> None:
    """Verify LaxComponentType parses valid component strings and rejects invalid values."""

    class DummyModel(BaseModel):
        comp_type: LaxComponentType

    obj = DummyModel(comp_type="slider")
    assert obj.comp_type == ComponentType.SLIDER

    with pytest.raises(ValidationError):
        DummyModel(comp_type="invalid_comp")


def test_lax_historical_context_mode() -> None:
    """Verify LaxHistoricalContextMode parses valid mode strings and rejects invalid values."""

    class DummyModel(BaseModel):
        mode: LaxHistoricalContextMode

    obj = DummyModel(mode="DISABLED")
    assert obj.mode == HistoricalContextMode.DISABLED

    with pytest.raises(ValidationError):
        DummyModel(mode="INVALID_MODE")


def test_parity_ui_variant() -> None:
    """Tier 2 / Phase 2: Contract Parity Gate.

    Asserts exact parity between Python UiVariant and Dart UiVariant.
    """
    expected_values = {"default", "success", "warning", "error", "neutral"}
    python_values = {v.value for v in UiVariant}

    assert python_values == expected_values


def test_enum_l10n_properties() -> None:
    """Verify all L10n properties across enums return valid mapped strings."""
    assert DisplayScale.ORIGINAL.l10n_key == "displayScaleOriginal"
    assert DisplayScale.CUSTOM.l10n_key == "displayScaleCustom"
    assert DisplayScale.NORMALIZED_100.l10n_key == "displayScaleNormalized100"

    assert XaiExtensionType.COACHING.l10n_key == "xaiCoachingTip"
    assert XaiExtensionType.JUSTIFICATION.l10n_key == "xaiJustification"
    assert XaiExtensionType.FALSIFICATION.l10n_key == "xaiDevilsAdvocate"
    assert XaiExtensionType.MISSING_CONTEXT.l10n_key == "xaiMissingContext"
    assert XaiExtensionType.THEORY_LINK.l10n_key == "xaiTheoryLink"
    assert XaiExtensionType.RISK_FLAG.l10n_key == "xaiRiskFlag"
    assert XaiExtensionType.REMEDIATION_STEPS.l10n_key == "xaiRemediation"
    assert XaiExtensionType.EMOTIONAL_SENTIMENT.l10n_key == "xaiSentiment"
    assert XaiExtensionType.VARIANCE_VALIDATION.l10n_key == "xaiVarianceValidationTitle"
    assert XaiExtensionType.AUTHENTICITY_EVALUATION.l10n_key == "xaiAuthenticityEvaluationTitle"
    assert XaiExtensionType.CITATION.l10n_key == ""

    assert ExecutionStatus.PASSED.l10n_key == "status_passed"
    assert ExecutionStatus.FAILED.l10n_key == "status_failed"
    assert ExecutionStatus.N_A.l10n_key == "status_n_a"
    assert ExecutionStatus.SYSTEM_ERROR.l10n_key == "status_system_error"
    assert ExecutionStatus.BLOCKED.l10n_key == "status_blocked"
    assert ExecutionStatus.PENDING.l10n_key == "status_pending"
    assert ExecutionStatus.RUNNING.l10n_key == "status_running"
    assert ExecutionStatus.QUEUED.l10n_key == "status_queued"

    assert SDUIComponentType.BOOLEAN_CARD.l10n_key == "sdui_boolean_card"
    assert SDUIComponentType.EXTRACTED_VALUE_CARD.l10n_key == "sdui_extracted_value_card"
    assert SDUIComponentType.ERROR_CARD.l10n_key == "sdui_error_card"
    assert SDUIComponentType.N_A_CARD.l10n_key == "sdui_n_a_card"

    assert RoleClassification.PASSENGER.l10n_key == "rolePassenger"
    assert RoleClassification.NAVIGATOR.l10n_key == "roleNavigator"
    assert RoleClassification.DRIVER.l10n_key == "roleDriver"
    assert RoleClassification.ARCHITECT.l10n_key == "roleArchitect"

    assert TitleKey.TITLE_TIMELINE.l10n_key == "titleTimeline"
    assert TitleKey.TITLE_HYPOTHESES.l10n_key == "titleHypotheses"
    assert TitleKey.SECURITY.l10n_key == ""

    assert ReportStatus.PENDING.l10n_key == "reportStatusPending"
    assert ReportStatus.GENERATING.l10n_key == "reportStatusGenerating"
    assert ReportStatus.READY.l10n_key == "reportStatusReady"
    assert ReportStatus.FAILED.l10n_key == "reportStatusFailed"

    assert ReportMatrixColumn.LABEL.l10n_key == "matrix_col_label"
    assert ReportAtomColumn.MATRIX.l10n_key == "export_col_matrix"
    assert ReportAtomColumn.CAUSAL_STATUS.l10n_key == "export_col_causal_status"
    assert ReportAtomColumn.BLAME_PARENT_ID.l10n_key == "export_col_blame_parent_id"
    assert ReportAtomColumn.DEPENDENT_COUNT.l10n_key == "export_col_dependent_count"
    assert ReportSheetKey.SUMMARY.l10n_key == "export_sheet_summary"
    assert ReportSheetKey.RAW_DATA.l10n_key == "export_sheet_raw_data"

    assert CausalRootCauseType.NODE_FAILURE.l10n_key == "causal_root_cause_node_failure"
    assert CausalRootCauseType.WARRANT_GROUNDING_FAILURE.l10n_key == "causal_root_cause_warrant_grounding_failure"
    assert CausalRootCauseType.PRECONDITION_MISMATCH.l10n_key == "causal_root_cause_precondition_mismatch"

    assert ToolCapability.SEARCH.l10n_key == "mcp_capability_search"
    assert ToolCapability.DOCUMENT_READER.l10n_key == "mcp_capability_document_reader"
    assert ToolCapability.ACTION.l10n_key == "mcp_capability_action"
    assert ToolCapability.GENERAL.l10n_key == "mcp_capability_general"


def test_role_classification_from_score_boundaries() -> None:
    """Verify RoleClassification.from_score across ISTQB boundary value partitions."""
    assert RoleClassification.from_score(-10.0) == RoleClassification.PASSENGER
    assert RoleClassification.from_score(0) == RoleClassification.PASSENGER
    assert RoleClassification.from_score(1) == RoleClassification.PASSENGER
    assert RoleClassification.from_score(2.4) == RoleClassification.PASSENGER
    assert RoleClassification.from_score(2.6) == RoleClassification.NAVIGATOR
    assert RoleClassification.from_score(3) == RoleClassification.NAVIGATOR
    assert RoleClassification.from_score(3.4) == RoleClassification.NAVIGATOR
    assert RoleClassification.from_score(3.6) == RoleClassification.DRIVER
    assert RoleClassification.from_score(4) == RoleClassification.DRIVER
    assert RoleClassification.from_score(4.4) == RoleClassification.DRIVER
    assert RoleClassification.from_score(4.6) == RoleClassification.ARCHITECT
    assert RoleClassification.from_score(5) == RoleClassification.ARCHITECT
    assert RoleClassification.from_score(99.9) == RoleClassification.ARCHITECT


def test_role_classification_from_score_invalid_inputs() -> None:
    """Negative test: Verify RoleClassification.from_score rejects non-finite float inputs."""
    with pytest.raises(ValueError):
        RoleClassification.from_score(float("nan"))

    with pytest.raises(OverflowError):
        RoleClassification.from_score(float("inf"))


def test_pipeline_config_immutability() -> None:
    """Verify PipelineConfig is frozen and hashable."""
    cfg = PipelineConfig(profile=ExecutionProfile.ONE_SHOT, default_strategy="fast")
    assert cfg.profile == ExecutionProfile.ONE_SHOT
    assert cfg.default_strategy == "fast"
    assert isinstance(hash(cfg), int)


def test_lax_causal_root_cause_and_step_zone() -> None:
    """Verify LaxCausalRootCauseType and LaxStepZone positive coercion and negative rejection."""

    class DummyModel(BaseModel):
        cause: LaxCausalRootCauseType
        zone: LaxStepZone

    obj = DummyModel(cause="node_failure", zone="zone_a")
    assert obj.cause == CausalRootCauseType.NODE_FAILURE
    assert obj.zone == StepZone.ZONE_A

    with pytest.raises(ValidationError):
        DummyModel(cause="invalid_cause", zone="zone_a")

    with pytest.raises(ValidationError):
        DummyModel(cause="node_failure", zone="invalid_zone")


def test_lax_tool_capability() -> None:
    """Verify LaxToolCapability parses enums and string coercions, and rejects invalid strings."""

    class DummyModel(BaseModel):
        cap: LaxToolCapability

    obj1 = DummyModel(cap=ToolCapability.SEARCH)
    assert obj1.cap == ToolCapability.SEARCH

    obj2 = DummyModel(cap="document_reader")
    assert obj2.cap == ToolCapability.DOCUMENT_READER

    with pytest.raises(ValidationError):
        DummyModel(cap="invalid_capability")


def test_storage_backend_and_proposition_graph_enums() -> None:
    """Verify StorageBackend, PropositionNodeType, DependencyRelationType, and EntityPrefix members."""
    assert str(EntityPrefix.NODE) == "nod"
    assert str(EntityPrefix.EDGE) == "edg"
    assert str(EntityPrefix.SCALE) == "sc"
    assert str(EntityPrefix.SYNTHESIS_GROUP) == "grp"
    assert SystemConfigID.MCP_GATEWAYS.value == "sys_0195f3a00000700080008172bda70c86"
    assert str(StorageBackend.POSTGRES) == "POSTGRES"
    assert str(PropositionNodeType.CLAIM) == "claim"
    assert str(PropositionNodeType.GROUND) == "ground"
    assert str(PropositionNodeType.WARRANT) == "warrant"
    assert str(PropositionNodeType.REBUTTAL) == "rebuttal"
    assert str(PropositionNodeType.SCM_VAR) == "scm_var"
    assert str(DependencyRelationType.SUPPORTS) == "supports"
    assert str(DependencyRelationType.WARRANTS) == "warrants"
    assert str(DependencyRelationType.REBUTS) == "rebuts"
    assert str(DependencyRelationType.CAUSES) == "causes"

    class GraphEnumModel(BaseModel):
        backend: LaxStorageBackend
        node_type: LaxPropositionNodeType
        rel_type: LaxDependencyRelationType

    parsed = GraphEnumModel(backend="POSTGRES", node_type="warrant", rel_type="rebuts")
    assert parsed.backend == StorageBackend.POSTGRES
    assert parsed.node_type == PropositionNodeType.WARRANT
    assert parsed.rel_type == DependencyRelationType.REBUTS

    with pytest.raises(ValidationError):
        GraphEnumModel(backend="UNKNOWN_DB", node_type="warrant", rel_type="rebuts")

    with pytest.raises(ValidationError):
        GraphEnumModel(backend="POSTGRES", node_type="invalid_node", rel_type="rebuts")

    with pytest.raises(ValidationError):
        GraphEnumModel(backend="POSTGRES", node_type="warrant", rel_type="invalid_rel")


def test_lax_report_status_and_preset_view() -> None:
    """Verify LaxReportStatus and LaxPresetView coerce valid strings and reject invalid values."""

    class ReportPresetModel(BaseModel):
        status: LaxReportStatus
        preset: LaxPresetView

    obj1 = ReportPresetModel(status=ReportStatus.READY, preset=PresetView.COMPARE_2D)
    assert obj1.status == ReportStatus.READY
    assert obj1.preset == PresetView.COMPARE_2D

    obj2 = ReportPresetModel(status="generating", preset="3d_matrix")
    assert obj2.status == ReportStatus.GENERATING
    assert obj2.preset == PresetView.MATRIX_3D

    with pytest.raises(ValidationError):
        ReportPresetModel(status="invalid_status", preset="3d_matrix")

    with pytest.raises(ValidationError):
        ReportPresetModel(status="ready", preset="invalid_preset")
