import pytest
from pydantic import BaseModel

from backend_v2.core.registry import TaskRegistry
from backend_v2.exceptions import AppException, ErrorCodes


class DummyInput(BaseModel):
    data: str


class DummyOutput(BaseModel):
    result: str


def test_task_registry_register_and_get() -> None:
    @TaskRegistry.register_task(
        name="test_task", input_schema=DummyInput, output_schema=DummyOutput, description="A test task"
    )
    def my_task(input_data: DummyInput) -> DummyOutput:
        return DummyOutput(result=input_data.data + "_done")

    task_def = TaskRegistry.get("test_task")
    assert task_def is not None
    assert task_def.name == "test_task"
    assert task_def.input_schema == DummyInput
    assert task_def.output_schema == DummyOutput

    res = my_task(DummyInput(data="hello"))
    assert res.result == "hello_done"


def test_task_registry_fails_fast_on_duplicate() -> None:
    with pytest.raises(AppException) as excinfo:

        @TaskRegistry.register_task(
            name="test_task",
            input_schema=DummyInput,
            output_schema=DummyOutput,
        )
        def my_task2(input_data: DummyInput) -> DummyOutput:
            return DummyOutput(result="")

    assert excinfo.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


def test_task_registry_fails_fast_on_missing() -> None:
    with pytest.raises(AppException) as excinfo:
        TaskRegistry.get("non_existent_task")

    assert excinfo.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


def test_task_registry_uses_docstring_for_description() -> None:
    @TaskRegistry.register_task(
        name="docstring_task",
        input_schema=DummyInput,
        output_schema=DummyOutput,
    )
    def my_task3(input_data: DummyInput) -> DummyOutput:
        """My nice docstring."""
        return DummyOutput(result="")

    task_def = TaskRegistry.get("docstring_task")
    assert task_def.description == "My nice docstring."
