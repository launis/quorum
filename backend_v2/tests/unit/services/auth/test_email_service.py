"""Unit tests for EmailService transactional dispatch across CONSOLE and HTTP_API modes."""

from __future__ import annotations

import logging
from typing import Annotated

import httpx
import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from backend_v2.exceptions import ConfigurationError, ErrorCodes
from backend_v2.models.auth import TransactionalEmailItemDTO
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.enums import EmailDeliveryStatus, EmailTransportMode, EntityPrefix, SystemLocale
from backend_v2.services.auth.email_service import EmailService, _redact_action_url
from backend_v2.settings import Settings, get_settings

__all__ = [
    "test_email_service_console_dispatch_positive",
    "test_email_service_empty_batch_boundary",
    "test_email_service_http_api_blank_api_key_negative",
    "test_email_service_http_api_blank_endpoint_negative",
    "test_email_service_http_api_missing_config_negative",
    "test_email_service_http_api_partial_failure_negative",
]


class _CapturedHttpRequest(BaseModel):
    """Immutable test capture record for outbound HTTP_API requests.

    Attributes:
        url: Target HTTP POST endpoint URL.
        recipient_to: Serialized recipient email address from JSON body.
        action_url: Unwrapped action URL transmitted in JSON body.
        authorization_header: Outbound Bearer authorization header value.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    url: Annotated[str, Field(description="Target HTTP POST endpoint URL")]
    recipient_to: Annotated[str, Field(description="Serialized recipient email address")]
    action_url: Annotated[str, Field(description="Transmitted action URL")]
    authorization_header: Annotated[str, Field(description="Authorization header value")]


class _TransactionalEmailItemFactory(ModelFactory[TransactionalEmailItemDTO]):
    """Hermetic Polyfactory builder for TransactionalEmailItemDTO instances."""

    __model__ = TransactionalEmailItemDTO
    __set_as_default_factory_for_type__ = False

    recipient_email: str = "alice@acme.example.com"
    recipient_name: str | None = "Alice Example"
    locale: SystemLocale = SystemLocale.EN
    subject: str = "Join Acme Corp"
    html_body: str = "<p>Transactional email body</p>"

    @classmethod
    def entity_id(cls) -> str:
        """Generate a canonical 32-hex UUIDv7 invitation identifier.

        Returns:
            Canonical Invitation Opaque Stripe ID.
        """
        return generate_opaque_id(EntityPrefix.INVITATION)

    @classmethod
    def action_url(cls) -> SecretStr:
        """Generate a SecretStr-wrapped invitation URL using centralized settings.

        Returns:
            SecretStr wrapping a frontend invitation accept URL.
        """
        base_url = get_settings().frontend_app_base_url.rstrip("/")
        return SecretStr(f"{base_url}/invite/accept?token=secret_token_value_12345")


class _StubAsyncClient:
    """Deterministic stub for httpx.AsyncClient verifying HTTP_API batch behavior."""

    def __init__(self, status_codes_by_email: dict[str, int], raise_for_emails: set[str] | None = None) -> None:
        """Initialize stub client with per-recipient status codes and error triggers.

        Args:
            status_codes_by_email: Mapping of recipient email to simulated HTTP status code.
            raise_for_emails: Optional set of recipient emails that trigger transport ConnectError.
        """
        self.status_codes_by_email = status_codes_by_email
        self.raise_for_emails = set() if raise_for_emails is None else raise_for_emails
        self.captured_requests: list[_CapturedHttpRequest] = []

    async def __aenter__(self) -> _StubAsyncClient:
        """Enter async context.

        Returns:
            Active _StubAsyncClient instance.
        """
        return self

    async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Exit async context.

        Args:
            exc_type: Exception class if raised, else None.
            exc_val: Exception instance if raised, else None.
            exc_tb: Traceback object if raised, else None.
        """
        _ = (exc_type, exc_val, exc_tb)

    async def post(self, url: str, *, json: dict[str, str | None], headers: dict[str, str]) -> httpx.Response:
        """Record POST request and return stubbed httpx.Response or raise transport error.

        Args:
            url: Target HTTP endpoint URL.
            json: Outbound JSON payload dictionary.
            headers: Outbound HTTP request headers.

        Returns:
            Simulated httpx.Response with configured status code.

        Raises:
            httpx.ConnectError: When recipient email belongs to raise_for_emails.
        """
        recipient = str(json["to"])
        self.captured_requests.append(
            _CapturedHttpRequest(
                url=url,
                recipient_to=recipient,
                action_url=str(json["action_url"]),
                authorization_header=headers["Authorization"],
            )
        )
        if recipient in self.raise_for_emails:
            raise httpx.ConnectError("Simulated transport timeout")
        code = self.status_codes_by_email[recipient] if recipient in self.status_codes_by_email else 200
        return httpx.Response(status_code=code)


@pytest.mark.asyncio
async def test_email_service_console_dispatch_positive(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify EmailService dispatches in CONSOLE mode and redacts both query and /task/<token> secrets."""
    base_settings = get_settings()
    console_settings = base_settings.model_copy(update={"email_transport_mode": EmailTransportMode.CONSOLE})
    monkeypatch.setattr("backend_v2.services.auth.email_service.get_settings", lambda: console_settings)

    service = EmailService()
    inv_id_1 = generate_opaque_id(EntityPrefix.INVITATION)
    inv_id_2 = generate_opaque_id(EntityPrefix.INVITATION)
    assign_id = generate_opaque_id(EntityPrefix.ASSIGNMENT)
    base_url = base_settings.frontend_app_base_url.rstrip("/")
    invite_url = f"{base_url}/invite/accept?token=secret_query_token_12345"
    assignment_url = f"{base_url}/task/secret_path_token_67890"

    inv_items = [
        _TransactionalEmailItemFactory.build(
            entity_id=inv_id_1,
            recipient_email="alice@acme.example.com",
            action_url=SecretStr(invite_url),
        ),
        _TransactionalEmailItemFactory.build(
            entity_id=inv_id_2,
            recipient_email="bob@acme.example.com",
            action_url=SecretStr(invite_url),
        ),
    ]
    assign_item = _TransactionalEmailItemFactory.build(
        entity_id=assign_id,
        recipient_email="candidate@acme.example.com",
        action_url=SecretStr(assignment_url),
    )

    with caplog.at_level(logging.INFO, logger="backend_v2.services.auth.email_service"):
        inv_result = await service.send_invitation_emails(inv_items)
        assign_result = await service.send_assignment_emails([assign_item])

    assert inv_result.sent_count == 2
    assert inv_result.failed_count == 0
    assert inv_result.delivery_statuses[inv_id_1] == EmailDeliveryStatus.SENT
    assert inv_result.delivery_statuses[inv_id_2] == EmailDeliveryStatus.SENT
    assert assign_result.sent_count == 1
    assert assign_result.failed_count == 0
    assert assign_result.delivery_statuses[assign_id] == EmailDeliveryStatus.SENT
    assert len(service.console_outbox) == 3

    redacted_invite = _redact_action_url(SecretStr(invite_url))
    assert "secret_query_token_12345" not in redacted_invite
    assert redacted_invite.endswith("/invite/accept")

    redacted_assignment = _redact_action_url(SecretStr(assignment_url))
    assert "secret_path_token_67890" not in redacted_assignment
    assert redacted_assignment.endswith("/task/[REDACTED_TOKEN]")
    assert "secret_query_token_12345" not in caplog.text
    assert "secret_path_token_67890" not in caplog.text


@pytest.mark.asyncio
async def test_email_service_empty_batch_boundary() -> None:
    """Verify EmailService returns zero counts immediately on an empty batch and redacts relative paths."""
    service = EmailService()
    result = await service.send_invitation_emails([])
    assert result.sent_count == 0
    assert result.failed_count == 0
    assert result.delivery_statuses == {}
    assert _redact_action_url("/relative/path?token=abc") == "/relative/path"
    assert _redact_action_url("/task/raw_relative_secret_token") == "/task/[REDACTED_TOKEN]"


@pytest.mark.asyncio
async def test_email_service_http_api_missing_config_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify EmailService raises ConfigurationError when HTTP_API mode lacks endpoint and API key."""
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
    item = _TransactionalEmailItemFactory.build()

    with pytest.raises(ConfigurationError) as exc_info:
        await service.send_invitation_emails([item])
    assert exc_info.value.error_code == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_email_service_http_api_blank_endpoint_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify EmailService raises ConfigurationError when HTTP_API mode has a whitespace-only endpoint."""
    base_settings: Settings = get_settings()
    invalid_settings = base_settings.model_copy(
        update={
            "email_transport_mode": EmailTransportMode.HTTP_API,
            "email_api_endpoint": "   ",
            "email_api_key": SecretStr("configured_non_empty_key"),
        }
    )
    monkeypatch.setattr("backend_v2.services.auth.email_service.get_settings", lambda: invalid_settings)

    service = EmailService()
    item = _TransactionalEmailItemFactory.build()

    with pytest.raises(ConfigurationError) as exc_info:
        await service.send_assignment_emails([item])
    assert exc_info.value.error_code == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_email_service_http_api_blank_api_key_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify EmailService raises ConfigurationError when HTTP_API mode has a whitespace-only API key."""
    base_settings: Settings = get_settings()
    invalid_settings = base_settings.model_copy(
        update={
            "email_transport_mode": EmailTransportMode.HTTP_API,
            "email_api_endpoint": "https://mail.quorum.example.com/v1/send",
            "email_api_key": SecretStr("   "),
        }
    )
    monkeypatch.setattr("backend_v2.services.auth.email_service.get_settings", lambda: invalid_settings)

    service = EmailService()
    item = _TransactionalEmailItemFactory.build()

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
            "http400@acme.example.com": 400,
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
    id_400 = generate_opaque_id(EntityPrefix.ASSIGNMENT)
    id_500 = generate_opaque_id(EntityPrefix.ASSIGNMENT)
    id_timeout = generate_opaque_id(EntityPrefix.ASSIGNMENT)
    items = [
        _TransactionalEmailItemFactory.build(
            entity_id=id_ok,
            recipient_email="ok@acme.example.com",
            action_url=SecretStr(f"{base_url}/task/tok_ok"),
        ),
        _TransactionalEmailItemFactory.build(
            entity_id=id_400,
            recipient_email="http400@acme.example.com",
            action_url=SecretStr(f"{base_url}/task/tok_400"),
        ),
        _TransactionalEmailItemFactory.build(
            entity_id=id_500,
            recipient_email="http500@acme.example.com",
            action_url=SecretStr(f"{base_url}/task/tok_500"),
        ),
        _TransactionalEmailItemFactory.build(
            entity_id=id_timeout,
            recipient_email="timeout@acme.example.com",
            action_url=SecretStr(f"{base_url}/task/tok_timeout"),
        ),
    ]

    service = EmailService()
    result = await service.send_assignment_emails(items)
    assert result.sent_count == 1
    assert result.failed_count == 3
    assert result.delivery_statuses[id_ok] == EmailDeliveryStatus.SENT
    assert result.delivery_statuses[id_400] == EmailDeliveryStatus.FAILED
    assert result.delivery_statuses[id_500] == EmailDeliveryStatus.FAILED
    assert result.delivery_statuses[id_timeout] == EmailDeliveryStatus.FAILED
    assert len(stub_client.captured_requests) == 4
    assert stub_client.captured_requests[0].action_url == f"{base_url}/task/tok_ok"
