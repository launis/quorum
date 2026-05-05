import logging
from collections.abc import Callable
from typing import Any

from fastapi import status
from pydantic import BaseModel, ConfigDict

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase

logger = logging.getLogger(__name__)


class TaskDefinition(V2CoreBase):
    """Metadata for a registered task."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    handler: Callable[..., Any]
    input_schema: type[BaseModel]
    output_schema: type[BaseModel]
    description: str | None = None
    metadata: dict[str, Any] | None = None


class TaskRegistry:
    """Registry for functional agent tasks."""

    _tasks: dict[str, TaskDefinition] = {}

    @classmethod
    def register_task(
        cls,
        name: str,
        input_schema: type[BaseModel],
        output_schema: type[BaseModel],
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register a function as a task.

        Args:
            name: Unique identifier for the task.
            input_schema: Pydantic model for input validation.
            output_schema: Pydantic model for output validation.
            description: Optional description (defaults to docstring).
            metadata: Optional metadata for the task.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            if name in cls._tasks:
                msg = f"Task with name '{name}' is already registered."
                logger.error("[TaskRegistry] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

            desc = description
            if desc is None and func.__doc__ is not None:
                desc = func.__doc__

            cls._tasks[name] = TaskDefinition(
                name=name,
                handler=func,
                input_schema=input_schema,
                output_schema=output_schema,
                description=desc,
                metadata=metadata,
            )
            return func

        return decorator

    @classmethod
    def get(cls, name: str) -> TaskDefinition:
        """Retrieve a task definition by name."""
        if name not in cls._tasks:
            msg = f"Task '{name}' not found in registry."
            logger.error("[TaskRegistry] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(
                message=msg,
                status_code=status.HTTP_404_NOT_FOUND,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "task_name": name},
            )
        return cls._tasks[name]
