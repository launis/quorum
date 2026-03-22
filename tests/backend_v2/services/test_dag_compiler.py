import pytest

from backend_v2.exceptions import AppException, WorkflowCompilationError
from backend_v2.models.v2_core import ExpectedInput, StepRule, Workflow
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService


def _create_base_workflow(steps: list[StepRule], expected_inputs: list[ExpectedInput] | None = None) -> Workflow:
    return Workflow.model_validate({
        "id": "testwf_12345678",
        "slug": "test_wf",
        "name": {"default_locale": "en", "translations": {"en": "Test Workflow"}},
        "description": {"default_locale": "en", "translations": {"en": "Test description"}},
        "organization_id": "system",
        "steps": steps,
        "expected_inputs": expected_inputs or [],
        "output_profiles": {},
    })

def test_valid_linear_dag() -> None:
    steps = [
        StepRule(id="step_11111111", task_blueprint="foo", depends_on=[]),
        StepRule(id="step_22222222", task_blueprint="bar", depends_on=["step_11111111"]),
        StepRule(id="step_33333333", task_blueprint="baz", depends_on=["step_22222222"]),
    ]
    wf = _create_base_workflow(steps)
    # Should not raise any exceptions
    DAGCompilerService.validate_workflow(wf)

def test_valid_parallel_dag() -> None:
    steps = [
        StepRule(id="step_11111111", task_blueprint="foo", depends_on=[]),
        StepRule(id="stepa_22222222", task_blueprint="bar", depends_on=["step_11111111"]),
        StepRule(id="stepb_22222222", task_blueprint="baz", depends_on=["step_11111111"]),
        StepRule(id="step_33333333", task_blueprint="qux", depends_on=["stepa_22222222", "stepb_22222222"]),
    ]
    wf = _create_base_workflow(steps)
    DAGCompilerService.validate_workflow(wf)

def test_cyclic_dependency_rejected() -> None:
    steps = [
        StepRule(id="step_11111111", task_blueprint="a", depends_on=["step_22222222"]),
        StepRule(id="step_22222222", task_blueprint="b", depends_on=["step_11111111"]),
    ]
    wf = _create_base_workflow(steps)
    with pytest.raises(WorkflowCompilationError) as exc_info:
        DAGCompilerService.validate_workflow(wf)

    assert "Cyclic dependency" in str(exc_info.value.message)

def test_cyclic_dependency_self_rejected() -> None:
    steps = [
        StepRule(id="step_11111111", task_blueprint="a", depends_on=["step_11111111"]),
    ]
    wf = _create_base_workflow(steps)
    with pytest.raises(WorkflowCompilationError) as exc_info:
        DAGCompilerService.validate_workflow(wf)

    assert "Cyclic dependency" in str(exc_info.value.message)

def test_dangling_input_reference_rejected() -> None:
    # Expects "doc_id" but references "user_id"
    steps = [
        StepRule(
            id="step_11111111",
            task_blueprint="a",
            depends_on=[],
            input_mappings={"val": "$inputs.user_id"}
        ),
    ]
    expected_inputs = [
        ExpectedInput.model_validate({
            "input_key": "doc_id",
            "required": True,
            "label": {"default_locale": "en", "translations": {"en": "doc"}},
            "description": {"default_locale": "en", "translations": {"en": "doc"}},
            "input_modes": ["file"]
        })
    ]
    wf = _create_base_workflow(steps, expected_inputs)
    with pytest.raises(WorkflowCompilationError) as exc_info:
        DAGCompilerService.validate_workflow(wf)

    assert "references unknown input" in str(exc_info.value.message)

def test_valid_input_reference() -> None:
    steps = [
        StepRule(
            id="step_11111111",
            task_blueprint="a",
            depends_on=[],
            input_mappings={"val": "$inputs.doc_id"}
        ),
    ]
    expected_inputs = [
        ExpectedInput.model_validate({
            "input_key": "doc_id",
            "required": True,
            "label": {"default_locale": "en", "translations": {"en": "doc"}},
            "description": {"default_locale": "en", "translations": {"en": "doc"}},
            "input_modes": ["file"]
        })
    ]
    wf = _create_base_workflow(steps, expected_inputs)
    # Should compile cleanly
    DAGCompilerService.validate_workflow(wf)

def test_out_of_order_step_reference_rejected() -> None:
    # step_1 depends on step_2 for variables but doesn't declare the edge
    steps = [
        StepRule(
            id="step_11111111",
            task_blueprint="a",
            depends_on=[],
            input_mappings={"val": "$steps.step_22222222.result"}
        ),
        StepRule(
            id="step_22222222",
            task_blueprint="b",
            depends_on=[]
        ),
    ]
    wf = _create_base_workflow(steps)
    with pytest.raises(WorkflowCompilationError) as exc_info:
        DAGCompilerService.validate_workflow(wf)

    assert "references unexecuted or missing step" in str(exc_info.value.message)

def test_valid_step_reference() -> None:
    # step_2 correctly depends on step_1
    steps = [
        StepRule(
            id="step_11111111",
            task_blueprint="a",
            depends_on=[],
        ),
        StepRule(
            id="step_22222222",
            task_blueprint="b",
            depends_on=["step_11111111"],
            input_mappings={"val": "$steps.step_11111111.result"}
        ),
    ]
    wf = _create_base_workflow(steps)
    DAGCompilerService.validate_workflow(wf)

def test_missing_required_input_in_model() -> None:
    steps = [StepRule(id="step_11111111", task_blueprint="a")]
    expected_inputs = [
        ExpectedInput.model_validate({
            "input_key": "optional",
            "required": False,
            "label": {"default_locale": "en", "translations": {"en": "doc"}},
            "description": {"default_locale": "en", "translations": {"en": "doc"}},
            "input_modes": ["file"]
        })
    ]
    with pytest.raises(AppException) as exc_info:
        DAGCompilerService.validate_workflow(_create_base_workflow(steps, expected_inputs))

    assert "at least one input must be 'required=True'" in str(exc_info.value.message)
    assert exc_info.value.status_code == 400
