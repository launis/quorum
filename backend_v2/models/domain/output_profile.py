"""Domain models for Output Profiles.

This module simply re-exports the V2 Core models to prevent duplicate
schemas under Pydantic strict validations.
"""

from backend_v2.models.v2_core import OutputProfile

__all__ = ["OutputProfile"]
