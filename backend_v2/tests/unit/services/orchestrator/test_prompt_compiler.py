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
                                "tda_id": "tda_1111111111111111",
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
                                "tda_id": "tda_2222222222222222",
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
                                "tda_id": "tda_3333333333333333",
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
    expected_snapshot = (
        "Evaluation field for matrix block 'blk_1234567890abcdef' (Critical Distance Score). "
        "Objective: ROLE: ADVERSARIAL AUDITOR... Evaluate the user's intellectual effort..."
    )

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
                                "tda_id": "tda_4444444444444444",
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
            "semantic_reasoning": "None",
            "remediation_steps": "Do better",
            "confidence": 0.95,
        },
    }

    parsed = DynamicSchema.model_validate(llm_payload)
    assert parsed.blk_2234567890abcdef.semantic_reasoning == "None"  # type: ignore[attr-defined]
    assert parsed.reasoning_trace == "Let's think..."  # type: ignore[attr-defined]


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
    assert "Blind Extraction Engine" in instruction_en
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
            "computed_min": 1,
            "computed_max": 5,
            "label": {"default_locale": "en", "translations": {"en": "Test"}},
            "ai_description": "Test description",
        }
    ]

    from backend_v2.models.v2_core import PromptBlock

    result = compiler.compile_xml_rubrics([PromptBlock.model_validate(c) for c in mock_criteria], target_locale="en")

    assert "<ANTI_SYCOPHANCY_MANDATE>" in result
    assert "ANTI-SYCOPHANCY MANDATE:" in result
    assert "Speak like a strict professional auditor." in result


def test_dynamic_schema_descriptions_are_present() -> None:
    """Ensure dynamic schemas are enriched with semantic descriptions to guide the LLM."""
    from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

    compiler = PromptCompiler()

    # 1. Test build_blind_evaluation_schema
    BlindSchema = compiler.build_blind_evaluation_schema("BlindTest")
    assert BlindSchema.model_fields["evaluations"].description == "List of blind atomic evaluations."

    evaluations_field = BlindSchema.model_fields["evaluations"]
    assert evaluations_field.annotation is not None
    annotation_args = getattr(evaluations_field.annotation, "__args__", None)
    assert annotation_args is not None
    atom_response_model = annotation_args[0]
    assert (
        atom_response_model.model_fields["atom_id"].description
        == "Unique system identifier of the target evaluation atom."
    )  # noqa: E501
    assert (
        atom_response_model.model_fields["step_1_evidence_type"].description
        == "Type of evidence discovered (EXPLICIT_QUOTE, IMPLIED_INTENT, or NO_EVIDENCE)."
    )  # noqa: E501
    assert (
        atom_response_model.model_fields["step_2_quote"].description
        == "Literal verbatim quote containing the exact physical evidence from the source document. REQUIRED if evidence type is EXPLICIT_QUOTE."  # noqa: E501
    )  # noqa: E501
    assert (
        atom_response_model.model_fields["step_3_implicit_justification"].description
        == "Conclusive justification if intent is implied. Must be at least 20 words. Allowed ONLY if strictness < 70."  # noqa: E501
    )  # noqa: E501
    assert (
        atom_response_model.model_fields["step_4_reasoning"].description
        == "Strict analytical reasoning trace explaining the presence or absence of evidence."
    )  # noqa: E501
    assert (
        atom_response_model.model_fields["step_5_boolean"].description
        == "Final Boolean determination: True if rule is satisfied, False if violated or unsupported."
    )  # noqa: E501

    # 2. Test build_chunk_response_schema
    from pydantic import BaseModel

    class MockItem(BaseModel):
        val: str

    ChunkSchema = compiler.build_chunk_response_schema("ChunkTest", MockItem)
    assert (
        ChunkSchema.model_fields["chunk_id"].description
        == "The unique system identifier of the current execution chunk."
    )  # noqa: E501
    assert ChunkSchema.model_fields["records"].description == "List of records contained in this execution chunk."

    records_field = ChunkSchema.model_fields["records"]
    assert records_field.annotation is not None
    records_annotation_args = getattr(records_field.annotation, "__args__", None)
    assert records_annotation_args is not None
    chunk_record_model = records_annotation_args[0]
    assert (
        chunk_record_model.model_fields["original_id"].description
        == "The original system identifier of the source record."
    )  # noqa: E501
    assert (
        chunk_record_model.model_fields["payload"].description
        == "The validated item payload matching the target data schema."
    )  # noqa: E501

    # 3. Assert max_length constraints exist to limit LLM schema serving states
    from backend_v2.models.enums import SystemConcurrency
    from backend_v2.services.orchestrator.prompt_compiler import StrippedBaseTDAExtraction

    tda_schema = StrippedBaseTDAExtraction.model_json_schema()
    assert (
        tda_schema["properties"]["localized_anchors_found"]["maxItems"]
        == SystemConcurrency.SCHEMA_MAX_LOCALIZED_ANCHORS
    )  # noqa: E501

    blind_json_schema = BlindSchema.model_json_schema()
    assert blind_json_schema["properties"]["evaluations"]["maxItems"] == SystemConcurrency.SCHEMA_MAX_EVALUATIONS

    chunk_json_schema = ChunkSchema.model_json_schema()
    assert chunk_json_schema["properties"]["records"]["maxItems"] == SystemConcurrency.SCHEMA_MAX_CHUNK_RECORDS


def test_fsm_serving_state_safety_limits() -> None:
    """Varmistaa, että FSM-tilojen räjähdyksen estävät rajoitukset ovat riittävän tiukat."""
    from backend_v2.models.enums import SystemConcurrency

    # Vertex AI FSM -kääntäjä ei hyväksy liian suuria sisäkkäisiä taulukkorajoja.
    # Varmistetaan matemaattinen yläraja tilojen määrälle.
    assert SystemConcurrency.SCHEMA_MAX_LOCALIZED_ANCHORS <= 10
    assert SystemConcurrency.SCHEMA_MAX_EVALUATIONS <= 15
    assert SystemConcurrency.SCHEMA_MAX_CHUNK_RECORDS <= 15


def test_tda_extraction_schema_has_semantic_descriptions() -> None:
    """Varmistaa, että StrippedBaseTDAExtraction-luokan kentissä on semanttinen ohjeistus."""
    from backend_v2.services.orchestrator.prompt_compiler import StrippedBaseTDAExtraction

    override_desc = StrippedBaseTDAExtraction.model_fields["contextual_override"].description or ""
    quote_desc = StrippedBaseTDAExtraction.model_fields["exact_quote"].description or ""

    assert "exact_quote MUST be empty if True" in override_desc
    assert "MUST be empty if contextual_override is True" in quote_desc


def test_prompt_compiler_extreme_description_truncation() -> None:
    """Epic 56 Phase 4: Varmistaa, että erittäin pitkät ai_description-kentät säilytetään
    täydellisinä dynamic schema -kenttien kuvauksissa ilman keinotekoista typistämistä.
    """
    compiler = PromptCompiler()
    from backend_v2.models.enums import BlockDataType
    from backend_v2.models.v2_core import PromptBlock

    extreme_desc = "X" * 1000  # 1000 merkin pituinen ohjeistus
    mock_block = {
        "id": "blk_1234567890abcdef",
        "slug": "extreme_test",
        "category_id": "matrix",
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "type": BlockDataType.FLOAT,
        "allow_decimals": True,
        "scale_min": 1,
        "scale_max": 5,
        "label": {"default_locale": "en", "translations": {"en": "Extreme Score"}},
        "ai_description": extreme_desc,
        "scales": [
            {
                "score": 1,
                "ai_label": "ONE",
                "claims": [
                    {
                        "label": {"default_locale": "en", "translations": {"en": "Minimal Claim"}},
                        "ai_description": "Minimal claim AI description",
                        "tda_assertions": [
                            {
                                "tda_id": "tda_1111111111111111",
                                "ai_rule_description": "Assertion rule",
                                "inverse_evidence": False,
                                "aggregation_mode": "ALL_MUST_COMPLY",
                            }
                        ],
                    }
                ],
            }
        ],
    }

    DynamicSchema = compiler.build_dynamic_schema(
        schema_name="ExtremeSchema", criteria=[PromptBlock.model_validate(mock_block)]
    )

    field_info = DynamicSchema.model_fields["blk_1234567890abcdef"]
    compiled_desc = field_info.description
    assert compiled_desc is not None

    # Kuvauksen tulee sisältää koko extreme_desc ilman typistystä
    assert extreme_desc in compiled_desc
    assert len(compiled_desc) > 1000


def test_build_dynamic_schema_instruction_with_custom_category() -> None:
    compiler = PromptCompiler()
    from backend_v2.models.v2_core import PromptBlock

    mock_block = {
        "id": "blk_599645bd5baf44e2",
        "slug": "custom_instruction",
        "category_id": "system_rule",
        "type": "instruction",
        "label": {"default_locale": "en", "translations": {"en": "Instruction Label"}},
        "description": {"default_locale": "en", "translations": {"en": "Instruction Description"}},
        "ai_description": "Custom instruction details.",
    }

    DynamicSchema = compiler.build_dynamic_schema(
        schema_name="CustomInstructionSchema",
        criteria=[PromptBlock.model_validate(mock_block)],
    )

    # The field type must be a simple string (str), NOT a nested Pydantic model class
    field_info = DynamicSchema.model_fields["blk_599645bd5baf44e2"]
    assert field_info.annotation is str

    # The schema must parse valid string payloads perfectly
    llm_payload = {
        "step_1_reasoning_trace": "Some reasoning trace.",
        "evaluation_notes": "Qualitative evaluation notes.",
        "blk_599645bd5baf44e2": "Verification completed successfully.",
    }
    parsed = DynamicSchema.model_validate(llm_payload)
    assert parsed.blk_599645bd5baf44e2 == "Verification completed successfully."  # type: ignore[attr-defined]
