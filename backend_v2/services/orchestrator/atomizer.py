"""Design-time prompt atomizer service for Cognitive Quorum V2.

Responsible for assigning secure, opaque TDA assertion identifiers during design-time compilation.
"""

from __future__ import annotations

import logging
import re

from fastapi import status

from backend_v2.database.interfaces import ISystemRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, generate_opaque_id
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlock
from backend_v2.models.enums import EntityPrefix

__all__ = ["PromptAtomizer"]

logger = logging.getLogger(__name__)


def _is_valid_tda_opaque_id(candidate_id: str) -> bool:
    """Validate whether a candidate TDA identifier conforms to canonical Opaque Stripe ID rules.

    Args:
        candidate_id: Candidate string identifier on a TDAAssertion.

    Returns:
        True if candidate_id matches OPAQUE_STRIPE_ID_REGEX with the 'tda' EntityPrefix and 32-hex payload.
    """
    if not candidate_id or not re.match(OPAQUE_STRIPE_ID_REGEX, candidate_id):
        return False
    prefix_part, hex_part = candidate_id.split("_", 1)
    return prefix_part == EntityPrefix.TDA.value and len(hex_part) == 32


class PromptAtomizer:
    """Design-time compiler logic to assign canonical Opaque Stripe IDs to TDA assertions.

    Ensures compliance with structural identifier invariants before database persistence.
    """

    @classmethod
    async def atomize_prompt_block(
        cls,
        block: PromptBlock,
        repository: ISystemRepository | None = None,
        is_test: bool = False,
    ) -> PromptBlock:
        """Assign canonical Opaque Stripe IDs to TDA assertions when missing or malformed.

        Executed during design-time persistence before database commit.

        Args:
            block: The PromptBlock instance to process.
            repository: Optional system repository context.
            is_test: Optional test execution flag.

        Returns:
            The processed PromptBlock instance with canonical TDA assertion identifiers.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED (422) if validation or model mutation fails.
        """
        _ = (repository, is_test)
        try:
            if not isinstance(block, MatrixPromptBlock) or not block.scales:
                return block

            new_scales = []
            for scale in block.scales:
                new_claims = []
                for claim in scale.claims:
                    if not claim.tda_assertions:
                        new_claims.append(claim)
                        continue

                    new_assertions = []
                    for assertion in claim.tda_assertions:
                        if not _is_valid_tda_opaque_id(assertion.tda_id):
                            new_id = generate_opaque_id(EntityPrefix.TDA, length=32)
                            updated_assertion = assertion.model_copy(update={"tda_id": new_id})
                            new_assertions.append(updated_assertion)
                        else:
                            new_assertions.append(assertion)

                    updated_claim = claim.model_copy(update={"tda_assertions": new_assertions})
                    new_claims.append(updated_claim)

                updated_scale = scale.model_copy(update={"claims": new_claims})
                new_scales.append(updated_scale)

            return block.model_copy(update={"scales": new_scales})
        except Exception as e:
            logger.error(
                "[PromptAtomizer] %s: Failed to atomize prompt block: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                str(e),
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=f"Prompt block atomization failed: {str(e)}",
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e
