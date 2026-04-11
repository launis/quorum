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
                            "ENFORCEMENT RULE: Falsify immediately if any objection exists. Absolute zero tolerance."
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
    expected_snapshot = "Evaluation object for Critical Distance Score"

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
        "output_extensions": ["justification", "remediation_steps", "confidence"],
        "scales": [{"score": 1, "ai_label": "ONE", "claims": [{"label": "Claim 1", "ai_description": "Directive 1"}]}],
    }

    DynamicSchema = compiler.build_dynamic_schema("TestExtract", [mock_matrix])

    # Simulate LLM Response parsing
    llm_payload = {
        "reasoning_trace": "Let's think...",
        "evaluation_notes": "User was bad",
        "blk_extract_test": {
            "step_3_logical_friction": "I gave a 1 because...",
            "extension_remediation_steps": ["Step 1", "Step 2"],
            "extension_confidence": 95.5,
            "step_4_final_score": 1.0,
        },
    }

    parsed = DynamicSchema.model_validate(llm_payload)
    assert parsed.blk_extract_test.step_4_final_score == 1.0  # type: ignore[attr-defined]
    assert parsed.blk_extract_test.extension_remediation_steps == ["Step 1", "Step 2"]  # type: ignore[attr-defined]
    assert parsed.blk_extract_test.extension_confidence == 95.5  # type: ignore[attr-defined]
    assert parsed.reasoning_trace == "Let's think..."  # type: ignore[attr-defined]
    assert parsed.blk_extract_test.step_3_logical_friction == "I gave a 1 because..."  # type: ignore[attr-defined]


def test_generate_mcp_instruction() -> None:
    compiler = PromptCompiler()

    # Test with no tools
    assert compiler.generate_mcp_instruction([]) == ""

    # Test with tools
    instruction = compiler.generate_mcp_instruction(["mcp_tavily_search", "mcp_other_tool"])

    # Verify the dynamic list is injected
    assert "mcp_tavily_search" in instruction
    assert "mcp_other_tool" in instruction

    # Verify the logic instructions explicitly encourage usage
    assert "proactively to search" in instruction
    assert "Stop data collection as soon as you have sufficient context." in instruction

def test_build_blind_evaluation_schema() -> None:
    compiler = PromptCompiler()
    DynamicSchema = compiler.build_blind_evaluation_schema("BlindTest")
    assert issubclass(DynamicSchema, BaseModel)
    
    llm_payload = {
        "evaluations": [
            {
                "atom_id": "test_hash_123",
                "quote": "This is a test.",
                "reasoning": "Simple logic.",
                "boolean": True
            }
        ]
    }
    parsed = DynamicSchema.model_validate(llm_payload)
    assert len(parsed.evaluations) == 1  # type: ignore[attr-defined]
    assert parsed.evaluations[0].atom_id == "test_hash_123"  # type: ignore[attr-defined]
    assert parsed.evaluations[0].boolean is True  # type: ignore[attr-defined]

def test_compile_blind_system_instruction() -> None:
    compiler = PromptCompiler()
    instruction_en = compiler.compile_blind_system_instruction("en")
    assert "Duck-Typing Token Shield" in instruction_en
    assert "exclusively in the 'en' language" in instruction_en
    
    instruction_fi = compiler.compile_blind_system_instruction("fi")
    assert "exclusively in the 'fi' language" in instruction_fi
