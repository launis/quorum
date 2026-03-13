# Initialize all hooks to trigger the @hook_registry.register decorators
from . import (
    archival,
    hydration,
    input_processing,
    integrity,
    linguistics,
    llm,
    metrics,
    references,
    reporting,
    scoring,
    search,
    security,
    validation,
    metadata,
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
    "search",
    "security",
    "validation",
    "metadata",
]
