# EPIC 154 — Audit Report (Dynamic Causal Discovery Engine)

**Audit Date:** 2026-09-30
**Auditor Role:** Principal Enterprise Architect & System Red Team
**Status:** CONDITIONALLY APPROVED (with mandatory corrections)

---

## 1. Executive Summary

EPIC 154 proposes a `CausalDiscoveryEngine` as a new `ExecutionEngine` implementation for exploratory open-text argument mining. The Epic is architecturally ambitious but fundamentally sound. It correctly identifies the neuro-symbolic hybrid paradigm (LLM extraction + deterministic topological evaluation), cleanly separates from `TDAEngine`, and reuses established infrastructure (`TopologicalEvaluator`, `SlidingWindowLinker`, `TwoPassAtomizer`).

**Overall Assessment:** The Epic demonstrates strong alignment with Quorum's 2026 architectural invariants. It correctly identifies pre-existing technical debt, applies Five-Axis pruning, and maintains the Tripartite Pipeline boundary. However, several **stale line-bound references**, **missing method references**, and **potential architectural violations** require correction before implementation planning.

---

## 2. System 2 Deep Deconstruction — Five-Axis Analysis

### Axis 1: Target Scope & Boundary (Scope Inquisitor)

**Findings:**

| Finding | Severity | Detail |
| :--- | :--- | :--- |
| **Scope is appropriate for a Feature Epic** | ✅ PASS | 42 target files (8 NEW, 34 MODIFY) + 5 context files is justified for a full-stack engine + SDUI + export pipeline. |
| **DISTANT FUTURE ROADMAP classification is correct** | ✅ PASS | The `[!CAUTION]` box explicitly prevents premature activation into the normative evaluation core. |
| **Blast radius is well-bounded** | ✅ PASS | New engine is cleanly isolated in its own file; modifications to existing files are surgical (enum additions, union extensions, registry mappings). |
| **`_calculate_packets` method DOES exist — reference valid** | ✅ PASS | Verified at `@[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L71]`. The anonymous `list[tuple[str, str, list[str]]]` return type is confirmed as active Tuple Hell. |
| **`self.type == "llm"` string comparisons EXIST — reference valid** | ✅ PASS | Verified at `@[backend_v2/models/domain/step.py#L102]` and `@[backend_v2/models/domain/step.py#L115]`. Additionally, `ValueError` is used instead of `AppException` at L106, L110, L114, L118. |
| **`atom_flattening_hook` heuristic DOES exist — reference valid** | ✅ PASS | Verified at `@[backend_v2/services/orchestrator/dag_executor.py#L184]`. This is a `ban_heuristic_identifier_matching` violation. |
| **`AnySduiBlock` union currently has 18 block types** | ✅ PASS | Verified at `@[backend_v2/models/view/sdui.py]` (L797-L815). Adding `SduiCausalGraphBlock` would make 19 — consistent with Epic's assertion. |
| **`ExecutionEngine` Protocol lacks `telemetry_strategy_label`** | ✅ PASS | Verified at `@[backend_v2/services/orchestrator/engines/base.py]` (L12-L31). Protocol only defines `execute()`. |
| **`_resolve_execution_engine` exists at correct location** | ✅ PASS | Verified at `@[backend_v2/services/orchestrator/dag_executor.py#L160-L187]`. |

### Axis 2: Eradicated Duct-Tape (Under-Engineering Ban)

**Pre-Existing Technical Debt Confirmed in Touched Files:**

| File | Debt Item | Line(s) | Status |
| :--- | :--- | :--- | :--- |
| `@[backend_v2/models/domain/step.py#L92-L119]` | String literal comparisons `self.type == "llm"` and `self.type == "logic"` instead of `StepType.LLM` / `StepType.LOGIC` enum checks | L102, L115 | 🔴 Active debt — Epic Phase 1.3 correctly schedules fix |
| `@[backend_v2/models/domain/step.py#L92-L119]` (L106-L118) | `ValueError(msg)` instead of `AppException(ErrorCodes.VALIDATION_FAILED, msg)` — violates RFC 7807 dual-reporting | L106, L110, L114, L118 | 🔴 Active debt — Epic Phase 1.3 correctly schedules fix |
| `@[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L71]` | Anonymous 3-tuple return type `list[tuple[str, str, list[str]]]` — violates `ban_anonymous_state_tuples` | L50, L65 | 🔴 Active debt — Epic Phase 1.1 correctly schedules fix |
| `@[backend_v2/services/orchestrator/two_pass_atomizer.py#L50]` | Hardcoded `packet_size: int = 50` default — should be `get_settings().two_pass_atomizer_packet_size` | L50 | 🔴 Active debt — Epic Phase 1.1 correctly schedules fix |
| `@[backend_v2/services/orchestrator/dag_executor.py#L184]` | `"atom_flattening_hook" in step_def.pre_hooks` — violates `ban_heuristic_identifier_matching` | L184 | 🔴 Active debt — Epic Phase 1.4 correctly schedules fix |
| `@[backend_v2/models/dtos/step_output.py#L57-L71]` (L42-L47) | `dict[str, HydratedAtomDTO]`, `dict[str, float]`, `dict[str, str]` in `StepPayloadValue` union — typed but borderline naked dicts | L42, L46, L47 | ⚠️ Pre-existing — not in Epic scope boundary |

**Verdict:** The Epic correctly identifies and schedules ALL critical pre-existing debt in Phase 1. The Scoped Boy Scout Rule is properly applied.

### Axis 3: Approved Best Practice (Target Invariant)

| Invariant | Epic Compliance |
| :--- | :--- |
| `ConfigDict(strict=True, extra="forbid", frozen=True)` on all new DTOs | ✅ Explicitly mandated for all 8 new DTOs |
| `ExecutionEngine` Protocol compliance | ✅ `CausalDiscoveryEngine(ExecutionEngine)` with `execute(EngineExecutionRequest) -> EngineExecutionResult` |
| Tripartite Pipeline decoupling | ✅ Phase 1 execution produces immutable DTOs; Phase 2/3 consume without mutation |
| Four-Layer Clean Stack prompting | ✅ Static prefix for caching, dynamic theory context, extraction protocol, user payload at tail |
| Exact lexical anchoring (`str.find`) | ✅ Explicitly mandated, fuzzy matching explicitly prohibited |
| SDUI Dumb Painter architecture | ✅ Backend pre-computes all critical path nodes; client performs zero semantic inference |
| RFC 7807 dual-reporting | ✅ Specific `ErrorCodes` defined: `CAUSAL_DISCOVERY_EMPTY_DOCUMENT`, `CAUSAL_DISCOVERY_CYCLE_DETECTED`, `CAUSAL_DISCOVERY_DATA_STARVATION` |
| Strategy + Registry Pattern | ✅ `NODE_STRATEGY_REGISTRY[StepType.CAUSAL_DISCOVERY] -> _build_llm_strategy` |
| Thread-isolated cycle detection | ✅ Reuses `TopologicalEvaluator` with `asyncio.to_thread` cycle detection |
| Cross-language enum parity | ✅ `test_enum_parity.py` assertions mandated for `TargetBlockType` and `CausalDisplayMode` |

### Axis 4: Pruned Over-Engineering (Complexity Slayer — 30% Deletion Test)

| Proposed Abstraction | Verdict | Justification |
| :--- | :--- | :--- |
| `CausalStep` domain subclass | ✅ PRUNED | Correctly rejected. Reuses existing `Step` with validation branching. |
| Persistent graph database (Neo4j/NetworkX persistence) | ✅ PRUNED | Correctly rejected. In-memory `LinkedAtomGraph` projected directly to SDUI. |
| Granular micro-toggles (4 separate booleans) | ✅ PRUNED | Correctly replaced with single `CausalDisplayMode` selector. |
| 8 Pydantic V2 DTOs | ✅ RETAINED | Each DTO represents an irreducible domain concept. Cannot be merged without semantic loss. |

**30% Deletion Test:** If `AntiFluffAuditDTO`, `PrescriptiveRemediationDTO`, and `FairScoringBreakdownDTO` were deleted, the five stakeholder benefit pipelines collapse to simple pass/fail with no diagnostic granularity. These are retained correctly.

### Axis 5: Fail-Fast Proof Anchor (Incorruptible Judge)

| Verification Gate | Status |
| :--- | :--- |
| `AppException(CAUSAL_DISCOVERY_EMPTY_DOCUMENT)` on empty text | ✅ Mandated in Phase 3.1 with ISTQB negative test |
| `AppException(CAUSAL_DISCOVERY_DATA_STARVATION)` on 0 upstream nodes | ✅ Mandated in Phase 3.2 with integration test |
| `cycle_detected=True` without event loop deadlock | ✅ Mandated via `TopologicalEvaluator` thread-isolated detection |
| `ConfigDict(strict=True, extra="forbid")` AST guardrails | ✅ `QGR001`, `QGR002` enforcement mandated |
| `test_sdui_semantic_parity.py` cross-platform parity | ✅ Mandated for 19 block types |
| `test_enum_parity.py` cross-language parity | ✅ Mandated for `TargetBlockType` and `CausalDisplayMode` |
| `backend_audit_loop.py` global completion gate | ✅ Phase 7 step mandated |

---

## 3. Falsification & Red-Teaming (Anti-Happy-Path)

### 3.1 Mandatory Falsification Questions

| Question | Finding |
| :--- | :--- |
| **Duct-Tape solutions or hidden fallbacks?** | ✅ NO. Epic explicitly bans all fallback branches. `CausalDiscoveryEngine` is zero-fallback; Fail-Fast on empty documents and data starvation. |
| **Boundary contracts strictly defined?** | ✅ YES. All 8 DTOs use `extra="forbid"`. `EngineExecutionRequest` / `EngineExecutionResult` are the sole interface. |
| **Atomic Data & Test Migration bound together?** | ✅ YES. Phase 1 cleanups run BEFORE new business logic. Phase 2 enum additions synchronize Python + Dart + test assertions in the same step. |
| **Destructive Operation Inventory with Sunset List?** | ✅ YES. Section 2.3 explicitly maps 6 items to replacements or "INTENTIONALLY DROPPED". |
| **Quantitative Scope Validation?** | ✅ YES. Section 2.1 has an explicit table: 42 target files (8 NEW, 34 MODIFY) + 5 context files. |
| **Legacy Flat Field Eradication?** | ✅ N/A. No legacy flat fields being migrated. |
| **Mandatory Phase Execution Order?** | ⚠️ PARTIALLY. See Finding F-01 below. |
| **Upstream Parity & Goal Alignment?** | ✅ YES. Aligns with `ki_execution_engine_protocol`, `ki_topological_engine`, `ki_tripartite_pipeline_architecture`, `ki_zero_permissive_typing`, `ki_dumb_painter_sdui`. |

### 3.2 Concrete Failure Modes

**Failure Mode F-01: Phase Ordering Risk — Flutter Enum Parity Before Backend Enums Exist**

- **Root Cause:** Phase 2 (Step 2 in the execution protocol XML) bundles Python enum creation AND Dart enum creation AND Studio Flutter widget updates into a SINGLE execution step. If the executing agent processes Dart files before Python `enums.py` is committed, the `test_enum_parity.py` gate will fail because the Python SSOT doesn't yet exist.
- **Risk Level:** MEDIUM
- **Recommendation:** The Epic already places Python enum creation before Dart updates within the step's action list (correct ordering). However, the implementation plan should mandate an ATOMIC CHECKPOINT COMMIT between backend enum additions and frontend enum additions to guarantee deterministic baseline.

**Failure Mode F-02: `AdapterContext` Schema Mutation with `extra="forbid"`**

- **Root Cause:** The Epic proposes adding `causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None` to `AdapterContext` (Phase 4.1, line 497). `AdapterContext` currently enforces `ConfigDict(frozen=True, strict=True, extra="forbid")` (verified at `@[backend_v2/services/sdui/adapters/base_adapter.py#L25]`). This is a legitimate schema mutation but triggers `ban_drive_by_schema_mutations` — the mutation IS within the Epic's explicit scope boundary (not a drive-by fix), so it is architecturally permissible.
- **Risk Level:** LOW — Must ensure Full-Duplex Serialization Parity and that `causal_result` is never serialized across network boundaries.
- **Recommendation:** The Epic correctly states "strictly an in-memory execution context envelope (never serialized across boundaries)". The implementation plan MUST verify this by asserting `causal_result` is excluded from any `model_dump(mode='json')` boundary serialization.

### 3.3 Zero-Behavioral-Change Gate

**Classification:** This is a **Feature Epic**, not a Refactoring Epic. Phase 1 is correctly isolated as a pure refactoring phase (zero-behavioral-change tech debt cleanups). Phases 2-4 introduce new functionality. This phase separation is architecturally correct and does NOT violate the zero-behavioral-change gate.

### 3.4 Context Rules & KI Coverage Audit

**Rules Coverage:**
- `@[.agents/rules/00-antigravity-core.md]` ✅ Present
- `@[.agents/rules/01-python-backend.md]` ✅ Present
- `@[.agents/rules/02_flutter_desktop.md]` ✅ Present
- `@[.agents/rules/03_seed_vault.md]` ✅ Present
- `@[.agents/rules/04_directory_reference.md]` ✅ Present
- `@[.agents/rules/05_llm_architecture.md]` ✅ Present

**KI Coverage (21 KIs referenced):**
All 21 referenced KIs are architecturally relevant and verified present in the KI summaries. Cross-reference audit result: **6 Rules verified, 21 KIs verified.**

> [!NOTE]
> The KI coverage is comprehensive. No architecturally relevant KIs were found missing from the `<required_context_rules>` block.

---

## 4. Modernity Gate Invariants Audit

| Invariant | Finding |
| :--- | :--- |
| **"e.g." ban** | ⚠️ Line 72: "referencing dynamic PromptBlocks including Toulmin, Walton, or custom enterprise criteria" — uses "including" which is open-ended but acceptable for dynamic domain entities. NOT a violation per `prompt_illustrative_examples_mandate` exemption (these are genuinely open-ended, dynamically configurable Studio entities). |
| **`asyncio.gather` ban** | ✅ PASS. Epic mandates `asyncio.TaskGroup` throughout. |
| **`ConfigDict()` without strict/forbid** | ✅ PASS. All new DTOs mandate `ConfigDict(strict=True, extra="forbid", frozen=True)`. |
| **Raw dict state passing** | ✅ PASS. Zero naked dicts in proposed architecture. |
| **Hardcoded model strings** | ✅ PASS. Uses `LLMClient.from_strategy()` via Model Garden. |
| **`try/except Exception` catch-all** | ✅ PASS. All errors route through `AppException` with RFC 7807. |
| **Regex/fuzzy matching for evidence** | ✅ PASS. Explicitly prohibits fuzzy matching; mandates `str.find`. |
| **Frontend business logic** | ✅ PASS. Flutter widgets are Dumb Painters; `CausalInspectorModal` provides only navigation/exploration, not computation. |

---

## 5. Five-Column Architectural Directive Table (Synthesis)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape | 3. Approved Best Practice | 4. Pruned Over-Engineering | 5. Verification & Fail-Fast |
| :--- | :--- | :--- | :--- | :--- |
| **`CausalDiscoveryEngine`** (NEW standalone engine) | Zero `TDAEngine` branching; zero fallback modes; zero shared state | `ExecutionEngine(Protocol)` with typed `EngineExecutionRequest` / `EngineExecutionResult`; `telemetry_strategy_label` property | `CausalStep` subclass PRUNED; persistent graph DB PRUNED | `test_causal_discovery_engine.py` with ISTQB negative partitions; `AppException(CAUSAL_DISCOVERY_EMPTY_DOCUMENT)` |
| **Phase 1 Tech Debt** (Scoped Boy Scout) | Tuple Hell in `_calculate_packets`; string literal `self.type == "llm"`; `ValueError` not `AppException`; `"atom_flattening_hook"` heuristic | `ChunkPacketDTO`; `StepType.LLM` enum; `AppException(ErrorCodes.VALIDATION_FAILED)`; typed step ontology resolution | No additional abstractions needed | `backend_audit_loop.py` 100% green before Phase 2 |
| **8 Causal DTOs** (NEW Pydantic V2 contracts) | Zero naked dicts; zero anonymous tuples; zero optional fallback keys | `ConfigDict(strict=True, extra="forbid", frozen=True)` on all 8 DTOs | Polymorphic node hierarchies PRUNED; recursive graph wrapper classes PRUNED | `QGR001` + `QGR002` AST guardrails |
| **SDUI Integration** (`SduiCausalGraphBlock` + adapters) | Client-side semantic computation banned; generic raw JSON passing banned | `SduiBlockBase` polymorphic discriminated union; `CausalGraphAdapter` with `causal_display_mode` | Dynamic client-side layout calculators PRUNED; SVG vector serialization PRUNED | `test_sdui_semantic_parity.py` for 19 block types; `test_sdui_template_parity.py` |
| **Studio OutputProfile** (`CausalDisplayMode` selector) | Micro-toggles (`show_causal_anti_fluff`, etc.) eradicated | Single SSOT `causal_display_mode: CausalDisplayMode` selector; Full-Duplex Serialization Parity | Multi-tab configuration wizards PRUNED; per-node styling PRUNED | `flutter_audit_loop.py` build runner; compile-time Freezed parity |
| **Tabular Export** (Excel + Flat CSV) | Multi-row hierarchical CSV headers banned; ragged nested rows banned | Typed scalar causal fields in `FlatExecutionRecordDTO`; strictly 2-line flat CSV | Pivot table generators PRUNED; dynamic CSV dialect negotiation PRUNED | `test_export_service.py` asserting exact column headers and row counts |

---

## 6. Findings Requiring Implementation Planner Awareness

### Finding F-03: `SynthesisEngine` Does Not Implement `ExecutionEngine(Protocol)` Formally

- **Root Cause:** Verified that `SynthesisEngine` at `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36]` uses `class SynthesisEngine:` (no Protocol inheritance) vs `class TDAEngine(ExecutionEngine):` and `class PromptEngine(ExecutionEngine):`.
- **Impact on Epic:** The Epic proposes adding `telemetry_strategy_label` property to the `ExecutionEngine` Protocol. If `SynthesisEngine` doesn't formally implement the Protocol, this property won't be enforced on it by type-checking.
- **Classification:** Pre-existing architectural debt. NOT within EPIC 154's scope boundary, but the implementation plan should be aware that `SynthesisEngine` is a structural Protocol conformer (duck typing) rather than an explicit Protocol implementer.
- **Recommendation:** Flag as adjacent technical debt. The executing agent MUST still add `telemetry_strategy_label` to `SynthesisEngine` to satisfy the Protocol contract, even though it's duck-typed.

### Finding F-04: Line-Bound References Are Currently Accurate But May Drift

- **Root Cause:** All `#Lnn-Lmm` line-bound references were verified against the current codebase state and are accurate. However, any intervening commits before implementation will invalidate these bounds.
- **Recommendation:** Standard practice. The `/tier2-execute` workflow always re-verifies line bounds before editing.

### Finding F-05: `StepPayloadValue` Union Contains Pre-Existing Typed Dicts

- **Root Cause:** `StepPayloadValue` at `@[backend_v2/models/dtos/step_output.py#L57-L71]` (type alias L30-L54) already contains `dict[str, HydratedAtomDTO]`, `dict[str, float]`, `dict[str, str]` — these are typed dictionaries (not `dict[str, Any]`) but still represent Primitive Obsession that should eventually be replaced with dedicated DTOs.
- **Impact on Epic:** The Epic proposes extending this union with `CausalGraphPayloadDTO | CausalTdaFusionResultDTO` which are properly typed DTOs — no regression introduced.
- **Classification:** Pre-existing debt. NOT within Epic scope. No action required.

### Finding F-06: `data_type` Literal Extension May Break Downstream Consumers

- **Root Cause:** `StepOutputDTO.data_type` is currently `Literal["text", "matrix", "unknown"]`. The Epic proposes extending to `Literal["text", "matrix", "causal", "unknown"]`. Any downstream consumer using exhaustive `match/case` on this literal will need updating.
- **Recommendation:** The implementation plan MUST grep for all consumers of `data_type` and verify exhaustive match handling. This should be added as an explicit action in Phase 2 Step 2.

---

## 7. Falsification Matrix Completeness

The Epic's Section 4.6 Falsification Matrix covers 9 invariants. **All 9 are valid and well-specified.** No additional failure modes were discovered beyond F-01 through F-06 documented above.

---

## 8. Final Verdict

| Category | Rating |
| :--- | :--- |
| **Scope & Boundary Definition** | ✅ EXCELLENT — 42 target files with exact line bounds, all verified |
| **Pre-Existing Tech Debt Discovery** | ✅ EXCELLENT — All critical debt in touched files identified and scheduled in Phase 1 |
| **Architectural Compliance** | ✅ EXCELLENT — Full alignment with all Quorum 2026 invariants |
| **Pruning & Over-Engineering Prevention** | ✅ EXCELLENT — 3 abstractions correctly pruned, 8 DTOs correctly retained |
| **Falsification & Red-Teaming** | ✅ GOOD — Comprehensive failure mode analysis with dedicated tests |
| **Phase Execution Order** | ⚠️ GOOD — Minor F-01 risk on atomic commit ordering within Phase 2 |
| **KI & Context Rules Coverage** | ✅ EXCELLENT — 6 rules, 21 KIs verified |

**OVERALL: CONDITIONALLY APPROVED**

The Epic is ready for `/tier1-planner` decomposition after the minor corrections listed in Section 6 are acknowledged. No critical architectural violations were found. The Epic demonstrates exemplary adherence to Quorum's Five-Axis System 2 methodology and the Tripartite Pipeline Architecture.

---

## 9. Recommended Next Steps

1. **Acknowledge** findings F-01 through F-06 (no Epic mutations required — findings are informational for the implementation planner).
2. Start a **new chat session** and execute:
   ```
   /tier1-planner @[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md]
   ```
   The planner should incorporate F-01 (atomic commit between backend/frontend enum steps) and F-06 (`data_type` literal consumer audit) as explicit sub-actions.
