"""Legacy and Active hook definitions for the AI Orchestrator."""

# Initialize all hooks to trigger the @hook_registry.register decorators
from . import (  # pragma: no cover
    archival,
    atom_flattening,
    hydration,
    input_processing,
    integrity,
    interaction_hook,
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

__all__ = [  # pragma: no cover
    "archival",
    "atom_flattening",
    "hydration",
    "input_processing",
    "integrity",
    "interaction_hook",
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
