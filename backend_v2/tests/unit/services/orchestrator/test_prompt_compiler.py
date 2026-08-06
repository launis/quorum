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
        "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
        "type": BlockDataType.FLOAT,
        "allow_decimals": True,
        "scale_min": 1,
        "scale_max": 5,
        "label": {
            "default_locale": "en",
            "translations": {"en": "Critical Distance Score", "fi": "Critical Distance Score"},
        },
        "ai_description": "ROLE: ADVERSARIAL AUDITOR... Evaluate the user's intellectual effort...",
        "rows": [
            {
                "label": {
                    "default_locale": "en",
                    "translations": {"en": "Critical Distance Score", "fi": "Critical Distance Score"},
                },
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
                                "en": "The user is a 'Yes-man'. Blindly accepted the AI's first response.",
                                "fi": "Mock",
                            },
                        },
                        "ai_description": (
                            "CRITICAL EVALUATION DIRECTIVE: Total failure of critical faculty. "
                            "The user exhibits sycophantic behavior..."
                        ),
                        "tda_assertions": [
                            {
                                "tda_id": "tda_11111111111111111111111111111111",
                                "concept_description": "Total failure of critical faculty...",
                                "inverse_evidence": False,
                                "aggregation_mode": "ALL_MUST_COMPLY",
                            }
                        ],
                    },
                    {
                        "label": {
                            "default_locale": "en",
                            "translations": {"en": "No corrective move or objection presented.", "fi": "Mock"},
                        },
                        "ai_description": (
                            "ENFORCEMENT RULE: Falsify immediately if any objection exists. Absolute zero tolerance."
                        ),
                        "tda_assertions": [
                            {
                                "tda_id": "tda_22222222222222222222222222222222",
                                "concept_description": "Falsify immediately if any objection exists.",
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
                            "translations": {
                                "en": "The user requested changes, but they were only superficial.",
                                "fi": "Mock",
                            },
                        },
                        "ai_description": "CRITICAL EVALUATION DIRECTIVE: Engagement is purely cosmetic...",
                        "tda_assertions": [
                            {
                                "tda_id": "tda_33333333333333333333333333333333",
                                "concept_description": "Engagement is purely cosmetic...",
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
        schema_name="TestSchema", criteria=[PromptBlock.model_validate(mock_matrix_block)], strictness_level=50
    )  # noqa: E501

    # Assert
    assert issubclass(DynamicSchema, BaseModel)

    # Get the field description which contains the compiled BARS matrix
    matrix_model = DynamicSchema.model_fields["global_matrices"].annotation
    field_info = matrix_model.model_fields["blk_1234567890abcdef"]  # type: ignore[union-attr]
    compiled_desc = field_info.description

    # Target Snapshot format
    expected_snapshot = (
        "Global matrix evaluation for 'blk_1234567890abcdef' (Critical Distance Score). "
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
        "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
        "type": BlockDataType.FLOAT,
        "allow_decimals": True,
        "scale_min": 1,
        "scale_max": 5,
        "label": {"default_locale": "en", "translations": {"en": "Test Score", "fi": "Test Score"}},
        "ai_description": "Base Desc",
        "output_extensions": ["justification", "remediation_steps", "confidence"],
        "scales": [
            {
                "score": 1,
                "ai_label": "ONE",
                "claims": [
                    {
                        "label": {"default_locale": "en", "translations": {"en": "Claim 1", "fi": "Claim 1"}},
                        "ai_description": "Directive 1",
                        "tda_assertions": [
                            {
                                "tda_id": "tda_44444444444444444444444444444444",
                                "concept_description": "Directive 1",
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

    DynamicSchema = compiler.build_dynamic_schema(
        "TestExtract", [PromptBlock.model_validate(mock_matrix)], strictness_level=50
    )

    # Simulate LLM Response parsing
    llm_payload = {
        "reasoning_trace": "Let's think...",
        "evaluation_notes": "User was bad",
        "global_matrices": {
            "blk_2234567890abcdef": {
                "semantic_reasoning": "Valid reasoning",
                "remediation_steps": "Do better",
                "confidence": 0.95,
            }
        },
    }

    parsed = DynamicSchema.model_validate(llm_payload)
    assert parsed.global_matrices.blk_2234567890abcdef.semantic_reasoning == "Valid reasoning"  # type: ignore[attr-defined]
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


def test_prompt_compiler_architectural_integrity() -> None:
    """Suojelee arkkitehtuuria vahinkopoistoilta ja "salaa poistamisilta".
    Varmistaa, että molemmat evaluointistrategiat pysyvät olemassa.
    """
    from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

    msg1 = "CRITICAL: build_dynamic_schema on SALAA POISTETTU! Tämä rikkoo XAI-laajennukset ja 3D-matriisit."
    assert hasattr(PromptCompiler, "build_dynamic_schema"), msg1


def test_dynamic_schema_descriptions_are_present() -> None:
    """Ensure dynamic schemas are enriched with semantic descriptions to guide the LLM."""
    from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

    compiler = PromptCompiler()

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

    # 3. Assert max_length constraints DO NOT exist to limit LLM schema serving states
    from backend_v2.services.orchestrator.schema_factory import StrippedBaseTDAExtraction

    tda_schema = StrippedBaseTDAExtraction.model_json_schema()
    assert "localized_anchors_found" not in tda_schema["properties"]

    chunk_json_schema = ChunkSchema.model_json_schema()
    assert "maxItems" not in chunk_json_schema["properties"]["records"]


def test_fsm_serving_state_safety_limits() -> None:
    """Varmistaa, että FSM-tilojen räjähdyksen estävät rajoitukset ovat riittävän tiukat."""
    from backend_v2.settings import get_settings

    # Vertex AI FSM -kääntäjä ei hyväksy liian suuria sisäkkäisiä taulukkorajoja.
    # Varmistetaan matemaattinen yläraja tilojen määrälle.
    assert get_settings().schema_max_localized_anchors <= 30
    assert get_settings().schema_max_evaluations <= 30
    assert get_settings().schema_max_chunk_records <= 30


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
        "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
        "type": BlockDataType.FLOAT,
        "allow_decimals": True,
        "scale_min": 1,
        "scale_max": 5,
        "label": {"default_locale": "en", "translations": {"en": "Extreme Score", "fi": "Extreme Score"}},
        "ai_description": extreme_desc,
        "scales": [
            {
                "score": 1,
                "ai_label": "ONE",
                "claims": [
                    {
                        "label": {
                            "default_locale": "en",
                            "translations": {"en": "Minimal Claim", "fi": "Minimal Claim"},
                        },
                        "ai_description": "Minimal claim AI description",
                        "tda_assertions": [
                            {
                                "tda_id": "tda_11111111111111111111111111111111",
                                "concept_description": "Assertion rule",
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
        schema_name="ExtremeSchema", criteria=[PromptBlock.model_validate(mock_block)], strictness_level=50
    )

    matrix_model = DynamicSchema.model_fields["global_matrices"].annotation
    field_info = matrix_model.model_fields["blk_1234567890abcdef"]  # type: ignore[union-attr]
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
        "label": {"default_locale": "en", "translations": {"en": "Instruction Label", "fi": "Instruction Label"}},
        "description": {
            "default_locale": "en",
            "translations": {"en": "Instruction Description", "fi": "Instruction Description"},
        },
        "ai_description": "Custom instruction details.",
    }

    DynamicSchema = compiler.build_dynamic_schema(
        schema_name="CustomInstructionSchema", criteria=[PromptBlock.model_validate(mock_block)], strictness_level=50
    )

    # The field type must be a simple string (str), NOT a nested Pydantic model class
    field_info = DynamicSchema.model_fields["blk_599645bd5baf44e2"]
    assert field_info.annotation is str

    # The schema must parse valid string payloads perfectly
    llm_payload = {
        "reasoning_trace": "Some reasoning trace.",
        "evaluation_notes": "Qualitative evaluation notes.",
        "blk_599645bd5baf44e2": "Verification completed successfully.",
    }
    parsed = DynamicSchema.model_validate(llm_payload)
    assert parsed.blk_599645bd5baf44e2 == "Verification completed successfully."  # type: ignore[attr-defined]


def test_build_xml_context() -> None:
    from backend_v2.models.v2_core import ExpectedInput, I18nText

    compiler = PromptCompiler()
    state = {
        "inputs": {
            "normal_input": "user data",
            "chat_input": "chat data",
        },
        "steps": {"step_1": "ai drafted this"},
    }

    expected_inputs = [
        ExpectedInput(
            input_key="normal_input",
            label=I18nText(default_locale="en", translations={"en": "Normal"}),
            description=I18nText(default_locale="en", translations={"en": "Desc"}),
            is_chat_history=False,
            input_modes=["text"],
            required=True,
        ),
        ExpectedInput(
            input_key="chat_input",
            label=I18nText(default_locale="en", translations={"en": "Chat"}),
            description=I18nText(default_locale="en", translations={"en": "Desc"}),
            is_chat_history=True,
            input_modes=["text"],
            required=True,
        ),
    ]

    input_mappings = {
        "src_1": "$inputs.normal_input",
        "src_2": "$inputs.chat_input",
        "src_3": "$steps.step_1",
    }

    xml = compiler.build_xml_context(input_mappings, state, "en", expected_inputs=expected_inputs)

    # src_1: normal input -> <user_payload> wrapper
    assert '<matrix_input source_id="src_1">' in xml
    assert "<user_payload>\n<![CDATA[user data]]>\n</user_payload>" in xml

    # src_2: chat input -> NO wrapper
    assert '<matrix_input source_id="src_2">' in xml
    assert "<user_payload>" not in xml.split('source_id="src_2"')[1].split("</matrix_input>")[0]
    assert "<![CDATA[chat data]]>" in xml

    # src_3: step output -> <ai_draft_context> wrapper
    assert '<matrix_input source_id="src_3">' in xml
    assert "<ai_draft_context>\n<![CDATA[ai drafted this]]>\n</ai_draft_context>" in xml


def test_extract_value_from_state() -> None:
    compiler = PromptCompiler()
    state = {"a": "123", "b": {"c": "456"}, "steps": {"a": "789"}}
    assert compiler._extract_value_from_state("a", state) == "123"
    assert compiler._extract_value_from_state("b.c", state) == "456"
    assert compiler._extract_value_from_state("steps.a", state) == "789"


def test_calibrate_strictness() -> None:
    compiler = PromptCompiler()
    assert "SCORING_STRICTNESS: 0/100" in compiler.calibrate_strictness(0)
    assert "SCORING_STRICTNESS: 20/100" in compiler.calibrate_strictness(20)
    assert "SCORING_STRICTNESS: 50/100" in compiler.calibrate_strictness(50)
    assert "SCORING_STRICTNESS: 80/100" in compiler.calibrate_strictness(80)
    assert "SCORING_STRICTNESS: 100/100" in compiler.calibrate_strictness(100)


def test_get_schema_healing_prompt() -> None:
    compiler = PromptCompiler()
    assert "EOF DETECTED" in compiler.get_schema_healing_prompt("err", False, True)
    assert "STRICT LOGICAL COMPLIANCE" in compiler.get_schema_healing_prompt("err", True, False)
    assert "STRICT JSON SCHEMA VALIDATION FAILED" in compiler.get_schema_healing_prompt("err", False, False)
