import pytest
from pydantic import ValidationError

from backend_v2.models.domain.guard import (
    GuardDTO,
    GuardInput,
    GuardOutput,
    SanitizationResult,
    SecurityCheck,
    TaintedDataContent,
)
from backend_v2.models.enums import RiskLevel, SimulationType


def test_guard_input_valid() -> None:
    gi = GuardInput(
        chat_log="hello",
        product_text="prod",
        reflection_text="refl",
        last_reasoning_trace="trace",
    )
    assert gi.chat_log == "hello"


def test_guard_input_empty_whitespace() -> None:
    with pytest.raises(ValidationError):
        GuardInput(chat_log="   ")


def test_guard_input_banned_phrases_pass() -> None:
    gi = GuardInput.model_validate({"chat_log": "safe text"}, context={"banned_phrases": ["banned"]})
    assert gi.chat_log == "safe text"


def test_guard_input_banned_phrases_fail() -> None:
    with pytest.raises(ValidationError) as exc:
        GuardInput.model_validate({"chat_log": "this is a banned text"}, context={"banned_phrases": ["banned"]})
    assert "banned" in str(exc.value).lower()


def test_tainted_data_content_valid() -> None:
    tdc = TaintedDataContent(
        chat_history="hist",
        product_text="prod",
        reflection_text="refl",
        safe_data="safe",
    )
    assert tdc.chat_history == "hist"


def test_tainted_data_content_empty_whitespace() -> None:
    with pytest.raises(ValidationError):
        TaintedDataContent(chat_history="  ", reflection_text="refl", safe_data="safe")


def test_security_check_valid() -> None:
    sc = SecurityCheck(
        threat_detected=False,
        risk_level=RiskLevel.LOW,
        risk_score=1.0,
        simulation_score=1.0,
        simulation_result=SimulationType.PASSIVE,
        anonymized=False,
        pii_findings=["name"],
    )
    assert sc.risk_score == 1.0


def test_security_check_extra_forbid() -> None:
    with pytest.raises(ValidationError):
        SecurityCheck.model_validate(
            {
                "threat_detected": False,
                "risk_level": "LOW",
                "risk_score": 1.0,
                "simulation_score": 1.0,
                "simulation_result": "passive",
                "anonymized": False,
                "pii_findings": [],
                "unknown_field": "not allowed",
            }
        )


def test_guard_dto_valid() -> None:
    sc = SecurityCheck(
        threat_detected=False,
        risk_level=RiskLevel.LOW,
        risk_score=1.0,
        simulation_score=1.0,
        simulation_result=SimulationType.PASSIVE,
        anonymized=False,
        pii_findings=[],
    )
    dto = GuardDTO(thought_process="thinking", conclusion="safe", confidence_score=0.9, security_check=sc)
    assert dto.security_check.threat_detected is False


def test_guard_output_valid() -> None:
    sc = SecurityCheck(
        threat_detected=False,
        risk_level=RiskLevel.LOW,
        risk_score=1.0,
        simulation_score=1.0,
        simulation_result=SimulationType.PASSIVE,
        anonymized=False,
        pii_findings=[],
    )
    tdc = TaintedDataContent(
        chat_history="hist",
        reflection_text="refl",
        safe_data="safe",
    )
    output = GuardOutput(
        thought_process="thinking", conclusion="safe", confidence_score=0.9, security_check=sc, tainted_data=tdc
    )
    assert output.tainted_data.chat_history == "hist"


def test_sanitization_result_valid() -> None:
    sr = SanitizationResult(
        sanitized_inputs={"key": "value"}, pii_threats_detected=["name"], banned_phrases_detected=["badword"]
    )
    assert sr.sanitized_inputs["key"] == "value"


def test_sanitization_result_extra_forbid() -> None:
    with pytest.raises(ValidationError):
        SanitizationResult.model_validate(
            {
                "sanitized_inputs": {"key": "value"},
                "pii_threats_detected": [],
                "banned_phrases_detected": [],
                "illegal": "no",
            }
        )
