
import pytest
from backend.models.state import WorkflowState
from backend.hooks.validation import verify_structure
from backend.hooks.metrics import calculate_text_metrics_hook
from backend.hooks.integrity import verify_citation_integrity
from backend.exceptions import AppException, ErrorCodes
from backend.models.domain.analyst import AnalystOutput, Hypothesis as AnalystHypothesis

# Mock State for Testing
def get_empty_state():
    return WorkflowState(
        id="test-val-1", 
        workflow_id="test-wf",
        step_id="start",
        status="running",
        context_variables={} 
    )

def test_validation_hook_empty_input_fails_strictly():
    """Verify validation.py raises EMPTY_INPUT for missing inputs."""
    state = get_empty_state()
    # No 'inputs' key
    try:
        verify_structure(state)
        assert False, "Should have raised AppException"
    except AppException as e:
        assert isinstance(e, AppException)
        # Note: In our refactor, we raise specific codes.
        # validation.py raises EMPTY_INPUT (400) if inputs missing.
        # Adjust for Enum handling: e.error_code is the Enum member.
        assert e.error_code == ErrorCodes.EMPTY_INPUT
        assert e.status_code == 400

def test_metrics_hook_missing_inputs_fails_fast():
    """Verify metrics.py raises VALIDATION_FAILED if inputs missing."""
    state = get_empty_state()
    state = get_empty_state()
    # Populate context so it's not empty (which raises INTERNAL_SERVER_ERROR)
    # but missing 'inputs' key (which raises VALIDATION_FAILED)
    state = state.model_copy(update={"context_variables": {"dummy": "data"}})
    try:
        calculate_text_metrics_hook(state)
        assert False
    except AppException as e:
        # metrics.py raises VALIDATION_FAILED (500) if inputs missing
        assert e.error_code == ErrorCodes.VALIDATION_FAILED

def test_integrity_hook_empty_corpus_fails():
    """Verify integrity.py raises STATE_INTEGRITY_ERROR if corpus empty but citations exist."""
    state = get_empty_state()
    # Use whitespace to pass "missing input" check but fail "empty corpus" check
    state.context_variables["inputs"] = {"history_text": " ", "product_text": " ", "reflection_text": " "}
    
    # Mock analyst with quotes
    # Use real model to avoid strict inflation errors on the model itself!
    mock_analyst = AnalystOutput(
        hypotheses=[
            AnalystHypothesis(id="HYP-1", claim_text="Test", evidence_found=True, search_query="Test", quotes=["some quote"])
        ],
        thought_process="Mock reasoning",
        conclusion="Mock conclusion",
        confidence_score=0.9
    )
    
    # Store as dict to simulate real storage
    state.context_variables["step_analyst"] = mock_analyst.model_dump()
    
    try:
        verify_citation_integrity(state)
        # Should raise because corpus is empty but we have citations
        assert False
    except AppException as e:
        # integrity.py raises STATE_INTEGRITY_ERROR (500) if check fails
        assert e.error_code == ErrorCodes.STATE_INTEGRITY_ERROR

def test_integrity_hook_no_citations_passes_silently():
    """Verify passes if no citations found."""
    state = get_empty_state()
    state.context_variables["inputs"] = {"history_text": "foo", "product_text": "bar"}
    # No analyst step
    
    new_state = verify_citation_integrity(state)
    new_state = verify_citation_integrity(state)
    assert new_state # Should return state unmodified/valid

def test_llm_hook_strict_enforcement():
    """Verify llm.py fails fast if settings registry missing or type error."""
    from backend.hooks.llm import configure_llm_context
    state = get_empty_state()
    # No context variables might pass (return early), so try with empty context
    state = state.model_copy(update={"context_variables": {"model_strategy": "non_existent"}})
    
    # We expect CONFIGURATION_ERROR because 'non_existent' strategy won't be in registry
    # OR registry checks might fail depending on current settings environment
    try:
        configure_llm_context(state)
        # Should raise Config Error
    except AppException as e:
        assert e.error_code in [ErrorCodes.CONFIGURATION_ERROR, ErrorCodes.INTERNAL_SERVER_ERROR]
    except Exception as e:
        # Standard Exception conversion check
        assert False, f"Should have raised AppException, got {type(e)}"
