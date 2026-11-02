"""Transactional Email Dispatch Service for B2B Invitations and Execution Assignments."""

from __future__ import annotations

import asyncio
import logging
from urllib.parse import urlsplit

import httpx
from pydantic import SecretStr

from backend_v2.exceptions import ConfigurationError, ErrorCodes
from backend_v2.models.auth import (
    TransactionalEmailBatchResultDTO,
    TransactionalEmailItemDTO,
)
from backend_v2.models.core_base import PrefixedUUID7
from backend_v2.models.enums import EmailDeliveryStatus, EmailTransportMode
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = ["EmailService"]


def _redact_action_url(action_url: SecretStr | str) -> str:
    """Strip sensitive query parameters from an action URL before logging.

    Args:
        action_url: SecretStr or string action URL potentially containing a query token.

    Returns:
        Redacted URL containing only scheme, netloc, and path.
    """
    raw = action_url.get_secret_value() if isinstance(action_url, SecretStr) else action_url
    parsed = urlsplit(raw)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    return parsed.path


class EmailService:
    """Service for dispatching transactional B2B invitation and execution assignment emails.

    Supports deterministic console logging (`EmailTransportMode.CONSOLE`) for local/test
    environments and bounded asynchronous HTTP API dispatch (`EmailTransportMode.HTTP_API`)
    for production environments.
    """

    def __init__(self) -> None:
        """Initialize the EmailService with an in-memory outbox for inspection in console mode."""
        self._console_outbox: list[TransactionalEmailItemDTO] = []

    @property
    def console_outbox(self) -> list[TransactionalEmailItemDTO]:
        """Return a shallow copy of emails dispatched in CONSOLE mode.

        Returns:
            List of TransactionalEmailItemDTO objects recorded during console transport.
        """
        return list(self._console_outbox)

    async def send_invitation_emails(
        self,
        items: list[TransactionalEmailItemDTO],
    ) -> TransactionalEmailBatchResultDTO:
        """Dispatch a batch of B2B organization invitation emails.

        Args:
            items: List of transactional email items to dispatch.

        Returns:
            Aggregated batch dispatch result with sent count, failed count, and delivery statuses.

        Raises:
            ConfigurationError: If HTTP_API mode is active and endpoint or API key is missing
                (ErrorCodes.CONFIGURATION_ERROR).
        """
        return await self._dispatch_batch(category="B2B_INVITATION", items=items)

    async def send_assignment_emails(
        self,
        items: list[TransactionalEmailItemDTO],
    ) -> TransactionalEmailBatchResultDTO:
        """Dispatch a batch of time-bound execution assignment magic-link emails.

        Args:
            items: List of transactional email items to dispatch.

        Returns:
            Aggregated batch dispatch result with sent count, failed count, and delivery statuses.

        Raises:
            ConfigurationError: If HTTP_API mode is active and endpoint or API key is missing
                (ErrorCodes.CONFIGURATION_ERROR).
        """
        return await self._dispatch_batch(category="EXECUTION_ASSIGNMENT", items=items)

    async def _dispatch_batch(
        self,
        *,
        category: str,
        items: list[TransactionalEmailItemDTO],
    ) -> TransactionalEmailBatchResultDTO:
        """Execute transport-mode routing for a batch of transactional email items.

        Args:
            category: Logical email category identifier for structured telemetry.
            items: Validated transactional email items to send.

        Returns:
            TransactionalEmailBatchResultDTO summarizing batch delivery status.

        Raises:
            ConfigurationError: If HTTP_API mode lacks required endpoint or key configuration
                (ErrorCodes.CONFIGURATION_ERROR).
        """
        if not items:
            return TransactionalEmailBatchResultDTO(
                sent_count=0,
                failed_count=0,
                delivery_statuses={},
            )

        settings = get_settings()
        if settings.email_transport_mode == EmailTransportMode.CONSOLE:
            statuses: dict[PrefixedUUID7, EmailDeliveryStatus] = {}
            for item in items:
                self._console_outbox.append(item)
                statuses[item.entity_id] = EmailDeliveryStatus.SENT
                logger.info(
                    "[EmailService] CONSOLE dispatch category=%s entity_id=%s to=%s subject=%s action_path=%s",
                    category,
                    item.entity_id,
                    item.recipient_email,
                    item.subject,
                    _redact_action_url(item.action_url),
                )
            return TransactionalEmailBatchResultDTO(
                sent_count=len(items),
                failed_count=0,
                delivery_statuses=statuses,
            )

        endpoint = settings.email_api_endpoint
        api_key_secret = settings.email_api_key
        if endpoint is None or not endpoint.strip() or api_key_secret is None:
            msg = "HTTP_API email transport mode requires both EMAIL_API_ENDPOINT and EMAIL_API_KEY."
            logger.error(
                "[EmailService] %s: %s",
                ErrorCodes.CONFIGURATION_ERROR.name,
                msg,
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                exc_info=True,
            )
            raise ConfigurationError(msg)

        raw_api_key = api_key_secret.get_secret_value().strip()
        if not raw_api_key:
            msg = "HTTP_API email transport mode requires a non-empty EMAIL_API_KEY."
            logger.error(
                "[EmailService] %s: %s",
                ErrorCodes.CONFIGURATION_ERROR.name,
                msg,
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                exc_info=True,
            )
            raise ConfigurationError(msg)

        return await self._dispatch_http_batch(
            category=category,
            endpoint=endpoint.strip(),
            api_key=raw_api_key,
            from_address=settings.email_from_address,
            timeout_seconds=settings.email_http_timeout_seconds,
            items=items,
        )

    async def _dispatch_http_batch(
        self,
        *,
        category: str,
        endpoint: str,
        api_key: str,
        from_address: str,
        timeout_seconds: float,
        items: list[TransactionalEmailItemDTO],
    ) -> TransactionalEmailBatchResultDTO:
        """Send each transactional email item over HTTP POST with bounded timeout isolation.

        Args:
            category: Logical email category identifier.
            endpoint: Configured HTTP POST endpoint URL.
            api_key: Bearer token for authenticating with the transactional email provider.
            from_address: Sender email address.
            timeout_seconds: Per-request and batch timeout in seconds.
            items: List of transactional email items to send.

        Returns:
            TransactionalEmailBatchResultDTO summarizing successful and failed deliveries.
        """
        sent_count = 0
        failed_count = 0
        statuses: dict[PrefixedUUID7, EmailDeliveryStatus] = {}
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            for item in items:
                item_result = await self._send_single_http_item(
                    client=client,
                    category=category,
                    endpoint=endpoint,
                    headers=headers,
                    from_address=from_address,
                    timeout_seconds=timeout_seconds,
                    item=item,
                )
                sent_count += item_result.sent_count
                failed_count += item_result.failed_count
                statuses.update(item_result.delivery_statuses)

        return TransactionalEmailBatchResultDTO(
            sent_count=sent_count,
            failed_count=failed_count,
            delivery_statuses=statuses,
        )

    async def _send_single_http_item(
        self,
        *,
        client: httpx.AsyncClient,
        category: str,
        endpoint: str,
        headers: dict[str, str],
        from_address: str,
        timeout_seconds: float,
        item: TransactionalEmailItemDTO,
    ) -> TransactionalEmailBatchResultDTO:
        """Send a single transactional email item and return a typed single-item batch result DTO.

        Args:
            client: Active httpx.AsyncClient session.
            category: Logical email category identifier.
            endpoint: Configured HTTP POST endpoint URL.
            headers: HTTP request headers with Bearer authorization.
            from_address: Sender email address.
            timeout_seconds: Request timeout in seconds.
            item: TransactionalEmailItemDTO to send.

        Returns:
            TransactionalEmailBatchResultDTO for the single item.
        """
        payload = {
            "category": category,
            "entity_id": item.entity_id,
            "from": from_address,
            "to": str(item.recipient_email),
            "recipient_name": item.recipient_name,
            "locale": item.locale.value,
            "subject": item.subject,
            "html_body": item.html_body,
            "action_url": item.action_url.get_secret_value(),
        }
        try:
            async with asyncio.timeout(timeout_seconds):
                response = await client.post(endpoint, json=payload, headers=headers)
            if response.status_code >= 400:
                logger.warning(
                    "[EmailService] HTTP dispatch failed category=%s entity_id=%s status=%d",
                    category,
                    item.entity_id,
                    response.status_code,
                )
                return TransactionalEmailBatchResultDTO(
                    sent_count=0,
                    failed_count=1,
                    delivery_statuses={item.entity_id: EmailDeliveryStatus.FAILED},
                )
            return TransactionalEmailBatchResultDTO(
                sent_count=1,
                failed_count=0,
                delivery_statuses={item.entity_id: EmailDeliveryStatus.SENT},
            )
        except (httpx.HTTPError, TimeoutError, OSError) as exc:
            logger.warning(
                "[EmailService] Transport exception category=%s entity_id=%s error=%s",
                category,
                item.entity_id,
                type(exc).__name__,
            )
            return TransactionalEmailBatchResultDTO(
                sent_count=0,
                failed_count=1,
                delivery_statuses={item.entity_id: EmailDeliveryStatus.FAILED},
            )
