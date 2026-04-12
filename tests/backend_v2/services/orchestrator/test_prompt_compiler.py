import json
from typing import Any

import pytest
from pydantic import ValidationError

from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


def test_nested_state_flattening_logic() -> None:
    """Epic 12 Phase 2: Assert state flattening logic cleans cognitive prefixes."""
    compiler = PromptCompiler()

    nested_state = {
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

    # Path='steps' triggers the Attention Dilution recursive formatting logic
    result = compiler._extract_value_from_state("steps", nested_state)

    assert "<prior_step_context source=\"STEP_XYZ\">" in result
    assert "### MATRIX_EVALUATION" in result
    # Attention Dilution Patch: Assert prefixes are cleaned out
    assert "- **Evidence Quote:** The quoted text" in result
    assert "- **Final Score:** 5" in result
    assert "- **Something Else:** Random" in result


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
    assert '| 5 | Excellent | Student performed perfectly. |' in xml
    assert '| 1 | Poor | Student failed. |' in xml


@pytest.mark.skip(reason="Legacy dynamic schema removed in Epic 20 Phase 7 blind evaluation")
def test_micro_cot_validation_healing() -> None:
    """Epic 12 Phase 3: Assert Semantic Self-Healing triggers Pydantic ValidationError."""
    compiler = PromptCompiler()

    criteria_json = json.dumps([
        {
            "id": "crit_validation",
            "type": "int",
            "label": {"translations": {"en": "Strict Logic Test"}},
            "ai_description": "Evaluate securely.",
            "output_extensions": ["citation"],  # This triggers step_1_evidence_quote
            "allow_decimals": False,
            "scales": [{"score": 1}, {"score": 5}]
        }
    ])

    DynamicModel = compiler._cached_build_dynamic_schema(
        schema_name="TestSchema",
        criteria_json=criteria_json,
        target_locale="en",
        has_search_result=False
    )

    # 1. Negative Test: Semantic Logic Error (Score >= 4 without quote)
    with pytest.raises(ValidationError) as exc:
        DynamicModel.model_validate({
            "reasoning_trace": "I think it is a 5.",
            "evaluation_notes": "Very good.",
            "crit_validation": {
                "step_1_evidence_quote": None,
                "step_4_final_score": 5
            }
        })

    # Verify the exact custom logic error message we defined in PromptCompiler
    assert "CRITICAL LOGICAL ERROR" in str(exc.value)
    assert "high score (5.0)" in str(exc.value)
    assert "step_1_evidence_quote" in str(exc.value)

    # 2. Positive Test: Score >= 4 WITH quote
    valid_obj = DynamicModel.model_validate({
        "reasoning_trace": "I think it is a 5.",
        "evaluation_notes": "Very good because text says 'Yes'.",
        "crit_validation": {
            "step_1_evidence_quote": "Yes",
            "step_4_final_score": 5
        }
    })

    # Mypy cannot know about dynamically created fields, so we use type ignore
    crit_block_1: Any = valid_obj.crit_validation  # type: ignore[attr-defined]
    assert crit_block_1.step_4_final_score == 5
    assert crit_block_1.step_1_evidence_quote == "Yes"

    # 3. Positive Test: Score < 4 without quote (Should be allowed by logic)
    valid_low_obj = DynamicModel.model_validate({
        "reasoning_trace": "It's bad.",
        "evaluation_notes": "Nothing found.",
        "crit_validation": {
            "step_1_evidence_quote": None,
            "step_4_final_score": 3
        }
    })

    crit_block_2: Any = valid_low_obj.crit_validation  # type: ignore[attr-defined]
    assert crit_block_2.step_4_final_score == 3
    assert crit_block_2.step_1_evidence_quote is None
