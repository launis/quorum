import pytest
from pydantic import ValidationError

from backend_v2.models.v2_core import RenderBlueprint, HeaderComponent, Gauge1DComponent

def test_render_blueprint_valid():
    """Test valid instantiation."""
    data = {
        "version": "1.0",
        "components": [
            {"type": "header", "title": "Test Title"},
            {"type": "1d_gauge", "data_path": "$results.score", "title": "Total Score"}
        ]
    }
    bp = RenderBlueprint.model_validate(data)
    assert bp.version == "1.0"
    assert len(bp.components) == 2
    assert isinstance(bp.components[0], HeaderComponent)
    assert bp.components[0].title == "Test Title"

def test_render_blueprint_invalid_type():
    """Test corrupted component type fails fast."""
    data = {
        "version": "1.0",
        "components": [
            {"type": "himmeli", "title": "Test Title"}
        ]
    }
    with pytest.raises(ValidationError) as exc:
        RenderBlueprint.model_validate(data)
    
    assert "Input should be 'header'" in str(exc.value)

def test_render_blueprint_missing_mandatory_keys():
    """Test missing mandatory paths in components fails fast."""
    data = {
        "version": "1.0",
        "components": [
            {"type": "1d_gauge"} # Missing data_path
        ]
    }
    with pytest.raises(ValidationError) as exc:
        RenderBlueprint.model_validate(data)
    
    assert "data_path" in str(exc.value)
    assert "Field required" in str(exc.value)

def test_render_blueprint_empty_payload():
    """Test empty spaces and minimal valid definition."""
    data = {}
    bp = RenderBlueprint.model_validate(data)
    assert bp.version == "1.0" # Defaults
    assert bp.components == [] # Defaults to empty list
