import socket
from typing import Any

import pytest


@pytest.fixture(autouse=True)
def block_live_network_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    """KRIITTINEN ILMARAKO: Estää verkkokutsut yksikkötesteissä."""

    def guarded_getaddrinfo(*args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("🛑 FATAL TEST FAILURE: Yritit tehdä oikean verkkokutsun testin aikana! Käytä mock_data.py.")

    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)
