import pytest

from backend_v2.exceptions import AppException
from backend_v2.llm.mock import MockLLMService
from backend_v2.settings import get_settings


def test_mock_llm_service_forbidden(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that MockLLMService crashes if use_mock_llm is False."""
    settings = get_settings()
    monkeypatch.setattr(settings, "use_mock_llm", False)
    with pytest.raises(RuntimeError, match="STRICT EXECUTION AUTHORITY"):
        MockLLMService()


def test_mock_llm_service_generate_content(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test generation of content."""
    settings = get_settings()
    monkeypatch.setattr(settings, "use_mock_llm", True)

    service = MockLLMService()

    # Missing explicit identity -> AppException
    with pytest.raises(
        AppException, match="STRICT FAIL-FAST: Mock service was called without an explicit 'agent_identity'"
    ):
        service.generate_content("hello")

    # Valid identity
    res = service.generate_content("hello", agent_identity="GuardAgent")
    assert "conclusion" in res  # It returns a JSON string containing conclusion
