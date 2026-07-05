from backend_v2.models.state import StepOutputDTO
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import ContextBuilder


class DummyCompiler(PromptCompiler):
    def __init__(self) -> None:
        pass


def test_extract() -> None:
    state_data = {
        "steps": [
            StepOutputDTO(step_id="sr_123", block_id="sr_123", data_type="unknown", payload={"some": "data"}),
            StepOutputDTO(step_id="sr_456", block_id="sr_456", data_type="unknown", payload={"other": "data"}),
        ],
        "inputs": {"product_text": "input data"},
    }

    compiler = DummyCompiler()

    # 1. Test PromptCompiler extraction of specific step
    try:
        val1 = compiler._extract_value_from_state("$steps.sr_123", state_data)
        print("PromptCompiler successfully extracted $steps.sr_123:", val1)
    except Exception as e:
        print("PromptCompiler FAILED to extract $steps.sr_123:", e)

    # 2. Test ContextBuilder
    input_mappings = {"analyst_report": "$steps.sr_123"}
    llm_context, new_mappings = ContextBuilder.build(
        input_mappings=input_mappings, state_data=state_data, schema_map={"sr_123": "unknown"}
    )
    print("ContextBuilder llm_context_data keys:", list(llm_context.keys()))


if __name__ == "__main__":
    test_extract()
