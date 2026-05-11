import logging
import uuid
from typing import Any

from backend_v2.models.v2_core import PromptBlock

logger = logging.getLogger(__name__)


class PromptAtomizer:
    """Design-time Compiler logic to assign IDs to TDA assertions."""

    @classmethod
    async def atomize_prompt_block(
        cls, block: PromptBlock, repository: Any = None, is_test: bool = False
    ) -> PromptBlock:
        """Assigns Stripe Opaque IDs to TDA Assertions if they are missing.
        Executed during Design-Time (save) before DB commit.
        """
        if not block.scales:
            return block

        new_scales = []
        for scale in block.scales:
            new_claims = []
            for claim in scale.claims:
                # We expect claim to have 'tda_assertions' mapped in v2_core.py
                if not claim.tda_assertions:
                    new_claims.append(claim)
                    continue

                new_assertions = []
                for assertion in claim.tda_assertions:
                    # If ID is missing or not following Opaque Stripe ID pattern, assign one.
                    # Usually, TDAAssertion schema enforces the field,
                    # so it might be empty string or missing if from raw JSON.
                    if not assertion.tda_id or not str(assertion.tda_id).startswith("tda_"):
                        new_id = f"tda_{uuid.uuid4().hex[:8]}"
                        new_assertions.append(assertion.model_copy(update={"tda_id": new_id}))
                    else:
                        new_assertions.append(assertion)

                new_claims.append(claim.model_copy(update={"tda_assertions": new_assertions}))

            new_scales.append(scale.model_copy(update={"claims": new_claims}))

        return block.model_copy(update={"scales": new_scales})
