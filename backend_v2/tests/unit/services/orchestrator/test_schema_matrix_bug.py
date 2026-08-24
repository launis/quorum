import json
from pathlib import Path

import pytest

from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.services.orchestrator.schema_factory import SchemaFactory


@pytest.fixture
def schema_factory() -> SchemaFactory:
    return SchemaFactory(resolve_i18n_fn=lambda lbl, loc: lbl)


def test_schema_matrix_bug_repro(schema_factory: SchemaFactory) -> None:
    """TDD Repro for the Matrix Schema Validation Bug (Epic 56).

    When has_shuffled_atoms=True, matrix blocks are extracted into `global_matrices`
    instead of being output at the root `eval_{index}` layer.
    """
    # 1. Setup Mock Criteria using real seed data to avoid deep validation errors
    seed_path = Path("backend_v2/seed/seed_data.json")
    with open(seed_path, encoding="utf-8") as f:
        seed_data = json.load(f)

    raw_blocks = seed_data.get("prompt_blocks", [])
    matrix_blocks = [b for b in raw_blocks if b.get("category_id") == "matrix"]
    protocol_blocks = [b for b in raw_blocks if b.get("category_id") == "protocol"]

    assert len(matrix_blocks) > 0, "Seed data must contain at least one matrix block"
    assert len(protocol_blocks) > 0, "Seed data must contain at least one protocol block"

    # Use one protocol and one matrix block exactly as they are in production, but strip extensions
    matrix_block_raw = matrix_blocks[0]
    protocol_block_raw = protocol_blocks[0]
    matrix_block_raw["output_extensions"] = []
    protocol_block_raw["output_extensions"] = []

    criteria = [
        PromptBlock.model_validate(protocol_block_raw),
        PromptBlock.model_validate(matrix_block_raw),
    ]

    # 2. Build the Schema with has_shuffled_atoms=True
    DynamicSchema = schema_factory.build_dynamic_schema(
        schema_name="TestSchema",
        criteria=criteria,
        has_shuffled_atoms=True,
        strictness_level=100,
    )

    # 3. Mock LLM Output
    # We now expect 'global_matrices' at the root layer, and the matrix_id as a nested key.
    llm_output = {
        "reasoning_trace": "test reasoning",
        "evaluation_notes": "test notes",
        "evaluations": [
            {
                "atom_id": "tda_123",
                "used_source_aliases": [],
                "rule_internalization": "test",
                "source_document_aliases": [],
                "exact_quotes": [],
                "reasoning_steps": "test",
                "falsification_argument": "test",
                "decision": True,
                "semantic_reasoning": "atom reasoning",
            }
        ],
        "global_matrices": {matrix_block_raw["id"]: {"semantic_reasoning": "test reasoning for global matrix"}},
    }

    # 4. Verify Pydantic strictly accepts this structure
    result = DynamicSchema.model_validate(llm_output)

    # 5. Verify the parsed result has the global matrices structured properly
    assert hasattr(result, "global_matrices")
    matrices = result.global_matrices
    matrix_evaluation = getattr(matrices, matrix_block_raw["id"])
    assert matrix_evaluation.semantic_reasoning == "test reasoning for global matrix"
