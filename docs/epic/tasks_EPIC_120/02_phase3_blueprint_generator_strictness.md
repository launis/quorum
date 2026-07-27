# Phase 3: Blueprint Generator & Worker Strictness Hardening

This plan refactors the SDUI block consumers (Blueprint and Worker) to handle typed `AnySduiBlock` objects instead of raw dicts, eliminating duck-typing anti-patterns.

**Target Files**:
- `@[c:\src\quorum\backend_v2\services\blueprint.py]` [MODIFY]
- `@[c:\src\quorum\backend_v2\services\orchestrator\synthesis_distiller.py]` [MODIFY]
- `@[c:\src\quorum\backend_v2\worker.py]` [MODIFY]

```xml
<execution_protocol level="2_execute">
  <constraint invariant="the_zero_compromise_pledge">Eliminate all duck-typing (hasattr, isinstance dict, .get) in favor of typed Pydantic models.</constraint>
  <constraint invariant="frozen_state_mutability">In-place dictionary mutation is forbidden on Pydantic models; use model_copy or reinstantiation.</constraint>
  <step id="1" name="Blueprint Generator Refactor">
    <action>Modify `@[c:\src\quorum\backend_v2\services\blueprint.py]`.</action>
    <demolish>REMOVE: `isinstance(cb, dict)` checks in both `content_blocks` loop and `section_syntheses` PII masking loop.</demolish>
    <demolish>REMOVE: `.copy()` calls on dict elements, replace with `.model_copy()`.</demolish>
    <demolish>REMOVE: `hasattr(cache_b, "copy")`.</demolish>
    <demolish>REMOVE: `c_block.get("id")` raw dict access; redesign lookup logic since `SduiBlockBase` lacks an `id` field.</demolish>
    <demolish>REMOVE: Inline dict construction (e.g., `{"block_type": "markdown"...}`); replace with `MarkdownBlock(...)` instantiation.</demolish>
    <demolish>REMOVE: `c_block["text"] = safe_md` mutation; replace with `MarkdownBlock(text=safe_md)` reconstruction.</demolish>
  </step>
  <step id="2" name="Synthesis Distiller Refactor">
    <action>Modify `@[c:\src\quorum\backend_v2\services\orchestrator\synthesis_distiller.py]`.</action>
    <demolish>REMOVE: `json.dumps(best_cache.content_blocks, ensure_ascii=False)`.</demolish>
    <action>Replace with `json.dumps([b.model_dump(mode='json') for b in best_cache.content_blocks], ensure_ascii=False)`.</action>
  </step>
  <step id="3" name="Worker Double-Serialization Removal">
    <action>Modify `@[c:\src\quorum\backend_v2\worker.py]`.</action>
    <demolish>REMOVE: Explicit `.model_dump()` + `typing.cast(list[dict[str, Any]], ...)` pattern when storing `content_blocks` and `sec_dict` into `RenderedSynthesisCache`.</demolish>
    <action>Store the `AnySduiBlock` objects directly into the cache.</action>
    <action>Ensure `pydantic.ValidationError` is caught during LLM response parsing into `SynthesisSectionDTO` and repackaged into an `AppException` to trigger Schema Healing.</action>
  </step>
</execution_protocol>
```
## Testing & Quality Gate Plan
- Run backend audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`
- Run SDUI Parity Tests: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`
- Final Live E2E REST API Verification Gate: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
