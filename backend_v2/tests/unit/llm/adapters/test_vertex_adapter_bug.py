import pytest
from backend_v2.llm.adapters.vertex_adapter import VertexCacheAdapter
from backend_v2.models.prompt import CompiledPrompt

@pytest.mark.asyncio
async def test_vertex_adapter_caching_import_bug():
    """
    Tier 4 RCA: Verify that VertexCacheAdapter crashes due to invalid 
    import of 'cached_contents' when attempting to use Vertex AI Context Caching.
    """
    adapter = VertexCacheAdapter()
    
    # Create a large prompt to trigger the caching logic (> 130000 chars)
    # The threshold is 130000, so 140000 will easily surpass it.
    large_text = "A" * 140000
    prompt = CompiledPrompt(
        static_messages=[{"role": "system", "content": large_text}],
        dynamic_messages=[]
    )
    
    # Act: This should crash BEFORE hitting the try/except block because
    # generative_models.cached_contents doesn't exist.
    # We expect an AttributeError or similar import error.
    messages, kwargs = await adapter.prepare_caching_payload(
        compiled_prompt=prompt,
        model_name="vertex_ai/gemini-2.5-pro"
    )
    
    print(f"KWARGS: {kwargs}")
    assert "cached_content" in kwargs, "Caching failed and it silently returned!"
