import os
import socket
import sys
from pathlib import Path
from typing import Any

import pytest


# Hotfix for Python 3.14 + pytest-cov import crash on BaseModel MRO matching and descriptor proxy reloads
def patch_pydantic_base_model_cache() -> None:
    def custom_import_cached_base_model() -> Any:
        frame: Any = sys._getframe(1)
        while frame:
            if "cls" in frame.f_locals:
                cls = frame.f_locals["cls"]
                if hasattr(cls, "__mro__"):
                    for base in cls.__mro__:
                        if base.__name__ == "BaseModel":
                            return base
            frame = frame.f_back
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
# Force FAST_DEV_MODE false globally for unit tests to ensure they test production limits
os.environ["FAST_DEV_MODE"] = "false"


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
