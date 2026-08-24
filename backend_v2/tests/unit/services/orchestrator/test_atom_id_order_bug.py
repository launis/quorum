from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


def test_atom_id_is_first_field_in_shuffled_atoms_schema() -> None:
    """Tier 4 Bug Hunting: Reproduces the 'atom_id' omission bug.
    If atom_id is appended at the end of the JSON Schema, Gemini 2.5 Flash
    may drop it when generating long outputs (like exact_quote), causing
    AGENT_SCHEMA_VALIDATION_FAILED and crashing the execution.
    This test verifies that atom_id is strictly the first field in the
    generated AtomResponse schema.
    """
    compiler = PromptCompiler()

    # Create a dummy matrix block dict matching PromptBlock
    from backend_v2.models.enums import BlockDataType

    mock_matrix_block = {
        "id": "blk_1234567890abcdef",
        "slug": "test_matrix",
        "category_id": "matrix",
        "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
        "type": BlockDataType.FLOAT,
        "allow_decimals": True,
        "label": {
            "default_locale": "en",
            "translations": {"en": "Critical Distance Score", "fi": "Critical Distance Score"},
        },
        "ai_description": "ROLE: ADVERSARIAL AUDITOR... Evaluate the user's intellectual effort...",
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
                        "tda_assertions": [
                            {
                                "tda_id": "tda_11111111111111111111111111111111",
                                "concept_description": "Total failure of critical faculty...",
                                "inverse_evidence": False,
                                "aggregation_mode": "ALL_MUST_COMPLY",
                            }
                        ],
                    }
                ],
            }
        ],
    }

    from backend_v2.models.domain.prompt_blocks import PromptBlockAdapter

    dynamic_schema = compiler.build_dynamic_schema(
        schema_name="Step_Test_Response",
        criteria=[PromptBlockAdapter.validate_python(mock_matrix_block)],
        has_shuffled_atoms=True,
        target_locale="en",
        strictness_level=50,
    )

    # Extract the evaluations array schema
    schema_json = dynamic_schema.model_json_schema()

    # In Pydantic V2, nested models are in $defs
    # Find the AtomResponse schema in $defs
    defs = schema_json.get("$defs", {})
    atom_response_schema = None
    for def_name, def_schema in defs.items():
        if "AtomResponse" in def_name:
            atom_response_schema = def_schema
            break

    assert atom_response_schema is not None, "AtomResponse schema not found in $defs"

    # Get the ordered properties
    properties = atom_response_schema.get("properties", {})
    fields_list = list(properties.keys())

    assert len(fields_list) > 0, "AtomResponse has no fields"

    # THIS IS THE CRITICAL RED STATE ASSERTION:
    # atom_id MUST be the FIRST field so the LLM processes it before long text fields.
    assert fields_list[0] == "atom_id", f"Bug triggered! atom_id is not the first field. Field order: {fields_list}"
