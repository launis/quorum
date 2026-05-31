import pytest
from backend_v2.exceptions import AppException
from backend_v2.llm.adapters.adapter_factory import LLMCacheAdapterFactory
from backend_v2.llm.adapters.vertex_adapter import VertexCacheAdapter

def test_llm_adapter_factory_google_provider():
    """Verify that 'google' is correctly mapped to VertexCacheAdapter to prevent caching teardown crashes."""
    # This should return a VertexCacheAdapter without throwing an AppException
    adapter = LLMCacheAdapterFactory.get_adapter("google")
    assert isinstance(adapter, VertexCacheAdapter)
