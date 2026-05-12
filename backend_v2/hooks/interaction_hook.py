"""Interaction Role Hook.

This hook is responsible for evaluating the user's cognitive role (Passenger to Architect)
based on the current execution chat log and strict Python heuristics.
"""

import logging

from fastapi import status
from pydantic import ValidationError

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.hooks.metrics import calculate_behavioral_metrics, calculate_control_ratio
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.interaction import InteractionAnalysisDTO, InteractionInput
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

logger = logging.getLogger(__name__)

_SYSTEM_INSTRUCTION = """<system_directive>
<objective>
Analyze the user's interaction behavior and assign a precise cognitive role based on the provided
conversation history and hard mathematical heuristics.
</objective>
<role>Interaction Analyst</role>
<rules>
  <rule>
    You must classify the user into one of four roles: ROLE_PASSENGER, ROLE_NAVIGATOR, ROLE_DRIVER,
    or ROLE_ARCHITECT.
  </rule>
  <rule>
    ROLE_PASSENGER: The user provides minimal input, relying almost entirely on the AI to lead,
    structure, and generate content.
  </rule>
  <rule>
    ROLE_NAVIGATOR: The user provides direction and goals but relies on the AI to execute the details.
  </rule>
  <rule>
    ROLE_DRIVER: The user actively controls the execution, providing specific constraints, structural
    requirements, and detailed data.
  </rule>
  <rule>
    ROLE_ARCHITECT: The user defines the entire conceptual framework, methodology, and strict rules,
    treating the AI purely as a compiler or executor of their complex design.
  </rule>
  <rule>
    HYBRID TRUTH MANDATE: You MUST respect the hard mathematical metrics provided in the
    <execution_parameters> tag. The mathematical `control_ratio` is the ultimate baseline.
    If the user's control ratio is low, they CANNOT be an Architect, regardless of their tone.
  </rule>
  <rule>
    Do NOT output Markdown. You MUST output ONLY the requested strict JSON schema matching
    InteractionAnalysisDTO.
  </rule>
</rules>
</system_directive>"""


@hook_registry.register(name="analyze_interaction_role")
async def analyze_interaction_role(state: HookState, deps: HookDependencies) -> HookResult:
    """Evaluate user's cognitive role using a hybrid logic (Python + LLM)."""
    logger.info("[InteractionRoleHook] Running interaction analysis...")

    # 1. Isolation: Extract only current execution chat_log
    try:
        input_data = InteractionInput.model_validate(state.inputs)
    except ValidationError as e:
        error_code = ErrorCodes.INVALID_JSON_PAYLOAD
        msg = f"Invalid inputs schema: {e}"
        logger.error("[InteractionRoleHook] %s: %s", error_code.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code.value},
        ) from e

    chat_log = input_data.chat_log
    if not chat_log.strip():
        logger.debug("[InteractionRoleHook] Empty chat log. Skipping.")
        return HookResult(success=True, state_delta={})

    # 2. Hard Heuristics (Python)
    control_ratio = calculate_control_ratio(chat_log)
    behavioral_metrics = calculate_behavioral_metrics(chat_log)

    system_repo = deps.system_repo
    if not system_repo:
        msg = "Strict Fail-Fast Enforced: Missing repository context in InteractionRoleHook."
        logger.error("[InteractionRoleHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

    try:
        # Internal Utility LLM Execution pattern
        llm_client = await LLMClient.from_strategy("fast", repository=system_repo)
        executor = LLMTaskExecutor(prompt_compiler=PromptCompiler())
    except ConfigurationError as e:
        logger.error("[InteractionRoleHook] %s: Failed to init LLM: %s", ErrorCodes.CONFIGURATION_ERROR.name, e)
        raise AppException(
            message="Failed to init LLM.",
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        ) from e

    # 3. Dynamic User Message (High-Fidelity Prompting)
    user_content = (
        f"<execution_parameters>\n"
        f"  <control_ratio>{control_ratio}</control_ratio>\n"
        f"  <imperative_command_count>{behavioral_metrics.imperative_command_count}</imperative_command_count>\n"
        f"  <say_do_gap>{behavioral_metrics.say_do_gap}</say_do_gap>\n"
        f"  <automation_bias>{behavioral_metrics.automation_bias}</automation_bias>\n"
        f"</execution_parameters>\n\n"
        f"<source_data>\n"
        f"  <user_payload>\n{chat_log}\n  </user_payload>\n"
        f"</source_data>"
    )

    messages = [{"role": "system", "content": _SYSTEM_INSTRUCTION}, {"role": "user", "content": user_content}]

    # 4. Structured Execution
    try:
        response_dto, _ = await executor.execute_structured_task(
            client=llm_client,
            messages=messages,
            response_model=InteractionAnalysisDTO,
        )

        logger.info("[InteractionRoleHook] Role classified: %s", response_dto.role_classification.name)

        return HookResult(success=True, state_delta={"interaction_analysis": response_dto.model_dump(mode="json")})

    except Exception as e:
        logger.error(
            "[InteractionRoleHook] %s: LLM structured execution failed: %s",
            ErrorCodes.AGENT_RESPONSE_PARSING_FAILED.name,
            e,
            exc_info=True,
        )
        raise AppException(
            message="LLM structured execution failed.",
            status_code=500,
            details={"error_code": ErrorCodes.AGENT_RESPONSE_PARSING_FAILED.value},
        ) from e
