import pytest
from pydantic import ValidationError
from backend.models.llm import LLMProviderConfig

def test_llm_provider_config_defaults():
    """Test that default values are set correctly."""
    config = LLMProviderConfig(
        id="test/default",
        provider="openai",
        model_name="gpt-4o",
        tpm_limit=100000,
        rpm_limit=1000,
    )
    assert config.tpm_limit == 100000
    assert config.rpm_limit == 1000
    assert config.default_max_tokens is None
    assert config.vertex_location is None
    assert config.supports_grounding is False
    assert config.is_active is True
    assert config.temperature == 0.7

def test_llm_provider_config_values():
    """Test that values are correctly assigned."""
    config = LLMProviderConfig(
        id="test/custom",
        provider="vertex_ai",
        model_name="gemini-1.5-pro",
        tpm_limit=1000,
        rpm_limit=60,
        default_max_tokens=8192,
        vertex_location="us-central1",
        supports_grounding=True,
        is_active=False
    )
    assert config.tpm_limit == 1000
    assert config.rpm_limit == 60
    assert config.default_max_tokens == 8192
    assert config.vertex_location == "us-central1"
    assert config.supports_grounding is True
    assert config.is_active is False

def test_llm_provider_config_validation():
    """Test strict validation rules."""
    # Negative limits should fail (ge=0)
    with pytest.raises(ValidationError):
        LLMProviderConfig(
            id="test/fail",
            provider="openai",
            model_name="gpt-4",
            tpm_limit=-1,
            rpm_limit=1000
        )
    
    with pytest.raises(ValidationError):
        LLMProviderConfig(
            id="test/fail",
            provider="openai",
            model_name="gpt-4",
            tpm_limit=100000,
            rpm_limit=-1
        )

    # Max tokens < 1 should fail
    with pytest.raises(ValidationError):
        LLMProviderConfig(
            id="test/fail",
            provider="openai",
            model_name="gpt-4",
            tpm_limit=100000,
            rpm_limit=1000,
            default_max_tokens=0
        )

def test_ui_labels_presence():
    """Verify that x-ui-label is present in the schema for new fields."""
    schema = LLMProviderConfig.model_json_schema()
    props = schema["properties"]
    
    assert props["tpm_limit"]["x-ui-label"] == "TPM Limit"
    assert props["rpm_limit"]["x-ui-label"] == "RPM Limit"
    assert props["default_max_tokens"]["x-ui-label"] == "Max Tokens"
    assert props["vertex_location"]["x-ui-label"] == "Vertex Location"
    assert props["supports_grounding"]["x-ui-label"] == "Supports Grounding"
    assert props["is_active"]["x-ui-label"] == "Is Active"
