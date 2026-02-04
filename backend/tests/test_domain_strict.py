from backend.models.domain import DimensionResultItem, EvaluationResult


def test_evaluation_result_strict_validation():
    # 1. Valid Case (Standard 1-5)
    valid = EvaluationResult(
        matrix_id="test_matrix",
        scale_min=1,
        scale_max=5,
        total_score=4.5,
        dimensions=[
            DimensionResultItem(dimension_id="dim1", score=3, reasoning="ok")
        ],
        metadata={
             "luontiaika": "2026-01-01",
             "agentti": "Test",
             "vaihe": 1
        },
        metodologinen_loki="log",
        edellisen_vaiheen_validointi="ok",
        semanttinen_tarkistussumma="hash"
    )
    assert valid.total_score == 4.5

    # 2. Valid Case (Dynamic 1-10)
    valid_dynamic = EvaluationResult(
        matrix_id="test_matrix_10",
        scale_min=1,
        scale_max=10,
        total_score=9.0,
        dimensions=[],
        metadata={
             "luontiaika": "2026-01-01",
             "agentti": "Test",
             "vaihe": 1
        },
        metodologinen_loki="log",
        edellisen_vaiheen_validointi="ok",
        semanttinen_tarkistussumma="hash"
    )
    assert valid_dynamic.total_score == 9.0

    # 3. Invalid Case (Score > Max)
    try:
        EvaluationResult(
            matrix_id="test_fail",
            scale_min=1,
            scale_max=4,
            total_score=4.5, # FAIL
            dimensions=[],
            metadata={
                 "luontiaika": "2026-01-01",
                 "agentti": "Test",
                 "vaihe": 1
            },
            metodologinen_loki="log",
            edellisen_vaiheen_validointi="ok",
            semanttinen_tarkistussumma="hash"
        )
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "out of bounds" in str(e)

    # 4. Invalid Case (Dimension Score > Max)
    try:
        EvaluationResult(
            matrix_id="test_fail_dim",
            scale_min=1,
            scale_max=5,
            total_score=3,
            dimensions=[
                 DimensionResultItem(dimension_id="dim1", score=6, reasoning="bad") # FAIL
            ],
            metadata={
                 "luontiaika": "2026-01-01",
                 "agentti": "Test",
                 "vaihe": 1
            },
            metodologinen_loki="log",
            edellisen_vaiheen_validointi="ok",
            semanttinen_tarkistussumma="hash"
        )
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "dimension" in str(e).lower()

if __name__ == "__main__":
    test_evaluation_result_strict_validation()
    print("Strict Pydantic Validation Tests Passed!")
