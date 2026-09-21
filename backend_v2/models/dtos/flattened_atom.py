"""Flattened Atom DTO module.

Provides the strict Pydantic V2 schema for individual shuffled extraction items
(No Naked Dicts rule), decoupled from engine execution requests to prevent circular imports.
"""

from __future__ import annotations

from backend_v2.models.domain.matrix import (
    FlattenedAtom as FlattenedAtom,
)
from backend_v2.models.domain.matrix import (
    _coerce_to_tuple as _coerce_to_tuple,
)

__all__ = ["FlattenedAtom", "_coerce_to_tuple"]
