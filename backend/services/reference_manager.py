"""Reference Manager for handling citations and bibliography generation."""

import logging
import re
from typing import Any

from pydantic import ValidationError

from backend.exceptions import AppException, ErrorCodes
from backend.models.dtos.knowledge_base import CitationReport, KnowledgeBaseSchema

logger = logging.getLogger(__name__)


class ReferenceManager:
    """Centralized service for managing bibliometric citations and generating master bibliographies.

    Scans text for short citations (e.g. "Acemoglu 2023") and resolves them against the Knowledge Base
    to produce accurate lists of references used in generated output.
    Enforces strict typing and Fail Fast validation on KB content.
    """

    def __init__(self, knowledge_base: dict[str, Any] | KnowledgeBaseSchema):
        """Initializes the manager with knowledge base content.

        Args:
            knowledge_base: The full KB content (dict or typed schema).

        Raises:
            AppException: If KB content is invalid (Fail Fast).
        """
        # Fail Fast: Strict Schema Validation
        if isinstance(knowledge_base, KnowledgeBaseSchema):
            self.kb = knowledge_base
        else:
            try:
                self.kb = KnowledgeBaseSchema(**knowledge_base)
            except ValidationError as e:
                logger.error(f"Invalid Knowledge Base schema: {e}")
                raise AppException(
                    message="Refusing to initialize ReferenceManager with invalid Knowledge Base.",
                    status_code=500,
                    details={"error_code": ErrorCodes.KNOWLEDGE_BASE_INVALID, "validation_errors": str(e)},
                ) from e

        self.references_map = self._build_reference_map()

        # Regex to find parenthetical citations: (Author 2020) or (Author et al. 2020)
        # Matches: "(Smith 2020)", "(Smith & Jones 2020)", "(Smith ym. 2020)", "(vrt. Smith 2020)"
        self.citation_pattern = re.compile(
            r"\((?:vrt\.\s*)?(?:[A-Za-zÅÄÖåäö&,-]+\s+)+(?:et\s+al\.|ym\.)?\s*,?\s*\d{4}[a-z]?\)"
        )

    def _build_reference_map(self) -> dict[str, str]:
        """Builds a normalized lookup map: Short Citation (lowercase) -> Full Reference String.

        Used for O(1) resolution of citations found in text.

        Returns:
            Dict[str, str]: Map of short citation to full bibliography entry.

        """
        ref_map = {}

        # Safe strict usage of typed KB
        for r in self.kb.references:
            full = r.full_text
            short = r.short_citation

            if short and full:
                ref_map[short.lower()] = full

        return ref_map

    def scan_and_collect_references(self, content: Any) -> list[str]:
        """Recursively scans a JSON-like structure (dict/list/str) for citations.

        Extracts all parenthetical citations and resolves them to full references.

        Args:
            content (Any): The data structure to scan.

        Returns:
            List[str]: Sorted list of unique Full Reference strings used in the content.

        """
        used_refs: set[str] = set()

        def _recursive_scan(obj):
            if isinstance(obj, str):
                self._scan_text(obj, used_refs)
            elif isinstance(obj, dict):
                for v in obj.values():
                    _recursive_scan(v)
            elif isinstance(obj, list):
                for item in obj:
                    _recursive_scan(item)

        _recursive_scan(content)

        return sorted(list(used_refs))

    def _scan_text(self, text: str, used_refs: set[str]):
        """Scans a single string for citations and updates the set of used references.

        Args:
            text (str): Input text.
            used_refs (set): Accumulator for found full references.
        """
        if not text or len(text) < 10:
            return

        try:
            matches = self.citation_pattern.findall(text)
        except Exception as e:
            # Should technically never happen on standard string, but adhering to Fail Fast for robust parsers
            logger.warning(f"Regex failure in reference scan: {e}")
            raise AppException(
                message="Critical Regex failure in citation parsing.",
                status_code=500,
                details={"error_code": ErrorCodes.CITATION_PARSING_FAILED, "original_error": str(e)},
            ) from e

        for match in matches:
            # Clean: "(vrt. Smith 2020)" -> "smith 2020"
            clean = match.strip("()")
            clean = clean.replace("vrt.", "").strip()
            clean_lower = clean.lower()

            # 1. Direct Match against Short Citations
            if clean_lower in self.references_map:
                used_refs.add(self.references_map[clean_lower])
            else:
                # 2. Fuzzy Match?
                # If "Smith & Jones 2020" is in text, but Map has "Smith et al. 2020"
                # This requires more complex logic.
                # For now, check if map key is substring of text citation or vice versa
                for map_key, full_ref in self.references_map.items():
                    if map_key in clean_lower or clean_lower in map_key:
                        used_refs.add(full_ref)
                        break

    def advanced_scan(self, text_dump: str) -> CitationReport:
        """Performs a deep (2-hop) scan for citation relevance.

        1. Checks for direct citation in text.
        2. Checks for theoretical concepts mentioned in text, and includes references defining those concepts.

        Args:
            text_dump (str): The combined text to analyze.

        Returns:
            CitationReport: Typed map of {Full Reference -> [List of Reasons/Contexts]}.

        """
        found: dict[str, list[str]] = {}
        text_lower = text_dump.lower()

        # A. Strict Reference Scan
        # Use existing map
        for short, full in self.references_map.items():
            if short in text_lower:  # Basic substring match
                if full not in found:
                    found[full] = []
                found[full].append("Suora viittaus")
            else:
                # Check cleaned keys (no parens)
                clean_short = short.replace("(", "").replace(")", "")
                if clean_short in text_lower:
                    if full not in found:
                        found[full] = []
                    found[full].append("Suora viittaus (ilman sulkeita)")

        # B. Scan Concepts (Semantic Linking)
        cit_pattern = re.compile(r"\((?:[A-Za-zÅÄÖåäö&,.-]+\s+)+\d{4}[a-z]?\)")

        ignored_concepts = {
            "abstrakti",
            "tiivistelmä",
            "johdanto",
            "yhteenveto",
            "lähdeluettelo",
            "lähteet",
            "references",
            "abstract",
            "summary",
            "introduction",
        }

        for item in self.kb.concepts:
            term = item.term
            defn = item.definition

            if not term:
                continue
            if term.lower() in ignored_concepts:
                continue

            # If Concept TERM is mentioned in the text...
            if len(term) > 3 and term.lower() in text_lower:
                # ... check if the Concept DEFINITION has citations
                matches = cit_pattern.findall(defn)
                for m in matches:
                    raw_key = m.strip("()")

                    # Resolve raw_key to full reference
                    resolved_ref = None

                    # Try map first
                    if raw_key.lower() in self.references_map:
                        resolved_ref = self.references_map[raw_key.lower()]
                    else:
                        # Try fuzzy match
                        for short, full in self.references_map.items():
                            if raw_key.lower() in short or short in raw_key.lower():
                                resolved_ref = full
                                break

                    # If not resolved, use raw key (fallback) but try to clean prefixes
                    if not resolved_ref:
                        prefixes = ["vrt.", "cf.", "e.g.", "esim.", "ks.", "see"]
                        clean_raw = raw_key
                        for p in prefixes:
                            if clean_raw.lower().startswith(p + " "):
                                clean_raw = clean_raw[len(p) + 1 :].strip()
                        resolved_ref = clean_raw

                    if resolved_ref and len(resolved_ref) > 4:
                        if resolved_ref not in found:
                            found[resolved_ref] = []
                        msg = f"Käsite: '{term}'"
                        if msg not in found[resolved_ref]:
                            found[resolved_ref].append(msg)

        return CitationReport(relevance_map=found)
