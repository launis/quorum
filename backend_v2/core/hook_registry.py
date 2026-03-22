"""Dynamic Hook Registry for the Cognitive Quorum System (V2).

This module provides a singleton registry for registering and executing Python
functions (hooks) dynamically. It enforces strict typing (Dict -> Dict) and
"Fail-Fast" principles, allowing legacy V1 capabilities to be exposed without
hardcoded domain model dependencies.
"""

import inspect
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Protocol

from fastapi import status
from pydantic import BaseModel, ConfigDict, Field

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

from backend_v2.database.repository import AbstractWorkflowRepository


class IExecutionRepository(Protocol):
    """Protocol for abstracting repository I/O from hook execution."""
    async def get_execution(self, execution_id: str) -> dict[str, Any] | None: ...
    async def update_execution(self, execution_id: str, updates: dict[str, Any]) -> None: ...


class ISearchClient(Protocol):
    """Protocol for abstracting search client I/O from hook execution."""
    async def search(self, query: str) -> list[dict[str, Any]]: ...


@dataclass(frozen=True)
class HookDependencies:
    """Strictly typed DI container separating infrastructure from data."""
    repository: AbstractWorkflowRepository
    search_client: ISearchClient | None = None


class HookState(BaseModel):
    """Immutable cognitive data model for hook execution.
    Enforces rules: Fail-Fast, Zero Side-Effects (frozen=True).
    """
    model_config = ConfigDict(frozen=True, extra='forbid', strict=True)
    execution_id: str
    workflow_id: str
    step_id: str | None = None
    task_blueprint: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    global_context_vars: dict[str, Any] = Field(default_factory=dict)
    inputs: dict[str, Any]


class HookResult(BaseModel):
    """Explicit state delta returned by Hooks for deep merging."""
    success: bool
    state_delta: dict[str, Any] | None = None


# Strict type definition for a hook function
# It accepts HookState and HookDependencies, returning a HookResult State Delta
# It can be either synchronous or asynchronous
HookFunction = Callable[[HookState, HookDependencies], HookResult | Awaitable[HookResult]]


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

    async def execute(self, name: str, state: HookState, deps: HookDependencies) -> HookResult:
        """Executes a registered hook securely.

        Handles both synchronous and asynchronous functions and enforces
        the strict HookState and HookDependencies injection, ensuring Fail-Fast protocol.

        Args:
            name (str): The name of the hook to execute.
            state (HookState): The immutable data payload.
            deps (HookDependencies): The strictly typed DI container.

        Returns:
            HookResult: The explicit state delta result.

        Raises:
            AppException: If execution fails or returns an invalid type.
        """
        hook_func = self.get_hook(name)

        try:
            logger.debug(f"Executing hook '{name}' for step '{state.step_id}'")

            # Execute taking into account whether it is a coroutine
            if inspect.iscoroutinefunction(hook_func):
                result = await hook_func(state, deps)
            else:
                result = hook_func(state, deps)

            # Enforce strict return type according to architectural mandate
            if not isinstance(result, HookResult):
                msg = f"Hook '{name}' returned invalid type '{type(result).__name__}'. Must return HookResult."
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
