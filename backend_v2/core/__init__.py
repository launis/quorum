"""Core Backend Services and Registries.

This package contains core singletons and components for the Quorum V2 backend.
"""

from backend_v2.core.registry import (
    GridSchemaStrategy,
    HeroInsightSchemaStrategy,
    MarkdownSchemaStrategy,
)

__all__ = [
    "GridSchemaStrategy",
    "HeroInsightSchemaStrategy",
    "MarkdownSchemaStrategy",
]
