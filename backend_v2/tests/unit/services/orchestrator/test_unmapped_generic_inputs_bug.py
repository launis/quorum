import pytest

from backend_v2.exceptions import AppException, ErrorCodes, WorkflowCompilationError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.step import ExpectedInput, StepRule
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.prompt import LLMContextDataDTO
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


def test_reproduce_prompt_compiler_crash_on_raw_inputs() -> None:
    """Reproduces the exact runtime crash from backend_debug.log line 579.

    When a step contains 'inputs': '$inputs' (which was injected by Flutter Studio _addStep),
    PromptCompiler.build_xml_context raises AppException because '$inputs' cannot resolve
    to any declared expected_input key ($inputs.<key>).
    """
    compiler = PromptCompiler()
    state = LLMContextDataDTO(
        inputs={
            "inputs": "all raw inputs",
            "chat_log": "User: Hello",
            "product_text": "Deliverable content",
        }
    )
    expected_inputs = [
        ExpectedInput(
            input_key="chat_log",
            label=I18nText(translations={"en": "Chat Log"}),
            description=I18nText(translations={"en": "Chat log description"}),
            is_chat_history=True,
            input_modes=["file", "paste"],
            required=True,
        ),
        ExpectedInput(
            input_key="product_text",
            label=I18nText(translations={"en": "Product Deliverable"}),
            description=I18nText(translations={"en": "Product text description"}),
            is_chat_history=False,
            input_modes=["file", "paste"],
            required=False,
        ),
    ]

    # Exactly the input_mappings found on step sr_e40d96fd843f4cad
    input_mappings = {
        "inputs": "$inputs",
        "chat_log": "$inputs.chat_log",
        "product_text": "$inputs.product_text",
    }

    with pytest.raises(AppException) as exc_info:
        compiler.build_xml_context(
            input_mappings=input_mappings,
            state_data=state,
            target_locale="en",
            expected_inputs=expected_inputs,
        )

    assert exc_info.value.error_code == ErrorCodes.CONFIGURATION_ERROR
    assert "Unmapped input reference '$inputs'" in str(exc_info.value)


def test_dag_compiler_should_reject_generic_inputs_preflight() -> None:
    """Pre-flight Fail-Fast: DAGCompilerService must reject generic '$inputs' references.

    Currently, DAGCompilerService has a blind spot:
        if root_namespace == "$inputs": continue
    which lets raw '$inputs' pass validation, causing runtime crashes during execution.
    This test asserts that DAGCompilerService raises WorkflowCompilationError on generic '$inputs'.
    """
    wf = Workflow(
        id="wf_0000000000000001",
        slug="test-workflow",
        name="wf",
        description="test",
        status="active",
        version=1,
        default_profile_id="pf_0000000000000001",
        historical_context_mode="DISABLED",
        model_registry_id="cfg_model_registry_01",
        steps=[
            StepRule(
                id="sr_0000000000000001",
                task_blueprint="sp_db849f9790984585",
                depends_on=[],
                input_mappings={
                    "inputs": "$inputs",
                    "chat_log": "$inputs.chat_log",
                },
            ),
        ],
        expected_inputs=[
            ExpectedInput(
                input_key="chat_log",
                label=I18nText(translations={"en": "Chat Log"}),
                description=I18nText(translations={"en": "Chat log description"}),
                required=True,
                input_modes=["file", "paste"],
                is_chat_history=True,
            )
        ],
    )

    with pytest.raises(WorkflowCompilationError) as exc_info:
        DAGCompilerService.validate_workflow(wf)

    assert (
        "references unknown or generic input '$inputs'" in str(exc_info.value)
        or "generic" in str(exc_info.value)
        or "unknown" in str(exc_info.value)
    )
