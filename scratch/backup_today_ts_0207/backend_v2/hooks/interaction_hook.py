"""Interaction Role Hook Module.

This hook evaluates the user's cognitive role (Passenger to Architect)
based on the current execution chat log and strict Python heuristics.
"""

import logging

from fastapi import status
from pydantic import ValidationError

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.hooks.metrics import calculate_behavioral_metrics, calculate_control_ratio
from backend_v2.llm.client import LLMClient
from backend_v2.llm.prompt_builder import build_system_directive
from backend_v2.models.domain.interaction import InteractionAnalysisDTO, InteractionInput
from backend_v2.models.prompts.hook_prompts import INTERACTION_OBJECTIVE, INTERACTION_RULES
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

_SYSTEM_INSTRUCTION: str = build_system_directive(
    objective=INTERACTION_OBJECTIVE,
    role="Interaction Analyst",
    rules=INTERACTION_RULES,
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
    if not chat_log or not chat_log.strip():
        logger.debug("[InteractionRoleHook] Empty chat log. Skipping.")
        return HookResult(success=True, state_delta={})

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
        llm_client = await LLMClient.from_strategy("fast", repository=system_repo)
        executor = LLMTaskExecutor(prompt_compiler=PromptCompiler())
    except ConfigurationError as e:
        logger.error("[InteractionRoleHook] %s: Failed to init LLM: %s", ErrorCodes.CONFIGURATION_ERROR.name, e)
        raise AppException(
            message="Failed to init LLM.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        ) from e

    # 3. Dynamic User Message (High-Fidelity Prompting, Markdown parameters separated)
    user_content = (
        "## EXECUTION PARAMETERS\n"
        f"**Control Ratio:** {control_ratio}\n"
        f"**Imperative Command Count:** {behavioral_metrics.imperative_command_count}\n"
        f"**Say-Do Gap:** {behavioral_metrics.say_do_gap}\n"
        f"**Automation Bias:** {behavioral_metrics.automation_bias}\n\n"
        "## SOURCE DATA\n"
        "### USER PAYLOAD\n"
        f"{chat_log}\n"
    )

    messages: list[dict[str, str]] = [
        {"role": "system", "content": _SYSTEM_INSTRUCTION},
        {"role": "user", "content": user_content},
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

        # Epic 27: Inject localized role name to prevent Prompt Compiler leakage
        # Uses the backend LocalizationService to avoid hardcoding translations in Python.
        raw_role = dumped.get("role_classification", "")
        if raw_role:
            try:
                from backend_v2.services.localization import LocalizationService

                locale = state.inputs.get("locale", "en")
                l10n_key = raw_role.lower()
                dumped["role_classification"] = LocalizationService.translate(l10n_key, lang=locale)
            except Exception as loc_e:
                logger.warning("Failed to localize role %s: %s", raw_role, loc_e)

        return HookResult(success=True, state_delta={"interaction_analysis": dumped})

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
