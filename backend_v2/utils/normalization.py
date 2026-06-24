"""Text normalization utilities for evaluation variance reduction in the V2 engine.

Provides layout and structural text cleaning to standardize inputs fed to
the Large Language Models, optimizing context caching and determinism.
"""

import logging
import re

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


def normalize_evaluation_input(text: str) -> str:
    """Normalize input text to reduce layout and formatting variance for the LLM.

    Cleans up Markdown syntax markers, collapses multiple empty lines and spaces,
    and strips trailing whitespace on each line to stabilize tokenization.

    Args:
        text: The raw source text to normalize.

    Returns:
        The normalized string.

    Raises:
        AppException: If text normalization fails critically.
    """
    if not text:
        return ""

    try:
        # 1. Strip Markdown header markers, bold, italic, and inline code characters (#, *, _, `)
        cleaned = re.sub(r"[\#\*\_`]", "", text)

        # 2. Standardize multiple consecutive spaces or tabs to a single space on each line
        lines = []
        for line in cleaned.splitlines():
            stripped_line = line.strip()
            # Collapse multiple spaces or tabs
            collapsed_line = re.sub(r"[ \t]+", " ", stripped_line)
            lines.append(collapsed_line)

        # 3. Collapse multiple consecutive empty lines into a single empty line
        rebuilt = "\n".join(lines)
        rebuilt = re.sub(r"\n\s*\n\s*\n+", "\n\n", rebuilt)

        return rebuilt.strip()
    except Exception as e:
        msg = f"Text normalization failed: {e}"
        logger.error("[Normalization] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e
