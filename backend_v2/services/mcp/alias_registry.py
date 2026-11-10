"""Alias Registry Service for deterministic MCP tool namespace prefixing and parsing."""

from __future__ import annotations

import logging
import re
from typing import NoReturn

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.mcp import ParsedMCPToolAliasDTO

logger = logging.getLogger(__name__)

__all__ = ["AliasRegistry"]

_GATEWAY_SLUG_PATTERN: re.Pattern[str] = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


class AliasRegistry:
    """Provides deterministic bijective namespace construction and parsing for MCP tools."""

    @classmethod
    def build_namespaced_tool_alias(cls, gateway_slug: str, tool_id: str) -> str:
        """Construct a collision-free namespaced MCP tool alias ('{gateway_slug}__{tool_id}').

        Args:
            gateway_slug: Single-underscore lowercase alphanumeric slug of the parent MCP gateway.
            tool_id: Canonical technical identifier of the tool on the remote MCP server.

        Returns:
            Namespaced tool alias string ('{gateway_slug}__{tool_id}').

        Raises:
            AppException: If gateway_slug violates the single-underscore slug regex or tool_id is empty
                (ErrorCodes.VALIDATION_FAILED).
        """
        clean_slug = gateway_slug.strip()
        clean_tool_id = tool_id.strip()

        cls._validate_gateway_slug(clean_slug, raw_input=gateway_slug)

        if not clean_tool_id:
            cls._raise_validation_error("MCP tool_id must not be empty when building namespaced tool alias.")

        return f"{clean_slug}__{clean_tool_id}"

    @classmethod
    def parse_namespaced_tool_alias(cls, namespaced_alias: str) -> ParsedMCPToolAliasDTO:
        """Parse a namespaced MCP tool alias ('{gateway_slug}__{tool_id}') into its bijective components.

        Args:
            namespaced_alias: Full namespaced tool alias string.

        Returns:
            Validated ParsedMCPToolAliasDTO containing gateway_slug and tool_id.

        Raises:
            AppException: If namespaced_alias lacks the '__' delimiter, has an invalid gateway_slug,
                or has an empty tool_id (ErrorCodes.VALIDATION_FAILED).
        """
        clean_alias = namespaced_alias.strip()
        gateway_slug, separator, tool_id = clean_alias.partition("__")

        if not separator or not gateway_slug or not tool_id.strip():
            cls._raise_validation_error(
                f"Malformed namespaced MCP tool alias '{namespaced_alias}'. "
                "Expected format '{gateway_slug}__{tool_id}'."
            )

        cls._validate_gateway_slug(gateway_slug, raw_input=gateway_slug, raw_alias=namespaced_alias)

        return ParsedMCPToolAliasDTO(gateway_slug=gateway_slug, tool_id=tool_id.strip())

    @classmethod
    def _validate_gateway_slug(
        cls,
        clean_slug: str,
        *,
        raw_input: str,
        raw_alias: str | None = None,
    ) -> None:
        """Validate that clean_slug conforms to the single-underscore lowercase alphanumeric regex.

        Args:
            clean_slug: Trimmed candidate gateway slug.
            raw_input: Original gateway slug input for error diagnostics.
            raw_alias: Optional full namespaced alias string when parsing a combined alias.

        Raises:
            AppException: If clean_slug is empty or does not match _GATEWAY_SLUG_PATTERN
                (ErrorCodes.VALIDATION_FAILED).
        """
        if not clean_slug or not _GATEWAY_SLUG_PATTERN.fullmatch(clean_slug):
            if raw_alias is not None:
                msg = (
                    f"Invalid gateway_slug '{raw_input}' in namespaced alias '{raw_alias}'. "
                    "Must match '^[a-z0-9]+(?:_[a-z0-9]+)*$'."
                )
            else:
                msg = f"Invalid MCP gateway_slug '{raw_input}'. Must match '^[a-z0-9]+(?:_[a-z0-9]+)*$'."
            cls._raise_validation_error(msg)

    @staticmethod
    def _raise_validation_error(msg: str) -> NoReturn:
        """Log a structured RFC 7807 validation error and raise AppException.

        Args:
            msg: Deterministic validation failure message.

        Raises:
            AppException: Always raised with status_code 400 and ErrorCodes.VALIDATION_FAILED.
        """
        logger.error(
            "[AliasRegistry] %s: %s",
            ErrorCodes.VALIDATION_FAILED.name,
            msg,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            exc_info=True,
        )
        raise AppException(
            message=msg,
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
