# Epic 101: Global Extraction Node — Master Tracker

> **Epic Source:** [EPIC_101_Global_Extraction_Node.md](file:///c:/src/quorum/docs/epic/EPIC_101_Global_Extraction_Node.md)
> **Task Directory:** [tasks_epic_101_global_extraction/](file:///c:/src/quorum/docs/epic/tasks_epic_101_global_extraction/)

---

## Execution Status

### Phase 1: RAG Pre-Flight Pipeline & Virtual Step Injection

- [x] `[OK]` **Tier 0 Red-Team**: Run `/tier0-research-plan` on [phase_1a_backend_models_and_enums.md](file:///c:/src/quorum/docs/epic/tasks_epic_101_global_extraction/phase_1a_backend_models_and_enums.md) in a fresh context window. This plan introduces a new SSOT component (`GlobalAtomBlackboard`) and modifies core domain models.

- [x] `[OK]` **Phase 1A — Backend Models, Enums & Settings**: Execute [phase_1a_backend_models_and_enums.md](file:///c:/src/quorum/docs/epic/tasks_epic_101_global_extraction/phase_1a_backend_models_and_enums.md)
  - New `EngineOverrideStrategy` enum
  - `engine_override` field on `StepRule`
  - `GlobalAtomBlackboard` + `DraftAtomList` migration to domain models
  - `"progress"` added to `TraceEvent.event_type`
  - `max_extracted_atoms_per_document` setting
  - Physical Anchoring Null Hypothesis (`is_logical_deduction`)

- [x] `[OK]` **Phase 1B — RAG Pre-Flight Pipeline**: Execute [phase_1b_rag_preflight_pipeline.md](file:///c:/src/quorum/docs/epic/tasks_epic_101_global_extraction/phase_1b_rag_preflight_pipeline.md)
  - Virtual Step injection in `DAGExecutor`
  - Map-Reduce atomization with DLQ routing
  - Blackboard projection to `context_variables["global_atoms"]`
  - Progress events for SSE liveness
  - Quote Normalization Strategy (`AnchorValidationService`)

---

### Phase 2: Pre-Hydrated Synthesis Strategy & SDUI Routing

- [x] `[OK]` **Tier 0 Red-Team**: Run `/tier0-research-plan` on [phase_2a_pre_hydrated_synthesis_strategy.md](file:///c:/src/quorum/docs/epic/tasks_epic_101_global_extraction/phase_2a_pre_hydrated_synthesis_strategy.md) in a fresh context window. This plan introduces a new SSOT strategy component and modifies the `NodeExecutor` routing cascade.

- [x] `[OK]` **Phase 2A — Pre-Hydrated Synthesis Strategy**: Execute [phase_2a_pre_hydrated_synthesis_strategy.md](file:///c:/src/quorum/docs/epic/tasks_epic_101_global_extraction/phase_2a_pre_hydrated_synthesis_strategy.md)
  - `PreHydratedSynthesisStrategy` class creation
  - AliasEngine integration (inject & reverse hydrate)
  - Single-Call Mandate enforcement
  - `NodeExecutor.execute()` routing cascade
  - Cache-Busting structural unit test
  
- [x] `[OK]` **Phase 2B — Flutter StepRule & Seed Data**: Execute [phase_2b_flutter_seed_data_routing.md](file:///c:/src/quorum/docs/epic/tasks_epic_101_global_extraction/phase_2b_flutter_seed_data_routing.md)
  - Flutter `StepRule` Freezed update + `build_runner`
  - `seed_data.json` engine_override mappings
  - `"reasoning"` strategy in model_registry
  - Vertex adapter reasoning parameter extraction

- [x] `[OK]` **Phase 2C — Integration Checkpoint**: Execute [phase_2c_integration_checkpoint.md](file:///c:/src/quorum/docs/epic/tasks_epic_101_global_extraction/phase_2c_integration_checkpoint.md)
  - Full-stack end-to-end validation
  - Manual UI verification of Virtual Step, progress events, and synthesis path

---

### Phase 3+: Deferred Phases (Detailed Plans NOT Yet Generated)

> **CRITICAL LIMIT**: Per Tier 1 workflow rules, detailed plans beyond Phase 2 are deferred to prevent LLM cognitive overload. The executing agent must re-invoke Tier 1 after Phase 2 completion.

- [x] `[SKIPPED]` **Re-invoke Tier 1 Planner**: Skipped. Hardening is superseded by EPIC 104 & 105.

---

### Hardening & Sunset Pipeline

> **NOTE:** Hardening and proxy sunsets have been explicitly skipped. `pre_hydrated_synthesis.py` will be entirely deleted by **EPIC 105 (Synthesis Engine Unification)**, making its hardening wasted effort. Proxy cleanup in `llm.py` will happen naturally during **EPIC 104 (TDA Pipeline Extraction)**.

- [x] `[SKIPPED]` **Tier 2 Hardening — Backend**: Skipped (Superseded by EPIC 104/105)
- [x] `[SKIPPED]` **Tier 2 Hardening — Frontend**: Skipped (Superseded by EPIC 104/105)
- [x] `[SKIPPED]` **Proxy Sunset & Consumer Migration**: Skipped (Superseded by EPIC 104/105)
- [x] `[SKIPPED]` **Pre-Delete Audit**: Skipped (Superseded by EPIC 104/105)
- [x] `[SKIPPED]` **Semantic Coverage & Zero-Loss Audit**: Skipped (Superseded by EPIC 104/105)

---

### Documentation & Knowledge Items

> **NOTE:** Documentation updates deferred until the Execution Engine refactoring (EPIC 104/105) stabilizes the final architecture.

- [x] `[SKIPPED]` **Update Architecture Documentation**: Deferred to post-EPIC 105.
- [x] `[SKIPPED]` **Update Directory Reference**: Deferred to post-EPIC 105.
- [x] `[SKIPPED]` **Create Knowledge Item**: Deferred to post-EPIC 105.

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
| **§2.1** RAG Pre-Flight Pipeline (run atomizer ONCE before steps) | Phase 1B | `[OK]` |
| **§2.2** Virtual Step Injection (ephemeral UI step during RAG) | Phase 1B | `[OK]` |
| **§2.3** Pre-Hydrated Synthesis Strategy (single-call fast path) | Phase 2A | `[OK]` |
| **§2.5** Dual-Input Synthesis Model (Map + Encyclopedia) | Phase 2A | `[OK]` |
| **§3.1** Pre-Condition Scan (skip preflight if no PRE_HYDRATED steps) | Phase 1B | `[OK]` |
| **§3.1.2** Virtual StepRule injection with model_copy | Phase 1B | `[OK]` |
| **§3.1.3** ChunkingService + TwoPassAtomizer per input file | Phase 1B | `[OK]` |
| **§3.1.4** TaskGroup + Semaphore + DLQ routing | Phase 1B | `[OK]` |
| **§3.1.5** Progress TraceEvents during map-reduce | Phase 1B (+ Phase 1A `"progress"` literal) | `[OK]` |
| **§3.1.6** GlobalAtomBlackboard model + context_variables projection | Phase 1A + Phase 1B | `[OK]` |
| **§3.2.1** Hydrate facts + AliasEngine isolation | Phase 2A | `[OK]` |
| **§3.2.2** PromptCompiler preservation (XML sovereignty) | Phase 2A | `[OK]` |
| **§3.2.3** Ephemeral Caching Topology (static system prompt) | Phase 2A | `[OK]` |
| **§3.2.4** Single-Call Synthesis via execute_structured_task | Phase 2A | `[OK]` |
| **§3.1** EngineOverrideStrategy enum | Phase 1A | `[OK]` |
| **§3.2** StepRule.engine_override field | Phase 1A (backend) + Phase 2B (Flutter) | `[OK]` |
| **§3.2** NodeExecutor routing priority cascade | Phase 2A | `[OK]` |
| **§3.4** seed_data.json engine_override mappings | Phase 2B | `[OK]` |
| **§3.5** Reasoning strategy in model_registry | Phase 2B | `[OK]` |
| **§3.5** Vertex adapter reasoning parameter extraction | Phase 2B | `[OK]` |
| **§3.6** Apply reasoning to critical nodes | Phase 2B | `[OK]` |
| **§4** UI Fallback (Virtual Injection Risk) — AppErrorBoundary | Phase 2C (validation) | `[OK]` |
| **§4** TaskGroup Cascade Isolation — DLQ routing | Phase 1B | `[OK]` |
| **§4** Blackboard Anti-Corruption Layer | Phase 1B | `[OK]` |
| **§4** Alias Hallucination Resilience | Phase 2A | `[OK]` |
| **§4** Payload Bloat Risk — Atom Ceiling | Phase 1A (setting) + Phase 1B (enforcement) | `[OK]` |
| **§4** Cache-Busting Prevention (hash test) | Phase 2A (test) | `[OK]` |
| **§4** Quote Normalization (AnchorValidationService) | Phase 2A | `[OK]` |
| **§4** State Sovereignty (no raw dicts) | Phase 1B | `[OK]` |
| **§4** Fail-Fast Hydration (DependencyError) | Phase 2A | `[OK]` |
| **§4** Single-Call Mandate (no hidden loops) | Phase 2A | `[OK]` |
| **§4** Rogue SDK Ban | Phase 2A | `[OK]` |
| **§4** FinOps Cascading Routing (override Bo3) | Phase 2A | `[OK]` |
| **§4** Tripartite Configuration Architecture | Phase 1A (enums/settings split) | `[OK]` |
| **DraftAtomList/DraftExtractedAtom** SSOT migration | Phase 1A | `[OK]` |
| **DraftAtomList.dlq_status** sentinel field | Phase 1A | `[OK]` |
| Proxy sunset for two_pass_atomizer re-exports | Hardening pipeline | `[SKIPPED]` |
| Architecture docs update | Documentation phase | `[SKIPPED]` |
| KI creation for GlobalAtomBlackboard | Documentation phase | `[SKIPPED]` |

---

## Session Handover Context

### Achieved
- Phase 1A (Backend Models & Enums) completely implemented and validated.
- Phase 1B (RAG Pre-Flight Pipeline) completely implemented and validated.
- Phase 2A (Pre-Hydrated Synthesis Strategy) completely implemented and validated. 100% backend test pass and 79.12% coverage.
- Phase 2B (Flutter StepRule & Seed Data routing) completely implemented and validated. Seed data nodes mapped and Vertex adapter configured for thinking budget.
- Phase 2C (Integration Checkpoint) completely implemented and validated.

### Learned
- Mocking classes imported directly inside local methods (e.g. `TwoPassAtomizer`) requires patching their source module path, not the consumer module.
- Retries using `@retry` must be configured to fetch variables dynamically (`get_settings()`) at import time to preserve Configuration Sovereignty.
- Pydantic reverse-MRO iteration requires careful base class ordering in dynamic schemas.
- Vertex AI native thinking parameters must be passed directly into `extra_body` when bypassing LiteLLM abstractions.

### Remaining
- NONE. EPIC 101 is fully complete. Future hardening is delegated to EPIC 104 and EPIC 105. Proceed to EPIC 104.

---

## Resume Command

```
/tier5-resume --workflow=/tier1-planner --target="docs/epic/EPIC_104_tda_pipeline_extraction.md" --rules="00-antigravity-core.md, 01-python-backend.md, 02_flutter_desktop.md, 03_seed_vault.md" --achieved="EPIC 101, 102, and 103 are fully complete and integration tested. Hardening deferred to avoid conflicts." --learned="pre_hydrated_synthesis.py hardening is a waste as EPIC 105 will delete it. llm.py proxy cleanup deferred to EPIC 104." --remaining="Create implementation plan for EPIC 104: TDA Pipeline Extraction."
```
