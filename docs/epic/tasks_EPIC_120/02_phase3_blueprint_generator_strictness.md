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
    <demolish>REMOVE: `getattr(c_block, "id", None)` access; replace with strict `c_block.id` access since `SduiBlockBase` now correctly has an `id` field.</demolish>
    <demolish>REMOVE: `c_block.text = safe_md` in-place mutation; replace with `c_block.model_copy(update={"text": safe_md})` to respect frozen Pydantic models.</demolish>
  </step>
  <step id="2" name="Synthesis Distiller Refactor">
    <action>Modify `@[c:\src\quorum\backend_v2\services\orchestrator\synthesis_distiller.py]`.</action>
    <demolish>REMOVE: `json.dumps(best_cache.content_blocks, ensure_ascii=False)`.</demolish>
    <action>Replace with `json.dumps([b.model_dump(mode='json') for b in best_cache.content_blocks], ensure_ascii=False)`.</action>
  </step>
  <step id="3" name="Worker Double-Serialization Removal">
    <action>Modify `@[c:\src\quorum\backend_v2\worker.py]`.</action>
    <action>Catch `pydantic.ValidationError` (and `ExceptionGroup` containing it) inside the `generate_profile_synthesis_and_pdf_task` exception handler. Repackage it into an `AppException` with `ErrorCodes.VALIDATION_FAILED` to enforce the Fail-Fast mandate.</action>
  </step>
</execution_protocol>
```
## Testing & Quality Gate Plan
- Run backend audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`
- Run SDUI Parity Tests: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`
- Final Live E2E REST API Verification Gate: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
