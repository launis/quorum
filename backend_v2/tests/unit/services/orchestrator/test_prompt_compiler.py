import typing

import pytest
from pydantic import BaseModel

from backend_v2.exceptions import AppException
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.dtos.prompt import LLMContextDataDTO
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


def test_prompt_compiler_deep_matrix_schema() -> None:
    compiler = PromptCompiler()

    from backend_v2.models.enums import BlockDataType

    # Mocking the JSON structure we confirmed in Phase 1
    mock_matrix_block = {
        "id": "blk_1234567890abcdef",
        "slug": "test_matrix",
        "category_id": "matrix",
        "description": {"translations": {"en": "Desc", "fi": "Desc"}},
        "type": BlockDataType.FLOAT,
        "allow_decimals": True,
        "label": {
            "translations": {"en": "Critical Distance Score", "fi": "Critical Distance Score"},
        },
        "ai_description": "ROLE: ADVERSARIAL AUDITOR... Evaluate the user's intellectual effort...",
        "rows": [
            {
                "label": {
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
                            "translations": {
                                "en": "The user is a 'Yes-man'. Blindly accepted the AI's first response.",
                                "fi": "Mock",
                            },
                        },
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
                            "translations": {"en": "No corrective move or objection presented.", "fi": "Mock"},
                        },
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
                            "translations": {
                                "en": "The user requested changes, but they were only superficial.",
                                "fi": "Mock",
                            },
                        },
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
    from backend_v2.models.domain.prompt_blocks import PromptBlockAdapter

    DynamicSchema = compiler.build_dynamic_schema(
        schema_name="TestSchema", criteria=[PromptBlockAdapter.validate_python(mock_matrix_block)], strictness_level=50
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
        "description": {"translations": {"en": "Desc", "fi": "Desc"}},
        "type": BlockDataType.FLOAT,
        "allow_decimals": True,
        "label": {"translations": {"en": "Test Score", "fi": "Test Score"}},
        "ai_description": "Base Desc",
        "output_extensions": ["justification", "remediation_steps", "confidence"],
        "scales": [
            {
                "score": 1,
                "ai_label": "ONE",
                "claims": [
                    {
                        "label": {"translations": {"en": "Claim 1", "fi": "Claim 1"}},
                        "tda_assertions": [
                            {
                                "tda_id": "tda_44444444444444444444444444444444",
                                "concept_description": "Directive 1 valid description",
                                "inverse_evidence": False,
                                "aggregation_mode": "ALL_MUST_COMPLY",
                            }
                        ],
                    }
                ],
            }
        ],  # noqa: E501
    }

    from backend_v2.models.domain.prompt_blocks import PromptBlockAdapter

    DynamicSchema = compiler.build_dynamic_schema(
        "TestExtract", [PromptBlockAdapter.validate_python(mock_matrix)], strictness_level=50
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
    records_annotation_args = typing.get_args(records_field.annotation)
    assert len(records_annotation_args) > 0
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
    from backend_v2.models.domain.prompt_blocks import PromptBlockAdapter
    from backend_v2.models.enums import BlockDataType

    extreme_desc = "X" * 1000  # 1000 merkin pituinen ohjeistus
    mock_block = {
        "id": "blk_1234567890abcdef",
        "slug": "extreme_test",
        "category_id": "matrix",
        "description": {"translations": {"en": "Desc", "fi": "Desc"}},
        "type": BlockDataType.FLOAT,
        "allow_decimals": True,
        "label": {"translations": {"en": "Extreme Score", "fi": "Extreme Score"}},
        "ai_description": extreme_desc,
        "scales": [
            {
                "score": 1,
                "ai_label": "ONE",
                "claims": [
                    {
                        "label": {
                            "translations": {"en": "Minimal Claim", "fi": "Minimal Claim"},
                        },
                        "tda_assertions": [
                            {
                                "tda_id": "tda_11111111111111111111111111111111",
                                "concept_description": "Assertion rule valid description",
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
        schema_name="ExtremeSchema", criteria=[PromptBlockAdapter.validate_python(mock_block)], strictness_level=50
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
    from backend_v2.models.domain.prompt_blocks import PromptBlockAdapter

    mock_block = {
        "id": "blk_599645bd5baf44e2",
        "slug": "custom_instruction",
        "category_id": "system_rule",
        "type": "instruction",
        "label": {"translations": {"en": "Instruction Label", "fi": "Instruction Label"}},
        "description": {
            "translations": {"en": "Instruction Description", "fi": "Instruction Description"},
        },
        "instruction_text": "Custom instruction details.",
    }

    DynamicSchema = compiler.build_dynamic_schema(
        schema_name="CustomInstructionSchema",
        criteria=[PromptBlockAdapter.validate_python(mock_block)],
        strictness_level=50,
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
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.step import ExpectedInput

    compiler = PromptCompiler()
    state = ExecutionInputsDTO(
        raw_inputs={
            "normal_input": "user data",
            "chat_input": "chat data",
        },
        dynamic_inputs={"step_1": "ai drafted this"},
    )

    expected_inputs = [
        ExpectedInput(
            input_key="normal_input",
            label=I18nText(translations={"en": "Normal"}),
            description=I18nText(translations={"en": "Desc"}),
            is_chat_history=False,
            input_modes=["text"],
            required=True,
        ),
        ExpectedInput(
            input_key="chat_input",
            label=I18nText(translations={"en": "Chat"}),
            description=I18nText(translations={"en": "Desc"}),
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


def test_build_xml_context_assignment_mode() -> None:
    """Verify that ExpectedInput with 'assignment' mode wraps into
    <assignment_context> and excludes <user_payload>.
    """
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.step import ExpectedInput

    compiler = PromptCompiler()
    state = ExecutionInputsDTO(
        raw_inputs={
            "assignment_brief": "Analyze the financial liquidity risk under Basel III.",
            "deliverable": "Here is the comprehensive liquidity risk report.",
        },
    )

    expected_inputs = [
        ExpectedInput(
            input_key="assignment_brief",
            label=I18nText(translations={"en": "Task Brief", "fi": "Tehtävänanto"}),
            description=I18nText(translations={"en": "Brief instructions"}),
            is_chat_history=False,
            input_modes=["assignment"],
            required=True,
        ),
        ExpectedInput(
            input_key="deliverable",
            label=I18nText(translations={"en": "Candidate Report"}),
            description=I18nText(translations={"en": "Evaluated text"}),
            is_chat_history=False,
            input_modes=["file", "paste"],
            required=True,
        ),
    ]

    input_mappings = {
        "brief": "$inputs.assignment_brief",
        "doc": "$inputs.deliverable",
    }

    xml = compiler.build_xml_context(input_mappings, state, "en", expected_inputs=expected_inputs)

    # brief: assignment mode -> strictly wrapped in <assignment_context>, NEVER <user_payload>
    assert '<matrix_input source_id="brief">' in xml
    brief_section = xml.split('source_id="brief"')[1].split("</matrix_input>")[0]
    assert (
        "<assignment_context>\n<![CDATA[Analyze the financial liquidity risk under Basel III.]]>\n</assignment_context>"
        in brief_section
    )
    assert "<user_payload>" not in brief_section

    # doc: file/paste mode -> wrapped in <user_payload>, NOT <assignment_context>
    assert '<matrix_input source_id="doc">' in xml
    doc_section = xml.split('source_id="doc"')[1].split("</matrix_input>")[0]
    assert (
        "<user_payload>\n<![CDATA[Here is the comprehensive liquidity risk report.]]>\n</user_payload>" in doc_section
    )
    assert "<assignment_context>" not in doc_section


def test_build_xml_context_endorsed_deliverable_provenance() -> None:
    """Verify that ExpectedInput with is_endorsed_deliverable=True emits
    <document_provenance>ENDORSED_FINAL_DELIVERABLE</document_provenance> in metadata.
    """
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.step import ExpectedInput
    from backend_v2.services.orchestrator.prompt_compiler import _InputMetaDTO

    # Verify _InputMetaDTO contract
    meta_dto = _InputMetaDTO(
        label="Final Deliverable",
        desc="Candidate product text",
        is_chat_history=False,
        input_modes=["file"],
        is_endorsed_deliverable=True,
    )
    assert meta_dto.is_endorsed_deliverable is True

    compiler = PromptCompiler()
    state = ExecutionInputsDTO(
        raw_inputs={
            "deliverable": "Strategic transformation roadmap deliverable text.",
            "standard_doc": "Supporting document.",
        },
    )

    expected_inputs = [
        ExpectedInput(
            input_key="deliverable",
            label=I18nText(translations={"en": "Final Deliverable"}),
            description=I18nText(translations={"en": "Candidate deliverable"}),
            is_chat_history=False,
            input_modes=["file"],
            required=True,
            is_endorsed_deliverable=True,
        ),
        ExpectedInput(
            input_key="standard_doc",
            label=I18nText(translations={"en": "Standard Doc"}),
            description=I18nText(translations={"en": "Standard"}),
            is_chat_history=False,
            input_modes=["file"],
            required=False,
            is_endorsed_deliverable=False,
        ),
    ]

    input_mappings = {
        "doc_deliv": "$inputs.deliverable",
        "doc_std": "$inputs.standard_doc",
    }

    xml = compiler.build_xml_context(input_mappings, state, "en", expected_inputs=expected_inputs)

    # doc_deliv: must emit <document_provenance>ENDORSED_FINAL_DELIVERABLE</document_provenance>
    # inside <document_metadata>
    assert '<matrix_input source_id="doc_deliv">' in xml
    deliv_section = xml.split('source_id="doc_deliv"')[1].split("</matrix_input>")[0]
    assert "<document_provenance>ENDORSED_FINAL_DELIVERABLE</document_provenance>" in deliv_section
    assert (
        "<user_payload>\n<![CDATA[Strategic transformation roadmap deliverable text.]]>\n</user_payload>"
        in deliv_section
    )

    # doc_std: must NOT emit <document_provenance>
    assert '<matrix_input source_id="doc_std">' in xml
    std_section = xml.split('source_id="doc_std"')[1].split("</matrix_input>")[0]
    assert "<document_provenance>" not in std_section


def test_input_meta_dto_is_assignment_predicate() -> None:
    """Verify is_assignment predicate behavior on _InputMetaDTO and ExpectedInput."""
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.step import ExpectedInput
    from backend_v2.services.orchestrator.prompt_compiler import _InputMetaDTO

    meta_assignment = _InputMetaDTO(
        label="Assignment",
        desc="Desc",
        is_chat_history=False,
        input_modes=["assignment", "file", "paste"],
    )
    assert meta_assignment.is_assignment is True

    meta_standard = _InputMetaDTO(
        label="Standard",
        desc="Desc",
        is_chat_history=False,
        input_modes=["file", "paste"],
    )
    assert meta_standard.is_assignment is False

    meta_empty = _InputMetaDTO(
        label="Empty",
        desc="Desc",
        is_chat_history=False,
        input_modes=[],
    )
    assert meta_empty.is_assignment is False

    # Also verify ExpectedInput domain model predicate parity
    ei_assignment = ExpectedInput(
        input_key="assignment_doc",
        label=I18nText(translations={"en": "Brief"}),
        description=I18nText(translations={"en": "Desc"}),
        is_chat_history=False,
        input_modes=["assignment", "file"],
        required=False,
    )
    assert ei_assignment.is_assignment is True

    ei_standard = ExpectedInput(
        input_key="standard_doc",
        label=I18nText(translations={"en": "Doc"}),
        description=I18nText(translations={"en": "Desc"}),
        is_chat_history=False,
        input_modes=["file", "paste"],
        required=True,
    )
    assert ei_standard.is_assignment is False


def test_build_xml_context_unmapped_inputs_raises_app_exception() -> None:
    """Verify that an unmapped $inputs reference triggers immediate Fail-Fast AppException."""
    from backend_v2.exceptions import AppException, ErrorCodes
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.step import ExpectedInput

    compiler = PromptCompiler()
    state = ExecutionInputsDTO(
        raw_inputs={
            "declared_input": "Valid content",
            "undeclared_input": "Orphan content",
        }
    )
    expected_inputs = [
        ExpectedInput(
            input_key="declared_input",
            label=I18nText(translations={"en": "Declared"}),
            description=I18nText(translations={"en": "Desc"}),
            is_chat_history=False,
            input_modes=["file", "paste"],
            required=True,
        )
    ]

    # Reference an input that is not in expected_inputs ($inputs.undeclared_input)
    input_mappings = {
        "doc": "$inputs.undeclared_input",
    }

    with pytest.raises(AppException) as exc_info:
        compiler.build_xml_context(
            input_mappings=input_mappings,
            state_data=state,
            target_locale="en",
            expected_inputs=expected_inputs,
        )

    assert exc_info.value.error_code == ErrorCodes.CONFIGURATION_ERROR
    assert "Unmapped input reference '$inputs.undeclared_input'" in str(exc_info.value)
    assert exc_info.value.details.get("source_path") == "$inputs.undeclared_input"
    assert exc_info.value.details.get("base_path") == "$inputs.undeclared_input"


def test_all_standard_input_types_wrapped_in_user_payload() -> None:
    """Verify that standard deliverable inputs are wrapped in <user_payload> with <document_metadata>."""
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.step import ExpectedInput

    compiler = PromptCompiler()
    standard_keys = [
        ("product_text", "Candidate Deliverable Memo"),
        ("reflection_text", "Metacognitive Self-Assessment"),
        ("source_evidence", "Primary Corpus Verification Dossier"),
        ("compliance_framework", "Statutory Safety Charter"),
    ]

    state = ExecutionInputsDTO(
        raw_inputs={key: f"Content for {key}" for key, _ in standard_keys},
    )

    expected_inputs = [
        ExpectedInput(
            input_key=key,
            label=I18nText(translations={"en": label_en}),
            description=I18nText(translations={"en": f"Description for {key}"}),
            ai_description=f"COGNITIVE DIRECTIVE: Evaluate {key}",
            is_chat_history=False,
            input_modes=["file", "paste"],
            required=True,
        )
        for key, label_en in standard_keys
    ]

    input_mappings = {key: f"$inputs.{key}" for key, _ in standard_keys}

    xml = compiler.build_xml_context(
        input_mappings=input_mappings,
        state_data=state,
        target_locale="en",
        expected_inputs=expected_inputs,
    )

    for key, label_en in standard_keys:
        assert f'<matrix_input source_id="{key}">' in xml
        section = xml.split(f'source_id="{key}"')[1].split("</matrix_input>")[0]

        # Metadata checks
        assert "<document_metadata>" in section
        assert f"<document_id>{key}</document_id>" in section
        assert f"<document_name>{label_en}</document_name>" in section
        assert f"<ai_context_mandate>COGNITIVE DIRECTIVE: Evaluate {key}</ai_context_mandate>" in section
        assert "</document_metadata>" in section

        # User payload encapsulation checks
        assert f"<user_payload>\n<![CDATA[Content for {key}]]>\n</user_payload>" in section

        # Strict non-leakage checks: standard deliverables must never be wrapped in assignment context
        assert "<assignment_context>" not in section
        assert "<ai_draft_context>" not in section


def test_extract_value_from_state() -> None:
    compiler = PromptCompiler()
    state = LLMContextDataDTO(
        inputs={
            "a": "123",
            "b": {"c": "456"},
            "steps.a": "789",
            "step_eval": {
                "outputs": {
                    "results": [{"atom_id": "a1", "exact_quotes": ["quote"]}],
                    "claim_analysis": {
                        "step_1_premise": "Test premise",
                        "step_2_scan": "Scan details",
                    },
                    "simple_key": "Simple value",
                }
            },
        }
    )
    assert compiler._extract_value_from_state("a", state) == "123"
    assert compiler._extract_value_from_state("b.c", state) == "456"
    assert compiler._extract_value_from_state("steps.a", state) == "789"

    # Test dictionary formatting and context suppression of results
    extracted_xml = compiler._extract_value_from_state("steps.step_eval", state)
    assert "<CLAIM_ANALYSIS>" in extracted_xml
    assert "<Premise>" in extracted_xml
    assert "<Simple_Key>" in extracted_xml
    assert "results" not in extracted_xml

    # Test error cases
    with pytest.raises(AppException):
        compiler._extract_value_from_state(123, state)  # type: ignore[arg-type]

    with pytest.raises(AppException):
        compiler._extract_value_from_state("missing.path", state)


def test_compile_static_and_dynamic_instructions() -> None:
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock
    from backend_v2.models.enums import BlockDataType, PromptBlockCategory

    compiler = PromptCompiler()
    block = SystemRulePromptBlock(
        id="blk_1111222233334444",
        slug="static_inst",
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.STRING,
        label=I18nText(translations={"en": "Label"}),
        description=I18nText(translations={"en": "Desc"}),
        instruction_text="Static instruction directive",
    )
    dynamic_block = SystemRulePromptBlock(
        id="blk_2222333344445555",
        slug="dyn_inst",
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.STRING,
        label=I18nText(translations={"en": "Dyn Label"}),
        description=I18nText(translations={"en": "Dyn Desc"}),
        instruction_text="Dynamic instruction directive",
    )

    static_res = compiler.compile_static_instructions([block], "en")
    assert isinstance(static_res, str)

    dyn_res = compiler.compile_dynamic_instructions([dynamic_block], "en")
    assert isinstance(dyn_res, str)


def test_compile_chunk_payload_instruction() -> None:
    compiler = PromptCompiler()
    chunk_prompt = compiler.compile_chunk_payload_instruction("chunk_1", "raw payload <test>")
    assert "chunk_1" in chunk_prompt
    assert "<user_payload>" in chunk_prompt
    assert "<![CDATA[raw payload <test>]]>" in chunk_prompt


def test_calibrate_strictness_exceptions_and_none() -> None:
    compiler = PromptCompiler()
    assert compiler.calibrate_strictness(None) == ""
    with pytest.raises(AppException):
        compiler.calibrate_strictness("invalid_string")  # type: ignore[arg-type]


def test_get_schema_healing_prompt_strictness_100() -> None:
    compiler = PromptCompiler()
    prompt = compiler.get_schema_healing_prompt(
        "Error detail", is_logical_error=False, is_eof=False, strictness_level=100
    )
    assert "[STRICTNESS OVERRIDE ACTIVE: level >= 100]" in prompt
    assert "'contextual_override'" in prompt


def test_calibrate_strictness_values() -> None:
    compiler = PromptCompiler()
    assert compiler.calibrate_strictness(50) == "SCORING_STRICTNESS: 50/100"
    assert compiler.calibrate_strictness(150) == "SCORING_STRICTNESS: 100/100"
    assert compiler.calibrate_strictness(-10) == "SCORING_STRICTNESS: 0/100"


def test_get_schema_healing_prompt_eof_and_logical() -> None:
    compiler = PromptCompiler()
    eof_prompt = compiler.get_schema_healing_prompt("EOF error", is_logical_error=False, is_eof=True)
    assert "[SYSTEM: EOF DETECTED]" in eof_prompt

    logical_prompt = compiler.get_schema_healing_prompt("Logical mismatch", is_logical_error=True, is_eof=False)
    assert "[SYSTEM: STRICT LOGICAL COMPLIANCE REQUIRED]" in logical_prompt
    assert "Logical mismatch" in logical_prompt


def test_build_xml_context_with_alias_engine_and_generic_path() -> None:
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.step import ExpectedInput
    from backend_v2.utils.alias_engine import AliasEngine

    compiler = PromptCompiler()
    alias_engine = AliasEngine()
    expected_inputs = [
        ExpectedInput(
            input_key="doc1",
            label=I18nText(translations={"en": "Doc 1", "fi": "Dok 1"}),
            description=I18nText(translations={"en": "Desc 1", "fi": "Kuv 1"}),
            required=True,
            input_modes=["file"],
            ai_description="Context mandate for doc1",
        )
    ]
    state_data = ExecutionInputsDTO(
        raw_inputs={"doc1": "Document content"},
        dynamic_inputs={"other_var": 42},
    )
    input_mappings = {"doc1": "$inputs.doc1", "other": "other_var"}

    result = compiler.build_xml_context(
        input_mappings=input_mappings,
        state_data=state_data,
        target_locale="en",
        expected_inputs=expected_inputs,
        alias_engine=alias_engine,
    )
    assert "<matrix_input source_id=" in result
    assert "<ai_context_mandate>Context mandate for doc1</ai_context_mandate>" in result
    assert "42" in result


def test_extract_value_from_state_complex_types() -> None:
    class DummyModel(BaseModel):
        field_a: str
        count: int

    compiler = PromptCompiler()
    state = LLMContextDataDTO(
        inputs={
            "model": DummyModel(field_a="hello", count=10),
            "nested": {"nested_model": DummyModel(field_a="world", count=20)},
            "number": 99,
            "flag": True,
            "json_list": ["item1", "item2"],
        }
    )
    assert "hello" in compiler._extract_value_from_state("model", state)
    assert "world" in compiler._extract_value_from_state("nested.nested_model.field_a", state)
    assert compiler._extract_value_from_state("number", state) == "99"
    assert compiler._extract_value_from_state("flag", state) == "True"


def test_prompt_compiler_expected_inputs_validation_branches() -> None:
    """Test expected_inputs handling with non-ExpectedInput items and empty input_keys."""
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.step import ExpectedInput

    compiler = PromptCompiler()
    expected_inputs = [
        "not_an_expected_input",
        ExpectedInput.model_construct(
            input_key="",
            label=I18nText(translations={"en": "Empty", "fi": "Tyhjä"}),
            description=I18nText(translations={"en": "Desc", "fi": "Kuv"}),
            required=False,
            input_modes=["text"],
        ),
    ]
    xml = compiler.build_xml_context(
        input_mappings={},
        state_data=ExecutionInputsDTO(),
        target_locale="en",
        expected_inputs=expected_inputs,
    )
    assert xml == ""


def test_extract_value_from_llm_context_data_dto() -> None:
    """Test _extract_value_from_state with LLMContextDataDTO branches."""
    from backend_v2.exceptions import AppException
    from backend_v2.models.dtos.prompt import LLMContextDataDTO
    from backend_v2.models.execution_core import ExecutionMetadata

    compiler = PromptCompiler()
    dto = LLMContextDataDTO(
        inputs={"doc1": "Document One Content", "plain": "Plain Value"},
        raw_inputs={"raw_doc": "Raw Doc Content", "plain_raw": "Plain Raw"},
        metadata=ExecutionMetadata(workflow_version=42),
    )

    # 1. inputs.path in inputs
    assert compiler._extract_value_from_state("inputs.doc1", dto) == "Document One Content"

    # 2. inputs.path in raw_inputs
    assert compiler._extract_value_from_state("inputs.raw_doc", dto) == "Raw Doc Content"

    # 3. inputs.path missing -> raises AppException
    with pytest.raises(AppException):
        compiler._extract_value_from_state("inputs.nonexistent", dto)

    # 4. direct clean_path in inputs
    assert compiler._extract_value_from_state("plain", dto) == "Plain Value"

    # 5. direct clean_path in raw_inputs
    assert compiler._extract_value_from_state("plain_raw", dto) == "Plain Raw"

    # 6. dot notation fallback on LLMContextDataDTO
    assert compiler._extract_value_from_state("metadata.workflow_version", dto) == "42"


def test_extract_value_from_execution_inputs_dto() -> None:
    """Test _extract_value_from_state with ExecutionInputsDTO branches."""
    from backend_v2.exceptions import AppException
    from backend_v2.models.dtos.hook_state import ExecutionInputsDTO

    compiler = PromptCompiler()
    exec_inputs = ExecutionInputsDTO(
        raw_inputs={"chat": "Chat transcript"},
        dynamic_inputs={"summary": "Summary text"},
    )

    # 1. inputs.key in raw_inputs
    assert compiler._extract_value_from_state("inputs.chat", exec_inputs) == "Chat transcript"

    # 2. inputs.key in dynamic_inputs
    assert compiler._extract_value_from_state("inputs.summary", exec_inputs) == "Summary text"

    # 3. inputs.key missing -> raises AppException
    with pytest.raises(AppException):
        compiler._extract_value_from_state("inputs.missing_key", exec_inputs)


def test_format_value_for_xml_branches() -> None:
    """Test _extract_value_from_state formatting branches for scalar in dict and lists."""
    compiler = PromptCompiler()

    # Dict where value is not a Mapping (line 419)
    state1 = LLMContextDataDTO(inputs={"data": {"SIMPLE_SECTION": "simple text value"}})
    res_scalar_in_dict = compiler._extract_value_from_state("data", state1)
    assert "<SIMPLE_SECTION>" in res_scalar_in_dict
    assert "simple text value" in res_scalar_in_dict
    assert "</SIMPLE_SECTION>" in res_scalar_in_dict

    # Non-str, non-mapping value (line 423)
    state2 = LLMContextDataDTO(inputs={"items": ["item1", "item2"]})
    res_list = compiler._extract_value_from_state("items", state2)
    assert "item1" in res_list
    assert "item2" in res_list
