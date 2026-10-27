"""Unit tests for LLMProvider base contract, LogfireShieldedClient, and MockProvider."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from pydantic import BaseModel, ConfigDict

import backend_v2.llm.provider.base_and_mock_provider as base_mock_mod
from backend_v2.exceptions import AppException, ConfigurationError
from backend_v2.llm.provider.base_and_mock_provider import (
    LLMProvider,
    LogfireShieldedClient,
    MockProvider,
)
from backend_v2.models.llm import LLMMessageDTO, LLMResponse
from backend_v2.settings import Settings


class _SampleStructuredOutput(BaseModel):
    """Strict Pydantic model for MockProvider structured output testing."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    status: str
    score: int


class _CapturedMockCallDTO(BaseModel):
    """Typed record of arguments received by _FakeMockLLMService.generate_content."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    prompt: str
    system_instruction: str | None
    agent_identity: str | None


class _ConcreteEchoProvider(LLMProvider):
    """Concrete test subclass exercising abstract LLMProvider contract."""

    async def generate(
        self,
        prompt: str | None = None,
        system_instruction: str | None = None,
        messages: Any = None,
        response_schema: Any = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        pass_reasoning_token: str | None = None,
        validation_context: Any = None,
        mock_identity: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Delegate to super then return a deterministic LLMResponse."""
        await super().generate(
            prompt=prompt,
            system_instruction=system_instruction,
            messages=messages,
            response_schema=response_schema,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return LLMResponse(content=prompt or "echo")


class _PlainTransportStub:
    """Minimal object without __aenter__ or __aexit__ for fallback context testing."""

    def __init__(self) -> None:
        """Initialize transport stub."""
        self.label = "plain-stub"


@pytest.mark.asyncio
async def test_logfire_shielded_client_delegates_async_context_and_attributes() -> None:
    """Verifies that LogfireShieldedClient wraps httpx.AsyncClient, delegates aenter/aexit, and shields transport attributes."""
    real_client = httpx.AsyncClient(timeout=5.0)
    shielded = LogfireShieldedClient(real_client)

    assert repr(shielded) == "<LogfireShieldedClient protecting httpx.AsyncClient>"
    assert shielded.timeout == real_client.timeout

    async with shielded as entered_client:
        assert entered_client is real_client
        assert not real_client.is_closed
    assert real_client.is_closed

    plain_stub = _PlainTransportStub()
    plain_shielded = LogfireShieldedClient(plain_stub)
    assert plain_shielded.label == "plain-stub"
    async with plain_shielded as fallback_entered:
        assert fallback_entered is plain_shielded

    concrete = _ConcreteEchoProvider()
    echo_res = await concrete.generate(prompt="contract-check", temperature=0.0, max_tokens=10)
    assert echo_res.content == "contract-check"


@pytest.mark.asyncio
async def test_mock_provider_consumes_mock_identity_directly(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies that MockProvider forwards mock_identity to MockLLMService and strips internal keys identically to pre-extraction behavior."""
    fast_settings = Settings(pacing_delay_mock_seconds=0, storage_backend="LOCAL")
    monkeypatch.setattr(base_mock_mod, "get_settings", lambda: fast_settings)

    provider = MockProvider(model_name="mock-model")
    captured_calls: list[_CapturedMockCallDTO] = []

    class _FakeMockLLMService:
        def generate_content(
            self,
            prompt: str,
            system_instruction: str | None = None,
            agent_identity: str | None = None,
            response_schema: Any = None,
        ) -> dict[str, str]:
            captured_calls.append(
                _CapturedMockCallDTO(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    agent_identity=agent_identity,
                )
            )
            return {"status": "ok", "identity": agent_identity or "none"}

    monkeypatch.setattr(base_mock_mod, "MockLLMService", _FakeMockLLMService)

    response = await provider.generate(
        prompt="Evaluate leadership matrix",
        system_instruction="Act as coach",
        temperature=0.0,
        max_tokens=100,
        mock_identity="ExecutiveSummaryTask",
    )

    assert len(captured_calls) == 1
    assert captured_calls[0].agent_identity == "ExecutiveSummaryTask"
    assert captured_calls[0].prompt == "Evaluate leadership matrix"
    assert captured_calls[0].system_instruction == "Act as coach"
    assert response.parsed_content == {"status": "ok", "identity": "ExecutiveSummaryTask"}
    assert response.messages is not None
    assert len(response.messages) == 2


@pytest.mark.asyncio
async def test_mock_provider_lifecycle_branches_and_negative_paths(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Verify MockProvider parameter validation, diagnostic dump, pacing, response formats, and usage tracking."""
    paced_settings = Settings(pacing_delay_mock_seconds=1, storage_backend="LOCAL")
    monkeypatch.setattr(base_mock_mod, "get_settings", lambda: paced_settings)

    sleep_mock = AsyncMock()
    monkeypatch.setattr("backend_v2.llm.provider.base_and_mock_provider.asyncio.sleep", sleep_mock)

    usage_service = MagicMock()
    usage_service.track_usage = AsyncMock()

    provider = MockProvider(
        model_name="mock-v2",
        usage_service=usage_service,
        organization_id="org_initial123",
    )
    assert provider.organization_id == "org_initial123"
    assert MockProvider().organization_id == "UNKNOWN_ORG"

    with pytest.raises(ConfigurationError):
        await provider.generate(prompt="missing temp", temperature=None, max_tokens=50)

    with pytest.raises(ConfigurationError):
        await provider.generate(prompt="missing max_tokens", temperature=0.0, max_tokens=None)

    dump_file = tmp_path / "mock_diag.log"
    monkeypatch.setenv("DUMP_PROMPTS_FILE", str(dump_file))

    with patch("backend_v2.llm.provider.MockLLMService") as patched_mock_cls:
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value = _SampleStructuredOutput(status="validated", score=5)
        patched_mock_cls.return_value = mock_instance

        res_pydantic = await provider.generate(
            prompt=None,
            system_instruction="Sys rule",
            messages=[LLMMessageDTO(role="user", content="Message payload")],
            response_schema=_SampleStructuredOutput,
            temperature=0.1,
            max_tokens=64,
            organization_id="org_override99",
            user_id="usr_override99",
        )

        assert res_pydantic.parsed_content == {"status": "validated", "score": 5}
        assert sleep_mock.await_count == 1
        usage_service.track_usage.assert_awaited_once_with(
            org_id="org_override99",
            user_id="usr_override99",
            model="mock-v2",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.002,
        )
        dumped_text = dump_file.read_text(encoding="utf-8")
        assert "MESSAGES:" in dumped_text
        assert "SYSTEM:\nSys rule" in dumped_text

        # String JSON response branch
        mock_instance.generate_content.return_value = '{"raw_str": true}'
        res_str = await provider.generate(prompt="Direct prompt", temperature=0.0, max_tokens=32)
        assert res_str.parsed_content == {"raw_str": True}

        # Invalid JSON string raises AppException
        mock_instance.generate_content.return_value = "{not-valid-json"
        with pytest.raises(AppException) as parse_exc:
            await provider.generate(prompt="Broken JSON", temperature=0.0, max_tokens=32)
        assert parse_exc.value.status_code == 500

        # Missing seed key raises ConfigurationError
        mock_instance.generate_content.return_value = {"message": "Mock data not found for key"}
        with pytest.raises(ConfigurationError) as seed_exc:
            await provider.generate(prompt="Unseeded prompt", temperature=0.0, max_tokens=32)
        assert "Mock data not found in Seed Vault" in str(seed_exc.value)

        # Usage service failure raises AppException
        mock_instance.generate_content.return_value = {"ok": 1}
        usage_service.track_usage = AsyncMock(side_effect=RuntimeError("Usage DB unreachable"))
        with pytest.raises(AppException) as usage_exc:
            await provider.generate(prompt="Usage failure", temperature=0.0, max_tokens=32)
        assert "Usage Tracking Failed" in str(usage_exc.value)

    # Diagnostic dump thread dispatch failure raises ConfigurationError
    async def _failing_to_thread(*args: Any, **kwargs: Any) -> None:
        raise OSError("disk full")

    monkeypatch.setattr("backend_v2.llm.provider.base_and_mock_provider.asyncio.to_thread", _failing_to_thread)
    with pytest.raises(ConfigurationError) as dump_exc:
        await provider.generate(prompt="Dump fail", temperature=0.0, max_tokens=32)
    assert "Diagnostic dump dispatch failed" in str(dump_exc.value)


# Phase 4, Step 1: Migrate MockProvider and LogfireShieldedClient tests from test_provider.py
@pytest.mark.asyncio
async def test_mock_provider_defaults_to_none_mock_identity() -> None:
    """Verify MockProvider defaults mock_identity to None cleanly."""
    provider = MockProvider(model_name="mock-model")

    with patch("backend_v2.llm.provider.MockLLMService") as mock_service_cls:
        mock_service_instance = MagicMock()
        mock_service_instance.generate_content.return_value = '{"status": "ok"}'
        mock_service_cls.return_value = mock_service_instance

        await provider.generate(
            prompt="Hello mock",
            temperature=0.0,
            max_tokens=100,
        )

        mock_service_instance.generate_content.assert_called_once()
        call_kwargs = mock_service_instance.generate_content.call_args[1]
        assert call_kwargs["agent_identity"] is None


@pytest.mark.asyncio
async def test_logfire_shielded_client() -> None:
    """Test LogfireShieldedClient proxy behavior."""
    mock_inner = AsyncMock()
    mock_inner.custom_attr = "hello"
    mock_inner.__aenter__.return_value = "entered"
    mock_inner.__aexit__.return_value = None

    proxy = LogfireShieldedClient(mock_inner)
    assert proxy.custom_attr == "hello"
    assert repr(proxy) == "<LogfireShieldedClient protecting httpx.AsyncClient>"

    async with proxy as p:
        assert p == "entered"

    plain_obj = MagicMock(spec=["test"])
    plain_proxy = LogfireShieldedClient(plain_obj)
    assert await plain_proxy.__aenter__() is plain_proxy
    assert await plain_proxy.__aexit__(None, None, None) is None


@pytest.mark.asyncio
async def test_mock_provider_full_lifecycle(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Verify MockProvider parameter checks, prompt dump, and usage tracking."""
    mock_settings = Settings(
        pacing_delay_mock_seconds=0,
        storage_backend="LOCAL",
    )
    monkeypatch.setattr("backend_v2.llm.provider.get_settings", lambda: mock_settings)

    usage_service = AsyncMock()
    mock_prov = MockProvider(
        model_name="mock-model",
        usage_service=usage_service,
        organization_id="org_test123",
    )

    with pytest.raises(ConfigurationError):
        await mock_prov.generate("hello", temperature=None, max_tokens=10)

    with pytest.raises(ConfigurationError):
        await mock_prov.generate("hello", temperature=0.0, max_tokens=None)

    dump_target = str(tmp_path / "mock_dump.txt")
    monkeypatch.setenv("DUMP_PROMPTS_FILE", dump_target)

    with patch("backend_v2.llm.provider.MockLLMService") as mock_service_cls:
        mock_inst = MagicMock()
        mock_inst.generate_content.return_value = {"answer": "mocked_json"}
        mock_service_cls.return_value = mock_inst

        resp = await mock_prov.generate(
            prompt="Test prompt",
            system_instruction="System rule",
            temperature=0.0,
            max_tokens=100,
            organization_id="org_kwarg",
            user_id="usr_kwarg",
        )

        assert resp.content == '{"answer": "mocked_json"}'
        usage_service.track_usage.assert_called_once()
        dump_content = (tmp_path / "mock_dump.txt").read_text(encoding="utf-8")
        assert "Test prompt" in dump_content

        resp_msg_only = await mock_prov.generate(
            prompt=None,
            messages=[LLMMessageDTO(role="user", content="msg only")],
            temperature=0.0,
            max_tokens=50,
        )
        assert resp_msg_only.content == '{"answer": "mocked_json"}'

        mock_inst.generate_content.return_value = {"message": "Mock data not found for key"}
        with pytest.raises(ConfigurationError):
            await mock_prov.generate("missing seed prompt", temperature=0.0, max_tokens=50)

        mock_inst.generate_content.return_value = _SampleStructuredOutput(status="pydantic-ok", score=1)
        resp_model = await mock_prov.generate("test model", temperature=0.0, max_tokens=50)
        assert "pydantic-ok" in resp_model.content

        mock_inst.generate_content.return_value = "invalid-json-{broken"
        with pytest.raises(AppException):
            await mock_prov.generate("broken string", temperature=0.0, max_tokens=50)

        mock_inst.generate_content.return_value = {"ok": True}
        usage_service.track_usage = AsyncMock(side_effect=RuntimeError("track fail"))
        with pytest.raises(AppException):
            await mock_prov.generate("track fail prompt", temperature=0.0, max_tokens=50)

