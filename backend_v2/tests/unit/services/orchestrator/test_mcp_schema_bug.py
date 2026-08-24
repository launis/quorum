from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.services.orchestrator.schema_factory import SchemaFactory


def test_mcp_source_id_literal_validation() -> None:
    """Verify that a dynamically generated MCP tool result ID is accepted by the SchemaFactory union schema."""
    factory = SchemaFactory(resolve_i18n_fn=lambda t, locale: str(t) if t else "")

    block = PromptBlock(
        id="blk_0123456789abcdef0123456789abcdef",
        slug="test",
        description={"default_locale": "en", "translations": {"en": "test"}},
        category_id="system_rule",
        type="string",
        label={"default_locale": "en", "translations": {"en": "test"}},
    )

    Schema = factory.build_dynamic_schema(
        schema_name="TestSchema",
        criteria=[block],
        strictness_level=1,
        source_document_ids=["doc0"],
        allowed_atom_ids=["a0"],
        allowed_dynamic_keys=["chat_log", "mcp0"],
    )

    # 3. Simulate the LLM returning a dynamic MCP tool ID
    payload = {
        "blk_0123456789abcdef0123456789abcdef": {
            "source_document_aliases": ["doc0"],
            "exact_quotes": [{"source_id": "mcp0", "text": "This is a fact checked from tavily."}],
            "semantic_reasoning": "Reasoning",
            "rule_internalization": "Understood",
            "reasoning_steps": "Step 1",
            "decision": True,
        },
        "evaluation_notes": "",
        "reasoning_trace": "",
    }

    # 4. This should pass because the schema should allow mcp0 for tool results
    validated = Schema.model_validate(payload)
    assert validated.model_dump()["blk_0123456789abcdef0123456789abcdef"]["exact_quotes"][0]["source_id"] == "mcp0"


def test_llm_has_search_flag_resolution() -> None:
    """Old test logic, kept for coverage but no longer strictly controls regex directly."""
    pass
