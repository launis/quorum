from pydantic import BaseModel

from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


def test_prompt_compiler_deep_matrix_schema() -> None:
    compiler = PromptCompiler()

    from backend_v2.models.enums import BlockDataType

    # Mocking the JSON structure we confirmed in Phase 1
    mock_matrix_block = {
        "id": "blk_1234567890abcdef",
        "slug": "test_matrix",
        "category_id": "matrix",
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "type": BlockDataType.FLOAT,
        "allow_decimals": True,
        "scale_min": 1,
        "scale_max": 5,
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
                        "tda_assertions": [
                            {
                                "tda_id": "tda_mock1111",
                                "ai_rule_description": "Total failure of critical faculty...",
                                "inverse_evidence": False,
                                "aggregation_mode": "ALL_MUST_COMPLY",
                            }
                        ],
                    },
                    {
                        "label": {
                            "default_locale": "en",
                            "translations": {"en": "No corrective move or objection presented."},
                        },
                        "ai_description": (
                            "ENFORCEMENT RULE: Falsify immediately if any objection exists. Absolute zero tolerance."
                        ),
                        "tda_assertions": [
                            {
                                "tda_id": "tda_mock2222",
                                "ai_rule_description": "Falsify immediately if any objection exists.",
                                "inverse_evidence": False,
                                "aggregation_mode": "ALL_MUST_COMPLY",
                            }
                        ],
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
                        "tda_assertions": [
                            {
                                "tda_id": "tda_mock3333",
                                "ai_rule_description": "Engagement is purely cosmetic...",
                                "inverse_evidence": False,
                                "aggregation_mode": "ALL_MUST_COMPLY",
                            }
                        ],
                    }
                ],
            },
        ],
    }

    # Act
    from backend_v2.models.v2_core import PromptBlock

    DynamicSchema = compiler.build_dynamic_schema(
        schema_name="TestSchema", criteria=[PromptBlock.model_validate(mock_matrix_block)]
    )  # noqa: E501

    # Assert
    assert issubclass(DynamicSchema, BaseModel)

    # Get the field description which contains the compiled BARS matrix
    field_info = DynamicSchema.model_fields["blk_1234567890abcdef"]
    compiled_desc = field_info.description

    # Target Snapshot format
    expected_snapshot = "Evaluation object for blk_1234567890abcdef"

    assert compiled_desc == expected_snapshot, (
        f"Snapshot mismatch!\nEXPECTED:\n{expected_snapshot}\n\nACTUAL:\n{compiled_desc}"
    )


def test_prompt_compiler_dynamic_extraction_resilience() -> None:
    from backend_v2.models.enums import BlockDataType

    # Test that extracting justification still works
    compiler = PromptCompiler()

    mock_matrix = {
        "id": "blk_2234567890abcdef",
        "slug": "extract_test",
        "category_id": "matrix",
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "type": BlockDataType.FLOAT,
        "allow_decimals": True,
        "scale_min": 1,
        "scale_max": 5,
        "label": {"default_locale": "en", "translations": {"en": "Test Score"}},
        "ai_description": "Base Desc",
        "output_extensions": ["justification", "remediation_steps", "confidence"],
        "scales": [
            {
                "score": 1,
                "ai_label": "ONE",
                "claims": [
                    {
                        "label": {"default_locale": "en", "translations": {"en": "Claim 1"}},
                        "ai_description": "Directive 1",
                        "tda_assertions": [
                            {
                                "tda_id": "tda_mock4444",
                                "ai_rule_description": "Directive 1",
                                "inverse_evidence": False,
                                "aggregation_mode": "ALL_MUST_COMPLY",
                            }
                        ],
                    }
                ],
            }
        ],  # noqa: E501
    }

    from backend_v2.models.v2_core import PromptBlock

    DynamicSchema = compiler.build_dynamic_schema("TestExtract", [PromptBlock.model_validate(mock_matrix)])

    # Simulate LLM Response parsing
    llm_payload = {
        "step_1_reasoning_trace": "Let's think...",
        "evaluation_notes": "User was bad",
        "blk_2234567890abcdef": {
            "step_3_logical_friction": "I gave a 1 because...",
            "extension_remediation_steps": "Step 1\nStep 2",
            "extension_confidence": 95.5,
        },
    }

    parsed = DynamicSchema.model_validate(llm_payload)
    assert parsed.blk_2234567890abcdef.extension_remediation_steps == "Step 1\nStep 2"  # type: ignore[attr-defined]
    assert parsed.blk_2234567890abcdef.extension_confidence == 95.5  # type: ignore[attr-defined]
    assert parsed.reasoning_trace == "Let's think..."  # type: ignore[attr-defined]
    assert parsed.blk_2234567890abcdef.step_3_logical_friction == "I gave a 1 because..."  # type: ignore[attr-defined]


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
    from backend_v2.services.orchestrator.prompt_compiler import EvidenceType, PromptCompiler

    compiler = PromptCompiler()
    DynamicSchema = compiler.build_blind_evaluation_schema("BlindTest")
    assert issubclass(DynamicSchema, BaseModel)

    llm_payload = {
        "evaluations": [
            {
                "atom_id": "test_hash_123",
                "step_1_evidence_type": EvidenceType.EXPLICIT_QUOTE,
                "step_2_quote": "This is a test.",
                "step_4_reasoning": "Simple logic.",
                "step_5_boolean": True,
            }
        ]
    }
    parsed = DynamicSchema.model_validate(llm_payload, context={"strictness_level": 50})
    assert len(parsed.evaluations) == 1  # type: ignore[attr-defined]
    assert parsed.evaluations[0].atom_id == "test_hash_123"  # type: ignore[attr-defined]
    assert parsed.evaluations[0].step_5_boolean is True  # type: ignore[attr-defined]


def test_atom_response_fail_fast_anti_laziness() -> None:
    import pytest
    from pydantic import ValidationError

    from backend_v2.services.orchestrator.prompt_compiler import EvidenceType, PromptCompiler

    compiler = PromptCompiler()
    DynamicSchema = compiler.build_blind_evaluation_schema("BlindTest")

    # EXPLICIT_QUOTE missing quote
    with pytest.raises(ValidationError) as exc:
        DynamicSchema.model_validate(
            {
                "evaluations": [
                    {
                        "atom_id": "1",
                        "step_1_evidence_type": EvidenceType.EXPLICIT_QUOTE,
                        "step_4_reasoning": "Reason",
                        "step_5_boolean": True,
                    }
                ]
            },
            context={"strictness_level": 50},
        )
    assert "Quote required for EXPLICIT_QUOTE" in str(exc.value)

    # IMPLIED_INTENT short justification
    with pytest.raises(ValidationError) as exc:
        DynamicSchema.model_validate(
            {
                "evaluations": [
                    {
                        "atom_id": "1",
                        "step_1_evidence_type": EvidenceType.IMPLIED_INTENT,
                        "step_3_implicit_justification": "Too short.",
                        "step_4_reasoning": "Reason",
                        "step_5_boolean": True,
                    }
                ]
            },
            context={"strictness_level": 50},
        )
    assert "Justification too short for IMPLIED_INTENT" in str(exc.value)

    # NO_EVIDENCE with True boolean
    with pytest.raises(ValidationError) as exc:
        DynamicSchema.model_validate(
            {
                "evaluations": [
                    {
                        "atom_id": "1",
                        "step_1_evidence_type": EvidenceType.NO_EVIDENCE,
                        "step_4_reasoning": "Reason",
                        "step_5_boolean": True,
                    }
                ]
            },
            context={"strictness_level": 50},
        )
    assert "Cannot be True with NO_EVIDENCE" in str(exc.value)

    # Valid IMPLIED_INTENT validation context > 70 strictness
    with pytest.raises(ValidationError) as exc:
        DynamicSchema.model_validate(
            {
                "evaluations": [
                    {
                        "atom_id": "1",
                        "step_1_evidence_type": EvidenceType.IMPLIED_INTENT,
                        "step_3_implicit_justification": (
                            "This is a sufficiently long justification that has more than twenty "
                            "words in it to satisfy the strict length requirement of the validator."
                        ),
                        "step_4_reasoning": "Reason",
                        "step_5_boolean": True,
                    }
                ]
            },
            context={"strictness_level": 85},
        )
    assert "Strictness >= 70 ei salli implisiittistä logiikkaa" in str(exc.value)


def test_compile_blind_system_instruction() -> None:
    compiler = PromptCompiler()
    instruction_en = compiler.compile_blind_system_instruction("en")
    assert "Duck-Typing Token Shield" in instruction_en
    assert "exclusively in the 'en' language" in instruction_en

    instruction_fi = compiler.compile_blind_system_instruction("fi")
    assert "exclusively in the 'fi' language" in instruction_fi


def test_prompt_compiler_architectural_integrity() -> None:
    """Suojelee arkkitehtuuria vahinkopoistoilta ja "salaa poistamisilta".
    Varmistaa, että molemmat evaluointistrategiat pysyvät olemassa.
    """
    from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

    msg1 = "CRITICAL: build_dynamic_schema on SALAA POISTETTU! Tämä rikkoo XAI-laajennukset ja 3D-matriisit."
    assert hasattr(PromptCompiler, "build_dynamic_schema"), msg1

    msg2 = (
        "CRITICAL: build_blind_evaluation_schema on SALAA POISTETTU! "
        "Tämä rikkoo Epic 20 Phase 7 sokeiden kokeilujen arkkitehtuurin."
    )
    assert hasattr(PromptCompiler, "build_blind_evaluation_schema"), msg2


def test_compile_xml_rubrics_anti_sycophancy() -> None:
    """Epic 29 Phase 2: Ensure Anti-Sycophancy XAI Header is injected into XML rubrics."""
    from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

    compiler = PromptCompiler()
    mock_criteria = [
        {
            "id": "blk_3234567890abcdef",
            "slug": "test",
            "category_id": "matrix",
            "description": {"default_locale": "en", "translations": {"en": "Desc"}},
            "type": "float",
            "scale_min": 1,
            "scale_max": 5,
            "label": {"default_locale": "en", "translations": {"en": "Test"}},
            "ai_description": "Test description",
        }
    ]

    from backend_v2.models.v2_core import PromptBlock

    result = compiler.compile_xml_rubrics([PromptBlock.model_validate(c) for c in mock_criteria], target_locale="en")

    assert "<ANTI_SYCOPHANCY_MANDATE>" in result
    assert "ANTI-SYCOPHANCY MANDATE:" in result
    assert "Speak like a strict professional auditor." in result
