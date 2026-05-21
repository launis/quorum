import os
import socket
from pathlib import Path
from typing import Any

import pytest

# Removed global mock of backend_v2.llm.client to allow unit tests to run.

os.environ["DISABLE_LOGFIRE"] = "true"
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"


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
