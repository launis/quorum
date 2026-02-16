"""Component definition model."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, TypeVar

# Generic Types for flexible but strict interfaces
InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class BaseComponent(ABC, Generic[InputT, OutputT]):
    """Abstract base class for all workflow components.

    Enforces strictly typed, asynchronous execution contracts.

    Mandates:
    1. Async Execution: All components must be async.
    2. Strict Typing: Inputs and Outputs must be defined.
    3. Error Handling: All exceptions MUST be wrapped in `backend.exceptions.AppException`.
    """

    @abstractmethod
    async def execute(
        self,
        input_data: InputT,
        execution_context: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> OutputT:
        """Executes the component logic.

        Args:
            input_data (InputT): Main input payload.
            execution_context (Optional[Dict[str, Any]]): Context variables (config, repo, etc).
            **kwargs: Arbitrary keyword arguments (e.g., system_instruction).

        Returns:
            OutputT: The component output.

        Raises:
            AppException: If execution fails.
        """
        pass
