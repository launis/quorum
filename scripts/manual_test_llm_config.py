from backend.models.llm import LLMProviderConfig
from pydantic import ValidationError
import sys

def run_tests():
    print("Running manual tests for LLMProviderConfig...")
    
    try:
        # Test Defaults
        config = LLMProviderConfig(id="test/default", provider="openai", model_name="gpt-4o")
        assert config.tpm_limit == 0
        assert config.rpm_limit == 0
        assert config.is_active is True
        print("[PASS] Defaults")

        # Test Values
        config = LLMProviderConfig(
            id="test/custom", provider="vertex_ai", model_name="gemini-1.5-pro",
            tpm_limit=1000, rpm_limit=60, supports_grounding=True, is_active=False
        )
        assert config.tpm_limit == 1000
        assert config.supports_grounding is True
        assert config.is_active is False
        print("[PASS] Values")

        # Test Validation
        try:
            LLMProviderConfig(id="test/fail", provider="o", model_name="m", tpm_limit=-1)
            print("[FAIL] Validation check failed for negative TPM")
            sys.exit(1)
        except ValidationError:
            print("[PASS] Validation (Nagative TPM)")

        # Test UI Labels
        schema = LLMProviderConfig.model_json_schema()
        assert schema["properties"]["tpm_limit"]["x-ui-label"] == "TPM Limit"
        print("[PASS] UI Labels")

        print("ALL TESTS PASSED")

    except Exception as e:
        print(f"[FAIL] Exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
