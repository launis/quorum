from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.exceptions import WorkflowCompilationError
from backend_v2.models.v2_core import StepRule, Workflow
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService


def test_extract_root_namespace() -> None:
    """Test parsing of variable root namespaces."""
    assert DAGCompilerService._extract_root_namespace("$inputs.user_id") == "$inputs.user_id"
    assert DAGCompilerService._extract_root_namespace("$steps.my_step.output.result") == "$steps.my_step"
    assert DAGCompilerService._extract_root_namespace("$inputs") == "$inputs"
    assert DAGCompilerService._extract_root_namespace("$steps") == "$steps"


def test_ensure_acyclic() -> None:
    """Test cycle detection in DAGs."""
    # Valid linear dependency
    steps = [
        StepRule(id="st_0000000000000001", depends_on=[], task_blueprint="bp", input_mappings={}),
        StepRule(id="st_0000000000000002", depends_on=["st_0000000000000001"], task_blueprint="bp", input_mappings={}),
    ]
    DAGCompilerService._ensure_acyclic(steps)

    # Invalid cyclic dependency
    steps_cycle = [
        StepRule(id="st_0000000000000001", depends_on=["st_0000000000000002"], task_blueprint="bp", input_mappings={}),
        StepRule(id="st_0000000000000002", depends_on=["st_0000000000000001"], task_blueprint="bp", input_mappings={}),
    ]
    with pytest.raises(WorkflowCompilationError):
        DAGCompilerService._ensure_acyclic(steps_cycle)


def test_get_topological_order() -> None:
    """Test topological sorting of steps."""
    steps = [
        StepRule(id="st_0000000000000003", depends_on=["st_0000000000000002"], task_blueprint="bp", input_mappings={}),
        StepRule(id="st_0000000000000001", depends_on=[], task_blueprint="bp", input_mappings={}),
        StepRule(id="st_0000000000000002", depends_on=["st_0000000000000001"], task_blueprint="bp", input_mappings={}),
    ]
    ordered = DAGCompilerService._get_topological_order(steps)
    assert [s.id for s in ordered] == ["st_0000000000000001", "st_0000000000000002", "st_0000000000000003"]


def test_validate_workflow_missing_dep() -> None:
    """Test validation fails if a dependency does not exist."""
    steps = [
        StepRule(id="st_0000000000000001", depends_on=["st_deadbeefdeadbeef"], task_blueprint="bp", input_mappings={})
    ]
    with pytest.raises(ValidationError):
        Workflow(
            allowed_exports=["pdf"],
            historical_context_mode="DISABLED",
            id="wf_0000000000000001",
            slug="test-workflow",
            name="wf",
            description="test",
            status="active",
            version=1,
            default_profile_id="pf_0000000000000001",
            steps=steps,
            expected_inputs=[],
        )
