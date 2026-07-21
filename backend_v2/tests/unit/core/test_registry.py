import pytest
from pydantic import BaseModel, ValidationError

from backend_v2.core.registry import (
    GridSchemaStrategy,
    HeroInsightSchemaStrategy,
    MarkdownSchemaStrategy,
    TaskDefinition,
    TaskRegistry,
    get_schema_strategy,
    register_sdui_schema,
)
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
    def handler() -> None:
        pass

    td = TaskDefinition(name="test", handler=handler, input_schema=DummyInput, output_schema=DummyOutput)
    assert td.name == "test"

    with pytest.raises(ValidationError):
        TaskDefinition(
            name="test",
            handler=handler,
            input_schema=DummyInput,
            output_schema=DummyOutput,
            extra="fail",  # type: ignore
        )


def test_get_schema_strategy_resolves_correctly() -> None:
    assert get_schema_strategy("markdown") == MarkdownSchemaStrategy
    assert get_schema_strategy("hero_insight") == HeroInsightSchemaStrategy
    assert get_schema_strategy("grid") == GridSchemaStrategy


def test_get_schema_strategy_unknown_raises_error() -> None:
    with pytest.raises(AppException) as exc:
        get_schema_strategy("unknown_type")
    assert exc.value.status_code == 500
    assert "Unknown expected_sdui_type" in exc.value.message


def test_register_sdui_schema_duplicate_raises_error() -> None:
    with pytest.raises(AppException) as exc:

        @register_sdui_schema("grid")
        class DuplicateGridSchemaStrategy(GridSchemaStrategy):
            pass

    assert exc.value.status_code == 500
    assert "is already registered" in exc.value.message
