from abc import ABC, abstractmethod
from typing import Any


class BaseComponent(ABC):
    """Abstract base class for all workflow components.
    All components must inherit from this class and implement the execute method.
    """

    @abstractmethod
    def execute(self, **kwargs) -> dict[str, Any]:
        """Executes the component logic.

        Args:
            **kwargs: Input arguments for the component.

        Returns:
            Dict[str, Any]: The output of the component execution.

        """
        pass
