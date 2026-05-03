"""Storage path utilities to enforce Single Source of Truth."""

def get_forensic_input_path(execution_id: str, input_key: str) -> str:
    """Returns the deterministic storage path for a forensic input."""
    safe_key = "".join(c for c in input_key if c.isalnum() or c in ("_", "-"))
    return f"executions/{execution_id}/inputs/input_{safe_key}.md"
