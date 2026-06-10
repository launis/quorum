import pytest
from pydantic import ValidationError

from backend_v2.models.enums import PromptBlockCategory
from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


def test_reproduce_tier4_schema_bug():
    # Setup prompt compiler
    compiler = PromptCompiler()

    # We have a prompt block blk_599645bd5baf44e2
    # What was its type and category?
    # The error says field `blk_599645bd5baf44e2` was expected to be a string.
    block = PromptBlock(
        id="blk_599645bd5baf44e2",
        type="instruction",
        category_id=PromptBlockCategory.MATRIX,
        label={"translations": {"en": "Matrix"}},
        ai_description="Do matrix things",
        scales=[
            {
                "score": 1,
                "ai_label": "POOR",
                "claims": [
                    {
                        "label": {"translations": {"en": "Claim"}},
                        "ai_description": "rule",
                        "tda_assertions": [
                            {
                                "ai_rule_description": "rule",
                                "inverse_evidence": False,
                                "aggregation_mode": "EXISTS"
                            }
                        ]
                    }
                ]
            }
        ]
    )

    schema = compiler.build_dynamic_schema(
        schema_name="TestSchema",
        criteria=[block],
        has_search_result=False,
        has_shuffled_atoms=False,
        target_locale="en"
    )

    # The LLM output
    # LLM outputs an array for blk_599645bd5baf44e2 instead of the expected type
    llm_output = {
        "reasoning_trace": "test",
        "evaluation_notes": "test",
        "blk_599645bd5baf44e2": [
            {
                "atom_id": "blk_599645bd5baf44e2_1",
                "semantic_reasoning": "...",
                "exact_quote": "..."
            }
        ]
    }

    # Validation should fail
    with pytest.raises(ValidationError) as exc_info:
        schema.model_validate(llm_output)

    errs = exc_info.value.errors()
    print("\nVAL ERRORS:", errs)
    assert errs[0]["type"] == "string_type"
