"""Dynamic Hook Registry for the Cognitive Quorum System (V2).

This module provides a singleton registry for registering and executing Python
functions (hooks) dynamically. It enforces strict typing (Dict -> Dict) and
"Fail-Fast" principles, allowing legacy V1 capabilities to be exposed without
hardcoded domain model dependencies.
"""

import inspect
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

from backend_v2.database.repository import AbstractWorkflowRepository


@dataclass
class HookExecutionContext:
    """Strictly typed execution context for V2 Hooks.

    Prevents Magic String injection of dependencies into the generic state dictionary.
    """
    repository: AbstractWorkflowRepository
    execution_id: str
    workflow_id: str
    step_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    global_context_vars: dict[str, Any] = field(default_factory=dict)

# Strict type definition for a hook function
# It accepts a dictionary of inputs and a HookExecutionContext, returning a dictionary of outputs
# It can be either synchronous or asynchronous
HookFunction = Callable[[dict[str, Any], HookExecutionContext], dict[str, Any] | Awaitable[dict[str, Any]]]


class HookRegistry:
    """Singleton registry for managing dynamic Python hooks."""

    _instance: HookRegistry | None = None
    _hooks: dict[str, HookFunction]

    def __new__(cls) -> HookRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._hooks = {}
        return cls._instance

    def register(self, name: str) -> Callable[[HookFunction], HookFunction]:
        """Decorator to register a function in the hook registry.

        Args:
            name (str): The unique identifier for the hook.

        Returns:
            Callable: The decorator function.

        Raises:
            AppException: If a hook with the given name is already registered.
        """

        def decorator(func: HookFunction) -> HookFunction:
            if name in self._hooks:
                msg = f"Hook with name '{name}' is already registered."
                logger.error(f"[HookRegistry] {ErrorCodes.CONFIGURATION_ERROR.name}: {msg}")
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
                )

            logger.info(f"Registering hook: {name} -> {func.__name__}")
            self._hooks[name] = func
            return func

        return decorator

    def get_hook(self, name: str) -> HookFunction:
        """Retrieves a registered hook function by name.

        Args:
            name (str): The name of the hook.

        Returns:
            HookFunction: The executable hook function.

        Raises:
            AppException: If the hook is not found (Fail-Fast).
        """
        if name not in self._hooks:
            msg = f"Hook '{name}' not found in registry."
            logger.error(f"[HookRegistry] {ErrorCodes.RESOURCE_NOT_FOUND.name}: {msg}")
            raise AppException(
                message=msg,
                status_code=status.HTTP_404_NOT_FOUND,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND, "hook_name": name},
            )
        return self._hooks[name]

    async def execute(self, name: str, data: dict[str, Any], context: HookExecutionContext) -> dict[str, Any]:
        """Executes a registered hook securely.

        Handles both synchronous and asynchronous functions and enforces
        the strict input/output format and context injection.

        Args:
            name (str): The name of the hook to execute.
            data (dict[str, Any]): The input data payload.
            context (HookExecutionContext): The strictly typed execution context.

        Returns:
            dict[str, Any]: The result of the hook execution.

        Raises:
            AppException: If execution fails or returns an invalid type.
        """
        hook_func = self.get_hook(name)

        try:
            logger.debug(f"Executing hook '{name}' with data: {data}")

            # Execute taking into account whether it is a coroutine
            if inspect.iscoroutinefunction(hook_func):
                result = await hook_func(data, context)
            else:
                result = hook_func(data, context)

            # Enforce strict return type according to architectural mandate
            if not isinstance(result, dict):
                msg = f"Hook '{name}' returned invalid type '{type(result).__name__}'. Must return dict."
                logger.error(f"[HookRegistry] {ErrorCodes.AGENT_EXECUTION_CRITICAL.name}: {msg}")
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL},
                )

            return result

        except AppException:
            # Re-raise already constructed exceptions without wrapping
            raise
        except Exception as e:
            msg = f"Hook '{name}' execution failed: {e}"
            logger.error(f"[HookRegistry] {ErrorCodes.AGENT_EXECUTION_CRITICAL.name}: {msg}", exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL, "hook": name},
            ) from e

    def get_all_hooks(self) -> list[str]:
        """Returns a list of all registered hook names."""
        return list(self._hooks.keys())

    def clear(self) -> None:
        """Clears all registered hooks. (Mainly for testing)."""
        self._hooks.clear()

# Global singleton instance
hook_registry = HookRegistry()
