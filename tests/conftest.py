import sys
import pytest
from unittest.mock import MagicMock
import os

# 1. FORCE ENV VARS BEFORE IMPORTS
os.environ["USE_MOCK_LLM"] = "true"
os.environ["USE_MOCK_DB"] = "true" # Ensure we default to safe mock DB
os.environ["STORAGE_BACKEND"] = "LOCAL"
os.environ["TESTING"] = "true"

# 2. PATCH ARQ TO PREVENT FAKEREDIS CRASH
# Fakeredis + Arq = Crash on startup because Arq tries to run 'INFO' command 
# inside a pipeline and parse it manually, which Fakeredis fails on.
try:
    import arq.connections
    
    async def _no_op_log(*args, **kwargs):
        pass

    arq.connections.log_redis_info = _no_op_log
    
    # Also patch the imported reference in worker.py!
    import arq.worker
    arq.worker.log_redis_info = _no_op_log
except ImportError:
    pass

@pytest.fixture(scope="session", autouse=True)
def global_setup():
    """
    Global setup for all tests.
    """
    pass
