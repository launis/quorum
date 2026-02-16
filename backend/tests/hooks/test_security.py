
import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.hooks.security import sanitize_text_hook, check_banned_phrases_hook, sanitize_text
from backend.models.state import WorkflowState
from backend.models.domain.guard import SanitizationResult
from backend.exceptions import AppException, ErrorCodes, SecurityViolationError

@pytest.fixture
def mock_state():
    return WorkflowState(
        workflow_id="test_wf",
        context_variables={"inputs": {
            "history_text": "History",
            "product_text": "Product",
            "reflection_text": "Reflection"
        }}
    )

def test_sanitize_text_basic():
    """Verify regex redaction works."""
    text = "Contact me at test@example.com or 050-1234567"
    clean, threats = sanitize_text(text)
    assert "[REDACTED_EMAIL]" in clean
    assert "[REDACTED_PHONE_FI]" in clean
    assert "EMAIL: 1 items" in threats

def test_sanitize_hook_success(mock_state):
    """Verify hook populates SanitizationResult."""
    mock_state = mock_state.model_copy(update={
        "context_variables": {
            "inputs": {
                "history_text": "My email is foo@bar.com",
                "product_text": "Clean product",
                "reflection_text": ""
            }
        }
    })
    
    new_state = sanitize_text_hook(mock_state)
    
    result = new_state.context_variables.get("sanitization_result")
    assert isinstance(result, SanitizationResult)
    assert "[REDACTED_EMAIL]" in result.sanitized_inputs["history_text"]
    assert "EMAIL: 1 items" in result.pii_threats_detected

def test_sanitize_hook_missing_inputs(mock_state):
    """Should handle missing inputs gracefully (or fail fast if strict). Code defaults to empty."""
    mock_state = mock_state.model_copy(update={"context_variables": {}})
    # If context is empty, hook returns state as is
    new_state = sanitize_text_hook(mock_state)
    assert new_state == mock_state

def test_banned_phrases_check_defaults(mock_state):
    """Verify fallback to DEFAULT_BANNED_PHRASES if no repository."""
    import asyncio
    
    mock_state = mock_state.model_copy(update={
        "context_variables": {
            "inputs": {"product_text": "This contains a paradigm shift."}
        }
    })

    # Should detect "paradigm shift" from defaults
    with pytest.raises(SecurityViolationError) as exc:
        asyncio.run(check_banned_phrases_hook(mock_state, repository=None))
    
    assert ErrorCodes.SECURITY_VIOLATION in str(exc.value.error_code)
    assert "paradigm shift" in exc.value.details["banned_phrases"]


@pytest.mark.asyncio
async def test_banned_phrases_db_error(mock_state):
    """Fail Fast: Repository error raises SECURITY_DB_ERROR."""
    mock_repo = AsyncMock()
    mock_repo.get_banned_phrases.side_effect = Exception("DB Down")
    
    with pytest.raises(AppException) as exc:
        await check_banned_phrases_hook(mock_state, repository=mock_repo)
    
    assert exc.value.error_code == ErrorCodes.SECURITY_DB_ERROR

@pytest.mark.asyncio
async def test_banned_phrases_detected(mock_state):
    """Raise SecurityViolationError if phrase detected."""
    mock_repo = AsyncMock()
    mock_repo.get_banned_phrases.return_value = [{"phrase": "secret"}]
    
    mock_state = mock_state.model_copy(update={
        "context_variables": {
            "inputs": {"product_text": "This is a secret message."}
        }
    })
    
    with pytest.raises(SecurityViolationError) as exc:
        await check_banned_phrases_hook(mock_state, repository=mock_repo)
    
    assert exc.value.error_code == ErrorCodes.SECURITY_VIOLATION
    assert "secret" in exc.value.details["banned_phrases"]

@pytest.mark.asyncio
async def test_banned_phrases_clean(mock_state):
    """Valid input updates SanitizationResult."""
    mock_repo = AsyncMock()
    mock_repo.get_banned_phrases.return_value = [{"phrase": "forbidden"}]
    
    mock_state = mock_state.model_copy(update={
        "context_variables": {
            "inputs": {"product_text": "Clean text."},
            # Pre-existing result to verify merge
            "sanitization_result": SanitizationResult(
                 sanitized_inputs={}, pii_threats_detected=[], banned_phrases_detected=[]
            )
        }
    })
    
    new_state = await check_banned_phrases_hook(mock_state, repository=mock_repo)
    result = new_state.context_variables["sanitization_result"]
    assert result.banned_phrases_detected == []
