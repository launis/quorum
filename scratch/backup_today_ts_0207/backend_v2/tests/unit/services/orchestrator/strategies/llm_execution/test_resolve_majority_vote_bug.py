from backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker import resolve_majority_vote


def test_resolve_majority_vote_drops_base_fields_and_matrices():
    # Arrange: 2 LLM results (ensemble mode)
    results = [
        {
            "reasoning_trace": "test reasoning 1",
            "evaluation_notes": "notes 1",
            "blk_matrix_1": {"exact_quote": "q1", "contextual_override": False},
            "blk_text_1": {"exact_quote": "t1", "contextual_override": False},
        },
        {
            "reasoning_trace": "test reasoning 2",
            "evaluation_notes": "notes 2",
            "blk_matrix_1": {"exact_quote": "q1", "contextual_override": False},
            "blk_text_1": {"exact_quote": "t1", "contextual_override": False},
        },
    ]

    from unittest.mock import MagicMock

    matrix_block = MagicMock()
    matrix_block.id = "blk_matrix_1"
    matrix_block.category_id = "matrix"
    matrix_block.type = "matrix"

    text_block = MagicMock()
    text_block.id = "blk_text_1"
    text_block.category_id = "text"
    text_block.type = "text"

    chunk_criteria = [matrix_block, text_block]

    # Act
    final_res = resolve_majority_vote(
        results=results,
        has_shuffled_atoms=False,
        chunk_criteria=chunk_criteria,
        user_payload="",
        global_source_text="This is the source text containing q1 and t1.",
        strictness_level=1,
    )

    # Assert
    # The bug causes final_res to only contain {"blk_text_1": ...} and drop everything else!
    assert "reasoning_trace" in final_res, "reasoning_trace was dropped!"
    assert "evaluation_notes" in final_res, "evaluation_notes was dropped!"
    assert "blk_matrix_1" in final_res, "blk_matrix_1 (matrix) was dropped!"
