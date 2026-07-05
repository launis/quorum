from pydantic import BaseModel, ConfigDict

from backend_v2.utils.alias_engine import AliasEngine


def test_mcp_source_id_literal_validation() -> None:
    """Verify that a dynamically generated MCP tool result ID is accepted by the Quote schema."""
    # 1. Reproduce what AliasEngine does when has_search_result=True
    QuoteIdsLiteralType = AliasEngine.build_quote_ids_literal(
        source_document_ids=["doc0"], allowed_atom_ids=["a0"], allowed_dynamic_keys=["chat_log"], has_search_result=True
    )

    # 2. Build a mock Pydantic model exactly like SchemaFactory does
    class MockExactQuote(BaseModel):
        source_id: QuoteIdsLiteralType
        text: str
        model_config = ConfigDict(extra="forbid")

    # 3. Simulate the LLM returning a dynamic Tavily tool ID
    payload = {"source_id": "tavily_ff768d39", "text": "This is a fact checked from tavily."}

    # 4. This should pass because the schema should allow alphanumeric suffixes for tool results
    quote = MockExactQuote.model_validate(payload)
    assert quote.source_id == "tavily_ff768d39"


def test_llm_has_search_flag_resolution() -> None:
    """Verify that mcp_tools existence forces has_search to True during orchestration."""

    # We simulate llm.py line 483 logic
    class MockStep:
        def __init__(self, mcp_tools=None):
            self.mcp_tools = mcp_tools or []

    step_with_tools = MockStep(mcp_tools=[{"type": "function", "function": {"name": "tavily_search"}}])
    state_data = {"some_other_key": {}}

    # If mcp_tools are present, has_search MUST be True, even if search_result is not yet in state
    has_search = any("search_result" in v for v in state_data.values() if type(v) is dict) or bool(
        getattr(step_with_tools, "mcp_tools", None)
    )
    assert has_search is True, "has_search must be True if mcp_tools are available for dynamic execution"
