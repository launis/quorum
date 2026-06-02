import logging
from collections.abc import Callable
from typing import Any

from fastapi import status
from pydantic import BaseModel, ConfigDict

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase

logger = logging.getLogger(__name__)


class TaskDefinition(V2CoreBase):
    """Metadata for a registered task.

    Attributes:
        name: Unique task identifier.
        handler: Handing callable logic.
        input_schema: Input Pydantic model.
        output_schema: Output Pydantic model.
        description: Task description text.
        metadata: Arbitrary associated dict metadata.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    handler: Callable[..., Any]
    input_schema: type[BaseModel]
    output_schema: type[BaseModel]
    description: str | None = None
    metadata: dict[str, Any] | None = None


class TaskRegistry:
    """Registry for functional agent tasks.

    Provides safe, static, global execution tracking of agentic
    routines linked with formal Pydantic schemas.

    Attributes:
        _tasks: Internal registry storage mapping task names to TaskDefinitions.
    """

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

        Returns:
            A decorator function that registers the decorated callable and returns it.

        Raises:
            AppException: Triggered with CONFIGURATION_ERROR if the task name is already registered.
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
        """Retrieve a task definition by name.

        Args:
            name: Task name identifier.

        Returns:
            The corresponding registered TaskDefinition structure.

        Raises:
            AppException: Triggered with RESOURCE_NOT_FOUND if the requested task does not exist.
        """
        if name not in cls._tasks:
            msg = f"Task '{name}' not found in registry."
            logger.error("[TaskRegistry] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(
                message=msg,
                status_code=status.HTTP_404_NOT_FOUND,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "task_name": name},
            )
        return cls._tasks[name]
