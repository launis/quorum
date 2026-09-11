"""Smart Ingress Resolver Service for Cognitive Quorum V2.

Resolves raw incoming payloads and attachments against target workflow expected inputs
using 2-tier deterministic lexical matching with an Anti-Collision Firewall.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.inputs import Base64Attachment
from backend_v2.models.dtos.ingress import ResolvedIngressDTO

if TYPE_CHECKING:
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.inputs import WorkflowInputsIngress
    from backend_v2.models.v2_core import ExpectedInput

logger = logging.getLogger(__name__)

__all__ = ["SmartIngressResolver"]


def _normalize_token(text: str) -> str:
    """Normalize token by lowercasing and stripping non-alphanumeric characters.

    Args:
        text: Raw input text token or label.

    Returns:
        Cleaned lowercase alphanumeric string.
    """
    return re.sub(r"[^a-z0-9]", "", text.lower())


class SmartIngressResolver:
    """Resolves raw workflow inputs against expected inputs with collision protection.

    Attributes:
        logger: Logger instance for structured RFC 7807 audit reporting.
    """

    def __init__(self) -> None:
        """Initialize the SmartIngressResolver."""
        self.logger = logger

    def resolve(
        self,
        raw_inputs: WorkflowInputsIngress | None,
        expected_inputs: list[ExpectedInput],
        target_locale: str,
    ) -> ResolvedIngressDTO:
        """Resolve incoming inputs against target workflow expected inputs.

        Args:
            raw_inputs: The raw workflow inputs ingress payload.
            expected_inputs: Expected inputs configured on the target workflow.
            target_locale: Target locale for resolving missing optional label manifests.

        Returns:
            ResolvedIngressDTO containing resolved inputs and source identity manifest.

        Raises:
            AppException: If collision is detected, matches are ambiguous, or required inputs are missing.
        """
        resolved: dict[str, Any] = {}
        manifest: dict[str, str] = {}
        slot_sources: dict[str, str] = {}

        dynamic_inputs: dict[str, Any] = {}
        if raw_inputs is not None:
            dynamic_inputs = raw_inputs.dynamic_inputs

        for key, val in dynamic_inputs.items():
            source_filename: str | None = None
            if isinstance(val, Base64Attachment):
                source_filename = val.filename
            else:
                try:
                    attachment = Base64Attachment.model_validate(val)
                    source_filename = attachment.filename
                except ValidationError, TypeError, ValueError:
                    source_filename = None

            source_name = key
            if source_filename is not None:
                source_name = source_filename

            candidates: list[str] = []
            if source_filename is not None:
                file_stem = Path(source_filename).stem
                if file_stem and file_stem not in candidates:
                    candidates.append(file_stem)
            key_stem = Path(key).stem
            if key_stem and key_stem not in candidates:
                candidates.append(key_stem)
            if key and key not in candidates:
                candidates.append(key)

            matched_slots: set[str] = set()
            for cand in candidates:
                matched_slots.update(self._find_matching_slots(cand, expected_inputs))

            if len(matched_slots) > 1:
                sorted_slots = sorted(matched_slots)
                self.logger.error(
                    "[SmartIngressResolver] %s: Ambiguous match for key '%s': candidate resolved to %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    key,
                    sorted_slots,
                )
                raise AppException(
                    message=f"Ambiguous match for input '{key}': Matches multiple expected input slots: {sorted_slots}",
                    status_code=400,
                    details={
                        "error_code": ErrorCodes.VALIDATION_FAILED.value,
                        "ambiguous_match": {"key": key, "slots": sorted_slots},
                    },
                )

            if len(matched_slots) == 1:
                target_slot = next(iter(matched_slots))
                if target_slot in slot_sources:
                    prev_source = slot_sources[target_slot]
                    self.logger.error(
                        "[SmartIngressResolver] %s: Collision on slot '%s' between '%s' and '%s'",
                        ErrorCodes.VALIDATION_FAILED.name,
                        target_slot,
                        prev_source,
                        source_name,
                    )
                    raise AppException(
                        message=(
                            f"Input collision on slot '{target_slot}': Both '{prev_source}' "
                            f"and '{source_name}' resolve to the same expected input slot."
                        ),
                        status_code=400,
                        details={
                            "error_code": ErrorCodes.VALIDATION_FAILED.value,
                            "collision": {
                                "slot": target_slot,
                                "sources": [prev_source, source_name],
                            },
                        },
                    )

                slot_sources[target_slot] = source_name
                resolved[target_slot] = val
                manifest[target_slot] = source_name
            else:
                resolved[key] = val
                manifest[key] = source_name

        missing_fields: list[str] = []
        for expected in expected_inputs:
            if expected.required:
                if expected.input_key not in resolved:
                    missing_fields.append(expected.input_key)
                else:
                    v = resolved[expected.input_key]
                    if v is None:
                        missing_fields.append(expected.input_key)
                    elif isinstance(v, str) and not v.strip():
                        missing_fields.append(expected.input_key)
                    elif isinstance(v, (list, tuple, set)) and len(v) == 0:
                        missing_fields.append(expected.input_key)
                    elif v == {}:
                        missing_fields.append(expected.input_key)

        if missing_fields:
            self.logger.error(
                "[SmartIngressResolver] %s: Missing required inputs from payload: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                missing_fields,
            )
            raise AppException(
                message=f"Missing required inputs from payload: {', '.join(missing_fields)}",
                status_code=400,
                details={
                    "error_code": ErrorCodes.VALIDATION_FAILED.value,
                    "missing_fields": missing_fields,
                },
            )

        for expected in expected_inputs:
            if expected.input_key not in manifest:
                manifest[expected.input_key] = expected.label.resolve(target_locale)

        return ResolvedIngressDTO(
            resolved_inputs=resolved,
            source_identity_manifest=manifest,
        )

    def _find_matching_slots(self, candidate: str, expected_inputs: list[ExpectedInput]) -> set[str]:
        """Find matching expected input slot keys for a candidate string.

        Args:
            candidate: Candidate string from input key or filename stem.
            expected_inputs: List of ExpectedInput definitions.

        Returns:
            Set of matched expected input keys.
        """
        cand_norm = _normalize_token(candidate)
        if not cand_norm:
            return set()

        tier1_matches = {exp.input_key for exp in expected_inputs if cand_norm == _normalize_token(exp.input_key)}
        if tier1_matches:
            return tier1_matches

        return {exp.input_key for exp in expected_inputs if self._matches_label(cand_norm, exp.label)}

    def _matches_label(self, cand_norm: str, label: I18nText) -> bool:
        """Check if normalized candidate matches localized label translations.

        Args:
            cand_norm: Normalized alphanumeric candidate string.
            label: Localized I18nText containing translations.

        Returns:
            True if candidate matches any translation directly or via stem.
        """
        for raw_trans in label.translations.values():
            trans_norm = _normalize_token(raw_trans)
            if cand_norm == trans_norm:
                return True

            base_label = re.sub(r"\([^)]*\)", "", raw_trans).strip()
            base_norm = _normalize_token(base_label)
            if base_norm:
                if cand_norm == base_norm:
                    return True
                if len(cand_norm) >= 4 and len(base_norm) >= 4:
                    if cand_norm.startswith(base_norm) or base_norm.startswith(cand_norm):
                        return True

            for paren in re.findall(r"\(([^)]+)\)", raw_trans):
                paren_norm = _normalize_token(paren)
                if paren_norm and cand_norm == paren_norm:
                    return True

        return False
