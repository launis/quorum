import re
from pathlib import Path

from backend_v2.models.v2_core import ReportDataDTO


def test_report_data_dto_contract_parity() -> None:
    """Tier 3 / Phase 1: Contract Parity Gate
    Asserts that the Python ReportDataDTO strictly matches the Dart ReportDataDto
    at the JSON serialization level.
    """
    dart_file_path = (
        Path(__file__).parent.parent.parent.parent.parent
        / "client_app_v2"
        / "lib"
        / "features"
        / "execution"
        / "models"
        / "report_data_v2_dto.dart"
    )

    assert dart_file_path.exists(), f"Dart DTO not found at {dart_file_path}"

    with open(dart_file_path, encoding="utf-8") as f:
        dart_content = f.read()

    # Extract all @JsonKey(name: 'something') from Dart definition
    dart_keys = set(re.findall(r"@JsonKey\(\s*name:\s*'([^']+)'\s*\)", dart_content))

    # Get Pydantic keys
    pydantic_keys = set(ReportDataDTO.model_fields.keys())

    # We ignore execution diagnostics metadata that might not be synced 100% in some older versions,
    # but since this is strict parity, they should be identical.
    missing_in_dart = pydantic_keys - dart_keys
    missing_in_python = dart_keys - pydantic_keys

    assert not missing_in_dart, f"Python ReportDataDTO has fields missing in Dart: {missing_in_dart}"
    assert not missing_in_python, f"Dart ReportDataDto has fields missing in Python: {missing_in_python}"
