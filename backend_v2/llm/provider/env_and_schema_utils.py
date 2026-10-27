"""Leaf static reflection, environment resolution, MCP schema normalization, and diagnostic dump utilities."""

import inspect
import logging
import os
import types
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel

from backend_v2.exceptions import ConfigurationError, ErrorCodes

__all__ = [
    "_INTERNAL_NON_API_KEYS",
    "_normalize_mcp_tool_schema_for_llm",
    "_safe_static_getattr",
    "_safe_static_hasattr",
    "_sync_diagnostic_dump",
    "resolve_env_variables",
]

logger = logging.getLogger(__name__)

_SENTINEL = object()

# Internal non-API keys stripped before dispatching requests to external LLM routers
_INTERNAL_NON_API_KEYS: frozenset[str] = frozenset({"mock_identity", "validation_context"})


def _safe_static_getattr(obj: Any, attr: str, default: Any = None) -> Any:
    """Safely extracts an attribute using static inspection without dynamic reflection.

    Args:
        obj: Target object or mapping to inspect.
        attr: Attribute or key name to resolve.
        default: Value returned when attribute or key is absent.

    Returns:
        Extracted attribute value or default.
    """
    if obj is None:
        return default
    try:
        val = inspect.getattr_static(obj, attr, _SENTINEL)
        if val is not _SENTINEL:
            if isinstance(val, property):
                return val.fget(obj) if val.fget is not None else default
            if isinstance(val, types.FunctionType):
                return val.__get__(obj, type(obj))
            return val
    except AttributeError, TypeError:
        pass
    try:
        if attr in obj:
            return obj[attr]
    except TypeError, KeyError:
        pass
    return default


def _safe_static_hasattr(obj: Any, attr: str) -> bool:
    """Safely checks if an attribute exists using static inspection without dynamic reflection.

    Args:
        obj: Target object or mapping to inspect.
        attr: Attribute or key name to check.

    Returns:
        True if the attribute or key exists on obj, False otherwise.
    """
    if obj is None:
        return False
    try:
        val = inspect.getattr_static(obj, attr, _SENTINEL)
        if val is not _SENTINEL:
            return True
    except AttributeError, TypeError:
        pass
    try:
        return attr in obj
    except TypeError, KeyError:
        return False


# Ensure env is loaded from project root for LLM secrets
_root_dir = Path(__file__).resolve().parent.parent.parent.parent
_env_path = _root_dir / ".env"
load_dotenv(dotenv_path=_env_path)


def resolve_env_variables(params: dict[str, Any]) -> dict[str, Any]:
    """Replace ${ENV_VAR} references with actual environment variable values.

    Args:
        params: Dictionary containing configuration parameters.

    Returns:
        New dictionary with resolved environment variables.

    Raises:
        ConfigurationError: If a required environment variable is not set (ErrorCodes.CONFIGURATION_ERROR).
    """
    resolved = {}
    for k, v in params.items():
        if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
            env_key = v[2:-1]
            resolved_value = os.getenv(env_key)
            if not resolved_value:
                msg = f"Strict Mode: Required environment variable '{env_key}' is missing for parameter '{k}'."
                logger.error(
                    msg,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )
                raise ConfigurationError(msg)
            resolved[k] = resolved_value
        else:
            resolved[k] = v
    return resolved


def _normalize_mcp_tool_schema_for_llm(node: Any) -> Any:
    """Recursively map internal DTO schema keys to standard JSON Schema keys for LLM providers.

    Transforms 'enum_values' to 'enum' and 'additional_properties' to 'additionalProperties'
    at the outbound LLM provider boundary while preserving internal DTO field names for REST parity.

    Args:
        node: Serialized tool declaration or nested JSON Schema structure.

    Returns:
        Normalized JSON Schema structure with standard 'enum' and 'additionalProperties' keys.
    """
    if isinstance(node, BaseModel):
        dumped = node.model_dump(mode="json", by_alias=True, exclude_none=True)
        return _normalize_mcp_tool_schema_for_llm(dumped)
    if type(node) is dict:
        return {
            ("enum" if k == "enum_values" else ("additionalProperties" if k == "additional_properties" else k)): (
                _normalize_mcp_tool_schema_for_llm(v)
            )
            for k, v in node.items()
        }
    if isinstance(node, list):
        return [_normalize_mcp_tool_schema_for_llm(item) for item in node]
    return node


def _sync_diagnostic_dump(dump_file: str, model_name: str, payload_str: str) -> None:
    """Synchronous file writing for diagnostic dumps to prevent blocking the async event loop.

    Args:
        dump_file: Absolute or relative path to the dump file.
        model_name: The name of the model being called.
        payload_str: The payload string to dump.

    Returns:
        None
    """
    try:
        with open(dump_file, "a", encoding="utf-8") as f:
            f.write(f"\n\n--- {model_name} ---\n")
            f.write(payload_str)
            f.write("\n")
    except OSError as e:
        logger.error("Failed to dump prompt: %s", e, exc_info=True)
