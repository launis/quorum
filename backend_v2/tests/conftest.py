from __future__ import annotations

import json
import os
import socket
import sys
from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import pytest

if TYPE_CHECKING:
    from backend_v2.models.domain.mcp import OpenAIToolCallDTO
    from backend_v2.models.llm import LLMMessageDTO


# Hotfix for Python 3.14 + pytest-cov import crash on BaseModel MRO matching and descriptor proxy reloads
def patch_pydantic_base_model_cache() -> None:
    # Ensure pydantic.root_model is registered in sys.modules for Python 3.14 + coverage support
    try:
        import pydantic.root_model

        sys.modules["pydantic.root_model"] = pydantic.root_model
    except Exception:
        pass

    def custom_import_cached_base_model() -> Any:
        from pydantic import BaseModel

        return BaseModel

    import pydantic._internal._import_utils as import_utils

    import_utils.import_cached_base_model = custom_import_cached_base_model  # type: ignore[assignment]

    import pydantic._internal._model_construction as model_construction

    model_construction.import_cached_base_model = custom_import_cached_base_model  # type: ignore[attr-defined, assignment]

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

    model_construction.default_ignored_types = custom_default_ignored_types  # type: ignore[assignment]

    from pydantic._internal._generate_schema import GenerateSchema
    from pydantic_core import core_schema

    orig_unknown = GenerateSchema._unknown_type_schema

    def custom_unknown(self: Any, obj: Any) -> Any:
        if "litellm" in str(obj) or "CacheCreationTokenDetails" in str(obj):
            return core_schema.is_instance_schema(obj)
        return orig_unknown(self, obj)

    GenerateSchema._unknown_type_schema = custom_unknown  # type: ignore[method-assign]


patch_pydantic_base_model_cache()

# Removed global mock of backend_v2.llm.client to allow unit tests to run.

os.environ["DISABLE_LOGFIRE"] = "true"
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
# Force DEV_EXECUTION_MODE to full globally for unit tests to ensure they test production limits
os.environ["DEV_EXECUTION_MODE"] = "full"


@pytest.fixture(autouse=True, scope="session")
def setup_test_environment() -> None:
    """Creates necessary directories for testing."""
    # Create data/files directory to satisfy LocalFileDriver strict validation
    files_dir = Path(__file__).parent.parent.parent / "data" / "files"
    files_dir.mkdir(parents=True, exist_ok=True)


@pytest.fixture(autouse=True)
def block_live_network_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    """KRIITTINEN ILMARAKO: Estää verkkokutsut yksikkötesteissä, paitsi localhostiin E2E-testejä varten."""
    original_getaddrinfo = socket.getaddrinfo

    def guarded_getaddrinfo(*args: Any, **kwargs: Any) -> Any:
        host = args[0]
        if host in ("127.0.0.1", "localhost", "::1"):
            return original_getaddrinfo(*args, **kwargs)
        raise RuntimeError(
            f"🛑 FATAL TEST FAILURE: Yritit tehdä oikean verkkokutsun ({host}) testin aikana! Käytä mock_data.py."
        )

    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)


@pytest.fixture(scope="session")
def seed_data() -> dict[str, Any]:
    """Loads the authentic SSOT seed_data.json into memory once for all tests."""
    seed_path = Path(__file__).parent.parent / "seed" / "seed_data.json"
    with open(seed_path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(autouse=True)
def clear_litellm_provider_caches() -> Generator[None]:
    """KRIITTINEN ILMARAKO: Ensures LiteLLMProvider caches and semaphores are wiped before and after each test to prevent cross-test asyncio loop deadlocks."""
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
