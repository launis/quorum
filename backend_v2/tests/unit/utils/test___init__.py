import backend_v2.utils


def test_utils_init() -> None:
    """Test utils init."""
    assert "__all__" in dir(backend_v2.utils)
    assert backend_v2.utils.__all__ == [
        "get_forensic_input_path",
        "inflate",
        "normalize_evaluation_input",
        "ranked_round_robin_select",
    ]
