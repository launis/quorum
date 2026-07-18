import pytest

from backend_v2.models.dtos.dag_models import ExtractedAtom
from backend_v2.services.orchestrator.sliding_window_linker import SlidingWindowLinker


def test_sliding_window_linker_get_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that the sliding window correctly batches atoms with overlap."""

    class MockSettings:
        linker_max_atoms_per_window = 20

    monkeypatch.setattr("backend_v2.services.orchestrator.sliding_window_linker.get_settings", lambda: MockSettings())

    linker = SlidingWindowLinker(window_size=3, overlap=1)

    # Create dummy chunks (each list is one chunk containing atoms from a source)
    chunks = [
        [
            ExtractedAtom(
                tda_id="tda_0123456789abcdef", resolved_claim="claim 1", reasoning="reason 1", source_quote="quote 1"
            )
        ],
        [
            ExtractedAtom(
                tda_id="tda_0123456789abcde0", resolved_claim="claim 2", reasoning="reason 2", source_quote="quote 2"
            )
        ],
        [
            ExtractedAtom(
                tda_id="tda_0123456789abcde1", resolved_claim="claim 3", reasoning="reason 3", source_quote="quote 3"
            )
        ],
        [
            ExtractedAtom(
                tda_id="tda_0123456789abcde2", resolved_claim="claim 4", reasoning="reason 4", source_quote="quote 4"
            )
        ],
        [
            ExtractedAtom(
                tda_id="tda_0123456789abcde3", resolved_claim="claim 5", reasoning="reason 5", source_quote="quote 5"
            )
        ],
    ]

    windows = linker._get_sliding_windows(chunks)

    # Expected:
    # window 1: chunks[0, 1, 2]
    # window 2: chunks[2, 3, 4]
    assert len(windows) == 2

    assert len(windows[0]) == 3
    assert windows[0][0][0].tda_id == "tda_0123456789abcdef"
    assert windows[0][1][0].tda_id == "tda_0123456789abcde0"
    assert windows[0][2][0].tda_id == "tda_0123456789abcde1"

    assert len(windows[1]) == 3
    assert windows[1][0][0].tda_id == "tda_0123456789abcde1"
    assert windows[1][1][0].tda_id == "tda_0123456789abcde2"
    assert windows[1][2][0].tda_id == "tda_0123456789abcde3"


def test_sliding_window_linker_get_windows_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test sliding window with empty chunks."""

    class MockSettings:
        linker_max_atoms_per_window = 20

    monkeypatch.setattr("backend_v2.services.orchestrator.sliding_window_linker.get_settings", lambda: MockSettings())
    linker = SlidingWindowLinker(window_size=3, overlap=1)
    windows = linker._get_sliding_windows([])
    assert len(windows) == 0


def test_sliding_window_linker_get_windows_small(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test sliding window with chunks less than window size."""

    class MockSettings:
        linker_max_atoms_per_window = 20

    monkeypatch.setattr("backend_v2.services.orchestrator.sliding_window_linker.get_settings", lambda: MockSettings())
    linker = SlidingWindowLinker(window_size=3, overlap=1)
    chunks = [
        [
            ExtractedAtom(
                tda_id="tda_0123456789abcdef", resolved_claim="claim 1", reasoning="reason 1", source_quote="quote 1"
            )
        ],
        [
            ExtractedAtom(
                tda_id="tda_0123456789abcde0", resolved_claim="claim 2", reasoning="reason 2", source_quote="quote 2"
            )
        ],
    ]
    windows = linker._get_sliding_windows(chunks)
    assert len(windows) == 1
    assert len(windows[0]) == 2


def test_sliding_window_linker_subdivides_oversized_chunks(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that chunks exceeding max_atoms are subdivided."""

    class MockSettings:
        linker_max_atoms_per_window = 2

    monkeypatch.setattr("backend_v2.services.orchestrator.sliding_window_linker.get_settings", lambda: MockSettings())

    linker = SlidingWindowLinker(window_size=3, overlap=1)
    chunk = [
        ExtractedAtom(
            tda_id=f"tda_0000000{i}", resolved_claim=f"claim {i}", reasoning=f"reason {i}", source_quote=f"quote {i}"
        )
        for i in range(5)
    ]

    windows = linker._get_sliding_windows([chunk])

    assert len(windows) == 3
    assert len(windows[0]) == 1
    assert len(windows[0][0]) == 2
    assert windows[0][0][0].tda_id == "tda_00000000"

    assert len(windows[1]) == 1
    assert len(windows[1][0]) == 2
    assert windows[1][0][0].tda_id == "tda_00000002"

    assert len(windows[2]) == 1
    assert len(windows[2][0]) == 1
    assert windows[2][0][0].tda_id == "tda_00000004"


from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.orchestrator.sliding_window_linker import LinkerResponseDTO


def test_linker_response_dto_schema_no_dicts() -> None:
    payload = {
        "dependencies": [
            {
                "child_alias": "a1",
                "parent_dependencies": [
                    {
                        "edge_reasoning": "Logical dependency",
                        "tda_id": "a0",
                        "expected_status": ExecutionStatus.PASSED,
                    }
                ],
            }
        ]
    }

    model = LinkerResponseDTO.model_validate(payload)

    assert len(model.dependencies) == 1
    assert model.dependencies[0].child_alias == "a1"
    assert len(model.dependencies[0].parent_dependencies) == 1
    assert model.dependencies[0].parent_dependencies[0].tda_id == "a0"

    schema = LinkerResponseDTO.model_json_schema()
    assert schema["properties"]["dependencies"]["type"] == "array"
