import pytest
from pydantic import TypeAdapter, ValidationError
from unittest.mock import MagicMock
from backend_v2.llm.schema_builder import SchemaCompilerService
from backend_v2.models.v2_core import BlockDataType

class MockBlock:
    def __init__(self, slug, type_val, output_extensions):
        self.slug = slug
        self.type = type_val
        self.output_extensions = output_extensions

@pytest.fixture
def test_blocks():
    return [
        MockBlock(
            slug="matrix_risk",
            type_val=BlockDataType.FLOAT,
            output_extensions=["confidence", "risk_flag", "remediation_steps"]
        ),
        MockBlock(
            slug="block_coach",
            type_val=BlockDataType.STRING,
            output_extensions=["coaching", "emotional_sentiment", "theory_link"]
        ),
        MockBlock(
            slug="matrix_logic",
            type_val=BlockDataType.INT,
            output_extensions=["justification", "citation", "falsification", "missing_context"]
        )
    ]

def test_xai_extensions_schema_generation_happy_path(test_blocks):
    """Test that schema builder dynamically generates all fields with correct types."""
    DynamicModel = SchemaCompilerService.compile(test_blocks)
    adapter = TypeAdapter(DynamicModel)
    
    # Valid payload from "LLM"
    payload = {
        # Base outputs
        "matrix_risk": 5.0,
        "block_coach": "Nice work",
        "matrix_logic": 1,
        
        # Extended outputs for matrix_risk
        "matrix_risk_confidence": 95.5,
        "matrix_risk_risk_flag": True,
        "matrix_risk_remediation_steps": ["Step 1", "Step 2"],
        
        # Extended outputs for block_coach
        "block_coach_coaching": "Try alternative phrasing.",
        "block_coach_emotional_sentiment": "Positive and encouraging",
        "block_coach_theory_link": "Constructivist learning theory",
        
        # Extended outputs for matrix_logic
        "matrix_logic_justification": "Valid logic structure.",
        "matrix_logic_citation": "'Always test edge cases.'",
        "matrix_logic_falsification": "Unless the edge case is impossible.",
        "matrix_logic_missing_context": "Background dependencies not mentioned."
    }
    
    # Validation should succeed without raising exceptions
    instance = adapter.validate_python(payload)
    
    # Strict attribute checking
    assert instance.matrix_risk == 5.0
    assert getattr(instance, "matrix_risk_confidence") == 95.5
    assert getattr(instance, "matrix_risk_risk_flag") is True
    assert getattr(instance, "matrix_risk_remediation_steps") == ["Step 1", "Step 2"]
    
    assert instance.block_coach == "Nice work"
    assert getattr(instance, "block_coach_coaching") == "Try alternative phrasing."
    assert getattr(instance, "block_coach_emotional_sentiment") == "Positive and encouraging"
    assert getattr(instance, "block_coach_theory_link") == "Constructivist learning theory"
    
    assert instance.matrix_logic == 1
    assert getattr(instance, "matrix_logic_justification") == "Valid logic structure."
    assert getattr(instance, "matrix_logic_citation") == "'Always test edge cases.'"
    assert getattr(instance, "matrix_logic_falsification") == "Unless the edge case is impossible."
    assert getattr(instance, "matrix_logic_missing_context") == "Background dependencies not mentioned."


def test_xai_extensions_validation_failures(test_blocks):
    """Test that schema builder strictly enforces type hints on extensions, rejecting bad LLM output."""
    DynamicModel = SchemaCompilerService.compile(test_blocks)
    adapter = TypeAdapter(DynamicModel)

    base_payload = {
        "matrix_risk": 5.0,
        "block_coach": "Nice work",
        "matrix_logic": 1,
        
        "matrix_risk_confidence": 95.5,
        "matrix_risk_risk_flag": True,
        "matrix_risk_remediation_steps": ["Step 1", "Step 2"],
        
        "block_coach_coaching": "Try alternative phrasing.",
        "block_coach_emotional_sentiment": "Positive and encouraging",
        "block_coach_theory_link": "Constructivist learning theory",
        
        "matrix_logic_justification": "Valid logic structure.",
        "matrix_logic_citation": "'Always test edge cases.'",
        "matrix_logic_falsification": "Unless the edge case is impossible.",
        "matrix_logic_missing_context": "Background dependencies not mentioned."
    }

    # 1. Test incompatible confidence (float expected, string given)
    bad_confidence = base_payload.copy()
    bad_confidence["matrix_risk_confidence"] = "HIGH" # MUST FAIL
    
    with pytest.raises(ValidationError) as exc:
        adapter.validate_python(bad_confidence)
    assert "matrix_risk_confidence" in str(exc.value)

    # 2. Test incompatible risk_flag (bool expected, string given)
    bad_risk_flag = base_payload.copy()
    bad_risk_flag["matrix_risk_risk_flag"] = "NotABoolean" # MUST FAIL
    
    with pytest.raises(ValidationError) as exc:
        adapter.validate_python(bad_risk_flag)
    assert "matrix_risk_risk_flag" in str(exc.value)

    # 3. Test incompatible remediation_steps (list[str] expected, string given)
    bad_remediation = base_payload.copy()
    bad_remediation["matrix_risk_remediation_steps"] = "Just fix it." # MUST FAIL
    
    with pytest.raises(ValidationError) as exc:
        adapter.validate_python(bad_remediation)
    assert "matrix_risk_remediation_steps" in str(exc.value)

    # 4. Test float coercion works for confidence (if int given)
    good_coercion = base_payload.copy()
    good_coercion["matrix_risk_confidence"] = 90 # Int should correctly coerce to 90.0 FLOAT
    
    instance = adapter.validate_python(good_coercion)
    assert getattr(instance, "matrix_risk_confidence") == 90.0
    assert isinstance(getattr(instance, "matrix_risk_confidence"), float)
