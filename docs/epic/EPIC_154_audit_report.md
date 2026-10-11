# EPIC 154 System 2 Architectural Research & Red-Team Audit Report

**Epic Document:** `@[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md]`  
**Target Domain:** Exploratory Text DAG & Argument Mapping (`CausalDiscoveryEngine`)  
**Auditor:** Principal Enterprise Architect & System Red Team  
**Evaluation Level:** Tier 0 Research Epic (`/tier0-research-epic`)  
**Status:** VALIDATED & HARDENED (DISTANT FUTURE ROADMAP ONLY)

---

## 1. Executive Summary & Architectural Posture

EPIC 154 defines the architecture for Quorum's future **Dynamic Causal Discovery Engine** (`CausalDiscoveryEngine`). It establishes an autonomous neuro-symbolic argument mining pipeline capable of extracting premises, claims, and conclusions directly from free-form text, chaining them into a directed argument graph (`LinkedAtomGraph`), executing topological wave evaluation with Kahn's sort and thread-isolated cycle detection, and attributing causal blame (`blame_parent_ids`) to isolate root causes and prevent double-penalization of secondary faults.

The Epic enforces two decoupled modes:
1. **100% Standalone Mode:** Pure open-text argument mining without criteria blocks, evaluation matrices, or `TDAEngine` dependencies.
2. **Optional Chained Fusion Mode (Phase 1A -> Phase 1B):** Studio-driven pipeline chaining via `StepRule.causal_source_step_id`, where Discovery structures document topology and `TDAEngine` qualitatively evaluates discovered atoms against dynamic matrices.

Presentation is consolidated into **exactly ONE presentation point**: the **Unified Causal Action Card** (`SduiCausalGraphBlock`) integrated directly into `TargetBlockType.EXECUTIVE_SUMMARY_BLOCK`, obeying Flutter Theme Sovereignty and achieving 1:1 cross-platform parity between Flutter desktop and A4 PDF print layouts (constrained to a strict half-page budget). Tabular reporting achieves rectangular multi-row atom parity across Excel ("Raw Data" Tab 2) and CSV exports via `ReportHeaderResolver`.

---

## 2. Context Rules & Knowledge Item (KI) Governance Audit

A comprehensive audit was performed matching the canonical `<required_context_rules>` block in lines 1–28 of `EPIC_154_Dynamic_Causal_Discovery_Engine.md` against Quorum's architectural laws and knowledge base:

| Rule / Knowledge Item Reference | Validation Status | Architectural Role |
| :--- | :--- | :--- |
| `@[.agents/rules/00-antigravity-core.md]` | VERIFIED | Global system invariants, Fail-Fast, no legacy fallbacks, anti-ambiguity |
| `@[.agents/rules/01-python-backend.md]` | VERIFIED | Strict Pydantic V2, zero naked dicts, no duck-typing, RFC 7807 logging |
| `@[.agents/rules/02_flutter_desktop.md]` | VERIFIED | Flutter desktop, Freezed models, Dumb Painter SDUI, Flutter Theme Sovereignty |
| `@[.agents/rules/03_seed_vault.md]` | VERIFIED | SSOT seed data integrity (`seed_data.json`), no drive-by mutations |
| `@[.agents/rules/04_directory_reference.md]` | VERIFIED | Workspace file paths and module boundaries |
| `@[.agents/rules/05_llm_architecture.md]` | VERIFIED | Four-Layer Clean Stack, prompt caching, static prefix, exact lexical quotes |
| `@[ki_god_code_prevention.md]` | VERIFIED | Modular decomposition, single responsibility, clean strategy extraction |
| `@[ki_context_enriched_decompose_verify.md]` | VERIFIED | Two-pass extraction, DAG grounding, exact physical quote anchoring |
| `@[ki_tripartite_pipeline_architecture.md]` | VERIFIED | 3-phase decoupling: Phase 1 (Compute), Phase 2 (Synthesis), Phase 3 (SDUI) |
| `@[ki_topological_engine.md]` | VERIFIED | Kahn's wave evaluation, thread-isolated cycle detection, Markov conditioning |
| `@[ki_execution_engine_protocol.md]` | VERIFIED | `ExecutionEngine` protocol, Pure Compute Engine Law, dynamic semaphore pool |
| `@[ki_zero_permissive_typing.md]` | VERIFIED | Zero naked dicts (`QGR001`), `extra='forbid'` (`QGR002`), no Tuple Hell |
| `@[ki_dumb_painter_sdui.md]` | VERIFIED | Zero client-side semantic inference, 1:1 Flutter & PDF parity, Anti-Synthetic Row |
| `@[ki_prompt_orchestration_and_matrix_evaluation.md]` | VERIFIED | Four-Layer Stack, atom aliasing (`a0`, `a1`), XML sandwich CDATA shielding |
| `@[ki_unified_matrix_scoring_strictness.md]` | VERIFIED | Continuous strictness curve, secondary fault dampening |
| `@[ki_desktop_pro_tool_studio_ux.md]` | VERIFIED | Desktop pro-tool UX, decoupled inspector modal (`CausalInspectorModal`) |
| `@[ki_shared_storage_driver_architecture.md]` | VERIFIED | FileDriver storage boundaries, report artifact isolation |
| `@[ki_dag_engine_dto_projection_rules.md]` | VERIFIED | DAG engine state boundaries, immutable DTO projection |
| `@[ki_python_314_concurrency_strictness.md]` | VERIFIED | Python 3.14 runtime, `TaskGroup` wave execution, DLQ failure recording |
| `@[ki_dual_axis_localization_architecture.md]` | VERIFIED | Axis 1 ARB client chrome, Axis 2 backend `ReportHeaderResolver` & `I18nText` |
| `@[ki_workflow_context_governance.md]` | VERIFIED | Workflow step taxonomy, `StepRule` governance, studio chaining |
| `@[ki_execution_record_ssot.md]` | VERIFIED | ExecutionRecord SSOT, trace events, FinOps telemetry |
| `@[ki_opentelemetry_logfire_observability.md]` | VERIFIED | GenAI semantic conventions, trace telemetry |
| `@[ki_llm_extraction_architecture.md]` | VERIFIED | Four-Layer static prompt compilation, exact quote verification |
| `@[ki_epic_lifecycle_workflow.md]` | VERIFIED | Epic lifecycle governance, 5-tier regression defense |
| `@[ki_synthesis_payload_compression.md]` | VERIFIED | Phase 2 synthesis payload compression, token shield |

**Audit Result:** 6 Rules verified, 20 Knowledge Items verified. 100% context coverage achieved.

---

## 3. Five-Axis System 2 Deconstruction

### Axis 1: Target Scope & Boundary (Scope Inquisitor)
- **Blast Radius:** 47 Active Target Files (9 NEW, 35 MODIFIED, 3 COMPLETED) + 3 Read-Only Reference Files across Backend and Frontend.
- **Physical Boundaries:**
  - Standalone engine implementation is strictly isolated to `backend_v2/services/orchestrator/engines/causal_discovery_engine.py`.
  - Engine dispatch is isolated to `backend_v2/services/orchestrator/engines/registry.py` and `ENGINE_REGISTRY`.
  - DTOs are isolated to `backend_v2/models/dtos/causal_discovery.py`.
  - Presentation is isolated to `SduiCausalGraphBlock`, `CausalGraphAdapter`, `ExecutiveSummaryAdapter`, `SduiCausalGraphWidget`, `CausalInspectorModal`, and Jinja2 PDF macro.
- **Scope Creep Eradication:**
  - Speculative `CausalStep` domain model subclass: **PRUNED**.
  - Persistent Neo4j / NetworkX graph database: **PRUNED**.
  - Disjoint parallel Excel worksheets ("Causal Graph", "Causal Diagnostics"): **PRUNED**.
  - Dedicated `TargetBlockType.CAUSAL_GRAPH_BLOCK` in profile order: **PRUNED** in favor of existing `EXECUTIVE_SUMMARY_BLOCK`.
  - Granular micro-toggles and `CausalDisplayMode`: **PRUNED** in favor of `visible_block_extensions`.

### Axis 2: Eradicated Duct-Tape (Duct-Tape Prosecutor - Under-Engineering Ban)
- **Eliminated Pre-Existing Technical Debt:**
  - `TwoPassAtomizer._calculate_packets`: Anonymous 3-tuples (`tuple[str, str, list[str]]`) eradicated; already encapsulated into `ChunkPacketDTO(start_block, end_block, packet_keys)` in `dag_models.py`.
  - `_resolve_execution_engine` in `dag_executor.py`: Pre-hook string checks (`"atom_flattening_hook" in step_def.pre_hooks`) and criteria block category guessing eradicated in favor of typed `ENGINE_REGISTRY[step_def.engine_type]`.
  - `LLMNodeStrategy.execute`: Duck-typing cascade (`isinstance(existing_meta, BaseModel|Mapping)`) and untyped dictionary accumulator (`meta_dict = {}`) eradicated in favor of typed `StepTraceMetadataDTO` and Protocol property `self._engine.telemetry_strategy_label`.
  - `Step.validate_step_consistency`: String literal comparisons (`self.type == "llm"`) modernized to typed `StepType.LLM` enums, and `ValueError` upgraded to `AppException(ErrorCodes.VALIDATION_FAILED)`.
  - `SlidingWindowLinker.__init__`: Constructor parameter defaults (`window_size = 4, overlap = 2`) preserved intact; causal settings injected explicitly to prevent caller parameter contamination.

### Axis 3: Approved Best Practice (Type Constitutionalist - Sovereign Target)
- **Immutable Pydantic V2:** All 8 causal DTOs (`CausalNodeDTO`, `CausalEdgeDTO`, `CausalGraphPayloadDTO`, `CausalRootCauseDiagnosisDTO`, `AntiFluffAuditDTO`, `PrescriptiveRemediationDTO`, `FairScoringBreakdownDTO`, `CausalTdaFusionResultDTO`) strictly enforce `ConfigDict(strict=True, extra="forbid", frozen=True)`.
- **Sealed Polymorphic Discriminators:** `SduiCausalGraphBlock` defines `block_type: Literal["causal_graph"] = "causal_graph"` matching Dart Freezed union `@FreezedUnionValue('causal_graph')`.
- **Theme Sovereignty:** Zero raw `Color(...)` or `Colors.*` in Flutter widgets; all styling derives dynamically from `Theme.of(context).colorScheme`, `AppSemanticColors`, and `Theme.of(context).textTheme`.
- **Exact Lexical Anchoring:** Extracted quotes validated strictly via `str.find` against indexed paragraphs `[B0]...[Bn]`. Fuzzy string matching is strictly prohibited.

### Axis 4: Pruned Over-Engineering (Complexity Slayer - 30% Deletion Test)
- **30% Deletion Question:** *"If 30% of proposed classes/functions were deleted, what gets cut and what breaks?"*
- **Cut:**
  - Standalone `CausalStep` subclass -> Reused `Step` domain model.
  - Neo4j graph storage engine -> In-memory transient `LinkedAtomGraph`.
  - Separate Causal Report tab & separate Excel worksheets -> Integrated into single executive horizon and canonical "Raw Data" sheet.
  - Dedicated display mode selector (`CausalDisplayMode`) -> Reused existing `visible_block_extensions`.
- **Preserved (Irreducible Core):**
  - Standalone `CausalDiscoveryEngine` implementing `ExecutionEngine`.
  - Typed `ENGINE_REGISTRY` mapping `EngineType`.
  - 8 Pydantic V2 DTOs capturing graph nodes, edges, root causes, remediations, and fusion states.
  - Single presentation card (`SduiCausalGraphBlock`) and decoupled inspector (`CausalInspectorModal`).

### Axis 5: Fail-Fast Proof Anchor (Incorruptible Judge - Deterministic Verification)
- **Automated Gates:**
  - `scripts/backend_audit_loop.py`: Enforces Ruff formatting, MyPy strict typing, and full Pytest execution.
  - `scripts/flutter_audit_loop.py --build`: Validates Freezed code generation and zero unrecognized keys under `disallowUnrecognizedKeys: true`.
  - `scripts/audit_flutter_theme_sovereignty.py`: Verifies zero raw hex colors, `Colors.*`, or naked `TextStyle(...)`.
  - `scripts/_ast_guardrails.py`: Enforces zero naked dicts (`QGR001`), `extra='forbid'` (`QGR002`), and Polyfactory test fixtures (`QGR029`).
  - `scripts/audit_markdown_boundaries.py`: Verifies boundary integrity and zero ambiguous documentation patterns.

---

## 4. Falsification & Red-Teaming Analysis (Anti-Happy-Path)

### Failure Mode 1: Document Starvation / Empty Extraction
- **Scenario:** The input document contains zero argumentative premises, whitespace only, or completely un-extractable text.
- **Vulnerability:** Downstream topological evaluation receives an empty graph, risking divide-by-zero errors in scoring or silent empty output in report generation.
- **Fail-Fast Defense:** `CausalDiscoveryEngine` implements pre-flight validation: if input text is empty or phase 1 extraction produces 0 nodes, it raises `AppException(ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT)` immediately. In fusion mode, if upstream discovery yields 0 nodes, `DAGExecutor` raises `AppException(ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION)`.

### Failure Mode 2: Circular Argument Deadlock
- **Scenario:** The candidate authors a circular argument chain: Premise A -> Claim B -> Conclusion C -> Premise A.
- **Vulnerability:** Standard Kahn's topological sort hangs or deadlocks in an infinite loop while waiting for in-degree to reach 0.
- **Fail-Fast Defense:** `TopologicalEvaluator` runs thread-isolated cycle detection via `asyncio.to_thread(list, nx.simple_cycles(g))`. When a cycle is detected, it terminates the topological wave loop without event loop deadlock, marks `cycle_detected=True`, flags participating nodes as `ExecutionStatus.SYSTEM_ERROR` with reason `CYCLIC_DEPENDENCY_DETECTED`, and records points deduction in `AntiFluffAuditDTO`.

### Failure Mode 3: Client Deserialization Contract Fracture (Unrecognized Keys)
- **Scenario:** Backend introduces new fields (`causal_source_step_id` on `StepRule`, `engine_type` on `NodeStrategy`) before client models are regenerated.
- **Vulnerability:** Dart models configured with `@JsonSerializable(disallowUnrecognizedKeys: true)` crash with fatal `FormatException` upon reading seed data or API payloads.
- **Fail-Fast Defense:** Phase 1 mandates Full-Duplex Serialization Parity: Dart models in `workflow.dart` and `enums.dart` are updated and generated via `flutter_audit_loop.py --build` in Phase 1 synchronously before any backend seed data or API routes expose the new fields.

### Failure Mode 4: Visual Report Layout Explosion (Unbounded Graph Rendering)
- **Scenario:** A 50-page technical paper generates 100+ argument nodes and 150+ edges. Rendering the full directed graph into the PDF report causes 10+ pages of illegible spaghetti lines, blowing past print page budgets.
- **Vulnerability:** Unusable PDF reports, rendering timeouts, memory exhaustion in WeasyPrint / Chrome headless.
- **Fail-Fast Defense:** The **Critical Causal Path Principle** strictly limits the primary report block (`SduiCausalGraphBlock`) to an executive, half-page linear error chain: `[Root Cause]` -> `[Cascading Fault]` -> `[Score Loss]`. All passing claims are summarized into a single compact metric chip (`"X other claims verified logically sound"`). Deep graph exploration is strictly decoupled into `CausalInspectorModal`.

---

## 5. Architectural Findings & Directives Summary

1. **Standalone Engine Sovereignty:** `CausalDiscoveryEngine` is a standalone `ExecutionEngine`. It does not subclass or branch inside `TDAEngine`.
2. **Single Pipeline Invariant:** Zero legacy shims, fallback branches, or dual pipelines. `_resolve_execution_engine` dispatches via typed `ENGINE_REGISTRY`.
3. **Executive Summary Unification:** Exactly one presentation point: `SduiCausalGraphBlock` integrated into `TargetBlockType.EXECUTIVE_SUMMARY_BLOCK`.
4. **Theme Sovereignty Compliance:** 100% compliance with `audit_flutter_theme_sovereignty.py`.
5. **Rectangular Atom Tabular Parity:** Canonical Excel Tab 2 enrichment and rectangular multi-row CSV streaming adhering strictly to `IMPLEMENTATION_PLAN_Logic_Matrix_Excel_and_CSV_Parity_Architecture.md`.
6. **Roadmap Isolation:** Explicitly flagged as `DISTANT FUTURE ROADMAP ONLY`. The engine remains reserved for future open-text discovery workflows and does not compromise current evaluation cores.

---

## 6. Audit Conclusion & Sign-Off

`EPIC_154_Dynamic_Causal_Discovery_Engine.md` has been thoroughly analyzed, deconstructed across all five System 2 axes, stress-tested against red-team failure modes, and verified for 100% compliance with Quorum 2026 architectural invariants, AST guardrails, and knowledge items.

**Verdict:** **APPROVED AS ARCHITECTURALLY SOUND (DISTANT FUTURE ROADMAP)**  
**Readiness:** Ready for future planning via `/tier1-planner` when scheduled on the active development roadmap.
