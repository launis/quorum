"""LLM Provider package facade re-exporting all public and internal provider symbols."""

import opentelemetry.trace as otel_trace

# Phase 4, Step 2: Explicit redundant re-exports for backend_v2.llm.provider package facade
from backend_v2.llm.adapters.base_adapter import (
    apply_provider_pacing as apply_provider_pacing,
)
from backend_v2.llm.mock import MockLLMService as MockLLMService
from backend_v2.llm.provider.base_and_mock_provider import (
    LLMProvider as LLMProvider,
)
from backend_v2.llm.provider.base_and_mock_provider import (
    LogfireShieldedClient as LogfireShieldedClient,
)
from backend_v2.llm.provider.base_and_mock_provider import (
    MockProvider as MockProvider,
)
from backend_v2.llm.provider.env_and_schema_utils import (
    _INTERNAL_NON_API_KEYS as _INTERNAL_NON_API_KEYS,
)
from backend_v2.llm.provider.env_and_schema_utils import (
    _normalize_mcp_tool_schema_for_llm as _normalize_mcp_tool_schema_for_llm,
)
from backend_v2.llm.provider.env_and_schema_utils import (
    _safe_static_getattr as _safe_static_getattr,
)
from backend_v2.llm.provider.env_and_schema_utils import (
    _safe_static_hasattr as _safe_static_hasattr,
)
from backend_v2.llm.provider.env_and_schema_utils import (
    _sync_diagnostic_dump as _sync_diagnostic_dump,
)
from backend_v2.llm.provider.env_and_schema_utils import (
    resolve_env_variables as resolve_env_variables,
)
from backend_v2.llm.provider.litellm_provider import (
    LiteLLMProvider as LiteLLMProvider,
)
from backend_v2.llm.provider.litellm_response_stage import (
    _truncate_for_debug as _truncate_for_debug,
)
from backend_v2.llm.provider.litellm_response_stage import (
    classify_and_raise_litellm_error as classify_and_raise_litellm_error,
)
from backend_v2.llm.provider.litellm_response_stage import (
    extract_litellm_content_and_usage as extract_litellm_content_and_usage,
)
from backend_v2.llm.provider.provider_factory import (
    LLMFactory as LLMFactory,
)
from backend_v2.llm.provider.transient_retry_policy import (
    _RETRY_AFTER_REGEX as _RETRY_AFTER_REGEX,
)
from backend_v2.llm.provider.transient_retry_policy import (
    _AdaptiveWaitWithRetryAfter as _AdaptiveWaitWithRetryAfter,
)
from backend_v2.llm.provider.transient_retry_policy import (
    _extract_retry_after_seconds as _extract_retry_after_seconds,
)
from backend_v2.llm.provider.transient_retry_policy import (
    _format_attempt_error as _format_attempt_error,
)
from backend_v2.llm.provider.transient_retry_policy import (
    _is_transient_llm_error as _is_transient_llm_error,
)
from backend_v2.settings import get_settings as get_settings

__all__ = [
    "LLMFactory",
    "LLMProvider",
    "LiteLLMProvider",
    "LogfireShieldedClient",
    "MockLLMService",
    "MockProvider",
    "_AdaptiveWaitWithRetryAfter",
    "_INTERNAL_NON_API_KEYS",
    "_RETRY_AFTER_REGEX",
    "_extract_retry_after_seconds",
    "_format_attempt_error",
    "_is_transient_llm_error",
    "_normalize_mcp_tool_schema_for_llm",
    "_safe_static_getattr",
    "_safe_static_hasattr",
    "_sync_diagnostic_dump",
    "_truncate_for_debug",
    "apply_provider_pacing",
    "classify_and_raise_litellm_error",
    "extract_litellm_content_and_usage",
    "get_settings",
    "otel_trace",
    "resolve_env_variables",
]
