import os
import socket
from typing import Any

import pytest

os.environ["DISABLE_LOGFIRE"] = "true"


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
