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
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
</required_context_rules>

# SYSTEM 2 ARCHITECTURAL AUDIT REPORT: EPIC 158
**Title**: Multi-Segment Evidence Extraction, Morphological Decoupling & Causal Horizon Expansion  
**Epic Document**: `@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]`  
**Target Epic ID**: EPIC 158  
**Auditor**: Principal Enterprise Architect & System Red Team  
**Audit Tier**: Tier 0 (Epic Research, Falsification & In-Place Hardening)  
**Status**: APPROVED & HARDENED WITH MANDATORY ARCHITECTURAL AMENDMENTS  

---

## 1. Executive Summary & Root Cause Analysis

### 1.1 The Core Problem & Quantitative Baseline
Empirical validation of Quorum's Phase 1 DAG pipeline across an offline ablation benchmark ($N=220$ proposition frames) and production verification pairs revealed two critical architectural bottlenecks:
1. **The 13.33 % Conditional False Omission Rate ($\widehat{FOR}$)**: In human expert calibration, 13.33% of valid analytical claims were erroneously omitted or rejected. Deconstruction revealed this error consists of:
   - **10.00 % Multi-Sentence Omission Gap ($FOR_{omission}$)**: Legitimate claims where the causal premise and operational conclusion span non-contiguous clauses within the same section. Because `source_quote` was restricted to a single unbroken substring, LLM extractors either omitted the evidence entirely or attempted illegal ellipse splicing (`...`), which was rejected Fail-Fast by `AnchorValidationService`.
   - **3.33 % Agglutinative Inflection Rejection ($FOR_{rejection}$)**: Valid Finnish grammatical case inflections rejected at high evaluation strictness because lexical verification tolerance ($\zeta_{lex}$) was coupled 1:1 with power-curve scoring dampening ($\zeta_{score}$).
   - **28.61 % Population False Negative Rate ($FNR_{pop}$)**: Resulting in artificial suppression of candidate competence scores and high inter-run variance ($\overline{\kappa} = 0.9348$, 6/7 retrieval gap disagreements).
2. **Long-Range Causal Horizon Truncation ($r_{iso}^{deliv} = 0.264$)**: In extended documents ($|\mathcal{V}_{claim}| > 140$), `SlidingWindowLinker`'s context-bounded windowing ($W_{win}=4, O_{win}=2$) caused later deliverable chapters to lose visibility of initial root axioms ($InDegree(v)=0$). In the Sitra verification trial, deliverable isolated concept ratio reached $0.264$, exceeding the $r_{L3}^{max} = 0.20$ threshold and causing false failure on BARS Level 3/Level 4 argument cohesion.

### 1.2 Architectural Root Cause
- **Root Cause A (Scalar Evidence Contract)**: The SSOT DTO contract `source_quote: str | None` enforced scalar representation. Natural language analytical reasoning inherently exhibits discontinuous rhetorical structure (elaborative subclauses separating premise and consequence).
- **Root Cause B (Strictness Coupling)**: `Workflow.default_strictness_level` conflated two mathematically orthogonal concerns: epistemic stringency (power-law scoring dampening $\gamma(\zeta_{score})$) and morphological recognition tolerance ($\zeta_{lex}$).
- **Root Cause C (Memoryless Window Horizon)**: `SlidingWindowLinker` advanced across chunk sequences without retaining global root axioms, breaking the long-range transitive closure of the argument DAG.

---

## 2. Panel of Architects Evaluation & Discovered Scope / Technical Debt Gaps

### 2.1 Global System Architect
- **Invariant Compliance**: The design strictly adheres to the Single Sovereign Pipeline invariant. Single-segment quotes are unified as 1-tuples (`m = 1`), eliminating bifurcated pipelines or legacy escape hatches.
- **Fail-Fast Defense**: Multi-segment extraction enforces monotonic byte-index order ($s_1 < e_1 < \dots < s_m < e_m$), span limits ($(e_m - s_1) \le 1\,000$ chars), and segment length floors ($\ge 30$ chars when $m > 1$). Violations immediately raise `SemanticEvidenceError` or `ValidationError`.
- **Lexical Specificity**: Synthetic chimera injection benchmarks confirm zero chimera quote leaks ($\text{Specificity}_{lex} = 1.000$).

### 2.2 Backend & Data Architect
- **Pydantic V2 Strictness**: All modified DTOs (`BooleanEvaluationResult`, `PreFlightResult`, `ExtractedAtom`, `AtomEvaluationResultDTO`, `AtomExecutionState`, `CausalNodeDTO`, `AtomResultDTO`, `HydratedAtomDTO`, `EvaluatedAtomDTO`, `ReducedAtomDTO`, `QuoteEvidenceDTO`) enforce `ConfigDict(strict=True, extra="forbid", frozen=True)`.
- **Tuple Immutability**: Quotes transit as `tuple[str, ...] | None`, preventing in-place mutation and ensuring thread-safe immutability across concurrent topological evaluation waves.
- **Root Axiom Budgeting**: Deliverable root axioms are capped at $K_{axiom}^{max} = 8$, maintaining deterministic prompt window sizes without exceeding `linker_max_atoms_per_window`.

### 2.3 SDUI & Frontend Architect
- **Dumb Painter Parity**: The Flutter client and PDF export layer remain 100% stateless consumers. Multi-segment quotes are projected for presentation into uniform visual strings (`" [...] ".join(source_quotes)`) without client-side text manipulation.
- **Freezed Model Parity**: Flutter Freezed models (`AtomResultDTO`, client causal discovery models, `HydratedAtomDTO`, `QuoteEvidenceDto`) map `source_quotes` cleanly to `List<String>?` via `@JsonKey(name: 'source_quotes')`.
- **Studio Dual-Slider Integration**: Quorum Studio Workflow Editor exposes both `default_strictness_level` and `default_lexical_strictness_level` as independent continuous sliders in the Rigor tab (`Icons.balance`).

### 2.4 AI & Orchestration Architect
- **Four-Layer Clean Stack & Prefix Caching**: Prompt instructions remain 100% byte-static in Layer 1 (`MATRIX_SENSOR_SYSTEM_PROMPT`). Dynamic segment parameters reside at the user tail. Prompt caching prefix hit rate is 100% preserved.
- **Zero Additional API Calls**: Phase 1 DAG execution groups atoms into batched chunks (`sensor_batch_size: 15`). Multi-segment quote extraction requires 0 additional LLM calls and 0 additional network latency.
- **Algorithm 1 Dual Fault Attribution**: Ungrounded multi-segment warrants are typed strictly as `CausalRootCauseType.WARRANT_GROUNDING_FAILURE`, ensuring parent premises and downstream children are not unfairly double-penalized.

### 2.5 Discovered Scope & Technical Debt Gaps (Resolved via In-Place Hardening)
1. **Duplicate Epic File Elimination (SSOT Enforcement)**:
   - *Problem*: The repository previously contained both `@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]` and a duplicate file.
   - *Action*: `[DELETE] @[docs/epic/EPIC_MULTI_SEGMENT_EVIDENCE_AND_CAUSAL_HORIZON.md]` has been executed, enforcing a single authoritative SSOT document.
2. **Missing 1-Hop Producers & Consumers of `source_quote`**:
   - *Blackboard Models*: `@[backend_v2/models/domain/blackboard.py]` (`DraftExtractedAtom.source_quote` refactored to `source_quotes: tuple[str, ...] | None` with `coerce_source_quotes_tuple` and Null Hypothesis validator parity).
   - *Sensor Pre-Flight*: `@[backend_v2/services/orchestrator/extractive_sensor_service.py]` (`PreFlightResult.source_quote` refactored to `source_quotes: tuple[str, ...] | None`).
   - *Matrix Reduction & Synthesis*: `@[backend_v2/models/dtos/atom_evaluation.py]` (`ReducedAtomDTO.source_quote` refactored to `source_quotes: tuple[str, ...] | None`), and `@[backend_v2/services/orchestrator/matrix_reducer.py]` (updated to pass `source_quotes=atom.source_quotes` in line 216).
   - *Scorecard & Hydration*: `@[backend_v2/models/dtos/atom_result.py]` (`HydratedAtomDTO`, `EvaluatedAtomDTO`), `@[backend_v2/models/dtos/quote_evidence.py]` (`QuoteEvidenceDTO`), `@[backend_v2/models/dtos/matrix_scorecard.py]` (`ScorecardAtomDTO.exact_quotes`), `@[backend_v2/services/orchestrator/result_projector.py]`, and `@[backend_v2/services/orchestrator/state_reducer.py]`.
   - *Printable Sources & Export*: `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]` (updated to iterate over `eq.source_quotes` in lines 318-319), `@[backend_v2/services/export_evidence_formatter.py]` (`format_text_observations` signature updated to `Sequence[str] | str | None`), `@[backend_v2/services/export_service.py]` (updated to `source_quotes` in lines 555-558, 610), and `@[backend_v2/templates/report_template.jinja2#L478]` (updated quote rendering).
   - *Pass 1 Atomization*: `@[backend_v2/services/orchestrator/two_pass_atomizer.py]` and `@[backend_v2/services/orchestrator/prompts/atom_extraction.py]`.
3. **Studio UI and DTO Chain Decoupling**:
   - Backend Studio DTOs and service: `@[backend_v2/models/dtos/studio.py]`, `@[backend_v2/services/studio/workflow_service.py]`.
   - Frontend Studio models and views: `@[client_app_v2/lib/features/studio/models/workflow.dart]`, `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart]`.
   - Dual-axis localizations: `@[client_app_v2/lib/l10n/app_fi.arb]`, `@[client_app_v2/lib/l10n/app_en.arb]`, `@[backend_v2/l10n/fi.json]`, `@[backend_v2/l10n/en.json]`.
   - Frontend Presentation models and widgets: `@[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]` (`QuoteEvidenceDto.sourceQuotes`), `@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart#L563]`, and `@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L499-L535]` (updating both lines 499-500 null check and line 530 scalar quote interpolation).
4. **Atomic Test Factory & Seed Vault Synchronization**:
   - Strict Pydantic models with `extra="forbid"` require immediate atomic updates to `@[backend_v2/tests/factories/model_factories.py]`, `@[backend_v2/llm/mock_data.py]`, `@[backend_v2/tests/fixtures/sdui_golden_master.json]`, `@[backend_v2/tests/test_data/report_data_dto_fixture.json]`, and `@[backend_v2/seed/seed_data.json#L20538-L21331]` in lockstep with DTO schema changes.
5. **Pydantic V2 Strict Tuple Deserialization Trap (`coerce_source_quotes_tuple`)**:
   - *Problem*: In `ConfigDict(strict=True)`, passing a Python `list` from JSON deserialization or mock data to a `tuple[str, ...] | None` field raises `ValidationError: Input should be a valid tuple [type=tuple_type, input_type=list]`.
   - *Action*: Implemented reusable pre-validation coercion function `coerce_source_quotes_tuple` applied via `BeforeValidator` or `@field_validator("source_quotes", mode="before")` on all receiving DTOs.
6. **Jinja2 Silent Presentation Failure on Undefined Attributes**:
   - *Problem*: In `report_template.jinja2#L478`, Jinja2 silently renders undefined attributes as empty strings (`""`) without raising an error. If `QuoteEvidenceDTO.quote` is deprecated while the template evaluates `{{ quote.quote }}`, PDF reports will silently omit evidence quotes entirely.
   - *Action*: Updated template rendering contract to `{{ quote.source_quotes | join(' [...] ') if quote.source_quotes else '' }}` and mandated PDF rendering parity tests in `@[backend_v2/tests/unit/test_pdf_generator.py]` and `@[backend_v2/tests/unit/test_sdui_template_parity.py]`.

---

## 3. Five-Axis System 2 Deconstruction

### Axis 1: Target Scope & Blast Radius Boundary
- **Scope Inquisitor Audit**: Blast radius is strictly constrained to Phase 1 extraction (`extractive_sensor_service.py`), lexical validation (`anchor_validation_service.py`), DAG DTO schemas (`dag_models.py`, `atom_result.py`, `atom_evaluation.py`), causal linking (`sliding_window_linker.py`), hydration pipelines (`result_projector.py`), and downstream export formatting (`export_service.py`, `export_evidence_formatter.py`).
- **Pruned Creep**: Excluded changes to Phase 2 synthesis workers, LLM routing strategies, or storage drivers.

### Axis 2: Eradicated Duct-Tape (Under-Engineering Ban)
- **Banned Anti-Patterns**:
  - Eliminated `truncate_source_quote_at_sentence` string clipping in `BooleanEvaluationResult` (which previously mutilated citations) in favor of immutable boundary validation.
  - Eliminated asymmetric quote appending in `AnchorValidationService` (which appended unmapped raw quotes on fuzzy matches) in favor of symmetric `pdf_map` coordinate resolution.
  - Eliminated unannotated lambda dictionary instantiation in `sliding_window_linker.py`.
  - Prohibited fallback operators (`or []`, `or ""`) across quote transit.

### Axis 3: Approved Best Practice (Target Invariant)
- **Sovereign Invariants**:
  - Unified `source_quotes: tuple[str, ...] | None = None` across all DAG DTOs with `coerce_source_quotes_tuple`.
  - Null Hypothesis Guardrail: When `is_true == False` or `contextual_override == True`, `source_quotes` MUST be `None`. Ungrounded positive evaluations raise `ValidationError`.
  - Monotonic physical span verification: $s_k < e_k < s_{k+1}$ with $(e_m - s_1) \le 1\,000$ characters.
  - Bounded deliverable root axiom memory: $K_{axiom}^{max} = 8$, $InDegree(v)=0$.

### Axis 4: Pruned Over-Engineering (Complexity Slayer - 30% Deletion Test)
- **Question**: "If 30% of proposed classes/functions were deleted, what gets cut and what breaks?"
- **Cut Items**:
  - Rejected creating separate single-segment and multi-segment polymorphic quote models. A single-segment quote is simply a 1-tuple `(quote,)`.
  - Rejected creating a secondary multi-segment validation wrapper class. Enhanced existing `AnchorValidationService` directly.
  - Rejected introducing a secondary sliding window linker class. Enhanced `SlidingWindowLinker` with bounded axiom injection.

### Axis 5: Fail-Fast Proof Anchor (Deterministic Verification)
- **Mathematical Anchors**:
  - Inverted segment order ($s_2 < s_1$) raises `SemanticEvidenceError`.
  - Non-contiguous span exceeding $1\,000$ chars raises `SemanticEvidenceError`.
  - Non-empty quote on `is_true=False` raises Pydantic `ValidationError`.
  - Segment $<30$ chars when $m > 1$ raises Pydantic `ValidationError`.
  - Window atom count exceeding `linker_max_atoms_per_window` safely bounded by $K_{axiom}^{max} = 8$.

---

## 4. Red-Team Falsification & Attack Analysis

### Failure Mode 1: Forward-Scan Monotonicity False Rejection on Repeated Substrings
- **Attack Vector**: Segment $q_1$ occurs at $[500, 560]$ and segment $q_2$ occurs at $[620, 680]$, but the phrase $q_2$ also appeared earlier in the document introduction at $[120, 180]$. Calling `norm_doc.find(norm_q_2)` without a start index returns $s_2 = 120 < s_1 = 500$, triggering a false-positive `SemanticEvidenceError` for inverted segment order.
- **Defense & Proof**: Mandate bounded forward search `norm_doc.find(norm_q_k, prev_segment_end_idx)` for all segments $k > 1$ in `AnchorValidationService`. Monotonic progression is guaranteed in $O(N)$ text scanning.

### Failure Mode 2: Cross-Document Chimera Stitching in Multi-Document Contexts
- **Attack Vector**: An LLM extracts $q_1$ from Document 1 (offset 200) and $q_2$ from Document 2 (offset 450). If offset arithmetic is evaluated across concatenated or unpartitioned documents, $(450 - 200) = 250 \le 1\,000$ passes validation, allowing a cross-document chimera citation.
- **Defense & Proof**: Enforce single-document provenance isolation in `AnchorValidationService`: all segments $(q_1, \dots, q_m)$ of an atom's `source_quotes` tuple must resolve within the exact same physical source document buffer (`source_doc_id` isolation) before computing $(e_m - s_1) \le 1\,000$.

### Failure Mode 3: Pydantic V2 `strict=True` Tuple vs. JSON Array Deserialization Crash
- **Attack Vector**: LLM structured output returns JSON `{"source_quotes": ["seg1", "seg2"]}`. When parsed via `json.loads()` into a Python `dict` and passed to `model_validate()`, Pydantic V2 `strict=True` rejects `list` for a `tuple[str, ...]` field (`Input should be a valid tuple [type=tuple_type, input_type=list]`).
- **Defense & Proof**: Implement `coerce_source_quotes_tuple` pre-validation coercion via `BeforeValidator(coerce_source_quotes_tuple)` on all DTO fields where `source_quotes: tuple[str, ...] | None = None`. Validated empirically in `scratch/test_tuple.py`.

### Failure Mode 4: Non-Deterministic Root Axiom Selection in `SlidingWindowLinker`
- **Attack Vector**: In early sliding windows of an extended deliverable, more than $K_{axiom}^{max} = 8$ nodes have $InDegree(v) = 0$. Selecting 8 axioms from an unordered set or arbitrary sequence causes run-to-run graph topology variance and non-reproducible BARS scores.
- **Defense & Proof**: Filter root axiom candidates strictly by `Origin(v) == DELIVERABLE and InDegree(v) == 0` and sort deterministically by `(-OutDegree(v), atom_index_asc)` before slicing `[:K_axiom_max]` ($K_{axiom}^{max} = 8$, planned `linker_max_global_root_axioms`). Enforce `len(injected_axioms) + len(window_atoms) <= settings.linker_max_atoms_per_window`.

### Failure Mode 5: Jinja2 Silent Presentation Omission on Deprecated Scalar Quote
- **Attack Vector**: Jinja2 evaluates undefined attributes to empty string without raising an exception. In `report_template.jinja2#L478`, the macro accesses `quote.quote`. When `QuoteEvidenceDTO.quote` is replaced by `source_quotes`, Jinja2 silently renders `""`, wiping evidence quotes from generated PDF reports without failing tests.
- **Defense & Proof**: Update `report_template.jinja2#L478` to `{{ quote.source_quotes | join(' [...] ') if quote.source_quotes else '' }}` and assert physical presence of delimiters in `@[backend_v2/tests/unit/test_pdf_generator.py]` and `@[backend_v2/tests/unit/test_sdui_template_parity.py]`.

### Failure Mode 6: Sliding Window Token Budget Overflow under Fixed Axiom Quotas
- **Attack Vector**: In large sliding windows containing up to 15 current atoms, injecting an unconditional fixed $K_{axiom}^{max} = 8$ root axioms results in $15 + 8 = 23 > 20$ atoms, violating `linker_max_atoms_per_window = 20` and crashing with a budget assertion.
- **Defense & Proof**: Enforce dynamic quota allocation: guaranteed minimum current window quota $W_{min} = 12$ atoms; dynamic root axiom allocation $K_{eff} = \min(8, \max(0, M_{win} - W_{current}))$, preserving hard budget ceiling $M_{win} \le 20$.

---

## 5. 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`BooleanEvaluationResult` & `PreFlightResult` (`@[backend_v2/services/orchestrator/extractive_sensor_service.py]`)** | Banned mutating `truncate_source_quote_at_sentence` string clipping and scalar `source_quote: str \| None`. | `source_quotes: tuple[str, ...] \| None = None` ($1 \le m \le 3$, each $\ge 30$ chars when $m > 1$) with `BeforeValidator(coerce_source_quotes_tuple)` and `@model_validator` enforcing Null Hypothesis invariants (`source_quotes is None` on `is_inverse_evidence=True` absence). | Pruned separate Single vs. Multi DTO classes; unified under a single immutable tuple schema where single quotes are 1-tuples. | `pytest backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py` asserting `ValidationError` on ungrounded `is_true=True` or segment $<30$ chars. |
| **DAG & Domain DTOs (`@[backend_v2/models/domain/blackboard.py]`, `@[backend_v2/models/dtos/dag_models.py]`, `@[backend_v2/models/dtos/causal_discovery.py]`, `@[backend_v2/models/dtos/atom_result.py]`, `@[backend_v2/models/dtos/atom_evaluation.py]`, `@[backend_v2/models/dtos/quote_evidence.py]`, `@[backend_v2/models/dtos/matrix_scorecard.py]`, `@[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]`)** | Banned mutable lists, naked dict state transit, strict tuple validation rejection on JSON lists, and legacy `source_quote` scalar fields. | Strict Pydantic V2 frozen models (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with `source_quotes: tuple[str, ...] \| None` coerced via `coerce_source_quotes_tuple`, updating `DraftExtractedAtom`, `ExtractedAtom`, `AtomEvaluationResultDTO`, `AtomExecutionState`, `CausalNodeDTO`, `AtomResultDTO`, `HydratedAtomDTO`, `EvaluatedAtomDTO`, `ReducedAtomDTO`, `QuoteEvidenceDTO`, `ScorecardAtomDTO`, and Flutter Freezed `QuoteEvidenceDto`. | Pruned nested quote wrapper objects; passed directly as typed immutable `tuple[str, ...]`. | `uv run python scripts/backend_audit_loop.py backend_v2/models/ --test --ast-strict`. |
| **`AnchorValidationService` (`@[backend_v2/services/orchestrator/anchor_validation_service.py]`)** | Banned asymmetric quote appending on fuzzy/stemmed matches, unconstrained span distances, cross-document chimera stitching, and union duck-typing (`list[str] \| list[tuple]`). | Symmetric `pdf_map` coordinate extraction, forward-scan `find(q_k, prev_end)` monotonic order $s_k < e_k < s_{k+1}$, single-document isolation (`source_input_key`), normalized coordinate space (U+00A0/U+2002 invariance), and span $(e_m - s_1) \le 1\,000$ chars. | Pruned separate multi-segment validation service; enhanced unified `_is_lexically_valid` and `validate_evidence` in-place. | `pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py` asserting `SemanticEvidenceError` on $s_2 < s_1$, cross-document buffers, and $(e_m - s_1) > 1\,000$. |
| **`Workflow` Domain, Seed & Studio (`@[backend_v2/models/domain/workflow.py]`, `@[backend_v2/models/dtos/studio.py]`, `@[backend_v2/seed/seed_data.json#L20538-L21331]`)** | Banned conflating scoring dampening ($\zeta_{score}$) with lexical tolerance ($\zeta_{lex}$) in a single field. | Decoupled fields: `default_strictness_level: int = Field(default=50, ge=0, le=100)` and `default_lexical_strictness_level: int = Field(default=50, ge=0, le=100)`. | Pruned external lookup tables; stored directly as sovereign domain attributes on `Workflow` and Studio DTOs. | `uv run python backend_v2/seed/run_seed.py local --dry-run` and `test_workflow_strictness_decoupling`. |
| **`SlidingWindowLinker` & `CausalCohesionEvaluator` (`@[backend_v2/services/orchestrator/sliding_window_linker.py]`, `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]`)** | Banned memoryless sliding windows truncating long-range dependencies, static axiom quotas overflowing window limits, and unannotated lambda dicts. | Persistent Global Context Anchor header for root axioms ($InDegree(v)=0$), dynamic quota allocation ($W_{min}=12, K_{eff} = \min(8, \max(0, M_{win} - W_{current}))$, sorted by `(-OutDegree, idx)`; `@[docs/tiede.md]` Table 8 Row 4), resolving document length-dependent long-tail truncation (>2 000 words), budget guard $M_{win} \le 20$, and `WARRANT_GROUNDING_FAILURE` attribution. | Pruned secondary graph search passes; retained O(W) sequential sliding window with deterministic invariant header. | `pytest backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py` verifying window size $\le 20$ and $r_{iso}^{deliv} \le 0.20$. |
| **Export & SDUI Formatting (`@[backend_v2/services/export_service.py]`, `@[backend_v2/services/export_evidence_formatter.py]`, `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]`, `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]`, `@[backend_v2/templates/report_template.jinja2]`)** | Banned truncating cells, dropping multi-segment citation delimiters, direct scalar quote access on QuoteEvidenceDTO, or silent empty quote rendering in Jinja2 PDF reports (`{{ quote.quote }}`). | Standardized deterministic join `" [...] ".join(source_quotes)` at presentation boundaries, tuple-safe `format_text_observations(quotes: Sequence[str] \| str \| None)`, `printable_sources_adapter.py` multi-segment iteration, and Jinja2 template update `{{ quote.source_quotes \| join(' [...] ') }}`. | Pruned client-side string concatenation logic; formatted deterministically on the backend. | `pytest backend_v2/tests/unit/services/test_export_service.py` and `test_sdui_semantic_parity.py`. |
| **Flutter Client & Studio UI (`@[client_app_v2/lib/features/execution/models/atom_result_dto.dart]`, `@[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]`, `@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart#L563]`, `@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L499-L535]`, `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart]`, `@[client_app_v2/lib/l10n/app_en.arb]`, `@[client_app_v2/lib/l10n/app_fi.arb]`)** | Banned non-nullable fallback defaults (`@Default([])`), manual `substring()` clippings, scalar quote string interpolation, and hardcoded UI strings. | Full-duplex Freezed parity (`final List<String>? sourceQuotes`, `defaultLexicalStrictnessLevel`), multi-segment joining in `SduiMatrixTableWidget` and `CausalInspectorModal`, and localized Studio slider in `.arb` files. | Pruned custom client-side JSON converters; relied strictly on Freezed/JsonSerializable codegen. | `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`. |

---

## 6. Context Rules & KI Coverage Audit

- **Context Rules Audit**: 6 core rules declared and verified:
  - `@[.agents/rules/00-antigravity-core.md]`
  - `@[.agents/rules/01-python-backend.md]`
  - `@[.agents/rules/02_flutter_desktop.md]`
  - `@[.agents/rules/03_seed_vault.md]`
  - `@[.agents/rules/04_directory_reference.md]`
  - `@[.agents/rules/05_llm_architecture.md]`
- **Knowledge Item Coverage Audit**: 12 KIs verified:
  - `@[ki_structured_forensic_quotes.md]` (forensic quote anchoring, entropy gate, null hypothesis)
  - `@[ki_topological_engine.md]` (Kahn waves, Local Causal Markov, Algorithm 1 dual fault attribution)
  - `@[ki_prompt_orchestration_and_matrix_evaluation.md]` (Four-Layer Clean Stack, prompt caching)
  - `@[ki_unified_matrix_scoring_strictness.md]` (continuous strictness slider, power-curve dampening)
  - `@[ki_zero_permissive_typing.md]` (zero permissive typing, immutable tuples)
  - `@[ki_workflow_context_governance.md]` (deliverable provenance, Zone B specialist selection)
  - `@[ki_ai_testing_standards.md]` (ISTQB boundary value analysis, offline ablation benchmark)
  - `@[ki_dumb_painter_sdui.md]` (dumb painter parity, tabular CSV streaming)
  - `@[ki_desktop_pro_tool_studio_ux.md]` (studio rigor tab, dual continuous sliders)
  - `@[ki_opaque_id_hydration.md]` (deterministic alias attention anchors)
  - `@[ki_god_code_prevention.md]` (proactive decomposition, boundary defense)
  - `@[ki_ast_guardrail_engine.md]` (QGR rule enforcement and boundary scans)
- **Audit Result**: Context & KI Coverage Audit: 6 Rules verified, 12 KIs verified. 100% coverage achieved.

---

## 7. Sunset Phase Parity Gate Verification

Every deprecated symbol and contract from Chapter 2.1 is verified to have an explicit phase allocation in Chapter 3:
1. `EPIC_MULTI_SEGMENT_EVIDENCE_AND_CAUSAL_HORIZON.md` $\to$ **Phase 1 (Foundations & Technical Debt)**
2. `source_quote: str | None` in `BooleanEvaluationResult` $\to$ **Phase 2 (WP1)**
3. `source_quote: str | None` in `DraftExtractedAtom` (`@[backend_v2/models/domain/blackboard.py]`) $\to$ **Phase 2 (WP1)**
4. `source_quote: str | None` in `ExtractedAtom` $\to$ **Phase 2 (WP1)**
5. `source_quote: str | None` in `AtomEvaluationResultDTO` $\to$ **Phase 2 (WP1)**
6. `source_quote: str | None` in `AtomExecutionState` $\to$ **Phase 2 (WP1)**
7. `source_quote: str | None` in `CausalNodeDTO` $\to$ **Phase 2 (WP1)**
8. `source_quote: str | None` in `AtomResultDTO` $\to$ **Phase 2 (WP1)**
9. `source_quote: str | None` in `HydratedAtomDTO` (`@[backend_v2/models/dtos/atom_result.py]`) $\to$ **Phase 2 (WP1)**
10. `quote: str` in `QuoteEvidenceDTO` (`@[backend_v2/models/dtos/quote_evidence.py]`) $\to$ **Phase 2 (WP1)**
11. `default_strictness_level` as sole strictness SSOT $\to$ **Phase 4 (WP2)**
12. Single-string `exact_quotes: list[str]` parameter $\to$ **Phase 3 (WP2)**
13. Bounded single-window horizon without root memory $\to$ **Phase 5 (WP3)**
14. Scalar quote export formatting in `export_evidence_formatter.py` $\to$ **Phase 6 (WP1 & WP3)**
15. Scalar quote formatting in `xai_highlights_adapter.py` $\to$ **Phase 6 (WP1 & WP3)**
16. Scalar quote rendering in `report_template.jinja2` $\to$ **Phase 6 (WP1 & WP3)**
17. `source_quote: str | None` in `ReducedAtomDTO` (`@[backend_v2/models/dtos/atom_evaluation.py]`) $\to$ **Phase 2 (WP1)**
18. `source_quote: str | None` in `PreFlightResult` (`@[backend_v2/services/orchestrator/extractive_sensor_service.py]`) $\to$ **Phase 2 (WP1)**
19. `source_quote: str | None` in `EvaluatedAtomDTO` (`@[backend_v2/models/dtos/atom_result.py]`) $\to$ **Phase 2 (WP1)**
20. `exact_quotes: list[str]` in `EvaluatedAtomDTO` (`@[backend_v2/models/dtos/atom_result.py]`) $\to$ **Phase 2 (WP1)**
21. Direct quote access `eq.quote` in `printable_sources_adapter.py` $\to$ **Phase 6 (WP1 & WP3)**
22. Uncoupled Studio strictness controls $\to$ **Phase 4 & Phase 6 (WP2 & WP3)**
23. Strict tuple deserialization without list coercion $\to$ **Phase 2 (WP1)**
24. `quote: String` in `QuoteEvidenceDto` (`@[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]`) $\to$ **Phase 6 (WP1 & WP3)**
25. `sourceQuote: String?` in `AtomResultDTO` (`@[client_app_v2/lib/features/execution/models/atom_result_dto.dart]`) $\to$ **Phase 6 (WP1 & WP3)**
26. `sourceQuote: String?` in `CausalNodeDto` (`@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]`) $\to$ **Phase 6 (WP1 & WP3)**
27. `sourceQuote: String?` in `HydratedAtomDto` (`@[client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart]`) $\to$ **Phase 6 (WP1 & WP3)**
28. `truncate_source_quote_at_sentence` mutating pre-validator $\to$ **Phase 1 (Foundations & Technical Debt)**
29. `defaultdict(lambda: WindowCausalEdgesDTO(edges={}))` factory $\to$ **Phase 1 (Foundations & Technical Debt)**
30. Scalar quote rendering `"${q.quote}"` in `sdui_matrix_table_widget.dart#L563` $\to$ **Phase 6 (WP1 & WP3)**
31. Scalar quote interpolation `"${node.sourceQuote}"` in `causal_inspector_modal.dart#L499-L535` $\to$ **Phase 6 (WP1 & WP3)**

**Gate Status**: 100% PARITY ACHIEVED. All 31 deprecations and technical debt items allocated.

---

## 8. Post-Audit Recommendations for Tier 1 Planner

1. **Atomic Phase 2 Execution**: Because DTO schemas enforce `extra="forbid"`, updating `ExtractedAtom`, `AtomEvaluationResultDTO`, `DraftExtractedAtom`, `AtomResultDTO`, `HydratedAtomDTO`, `EvaluatedAtomDTO`, `ReducedAtomDTO`, and `QuoteEvidenceDTO` must be committed atomically with test factories (`backend_v2/tests/factories/model_factories.py`) and mock data (`backend_v2/llm/mock_data.py`).
2. **Deterministic Pre-Validation Coercion**: Ensure `coerce_source_quotes_tuple` is tested in isolation with both `list` and `tuple` inputs before running broad model validation tests.
3. **Continuous Strictness Calibration Gate**: In Phase 4, verify that workflows with $\zeta_{score} = 85$ and $\zeta_{lex} = 50$ properly validate 15 Finnish noun case inflections through Gate 5 Snowball stemming without false rejections.
4. **Dynamic Root Axiom Allocation**: In Phase 5, ensure `SlidingWindowLinker`'s dynamic quota calculation ($W_{min}=12, K_{eff} \le 8, M_{win} \le 20$) is tested with mock deliverables having $>20$ root axioms to confirm the window size never exceeds the configured ceiling.
