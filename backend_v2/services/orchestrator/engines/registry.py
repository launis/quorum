"""Typed Execution Engine Registry.

SSOT for polymorphic ExecutionEngine instantiation based on Step.engine_type.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING

from starlette import status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import EngineType
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.engines.base import ExecutionEngine
from backend_v2.services.orchestrator.engines.causal_discovery_engine import CausalDiscoveryEngine
from backend_v2.services.orchestrator.engines.prompt_engine import PromptEngine
from backend_v2.services.orchestrator.engines.synthesis_engine import SynthesisEngine
from backend_v2.services.orchestrator.engines.tda_engine import TDAEngine

if TYPE_CHECKING:
    from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

__all__ = ["ENGINE_REGISTRY", "build_execution_engine"]

logger = logging.getLogger(__name__)

ENGINE_REGISTRY: dict[EngineType, Callable[[PromptCompiler], ExecutionEngine]] = {
    EngineType.TDA: lambda compiler: TDAEngine(compiler),
    EngineType.SYNTHESIS: lambda compiler: SynthesisEngine(LLMTaskExecutor(compiler)),
    EngineType.PROMPT: lambda compiler: PromptEngine(LLMTaskExecutor(compiler)),
    EngineType.CAUSAL_DISCOVERY: lambda compiler: CausalDiscoveryEngine(compiler),
}


def build_execution_engine(
    engine_type: EngineType,
    prompt_compiler: PromptCompiler,
) -> ExecutionEngine:
    """Build and resolve ExecutionEngine instance based on step engine_type.

    Args:
        engine_type: Explicit EngineType enum designating the execution engine.
        prompt_compiler: PromptCompiler instance used for prompt compilation.

    Returns:
        Instantiated ExecutionEngine strategy instance.

    Raises:
        AppException: If engine_type is unknown, unsupported, or unmapped.
    """
    if not isinstance(engine_type, EngineType) or engine_type not in ENGINE_REGISTRY:
        msg = f"Unsupported engine type: {engine_type}"
        logger.error(
            "[EngineRegistry] %s: %s",
            ErrorCodes.VALIDATION_FAILED.name,
            msg,
            exc_info=True,
        )
        raise AppException(
            message=msg,
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            details={"error_code": ErrorCodes.VALIDATION_FAILED},
        )

    factory = ENGINE_REGISTRY[engine_type]
    return factory(prompt_compiler)
