from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.models.enums import PromptBlockCategory
from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


@pytest.mark.skip("Legacy architecture obsolete")
def test_reproduce_tier4_schema_bug() -> None:
    # Setup prompt compiler
    compiler = PromptCompiler()

    # We have a prompt block blk_599645bd5baf44e2
    # What was its type and category?
    # The error says field `blk_599645bd5baf44e2` was expected to be a string.
    block = PromptBlock.model_validate(
        {
            "id": "blk_599645bd5baf44e2",
            "type": "instruction",
            "category_id": PromptBlockCategory.MATRIX,
            "label": {"translations": {"en": "Matrix"}, "default_locale": "en"},
            "ai_description": "Do matrix things",
            "slug": "test_block",
            "description": {"translations": {"en": "desc"}, "default_locale": "en"},
            "scales": [
                {
                    "score": 1,
                    "ai_label": "POOR",
                    "claims": [
                        {
                            "label": {"translations": {"en": "Claim"}, "default_locale": "en"},
                            "ai_description": "rule",
                            "tda_assertions": [
                                {
                                    "concept_description": {
                                        "default_locale": "en",
                                        "translations": {"en": "rule", "fi": "rule"},
                                    },
                                    "inverse_evidence": False,
                                    "aggregation_mode": "EXISTS",
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    )

    schema = compiler.build_dynamic_schema(
        schema_name="TestSchema",
        criteria=[block],
        has_shuffled_atoms=False,
        target_locale="en",
        strictness_level=50,
    )

    # The LLM output
    # LLM outputs an array for blk_599645bd5baf44e2 instead of the expected type
    llm_output = {
        "reasoning_trace": "test",
        "evaluation_notes": "test",
        "blk_599645bd5baf44e2": [
            {"atom_id": "blk_599645bd5baf44e2_1", "semantic_reasoning": "...", "exact_quotes": ["..."]}
        ],
    }

    # Validation should fail
    with pytest.raises(ValidationError) as exc_info:
        schema.model_validate(llm_output)

    errs = exc_info.value.errors()
    print("\nVAL ERRORS:", errs)
    assert errs[0]["type"] == "string_type"
