"""Unit tests for EmailService transactional dispatch across CONSOLE and HTTP_API modes."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
from pydantic import SecretStr

from backend_v2.exceptions import ConfigurationError, ErrorCodes
from backend_v2.models.auth import TransactionalEmailItemDTO
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.enums import EmailDeliveryStatus, EmailTransportMode, EntityPrefix, SystemLocale
from backend_v2.services.auth.email_service import EmailService, _redact_action_url
from backend_v2.settings import Settings, get_settings


class _StubAsyncClient:
    """Deterministic stub for httpx.AsyncClient used to verify HTTP_API batch behavior."""

    def __init__(self, status_codes_by_email: dict[str, int], raise_for_emails: set[str] | None = None) -> None:
        """Initialize stub client with per-recipient status codes and error triggers."""
        self.status_codes_by_email = status_codes_by_email
        self.raise_for_emails = raise_for_emails or set()
        self.captured_requests: list[tuple[str, Any, dict[str, str]]] = []

    async def __aenter__(self) -> _StubAsyncClient:
        """Enter async context."""
        return self

    async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Exit async context."""
        _ = (exc_type, exc_val, exc_tb)

    async def post(self, url: str, *, json: Any, headers: dict[str, str]) -> httpx.Response:
        """Record POST request and return stubbed httpx.Response or raise transport error."""
        self.captured_requests.append((url, json, headers))
        recipient = str(json["to"])
        if recipient in self.raise_for_emails:
            raise httpx.ConnectError("Simulated transport timeout")
        code = self.status_codes_by_email[recipient] if recipient in self.status_codes_by_email else 200
        return httpx.Response(status_code=code)


@pytest.mark.asyncio
async def test_email_service_console_dispatch_positive(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify EmailService dispatches invitation and assignment emails in CONSOLE mode and redacts query tokens."""
    base_settings = get_settings()
    console_settings = base_settings.model_copy(update={"email_transport_mode": EmailTransportMode.CONSOLE})
    monkeypatch.setattr("backend_v2.services.auth.email_service.get_settings", lambda: console_settings)

    service = EmailService()
    inv_id_1 = generate_opaque_id(EntityPrefix.INVITATION)
    inv_id_2 = generate_opaque_id(EntityPrefix.INVITATION)
    action_url = f"{base_settings.frontend_app_base_url.rstrip('/')}/invite/accept?token=secret_token_value_12345"
    items = [
        TransactionalEmailItemDTO(
            entity_id=inv_id_1,
            recipient_email="alice@acme.example.com",
            locale=SystemLocale.EN,
            subject="Join Acme Corp",
            html_body="<p>Invite Alice</p>",
            action_url=SecretStr(action_url),
        ),
        TransactionalEmailItemDTO(
            entity_id=inv_id_2,
            recipient_email="bob@acme.example.com",
            locale=SystemLocale.EN,
            subject="Join Acme Corp",
            html_body="<p>Invite Bob</p>",
            action_url=SecretStr(action_url),
        ),
    ]

    inv_result = await service.send_invitation_emails(items)
    assert inv_result.sent_count == 2
    assert inv_result.failed_count == 0
    assert inv_result.delivery_statuses[inv_id_1] == EmailDeliveryStatus.SENT
    assert inv_result.delivery_statuses[inv_id_2] == EmailDeliveryStatus.SENT
    assert len(service.console_outbox) == 2

    assign_result = await service.send_assignment_emails([items[0]])
    assert assign_result.sent_count == 1
    assert assign_result.failed_count == 0
    assert len(service.console_outbox) == 3

    redacted = _redact_action_url(SecretStr(action_url))
    assert "secret_token_value_12345" not in redacted
    assert redacted.endswith("/invite/accept")


@pytest.mark.asyncio
async def test_email_service_empty_batch_boundary() -> None:
    """Verify EmailService returns zero counts immediately when given an empty batch."""
    service = EmailService()
    result = await service.send_invitation_emails([])
    assert result.sent_count == 0
    assert result.failed_count == 0
    assert result.delivery_statuses == {}
    assert _redact_action_url("/relative/path?token=abc") == "/relative/path"


@pytest.mark.asyncio
async def test_email_service_http_api_missing_config_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify EmailService raises ConfigurationError when HTTP_API mode lacks endpoint or API key."""
    base_settings: Settings = get_settings()
    invalid_settings = base_settings.model_copy(
        update={
            "email_transport_mode": EmailTransportMode.HTTP_API,
            "email_api_endpoint": None,
            "email_api_key": None,
        }
    )
    monkeypatch.setattr("backend_v2.services.auth.email_service.get_settings", lambda: invalid_settings)

    service = EmailService()
    item = TransactionalEmailItemDTO(
        entity_id=generate_opaque_id(EntityPrefix.INVITATION),
        recipient_email="alice@acme.example.com",
        locale=SystemLocale.EN,
        subject="Join Acme Corp",
        html_body="<p>Invite</p>",
        action_url=SecretStr(f"{base_settings.frontend_app_base_url.rstrip('/')}/invite/accept?token=tok_123456"),
    )

    with pytest.raises(ConfigurationError) as exc_info:
        await service.send_invitation_emails([item])
    assert exc_info.value.error_code == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_email_service_http_api_partial_failure_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify EmailService records FAILED delivery status on HTTP >= 400 or transport error without aborting batch."""
    base_settings: Settings = get_settings()
    http_settings = base_settings.model_copy(
        update={
            "email_transport_mode": EmailTransportMode.HTTP_API,
            "email_api_endpoint": "https://mail.quorum.example.com/v1/send",
            "email_api_key": SecretStr("test_api_key_placeholder_value"),
            "email_http_timeout_seconds": 5.0,
        }
    )
    monkeypatch.setattr("backend_v2.services.auth.email_service.get_settings", lambda: http_settings)

    stub_client = _StubAsyncClient(
        status_codes_by_email={
            "ok@acme.example.com": 202,
            "http500@acme.example.com": 503,
        },
        raise_for_emails={"timeout@acme.example.com"},
    )
    monkeypatch.setattr(
        "backend_v2.services.auth.email_service.httpx.AsyncClient",
        lambda timeout: stub_client,
    )

    base_url = base_settings.frontend_app_base_url.rstrip("/")
    id_ok = generate_opaque_id(EntityPrefix.ASSIGNMENT)
    id_500 = generate_opaque_id(EntityPrefix.ASSIGNMENT)
    id_timeout = generate_opaque_id(EntityPrefix.ASSIGNMENT)
    items = [
        TransactionalEmailItemDTO(
            entity_id=id_ok,
            recipient_email="ok@acme.example.com",
            locale=SystemLocale.EN,
            subject="Task 1",
            html_body="<p>Task 1</p>",
            action_url=SecretStr(f"{base_url}/task/tok_ok"),
        ),
        TransactionalEmailItemDTO(
            entity_id=id_500,
            recipient_email="http500@acme.example.com",
            locale=SystemLocale.EN,
            subject="Task 2",
            html_body="<p>Task 2</p>",
            action_url=SecretStr(f"{base_url}/task/tok_500"),
        ),
        TransactionalEmailItemDTO(
            entity_id=id_timeout,
            recipient_email="timeout@acme.example.com",
            locale=SystemLocale.EN,
            subject="Task 3",
            html_body="<p>Task 3</p>",
            action_url=SecretStr(f"{base_url}/task/tok_timeout"),
        ),
    ]

    service = EmailService()
    result = await service.send_assignment_emails(items)
    assert result.sent_count == 1
    assert result.failed_count == 2
    assert result.delivery_statuses[id_ok] == EmailDeliveryStatus.SENT
    assert result.delivery_statuses[id_500] == EmailDeliveryStatus.FAILED
    assert result.delivery_statuses[id_timeout] == EmailDeliveryStatus.FAILED
    assert len(stub_client.captured_requests) == 3
