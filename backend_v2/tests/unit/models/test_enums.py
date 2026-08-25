import pytest
from pydantic import BaseModel, ValidationError

from backend_v2.models.enums import (
    BlockDataType,
    ComponentType,
    DisplayScale,
    ExecutionStatus,
    HistoricalContextMode,
    LaxBlockDataType,
    LaxComponentType,
    LaxExecutionStatus,
    LaxHistoricalContextMode,
    LaxStepType,
    LaxXaiExtensionType,
    RoleClassification,
    ScoringStrategy,
    SDUIComponentType,
    StepType,
    TitleKey,
    UiVariant,
    XaiExtensionType,
)


def test_lax_xai_extension_type() -> None:
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
    class DummyModel(BaseModel):
        step_type: LaxStepType

    obj1 = DummyModel(step_type=StepType.LLM)
    assert obj1.step_type == StepType.LLM

    obj2 = DummyModel(step_type="logic")
    assert obj2.step_type == StepType.LOGIC

    with pytest.raises(ValidationError):
        DummyModel(step_type="invalid_step_type")


def test_lax_execution_status() -> None:
    class DummyModel(BaseModel):
        status: LaxExecutionStatus

    obj = DummyModel(status="PENDING")
    assert obj.status == ExecutionStatus.PENDING

    with pytest.raises(ValidationError):
        DummyModel(status="UNKNOWN_STATUS")


def test_lax_block_data_type() -> None:
    class DummyModel(BaseModel):
        data_type: LaxBlockDataType

    obj = DummyModel(data_type="float")
    assert obj.data_type == BlockDataType.FLOAT

    with pytest.raises(ValidationError):
        DummyModel(data_type="invalid_type")


def test_lax_component_type() -> None:
    class DummyModel(BaseModel):
        comp_type: LaxComponentType

    obj = DummyModel(comp_type="slider")
    assert obj.comp_type == ComponentType.SLIDER

    with pytest.raises(ValidationError):
        DummyModel(comp_type="invalid_comp")


def test_lax_historical_context_mode() -> None:
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
    assert XaiExtensionType.CITATION.l10n_key == ""

    assert ExecutionStatus.PASSED.l10n_key == "status_passed"
    assert SDUIComponentType.BOOLEAN_CARD.l10n_key == "sdui_boolean_card"

    assert RoleClassification.ARCHITECT.l10n_key == "roleArchitect"
    assert RoleClassification.DRIVER.l10n_key == "roleDriver"

    assert TitleKey.TITLE_TIMELINE.l10n_key == "titleTimeline"
    assert TitleKey.SECURITY.l10n_key == ""

    assert ScoringStrategy.WATERFALL.l10n_key == "strategyKoearvostelu"
    assert ScoringStrategy.AVERAGE.l10n_key == "strategyLineaarinenKeskiarvo"
