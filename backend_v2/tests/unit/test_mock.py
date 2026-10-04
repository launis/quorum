import json

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.mock import MockLLMService
from backend_v2.models.domain import AnalystOutput
from backend_v2.settings import get_settings


def test_mock_llm_service_forbidden(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that MockLLMService crashes if use_mock_llm is False."""
    settings = get_settings()
    monkeypatch.setattr(settings, "use_mock_llm", False)
    with pytest.raises(RuntimeError, match="STRICT EXECUTION AUTHORITY"):
        MockLLMService()


def test_mock_llm_service_missing_identity_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Negative test: verify AppException is raised if agent_identity is omitted."""
    settings = get_settings()
    monkeypatch.setattr(settings, "use_mock_llm", True)

    service = MockLLMService()
    with pytest.raises(
        AppException, match="STRICT FAIL-FAST: Mock service was called without an explicit 'agent_identity'"
    ) as exc:
        service.generate_content("hello")

    assert exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_mock_llm_service_generate_content_explicit_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test generation of content with explicit mapped identity."""
    settings = get_settings()
    monkeypatch.setattr(settings, "use_mock_llm", True)

    service = MockLLMService()
    res = service.generate_content("hello", agent_identity="GuardAgent")
    assert "conclusion" in res


def test_mock_llm_service_generate_content_direct_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test generation of content with direct mock key fallback."""
    settings = get_settings()
    monkeypatch.setattr(settings, "use_mock_llm", True)

    service = MockLLMService()
    res = service.generate_content("hello", agent_identity="guard_agent")
    parsed = json.loads(res)
    assert "conclusion" in parsed or "is_safe" in parsed or len(parsed) > 0


def test_mock_llm_service_schema_type_registry_hit(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test mock response via direct Pydantic model type in MOCK_REGISTRY."""
    settings = get_settings()
    monkeypatch.setattr(settings, "use_mock_llm", True)

    service = MockLLMService()
    res = service.generate_content("prompt", response_schema=AnalystOutput)
    parsed = json.loads(res)
    assert "hypotheses" in parsed


def test_mock_llm_service_schema_dict_registry_hit(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test mock response via dict response_schema matching title in MOCK_REGISTRY."""
    settings = get_settings()
    monkeypatch.setattr(settings, "use_mock_llm", True)

    service = MockLLMService()
    res = service.generate_content("prompt", response_schema={"title": "AnalystOutput"})
    parsed = json.loads(res)
    assert "hypotheses" in parsed


def test_mock_llm_service_judge_agent_dynamic_hydration_strategy_a(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test dynamic Judge hydration using Strategy A regex from prompt."""
    settings = get_settings()
    monkeypatch.setattr(settings, "use_mock_llm", True)

    service = MockLLMService()
    prompt = "Please evaluate candidate on:\n- Logic Quality (ID: logic_score):\n- Ethics (ID: ethics_score):"
    res = service.generate_content(prompt, agent_identity="JudgeAgent")
    parsed = json.loads(res)
    assert "pisteet" in parsed
    assert "logic_score" in parsed["pisteet"]
    assert "ethics_score" in parsed["pisteet"]


def test_mock_llm_service_judge_agent_dynamic_hydration_strategy_b(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test dynamic Judge hydration using Strategy B regex from schema properties."""
    settings = get_settings()
    monkeypatch.setattr(settings, "use_mock_llm", True)

    service = MockLLMService()
    sys_instruction = 'Schema requirement: "scores": {"properties": {"strategy_b_dim": {"type": "object"}},'
    res = service.generate_content("evaluate", system_instruction=sys_instruction, agent_identity="JudgeAgent")
    parsed = json.loads(res)
    assert "pisteet" in parsed
    assert "strategy_b_dim" in parsed["pisteet"]


def test_mock_llm_service_judge_agent_hydration_failure_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Negative test: verify AppException is raised if dynamic Judge hydration encounters an error."""
    settings = get_settings()
    monkeypatch.setattr(settings, "use_mock_llm", True)

    service = MockLLMService()
    monkeypatch.setattr(
        "backend_v2.llm.mock.re.findall", lambda *a, **kw: (_ for _ in ()).throw(ValueError("Hydration test failure"))
    )

    with pytest.raises(AppException, match="Mock Hydration Failed") as exc:
        service.generate_content("text (ID: dim1)", agent_identity="JudgeAgent")

    assert exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_mock_llm_service_json_serial_handling(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test custom JSON serialization for datetime and unsupported types."""
    import datetime

    settings = get_settings()
    monkeypatch.setattr(settings, "use_mock_llm", True)

    service = MockLLMService()

    # Test serialization of datetime object in fallback data
    now = datetime.datetime.now(datetime.timezone.utc)
    monkeypatch.setattr("backend_v2.llm.mock.get_fallback_data", lambda key: {"timestamp": now, "date": now.date()})
    res = service.generate_content("hello", agent_identity="guard_agent")
    parsed = json.loads(res)
    assert "timestamp" in parsed

    # Test unsupported type raises TypeError
    class UnserializableObject:
        pass

    monkeypatch.setattr("backend_v2.llm.mock.get_fallback_data", lambda key: {"bad": UnserializableObject()})
    with pytest.raises(TypeError, match="not serializable"):
        service.generate_content("hello", agent_identity="guard_agent")
