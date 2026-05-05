import pytest
from pydantic import BaseModel, ValidationError

from backend_v2.core.registry import TaskDefinition, TaskRegistry
from backend_v2.exceptions import AppException


class DummyInput(BaseModel):
    val: str


class DummyOutput(BaseModel):
    res: str


def test_task_registry_registration() -> None:
    registry = TaskRegistry()
    registry._tasks.clear()

    @registry.register_task(name="test_task", input_schema=DummyInput, output_schema=DummyOutput)
    def dummy_handler(data: DummyInput) -> DummyOutput:
        return DummyOutput(res=data.val)

    task = registry.get("test_task")
    assert task.name == "test_task"
    assert task.input_schema == DummyInput

    with pytest.raises(AppException) as exc:
        registry.get("unknown_task")
    assert exc.value.status_code == 404

    # Test duplicate
    with pytest.raises(AppException) as exc:
        @registry.register_task(name="test_task", input_schema=DummyInput, output_schema=DummyOutput)
        def duplicate_handler(data: DummyInput) -> DummyOutput:
            return DummyOutput(res="dup")
    assert exc.value.status_code == 500


def test_task_definition_strictness() -> None:
    def handler() -> None: pass
    
    td = TaskDefinition(
        name="test",
        handler=handler,
        input_schema=DummyInput,
        output_schema=DummyOutput
    )
    assert td.name == "test"

    with pytest.raises(ValidationError):
        TaskDefinition(
            name="test",
            handler=handler,
            input_schema=DummyInput,
            output_schema=DummyOutput,
            extra="fail"  # type: ignore
        )
