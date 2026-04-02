"""Legacy and Active hook definitions for the AI Orchestrator."""

# Initialize all hooks to trigger the @hook_registry.register decorators
from . import (
    archival,
    hydration,
    input_processing,
    integrity,
    linguistics,
    llm,
    metadata,
    metrics,
    references,
    reporting,
    scoring,
    security,
    synthesis,
    translation_hook,
    validation,
)

__all__ = [
    "archival",
    "hydration",
    "input_processing",
    "integrity",
    "linguistics",
    "llm",
    "metrics",
    "references",
    "reporting",
    "scoring",
    "security",
    "synthesis",
    "translation_hook",
    "validation",
    "metadata",
]

