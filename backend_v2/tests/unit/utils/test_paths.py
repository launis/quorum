from backend_v2.utils.paths import get_forensic_input_path


def test_get_forensic_input_path() -> None:
    path = get_forensic_input_path("exec123", "test-key-!@#")
    assert path == "executions/exec123/inputs/input_test-key-.md"
