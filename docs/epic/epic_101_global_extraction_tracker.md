# Epic 101: Global Extraction Node — Master Tracker

> **Epic Source:** [EPIC_101_Global_Extraction_Node.md](file:///c:/src/quorum/docs/epic/EPIC_101_Global_Extraction_Node.md)
> **Task Directory:** [tasks_epic_101_global_extraction/](file:///c:/src/quorum/docs/epic/tasks_epic_101_global_extraction/)

---

## Execution Status

### Phase 1: RAG Pre-Flight Pipeline & Virtual Step Injection

- [ ] `[NOK]` **Tier 0 Red-Team**: Run `/tier0-research-plan` on [phase_1a_backend_models_and_enums.md](file:///c:/src/quorum/docs/epic/tasks_epic_101_global_extraction/phase_1a_backend_models_and_enums.md) in a fresh context window. This plan introduces a new SSOT component (`GlobalAtomBlackboard`) and modifies core domain models.

- [ ] `[NOK]` **Phase 1A — Backend Models, Enums & Settings**: Execute [phase_1a_backend_models_and_enums.md](file:///c:/src/quorum/docs/epic/tasks_epic_101_global_extraction/phase_1a_backend_models_and_enums.md)
  - New `EngineOverrideStrategy` enum
  - `engine_override` field on `StepRule`
  - `GlobalAtomBlackboard` + `DraftAtomList` migration to domain models
  - `"progress"` added to `TraceEvent.event_type`
  - `max_extracted_atoms_per_document` setting

- [ ] `[NOK]` **Phase 1B — RAG Pre-Flight Pipeline**: Execute [phase_1b_rag_preflight_pipeline.md](file:///c:/src/quorum/docs/epic/tasks_epic_101_global_extraction/phase_1b_rag_preflight_pipeline.md)
  - Virtual Step injection in `DAGExecutor`
  - Map-Reduce atomization with DLQ routing
  - Blackboard projection to `context_variables["global_atoms"]`
  - Progress events for SSE liveness

---

### Phase 2: Pre-Hydrated Synthesis Strategy & SDUI Routing

- [ ] `[NOK]` **Tier 0 Red-Team**: Run `/tier0-research-plan` on [phase_2a_pre_hydrated_synthesis_strategy.md](file:///c:/src/quorum/docs/epic/tasks_epic_101_global_extraction/phase_2a_pre_hydrated_synthesis_strategy.md) in a fresh context window. This plan introduces a new SSOT strategy component and modifies the `NodeExecutor` routing cascade.

- [ ] `[NOK]` **Phase 2A — Pre-Hydrated Synthesis Strategy**: Execute [phase_2a_pre_hydrated_synthesis_strategy.md](file:///c:/src/quorum/docs/epic/tasks_epic_101_global_extraction/phase_2a_pre_hydrated_synthesis_strategy.md)
  - `PreHydratedSynthesisStrategy` class creation
  - AliasEngine integration (inject & reverse hydrate)
  - Single-Call Mandate enforcement
  - `NodeExecutor.execute()` routing cascade
  
- [ ] `[NOK]` **Phase 2B — Flutter StepRule & Seed Data**: Execute [phase_2b_flutter_seed_data_routing.md](file:///c:/src/quorum/docs/epic/tasks_epic_101_global_extraction/phase_2b_flutter_seed_data_routing.md)
  - Flutter `StepRule` Freezed update + `build_runner`
  - `seed_data.json` engine_override mappings
  - `"reasoning"` strategy in model_registry
  - Vertex adapter reasoning parameter extraction

- [ ] `[NOK]` **Phase 2C — Integration Checkpoint**: Execute [phase_2c_integration_checkpoint.md](file:///c:/src/quorum/docs/epic/tasks_epic_101_global_extraction/phase_2c_integration_checkpoint.md)
  - Full-stack end-to-end validation
  - Manual UI verification of Virtual Step, progress events, and synthesis path

---

### Phase 3+: Deferred Phases (Detailed Plans NOT Yet Generated)

> **CRITICAL LIMIT**: Per Tier 1 workflow rules, detailed plans beyond Phase 2 are deferred to prevent LLM cognitive overload. The executing agent must re-invoke Tier 1 after Phase 2 completion.

- [ ] `[NOK]` **Re-invoke Tier 1 Planner**: After Phase 2C completes, invoke the Tier 1 Planner (`/tier1-planner @[EPIC_101_Global_Extraction_Node.md]`) in a NEW context window to generate detailed plans for any remaining hardening phases based on the updated codebase state.

---

### Hardening & Sunset Pipeline

- [ ] `[NOK]` **Tier 2 Hardening — Backend**: Run `/tier2-hardening-backend` targeted at:
  - `backend_v2/models/domain/blackboard.py`
  - `backend_v2/services/orchestrator/strategies/pre_hydrated_synthesis.py`
  - Modernize to Pydantic V2 strict, PEP 257, and Push model patterns.

- [ ] `[NOK]` **Tier 2 Hardening — Frontend**: Run `/tier2-hardening-frontend` targeted at:
  - `client_app_v2/lib/features/studio/models/workflow.dart`
  - Verify Freezed strict compliance.

- [ ] `[NOK]` **Proxy Sunset & Consumer Migration**: Codebase-wide search/replace to remove the `@deprecated` re-export proxies in `two_pass_atomizer.py`. All consumers must import directly from `backend_v2.models.domain.blackboard`.
  - Search: `from backend_v2.services.orchestrator.two_pass_atomizer import DraftAtomList`
  - Replace: `from backend_v2.models.domain.blackboard import DraftAtomList`
  - Files affected: `test_two_pass_atomizer.py`, `test_atomizer.py`, `llm.py`

- [ ] `[NOK]` **Pre-Delete Audit**: Verify no orphaned dependencies remain. Confirm all consumers reference `backend_v2.models.domain.blackboard`. Remove `@deprecated` proxy re-exports from `two_pass_atomizer.py`.

- [ ] `[NOK]` **Semantic Coverage & Zero-Loss Audit**: Mathematically verify that:
  - Line coverage of surviving business logic remains >90%
  - All old fallback tests have been cleanly replaced by strict Pydantic V2 boundary tests
  - No legacy dictionary tests remain that violate the Anti-TDD Trap mandate

---

### Documentation & Knowledge Items

- [ ] `[NOK]` **Update Architecture Documentation**: Update `docs/architecture/` pillar documents with:
  - RAG Pre-Flight Pipeline description
  - PreHydratedSynthesisStrategy documentation
  - GlobalAtomBlackboard SSOT documentation
  
- [ ] `[NOK]` **Update Directory Reference**: Update `.agents/rules/04_directory_reference.md` with:
  - `backend_v2/models/domain/blackboard.py` — RAG Blackboard domain models
  - `backend_v2/services/orchestrator/strategies/pre_hydrated_synthesis.py` — Pre-Hydrated Synthesis strategy
  
- [ ] `[NOK]` **Create Knowledge Item**: Create KI `global_atom_blackboard` in `<appDataDir>/knowledge/` documenting:
  - `GlobalAtomBlackboard` usage rules
  - How `context_variables["global_atoms"]` is populated and consumed
  - The Single-Call Mandate for synthesis strategies
  - The DLQ sentinel pattern for `DraftAtomList.dlq_status`

---

## Instructions for the Execution Agent

1. Execute tasks in the order listed above. Each `[NOK]` becomes `[OK]` upon completion.
2. After completing each phase, run the quality gate specified in the plan.
3. After each quality gate pass, perform an atomic `git commit`.
4. **MANDATORY**: Before handing over the session, update the `/tier5-resume` command at the bottom of this tracker file with the current progress.
5. If you encounter an issue that requires re-planning, stop and inform the user.

---

## Requirements Traceability Matrix

| Epic Requirement | Phase/Plan | Status |
|---|---|---|
| **§2.1** RAG Pre-Flight Pipeline (run atomizer ONCE before steps) | Phase 1B | `[NOK]` |
| **§2.2** Virtual Step Injection (ephemeral UI step during RAG) | Phase 1B | `[NOK]` |
| **§2.3** Pre-Hydrated Synthesis Strategy (single-call fast path) | Phase 2A | `[NOK]` |
| **§2.5** Dual-Input Synthesis Model (Map + Encyclopedia) | Phase 2A | `[NOK]` |
| **§3.1** Pre-Condition Scan (skip preflight if no PRE_HYDRATED steps) | Phase 1B | `[NOK]` |
| **§3.1.2** Virtual StepRule injection with model_copy | Phase 1B | `[NOK]` |
| **§3.1.3** ChunkingService + TwoPassAtomizer per input file | Phase 1B | `[NOK]` |
| **§3.1.4** TaskGroup + Semaphore + DLQ routing | Phase 1B | `[NOK]` |
| **§3.1.5** Progress TraceEvents during map-reduce | Phase 1B (+ Phase 1A `"progress"` literal) | `[NOK]` |
| **§3.1.6** GlobalAtomBlackboard model + context_variables projection | Phase 1A + Phase 1B | `[NOK]` |
| **§3.2.1** Hydrate facts + AliasEngine isolation | Phase 2A | `[NOK]` |
| **§3.2.2** PromptCompiler preservation (XML sovereignty) | Phase 2A | `[NOK]` |
| **§3.2.3** Ephemeral Caching Topology (static system prompt) | Phase 2A | `[NOK]` |
| **§3.2.4** Single-Call Synthesis via execute_structured_task | Phase 2A | `[NOK]` |
| **§3.1** EngineOverrideStrategy enum | Phase 1A | `[NOK]` |
| **§3.2** StepRule.engine_override field | Phase 1A (backend) + Phase 2B (Flutter) | `[NOK]` |
| **§3.2** NodeExecutor routing priority cascade | Phase 2A | `[NOK]` |
| **§3.4** seed_data.json engine_override mappings | Phase 2B | `[NOK]` |
| **§3.5** Reasoning strategy in model_registry | Phase 2B | `[NOK]` |
| **§3.5** Vertex adapter reasoning parameter extraction | Phase 2B | `[NOK]` |
| **§3.6** Apply reasoning to critical nodes | Phase 2B | `[NOK]` |
| **§4** UI Fallback (Virtual Injection Risk) — AppErrorBoundary | Phase 2C (validation) | `[NOK]` |
| **§4** TaskGroup Cascade Isolation — DLQ routing | Phase 1B | `[NOK]` |
| **§4** Blackboard Anti-Corruption Layer | Phase 1B | `[NOK]` |
| **§4** Alias Hallucination Resilience | Phase 2A | `[NOK]` |
| **§4** Payload Bloat Risk — Atom Ceiling | Phase 1A (setting) + Phase 1B (enforcement) | `[NOK]` |
| **§4** Cache-Busting Prevention (hash test) | Phase 2A (test) | `[NOK]` |
| **§4** Quote Normalization (AnchorValidationService) | Phase 2A | `[NOK]` |
| **§4** State Sovereignty (no raw dicts) | Phase 1B | `[NOK]` |
| **§4** Fail-Fast Hydration (DependencyError) | Phase 2A | `[NOK]` |
| **§4** Single-Call Mandate (no hidden loops) | Phase 2A | `[NOK]` |
| **§4** Rogue SDK Ban | Phase 2A | `[NOK]` |
| **§4** FinOps Cascading Routing (override Bo3) | Phase 2A | `[NOK]` |
| **§4** Tripartite Configuration Architecture | Phase 1A (enums/settings split) | `[NOK]` |
| **DraftAtomList/DraftExtractedAtom** SSOT migration | Phase 1A | `[NOK]` |
| **DraftAtomList.dlq_status** sentinel field | Phase 1A | `[NOK]` |
| Proxy sunset for two_pass_atomizer re-exports | Hardening pipeline | `[NOK]` |
| Architecture docs update | Documentation phase | `[NOK]` |
| KI creation for GlobalAtomBlackboard | Documentation phase | `[NOK]` |

---

## Session Handover Context

### Achieved
- Comprehensive Tier 1 Epic decomposition of Epic 101 into 6 micro-chunked plans (1A, 1B, 2A, 2B, 2C, Integration)
- Strict architectural invariant injection from `.agents/rules/`
- Complete Requirements Traceability Matrix mapping all 35+ Epic requirements
- Dynamic codebase investigation confirming: current state of `dag_executor.py`, `two_pass_atomizer.py`, `state.py`, `v2_core.py`, `enums.py`, `execution_core.py`, `workflow.dart`, `seed_data.json`
- Destructive Operation Inventory for `DraftAtomList`/`DraftExtractedAtom` migration

### Learned
- `EngineOverrideStrategy` enum and `engine_override` field do NOT yet exist anywhere in the codebase — confirmed via grep
- `context_variables` is defined in `execution_core.py` as `dict[str, Any]` — suitable for blackboard projection
- `TraceEvent.event_type` currently has 7 literals, needs `"progress"` added
- Flutter `StepRule` uses `disallowUnrecognizedKeys: true` — MUST add `engine_override` field before backend change
- Virtual step injection pattern (`sys_render_*`) already exists in `dag_executor.py` lines 369-392
- `TwoPassAtomizer` has 3 external consumers for its model exports (2 test files + `llm.py`)

### Remaining
- Execute all `[NOK]` phases sequentially
- After Phase 2C, re-invoke Tier 1 for remaining hardening phases
- Complete documentation and KI creation

---

## Resume Command

```
/tier5-resume --workflow=/tier2-execute --target="docs/epic/epic_101_global_extraction_tracker.md, docs/epic/EPIC_101_Global_Extraction_Node.md" --rules="00-antigravity-core.md, 01-python-backend.md, 02_flutter_desktop.md"
```
