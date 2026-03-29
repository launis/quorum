from typing import Any
from pydantic import BaseModel

from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


def test_prompt_compiler_deep_matrix_schema() -> None:
    compiler = PromptCompiler()

    from backend_v2.models.enums import BlockDataType
    # Mocking the JSON structure we confirmed in Phase 1
    mock_matrix_block = {
        "id": "blk_test_matrix",
        "type": BlockDataType.FLOAT,
        "allow_decimals": True,
        "label": {"default_locale": "en", "translations": {"en": "Critical Distance Score"}},
        "ai_description": "ROLE: ADVERSARIAL AUDITOR... Evaluate the user's intellectual effort...",
        "rows": [
            {
                "label": {"default_locale": "en", "translations": {"en": "Critical Distance Score"}},
                "ai_description": (
                    "EVALUATE SPECIFICALLY: How well the user detached themselves from the AI "
                    "to judge its logic objectively."
                ),
            }
        ],
        "scales": [
            {
                "score": 1,
                "ai_label": "UNCRITICAL ACCEPTANCE",
                "claims": [
                    {
                        "label": {
                            "default_locale": "en",
                            "translations": {
                                "en": "The user is a 'Yes-man'. Blindly accepted the AI's first response."
                            },
                        },
                        "ai_description": (
                            "CRITICAL EVALUATION DIRECTIVE: Total failure of critical faculty. "
                            "The user exhibits sycophantic behavior..."
                        ),
                    },
                    {
                        "label": {
                            "default_locale": "en",
                            "translations": {"en": "No corrective move or objection presented."},
                        },
                        "ai_description": (
                            "ENFORCEMENT RULE: Falsify immediately if any objection exists. "
                            "Absolute zero tolerance."
                        ),
                    },
                ],
            },
            {
                "score": 2,
                "ai_label": "SUPERFICIAL REFINEMENT",
                "claims": [
                    {
                        "label": {
                            "default_locale": "en",
                            "translations": {"en": "The user requested changes, but they were only superficial."},
                        },
                        "ai_description": "CRITICAL EVALUATION DIRECTIVE: Engagement is purely cosmetic...",
                    }
                ],
            },
        ],
    }

    # Act
    DynamicSchema = compiler.build_dynamic_schema(schema_name="TestSchema", criteria=[mock_matrix_block])

    # Assert
    assert issubclass(DynamicSchema, BaseModel)

    # Get the field description which contains the compiled BARS matrix
    field_info = DynamicSchema.model_fields["blk_test_matrix"]
    compiled_desc = field_info.description

    # Target Snapshot format
    expected_snapshot = (
        "Critical Distance Score: ROLE: ADVERSARIAL AUDITOR... Evaluate the user's intellectual effort...\n\n"
        "TARGET ROW:\n"
        "- EVALUATE SPECIFICALLY: How well the user detached themselves from the AI to judge its logic "
        "objectively.\n\n\n"
        "EVALUATION MATRIX (BARS):\n"
        "- Score 1: UNCRITICAL ACCEPTANCE\n"
        "  * DIRECTIVE: CRITICAL EVALUATION DIRECTIVE: Total failure of critical faculty. The user exhibits "
        "sycophantic behavior...\n"
        "  * DIRECTIVE: ENFORCEMENT RULE: Falsify immediately if any objection exists. Absolute zero tolerance.\n"
        "- Score 2: SUPERFICIAL REFINEMENT\n"
        "  * DIRECTIVE: CRITICAL EVALUATION DIRECTIVE: Engagement is purely cosmetic...\n\n"
        "INSTRUCTION: Evaluate the core issue using the matrix above. "
        "Always return the final numerical evaluation with ONE decimal place (e.g. 4.2), "
        "so that the evaluation reflects exact nuance. You MUST return ONLY the exact numeric value."
    )

    assert compiled_desc == expected_snapshot, (
        f"Snapshot mismatch!\nEXPECTED:\n{expected_snapshot}\n\nACTUAL:\n{compiled_desc}"
    )


def test_prompt_compiler_dynamic_extraction_resilience() -> None:
    from backend_v2.models.enums import BlockDataType
    # Test that extracting justification still works
    compiler = PromptCompiler()

    mock_matrix = {
        "id": "blk_extract_test",
        "type": BlockDataType.FLOAT,
        "allow_decimals": True,
        "label": {"default_locale": "en", "translations": {"en": "Test Score"}},
        "ai_description": "Base Desc",
        "output_extensions": ["justification", "citation", "remediation_steps", "confidence"],
        "scales": [{"score": 1, "ai_label": "ONE", "claims": [{"label": "Claim 1", "ai_description": "Directive 1"}]}],
    }

    DynamicSchema = compiler.build_dynamic_schema("TestExtract", [mock_matrix])

    # Simulate LLM Response parsing
    llm_payload = {
        "reasoning_trace": "Let's think...",
        "evaluation_notes": "User was bad",
        "blk_extract_test_justification": "I gave a 1 because...",
        "blk_extract_test_cited_source_id": None,
        "blk_extract_test_cited_text_quote": "Yes man",
        "blk_extract_test_remediation_steps": ["Step 1", "Step 2"],
        "blk_extract_test_confidence": 95.5,
        "blk_extract_test": 1.0,
    }

    parsed = DynamicSchema.model_validate(llm_payload)
    assert getattr(parsed, "blk_extract_test") == 1.0
    assert getattr(parsed, "blk_extract_test_remediation_steps") == ["Step 1", "Step 2"]
    assert getattr(parsed, "blk_extract_test_confidence") == 95.5
    assert getattr(parsed, "reasoning_trace") == "Let's think..."
    assert getattr(parsed, "blk_extract_test_justification") == "I gave a 1 because..."
