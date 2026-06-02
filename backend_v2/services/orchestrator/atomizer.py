"""Design-time prompt atomizer service for Cognitive Quorum V2.

Responsible for assigning secure, opaque TDA assertion identifiers during design-time compilation.
"""

import logging
import secrets
from typing import Any

from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.v2_core import PromptBlock

logger = logging.getLogger(__name__)


class PromptAtomizer:
    """Design-time Compiler logic to assign IDs to TDA assertions.

    Ensures compliance with structural requirements before database persistence.
    """

    @classmethod
    async def atomize_prompt_block(
        cls,
        block: PromptBlock,
        repository: Any | None = None,
        is_test: bool = False,
    ) -> PromptBlock:
        """Assigns Stripe Opaque IDs to TDA Assertions if they are missing.

        Executed during Design-Time (save) before DB commit.

        Args:
            block: The PromptBlock instance to process.
            repository: Optional repository context.
            is_test: Optional test flag.

        Returns:
            The processed PromptBlock instance with updated IDs.

        Raises:
            AppException: VALIDATION_FAILED if validation or re-instantiation of Pydantic models fails.
        """
        try:
            if not block.scales:
                return block

            new_scales = []
            for scale in block.scales:
                new_claims = []
                for claim in scale.claims:
                    # Expect claim to have 'tda_assertions' mapped in v2_core
                    if not claim.tda_assertions:
                        new_claims.append(claim)
                        continue

                    new_assertions = []
                    for assertion in claim.tda_assertions:
                        # If ID is missing or not following Opaque Stripe ID pattern, assign one.
                        if not assertion.tda_id or not str(assertion.tda_id).startswith("tda_"):
                            # Opaque ID generation using safe secrets token to avoid standard entropy leaks
                            secure_suffix = secrets.token_hex(4)
                            new_id = f"tda_{secure_suffix}"

                            # Re-instantiate explicitly to enforce validation
                            updated_fields = {**assertion.model_dump(), "tda_id": new_id}
                            updated_assertion = type(assertion)(**updated_fields)
                            new_assertions.append(updated_assertion)
                        else:
                            new_assertions.append(assertion)

                    # Re-instantiate explicitly to enforce validation
                    updated_claim_fields = {**claim.model_dump(), "tda_assertions": new_assertions}
                    updated_claim = type(claim)(**updated_claim_fields)
                    new_claims.append(updated_claim)

                # Re-instantiate explicitly to enforce validation
                updated_scale_fields = {**scale.model_dump(), "claims": new_claims}
                updated_scale = type(scale)(**updated_scale_fields)
                new_scales.append(updated_scale)

            # Re-instantiate explicitly to enforce validation
            updated_block_fields = {**block.model_dump(), "scales": new_scales}
            return type(block)(**updated_block_fields)
        except Exception as e:
            logger.error(
                "Failed to atomize prompt block: %s",
                str(e),
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=f"Prompt block atomization failed: {str(e)}",
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e
