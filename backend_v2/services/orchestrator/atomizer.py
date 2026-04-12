import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.llm.client import LLMClient
from backend_v2.models.v2_core import PromptBlock

logger = logging.getLogger(__name__)


class AtomizationSchema(BaseModel):
    """Pydantic Strict V2 schema for Deep Atomization output."""

    model_config = ConfigDict(strict=True, extra="forbid")

    micro_atoms: list[str] = Field(
        ...,
        min_length=15,
        max_length=15,
        description=(
            "Exactly 15 distinct micro-atoms extracted from the claim. "
            "Domain-specific vocabulary MUST be obfuscated. "
            "Use Scaffolded exception mechanisms for special terms."
        ),
    )
    rubric_cot: str = Field(
        ...,
        description=(
            "Rubric-CoT reasoning to explain how these atoms preserve the original meaning to prevent Context Drift."
        ),
    )


class PromptAtomizer:
    """Design-time Compiler logic to deeply atomize evaluation criteria."""

    @classmethod
    async def atomize_prompt_block(
        cls, block: PromptBlock, repository: Any = None, is_test: bool = False
    ) -> PromptBlock:
        """Runs deep atomization on all matrix claims if they lack micro_atoms.
        Executed during Design-Time (save) before DB commit.
        """
        if not block.scales:
            return block

        try:
            # We use 'fast' strategy. Using LLMClient.from_strategy ensures architectural compliance.
            client = await LLMClient.from_strategy("fast", repository=repository)
        except Exception as e:
            logger.error("[PromptAtomizer] Failed to initialize LLMClient: %s", e)
            raise

        system_prompt = (
            "You are a 'Kääntäjä-AI' compiler expert. Your task is to perform Deep Atomization and Obfuscation "
            "on an evaluation claim.\n"
            "1. Explode the provided claim into precisely 15 distinct micro-atoms.\n"
            "2. Obfuscate domain-specific vocabulary into abstract criteria.\n"
            "3. Create 'Scaffolded' exception mechanisms for any special terms.\n"
            "4. Provide a 'Rubric-CoT' reasoning to explain how these atoms preserve the "
            "original meaning to prevent Context Drift."
        )

        for scale in block.scales:
            for claim in scale.claims:
                if not claim.micro_atoms:
                    text_to_atomize = claim.label.get("en", "No English label provided")
                    user_prompt = (
                        f"Score level: {scale.score}\n"
                        f"AI Label: {scale.ai_label}\n"
                        f"Original AI Description: {claim.ai_description}\n"
                        f"Claim label to atomize:\n{text_to_atomize}"
                    )

                    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

                    mock_identity = "atomize_mock" if is_test else None

                    try:
                        res, _ = await client.run_structured_task(
                            messages=messages, response_model=AtomizationSchema, mock_identity=mock_identity
                        )
                        atoms = res.micro_atoms
                        if len(atoms) < 15:
                            atoms.extend(["[MISSING ATOM]"] * (15 - len(atoms)))
                        elif len(atoms) > 15:
                            atoms = atoms[:15]

                        claim.micro_atoms = atoms

                    except Exception as e:
                        logger.error("[PromptAtomizer] Atomization failed for score %s: %s", scale.score, e)
                        raise

        return block
