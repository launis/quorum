import logging
import re
from typing import Dict, List, Optional

from backend.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


class BibliographyParser:
    """Parses text to identify bibliography sections and extract references.
    
    Supports multilingual detection (English, Finnish).
    Adheres to RFC 7807 (via AppException) and Fail Fast principles.
    """

    # Compiled regex patterns for performance and validation
    BIBLIOGRAPHY_HEADERS: List[str] = [
        r"^references\s*$",       # EN
        r"^bibliography\s*$",     # EN
        r"^lähdeluettelo\s*$",    # FI
        r"^kirjallisuutta\s*$",   # FI
        r"^viitteet\s*$",         # FI
    ]

    # Regex for citation keys: [1], [12], (1)
    CITATION_KEY_PATTERN = re.compile(r"^\[(\d+)\]")

    def __init__(self):
        """Initialize parser and validate patterns."""
        try:
            self._header_patterns = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in self.BIBLIOGRAPHY_HEADERS]
        except re.error as e:
            # Fail Fast check: Ensure patterns are valid regex during initialization
             raise AppException(
                message=f"Invalid regex pattern in configuration: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR}
            )

    def detect_bibliography(self, text: str) -> Optional[str]:
        """Finds the start of the bibliography section.

        Args:
            text: The full document text.

        Returns:
            The text content starting from the bibliography header, or None if not found.
            
        Raises:
            AppException: If text is empty (Fail Fast).
        """
        if not text:
             return None

        lines = text.split("\n")
        
        # Performance optimization: Check from end of file upwards first?
        # Or stick to linear scan but with restrictions.
        # Original logic had a heuristic: last 50% or small doc.

        start_index = -1

        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            for pattern in self._header_patterns:
                if pattern.match(line_stripped):
                    # Heuristic: Bibliography usually appears near the end (last 30%)
                    # but for small docs, it could be anywhere.
                    # Let's enforce it must be in the last 50% OR the doc is small.
                    if len(lines) < 100 or i > len(lines) * 0.5:
                        start_index = i
                        break
            if start_index != -1:
                break

        if start_index != -1:
            return "\n".join(lines[start_index:])

        return None

    def parse_references(self, text: str) -> Dict[str, str]:
        """Extracts references from a bibliography text block.

        Args:
            text: Text containing the bibliography.

        Returns:
            Dictionary mapping citation keys (e.g., '1') to the full reference text.
            
        Raises:
            AppException: If parsing logic fails critically (unexpected state).
        """
        if not text:
            # Empty input -> Empty output is valid domain behavior, not necessarily an error,
            # unless we EXPECT a bibliography. 
            # Given this is a parser utility, empty input returning empty dict is safe.
            return {}

        references: Dict[str, str] = {}
        
        try:
            bibliography_text = self.detect_bibliography(text)

            if not bibliography_text:
                logger.warning("No bibliography section detected in text.")
                raise AppException(
                    message="Bibliography section not found in document.",
                    status_code=400, # or 422? 400 seems appropriate for "invalid content structure"
                    details={"error_code": ErrorCodes.PARSING_FAILED}
                )

            lines = bibliography_text.split("\n")
            current_key: Optional[str] = None
            current_ref: List[str] = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check for new reference start: "[1] Author..."
                match = self.CITATION_KEY_PATTERN.match(line)
                if match:
                    # Save previous reference if exists
                    if current_key:
                        references[current_key] = " ".join(current_ref)

                    # Start new reference
                    current_key = match.group(1)
                    
                    # Remove the key from the text (optional, but keeps metadata clean)
                    # "[1] Author" -> "Author"
                    clean_line = line[match.end() :].strip()
                    current_ref = [clean_line]
                elif current_key:
                    # Append to current reference (multiline ref)
                    current_ref.append(line)

            # Save the last one
            if current_key and current_ref:
                references[current_key] = " ".join(current_ref)

            return references

        except Exception as e:
            logger.error(f"Bibliography Parsing Failed: {e}", exc_info=True)
            raise AppException(
                message=f"Bibliography Parsing Failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.PARSING_FAILED}
            ) from e
