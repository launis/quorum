import json
from types import SimpleNamespace

from pydantic.json_schema import models_json_schema

from backend_v2.services.orchestrator.schema_factory import SchemaFactory


def resolve_i18n(label, locale):
    return label

def test_schema_factory_max_length_vertex_ai_bug():
    """Regression test for Vertex AI 400 'too many states for serving'.
    
    Ensures that when dynamically generating Pydantic schemas using SchemaFactory,
    the resulting JSON Schema does NOT contain 'maxItems' or 'maxLength' for lists,
    as nested array limits multiply the Vertex AI JSON parser state machine exponentially,
    causing 400 BadRequest with 'too many states for serving' on complex models (e.g., Matrix).
    """
    factory = SchemaFactory(resolve_i18n_fn=resolve_i18n)

    # Mocking PromptBlock to bypass strict Pydantic validation for the test
    criteria = [
        SimpleNamespace(
            id="blk_matrix_1",
            type="instruction",
            category_id=SimpleNamespace(value="matrix"),
            label="Matrix Block",
            output_extensions=["confidence", "risk_flag", "justification"],
            scales=[],
            ai_description="Test matrix block."
        ),
        SimpleNamespace(
            id="blk_eval_1",
            type="instruction",
            category_id=SimpleNamespace(value="criteria"),
            label="Evaluation Block",
            output_extensions=[],
            scales=[]
        )
    ]

    Model = factory.build_dynamic_schema(
        schema_name="TestSchema",
        criteria=criteria,
        has_shuffled_atoms=True,
        target_locale="fi",
        strictness_level=100,
        source_document_ids=["doc_1", "doc_2"],
        allowed_atom_ids=["a1", "a2"],
        allowed_dynamic_keys=["k1"],
        max_evaluations=7
    )

    _, schema = models_json_schema([(Model, "validation")])

    schema_str = json.dumps(schema)

    assert "maxItems" not in schema_str, "maxItems found in JSON Schema, which causes Vertex AI 400 errors!"
    assert "maxLength" not in schema_str, "maxLength found in JSON Schema, which causes Vertex AI 400 errors!"
