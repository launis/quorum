from pydantic import BaseModel

from backend_v2.models.domain.prompt_blocks import PromptBlockAdapter
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


def test_causal_analyst_schema_generation_and_validation() -> None:
    """Verifies that the massive Causal Analyst criteria (loaded from seed_data.json)
    successfully generates a dynamic Pydantic schema without any validation or FSM failures.
    """
    compiler = PromptCompiler()

    # Criteria block structure for Causal Analyst (mirroring actual production seed_data.json)
    causal_block_data = {
        "id": "blk_1a2b3c4d5e6f7a8b",
        "slug": "matrix_causal_analyst",
        "category_id": "matrix",
        "label": {
            "translations": {
                "en": "Causal Depth & Counterfactual Rigor",
                "fi": "Kausaalinen syvyys ja kontrafaktuaalinen tarkkuus",
            },
        },
        "description": {
            "translations": {
                "en": "Evaluates causal inference depth and counterfactual verification.",
                "fi": "Arvioi kausaalisen pttelyn syvyytt ja kontrafaktuaalista verifiointia.",
            },
        },
        "ai_description": (
            "MANDATORY: Evaluates causal inference depth and counterfactual verification. "
            "Scores scale from 1 (Superficial/Correlational) to 5 (Deep Causal & Mechanism Verified)."
        ),
        "type": "float",
        "scales": [
            {
                "score": 1,
                "ai_label": "SUPERFICIAL CORRELATION",
                "claims": [
                    {
                        "label": {
                            "translations": {
                                "en": "Mistakes correlation for causation without mechanism analysis.",
                                "fi": "Sekoittaa korrelaation kausaliteettiin ilman mekanismin analysointia.",
                            },
                        },
                        "tda_assertions": [
                            {
                                "tda_id": "tda_11111111111111111111111111111111",
                                "concept_description": "Mistakes correlation for causation.",
                                "inverse_evidence": False,
                                "aggregation_mode": "EXISTS",
                            }
                        ],
                    }
                ],
            },
            {
                "score": 5,
                "ai_label": "DEEP CAUSAL MECHANISM",
                "claims": [
                    {
                        "label": {
                            "translations": {
                                "en": "Establishes full causal mechanism with counterfactual proofs.",
                                "fi": "Määrittää täyden kausaalisen mekanismin kontrafaktuaalisin todistein.",
                            },
                        },
                        "tda_assertions": [
                            {
                                "tda_id": "tda_55555555555555555555555555555555",
                                "concept_description": "Establishes full causal mechanism.",
                                "inverse_evidence": False,
                                "aggregation_mode": "EXISTS",
                            }
                        ],
                    }
                ],
            },
        ],
    }

    # Validate against core Pydantic DTO (PromptBlock)
    block = PromptBlockAdapter.validate_python(causal_block_data)

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
