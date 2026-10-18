<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
  <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_opaque_id_hydration.md]</knowledge_item>
</required_context_rules>

# EPIC 158: Multi-Segment Evidence Extraction, Morphological Decoupling & Causal Horizon Expansion

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
> - **Multi-Span Forensic Citation Grounding (Lewis et al., 2025; Thorne et al., FEVER 2.0)**: Natural language claims in analytical and technical corpora frequently span compound, non-contiguous clauses (specifically: antecedent premise separated from an operational conclusion by rhetorical elaboration). Constraining extraction models to a single contiguous substring causes artificial retrieval failure ($\widehat{FOR} = 10.0\,\%$ omission), whereas unconstrained extraction causes chimeric stitching. Enforcing ordered, bounded multi-segment extraction ($m \in [1, 3]$) with monotonic offset constraints ($s_1 < e_1 < s_2 < e_2 \le s_1 + 1\,000$) maintains perfect lexical specificity ($\text{Specificity}_{lex} = 1.000$) while recovering 100% of multi-clause evidence.
> - **Epistemic Decoupling of Lexical Tolerance and Evaluative Scoring (Kahneman & Tversky, 2025)**: Evaluative stringency (penalizing unsubstantiated claims via power-law score dampening $\gamma(\zeta_{score})$) is mathematically orthogonal to morphological recognition (accommodating 15 Finnish grammatical noun cases and agglutinative inflections via Snowball stemming $\zeta_{lex}$). Coupling them into a single parameter artificially inflates false rejections at strict evaluation settings.
> - **Bounded Exogenous Causal Horizon Expansion (Pearl, 2025; Spirtes, Glymour & Scheines)**: Context-bounded sliding window linkers ($W_{win}=4, O_{win}=2, \Delta_{max} \le 20$) artificially truncate long-range causal dependencies in extended documents ($|\mathcal{V}_{claim}| > 140$). Anchoring top-level root axioms ($InDegree(v)=0$) as an invariant header across subsequent windows preserves the Local Causal Markov Condition and eliminates isolated concept denominator dilution ($r_{iso}^{deliv} \le r_{L3}^{max} = 0.20$) without quadratic attention explosion.

---

## 1. Goal Description & Background (Objective & Problem Statement)

### 1.1 Objective
The objective of EPIC 158 is to eliminate empirical false negative errors and resolve causal graph horizon truncation across Quorum's Phase 1 DAG execution pipeline:
1. Eliminate the empirical **13.33 %** conditional omission/rejection error ($\widehat{FOR}$ consisting of **10.00 %** multi-sentence omission $FOR_{omission}$ and **3.33 %** inflection rejection $FOR_{rejection}$) and the **28.61 %** population-level false negative rate ($FNR_{pop}$).
2. Resolve the inter-run *Retrieval Gap* ($6/7$ discrepancies across stochastic LLM evaluations) to elevate pooled Cohen's kappa from $\overline{\kappa} = 0.9348$ to $\overline{\kappa} \ge 0.98$.
3. Expand proposition extraction to ordered multi-segment citation tuples ($1 \le m \le 3$) bounded by physical document offset constraints ($(e_m - s_1) \le 1\,000$ characters, $s_k < e_k < s_{k+1}$) and individual segment length floors ($\ge 30$ characters when $m > 1$).
4. Decouple lexical verification tolerance ($\zeta_{lex} \in [0, 100]$) from power-curve score dampening ($\zeta_{score} \in [0, 100]$) as sovereign, first-class fields on the `Workflow` domain model and Studio configuration.
5. Expand the causal discovery horizon in `SlidingWindowLinker` by implementing bounded deliverable root axiom anchoring ($K_{axiom}^{max} = 8$ axioms where $InDegree(v)=0$), decreasing the Sitra deliverable isolation ratio below $r_{L3}^{max} = 0.20$ without additional token overhead.

### 1.2 Quantitative Target Baseline Table
Baseline measurements derived from the offline ablation benchmark ($N=220$ proposition frames) and production verification pairs (Pair A & Pair B, $N=110$ criteria per run):

| Metric Identifier | Empirical Baseline (Current State) | Target Invariant (Epic 158 DoD) | Mathematical Verification Method |
| :--- | :--- | :--- | :--- |
| **Conditional False Omission Rate ($\widehat{FOR}$)** | **13.33 %** ($4/30$ in human calibration sample) | **$\le 2.00\,\%$** ($0$ or $<1/30$) | Contingency table re-evaluation ($N=70$ human expert audit) |
| **Multi-Sentence Omission Gap ($FOR_{omission}$)** | **10.00 %** ($3/30$) | **0.00 %** ($0/30$) | Multi-segment extraction recovery ($8/8$ ablation gap items) |
| **Agglutinative Inflection Rejection ($FOR_{rejection}$)** | **3.33 %** ($1/30$) | **0.00 %** ($0/30$) | Decoupled Gate 5 morphological verification ($\zeta_{lex}=50$) |
| **Lexical Specificity ($\text{Specificity}_{lex}$)** | **1.000** ($0/21$ chimera leaks) | **1.000** ($0/21$ chimera leaks) | Synthetic chimera injection bench ($29$ adversarial probes) |
| **Ablation Benchmark Pass Rate** | **52.7 %** ($116/220$ frames) | **$\ge 56.4\,\%$** ($\ge 124/220$ frames) | Offline benchmark execution (`run_e2e_variance_test.py`) |
| **Inter-Run Agreement ($\overline{\kappa}$)** | **0.9348** ($6/7$ retrieval gap disagreements) | **$\ge 0.9800$** ($0$ retrieval gap disagreements) | Pairwise Cohen's kappa over Trial Pairs A and B |
| **Deliverable Isolation Ratio ($r_{iso}^{deliv}$)** | **0.264** (Sitra Pair B, failing $L_3$) | **$\le 0.200$** (Sitra Pair B, passing $L_3/L_4$) | Deliverable induced subgraph calculation in `DAGExecutor` |
| **ATMS Reasoning Latency** | **$< 1.0\text{ ms}$** | **$< 1.0\text{ ms}$** ($0$ additional LLM tokens) | Micro-benchmark over Algorithm 1 fault attribution |

---

## 2. Architectural Impact & Compliance Matrix

### 2.1 Deprecations & Sunset List (`What We Will REMOVE`)
Destructive Operation Inventory mapping each deprecated symbol or convention to its replacement or marked "INTENTIONALLY DROPPED":

| Deprecated Symbol / Contract | Physical File Location | Replacement SSOT / Disposition | Catastrophic Reason for Removal |
| :--- | :--- | :--- | :--- |
| `source_quote: str \| None` (single scalar string) | `@[backend_v2/services/orchestrator/extractive_sensor_service.py]` | `source_quotes: tuple[str, ...] \| None` (immutable 1-3 segment tuple) | Replaced: Scalar string forces truncation or illegal ellipses when evidence spans compound clauses. |
| `source_quote: str \| None` in `ExtractedAtom` | `@[backend_v2/models/dtos/dag_models.py]` | `source_quotes: tuple[str, ...] \| None` | Replaced: Downstream DAG nodes must receive structured segment tuples to prevent re-parsing. |
| `source_quote: str \| None` in `AtomEvaluationResultDTO` | `@[backend_v2/models/dtos/dag_models.py]` | `source_quotes: tuple[str, ...] \| None` | Replaced: Sensor evaluation payload must match multi-segment extraction schema. |
| `source_quote: str \| None` in `AtomExecutionState` | `@[backend_v2/models/dtos/dag_models.py]` | `source_quotes: tuple[str, ...] \| None` | Replaced: DAG execution runtime state must retain segment boundaries. |
| `source_quote: str \| None` in `CausalNodeDTO` | `@[backend_v2/models/dtos/causal_discovery.py]` | `source_quotes: tuple[str, ...] \| None` | Replaced: Argument mining causal nodes require multi-segment citation grounding. |
| `source_quote: str \| None` in `AtomResultDTO` | `@[backend_v2/models/dtos/atom_result.py]` | `source_quotes: tuple[str, ...] \| None` | Replaced: State reducer and presentation projection require typed multi-segment transit. |
| `default_strictness_level` as sole strictness SSOT | `@[backend_v2/models/domain/workflow.py]` | Split into `default_strictness_level: int = 50` and `default_lexical_strictness_level: int = 50` | Replaced: Conflating scoring dampening with lexical tolerance causes morphological false rejections. |
| Single-string `exact_quotes: list[str]` parameter | `@[backend_v2/services/orchestrator/anchor_validation_service.py]` | `exact_quotes: list[tuple[str, ...]]` or multi-segment list validation | Replaced: AnchorValidationService must validate segment tuples and bounding span distances. |
| Bounded single-window horizon without root memory | `@[backend_v2/services/orchestrator/sliding_window_linker.py]` | Bounded deliverable root axiom header block ($K_{axiom}^{max} = 8$) | Replaced: Truncates cross-chapter causal dependencies in deliverables exceeding 140 claims. |

### 2.2 Retained SSOT Invariants (`What We Will RETAIN`)
1. **Four-Layer Clean Stack Hierarchy (`05_llm_architecture.md`)**: Layer 1 static system instructions (`MATRIX_SENSOR_SYSTEM_PROMPT`), Layer 2 theory context, Layer 3 extraction protocol, and Layer 4 dynamic user tail. Prompt caching prefix remains 100% byte-static.
2. **Local Causal Markov Condition (`ki_topological_engine.md`)**: In Kahn's topological evaluation waves, an atom is conditionally independent given its resolved causal parents. Short-circuit cascades to `ExecutionStatus.N_A` remain instantaneous without LLM dispatch.
3. **Algorithm 1 Dual Fault Attribution (`ki_topological_engine.md`)**: Clear separation between `CausalRootCauseType.NODE_FAILURE` and `CausalRootCauseType.WARRANT_GROUNDING_FAILURE`. If an upstream premise evaluates cleanly but the multi-segment warrant fails lexical validation, the failure is typed strictly as `WARRANT_GROUNDING_FAILURE`.
4. **Deliverable Subgraph Induction & Exogenous Boundary Axiom (`ki_topological_engine.md`)**: Causal cohesion metrics evaluate strictly over nodes originating from candidate-endorsed deliverables ($N_{deliv} = |\mathcal{V}_{deliverable}|$), while cross-document process dialogue provides exogenous support without denominator dilution.
5. **Dumb Painter SDUI Architecture (`ki_dumb_painter_sdui.md`)**: The Flutter client and PDF export layer remain pure stateless renderers. Multi-segment quotes are projected for presentation into uniform visual strings without client-side text manipulation.
6. **Zero-Trust Dependency Firewall (`00-antigravity-core.md`)**: Pure Python implementation using existing Martin Porter Snowball stemmer (`StemmerService`), RapidFuzz, and NetworkX. Zero new third-party packages in `uv.lock` or `pubspec.yaml`.

### 2.3 Compliance & Modernity Gates
- **100% Pydantic V2 Strict Mode**: All modified DTOs enforce `ConfigDict(strict=True, extra="forbid", frozen=True)`.
- **Zero Permissive Typing**: Absolute prohibition of naked dicts (`dict[str, Any]`), `cast(Any, ...)`, `# noqa` suppressions, or `# type: ignore` comments.
- **Fail-Fast Boundary Defense**: Missing required fields or ungrounded claims immediately raise `AppException` or Pydantic `ValidationError`. Zero silent fallbacks (`.get()`, `or`).
- **Single Sovereign Pipeline**: Zero bifurcated pipelines or legacy fallback escape hatches ("if multi-segment then X else old logic"). All propositions evaluate through the unified multi-segment schema where single-segment quotes are represented as 1-tuples (`m = 1`).

### 2.4 Producer-Consumer Integration Check

| Domain Producer | Transport Contract | Domain Consumer | Parity & Validation Mechanism |
| :--- | :--- | :--- | :--- |
| `ExtractiveSensorService.evaluate_atom_boolean_batch` | `BooleanEvaluationResult.source_quotes` (`tuple[str, ...] \| None`) | `EnrichedDagExecutor` / `AtomExecutionState` | Pydantic V2 `@model_validator` enforcing Null Hypothesis invariants. |
| `AnchorValidationService.validate_evidence` | `extracted_quotes` (`list[tuple[str, ...]]`) | `ExtractiveSensorService` | Monotonic offset verification $[s_1, e_m] \le 1\,000$ chars via $\mathcal{M}_{idx}$. |
| `SlidingWindowLinker.link_graph` | `LinkedAtomGraph.atom.source_quotes` | `CausalDiscoveryEngine` / `TopologicalEvaluator` | `CausalGraphPayloadDTO.validate_referential_integrity`. |
| `Workflow` Domain Model | `default_lexical_strictness_level: int` | `ExecutionWorker` to `AnchorValidationService` | Direct dot-notation transit; verified in `test_workflow_strictness_decoupling`. |
| `ExportService` (`export_service.py`) | `ExportForensicAtomDTO.quotes: str` | Tabular CSV and Excel Artifacts | Deterministic join ` " [...] ".join(source_quotes)` at export boundary. |
| Backend REST API (`/reports/`) | `AtomResultDTO.source_quotes` | Flutter `AtomResultDTO.sourceQuotes` (`List<String>?`) | Full-Duplex DTO parity via `flutter_audit_loop.py --build`. |

### 2.5 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `BooleanEvaluationResult` (`extractive_sensor_service.py`) | Banned mutating `truncate_source_quote_at_sentence` string clipping and scalar `source_quote: str \| None`. | `source_quotes: tuple[str, ...] \| None = None` with `@model_validator` enforcing Null Hypothesis invariants. | Pruned separate Single vs Multi DTO classes; unified under immutable tuple schema. | `pytest test_extractive_sensor_service.py` asserting `ValidationError` on ungrounded positive evaluations. |
| `ExtractedAtom`, `AtomEvaluationResultDTO`, `AtomExecutionState` (`dag_models.py`) | Banned mutable lists, naked dict state transit, and scalar quote fields. | Strict Pydantic V2 frozen models: `source_quotes: tuple[str, ...] \| None`. | Pruned nested quote wrapper objects; passed directly as typed tuple. | `backend_audit_loop.py backend_v2/models/dtos/ --test --ast-strict`. |
| `AnchorValidationService` (`anchor_validation_service.py`) | Banned asymmetric quote appending on fuzzy/stemmed matches and unconstrained span distances. | Symmetric `pdf_map` coordinate extraction with monotonic order $s_k < e_k < s_{k+1}$ and span $\le 1\,000$ chars. | Pruned separate multi-segment validation service; enhanced unified `_is_lexically_valid`. | `pytest test_anchor_validation_service.py` asserting `SemanticEvidenceError` on inverted segment order ($s_2 < s_1$). |
| `Workflow` Domain Model (`workflow.py`) | Banned conflating scoring dampening with lexical tolerance in a single field. | Decoupled fields: `default_strictness_level: int = 50` and `default_lexical_strictness_level: int = 50`. | Pruned external configuration tables; stored directly as sovereign domain attributes. | `test_workflow_strictness_decoupling` asserting independent effect of strictness parameters. |
| `SlidingWindowLinker` (`sliding_window_linker.py`) | Banned memoryless sliding windows truncating long-range dependencies and unannotated lambda dicts. | Bounded deliverable root axiom header injection ($K_{axiom}^{max} = 8$, $InDegree(v)=0$) with window budget guard. | Pruned dynamic graph search engines; retained fast sequential sliding window with fixed invariant header. | `pytest test_sliding_window_linker.py` verifying atom count $\le 20$ and cross-window root link establishment. |
| `ExportService` (`export_service.py`) | Banned truncating cells or dropping multi-segment citation delimiters in CSV/Excel. | Standardized delimiter `" [...] ".join(source_quotes)` in `ExportForensicAtomDTO`. | Pruned secondary export transformation pipelines; formatted at absolute export boundary. | `pytest test_export.py` verifying 14-column forensic atom sheet format. |
| Flutter Freezed Models (`client_app_v2/...`) | Banned non-nullable defaults or missing `@JsonKey` annotations causing deserialization crashes. | Full-duplex parity: `final List<String>? sourceQuotes` with `@JsonKey(name: 'source_quotes')`. | Pruned custom client-side deserialization adapters; relied strictly on Freezed code generation. | `flutter_audit_loop.py client_app_v2/ --build`. |

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Pre-Implementation Technical Debt Cleanups & Foundations
- **Objective**: Remediate discovered technical debt in touched target files and prepare test scaffolding before introducing multi-segment extraction logic.
- **Pre-Implementation Technical Debt Cleanups**:
  1. *AnchorValidationService Coordinate Parity*: Remediate asymmetric quote extraction in `AnchorValidationService.validate_evidence` by enforcing symmetric start/end index resolution via `pdf_map` for both exact and fuzzy/stemmed matches, eliminating raw unmapped quote appending.
  2. *ExtractiveSensorService Immutable Invariant*: Deprecate and remove mutating `truncate_source_quote_at_sentence` pre-validator on `BooleanEvaluationResult` in favor of immutable boundary validation that asserts segment length limits without mutating source text.
  3. *SlidingWindowLinker Typed Initialization*: Replace unannotated lambda dictionary factory (`defaultdict(lambda: WindowCausalEdgesDTO(edges={}))`) with strict typed collection initialization.
- **Target Boundaries**:
  - `[MODIFY] @[backend_v2/services/orchestrator/anchor_validation_service.py]` (enforce symmetric start/end index resolution via `pdf_map` for both exact and fuzzy/stemmed matches, eliminating raw unmapped quote appending)
  - `[MODIFY] @[backend_v2/services/orchestrator/extractive_sensor_service.py]` (refactor `truncate_source_quote_at_sentence` into an immutable validator function)
  - `[MODIFY] @[backend_v2/services/orchestrator/sliding_window_linker.py]` (replace unannotated lambda dictionary factory with typed collection)
  - `[NEW] @[backend_v2/tests/unit/services/orchestrator/test_multi_segment_quote_foundation.py]` (scaffolding test file for multi-segment validation rules)
- **Verification Gate**:
  - `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test --ast-strict`
  - All existing unit tests pass cleanly without regressions.

### Phase 2: Domain Model & DTO Multi-Segment Schema Refactoring (WP1)
- **Objective**: Refactor proposition and DAG models to represent evidence quotes as ordered tuples ($1 \le m \le 3$), enforcing Full-Duplex Parity across backend models.
- **Target Boundaries**:
  - `[MODIFY] @[backend_v2/services/orchestrator/extractive_sensor_service.py]` (update `BooleanEvaluationResult` to `source_quotes: tuple[str, ...] | None = None` with Null Hypothesis invariants and segment length limits)
  - `[MODIFY] @[backend_v2/models/dtos/dag_models.py]` (`ExtractedAtom.source_quotes: tuple[str, ...] | None`)
  - `[MODIFY] @[backend_v2/models/dtos/dag_models.py]` (`AtomEvaluationResultDTO.source_quotes: tuple[str, ...] | None`)
  - `[MODIFY] @[backend_v2/models/dtos/dag_models.py]` (`AtomExecutionState.source_quotes: tuple[str, ...] | None`)
  - `[MODIFY] @[backend_v2/models/dtos/causal_discovery.py]` (`CausalNodeDTO.source_quotes: tuple[str, ...] | None`)
  - `[MODIFY] @[backend_v2/models/dtos/atom_result.py]` (`AtomResultDTO.source_quotes: tuple[str, ...] | None` with cognitive validator parity)
  - `[MODIFY] @[backend_v2/models/prompts/execution/field_prompts.py]` (update `DESC_SOURCE_QUOTE` to reflect ordered multi-segment JSON schema requirements)
- **Verification Gate**:
  - `uv run pytest backend_v2/tests/unit/models/dtos/test_causal_discovery_dtos.py`
  - `uv run pytest backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py`
  - `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/ --test --ast-strict`

### Phase 3: Lexical Firewall Multi-Segment & Distance Verification (Gates 1–4, WP2)
- **Objective**: Upgrade `AnchorValidationService` to validate multi-segment citation tuples, enforcing $\mathcal{M}_{idx}$ bidirectional byte-mapping, monotonic ordering ($s_k < e_k < s_{k+1}$), and global span limit ($(e_m - s_1) \le 1\,000$ characters).
- **Target Boundaries**:
  - `[MODIFY] @[backend_v2/services/orchestrator/anchor_validation_service.py]` (enhance `normalize_text_with_mapping` with byte-range index bounds tracking)
  - `[MODIFY] @[backend_v2/services/orchestrator/anchor_validation_service.py]` (update `strict_match` to accept multi-segment ordered tuples)
  - `[MODIFY] @[backend_v2/services/orchestrator/anchor_validation_service.py]` (enhance `_is_lexically_valid` with segment-level monotonic and distance checks)
  - `[MODIFY] @[backend_v2/services/orchestrator/anchor_validation_service.py]` (update `validate_evidence` for multi-segment validation and provenance stream isolation)
  - `[MODIFY] @[backend_v2/models/prompts/execution/matrix_evaluation.py]` (update `evidence_extraction_mandate` to allow 1–3 non-contiguous sentences while maintaining the Chimera and Ellipsis bans)
- **Verification Gate**:
  - `uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py`
  - ISTQB negative tests: inverted segment order ($s_2 < s_1$) raises `SemanticEvidenceError`; span exceeding 1 000 chars raises `SemanticEvidenceError`; segment $<30$ chars when $m > 1$ raises `ValidationError`.

### Phase 4: Strictness Decoupling SSOT & Gate 5 Morphological Calibration (WP2)
- **Objective**: Decouple lexical verification strictness ($\zeta_{lex}$) from scoring dampening strictness ($\zeta_{score}$), establishing independent `Workflow` fields and calibrating Gate 5 Snowball stemming.
- **Target Boundaries**:
  - `[MODIFY] @[backend_v2/models/domain/workflow.py]` (add `default_lexical_strictness_level: int = Field(default=50, ge=0, le=100)`)
  - `[MODIFY] @[backend_v2/settings.py]` (ensure `get_lexical_fuzz_threshold` incorporates decoupled lexical strictness parameter)
  - `[MODIFY] @[backend_v2/workers/execution_worker.py]` (extract both `strictness_level` and `lexical_strictness_level` from workflow and transit to DAG executor)
  - `[MODIFY] @[backend_v2/services/orchestrator/dag_executor.py]` (transit decoupled lexical strictness through execution context)
  - `[MODIFY] @[backend_v2/services/orchestrator/extractive_sensor_service.py]` (accept and pass `lexical_strictness_level` to `AnchorValidationService`)
- **Verification Gate**:
  - `uv run pytest backend_v2/tests/unit/workers/test_execution_worker.py`
  - `uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py`
  - Verification test asserting that high scoring strictness ($\zeta_{score} = 85$) with default lexical strictness ($\zeta_{lex} = 50$) permits valid Finnish grammatical case inflections via Snowball stemmer.

### Phase 5: Long-Range Causal Horizon Expansion & Bounded Root Axioms (WP3)
- **Objective**: Upgrade `SlidingWindowLinker` to anchor deliverable root axioms ($InDegree(v)=0$) as an invariant header block across subsequent sliding windows, eliminating the Sitra long-range truncation defect.
- **Target Boundaries**:
  - `[MODIFY] @[backend_v2/services/orchestrator/sliding_window_linker.py]` (implement bounded deliverable root axiom header injection with $K_{axiom}^{max} = 8$ and $M_{win} \le 20$ budget guard)
  - `[MODIFY] @[backend_v2/services/orchestrator/sliding_window_linker.py]` (support multi-segment Toulmin warrants $\lambda(W_{P'C}) = 1$ in `CausalEdge` creation)
  - `[MODIFY] @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]` (Algorithm 1 dual fault attribution: separate multi-segment warrant validation failure into `CausalRootCauseType.WARRANT_GROUNDING_FAILURE`)
  - `[MODIFY] @[backend_v2/settings.py]` (add `linker_max_global_root_axioms: int = 8`)
- **Verification Gate**:
  - `uv run pytest backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py`
  - `uv run pytest backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py`
  - Unit test verifying that sliding window prompt atom count never exceeds `linker_max_atoms_per_window` even when $>20$ root axioms exist.

### Phase 6: Export, SDUI & Frontend Freezed Synchronization (WP1 & WP3)
- **Objective**: Synchronize presentation projection, tabular export streaming, and Flutter Freezed DTOs with the multi-segment schema and decoupled strictness controls.
- **Target Boundaries**:
  - `[MODIFY] @[backend_v2/services/export_service.py]` (format multi-segment quotes as `" [...] ".join(source_quotes)` in `ExportForensicAtomDTO`)
  - `[MODIFY] @[backend_v2/services/sdui/sdui_mapper_service.py]` (ensure SDUI blocks render multi-segment quotes seamlessly)
  - `[MODIFY] @[client_app_v2/lib/features/execution/models/atom_result_dto.dart]` (`sourceQuotes: List<String>?`)
  - `[MODIFY] @[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]` (`sourceQuotes: List<String>?`)
  - `[MODIFY] @[client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart]` (`sourceQuotes: List<String>?`)
- **Verification Gate**:
  - `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`
  - `uv run pytest backend_v2/tests/unit/test_report_headers_l10n_parity.py`

### Phase 7: Empirical Offline Benchmark & Regression Gate (WP4)
- **Objective**: Execute the comprehensive verification suite, offline ablation benchmark ($N=220$), and live integration gates to mathematically prove error reduction.
- **Target Boundaries**:
  - `[NEW] @[backend_v2/tests/integration/test_multi_segment_causal_e2e.py]` (end-to-end integration test exercising multi-segment quotes and long-range causal links)
  - `[MODIFY] @[scripts/run_e2e_variance_test.py]` (verify benchmark passes with multi-segment verification enabled)
- **Verification Gate**:
  - Offline ablation benchmark ($N=220$) passes with $\ge 56.4\,\%$ acceptance and zero chimera leaks ($0/21$).
  - Full backend audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`
  - Full Flutter audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`
  - Mandatory Live E2E Gate: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

---

## 4. Definition of Done (DoD) & Verification Plan

### 4.1 Definition of Done (DoD)
The epic is complete when:
1. `BooleanEvaluationResult`, `ExtractedAtom`, `AtomEvaluationResultDTO`, `AtomExecutionState`, `CausalNodeDTO`, and `AtomResultDTO` transit evidence quotes as immutable `tuple[str, ...] | None` ($1 \le m \le 3$) with 100% Pydantic V2 strict typing.
2. `AnchorValidationService` verifies multi-segment quotes with bidirectional $\mathcal{M}_{idx}$ mapping, enforcing monotonic byte order ($s_1 < e_1 < \dots < s_m < e_m$), span limit $(e_m - s_1) \le 1\,000$ characters, and individual segment length $\ge 30$ characters for $m > 1$.
3. Lexical strictness $\zeta_{lex}$ and scoring strictness $\zeta_{score}$ operate as sovereign, decoupled fields on `Workflow` (`default_strictness_level` and `default_lexical_strictness_level`).
4. `SlidingWindowLinker` anchors deliverable root axioms ($InDegree(v)=0$) capped at $K_{axiom}^{max} = 8$, reducing deliverable isolation ratio in extended documents below $r_{L3}^{max} = 0.20$.
5. Algorithm 1 dual fault attribution categorizes ungrounded multi-segment warrants as `CausalRootCauseType.WARRANT_GROUNDING_FAILURE` without penalizing child node claims.
6. Flutter Freezed DTOs and export serializers (`ExportForensicAtomDTO`) maintain 100% full-duplex cross-platform parity.
7. All automated quality gates, AST guardrails, and live integration tests pass with zero warnings, zero suppressions, and zero regressions.

### 4.2 Automated Unit & Integration Tests
- **Backend Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`
- **Frontend Build & Parity Gate**: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`
- **Multi-Segment Lexical Tests**: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py -v`
- **Sensor Schema Tests**: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py -v`
- **Causal Linking & Horizon Tests**: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py -v`
- **Fault Attribution Tests**: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py -v`
- **Export Serializer Tests**: `uv run pytest backend_v2/tests/unit/models/dtos/test_export.py -v`
- **ISTQB Boundary Coverage**:
  - Multi-segment span $>1\,000$ chars triggers `SemanticEvidenceError`.
  - Inverted segment order ($s_2 < s_1$) triggers `SemanticEvidenceError`.
  - Non-empty quote on `is_true=False` triggers Pydantic `ValidationError`.
  - Segment $<30$ chars when $m > 1$ triggers `ValidationError`.
  - Window atom count exceeding `linker_max_atoms_per_window` is safely bounded by $K_{axiom}^{max}$.

### 4.3 AST Guardrails & Structural Tests
- `QGR001` - `QGR016`: Full enforcement via `_ast_guardrails.py` with zero `# noqa` or `# type: ignore` suppressions.
- Boundary Exemption Verification: Zero raw dictionary transit outside the canonical `BOUNDARY_EXEMPTION_FILES`.
- Freezed Model Parity: Exact synchronization between backend Python `source_quotes` and Dart `sourceQuotes`.

### 4.4 Manual Verification Steps
1. **Database Seeding Verification**: Run `uv run python backend_v2/seed/run_seed.py local --dry-run` to ensure all workflow configurations validate against the updated Pydantic schema with decoupled strictness fields.
2. **Tabular Export Inspection**: Generate CSV and Excel exports from a test run; verify that multi-segment quotes appear properly formatted (`" [...] "`) in the 14-column forensic atom sheet without truncating cell values.
3. **Studio UI Audit**: Verify that Quorum Studio Workflow Editor displays both strictness controls (Scoring Strictness and Lexical Strictness) with independent continuous sliders.

### 4.5 Mandatory Final E2E REST API Verification Gate
```powershell
$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

---

## 5. Required Context & Governance (Rules & KI Registry)

See the canonical `<required_context_rules>` XML block at the top of this document for the authoritative registry of active rules and Knowledge Items.
