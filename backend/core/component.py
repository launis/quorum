"""Component definition model."""

from abc import ABC, abstractmethod
from typing import Any


class BaseComponent(ABC):
    """Abstract base class for all workflow components.

    All components must inherit from this class and implement the execute method.
    """

    @abstractmethod
    def execute(self, state: Any = None, **kwargs: Any) -> Any:
        """Executes the component logic.

        Args:
            state (Any, optional): The current execution state.
            *args: Variable positional arguments.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Any: The output of the component execution.

        """
        pass
