import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

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
            executor = LLMTaskExecutor(prompt_compiler=PromptCompiler())
        except Exception as e:
            logger.error("[PromptAtomizer] Failed to initialize LLMClient or Executor: %s", e)
            raise

        system_prompt = (
            "<system_directive>\n"
            "  <objective>\n"
            "    You are a 'Kääntäjä-AI' compiler expert. Your task is to perform Deep Atomization and Obfuscation "
            "on an evaluation claim.\n"
            "  </objective>\n"
            "  <rules>\n"
            "    <rule>Explode the provided claim into precisely 15 distinct micro-atoms.</rule>\n"
            "    <rule>Obfuscate domain-specific vocabulary into abstract criteria.</rule>\n"
            "    <rule>Create 'Scaffolded' exception mechanisms for any special terms.</rule>\n"
            "    <rule>Provide a 'Rubric-CoT' reasoning to explain how these atoms preserve the "
            "original meaning to prevent Context Drift.</rule>\n"
            "  </rules>\n"
            "</system_directive>"
        )

        new_scales = []
        for scale in block.scales:
            new_claims = []
            for claim in scale.claims:
                if not claim.micro_atoms:
                    if "en" not in claim.label.translations or not claim.label.translations["en"].strip():
                        msg = "Atomization failed: Claim label missing mandatory 'en' translation."
                        logger.error("[PromptAtomizer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                        raise AppException(
                            message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                        )

                    text_to_atomize = claim.label.translations["en"]
                    user_prompt = (
                        f"<context>\n"
                        f"  <score_level>{scale.score}</score_level>\n"
                        f"  <ai_label>{scale.ai_label}</ai_label>\n"
                        f"  <original_ai_description>{claim.ai_description}</original_ai_description>\n"
                        f"</context>\n"
                        f"<claim>\n{text_to_atomize}\n</claim>"
                    )

                    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

                    mock_identity = "atomize_mock" if is_test else None

                    try:
                        res, _ = await executor.execute_structured_task(
                            client=client,
                            messages=messages,
                            response_model=AtomizationSchema,
                            mock_identity=mock_identity,
                        )
                        atoms = res.micro_atoms
                        if len(atoms) != 15:
                            msg = f"Atomization failed: LLM generated {len(atoms)} micro-atoms, strictly 15 required."
                            logger.error("[PromptAtomizer] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                            raise AppException(
                                message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                            )

                        new_claims.append(claim.model_copy(update={"micro_atoms": atoms}))

                    except Exception as e:
                        logger.error("[PromptAtomizer] Atomization failed for score %s: %s", scale.score, e)
                        raise
                else:
                    new_claims.append(claim)

            new_scales.append(scale.model_copy(update={"claims": new_claims}))

        return block.model_copy(update={"scales": new_scales})
