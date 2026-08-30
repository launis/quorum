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
from typing import Any, Protocol, TypeVar

from fastapi import status
from pydantic import Field

from backend_v2.database.interfaces import (
    IAuditRepository,
    IComponentRepository,
    IExecutionRepository,
    IIdentityRepository,
    IOutputProfileRepository,
    IPromptBlockRepository,
    ISystemRepository,
    IWorkflowRepository,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO, GlobalContextVarsDTO, HookDeltaDTO
from backend_v2.models.execution_core import ExecutionMetadata

logger = logging.getLogger(__name__)

__all__ = [
    "ExecutionInputsDTO",
    "GlobalContextVarsDTO",
    "HookDeltaDTO",
    "HookDependencies",
    "HookFunction",
    "HookRegistry",
    "HookResult",
    "HookState",
    "ISearchClient",
    "hook_registry",
]


class ISearchClient(Protocol):
    """Protocol for abstracting search client I/O from hook execution."""

    async def search(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """Executes a search query and returns search results."""
        ...


@dataclass(frozen=True)
class HookDependencies:
    """Strictly typed DI container separating infrastructure from data."""

    exec_repo: IExecutionRepository
    workflow_repo: IWorkflowRepository
    comp_repo: IComponentRepository
    prompt_block_repo: IPromptBlockRepository
    output_profile_repo: IOutputProfileRepository
    identity_repo: IIdentityRepository
    audit_repo: IAuditRepository
    system_repo: ISystemRepository
    search_client: ISearchClient | None = None


class HookState(V2CoreBase):
    """Immutable cognitive data model for hook execution.

    Enforces rules: Fail-Fast, Zero Side-Effects (frozen=True).
    """

    execution_id: str
    workflow_id: str
    step_id: str | None = None
    task_blueprint: str | None = None
    metadata: ExecutionMetadata = Field(...)
    global_context_vars: GlobalContextVarsDTO = Field(default_factory=GlobalContextVarsDTO)
    inputs: ExecutionInputsDTO = Field(default_factory=ExecutionInputsDTO)


class HookResult(V2CoreBase):
    """Explicit state delta returned by Hooks for deep merging."""

    success: bool
    state_delta: HookDeltaDTO | None = Field(default=None)


# Strict type definition for a hook function
# It accepts HookState and HookDependencies, returning a HookResult State Delta
# It can be either synchronous or asynchronous
HookFunction = Callable[[HookState, HookDependencies], HookResult | Awaitable[HookResult]]
F = TypeVar("F", bound=HookFunction)


class HookRegistry:
    """Singleton registry for managing dynamic Python hooks."""

    _instance: HookRegistry | None = None
    _hooks: dict[str, HookFunction]

    def __new__(cls) -> HookRegistry:
        """Create or return the singleton instance of HookRegistry."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._hooks = {}
        return cls._instance

    def register(self, name: str) -> Callable[[F], F]:
        """Decorator to register a function in the hook registry.

        Args:
            name (str): The unique identifier for the hook.

        Returns:
            Callable: The decorator function.

        Raises:
            AppException: If a hook with the given name is already registered.
        """

        def decorator(func: F) -> F:
            if name in self._hooks:
                msg = f"Hook with name '{name}' is already registered."
                logger.error("[HookRegistry] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

            logger.info("Registering hook: %s -> %s", name, func.__name__)
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
            logger.error("[HookRegistry] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(
                message=msg,
                status_code=status.HTTP_404_NOT_FOUND,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "hook_name": name},
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
            logger.debug("Executing hook '%s' for step '%s'", name, state.step_id)

            # Execute taking into account whether it is a coroutine
            if inspect.iscoroutinefunction(hook_func):
                result = await hook_func(state, deps)
            else:
                result = hook_func(state, deps)

            # Enforce strict return type according to architectural mandate
            if not isinstance(result, HookResult):
                msg = f"Hook '{name}' returned invalid type '{type(result).__name__}'. Must return HookResult."
                logger.error("[HookRegistry] %s: %s", ErrorCodes.AGENT_EXECUTION_CRITICAL.name, msg)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.value},
                )

            return result

        except AppException:
            # Re-raise already constructed exceptions without wrapping
            raise
        except Exception as e:
            msg = f"Hook '{name}' execution failed: {e}"
            logger.error("[HookRegistry] %s: %s", ErrorCodes.AGENT_EXECUTION_CRITICAL.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.value, "hook": name},
            ) from e

    def get_all_hooks(self) -> list[str]:
        """Returns a list of all registered hook names.

        Returns:
            A list of strings containing the names of all registered hooks.
        """
        return list(self._hooks.keys())

    def clear(self) -> None:
        """Clears all registered hooks. (Mainly for testing).

        Returns:
            None.
        """
        self._hooks.clear()


# Global singleton instance
hook_registry = HookRegistry()
