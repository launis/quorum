import pytest
from pydantic import ValidationError

from backend_v2.models.workflow import ComponentScoringRule, ScoringLogic, WorkflowDefinition, WorkflowStep


def test_workflow_step_valid() -> None:
    step = WorkflowStep(
        name="Test Step",
        task_key="test_task",
    )
    assert step.name == "Test Step"
    assert step.task_key == "test_task"
    assert step.id.startswith("step_")


def test_workflow_step_invalid_whitespace() -> None:
    with pytest.raises(ValidationError):
        WorkflowStep(name="Test", task_key="   ")


def test_component_scoring_rule_valid() -> None:
    rule = ComponentScoringRule(
        component_id="comp_1",
        metric_key="score",
    )
    assert rule.component_id == "comp_1"
    assert rule.weight == 1.0


def test_scoring_logic_valid() -> None:
    logic = ScoringLogic(
        label="Main Logic",
    )
    assert logic.label == "Main Logic"


def test_workflow_definition_valid() -> None:
    wf = WorkflowDefinition(
        name="Test Workflow",
        description="A workflow for testing",
        organization_id="org_123",
    )
    assert wf.status == "draft"
    assert wf.version == 1


def test_workflow_definition_invalid_status() -> None:
    with pytest.raises(ValidationError):
        WorkflowDefinition(
            name="Test",
            description="Test",
            organization_id="org_123",
            status="invalid_status",  # type: ignore
        )
