import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, WorkflowCompilationError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.step import ExpectedInput, StepRule
from backend_v2.models.domain.workflow import Workflow
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


def test_compute_topological_waves() -> None:
    """Test computing concurrent topological waves for steps."""
    steps = [
        StepRule(id="st_0000000000000001", depends_on=[], task_blueprint="bp", input_mappings={}),
        StepRule(id="st_0000000000000002", depends_on=[], task_blueprint="bp", input_mappings={}),
        StepRule(id="st_0000000000000003", depends_on=["st_0000000000000001"], task_blueprint="bp", input_mappings={}),
        StepRule(id="st_0000000000000004", depends_on=["st_0000000000000002"], task_blueprint="bp", input_mappings={}),
        StepRule(
            id="st_0000000000000005",
            depends_on=["st_0000000000000003", "st_0000000000000004"],
            task_blueprint="bp",
            input_mappings={},
        ),
    ]
    waves = DAGCompilerService.compute_topological_waves(steps)
    assert len(waves) == 3
    assert {s.id for s in waves[0]} == {"st_0000000000000001", "st_0000000000000002"}
    assert {s.id for s in waves[1]} == {"st_0000000000000003", "st_0000000000000004"}
    assert {s.id for s in waves[2]} == {"st_0000000000000005"}


def test_validate_workflow_missing_dep() -> None:
    """Test validation fails if a dependency does not exist."""
    steps = [
        StepRule(id="st_0000000000000001", depends_on=["st_deadbeefdeadbeef"], task_blueprint="bp", input_mappings={})
    ]
    with pytest.raises(ValidationError):
        Workflow(
            historical_context_mode="DISABLED",
            model_registry_id="cfg_model_registry_01",
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


def test_compute_topological_waves_missing_dep_raises() -> None:
    """Test compute_topological_waves raises WorkflowCompilationError on undeclared dependency."""
    steps = [
        StepRule(id="st_0000000000000001", depends_on=["st_missing00000001"], task_blueprint="bp", input_mappings={})
    ]
    with pytest.raises(WorkflowCompilationError) as exc_info:
        DAGCompilerService.compute_topological_waves(steps)
    assert "declares dependency on 'st_missing00000001'" in str(exc_info.value)


def test_validate_workflow_expected_inputs_none_required_raises() -> None:
    """Test validate_workflow raises AppException if expected_inputs has no required inputs."""
    wf = Workflow(
        historical_context_mode="DISABLED",
        model_registry_id="cfg_model_registry_01",
        id="wf_0000000000000001",
        slug="test-workflow",
        name="wf",
        description="test",
        status="active",
        version=1,
        default_profile_id="pf_0000000000000001",
        steps=[StepRule(id="st_0000000000000001", depends_on=[], task_blueprint="bp", input_mappings={})],
        expected_inputs=[
            ExpectedInput(
                input_key="optional_doc",
                label=I18nText(translations={"en": "Doc"}),
                description=I18nText(translations={"en": "Desc"}),
                required=False,
                input_modes=["text"],
                is_chat_history=False,
            )
        ],
    )
    with pytest.raises(AppException) as exc_info:
        DAGCompilerService.validate_workflow(wf)
    assert "at least one input must be 'required=True'" in str(exc_info.value)


def test_validate_workflow_success_and_valid_references() -> None:
    """Test validate_workflow succeeds with valid input references and step dependencies."""
    wf = Workflow(
        historical_context_mode="DISABLED",
        model_registry_id="cfg_model_registry_01",
        id="wf_0000000000000001",
        slug="test-workflow",
        name="wf",
        description="test",
        status="active",
        version=1,
        default_profile_id="pf_0000000000000001",
        steps=[
            StepRule(
                id="st_0000000000000001",
                depends_on=[],
                task_blueprint="bp",
                input_mappings={"doc": "$inputs.main_doc", "all_inp": "$inputs"},
            ),
            StepRule(
                id="st_0000000000000002",
                depends_on=["st_0000000000000001"],
                task_blueprint="bp",
                input_mappings={
                    "prev": "$steps.st_0000000000000001.output",
                    "reducer": "$steps.matrix_reducer",
                    "all_steps": "$steps",
                },
            ),
        ],
        expected_inputs=[
            ExpectedInput(
                input_key="main_doc",
                label=I18nText(translations={"en": "Doc"}),
                description=I18nText(translations={"en": "Desc"}),
                required=True,
                input_modes=["text"],
                is_chat_history=False,
            )
        ],
    )
    DAGCompilerService.validate_workflow(wf)


def test_validate_workflow_unknown_input_reference_raises() -> None:
    """Test validate_workflow raises WorkflowCompilationError on unknown input reference."""
    wf = Workflow(
        historical_context_mode="DISABLED",
        model_registry_id="cfg_model_registry_01",
        id="wf_0000000000000001",
        slug="test-workflow",
        name="wf",
        description="test",
        status="active",
        version=1,
        default_profile_id="pf_0000000000000001",
        steps=[
            StepRule(
                id="st_0000000000000001",
                depends_on=[],
                task_blueprint="bp",
                input_mappings={"doc": "$inputs.unknown_doc"},
            )
        ],
        expected_inputs=[
            ExpectedInput(
                input_key="main_doc",
                label=I18nText(translations={"en": "Doc"}),
                description=I18nText(translations={"en": "Desc"}),
                required=True,
                input_modes=["text"],
                is_chat_history=False,
            )
        ],
    )
    with pytest.raises(WorkflowCompilationError) as exc_info:
        DAGCompilerService.validate_workflow(wf)
    assert "references unknown input '$inputs.unknown_doc'" in str(exc_info.value)


def test_validate_workflow_unexecuted_step_reference_raises() -> None:
    """Test validate_workflow raises WorkflowCompilationError when referencing a step that has not run."""
    wf = Workflow(
        historical_context_mode="DISABLED",
        model_registry_id="cfg_model_registry_01",
        id="wf_0000000000000001",
        slug="test-workflow",
        name="wf",
        description="test",
        status="active",
        version=1,
        default_profile_id="pf_0000000000000001",
        steps=[
            StepRule(
                id="st_0000000000000001",
                depends_on=[],
                task_blueprint="bp",
                input_mappings={"doc": "$steps.st_0000000000000002.output"},
            ),
            StepRule(
                id="st_0000000000000002",
                depends_on=["st_0000000000000001"],
                task_blueprint="bp",
                input_mappings={},
            ),
        ],
        expected_inputs=[
            ExpectedInput(
                input_key="main_doc",
                label=I18nText(translations={"en": "Doc"}),
                description=I18nText(translations={"en": "Desc"}),
                required=True,
                input_modes=["text"],
                is_chat_history=False,
            )
        ],
    )
    with pytest.raises(WorkflowCompilationError) as exc_info:
        DAGCompilerService.validate_workflow(wf)
    assert "references unexecuted or missing step '$steps.st_0000000000000002'" in str(exc_info.value)
