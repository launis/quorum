import pytest
from pydantic import ValidationError

from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler, EvidenceType


def test_anti_laziness_mandate_forbids_true_with_no_evidence():
    """
    Test that reproducing the bug where a negative claim evaluation (step_5_boolean=True)
    is rejected if evidence_type is NO_EVIDENCE due to the hardcoded ANTI-LAZINESS MANDATE.
    """
    compiler = PromptCompiler()
    
    # 1. Create a dummy criteria that triggers the dynamic schema builder
    criteria = [
        PromptBlock(
            id="cr_0123456789abcdef0123456789abcdef",
            slug="test-atom",
            type="criteria",
            category_id="test",
            ai_description="Dummy atom",
            label={"translations": {"en": "Test Atom"}, "default_locale": "en"},
            description={"translations": {"en": "desc"}, "default_locale": "en"},
        )
    ]
    
    # 2. Build the dynamic schema (has_shuffled_atoms=False will use the standard AtomResponse inside build_blind_evaluation_schema indirectly? 
    # Actually, the blind evaluation schema is built via build_blind_evaluation_schema
    # Let's test build_blind_evaluation_schema directly since it's cleaner.
    DynamicModel = compiler.build_blind_evaluation_schema("TestSchema")
    
    # 3. Create a payload that triggers the bug
    payload = {
        "evaluations": [
            {
                "atom_id": "cr_0123456789abcdef0123456789abcdef",
                "step_1_evidence_type": EvidenceType.NO_EVIDENCE,
                "step_2_quote": None,
                "step_3_implicit_justification": None,
                "step_4_reasoning": "There is no evidence of this, so the claim 'it is missing' is True.",
                "step_5_boolean": True
            }
        ]
    }
    
    # 4. Validate the payload. It should SUCCEED now that the bug is fixed!
    try:
        validated_data = DynamicModel.model_validate(payload, context={"strictness_level": 50})
        # If we reached here, the validation passed successfully.
        assert validated_data is not None
    except ValidationError as e:
        pytest.fail(f"Validation failed unexpectedly: {e}")
