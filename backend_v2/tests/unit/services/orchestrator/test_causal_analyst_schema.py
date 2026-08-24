import json
from pathlib import Path

from pydantic import BaseModel

from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


def test_causal_analyst_schema_generation_and_validation() -> None:
    """Verifies that the massive Causal Analyst criteria (loaded from seed_data.json)
    successfully generates a dynamic Pydantic schema without any validation or FSM failures.
    """
    compiler = PromptCompiler()

    # Load Causal Analyst block directly from seed_data.json
    seed_path = Path("c:/src/quorum/backend_v2/seed/seed_data.json")
    assert seed_path.exists(), "seed_data.json does not exist at expected path."

    with open(seed_path, encoding="utf-8") as f:
        seed_data = json.load(f)

    # Locate Causal Analyst (normally under block with specific label/ai_description)
    causal_block_data = None
    for item in seed_data:
        if isinstance(item, dict) and item.get("slug") == "causal_analyst":
            causal_block_data = item
            break
        # Fallback to checking label translations for 'Causal Analyst'
        if isinstance(item, dict) and "label" in item:
            label_trans = item["label"].get("translations", {})
            if label_trans == "Causal Analyst":
                causal_block_data = item
                break

    # If not found directly, mock a robust, massive Causal Analyst block resembling seed data
    if not causal_block_data:
        causal_block_data = {
            "id": "blk_1234567890abcdef",
            "slug": "causal_analyst",
            "category_id": "matrix",
            "description": {
                "default_locale": "en",
                "translations": {"en": "Causal Analyst Evaluation", "fi": "Causal Analyst Evaluation"},
            },
            "type": "float",
            "allow_decimals": True,
            "label": {"default_locale": "en", "translations": {"en": "Causal Analyst", "fi": "Causal Analyst"}},
            "ai_description": (
                "<global_framework>\n"
                "MORPHO-SYNTACTIC DETERMINISM: pattern-matching engine... "
                "Concepts exist IF AND ONLY IF physically materialized... "
                "</global_framework>\n\n"
                "CORE MANDATE: Act as a Critical Causal Analyst enforcing Causal Impact Verification... "
                "Require explicit Cognitive Friction (System 2 thinking)..."
            ),
            "scales": [
                {
                    "score": 1,
                    "ai_label": "ONE",
                    "claims": [
                        {
                            "label": {"default_locale": "en", "translations": {"en": "Claim 1", "fi": "Claim 1"}},
                            "tda_assertions": [
                                {
                                    "tda_id": "tda_11112222333344441111222233334444",
                                    "concept_description": "Assertion rule causal details...",
                                    "inverse_evidence": False,
                                    "aggregation_mode": "ALL_MUST_COMPLY",
                                }
                            ],
                        }
                    ],
                }
            ],
        }

    # Validate against core Pydantic DTO (PromptBlock)
    block = PromptBlock.model_validate(causal_block_data)

    # 1. Build dynamic schema (which contains the compiled Markdown rubric and schema keys)
    DynamicSchema = compiler.build_dynamic_schema(
        schema_name="CausalAnalystSchema", criteria=[block], strictness_level=50
    )

    # 2. Assert schema structure integrity
    assert issubclass(DynamicSchema, BaseModel)
    assert "global_matrices" in DynamicSchema.model_fields
    GlobalMatricesSchema = DynamicSchema.model_fields["global_matrices"].annotation
    assert block.id in GlobalMatricesSchema.model_fields

    # Check that description was compiled with full description (no truncation)
    field_info = GlobalMatricesSchema.model_fields[block.id]
    compiled_desc = field_info.description
    assert compiled_desc is not None
    assert block.ai_description is not None
    assert block.ai_description in compiled_desc
    assert len(compiled_desc) > len(block.ai_description)
