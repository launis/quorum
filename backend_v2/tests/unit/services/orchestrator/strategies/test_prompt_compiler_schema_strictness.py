from unittest.mock import AsyncMock
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


def test_prompt_compiler_strict_atom_schema_descriptions() -> None:
    """Tier 4 RCA Test: Ensures that the dynamic schema for shuffled atoms explicitly
    forbids hallucinating new atoms and strictly mandates atom_id mapping.
    """
    compiler = PromptCompiler()

    # Build dynamic schema
    DynamicSchema = compiler.build_dynamic_schema(
        schema_name="TestSchema",
        criteria=[],
        has_shuffled_atoms=True,
        target_locale="fi",
        strictness_level=50,
    )

    schema_json = DynamicSchema.model_json_schema()

    # Assert Evaluations description is strict against hallucinations
    evals_prop = schema_json["properties"]["evaluations"]
    assert "ONLY the exact atoms explicitly listed" in evals_prop["description"]
    assert "Do NOT hallucinate" in evals_prop["description"]

    # Assert atom_id description is strict
    atom_response_ref = evals_prop["items"]["$ref"].split("/")[-1]
    atom_id_prop = schema_json["$defs"][atom_response_ref]["properties"]["atom_id"]
    assert "MUST exactly match" in atom_id_prop["description"]


def test_prompt_compiler_no_confusing_id_examples() -> None:
    """Tier 4 RCA Test: Ensures that we do not use confusing 'sr_...' examples
    in the schema descriptions or anti-id mandates which causes Gemini 2.5 to
    drop the atom_id entirely.
    """
    compiler = PromptCompiler()

    # Build dynamic schema
    DynamicSchema = compiler.build_dynamic_schema(
        schema_name="TestSchema",
        criteria=[],
        has_shuffled_atoms=True,
        target_locale="fi",
        strictness_level=50,
    )

    schema_json = DynamicSchema.model_json_schema()

    # Assert atom_id description does not contain sr_
    evals_prop = schema_json["properties"]["evaluations"]
    atom_response_ref = evals_prop["items"]["$ref"].split("/")[-1]
    atom_id_prop = schema_json["$defs"][atom_response_ref]["properties"]["atom_id"]

    assert "sr_" not in atom_id_prop["description"], "Schema description must not contain confusing sr_ example"

    # Assert anti_id_mandate does not contain sr_
    xml = compiler.compile_xml_rubrics(criteria=[], target_locale="fi")
    assert "sr_" not in xml, "Anti-ID mandate must not contain confusing sr_ example"
