"""Alias Registry Service for deterministic MCP tool namespace prefixing and parsing."""

from __future__ import annotations

import logging
import re

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.mcp import ParsedMCPToolAliasDTO

logger = logging.getLogger(__name__)

__all__ = ["AliasRegistry"]

_GATEWAY_SLUG_PATTERN: re.Pattern[str] = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


class AliasRegistry:
    """Provides deterministic bijective namespace construction and parsing for MCP tools."""

    @staticmethod
    def build_namespaced_tool_alias(gateway_slug: str, tool_id: str) -> str:
        """Construct a collision-free namespaced MCP tool alias ('{gateway_slug}__{tool_id}').

        # Phase 3, Step 3.2: Deterministic namespace prefixing for MCP tools

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

        if not clean_slug or not _GATEWAY_SLUG_PATTERN.fullmatch(clean_slug):
            msg = f"Invalid MCP gateway_slug '{gateway_slug}'. Must match '^[a-z0-9]+(?:_[a-z0-9]+)*$'."
            logger.error(
                "[AliasRegistry] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        if not clean_tool_id:
            msg = "MCP tool_id must not be empty when building namespaced tool alias."
            logger.error(
                "[AliasRegistry] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        return f"{clean_slug}__{clean_tool_id}"

    @staticmethod
    def parse_namespaced_tool_alias(namespaced_alias: str) -> ParsedMCPToolAliasDTO:
        """Parse a namespaced MCP tool alias ('{gateway_slug}__{tool_id}') into its bijective components.

        # Phase 3, Step 3.2: Deterministic namespace parsing on first '__' delimiter

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
            msg = (
                f"Malformed namespaced MCP tool alias '{namespaced_alias}'. "
                "Expected format '{gateway_slug}__{tool_id}'."
            )
            logger.error(
                "[AliasRegistry] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        if not _GATEWAY_SLUG_PATTERN.fullmatch(gateway_slug):
            msg = (
                f"Invalid gateway_slug '{gateway_slug}' in namespaced alias '{namespaced_alias}'. "
                "Must match '^[a-z0-9]+(?:_[a-z0-9]+)*$'."
            )
            logger.error(
                "[AliasRegistry] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        return ParsedMCPToolAliasDTO(gateway_slug=gateway_slug, tool_id=tool_id.strip())
