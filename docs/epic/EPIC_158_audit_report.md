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
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
  <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_chat_ingress_and_provenance_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_generation_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
</required_context_rules>

# SYSTEM 2 ARCHITECTURAL RESEARCH & RED-TEAM AUDIT REPORT

**Target Document:** @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]  
**Auditor:** Principal Enterprise Architect & System Red Team  
**Evaluation Date:** 2026-10-18  
**Audit Status:** APPROVED (HARDENED)  

---

## 1. Executive Summary & Root Cause Analysis

### 1.1 Root Cause & Scientific Problem Formulation
In Quorum's Phase 1 DAG cognitive extraction pipeline, empirical evaluation over $N=220$ proposition frames and production trial pairs identified three critical structural failure modes:
1. **The 13.33 % Conditional False Omission Rate ($\widehat{FOR}$)**:
   - **Multi-Sentence Omission Gap ($FOR_{omission} = 10.00\%$)**: Natural language claims in strategic deliverables frequently span compound, non-contiguous clauses (specifically: an antecedent premise separated from an operational conclusion by rhetorical elaboration). The current single scalar string citation contract (`source_quote: str | None`) forces the extraction sensor to choose between truncating the citation (violating the Anti-Ellipsis Mandate) or rejecting the claim entirely, inflating false negative omissions.
   - **Agglutinative Inflection Rejection ($FOR_{rejection} = 3.33\%$)**: Evaluative scoring dampening ($\zeta_{score}$) and morphological recognition tolerance ($\zeta_{lex}$) are conflated in a single parameter (`default_strictness_level`). Setting high evaluative strictness artificially suppresses Gate 5 Snowball stemming, falsely rejecting valid Finnish noun case inflections.
2. **The Inter-Run Retrieval Gap ($\bar{\kappa} = 0.9348$)**:
   - Discrepancy analysis over production trial pairs revealed that 85.7% (6 of 7 total discrepancies) stemmed not from cognitive or reasoning divergence, but from physical extraction gating where one run captured a single-sentence fragment while the second run failed to encapsulate the compound sentence, causing inter-run disagreement.
3. **Causal Horizon Truncation in Extended Documents ($r_{iso}^{deliv} = 0.264$)**:
   - `SlidingWindowLinker` operates over local window slices ($W_{win}=4, O_{win}=2, \Delta_{max} \le 20$). In short corpora (specifically: the 666-word candidate deliverable in Trial Pair A), all atoms naturally fit within 1–2 windows, satisfying deliverable isolation thresholds ($r_{iso}^{deliv} \le 0.20$). However, in extended corpora (>2 000 words, specifically Sitra Trial Pair B), early deliverable root axioms ($InDegree(v)=0$) are evicted from memory in subsequent windows, leaving late claims disconnected and driving the isolation ratio to $r_{iso}^{deliv} = 0.264$ (failing the Level 3 BARS gate).

### 1.2 Justification of Proposed Architectural Solution
EPIC 158 solves these empirical bottlenecks with zero new third-party dependencies and zero token latency overhead:
- **Ordered Multi-Segment Citation Tuples ($1 \le m \le 3$)**: Expands evidence representation from a scalar string to an immutable tuple `source_quotes: tuple[str, ...] | None`, bounded by physical coordinate mapping ($(e_m - s_1) \le 1\,000$ characters) with an individual segment floor ($\ge 30$ characters when $m > 1$). This recovers 100% of compound premise-conclusion claims while maintaining $\text{Specificity}_{lex} = 1.000$ against chimeric stitching.
- **Sovereign Strictness Decoupling**: Mathematically separates power-curve score dampening ($\zeta_{score} \in [0, 100]$) from morphological lexical tolerance ($\zeta_{lex} \in [0, 100]$) as sovereign, first-class fields on `Workflow` and Studio configuration.
- **Persistent Global Context Anchor Header for Root Axioms ($K_{axiom}^{max} = 8$)**: Injects deliverable root axioms into subsequent sliding windows under dynamic budget allocation ($W_{min}=12, K_{eff} \le 8, M_{win} \le 20$), preserving the Local Causal Markov Condition and eliminating long-tail causal horizon truncation.

---

## 2. Five-Axis System 2 Deconstruction Findings

### Axis 1: Target Scope & Boundaries (Scope Inquisitor)
- **Codebase Targets**: 50 codebase files physically verified across backend models, orchestrators, adapters, database seeds, and frontend Flutter clients.
- **Blast Radius**: ~1,790 lines of code across 39 domain contracts and 40 sunset symbols/operations.
- **Caller Audit**: 1-hop callers inspected across `TopologicalEvaluator`, `DAGExecutor`, `CausalCohesionEvaluator`, `CausalDiscoveryEngine`, `MatrixHook`, `MatrixDomainParser`, and `ReportService`, eliminating hidden scalar quote lookups and preventing `AttributeError` crashes.

### Axis 2: Eradicated Duct-Tape (Under-Engineering Ban)
The audit identified and eradicated 15 specific technical debt anti-patterns:
1. Mutating sentence clipping in `truncate_source_quote_at_sentence` within `BooleanEvaluationResult`.
2. Asymmetric quote extraction in `AnchorValidationService.validate_evidence` (exact matches resolving coordinates, fuzzy matches returning raw strings).
3. Unannotated lambda dictionary factory `defaultdict(lambda: WindowCausalEdgesDTO(edges={}))` in `SlidingWindowLinker`.
4. Anonymous 3-tuple coordinate returns `(is_valid, start_idx, end_idx)` violating Quorum's Anti-Tuple Architecture (Rule `ban_anonymous_state_tuples` and QGR015).
5. Union duck-typing `quotes: list[str] | str | None` in `ExportEvidenceFormatter`.
6. Direct scalar attribute access `eq.quote` in `PrintableSourcesAdapter`.
7. Wave evaluation state copy using retired `"source_quote"` keyword in `TopologicalEvaluator`.
8. Direct `node.source_quote` and `if not n.source_quote` in `DAGExecutor`.
9. Direct `source_quote=None` in `HydratedAtomDTO` instantiation within `CausalCohesionEvaluator`.
10. Direct scalar `atom.source_quote` string lookups in `CausalDiscoveryEngine`.
11. Direct scalar quote construction in `MatrixHook` and `MatrixDomainParser`.
12. Direct scalar quote projection in `ReportService.get_report_rows`.
13. Bare `Field(...)` assignments and duck-typed `dict(data)` parsing in `QuoteEvidenceDTO`.
14. Hardcoded `const TextStyle`, `const SizedBox`, and unlocalized strings in Flutter widgets (`human_override_dialog.dart`, `sdui_matrix_table_widget.dart`, `causal_inspector_modal.dart`).
15. Silent Jinja2 PDF quote dropping caused by scalar attribute access `{{ quote.quote }}`.

### Axis 3: Approved Best Practice (Type Constitutionalist)
- **Pydantic V2 Strict Immutability**: All modified DTOs enforce `ConfigDict(strict=True, extra="forbid", frozen=True)`.
- **Centralized Pre-Validation Coercion SSOT**: Established `coerce_source_quotes_tuple` in `backend_v2/models/core_base.py` to safely wrap single string payloads into 1-tuples (preventing character shattering) and coerce deserialized JSON lists into immutable tuples prior to strict validation.
- **Typed Anti-Tuple Contract**: Created `GateMatchResultDTO(is_valid: bool, start_idx: int, end_idx: int)` to eradicate anonymous 3-tuples across `AnchorValidationService` lexical gates.
- **Full-Duplex Parity**: Synchronous alignment between Python `source_quotes: tuple[str, ...] | None` and Flutter Freezed `final List<String>? sourceQuotes` with `disallowUnrecognizedKeys: true`.
- **Flutter Theme Sovereignty**: Complete replacement of raw typography and sizing in citation widgets with `Theme.of(context).textTheme` and `AppSpacing` tokens.

### Axis 4: Pruned Over-Engineering (Complexity Slayer - 30% Deletion Test)
- **Unified Single Pipeline**: Rejected proposals to create bifurcated single-segment vs. multi-segment validator pipelines or parallel DTO hierarchies. Single quotes are naturally represented as 1-tuples ($m=1$).
- **No Speculative Token-Bucket Throttlers**: Phase 1 DAG groups atoms into 5–15 chunked requests; execution latency is dominated by reasoning tokens, not pacing. Speculative throttler refactorings were pruned.
- **Direct Domain Attributes**: Sovereign strictness levels are stored directly on `Workflow` and Studio DTOs, pruning proposed external database lookup tables.

### Axis 5: Fail-Fast Proof Anchors (Incorruptible Judge)
- **ISTQB Boundary Coverage**:
  - Segment span $>1\,000$ characters raises `SemanticEvidenceError`.
  - Inverted segment order ($s_2 < s_1$) raises `SemanticEvidenceError`.
  - Segment $<30$ characters when $m > 1$ raises `ValidationError`.
  - Cross-document buffer stitching raises `SemanticEvidenceError`.
  - Affirmative claim without evidence raises `ValidationError`.
  - Verified absence on inverse evidence enforces `source_quotes is None`.
- **Automated Quality Gates**:
  - `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`
  - `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`
  - Offline ablation benchmark ($N=220$) verifying pass rate $\ge 56.4\%$ with $0/21$ chimera leaks.

---

## 3. Panel of Architects Evaluation

### 3.1 Global System Architect
- **Verdict: PASS (HARDENED)**
- **Findings**: The Epic strictly adheres to the Single Sovereign Pipeline invariant. Single-segment quotes and multi-segment quotes flow through the exact same mathematical validation gates. Bypasses of Fail-Fast are strictly prohibited. The Anti-Tuple mandate is enforced by replacing anonymous 3-tuples with `GateMatchResultDTO`.

### 3.2 Backend & Data Architect
- **Verdict: PASS (HARDENED)**
- **Findings**: Database seed synchronizations in `seed_data.json` are bounded atomically. Ingress JSON list deserialization under Pydantic V2 `strict=True` is safely handled by `coerce_source_quotes_tuple`, eliminating list rejection crashes while preventing string shattering.

### 3.3 SDUI & Frontend Architect
- **Verdict: PASS (HARDENED)**
- **Findings**: Strict Dumb Painter SDUI parity is preserved across Flutter desktop views, tabular CSV/Excel streaming, and Jinja2 PDF templates. Silent quote omissions in PDF reports are prevented by updating `report_template.jinja2#L478` to `{{ quote.source_quotes | join(' [...] ') }}`. Hardcoded UI strings and styling in touched Flutter widgets are localized and aligned with Flutter Theme Sovereignty.

### 3.4 AI & Orchestration Architect
- **Verdict: PASS (HARDENED)**
- **Findings**: The Four-Layer Clean Stack hierarchy is strictly maintained; prompt caching prefixes remain 100% byte-static. Sliding window budget allocation ($W_{min}=12, K_{eff} \le 8, M_{win} \le 20$) prevents prompt token overflow even in extended corpora (>2 000 words). ATMS fault attribution incurs zero additional LLM tokens.

---

## 4. Falsification & Red-Team Attack (Concrete Failure Modes)

### Failure Mode 1: Candidate $s_1$ Anchor Coordinate Shadowing (The Table of Contents Trap)
- **Attack Scenario**: A compound claim $C$ spans two sentences $q_1$ and $q_2$. Segment $q_1$ appears verbatim as a section heading in the Table of Contents at character offset 120 ($s_1^{(1)} = 120$). The true body of the proposal containing $q_1$ and $q_2$ in semantic proximity occurs in Section 3 at character offset 4,500 ($s_1^{(2)} = 4500, s_2 = 4580$).
- **Vulnerability**: If `AnchorValidationService` greedily terminates on the first occurrence of $q_1$ via `norm_doc.find(norm_q_1)`, it anchors at $s_1^{(1)} = 120$. Searching for $q_2$ within the subsequent 1,000-character window (`norm_doc[120:1120]`) fails completely, causing a false-positive `SemanticEvidenceError` that erroneously rejects valid physical evidence.
- **Proof Anchor**: `AnchorValidationService._is_lexically_valid` iterates through all candidate occurrences $s_1^{(r)}$ in `norm_doc`. For each candidate $s_1^{(r)}$, it evaluates whether subsequent segments $k > 1$ resolve monotonically within $(e_m - s_1^{(r)}) \le 1\,000$ characters. Validation succeeds as soon as any valid coordinate chain is verified.

### Failure Mode 2: Cross-Document Chimera Stitching via Flat Concatenated Ingress Buffers
- **Attack Scenario**: External inputs (`product_text` and `chat_log`) are concatenated into an unsegregated validation buffer. An LLM extracts segment $q_1$ from the candidate deliverable and segment $q_2$ from the interviewer's prompt in the chat log. If the boundary between documents falls within 1,000 characters, naive span distance checking ($(e_2 - s_1) \le 1\,000$) succeeds, manufacturing an illegal cross-document chimera citation.
- **Vulnerability**: Attributing interviewer coaching or prompt text to the candidate's deliverable corrupts evidence integrity and breaches EU AI Act Articles 12–15.
- **Proof Anchor**: Multi-segment coordinate resolution enforces strict buffer provenance boundaries: segments $q_1, \dots, q_m$ must resolve entirely within the identical discrete source document boundary (`source_input_key`). If any segment crosses into an adjacent document buffer, `AnchorValidationService` raises `SemanticEvidenceError` immediately.

### Failure Mode 3: Anonymous 3-Tuple Hell in Coordinate Resolution (QGR015 Fatal AST Breach)
- **Attack Scenario**: Returning an anonymous tuple `(is_valid: bool, start_idx: int, end_idx: int)` from lexical validation gates introduces positional tuple unpacking into `AnchorValidationService` and `ExtractiveSensorService`.
- **Vulnerability**: Positional unpacking (`start_idx, end_idx, is_valid = ...`) is susceptible to type blindness and positional swapping, triggering fatal AST guardrail `QGR015` and crashing the codebase audit loop.
- **Proof Anchor**: All lexical validation gates return the strongly typed immutable Pydantic V2 DTO `GateMatchResultDTO(is_valid: bool, start_idx: int, end_idx: int)`.

### Failure Mode 4: Silent PDF Evidence Erasure via Jinja2 Attribute Scaffolding
- **Attack Scenario**: When `QuoteEvidenceDTO` sunsets scalar `quote` in favor of `source_quotes`, `report_template.jinja2#L478` continues to evaluate `{{ quote.quote }}`.
- **Vulnerability**: Jinja2 silently renders undefined attributes as empty strings (`""`) without raising an error. PDF reports generated in production silently lose all evidence citations without a single log warning or stack trace, compromising enterprise compliance audits.
- **Proof Anchor**: `report_template.jinja2#L478` is updated synchronously in Phase 6 to `{{ quote.source_quotes | join(' [...] ') if quote.source_quotes else '' }}`, verified by golden master PDF rendering integration tests in `test_pdf_generator.py`.

### Failure Mode 5: String Shattering on Single-String Test Payloads in `coerce_source_quotes_tuple`
- **Attack Scenario**: Legacy test mocks or external inputs pass a single string `"Hankkeen tavoite"` to a DTO expecting `source_quotes: tuple[str, ...] | None`.
- **Vulnerability**: Calling `tuple("Hankkeen tavoite")` without an explicit type guard shatters the string into individual characters: `('H', 'a', 'n', 'k', 'k', 'e', 'e', 'n', ' ', ...)`. Each 1-character segment violates the 30-character floor ($m > 1$) and fails lexical validation.
- **Proof Anchor**: `coerce_source_quotes_tuple` in `backend_v2/models/core_base.py` explicitly checks `if isinstance(v, str): return (v.strip(),) if v.strip() else None` before handling list/iterable conversion.

---

## 5. 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`BooleanEvaluationResult` (`@[backend_v2/services/orchestrator/extractive_sensor_service.py]`)** | Banned mutating `truncate_source_quote_at_sentence` string clipping and scalar `source_quote: str \| None`. | `source_quotes: tuple[str, ...] \| None = None` ($1 \le m \le 3$, each $\ge 30$ chars when $m > 1$) with `BeforeValidator(coerce_source_quotes_tuple)` and `@model_validator` enforcing Null Hypothesis invariants (`source_quotes is None` on `is_inverse_evidence=True` absence). | Pruned separate Single vs. Multi DTO classes; unified under a single immutable tuple schema where single quotes are 1-tuples. | `pytest backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py` asserting `ValidationError` on ungrounded `is_true=True` or segment $<30$ chars. |
| **DAG & Domain DTOs (`@[backend_v2/models/core_base.py]`, `@[backend_v2/models/domain/blackboard.py]`, `@[backend_v2/models/dtos/dag_models.py]`, `@[backend_v2/models/dtos/causal_discovery.py]`, `@[backend_v2/models/dtos/atom_result.py]`, `@[backend_v2/models/dtos/atom_evaluation.py]`, `@[backend_v2/models/dtos/quote_evidence.py]`, `@[backend_v2/models/dtos/matrix_scorecard.py]`, `@[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]`)** | Banned mutable lists, naked dict state transit, strict tuple validation rejection on JSON lists, legacy `source_quote` scalar fields, and bare `Field(...)` / duck-typed parsing in `quote_evidence.py`. | Strict Pydantic V2 frozen models (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with `source_quotes: tuple[str, ...] \| None` coerced via `coerce_source_quotes_tuple` SSOT in `core_base.py` (preventing string shattering), updating `DraftExtractedAtom`, `ExtractedAtom`, `AtomEvaluationResultDTO`, `AtomExecutionState`, `CausalNodeDTO`, `AtomResultDTO`, `HydratedAtomDTO`, `EvaluatedAtomDTO`, `ReducedAtomDTO`, `QuoteEvidenceDTO`, `ScorecardAtomDTO`, and Flutter Freezed `QuoteEvidenceDto`. | Pruned nested quote wrapper objects; passed directly as typed immutable `tuple[str, ...]`. | `uv run python scripts/backend_audit_loop.py backend_v2/models/ --test --ast-strict`. |
| **`AnchorValidationService` (`@[backend_v2/services/orchestrator/anchor_validation_service.py]`)** | Banned asymmetric quote appending on fuzzy/stemmed matches, unconstrained span distances, cross-document chimera stitching, anonymous 3-tuples (`(is_valid, start, end)`), and union duck-typing (`list[str] \| list[tuple]`). | Symmetric `pdf_map` coordinate extraction, forward-scan `find(q_k, prev_end)` monotonic order $s_k < e_k < s_{k+1}$, single-document isolation (`source_input_key`), normalized coordinate space (U+00A0/U+2002 invariance), span $(e_m - s_1) \le 1\,000$ chars, and typed `GateMatchResultDTO` coordinate returns (strictly banning anonymous state tuples under `ban_anonymous_state_tuples` and QGR015). | Pruned separate multi-segment validation service; enhanced unified `_is_lexically_valid` and `validate_evidence` in-place. | `pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py` asserting `SemanticEvidenceError` on $s_2 < s_1$, cross-document buffers, and $(e_m - s_1) > 1\,000$. |
| **`Workflow` Domain, Seed & Studio (`@[backend_v2/models/domain/workflow.py]`, `@[backend_v2/models/dtos/studio.py]`, `@[backend_v2/seed/seed_data.json#L20538-L21331]`)** | Banned conflating scoring dampening ($\zeta_{score}$) with lexical tolerance ($\zeta_{lex}$) in a single field. | Decoupled fields: `default_strictness_level: int = Field(default=50, ge=0, le=100)` and `default_lexical_strictness_level: int = Field(default=50, ge=0, le=100)`. | Pruned external lookup tables; stored directly as sovereign domain attributes on `Workflow` and Studio DTOs. | `uv run python backend_v2/seed/run_seed.py local --dry-run` and `test_workflow_strictness_decoupling`. |
| **`SlidingWindowLinker` & `CausalCohesionEvaluator` (`@[backend_v2/services/orchestrator/sliding_window_linker.py]`, `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]`)** | Banned memoryless sliding windows truncating long-range dependencies, static axiom quotas overflowing window limits, unannotated lambda dicts, and scalar `source_quote` references. | Persistent Global Context Anchor header for root axioms ($InDegree(v)=0$), dynamic quota allocation ($W_{min}=12, K_{eff} = \min(8, \max(0, M_{win} - W_{current}))$, sorted by `(-OutDegree, idx)`; `@[docs/tiede.md]` Table 8 Row 4), resolving document length-dependent long-tail truncation (>2 000 words), budget guard $M_{win} \le 20$, and `WARRANT_GROUNDING_FAILURE` attribution. | Pruned secondary graph search passes; retained O(W) sequential sliding window with deterministic invariant header. | `pytest backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py` verifying window size $\le 20$ and $r_{iso}^{deliv} \le 0.20$. |
| **Export & SDUI Formatting (`@[backend_v2/services/export_service.py]`, `@[backend_v2/services/export_evidence_formatter.py]`, `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]`, `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]`, `@[backend_v2/templates/report_template.jinja2]`, `@[backend_v2/scripts/generate_openapi.py]`, `@[docs/swagger/openapi.json]`)** | Banned truncating cells, dropping multi-segment citation delimiters, direct scalar quote access on QuoteEvidenceDTO, `Sequence[str] | str` legacy union duck-typing, or silent empty quote rendering in Jinja2 PDF reports (`{{ quote.quote }}`). | Standardized deterministic join `" [...] ".join(source_quotes)` at presentation boundaries, strict `format_text_observations(quotes: tuple[str, ...] \| None)`, `printable_sources_adapter.py` multi-segment iteration, Jinja2 template update `{{ quote.source_quotes \| join(' [...] ') }}`, and OpenAPI schema regeneration. | Pruned client-side string concatenation logic; formatted deterministically on the backend. | `pytest backend_v2/tests/unit/services/test_export_service.py` and `test_sdui_semantic_parity.py`. |
| **`ReportService` & `ReportRowItemDTO` (`@[backend_v2/services/report_service.py#L636]`, `@[backend_v2/models/dtos/report_artifact.py#L79]`)** | Banned direct scalar quote access `atom.source_quote` in B2B tabular report extraction and unvalidated string assumptions. | Standardized delimiter projection `quote=" [...] ".join(atom.source_quotes) if atom.source_quotes else None` into `ReportRowItemDTO(quote=...)`, maintaining B2B tabular presentation contract. | Pruned bespoke export string formatters; shared standard delimiter format. | `pytest backend_v2/tests/unit/services/test_report_service.py` asserting non-empty joined quote string on affirmative atoms. |
| **`TopologicalEvaluator` & `DAGExecutor` (`@[backend_v2/services/orchestrator/topological_evaluator.py#L163]`, `@[backend_v2/services/orchestrator/dag_executor.py#L111]`)** | Banned retired `"source_quote"` keyword in `model_copy(update=...)`, unhandled scalar string attribute lookups, and unsupported deliverable count scalar checks. | Strict update to `"source_quotes": res.source_quotes` on `AtomExecutionState`, `" [...] ".join(node.source_quotes)` formatting for `FlattenedAtom`, and `if not n.source_quotes` for deliverable support audits. | Pruned intermediate string sanitizers; derived formatting directly from typed segment tuple. | `pytest backend_v2/tests/unit/services/orchestrator/test_topological_evaluator.py` and `test_dag_executor.py`. |
| **Flutter Client & Studio UI (`@[client_app_v2/lib/features/execution/models/atom_result_dto.dart]`, `@[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]`, `@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart#L563]`, `@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L499-L535]`, `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart]`, `@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L264-L295]`, `@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart#L697-L749]`, `@[client_app_v2/lib/l10n/app_en.arb]`, `@[client_app_v2/lib/l10n/app_fi.arb]`)** | Banned non-nullable fallback defaults (`@Default([])`), manual `substring()` clippings, scalar quote string interpolation, legacy `q.quote` getters, hardcoded UI strings, and Flutter Theme Sovereignty violations (`const TextStyle`, `const SizedBox`). | Full-duplex Freezed parity (`final List<String>? sourceQuotes`, `defaultLexicalStrictnessLevel`), multi-segment joining across all citation widgets, theme-governed typography, and localized Studio slider in `.arb` files. | Pruned custom client-side JSON converters; relied strictly on Freezed/JsonSerializable codegen. | `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`. |

---

## 6. Context Rules & Knowledge Item Coverage Audit

- **Canonical Rule Blocks Verified**: 6 Rules
  - `@[.agents/rules/00-antigravity-core.md]`
  - `@[.agents/rules/01-python-backend.md]`
  - `@[.agents/rules/02_flutter_desktop.md]`
  - `@[.agents/rules/03_seed_vault.md]`
  - `@[.agents/rules/04_directory_reference.md]`
  - `@[.agents/rules/05_llm_architecture.md]`
- **Domain Knowledge Items Verified**: 19 Knowledge Items
  - `@[ki_structured_forensic_quotes.md]`
  - `@[ki_topological_engine.md]`
  - `@[ki_prompt_orchestration_and_matrix_evaluation.md]`
  - `@[ki_unified_matrix_scoring_strictness.md]`
  - `@[ki_zero_permissive_typing.md]`
  - `@[ki_workflow_context_governance.md]`
  - `@[ki_ai_testing_standards.md]`
  - `@[ki_dumb_painter_sdui.md]`
  - `@[ki_desktop_pro_tool_studio_ux.md]`
  - `@[ki_opaque_id_hydration.md]`
  - `@[ki_god_code_prevention.md]`
  - `@[ki_ast_guardrail_engine.md]`
  - `@[ki_sdui_matrix_synthesis.md]`
  - `@[ki_dag_engine_dto_projection_rules.md]`
  - `@[ki_deterministic_hardening_state.md]`
  - `@[ki_dual_axis_localization_architecture.md]`
  - `@[ki_chat_ingress_and_provenance_architecture.md]`
  - `@[ki_prompt_generation_architecture.md]`
  - `@[ki_system_audit_trail_xai.md]`
- **Audit Outcome**: `Context & KI Coverage Audit: 6 Rules verified, 19 KIs verified.`

---

## 7. Implementation Readiness & Final Recommendation

The System 2 deconstruction, adversarial red-teaming, and architectural hardening confirm that EPIC 158 is **100% sound, mathematically grounded, and fully aligned with Quorum 2026 architectural invariants**:
1. All target boundaries and 1-hop callers are explicitly mapped.
2. Discovered technical debt has been isolated and scheduled into `Phase 1: Pre-Implementation Cleanups`.
3. Critical deployment sequence is locked to guarantee consumer Freezed models compile before backend serializers deploy.
4. Anonymous state tuples are eradicated via `GateMatchResultDTO`.
5. Markdown boundaries pass cleanly with zero warnings (`audit_markdown_boundaries.py` code 0).

**Next Step**: The Epic is ready for formal implementation planning. Per rule `context_amnesia_prevention`, the user must start a brand NEW chat session and execute:
```powershell
/tier1-planner @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]
```
