"""Interaction Role Hook Module.

This hook evaluates the user's cognitive role (Passenger to Architect)
based on the current execution chat log and strict Python heuristics.
"""

import logging

from fastapi import status
from pydantic import ValidationError

from backend_v2.core.hook_registry import (
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.hooks.metrics import calculate_behavioral_metrics, calculate_control_ratio
from backend_v2.llm.client import LLMClient
from backend_v2.llm.prompt_builder import build_system_directive
from backend_v2.models.domain.interaction import InteractionAnalysisDTO, InteractionInput
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompts.execution import INTERACTION_OBJECTIVE, INTERACTION_RULES
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

_SYSTEM_INSTRUCTION: str = build_system_directive(
    objective=INTERACTION_OBJECTIVE,
    role="Interaction Analyst",
    rules=None,
    interaction_rules=INTERACTION_RULES,
)


@hook_registry.register(name="analyze_interaction_role")
async def analyze_interaction_role(state: HookState, deps: HookDependencies) -> HookResult:
    """Evaluate user's cognitive role using a hybrid logic (Python + LLM).

    Args:
        state: The current execution hook state containing input context.
        deps: The resolution context carrying services and repositories.

    Returns:
        The HookResult carrying execution state_delta updating the model schema.

    Raises:
        AppException: Raised with ErrorCodes.INVALID_JSON_PAYLOAD if input validation fails,
            ErrorCodes.CONFIGURATION_ERROR if dependencies are missing, or
            ErrorCodes.AGENT_RESPONSE_PARSING_FAILED if structured execution fails.
    """
    logger.info("[InteractionRoleHook] Running interaction analysis...")

    # 1. Isolation: Extract only current execution chat_log
    try:
        inputs_source = state.inputs.raw_inputs
        input_data = InteractionInput.model_validate(inputs_source)
    except ValidationError as e:
        msg = f"Invalid inputs schema: {e}"
        logger.error("[InteractionRoleHook] %s: %s", ErrorCodes.INVALID_JSON_PAYLOAD.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.INVALID_JSON_PAYLOAD.value},
        ) from e

    chat_log = input_data.chat_log
    if not chat_log or not chat_log.strip():
        logger.debug("[InteractionRoleHook] Empty chat log. Skipping.")
        return HookResult(success=True, state_delta=HookDeltaDTO())

    # 2. Hard Heuristics (Python)
    control_ratio = calculate_control_ratio(chat_log)
    settings = get_settings()
    behavioral_metrics = calculate_behavioral_metrics(chat_log, settings)

    system_repo = deps.system_repo
    if not system_repo:
        msg = "Strict Fail-Fast Enforced: Missing repository context in InteractionRoleHook."
        logger.error("[InteractionRoleHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    try:
        # Internal Utility LLM Execution pattern
        llm_client = await LLMClient.from_strategy("fast", repository=system_repo, pipeline_name="interaction_hook")
        executor = LLMTaskExecutor(prompt_compiler=PromptCompiler())
    except ConfigurationError as e:
        logger.error("[InteractionRoleHook] %s: Failed to init LLM: %s", ErrorCodes.CONFIGURATION_ERROR.name, e)
        raise AppException(
            message="Failed to init LLM.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        ) from e

    # 3. Dynamic User Message (High-Fidelity Prompting, XML parameters separated)
    user_content = (
        "<execution_parameters>\n"
        f"  <control_ratio>{control_ratio}</control_ratio>\n"
        f"  <imperative_command_count>{behavioral_metrics.imperative_command_count}</imperative_command_count>\n"
        f"  <say_do_gap>{behavioral_metrics.say_do_gap}</say_do_gap>\n"
        f"  <automation_bias>{behavioral_metrics.automation_bias}</automation_bias>\n"
        "</execution_parameters>\n\n"
        "<source_data>\n"
        "  <user_payload>\n"
        f"{chat_log}\n"
        "  </user_payload>\n"
        "</source_data>"
    )

    messages: list[LLMMessageDTO] = [
        LLMMessageDTO(role="system", content=_SYSTEM_INSTRUCTION),
        LLMMessageDTO(role="user", content=user_content),
    ]

    # 4. Structured Execution
    try:
        response_dto, _ = await executor.execute_structured_task(
            client=llm_client,
            messages=messages,
            response_model=InteractionAnalysisDTO,
        )

        logger.info("[InteractionRoleHook] Role classified: %s", response_dto.role_classification.name)

        dumped = response_dto.model_dump(mode="json")

        return HookResult(success=True, state_delta=HookDeltaDTO(delta={"interaction_analysis": dumped}))

    except Exception as e:
        logger.error(
            "[InteractionRoleHook] %s: LLM structured execution failed: %s",
            ErrorCodes.AGENT_RESPONSE_PARSING_FAILED.name,
            e,
            exc_info=True,
        )
        raise AppException(
            message="LLM structured execution failed.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.AGENT_RESPONSE_PARSING_FAILED.value},
        ) from e
