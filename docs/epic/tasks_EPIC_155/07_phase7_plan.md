# Phase 7: Knowledge Base & Architecture Synchronization

**Overview:** Synchronize the Quorum Knowledge Base (`ki_execution_engine_protocol.md`, `ki_python_314_concurrency_strictness.md`), update the system directory reference (`04_directory_reference.md`), execute the fully parameterized `/tier7-describe-architecture` command to update pillar architecture manifests (`03_cognitive_orchestration_engine.md`, `05_resilience_and_observability.md`), and update the `system_concurrency_ssot` rule block in `01-python-backend.md` and `05_llm_architecture.md` with explicit user approval.

**Source:** @[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md#L361-L372] Phase 7: Knowledge Base & Architecture Synchronization

**Target Files:**
- `[MODIFY]` @[ki_execution_engine_protocol.md]
- `[MODIFY]` @[ki_python_314_concurrency_strictness.md]
- `[MODIFY]` @[.agents/rules/04_directory_reference.md]
- `[MODIFY]` @[.agents/rules/01-python-backend.md]
- `[MODIFY]` @[.agents/rules/05_llm_architecture.md]
- `[MODIFY]` @[docs/architecture/03_cognitive_orchestration_engine.md]
- `[MODIFY]` @[docs/architecture/05_resilience_and_observability.md]

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[ki_execution_engine_protocol.md]` | Obsolete mandates: `atomic_telemetry_signaling_mandate`, `engine_concurrency_nullcontext_mandate`, and semaphore DTO clause in `engine_dto_strictness`. | Codify the Pure Compute Engine Law: execution engines and sub-executors are 100% pure computational pipelines with zero semaphore or event dependencies. | Pruned obsolete concurrency plumbing rules and dead context manager mandates. | Human and automated audit of KI content against physical codebase. |
| `@[ki_python_314_concurrency_strictness.md]` | Obsolete setting references claiming `max_concurrent_jobs` (non-existent) and claims that `max_concurrent_llm_steps` acts as micro LLM request limiter. | Accurately document the Two-Tier Concurrency Architecture: macro Arq worker concurrency (`max_concurrent_workflows`), micro provider dynamic throttling (`semaphore_*` in `LiteLLMProvider`), and synthesis fan-out (`max_concurrent_llm_steps`). | Pruned misleading settings claims and redundant concurrency wrappers. | Verification against `backend_v2/settings.py` and `backend_v2/llm/provider.py`. |
| `@[.agents/rules/04_directory_reference.md]` | Outdated directory, routing, or proxy references to eradicated modules. | Register modernized pure compute engines (`orchestrator/engines/`), strategies (`orchestrator/strategies/`), and pure DTO contracts (`models/dtos/engine.py`). | Timeless present-tense architecture mapping without dead shims. | `uv run python scripts/audit_markdown_boundaries.py --file .agents/rules/04_directory_reference.md`. |
| `@[.agents/rules/01-python-backend.md]`, `@[.agents/rules/05_llm_architecture.md]` | Obsolete claims that parallel LLM steps are constrained by `asyncio.Semaphore(SystemConcurrency.MAX_CONCURRENT_LLM_STEPS)` or `LLMClient` semaphore. | Synchronize `system_concurrency_ssot` rule block with physical SSOT: macro Arq limit (`max_concurrent_workflows`) and micro provider limit (`semaphore_*` settings), with user approval. | Eliminate inaccurate concurrency claims across primary AI directives. | Explicit user approval gate, audited by `backend_audit_loop.py`. |
| `@[docs/architecture/03_cognitive_orchestration_engine.md]`, `@[docs/architecture/05_resilience_and_observability.md]` | Historical development language ("Epic 155", "Phase 1-5 refactoring", changelogs) and outdated semaphore descriptions. | Update capability manifests in timeless present tense describing current Two-Tier Concurrency Architecture and Pure Compute Engine Model via `/tier7-describe-architecture`. | Zero meta-narratives or historical phase progression commentary in architecture documents. | `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/tasks_EPIC_155/07_phase7_plan.md`. |

## Pre-Implementation Cleanups

1. `[CLEANUP]` Ensure Phase 6 quality gates, concurrency fuzzer test suites (Stage A and Stage B), AST line boundary reconciliation, and live E2E verification have passed 100%.
2. `[CLEANUP]` Verify AST concurrency guardrails (`test_ast_concurrency_guardrails.py`) and concurrency compliance tests (`test_system_concurrency_compliance.py`) pass with 0 errors before synchronizing documentation.
3. `[CLEANUP]` Request explicit user approval before modifying `.agents/rules/01-python-backend.md` and `.agents/rules/05_llm_architecture.md`.

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 6. Verify all code changes and live tests have passed.</action>
    <action>Look forward: Verify that updating Knowledge Items, system rules, and architecture documentation locks in the Pure Compute Model for all future AI agents.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md]) and the Tracker document (@[docs/epic/EPIC_155_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_155/07_phase7_plan.md] @[docs/epic/EPIC_155_tracker.md]`.</directive>
  </step>

  <dod_checklist>
    <item>ki_execution_engine_protocol.md updated with Pure Compute Engine Law, replacing deprecated semaphore mandates.</item>
    <item>ki_python_314_concurrency_strictness.md updated with Two-Tier Concurrency Architecture SSOT.</item>
    <item>04_directory_reference.md registered with latest orchestrator and engine routing.</item>
    <item>Fully parameterized /tier7-describe-architecture command executed with tracker, epic, target KIs, and directives.</item>
    <item>docs/architecture/03_cognitive_orchestration_engine.md and docs/architecture/05_resilience_and_observability.md updated in timeless present tense.</item>
    <item>system_concurrency_ssot rule block in 01-python-backend.md and 05_llm_architecture.md updated with explicit user approval.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_decompose_verify.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT use historical stage names (Phase 1, Epic 155, etc.) in docs/architecture/ files (document current state in present tense only).</anti_target>
    <anti_target>Do NOT update .agents/rules without explicit user approval.</anti_target>
    <anti_target>Do NOT introduce new Python domain code or alter database seed files in Phase 7.</anti_target>
  </anti_targets>

  <touched_artifacts>
    <backend>@[.agents/rules/04_directory_reference.md]</backend>
    <backend>@[.agents/rules/01-python-backend.md]</backend>
    <backend>@[.agents/rules/05_llm_architecture.md]</backend>
  </touched_artifacts>

  <test_contracts>
    <test name="test_markdown_boundaries_directory_reference" category="boundary">
      <input>.agents/rules/04_directory_reference.md</input>
      <expected>audit_markdown_boundaries.py passes with 0 findings</expected>
    </test>
    <test name="test_markdown_boundaries_phase7_plan" category="boundary">
      <input>docs/epic/tasks_EPIC_155/07_phase7_plan.md</input>
      <expected>audit_markdown_boundaries.py passes with 0 findings</expected>
    </test>
    <test name="test_ast_concurrency_guardrails_pass" category="guardrail">
      <input>backend_v2/tests/unit/test_ast_concurrency_guardrails.py</input>
      <expected>All 6 AST guardrail tests pass with 0 errors</expected>
    </test>
    <test name="test_system_concurrency_compliance_pass" category="compliance">
      <input>backend_v2/tests/unit/models/test_system_concurrency_compliance.py</input>
      <expected>All 4 concurrency compliance tests pass with 0 errors</expected>
    </test>
  </test_contracts>

  <step id="7.1" name="UPDATE_KNOWLEDGE_ITEM_PROTOCOL">
    <action>In `@[ki_execution_engine_protocol.md]`, deprecate `atomic_telemetry_signaling_mandate`, `engine_concurrency_nullcontext_mandate`, and the semaphore clause of `engine_dto_strictness`. Replace with the new Pure Compute Engine Law: execution engines (`PromptEngine`, `SynthesisEngine`, `TDAEngine`) and sub-executors (`TwoPassAtomizer`, `EnrichedDagExecutor`, `SlidingWindowLinker`) are 100% computational pipelines with zero semaphore or event dependencies.</action>
    <action>In `@[ki_python_314_concurrency_strictness.md]`, update the `two_tier_semaphore_architecture` rule block to accurately describe the physical SSOT: macro-level workflow concurrency in Arq daemon (`settings.max_concurrent_workflows`), micro-level provider throttling in `LiteLLMProvider` dynamic semaphore pool (`semaphore_low_rpm_threshold`, `semaphore_low_rpm_limit`, `semaphore_max_concurrency`, `semaphore_rpm_divisor`), Phase 2 synthesis fan-out governed by `settings.max_concurrent_llm_steps`, and pure stateless computation in `ExecutionEngine` pipelines without semaphore or event primitives.</action>
  </step>

  <step id="7.2" name="SYNCHRONIZE_META_ARCHITECTURE_DOCUMENTATION">
    <action>In `@[.agents/rules/04_directory_reference.md]`, ensure the orchestrator engines (`orchestrator/engines/`), strategies (`orchestrator/strategies/`), and pure DTO contracts (`models/dtos/engine.py`) are cleanly documented as decoupled computational pipelines.</action>
    <action>Execute the fully parameterized command `/tier7-describe-architecture` with tracker `docs/epic/EPIC_155_tracker.md`, Epic `@[docs/epic/EPIC_155_Engine_Concurrency_Decoupling.md]`, and the structured directives: (1) Target KIs to Synchronize: `@[ki_execution_engine_protocol.md]`, `@[ki_python_314_concurrency_strictness.md]`; (2) Directory Reference Sync: `@[.agents/rules/04_directory_reference.md]`; (3) Pillar Documentation Sync: `@[docs/architecture/03_cognitive_orchestration_engine.md]` and `@[docs/architecture/05_resilience_and_observability.md]`, documenting the 2-tier concurrency architecture: macro workflow concurrency in Arq (`max_concurrent_workflows`), micro request throttling in `LiteLLMProvider` (`semaphore_*` settings), Phase 2 synthesis fan-out (`max_concurrent_llm_steps`), and pure stateless computation in `ExecutionEngine`.</action>
  </step>

  <step id="7.3" name="SYNCHRONIZE_SYSTEM_CONCURRENCY_SSOT_RULE_TEXT">
    <action>With explicit user approval, update the `system_concurrency_ssot` rule block in `@[.agents/rules/01-python-backend.md]` and `@[.agents/rules/05_llm_architecture.md]` so the text names the physical SSOT: macro limit `max_concurrent_workflows` (Arq) and micro limit derived from `semaphore_low_rpm_threshold`, `semaphore_low_rpm_limit`, `semaphore_max_concurrency`, and `semaphore_rpm_divisor` (`LiteLLMProvider`), removing the obsolete claim that `LLMClient` is sized by `max_concurrent_llm_steps` and that parallel DAG steps acquire a step-level semaphore.</action>
  </step>

  <validation_gate>
    <action>Run `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/tasks_EPIC_155/07_phase7_plan.md`</action>
    <action>Run `uv run python scripts/audit_markdown_boundaries.py --file .agents/rules/04_directory_reference.md`</action>
    <action>Verify ki_execution_engine_protocol.md and ki_python_314_concurrency_strictness.md accurately describe the Pure Compute Engine Law and Two-Tier Concurrency Architecture</action>
    <action>Verify docs/architecture/ manifests accurately reflect present-tense concurrency architecture without historical phase references</action>
    <action>Run `uv run pytest backend_v2/tests/unit/test_ast_concurrency_guardrails.py`</action>
    <action>Run `uv run pytest backend_v2/tests/unit/models/test_system_concurrency_compliance.py`</action>
  </validation_gate>
</execution_protocol>
```

