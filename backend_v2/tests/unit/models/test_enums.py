from unittest.mock import AsyncMock
import pytest
from pydantic import BaseModel, ValidationError

from backend_v2.models.enums import (
    BlockDataType,
    ComponentType,
    ExecutionStatus,
    HistoricalContextMode,
    LaxBlockDataType,
    LaxComponentType,
    LaxExecutionStatus,
    LaxHistoricalContextMode,
    LaxXaiExtensionType,
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


def test_lax_execution_status() -> None:
    class DummyModel(BaseModel):
        status: LaxExecutionStatus

    obj = DummyModel(status="PENDING")
    assert obj.status == ExecutionStatus.PENDING


def test_lax_block_data_type() -> None:
    class DummyModel(BaseModel):
        data_type: LaxBlockDataType

    obj = DummyModel(data_type="float")
    assert obj.data_type == BlockDataType.FLOAT


def test_lax_component_type() -> None:
    class DummyModel(BaseModel):
        comp_type: LaxComponentType

    obj = DummyModel(comp_type="slider")
    assert obj.comp_type == ComponentType.SLIDER


def test_lax_historical_context_mode() -> None:
    class DummyModel(BaseModel):
        mode: LaxHistoricalContextMode

    obj = DummyModel(mode="DISABLED")
    assert obj.mode == HistoricalContextMode.DISABLED
