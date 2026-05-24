from typing import Any

import pytest
from pydantic import ValidationError

from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


def test_nested_state_flattening_logic() -> None:
    """Epic 12 Phase 2: Assert state flattening logic cleans cognitive prefixes."""
    compiler = PromptCompiler()

    state = {
        "inputs": {
            "history": {
                "step_xyz": {
                    "outputs": {
                        "matrix_evaluation": {
                            "step_1_evidence_quote": "The quoted text",
                            "step_4_final_score": 5,
                            "something_else": "Random",
                        }
                    }
                }
            }
        }
    }

    # Path='$inputs.history' triggers the Attention Dilution recursive formatting logic
    result = compiler._extract_value_from_state("$inputs.history", state)

    assert '<matrix_input source="STEP_XYZ">' in result
    assert "<MATRIX_EVALUATION>" in result
    assert "  <Evidence_Quote>The quoted text</Evidence_Quote>" in result
    assert "  <Final_Score>5</Final_Score>" in result
    assert "  <Something_Else>Random</Something_Else>" in result


def test_global_steps_extraction() -> None:
    """Tier 4 Bug Hunting: Test that '$steps' properly extracts the entire state."""
    compiler = PromptCompiler()
    state = {
        "sr_aaa": {"outputs": {"val": 1}},
        "sr_bbb": {"outputs": {"val": 2}},
    }

    result = compiler._extract_value_from_state("$steps", state)

    # Needs to extract the whole state via formatting logic
    assert "SR_AAA" in result
    assert "SR_BBB" in result


def test_compile_xml_rubrics_structure() -> None:
    """Epic 12 Phase 1: Assert PromptBlock criteria is rendered into Thick XML."""
    compiler = PromptCompiler()
    from backend_v2.models.v2_core import PromptBlock

    criteria = [
        PromptBlock.model_validate(
            {
                "id": "blk_1234567890abcdef",
                "slug": "test-matrix",
                "label": {"default_locale": "en", "translations": {"en": "Test Matrix"}},
                "description": {"default_locale": "en", "translations": {"en": "Test Matrix Description"}},
                "ai_description": "Strict directive for AI",
                "category_id": "matrix",
                "type": "string",
                "allow_decimals": False,
                "scale_min": 1,
                "scale_max": 5,
                "scales": [
                    {
                        "score": 5,
                        "ai_label": "EXCELLENT",
                        "name": {"default_locale": "en", "translations": {"en": "Excellent"}},
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "Excellent Claim"}},
                                "ai_description": "Student performed perfectly.",
                                "tda_assertions": [
                                    {
                                        "tda_id": "tda_1111111111111111",
                                        "ai_rule_description": "Student performed perfectly.",
                                        "inverse_evidence": False,
                                        "aggregation_mode": "EXISTS",
                                    }
                                ],
                            }
                        ],
                    },
                    {
                        "score": 1,
                        "ai_label": "POOR",
                        "name": {"default_locale": "en", "translations": {"en": "Poor"}},
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "Poor Claim"}},
                                "ai_description": "Student failed.",
                                "tda_assertions": [
                                    {
                                        "tda_id": "tda_2222222222222222",
                                        "ai_rule_description": "Student failed.",
                                        "inverse_evidence": False,
                                        "aggregation_mode": "EXISTS",
                                    }
                                ],
                            }
                        ],
                    },
                ],
            }
        )
    ]

    xml = compiler.compile_xml_rubrics(criteria, "en")

    # Assert thick XML wrapping
    assert "<EVALUATION_RUBRICS>" in xml
    assert "</EVALUATION_RUBRICS>" in xml
    assert '<MATRIX id="blk_1234567890abcdef" title="Test Matrix">' in xml
    assert "<DIRECTIVE>Strict directive for AI</DIRECTIVE>" in xml
    assert "<CRITICAL_DIRECTIVES>" in xml
    assert "Student performed perfectly." in xml
    assert "Student failed." in xml


def test_build_dynamic_schema_removes_scores() -> None:
    """Epic 26 Phase 1: Assert dynamic schema compilation completely strips soft score fields."""
    compiler = PromptCompiler()
    from backend_v2.models.v2_core import PromptBlock

    criteria = [
        PromptBlock.model_validate(
            {
                "id": "blk_1111111111111111",
                "slug": "crit-validation",
                "category_id": "matrix",
                "type": "int",
                "label": {"default_locale": "en", "translations": {"en": "Strict Logic Test"}},
                "description": {"default_locale": "en", "translations": {"en": "Strict Logic Test Description"}},
                "ai_description": "Evaluate securely.",
                "output_extensions": ["citation", "missing_context"],
                "allow_decimals": False,
                "scale_min": 1,
                "scale_max": 5,
                "scales": [
                    {
                        "score": 1,
                        "ai_label": "POOR",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "Poor Claim"}},
                                "ai_description": "Poor performance",
                                "tda_assertions": [
                                    {
                                        "tda_id": "tda_2222222222222222",
                                        "ai_rule_description": "Poor performance description",
                                        "inverse_evidence": False,
                                        "aggregation_mode": "EXISTS",
                                    }
                                ],
                            }
                        ],
                    },
                    {
                        "score": 5,
                        "ai_label": "EXCELLENT",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "Excellent Claim"}},
                                "ai_description": "Excellent performance",
                                "tda_assertions": [
                                    {
                                        "tda_id": "tda_1111111111111111",
                                        "ai_rule_description": "Excellent performance description",
                                        "inverse_evidence": False,
                                        "aggregation_mode": "EXISTS",
                                    }
                                ],
                            }
                        ],
                    },
                ],
                "theory_grounding": {
                    "source_url": "https://example.com/source",
                    "citation_reference": "Test Source Long String",
                },
            }
        )
    ]

    DynamicModel = compiler.build_dynamic_schema(
        schema_name="TestSchema", criteria=criteria, target_locale="en", has_search_result=True, has_shuffled_atoms=True
    )

    # Assert top-level fields
    assert "reasoning_trace" in DynamicModel.model_fields
    assert "evaluation_notes" in DynamicModel.model_fields

    # Assert Map-Reduce atom response integration
    assert "evaluations" in DynamicModel.model_fields

    # Assert nested matrix block
    assert "blk_1111111111111111" in DynamicModel.model_fields
    from typing import cast

    from pydantic import BaseModel

    NestedModel = cast(type[BaseModel], DynamicModel.model_fields["blk_1111111111111111"].annotation)

    # Verify standard text fields from extensions are present
    assert "semantic_reasoning" in NestedModel.model_fields

    # CRITICAL: Assert Epic 26 soft-schema removal is enforced
    assert "step_4_final_score" not in NestedModel.model_fields

    # Validate output validation parses correctly
    valid_obj = DynamicModel.model_validate(
        {
            "step_1_reasoning_trace": "Analysis...",
            "evaluation_notes": "Synthesis...",
            "evaluations": [
                {
                    "atom_id": "atom_1",
                    "localized_anchors_found": ["Sample"],
                    "semantic_reasoning": "Reason",
                    "contextual_override": False,
                    "exact_quote": "Sample",
                }
            ],
            "blk_1111111111111111": {"semantic_reasoning": "Yes, everything is correct."},
        }
    )

    # Ruff forces direct attribute access over getattr; type ignored for MyPy dynamic schema
    crit_block: Any = valid_obj.blk_1111111111111111  # type: ignore[attr-defined]
    assert crit_block.semantic_reasoning == "Yes, everything is correct."


def test_chunk_response_schema_generation() -> None:
    """Epic 23 Phase 3: Assert chunk schema generates correctly nested strictly typed items."""
    compiler = PromptCompiler()

    from pydantic import BaseModel, ConfigDict, Field

    class DummyPayload(BaseModel):
        score: int = Field(..., ge=1, le=5)
        text: str

        model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    DynamicSchema = compiler.build_chunk_response_schema("TestChunkSchema", DummyPayload)

    obj = DynamicSchema.model_validate(
        {
            "chunk_id": "chk_xyz",
            "records": [
                {
                    "original_id": "atom_1",
                    "payload": {"score": 5, "text": "Valid"},
                }
            ],
        }
    )

    assert obj.chunk_id == "chk_xyz"  # type: ignore[attr-defined]
    assert len(obj.records) == 1  # type: ignore[attr-defined]
    assert obj.records[0].original_id == "atom_1"  # type: ignore[attr-defined]
    assert obj.records[0].payload.score == 5  # type: ignore[attr-defined]

    # Test Validation failure parity
    with pytest.raises(ValidationError):
        DynamicSchema.model_validate(
            {
                "chunk_id": "chk_xyz",
                "records": [
                    {
                        "original_id": "atom_2",
                        "payload": {"score": 10, "text": "Score Too High"},  # Must fail ge/le
                    }
                ],
            }
        )


def test_compile_chunk_payload_instruction() -> None:
    """Epic 23 Phase 3: Assert chunk instruction adheres to Phase 9 fence rules."""
    compiler = PromptCompiler()

    res = compiler.compile_chunk_payload_instruction("chk_123", "Some dangerous input")

    assert "map-reduce chunk 'chk_123'" in res
    assert "<user_payload>" in res
    assert "</user_payload>" in res
    assert "Some dangerous input" in res


def test_context_snowballing_prevention() -> None:
    """Epic 32: Test that 'evaluations' array is stripped from prior step context to prevent 95k prompt bloat."""
    compiler = PromptCompiler()

    state = {
        "inputs": {
            "history": {
                "step_analyst": {
                    "outputs": {
                        "evaluations": [
                            {"atom_id": "1", "boolean": True, "reasoning": "Long text..."},
                            {"atom_id": "2", "boolean": False, "reasoning": "Another long text..."},
                        ],
                        "evaluation_notes": "This is the summary.",
                        "normalized_score": 4.5,
                    }
                }
            }
        }
    }

    result = compiler._extract_value_from_state("$inputs.history", state)

    # Should include the qualitative summary and score
    assert '<matrix_input source="STEP_ANALYST">' in result
    assert "<Evaluation_Notes>This is the summary.</Evaluation_Notes>" in result
    assert "<Normalized_Score>4.5</Normalized_Score>" in result

    # Should completely strip the raw evaluations array
    assert "EVALUATIONS" not in result.upper()
    assert "Long text" not in result
    assert "atom_id" not in result


def test_execution_persona_injection() -> None:
    """Epic 55 Phase 1: Verify that different ExecutionPersonas correctly inject their corresponding SSOT directives."""
    compiler = PromptCompiler()
    from backend_v2.models.enums import ExecutionPersona
    from backend_v2.models.v2_core import PromptBlock
    from backend_v2.core.system_directives import get_directive_for_persona

    def build_test_criteria(persona: ExecutionPersona) -> list[PromptBlock]:
        return [
            PromptBlock.model_validate(
                {
                    "id": "blk_1234567890abcdef",
                    "slug": "test-matrix",
                    "label": {"default_locale": "en", "translations": {"en": "Test Matrix"}},
                    "description": {"default_locale": "en", "translations": {"en": "Test Matrix Description"}},
                    "ai_description": "Test directive description",
                    "category_id": "matrix",
                    "type": "string",
                    "allow_decimals": False,
                    "execution_persona": persona,
                    "scale_min": 1,
                    "scale_max": 5,
                    "scales": [
                        {
                            "score": 5,
                            "ai_label": "EXCELLENT",
                            "name": {"default_locale": "en", "translations": {"en": "Excellent"}},
                            "claims": [
                                {
                                    "label": {"default_locale": "en", "translations": {"en": "Claim"}},
                                    "ai_description": "Perfect performance",
                                    "tda_assertions": [
                                        {
                                            "tda_id": "tda_1111111111111111",
                                            "ai_rule_description": "Perfect assertion",
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
        ]

    # Test DETERMINISTIC_PARSER
    criteria_det = build_test_criteria(ExecutionPersona.DETERMINISTIC_PARSER)
    xml_det = compiler.compile_xml_rubrics(criteria_det, "en")
    expected_det = get_directive_for_persona(ExecutionPersona.DETERMINISTIC_PARSER)
    assert xml_det.startswith(expected_det)
    assert "MORPHO-SYNTACTIC DETERMINISM" in xml_det

    # Test COACH
    criteria_coach = build_test_criteria(ExecutionPersona.COACH)
    xml_coach = compiler.compile_xml_rubrics(criteria_coach, "en")
    expected_coach = get_directive_for_persona(ExecutionPersona.COACH)
    assert xml_coach.startswith(expected_coach)
    assert "ACTIONABLE REMEDIATION" in xml_coach

    # Test XAI_REPORTER
    criteria_rep = build_test_criteria(ExecutionPersona.XAI_REPORTER)
    xml_rep = compiler.compile_xml_rubrics(criteria_rep, "en")
    expected_rep = get_directive_for_persona(ExecutionPersona.XAI_REPORTER)
    assert xml_rep.startswith(expected_rep)
    assert "PEDAGOGICAL SYNTHESIS" in xml_rep

