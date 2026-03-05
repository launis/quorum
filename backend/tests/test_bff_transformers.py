
from backend.api.transformers.domain.falsification import FalsificationDomainTransformer
from backend.api.transformers.domain.logic import LogicDomainTransformer
from backend.models.domain.falsifier import FalsifierData, FalsifierOutput, ReasoningFidelity
from backend.models.domain.logician import CognitiveLevel, LogicianData, LogicianOutput, ToulminComponent, WaltonScheme
from backend.models.enums import BloomLevel, FidelityLevel, StrategicDepth
from backend.models.state import WorkflowState
from backend.models.view.semantic_models import SemanticBlock


def test_logic_transformer_graceful_degradation():
    transformer = LogicDomainTransformer()
    # Construct a valid object but then break it to force the transformer to fail
    # We will pass an empty WorkflowState. The _extract_logician_section checks if step_logician exists,
    # but let's mock step_logician as something that will fail during transformation, e.g. missing required nested data.

    # Actually, we can just monkeypatch _transform_logician_data to raise an exception
    def mock_transform(*args, **kwargs):
        raise ValueError("Simulated transformation failure")

    transformer._transform_logician_data = mock_transform

    # Create valid mock state
    state = WorkflowState(
        workflow_id="test",
        step_logician=LogicianOutput(
            logician_data=LogicianData(
                toulmin_analysis=[ToulminComponent(id="1", claim="c", data="d", warrant="w")],
                cognitive_level=CognitiveLevel(
                    bloom_level=BloomLevel.REMEMBERING,
                    strategic_depth=StrategicDepth.LOW,
                    bloom_score=1.0,
                    strategic_score=1.0
                ),
                walton_scheme=WaltonScheme(identified_scheme="A", critical_questions=["Q"]),
                toulmin_score=1.0
            ),
            thought_process="test",
            conclusion="test",
            confidence_score=1.0
        )
    )

    # Ensure it doesn't crash but returns the SemanticBlock with value={}
    result = transformer._extract_logician_section(state)
    assert isinstance(result, SemanticBlock)
    assert result.value == {}
    assert result.id == "logic-analysis"


def test_falsification_transformer_graceful_degradation():
    transformer = FalsificationDomainTransformer()

    def mock_transform(*args, **kwargs):
        raise ValueError("Simulated transformation failure")

    transformer._transform_falsifier_data = mock_transform

    state = WorkflowState(
        workflow_id="test",
        step_falsifier=FalsifierOutput(
            falsifier_data=FalsifierData(
                stress_test_findings=[],
                fidelity_audit=ReasoningFidelity(
                    fidelity_score=FidelityLevel.WEAK,
                    fidelity_numeric=1.0,
                    abductive_score=1.0,
                    plausibility_score=1.0,
                    justification="test"
                )
            ),
            thought_process="test",
            conclusion="test",
            confidence_score=1.0
        )
    )

    result = transformer._extract_falsifier_section(state)
    assert isinstance(result, SemanticBlock)
    assert result.value == {}
    assert result.id == "stress-test"
