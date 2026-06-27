"""Text normalization utilities for evaluation variance reduction in the V2 engine.

Provides layout and structural text cleaning to standardize inputs fed to
the Large Language Models, optimizing context caching and determinism.
"""

import logging
import re
import unicodedata

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


def normalize_evaluation_input(text: str) -> str:
    """Normalize input text to reduce layout and formatting variance for the LLM.

    Cleans up Markdown syntax markers, collapses multiple empty lines and spaces,
    and strips trailing whitespace on each line to stabilize tokenization.
    Performs NFC Unicode normalization, zero-width character stripping,
    and smart quote/dash standardization.

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
        # Unicode NFC normalization
        normalized = unicodedata.normalize("NFC", text)

        # Remove zero-width characters (ZWSP, ZWJ, ZWNJ, BOM, soft hyphens)
        cleaned = re.sub(r"[\u200b\u200c\u200d\ufeff\u00ad]", "", normalized)

        # Normalize dashes and smart quotes into ASCII straight characters
        cleaned = cleaned.replace("\u2013", "-").replace("\u2014", "-")
        cleaned = cleaned.replace("\u201c", '"').replace("\u201d", '"')
        cleaned = cleaned.replace("\u2018", "'").replace("\u2019", "'")

        # 1. Strip Markdown header markers, bold, italic, and inline code characters (#, *, _, `)
        cleaned = re.sub(r"[\#\*\_`]", "", cleaned)

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
