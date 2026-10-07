from __future__ import annotations

import json
import os
import socket
import sys
from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import pytest
from pydantic import JsonValue

from backend_v2.models.dtos.flat_record import FlatExecutionRecordDTO as _FlatExecutionRecordDTO
from backend_v2.models.dtos.render import RenderExecutionResultDTO as _RenderExecutionResultDTO

_ = (_FlatExecutionRecordDTO, _RenderExecutionResultDTO)
from backend_v2.services.studio.prompt_block_service import StudioPromptBlockService
from backend_v2.services.studio.workflow_service import StudioWorkflowService
from backend_v2.settings import get_settings
from backend_v2.tests.fakes.in_memory_repositories import (
    InMemoryOutputProfileRepository,
    InMemoryPromptBlockRepository,
    InMemorySystemRepository,
    InMemoryWorkflowRepository,
)

if TYPE_CHECKING:
    from backend_v2.models.domain.mcp import OpenAIToolCallDTO
    from backend_v2.models.llm import LLMMessageDTO


# Hotfix for Python 3.14 + pytest-cov import crash on BaseModel MRO matching and descriptor proxy reloads
def patch_pydantic_base_model_cache() -> None:
    # Ensure pydantic.root_model is registered in sys.modules for Python 3.14 + coverage support
    try:
        import pydantic.root_model

        sys.modules["pydantic.root_model"] = pydantic.root_model
    except ImportError:
        pass

    def custom_import_cached_base_model() -> Any:
        from pydantic import BaseModel

        return BaseModel

    import pydantic._internal._import_utils as import_utils

    import_utils.import_cached_base_model = custom_import_cached_base_model

    import pydantic._internal._model_construction as model_construction

    model_construction.import_cached_base_model = custom_import_cached_base_model

    class NameMatcherMeta(type):
        def __instancecheck__(self, instance: Any) -> bool:
            name = instance.__class__.__name__
            return name in ("PydanticDescriptorProxy", "ComputedFieldInfo")

    class PydanticIgnoreMatcher(metaclass=NameMatcherMeta):
        pass

    orig_default_ignored_types = model_construction.default_ignored_types

    def custom_default_ignored_types() -> tuple[type[Any], ...]:
        orig = orig_default_ignored_types()
        return orig + (PydanticIgnoreMatcher,)

    model_construction.default_ignored_types = custom_default_ignored_types

    from pydantic._internal._generate_schema import GenerateSchema
    from pydantic_core import core_schema

    orig_unknown = GenerateSchema._unknown_type_schema

    def custom_unknown(self: Any, obj: Any) -> Any:
        if "litellm" in str(obj) or "CacheCreationTokenDetails" in str(obj):
            return core_schema.is_instance_schema(obj)
        return orig_unknown(self, obj)

    GenerateSchema._unknown_type_schema = custom_unknown


patch_pydantic_base_model_cache()

# Removed global mock of backend_v2.llm.client to allow unit tests to run.

os.environ["DISABLE_LOGFIRE"] = "true"
os.environ["LOGFIRE_TOKEN"] = ""
os.environ["OTEL_ENABLED"] = "false"
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
# Set environment to development so all automated tests run under the fast, deterministic profile
os.environ["ENVIRONMENT"] = "development"
os.environ["LOG_FILE_NAME"] = "tests_debug.log"

get_settings.cache_clear()


@pytest.fixture(autouse=True, scope="session")
def setup_test_environment() -> None:
    """Creates necessary directories for testing."""
    # Create data/files directory to satisfy LocalFileDriver strict validation
    files_dir = Path(__file__).parent.parent.parent / "data" / "files"
    files_dir.mkdir(parents=True, exist_ok=True)


@pytest.fixture(autouse=True)
def block_live_network_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    """Blocks live network calls in unit tests, except localhost for E2E tests."""
    original_getaddrinfo = socket.getaddrinfo

    def guarded_getaddrinfo(*args: Any, **kwargs: Any) -> Any:
        host = args[0]
        if host in ("127.0.0.1", "localhost", "::1"):
            return original_getaddrinfo(*args, **kwargs)
        raise RuntimeError(
            f"🛑 FATAL TEST FAILURE: Attempted a live network call ({host}) during testing! Use mock_data.py."
        )

    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)


@pytest.fixture(scope="session")
def seed_data() -> dict[str, JsonValue]:
    """Loads the authentic SSOT seed_data.json into memory once for all tests."""
    seed_path = Path(__file__).parent.parent / "seed" / "seed_data.json"
    with open(seed_path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(autouse=True)
def clear_litellm_provider_caches() -> Generator[None]:
    """Ensures LiteLLMProvider caches and semaphores are wiped before and after each test.

    This prevents cross-test asyncio loop deadlocks.
    """
    from backend_v2.llm.provider import LiteLLMProvider

    LiteLLMProvider._router_cache.clear()
    LiteLLMProvider._semaphores.clear()
    LiteLLMProvider._httpx_clients.clear()
    yield
    LiteLLMProvider._router_cache.clear()
    LiteLLMProvider._semaphores.clear()
    LiteLLMProvider._httpx_clients.clear()


def make_llm_message(
    role: Literal["system", "user", "assistant", "tool"],
    content: str,
    tool_calls: list[OpenAIToolCallDTO] | None = None,
    tool_call_id: str | None = None,
    name: str | None = None,
) -> LLMMessageDTO:
    """Helper to construct strictly validated LLMMessageDTO instances in tests."""
    from backend_v2.models.llm import LLMMessageDTO

    return LLMMessageDTO(
        role=role,
        content=content,
        tool_calls=tool_calls,
        tool_call_id=tool_call_id,
        name=name,
    )


@pytest.fixture
def fake_workflow_repo() -> InMemoryWorkflowRepository:
    """Provides a fresh, isolated in-memory workflow repository fake."""
    return InMemoryWorkflowRepository()


@pytest.fixture
def fake_prompt_block_repo() -> InMemoryPromptBlockRepository:
    """Provides a fresh, isolated in-memory prompt block repository fake."""
    return InMemoryPromptBlockRepository()


@pytest.fixture
def fake_output_profile_repo() -> InMemoryOutputProfileRepository:
    """Provides a fresh, isolated in-memory output profile repository fake."""
    return InMemoryOutputProfileRepository()


@pytest.fixture
def fake_system_repo() -> InMemorySystemRepository:
    """Provides a fresh, isolated in-memory system repository fake."""
    return InMemorySystemRepository()


@pytest.fixture
def studio_workflow_service(
    fake_workflow_repo: InMemoryWorkflowRepository,
    fake_output_profile_repo: InMemoryOutputProfileRepository,
    fake_prompt_block_repo: InMemoryPromptBlockRepository,
    fake_system_repo: InMemorySystemRepository,
) -> StudioWorkflowService:
    """Provides a StudioWorkflowService instance wired to typed in-memory repository fakes."""
    return StudioWorkflowService(
        workflow_repo=fake_workflow_repo,
        output_profile_repo=fake_output_profile_repo,
        prompt_block_repo=fake_prompt_block_repo,
        system_repo=fake_system_repo,
    )


@pytest.fixture
def studio_prompt_block_service(
    fake_prompt_block_repo: InMemoryPromptBlockRepository,
    fake_system_repo: InMemorySystemRepository,
) -> StudioPromptBlockService:
    """Provides a StudioPromptBlockService instance wired to typed in-memory repository fakes."""
    return StudioPromptBlockService(
        prompt_block_repo=fake_prompt_block_repo,
        system_repo=fake_system_repo,
    )


@pytest.fixture
def in_memory_spans() -> Generator[Any]:
    """Provides an isolated InMemorySpanExporter attached to a test TracerProvider."""
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    orig_provider = trace._TRACER_PROVIDER
    trace._TRACER_PROVIDER = provider
    try:
        yield exporter
    finally:
        exporter.clear()
        trace._TRACER_PROVIDER = orig_provider


def pytest_terminal_summary(terminalreporter: Any, exitstatus: int, config: Any) -> None:
    """Emits diagnostic banner pointing to local trace snapshot and Logfire MCP upon test failure."""
    if exitstatus != 0:
        terminalreporter.write_sep("=", "TELEMETRY DIAGNOSTIC GUIDANCE", bold=True, red=True)
        terminalreporter.write_line(
            "🔴 Tests failed. Inspect latest execution trace snapshot via view_file on:", bold=True
        )
        terminalreporter.write_line("   data/files/traces/latest_execution_trace.json", bold=True)
        terminalreporter.write_line("   Or query trace spans via Logfire MCP: query_spans or get_trace.", bold=True)
