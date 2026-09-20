# Phase 1: Architecture Baseline, AST Guardrail Definition & Pre-Implementation Technical Debt Cleanups

**Overview:** Establish the neuro-symbolic AST verification foundation (QGR018) for zero permissive typing, deep dictionary eradication, and lazy `.get()` eradication. Remediate foundational technical debt across settings, math utilities, logging, validation hooks, and persistence drivers to establish a strictly typed baseline before domain model hardening.
**Target Files:**
- `[NEW]` @[scripts/audit_dict_eradication.py]
- `[MODIFY]` @[scripts/_ast_guardrails.py]
- `[MODIFY]` @[scripts/run_e2e_variance_test.py]
- `[MODIFY]` @[backend_v2/hooks/validation.py]
- `[MODIFY]` @[backend_v2/settings.py]
- `[MODIFY]` @[backend_v2/utils/math_utils.py]
- `[MODIFY]` @[backend_v2/logging_config.py]
- `[MODIFY]` @[backend_v2/database/tinydb_driver.py]
- `[MODIFY]` @[backend_v2/database/firestore_driver.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the codebase baseline state and verify existing AST guardrails in @[scripts/_ast_guardrails.py].</action>
    <action>Look forward: Verify that subsequent phases (Phase 2 through 7) rely on the new QGR018 AST rules to prevent regression.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_152_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication/01_phase1_plan.md] @[docs/epic/EPIC_152_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>AST guardrail script [NEW] @[scripts/audit_dict_eradication.py] is created and passes across all target files.</item>
    <item>Rule QGR018 is registered in @[scripts/_ast_guardrails.py] with deterministic AST visitor scanning.</item>
    <item>All getattr, hasattr, and defensive .get() calls are eradicated from target files.</item>
    <item>All dictionary-based normalization in @[backend_v2/hooks/validation.py] is demolished.</item>
    <item>Settings and math utilities operate with 100% strongly typed interfaces.</item>
    <item>All unit and integration tests pass with zero regressions.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
    <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
    <knowledge_item>@[ki_cartesian_variance_and_authenticity.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_tda_best_of_three_flash.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_transient_error_resilience.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <forbidden>Do NOT modify domain execution models in @[backend_v2/models/domain/execution.py] during Phase 1 (reserved for Phase 2).</forbidden>
    <forbidden>Do NOT modify prompt compiler or DAG executor in @[backend_v2/services/orchestrator/prompt_compiler.py] during Phase 1 (reserved for Phase 5).</forbidden>
    <forbidden>Do NOT modify SDUI mappers or presentation models during Phase 1 (reserved for Phase 6).</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>[NEW] @[scripts/audit_dict_eradication.py]</backend>
    <backend>@[scripts/_ast_guardrails.py]</backend>
    <backend>@[scripts/run_e2e_variance_test.py]</backend>
    <backend>@[backend_v2/hooks/validation.py]</backend>
    <backend>@[backend_v2/settings.py]</backend>
    <backend>@[backend_v2/utils/math_utils.py]</backend>
    <backend>@[backend_v2/logging_config.py]</backend>
    <backend>@[backend_v2/database/tinydb_driver.py]</backend>
    <backend>@[backend_v2/database/firestore_driver.py]</backend>
  </touched_artifacts>

  <step id="1.1" name="AST Guardrail QGR018 Implementation">
    <action>Implement [NEW] @[scripts/audit_dict_eradication.py] and update @[scripts/_ast_guardrails.py] to register rule QGR018.</action>
    <action>Detect and flag forbidden patterns specifically and exhaustively: dict[str, Any] in state transit, raw dict subscripts on domain entities, getattr, hasattr, and defensive .get() calls with fallbacks.</action>
    <demolish>REMOVE: `hasattr` and `getattr` usage patterns across baseline scripts.</demolish>
    <constraint invariant="the_zero_compromise_pledge">Enforce Fail-Fast on any dynamic type inspection.</constraint>
  </step>

  <step id="1.2" name="Validation Hook Hardening">
    <action>Refactor @[backend_v2/hooks/validation.py] to eradicate getattr, hasattr, and _normalize_result_item.</action>
    <action>Replace legacy dictionary traversal with direct Pydantic V2 model attribute access and typed validation errors.</action>
    <demolish>REMOVE: `hasattr`, `getattr`, `_normalize_result_item` in @[backend_v2/hooks/validation.py]. REPLACE WITH: direct Pydantic model validation and explicit AppException error handling.</demolish>
  </step>

  <step id="1.3" name="Settings &amp; Math Utilities Strictness">
    <action>Refactor @[backend_v2/settings.py] and @[backend_v2/utils/math_utils.py] to eliminate loose dictionary unpacking.</action>
    <action>Ensure all configuration parameters and mathematical helper functions take strongly defined, typed arguments.</action>
  </step>

  <step id="1.4" name="Logging &amp; Database Driver Baseline Hardening">
    <action>Refactor @[backend_v2/logging_config.py] to utilize StructuredLogContextDTO for strongly typed structured log context data.</action>
    <action>Update @[backend_v2/database/tinydb_driver.py] and @[backend_v2/database/firestore_driver.py] to replace loose dictionary operations with typed serialization contracts.</action>
  </step>

  <step id="1.5" name="E2E Variance Test Harness Typed Payload Parity">
    <action>Update @[scripts/run_e2e_variance_test.py] to eliminate dictionary mock payloads and verify strongly typed DTO passing.</action>
    <action>Verify end-to-end variance execution harness against the modernized baseline.</action>
  </step>

  <test_contracts>
    <test name="test_audit_dict_eradication_flags_forbidden_patterns" category="positive">
      <input>Python source code containing raw dict[str, Any] and getattr calls.</input>
      <expected>Script outputs QGR018 violation finding with non-zero exit code.</expected>
    </test>
    <test name="test_validation_hook_rejects_malformed_dto" category="error_path">
      <input>Invalid evaluation item missing mandatory score attribute.</input>
      <expected>Raises AppException with VALIDATION_ERROR code, zero defensive fallbacks.</expected>
    </test>
    <test name="test_math_utils_strict_numeric_bounds" category="boundary">
      <input>Numeric inputs at boundary values (0.0, 1.0, 100.0).</input>
      <expected>Returns precise float calculation without dictionary wrappers.</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run AST guardrail audit: uv run python scripts/audit_dict_eradication.py</action>
    <action>Run backend audit on modified files: uv run python scripts/backend_audit_loop.py backend_v2/hooks/validation.py --test</action>
  </validation_gate>
</execution_protocol>
```
