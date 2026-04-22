import json
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
                            "something_else": "Random"
                        }
                    }
                }
            }
        }
    }

    # Path='$inputs.history' triggers the Attention Dilution recursive formatting logic
    result = compiler._extract_value_from_state("$inputs.history", state)

    assert "<prior_step_context source=\"STEP_XYZ\">" in result
    assert "### MATRIX_EVALUATION" in result
    # Attention Dilution Patch: Assert prefixes are cleaned out
    assert "- **Evidence Quote:** The quoted text" in result
    assert "- **Final Score:** 5" in result
    assert "- **Something Else:** Random" in result


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

    criteria: list[dict[str, Any]] = [
        {
            "id": "mat_123",
            "type": "string",
            "label": {"translations": {"en": "Test Matrix"}},
            "ai_description": "Strict directive for AI",
            "allow_decimals": False,
            "scales": [
                {
                    "score": 5,
                    "name": {"translations": {"en": "Excellent"}},
                    "claims": [{"ai_description": "Student performed perfectly."}]
                },
                {
                    "score": 1,
                    "name": {"translations": {"en": "Poor"}},
                    "claims": [{"ai_description": "Student failed."}]
                }
            ]
        }
    ]

    xml = compiler.compile_xml_rubrics(criteria, "en")

    # Assert thick XML wrapping
    assert "<EVALUATION_RUBRICS>" in xml
    assert '</EVALUATION_RUBRICS>' in xml
    assert '<MATRIX id="mat_123" title="Test Matrix">' in xml
    assert '<DIRECTIVE>Strict directive for AI</DIRECTIVE>' in xml

    # Assert Markdown table extraction
    assert '| Score | Label | Critical Directive |' in xml
    assert '| 5 | Excellent | Student performed perfectly. ENFORCEMENT: Evaluate as FALSE immediately unless explicit, documented evidence is provided. |' in xml
    assert '| 1 | Poor | Student failed. ENFORCEMENT: Evaluate as FALSE immediately unless explicit, documented evidence is provided. |' in xml


def test_build_dynamic_schema_removes_scores() -> None:
    """Epic 26 Phase 1: Assert dynamic schema compilation completely strips soft score fields."""
    compiler = PromptCompiler()

    criteria = [
        {
            "id": "crit_validation",
            "type": "int",
            "label": {"translations": {"en": "Strict Logic Test"}},
            "ai_description": "Evaluate securely.",
            "output_extensions": ["citation", "missing_context"],
            "allow_decimals": False,
            "scales": [{"score": 1}, {"score": 5}],
            "theory_grounding": {"citation_reference": "Test Source Long String"}
        }
    ]

    DynamicModel = compiler.build_dynamic_schema(
        schema_name="TestSchema",
        criteria=criteria,
        target_locale="en",
        has_search_result=True,
        has_shuffled_atoms=True
    )

    # Assert top-level fields
    assert "reasoning_trace" in DynamicModel.model_fields
    assert "evaluation_notes" in DynamicModel.model_fields
    
    # Assert Map-Reduce atom response integration
    assert "evaluations" in DynamicModel.model_fields
    evaluations_field = DynamicModel.model_fields["evaluations"]
    
    # Assert nested matrix block
    assert "crit_validation" in DynamicModel.model_fields
    NestedModel = DynamicModel.model_fields["crit_validation"].annotation

    # Verify standard text fields from extensions are present
    assert "step_1_evidence_quote" in NestedModel.model_fields
    assert "step_1b_cited_source_id" in NestedModel.model_fields
    assert "step_1c_google_citation" in NestedModel.model_fields
    assert "extension_missing_context" in NestedModel.model_fields

    # CRITICAL: Assert Epic 26 soft-schema removal
    assert "step_4_final_score" not in NestedModel.model_fields

    # Validate output validation parses correctly
    valid_obj = DynamicModel.model_validate({
        "reasoning_trace": "Analysis...",
        "evaluation_notes": "Synthesis...",
        "evaluations": [
            {
                "atom_id": "atom_1",
                "quote": "Sample",
                "reasoning": "Reason",
                "boolean": True
            }
        ],
        "crit_validation": {
            "step_1_evidence_quote": "Yes",
            "step_1b_cited_source_id": "Test Source",
            "step_1c_google_citation": "Verified",
            "extension_missing_context": "None"
        }
    })

    crit_block: Any = getattr(valid_obj, "crit_validation")
    assert crit_block.step_1_evidence_quote == "Yes"
    
    # Assert citations heal properly (LLM truncates string)
    heal_obj = DynamicModel.model_validate({
        "reasoning_trace": "Analysis...",
        "evaluation_notes": "Synthesis...",
        "evaluations": [],
        "crit_validation": {
            "step_1b_cited_source_id": "Test Source L",  # Truncated but >10 chars
            "extension_missing_context": "None"          # Required field
        }
    })
    crit_block_healed: Any = getattr(heal_obj, "crit_validation")
    assert crit_block_healed.step_1b_cited_source_id == "Test Source Long String"




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

    assert obj.chunk_id == "chk_xyz" # type: ignore[attr-defined]
    assert len(obj.records) == 1 # type: ignore[attr-defined]
    assert obj.records[0].original_id == "atom_1" # type: ignore[attr-defined]
    assert obj.records[0].payload.score == 5 # type: ignore[attr-defined]

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
