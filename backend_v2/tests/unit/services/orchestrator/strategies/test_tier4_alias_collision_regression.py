from unittest.mock import AsyncMock
"""Regression test: Verify no parallel alias system exists in LLMNodeStrategy.

Tier 4 RCA proved that llm.py had a parallel alias system (_apply_alias_chunks_and_audit)
that created conflicting doc IDs (doc1..docN starting from 1) and <source ID="..." label="...">
XML wrappers inside the data, bypassing AliasEngine entirely. This caused:
1. literal_error: LLM used label attribute instead of ID
2. doc0 vs doc1 numbering mismatch between AliasEngine and the parallel system

This test ensures the parallel system is never reintroduced.
"""

from pathlib import Path

# Read source directly from disk to avoid .pyc cache issues with inspect.getsource
_LLM_PY_PATH = Path(__file__).resolve().parents[5] / "services" / "orchestrator" / "strategies" / "llm.py"
_REGISTRY_PATH = Path(__file__).resolve().parents[5] / "core" / "registry.py"


def test_no_parallel_alias_system_in_llm_strategy() -> None:
    """Verify _apply_alias_chunks_and_audit and src_counter are absent from llm.py code."""
    raw_source = _LLM_PY_PATH.read_text(encoding="utf-8")

    # Filter out comment lines to avoid false positives from removal notes
    code_lines = [line for line in raw_source.splitlines() if line.strip() and not line.strip().startswith("#")]
    source = "\n".join(code_lines)

    # The parallel alias function must not exist in actual code
    assert "_apply_alias_chunks_and_audit" not in source, (
        "REGRESSION: _apply_alias_chunks_and_audit() was reintroduced in llm.py. "
        "This function creates a parallel alias system that conflicts with AliasEngine."
    )

    # The src_counter pattern must not exist in actual code
    assert "src_counter" not in source, (
        "REGRESSION: src_counter was reintroduced in llm.py. "
        "Source document aliasing must go through AliasEngine exclusively."
    )


def test_no_source_xml_wrapping_in_llm_strategy() -> None:
    """Verify llm.py does not inject <source ID=... label=...> XML tags into data."""
    source = _LLM_PY_PATH.read_text(encoding="utf-8")

    # The f-string pattern that injected <source ID="..." label="..."> wrappers
    assert 'label=\\"{k}\\"' not in source, (
        'REGRESSION: <source ID="..."> XML wrapping was reintroduced in llm.py. '
        "Data must remain unwrapped; prompt_compiler.build_xml_context() handles XML wrapping."
    )

    # Also verify the raw XML pattern is absent from non-comment lines
    non_comment_lines = [line for line in source.splitlines() if line.strip() and not line.strip().startswith("#")]
    non_comment_source = "\n".join(non_comment_lines)
    assert '<source ID="' not in non_comment_source, (
        'REGRESSION: <source ID="..."> XML wrapping found in non-comment code in llm.py.'
    )


def test_alias_engine_initialized_clean() -> None:
    """Verify AliasEngine is initialized without pre-populated alias_map from metadata."""
    source = _LLM_PY_PATH.read_text(encoding="utf-8")

    # Must not read alias_map from hook_state.metadata to initialize AliasEngine
    assert 'metadata.get("alias_map"' not in source, (
        "REGRESSION: AliasEngine is being initialized from hook_state.metadata['alias_map']. "
        "AliasEngine must be initialized clean; prompt_compiler.build_xml_context() "
        "registers aliases via AliasEngine.register()."
    )


def test_registry_excludes_source_id_from_matrix_extensions() -> None:
    """Verify source_id is in core_aliases set for both matrix and criteria extensions."""
    source = _REGISTRY_PATH.read_text(encoding="utf-8")

    # Verify 'source_id' appears in core_aliases set alongside known members
    lines = source.splitlines()
    found_count = 0
    for line in lines:
        stripped = line.strip()
        if "core_aliases" in stripped and "source_id" in stripped and "contextual_override" in stripped:
            found_count += 1

    # Must appear at least twice (once for matrix extensions, once for criteria extensions)
    assert found_count >= 2, (
        f"REGRESSION: 'source_id' must be in core_aliases set in BOTH matrix and criteria "
        f"extension loops in registry.py. Found only {found_count} occurrences."
    )
