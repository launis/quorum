# Phase 6: Background Workers, Typed Cache Boundary & Storage

**Phase Title:** Phase 6: Background Workers, Typed Cache Boundary & Storage
**Objective:** Eliminate dict mutations in `worker.py` metadata handling, integrate generic `TypedCacheService` / Inbound Cache Hydration Firewall with auto-eviction on `ValidationError`, lock `ExecutionRecord.profile_syntheses` as `dict[str, RenderedSynthesisCache]` with `model_validate_json()` hydration, and modernize worker unit tests atomically.

**Source Reference:** @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L307-L318] (Phase 6: Background Workers, Typed Cache Boundary & Storage)

**Expected Target Files:**
- `[MODIFY]` @[backend_v2/worker.py]
- `[NEW]` @[backend_v2/services/cache/typed_cache.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker_synthesis_hydration.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 5. Verify service layer is strictly typed.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/worker.py] and cache drivers.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `backend_v2/services/cache/typed_cache.py` created with generic `get_cached[T: BaseModel]` providing Rust-level `model_validate_json()` hydration and `redis.delete()` on `ValidationError`.
    - [ ] `worker.py` refactored to eliminate dictionary mutations in execution metadata.
    - [ ] `ExecutionRecord.profile_syntheses` deserialized cleanly as `dict[str, RenderedSynthesisCache]`.
    - [ ] Worker unit tests in @[backend_v2/tests/unit/test_worker_synthesis_hydration.py] and @[backend_v2/tests/unit/test_worker.py] passing.
    - [ ] Quality gate passes: `uv run python scripts/backend_audit_loop.py backend_v2/worker.py --test`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_domain_model_prompt_separation.md]</knowledge_item>
    <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_app_error_boundary.md]</knowledge_item>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[backend_v2/worker.py]</backend>
    <backend>@[backend_v2/services/cache/typed_cache.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `scripts/_ast_guardrails.py` in Phase 6 (reserved for Phase 7).
    - Do NOT use standard `json.loads()` for cache and storage deserialization.
  </anti_targets>

  <step id="1" name="TYPED CACHE SERVICE & WORKER HYDRATION">
    <action>Create `TypedCacheService` helper and integrate with `worker.py`.</action>
    <action>Modernize worker unit tests in `backend_v2/tests/unit/`.</action>
  </step>

  <validation_gate>
    uv run python scripts/backend_audit_loop.py backend_v2/worker.py --test
    uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_worker.py --test
  </validation_gate>
</execution_protocol>
```
