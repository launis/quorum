import pytest
from pydantic import BaseModel, ValidationError

from backend_v2.models.enums import (
    XaiExtensionType,
    ExecutionStatus,
    BlockDataType,
    ComponentType,
    HistoricalContextMode,
    LaxXaiExtensionType,
    LaxExecutionStatus,
    LaxBlockDataType,
    LaxComponentType,
    LaxHistoricalContextMode,
)

def test_lax_xai_extension_type():
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

def test_lax_execution_status():
    class DummyModel(BaseModel):
        status: LaxExecutionStatus
        
    obj = DummyModel(status="pending")
    assert obj.status == ExecutionStatus.PENDING

def test_lax_block_data_type():
    class DummyModel(BaseModel):
        data_type: LaxBlockDataType
        
    obj = DummyModel(data_type="float")
    assert obj.data_type == BlockDataType.FLOAT

def test_lax_component_type():
    class DummyModel(BaseModel):
        comp_type: LaxComponentType
        
    obj = DummyModel(comp_type="slider")
    assert obj.comp_type == ComponentType.SLIDER

def test_lax_historical_context_mode():
    class DummyModel(BaseModel):
        mode: LaxHistoricalContextMode
        
    obj = DummyModel(mode="DISABLED")
    assert obj.mode == HistoricalContextMode.DISABLED
