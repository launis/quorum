import pytest
import socket

@pytest.fixture(autouse=True)
def block_live_network_calls(monkeypatch):
    """KRIITTINEN ILMARAKO: Estää verkkokutsut yksikkötesteissä."""
    def guarded_getaddrinfo(*args, **kwargs):
        raise RuntimeError("🛑 FATAL TEST FAILURE: Yritit tehdä oikean verkkokutsun testin aikana! Käytä mock_data.py.")
    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)
