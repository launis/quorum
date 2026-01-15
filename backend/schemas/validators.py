"""Validation Helper Module.

Reusable validators and structure checkers for Pydantic models.
Previously logic located in backend/hooks/validation.py.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


def verify_content_structure(
    history_text: str | None, 
    product_text: str | None, 
    reflection_text: str | None,
    min_chars: int = 100
) -> List[str]:
    """
    Verifies that the core content inputs have sufficient length for analysis.
    
    Args:
        history_text: The conversation history text.
        product_text: The product text.
        reflection_text: The reflection text.
        min_chars: Minimum character count required per field.

    Returns:
        List[str]: A list of warning messages for any failed checks.
    """
    warnings = []
    
    inputs = {
        "history_text": history_text,
        "product_text": product_text,
        "reflection_text": reflection_text
    }

    for key, text in inputs.items():
        if not text or len(text) < min_chars:
            warnings.append(
                f"Input '{key}' is too short ({len(text) if text else 0} chars). Analysis quality may suffer."
            )

    if warnings:
        logger.warning(f"[Validators] Structural Warnings: {warnings}")
        
    return warnings
