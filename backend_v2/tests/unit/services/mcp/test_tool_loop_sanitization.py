"""Tests for MCP Tool Loop message sanitization and query relevance validation.

Bug 1: Orphaned `role: tool` messages without a preceding `role: assistant` + `tool_calls`
pair crash LiteLLM's Vertex AI transformation (`_gemini_convert_messages_with_history`).

Bug 2: LLM hallucinates irrelevant tool calls (e.g., "EUR to USD exchange rate") that waste
Tavily API calls and inject noise into the evaluation context.
"""


# ---------------------------------------------------------------------------
# BUG 1: Orphaned tool message sanitization
# ---------------------------------------------------------------------------


class TestOrphanedToolMessageSanitization:
    """Verify that `provider.py` strips orphaned `role: tool` messages before
    sending to LiteLLM, preventing the Vertex AI transformation crash.

    The function under test is `sanitize_messages_for_vertex` which must be
    added to `provider.py`.
    """

    def test_orphaned_tool_message_is_removed(self) -> None:
        """An orphaned `role: tool` without a preceding `role: assistant` + tool_calls
        must be stripped from the message array to prevent LiteLLM crash.
        """
        from backend_v2.llm.provider import sanitize_messages_for_vertex

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Evaluate this document."},
            # Orphaned tool response — no preceding assistant with tool_calls
            {
                "role": "tool",
                "tool_call_id": "call_abc123",
                "content": "<tool_response><query>EUR to USD</query></tool_response>",
            },
        ]

        sanitized = sanitize_messages_for_vertex(messages)

        # The orphaned tool message must be removed
        roles = [m["role"] for m in sanitized]
        assert "tool" not in roles, (
            "Orphaned tool message was not removed. This will crash LiteLLM Vertex transformation."
        )

    def test_valid_tool_pair_is_preserved(self) -> None:
        """A properly paired `assistant(tool_calls)` + `tool` sequence must be kept intact."""
        from backend_v2.llm.provider import sanitize_messages_for_vertex

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Evaluate this document."},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_abc123",
                        "type": "function",
                        "function": {"name": "mcp_tavily_search", "arguments": '{"query": "test"}'},
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call_abc123",
                "content": "<tool_response><query>test query</query></tool_response>",
            },
        ]

        sanitized = sanitize_messages_for_vertex(messages)

        # Both messages must be preserved
        assert len(sanitized) == 4
        assert sanitized[2]["role"] == "assistant"
        assert sanitized[3]["role"] == "tool"

    def test_multiple_orphaned_and_valid_pairs(self) -> None:
        """Mixed scenario: valid pairs are kept, orphans are removed."""
        from backend_v2.llm.provider import sanitize_messages_for_vertex

        messages = [
            {"role": "system", "content": "System prompt."},
            {"role": "user", "content": "User message."},
            # Valid pair
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_valid",
                        "type": "function",
                        "function": {"name": "mcp_tavily_search", "arguments": '{"query": "valid"}'},
                    }
                ],
            },
            {"role": "tool", "tool_call_id": "call_valid", "content": "valid response"},
            # Orphaned tool (no preceding assistant with tool_calls)
            {"role": "tool", "tool_call_id": "call_orphan", "content": "orphan response"},
            # Another user message
            {"role": "user", "content": "Continue."},
        ]

        sanitized = sanitize_messages_for_vertex(messages)

        tool_messages = [m for m in sanitized if m["role"] == "tool"]
        assert len(tool_messages) == 1, f"Expected 1 valid tool message, got {len(tool_messages)}"
        assert tool_messages[0]["tool_call_id"] == "call_valid"


# ---------------------------------------------------------------------------
# BUG 2: Hallucinated / irrelevant search query validation
# ---------------------------------------------------------------------------


class TestSearchQueryRelevanceValidation:
    """Verify that `mcp_tool_loop.py` rejects search queries that are clearly
    irrelevant to the source document being evaluated.
    """

    def test_irrelevant_query_is_rejected(self) -> None:
        """A query about 'EUR to USD exchange rate' should be rejected when
        the document is about hybrid work policy.
        """
        from backend_v2.services.mcp.mcp_tool_loop import validate_query_relevance

        source_context = (
            "MUISTIO: ETÄ- JA HYBRIDITYÖPOLITIIKAN UUDISTAMINEN. "
            "Vastaanottaja: Johtoryhmä. "
            "Ehdotus perustuu Työterveyslaitoksen ja Stanfordin yliopiston tuoreimpaan tutkimustietoon."
        )

        irrelevant_query = "current exchange rate EUR to USD"

        is_relevant = validate_query_relevance(irrelevant_query, source_context)
        assert is_relevant is False, (
            "Irrelevant query 'EUR to USD' was accepted. "
            "The LLM is hallucinating tool calls unrelated to the evaluation."
        )

    def test_relevant_query_is_accepted(self) -> None:
        """A query about 'Stanford hybrid work research' should be accepted
        when the document references Stanford.
        """
        from backend_v2.services.mcp.mcp_tool_loop import validate_query_relevance

        source_context = (
            "MUISTIO: ETÄ- JA HYBRIDITYÖPOLITIIKAN UUDISTAMINEN. "
            "Ehdotus perustuu Työterveyslaitoksen ja Stanfordin yliopiston tuoreimpaan tutkimustietoon."
        )

        relevant_query = "Stanford University hybrid work research 2024"

        is_relevant = validate_query_relevance(relevant_query, source_context)
        assert is_relevant is True, "Relevant query about Stanford was rejected. False positive in relevance filtering."

    def test_empty_context_accepts_all(self) -> None:
        """When source context is unavailable, all queries should be accepted
        (fail-open to prevent blocking legitimate searches).
        """
        from backend_v2.services.mcp.mcp_tool_loop import validate_query_relevance

        is_relevant = validate_query_relevance("any query", "")
        assert is_relevant is True


# ---------------------------------------------------------------------------
# L3: Source Sufficiency Gate — root cause fix
# ---------------------------------------------------------------------------


class TestSourceSufficiencyGate:
    """Verify that `execute_tool_loop` bypasses Phase 1 tool calling entirely
    when the source document is already fully available in the prompt.

    This is the L3 root cause fix: the LLM should never get the OPTION
    to call tools when there is no information gap to fill.
    """

    def test_sufficient_source_suppresses_tools(self) -> None:
        """When source_context exceeds the sufficiency threshold, the function
        should report that tools were suppressed via is_source_sufficient().
        """
        from backend_v2.services.mcp.mcp_tool_loop import is_source_sufficient

        long_document = "A" * 500  # Well above any reasonable threshold
        assert is_source_sufficient(long_document) is True

    def test_empty_source_allows_tools(self) -> None:
        """When source_context is empty, tools should be allowed
        (genuine information gap exists).
        """
        from backend_v2.services.mcp.mcp_tool_loop import is_source_sufficient

        assert is_source_sufficient("") is False

    def test_short_source_allows_tools(self) -> None:
        """When source_context is very short (e.g., a URL or title only),
        tools should be allowed since there's not enough to evaluate.
        """
        from backend_v2.services.mcp.mcp_tool_loop import is_source_sufficient

        assert is_source_sufficient("Check this link") is False
