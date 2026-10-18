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

# EPIC 158: Multi-Segment Evidence Extraction, Morphological Decoupling & Causal Horizon Expansion

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
> - **Neyman–Pearson Asymmetric Error Governance (`@[docs/tiede.md]` Section 8.6 Point 4, Table 8 Row 2; Neyman & Pearson, 1933)**: In high-stakes regulatory auditing and enterprise governance (specifically: EU AI Act Articles 12–15), Type I errors (accepting fabricated, hallucinated, or chimera evidence, $\alpha$) carry unbounded compliance liability. Quorum consciously locks physical citation specificity to $\text{Specificity}_{lex} = 1.000$ ($\alpha \to 0$), accepting an empirical sensitivity cost ($FNR_{pop} = 28.61\%$, $\widehat{FOR} = 13.33\%$, matching the 27.59% extraction recall penalty / 8 of 29 chimera benchmark claims in `@[docs/tiede.md]` Section 8.5 Table 7). EPIC 158 directly implements the roadmap mitigation formalized in `@[docs/tiede.md]` Table 8: recovering diffuse multi-sentence omissions ($FOR_{omission} = 10.00\%$) via bounded multi-segment extraction and inflectional rejections ($FOR_{rejection} = 3.33\%$) via decoupled Gate 5 morphology, while mathematically preserving $\text{Specificity}_{lex} = 1.000$.
> - **Five-Gate Lexical Firewall Architectural Parity (`@[docs/tiede.md]` Section 4.1.1; Lewis et al., 2025; Thorne et al., FEVER 2.0)**: Natural language claims in analytical corpora frequently span compound, non-contiguous clauses (specifically: antecedent premise separated from an operational conclusion by rhetorical elaboration). Multi-segment validation extends Gate 1 ($\mathcal{M}_{idx}$ bidirectional coordinate mapping) and Gate 2 ($1\,000$-character contiguous safety ceiling, $(e_m - s_1) \le 1\,000$), enforcing ordered monotonic offset constraints ($s_1 < e_1 < s_2 < e_2 \le s_1 + 1\,000$) with individual segment floors ($\ge 30$ characters when $m > 1$). This recovers 100% of multi-clause evidence while preventing chimeric stitching.
> - **Epistemic Decoupling of Lexical Tolerance and Evaluative Scoring (`@[docs/tiede.md]` Section 4.1.1 Gate 5, Section 5.4; Kahneman & Tversky, 2025)**: Evaluative stringency (penalizing unsubstantiated claims via power-law score dampening $\gamma(\zeta_{score})$) is mathematically orthogonal to morphological recognition (accommodating 15 Finnish grammatical noun cases and agglutinative inflections via Gate 5 Snowball stemming $\zeta_{lex}$). Coupling them into a single parameter artificially inflates false rejections at strict evaluation settings.
> - **Persistent Global Context Anchor Header for Root Axioms (`@[docs/tiede.md]` Section 2.2 Point 1, Section 10.1 Table 8 Row 4; Pearl, 2025; Spirtes, Glymour & Scheines)**: Context-bounded sliding window linkers ($W_{win}=4, O_{win}=2, \Delta_{max} \le 20$) artificially truncate long-range causal dependencies in extended documents ($|\mathcal{V}_{claim}| > 140$). Formally implementing the persistent Global Context Anchor header for deliverable root axioms ($K_{axiom}^{max} = 8$, $InDegree(v)=0$) preserves the Local Causal Markov Condition and eliminates isolated concept denominator dilution ($r_{iso}^{deliv} \le r_{L3}^{max} = 0.20$) without quadratic attention explosion.

---

## 1. Goal Description & Background (Objective & Problem Statement)

### 1.1 Objective
The objective of EPIC 158 is to eliminate empirical false negative errors and resolve causal graph horizon truncation across Quorum's Phase 1 DAG execution pipeline:
1. Eliminate the empirical **13.33 %** conditional omission/rejection error ($\widehat{FOR}$ consisting of **10.00 %** multi-sentence omission $FOR_{omission}$ and **3.33 %** inflection rejection $FOR_{rejection}$) and the **28.61 %** population-level false negative rate ($FNR_{pop}$).
2. Resolve the inter-run *Retrieval Gap* (specifically: 85.7% / 6 of 7 total inter-run discrepancies observed across production evaluation trials @[scratch/diff_report_2026-10-16_2242.md] and @[scratch/diff_report_2026-10-17_1130.md]) to elevate pooled Cohen's kappa from $\overline{\kappa} = 0.9348$ to $\overline{\kappa} \ge 0.9800$.
3. Expand proposition extraction to ordered multi-segment citation tuples ($1 \le m \le 3$) bounded by physical document offset constraints ($(e_m - s_1) \le 1\,000$ characters, $s_k < e_k < s_{k+1}$) and individual segment length floors ($\ge 30$ characters when $m > 1$).
4. Decouple lexical verification tolerance ($\zeta_{lex} \in [0, 100]$) from power-curve score dampening ($\zeta_{score} \in [0, 100]$) as sovereign, first-class fields on the `Workflow` domain model and Studio configuration.
5. Expand the causal discovery horizon in `SlidingWindowLinker` by implementing bounded deliverable root axiom anchoring ($K_{axiom}^{max} = 8$ axioms where $InDegree(v)=0$), resolving the document length-dependent long-tail truncation where short corpora (specifically: the 666-word candidate deliverable in @[scratch/diff_report_2026-10-16_2242.md]) naturally pass ($r_{iso}^{deliv} \le 0.20$) while extended corpora (>2 000 words, specifically Sitra Trial Pair B) fail at $r_{iso}^{deliv} = 0.264$, without additional token overhead.

### 1.2 Quantitative Target Baseline Table
Baseline measurements derived from the offline ablation benchmark ($N=220$ proposition frames) and production verification pairs (Pair A & Pair B, $N=110$ criteria per run):

| Metric Identifier | Empirical Baseline (Current State) | Target Invariant (Epic 158 DoD) | Mathematical Verification Method |
| :--- | :--- | :--- | :--- |
| **Conditional False Omission Rate ($\widehat{FOR}$)** | **13.33 %** ($4/30$ in human calibration sample) | **$\le 2.00\,\%$** ($0$ or $<1/30$) | Contingency table re-evaluation ($N=70$ human expert audit) |
| **Multi-Sentence Omission Gap ($FOR_{omission}$)** | **10.00 %** ($3/30$) | **0.00 %** ($0/30$) | Multi-segment extraction recovery ($8/8$ ablation gap items) |
| **Agglutinative Inflection Rejection ($FOR_{rejection}$)** | **3.33 %** ($1/30$) | **0.00 %** ($0/30$) | Decoupled Gate 5 morphological verification ($\zeta_{lex}=50$) |
| **Lexical Specificity ($\text{Specificity}_{lex}$)** | **1.000** ($0/21$ chimera leaks) | **1.000** ($0/21$ chimera leaks) | Synthetic chimera injection bench ($29$ adversarial probes) |
| **Ablation Benchmark Pass Rate** | **52.7 %** ($116/220$ frames) | **$\ge 56.4\,\%$** ($\ge 124/220$ frames) | Offline benchmark execution (`run_e2e_variance_test.py`) |
| **Inter-Run Agreement ($\overline{\kappa}$)** | **0.9348** (85.7% / 6 of 7 retrieval gap disagreements across @[scratch/diff_report_2026-10-16_2242.md] [$\kappa=0.9064$] and @[scratch/diff_report_2026-10-17_1130.md] [$\kappa=0.9633$]) | **$\ge 0.9800$** ($0$ retrieval gap disagreements) | Pairwise Cohen's kappa over Trial Pairs A and B |
| **Deliverable Isolation Ratio ($r_{iso}^{deliv}$)** | **0.264** (Extended Sitra Trial Pair B failing $L_3$; vs. 666-word short corpus in @[scratch/diff_report_2026-10-16_2242.md] passing $L_3$) | **$\le 0.200$** (Uniformly passing $L_3/L_4$ across both short and extended corpora) | Deliverable induced subgraph calculation in `DAGExecutor` |
| **ATMS Reasoning Latency** | **$< 1.0\text{ ms}$** | **$< 1.0\text{ ms}$** ($0$ additional LLM tokens) | Micro-benchmark over Algorithm 1 fault attribution |

### 1.3 Quantitative Scope Validation Table

| Architectural Archetype | Target Files Modified / Created | Affected Classes & DTO Contracts | Discovered Tech Debt / Sunset Operations | Blast Radius (Estimated LOC) |
| :--- | :--- | :--- | :--- | :--- |
| **Pydantic V2 Domain Models & DTOs** | 10 files (`backend_v2/models/`, including `core_base.py`) | 14 classes / validator SSOTs (`coerce_source_quotes_tuple`, `DraftExtractedAtom`, `ExtractedAtom`, `AtomEvaluationResultDTO`, `AtomExecutionState`, `CausalNodeDTO`, `AtomResultDTO`, `HydratedAtomDTO`, `EvaluatedAtomDTO`, `ReducedAtomDTO`, `QuoteEvidenceDTO`, `Workflow`, `WorkflowCreateDTO`, `ReportRowItemDTO`) | 13 sunset scalar `source_quote` fields replaced by `source_quotes: tuple[str, ...] \| None` with `coerce_source_quotes_tuple` SSOT in `core_base.py`, and bare `Field(...)` / duck-typed parsing in `quote_evidence.py` | ~330 LOC |
| **Orchestration & Sensor Services** | 12 files (`backend_v2/services/orchestrator/`, `studio/`) | 10 services (`ExtractiveSensorService`, `AnchorValidationService`, `SlidingWindowLinker`, `CausalCohesionEvaluator`, `ResultProjector`, `MatrixReducer`, `TwoPassAtomizer`, `TopologicalEvaluator`, `DAGExecutor`, `CausalDiscoveryEngine`) | 8 technical debt items eradicated (mutating sentence truncation, asymmetric quote appending, unannotated lambda dict, memoryless sliding window, wave copy scalar quote, missing caller tuple unpack, unanchored paragraph check, raw quote kwargs) | ~520 LOC |
| **Hooks & Domain Parsers** | 2 files (`backend_v2/hooks/scoring/`, `services/`) | 2 handlers (`matrix_hook.py`, `matrix_domain_parser.py`) | 2 direct scalar quote instantiations in `QuoteEvidenceDTO` upgraded to multi-segment `source_quotes` | ~60 LOC |
| **SDUI Adapters, Presentation & Export** | 7 files (`backend_v2/services/sdui/`, `export/`, `templates/`, `services/`) | 6 adapters / services (`ExportService`, `ExportEvidenceFormatter`, `XaiHighlightsAdapter`, `PrintableSourcesAdapter`, `ReportService`, `report_template.jinja2`) | 4 presentation failure modes prevented (silent Jinja2 quote drop, scalar quote truncation in CSV/Excel, direct `eq.quote` AttributeError, `get_report_rows` atom quote crash) | ~220 LOC |
| **Database Seed Vault** | 1 file (`backend_v2/seed/seed_data.json`) | All 8 seeded workflows in `@[backend_v2/seed/seed_data.json#L20538-L21331]` | Conflated strictness separated into sovereign `default_strictness_level: 50` and `default_lexical_strictness_level: 50` | ~40 LOC |
| **Frontend Flutter Desktop Client** | 11 files (`client_app_v2/lib/features/`) | 6 Freezed DTOs + 5 UI Widgets (`QuoteEvidenceDto`, `AtomResultDTO`, `CausalNodeDto`, `HydratedAtomDto`, `HumanOverrideRequestDto`, `WorkflowStrictnessTab`, `SduiMatrixTableWidget`, `CausalInspectorModal`, `HumanOverrideDialog`, `AtomMatrixTableWidget`) | 8 client compilation, parsing & Theme Sovereignty issues remediated (`disallowUnrecognizedKeys: true` parity, scalar quote interpolation, single slider limitation, override dialog compilation, raw `const TextStyle` and `const SizedBox` eradication) | ~360 LOC |
| **Test Fixtures, Factories & Mocks** | 7 files (`backend_v2/tests/`, `scripts/`) | 5 test suites + 2 golden fixtures (`model_factories.py`, `mock_data.py`, `sdui_golden_master.json`, `report_data_dto_fixture.json`, `run_e2e_variance_test.py`) | Outdated scalar quote test mocks and golden fixtures atomically modernized | ~260 LOC |
| **Total Quantitative Scope** | **50 codebase files** (plus 2 localized `.json`/`.arb` pairs, 1 integration test, 1 rule file, 1 academic doc, 1 audit report) = **68 files** | **39 domain contracts** | **40 sunset symbols / operations** | **~1,790 LOC** |

---

## 2. Architectural Impact & Compliance Matrix

### 2.1 Deprecations & Sunset List (`What We Will REMOVE`)
Destructive Operation Inventory mapping each deprecated symbol or convention to its replacement or marked "INTENTIONALLY DROPPED":

| Deprecated Symbol / Contract | Physical File Location | Replacement SSOT / Disposition | Catastrophic Reason for Removal |
| :--- | :--- | :--- | :--- |
| `EPIC_MULTI_SEGMENT_EVIDENCE_AND_CAUSAL_HORIZON.md` | `@[docs/epic/EPIC_MULTI_SEGMENT_EVIDENCE_AND_CAUSAL_HORIZON.md]` | `[DELETE]`: Previously deleted from repository to retain single SSOT in `@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]` | Replaced: Duplicate Epic file breaches Single Source of Truth and risks divergent planning. |
| `source_quote: str \| None` (single scalar string) | `@[backend_v2/services/orchestrator/extractive_sensor_service.py]` | `source_quotes: tuple[str, ...] \| None` (immutable 1-3 segment tuple) | Replaced: Scalar string forces truncation or illegal ellipses when evidence spans compound clauses. |
| `source_quote: str \| None` in `DraftExtractedAtom` | `@[backend_v2/models/domain/blackboard.py]` | `source_quotes: tuple[str, ...] \| None` (immutable 1-3 segment tuple) | Replaced: Blackboard draft atoms require multi-segment citation grounding during extraction. |
| `source_quote: str \| None` in `ExtractedAtom` | `@[backend_v2/models/dtos/dag_models.py]` | `source_quotes: tuple[str, ...] \| None` | Replaced: Downstream DAG nodes must receive structured segment tuples to prevent re-parsing. |
| `source_quote: str \| None` in `AtomEvaluationResultDTO` | `@[backend_v2/models/dtos/dag_models.py]` | `source_quotes: tuple[str, ...] \| None` | Replaced: Sensor evaluation payload must match multi-segment extraction schema. |
| `source_quote: str \| None` in `AtomExecutionState` | `@[backend_v2/models/dtos/dag_models.py]` | `source_quotes: tuple[str, ...] \| None` | Replaced: DAG execution runtime state must retain segment boundaries. |
| `source_quote: str \| None` in `CausalNodeDTO` | `@[backend_v2/models/dtos/causal_discovery.py]` | `source_quotes: tuple[str, ...] \| None` | Replaced: Argument mining causal nodes require multi-segment citation grounding. |
| `source_quote: str \| None` in `AtomResultDTO` | `@[backend_v2/models/dtos/atom_result.py]` | `source_quotes: tuple[str, ...] \| None` | Replaced: State reducer and presentation projection require typed multi-segment transit. |
| `source_quote: str \| None` in `HydratedAtomDTO` | `@[backend_v2/models/dtos/atom_result.py]` | `source_quotes: tuple[str, ...] \| None` | Replaced: Backend atom hydration must transit ordered multi-segment citation tuples. |
| `quote: str` in `QuoteEvidenceDTO` | `@[backend_v2/models/dtos/quote_evidence.py]` | `source_quotes: tuple[str, ...] \| None` | Replaced: Quote evidence transport requires multi-segment segment boundaries. |
| `default_strictness_level` as sole strictness SSOT | `@[backend_v2/models/domain/workflow.py]` | Split into `default_strictness_level: int = 50` and `default_lexical_strictness_level: int = 50` | Replaced: Conflating scoring dampening with lexical tolerance causes morphological false rejections. |
| Single-string `exact_quotes: list[str]` parameter | `@[backend_v2/services/orchestrator/anchor_validation_service.py]` | `exact_quotes: list[tuple[str, ...]]` or multi-segment list validation | Replaced: AnchorValidationService must validate segment tuples and bounding span distances. |
| Bounded single-window horizon without root memory | `@[backend_v2/services/orchestrator/sliding_window_linker.py]` | Dynamic budget-guarded root axiom header ($W_{min}=12, K_{eff} \le 8, M_{win} \le 20$; `@[docs/tiede.md]` Table 8 Row 4) | Replaced: Truncates cross-chapter causal dependencies in deliverables exceeding 140 claims. |
| Scalar quote export formatting in `export_evidence_formatter.py` | `@[backend_v2/services/export_evidence_formatter.py]` | Deterministic delimiter `" [...] ".join(source_quotes)` | Replaced: Export evidence formatter must format multi-segment quotes uniformly. |
| Scalar quote formatting in `xai_highlights_adapter.py` | `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]` | Standardized delimiter `" [...] ".join(source_quotes)` in SDUI highlights | Replaced: Highlights adapter must display multi-segment citations without truncation. |
| Scalar quote rendering `{{ quote.quote }}` in `report_template.jinja2` | `@[backend_v2/templates/report_template.jinja2]` | Render multi-segment citation delimiters `{{ quote.source_quotes \| join(' [...] ') }}` | Replaced: Jinja2 evaluates undefined attributes to empty strings, silently omitting evidence quotes from PDF reports. |
| `source_quote: str \| None` in `ReducedAtomDTO` | `@[backend_v2/models/dtos/atom_evaluation.py]` | `source_quotes: tuple[str, ...] \| None` (immutable 1-3 segment tuple) | Replaced: Matrix reduction and synthesis distillation require typed multi-segment transit. |
| `source_quote: str \| None` in `PreFlightResult` | `@[backend_v2/services/orchestrator/extractive_sensor_service.py]` | `source_quotes: tuple[str, ...] \| None` | Replaced: Pre-flight sensor evaluation payload must match multi-segment schema. |
| `source_quote: str \| None` in `EvaluatedAtomDTO` | `@[backend_v2/models/dtos/atom_result.py]` | `source_quotes: tuple[str, ...] \| None` | Replaced: Matrix scorecard evaluated atom model requires multi-segment citation grounding. |
| `exact_quotes: list[str]` in `EvaluatedAtomDTO` | `@[backend_v2/models/dtos/atom_result.py]` | `source_quotes: tuple[str, ...] \| None` | Replaced: Superseded by typed `source_quotes` multi-segment tuple representation. |
| Direct quote access `eq.quote` in `printable_sources_adapter.py` | `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]` | Multi-segment iteration over `eq.source_quotes` | Replaced: Direct attribute access crashes when QuoteEvidenceDTO migrates from scalar quote to source_quotes. |
| Uncoupled Studio strictness controls | `@[backend_v2/models/dtos/studio.py]` & `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart]` | Split into independent `default_strictness_level` and `default_lexical_strictness_level` | Replaced: Studio UI must provide decoupled continuous sliders for scoring and lexical strictness. |
| Strict tuple deserialization without list coercion | `@[backend_v2/models/dtos/dag_models.py]`, `@[backend_v2/services/orchestrator/extractive_sensor_service.py]` | `BeforeValidator(coerce_source_quotes_tuple)` | Replaced: Under `ConfigDict(strict=True)`, standard Pydantic V2 rejects deserialized JSON lists with `ValidationError`. |
| `quote: String` in `QuoteEvidenceDto` | `@[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]` | `sourceQuotes: List<String>?` | Replaced: Flutter QuoteEvidenceDto enforces disallowUnrecognizedKeys: true; must update to sourceQuotes to match backend QuoteEvidenceDTO. |
| `sourceQuote: String?` in `AtomResultDTO` | `@[client_app_v2/lib/features/execution/models/atom_result_dto.dart]` | `sourceQuotes: List<String>?` | Replaced: Flutter AtomResultDTO requires multi-segment quote transit without client-side deserialization errors. |
| `sourceQuote: String?` in `CausalNodeDto` | `@[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]` | `sourceQuotes: List<String>?` | Replaced: Flutter CausalNodeDto requires multi-segment citation grounding for causal inspector. |
| `sourceQuote: String?` in `HydratedAtomDto` | `@[client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart]` | `sourceQuotes: List<String>?` | Replaced: Flutter HydratedAtomDto requires multi-segment citation grounding for SDUI rendering. |
| `truncate_source_quote_at_sentence` mutating pre-validator | `@[backend_v2/services/orchestrator/extractive_sensor_service.py]` | Immutable boundary validation | Replaced: Mutating quotes destroys physical lexical anchoring; replaced by immutable boundary length assertions. |
| `defaultdict(lambda: WindowCausalEdgesDTO(edges={}))` factory | `@[backend_v2/services/orchestrator/sliding_window_linker.py]` | Explicit typed dictionary initialization | Replaced: Unannotated lambda dictionary factory violates strict typing and clean architecture invariants. |
| Scalar quote rendering `"${q.quote}"` | `@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart#L563]` | Multi-segment join `"${q.sourceQuotes?.join(' [...] ') ?? ''}"` | Replaced: Direct scalar string rendering breaks compilation and presentation when QuoteEvidenceDto migrates to sourceQuotes. |
| Scalar quote interpolation `"${node.sourceQuote}"` | `@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L499-L535]` | Multi-segment check and join `"${node.sourceQuotes?.join(' [...] ') ?? ''}"` | Replaced: Direct scalar string interpolation breaks compilation and presentation when sourceQuotes becomes a list. |
| Wave copy `"source_quote": res.source_quote` | `@[backend_v2/services/orchestrator/topological_evaluator.py#L163]` | `"source_quotes": res.source_quotes` | Replaced: AtomExecutionState enforces extra='forbid'; passing retired source_quote raises ValidationError. |
| Direct `node.source_quote` in DAG executor | `@[backend_v2/services/orchestrator/dag_executor.py#L111]` | `" [...] ".join(node.source_quotes)` and `if not n.source_quotes` | Replaced: Direct scalar attribute access raises AttributeError when CausalNodeDTO sunsets source_quote. |
| Direct `source_quote=None` in causal cohesion evaluator | `@[backend_v2/services/orchestrator/causal_cohesion_evaluator.py#L266]` | `source_quotes=None` | Replaced: HydratedAtomDTO enforces extra='forbid'; passing retired source_quote raises ValidationError. |
| Scalar `atom.source_quote` in paragraph search | `@[backend_v2/services/orchestrator/engines/causal_discovery_engine.py#L182]` | Iteration over `atom.source_quotes` or primary anchor `atom.source_quotes[0]` | Replaced: ExtractedAtom sunsets source_quote; direct attribute lookup raises AttributeError during graph synthesis. |
| Scalar `quote=ev_dto.source_quote` in matrix hook | `@[backend_v2/hooks/scoring/matrix_hook.py#L421]` | `source_quotes=ev_dto.source_quotes` | Replaced: QuoteEvidenceDTO sunsets quote parameter; direct scalar keyword argument raises ValidationError. |
| Scalar `{"quote": val_data.source_quote}` in domain parser | `@[backend_v2/services/matrix_domain_parser.py#L479]` | `{"source_quotes": val_data.source_quotes}` | Replaced: QuoteEvidenceDTO schema rejects quote dictionary key under strict Pydantic extra='forbid'. |
| Scalar `quote=atom.source_quote` in report service | `@[backend_v2/services/report_service.py#L636]` | `quote=" [...] ".join(atom.source_quotes) if atom.source_quotes else None` | Replaced: AtomResultDTO sunsets source_quote; get_report_rows raises AttributeError. |
| Scalar quote construction `quote: l10n.humanOverrideExpertNote` | `@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L264-L295]` | `sourceQuotes: [l10n.humanOverrideExpertNote]` and `q.sourceQuotes?.join(' [...] ') ?? ''` | Replaced: Dart compilation failure when QuoteEvidenceDto sunsets quote parameter. |
| Scalar quote access `q.quote` in atom matrix table | `@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart#L697-L749]` | `q.sourceQuotes?.join(' [...] ') ?? ''` | Replaced: Dart compilation failure when QuoteEvidenceDto sunsets quote getter. |
| Bare `Field(...)` and duck-typed `dict(data)` in `quote_evidence.py` | `@[backend_v2/models/dtos/quote_evidence.py#L113-L206]` | `Annotated[..., Field(...)]` and typed alias validation | Replaced: Violates PEP 593 typing and zero permissive typing invariants. |
| Raw `const TextStyle` and `const SizedBox` in UI widgets | `@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L265-L286]`, `@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart#L550]` | `Theme.of(context).textTheme` tokens and `AppSpacing` | Replaced: Violates Flutter Theme Sovereignty and AppSpacing Design Tokens. |

### 2.2 Retained SSOT Invariants (`What We Will RETAIN`)
1. **Four-Layer Clean Stack Hierarchy (`05_llm_architecture.md`)**: Layer 1 static system instructions (`MATRIX_SENSOR_SYSTEM_PROMPT`), Layer 2 theory context, Layer 3 extraction protocol, and Layer 4 dynamic user tail. Prompt caching prefix remains 100% byte-static.
2. **Local Causal Markov Condition (`ki_topological_engine.md`)**: In Kahn's topological evaluation waves, an atom is conditionally independent given its resolved causal parents. Short-circuit cascades to `ExecutionStatus.N_A` remain instantaneous without LLM dispatch.
3. **Algorithm 1 Dual Fault Attribution (`ki_topological_engine.md`)**: Clear separation between `CausalRootCauseType.NODE_FAILURE` and `CausalRootCauseType.WARRANT_GROUNDING_FAILURE`. If an upstream premise evaluates cleanly but the multi-segment warrant fails lexical validation, the failure is typed strictly as `WARRANT_GROUNDING_FAILURE`.
4. **Deliverable Subgraph Induction & Exogenous Boundary Axiom (`ki_topological_engine.md`)**: Causal cohesion metrics evaluate strictly over nodes originating from candidate-endorsed deliverables ($N_{deliv} = |\mathcal{V}_{deliverable}|$), while cross-document process dialogue provides exogenous support without denominator dilution.
5. **Dumb Painter SDUI Architecture (`ki_dumb_painter_sdui.md`)**: The Flutter client and PDF export layer remain pure stateless renderers. Multi-segment quotes are projected for presentation into uniform visual strings without client-side text manipulation.
6. **Zero-Trust Dependency Firewall (`00-antigravity-core.md`)**: Pure Python implementation using existing Martin Porter Snowball stemmer (`StemmerService`), RapidFuzz, and NetworkX. Zero new third-party packages in `uv.lock` or `pubspec.yaml`.
7. **Null Hypothesis Invariant on Inverse Evidence (`ki_prompt_orchestration_and_matrix_evaluation.md`)**: As demonstrated by discrepancy analysis in @[scratch/diff_report_2026-10-16_2242.md] (specifically: atom `tda_ea1a9c5b4176c72c7774c7037bb3eb4e`), propositions evaluating the absence of a negative pattern (`is_inverse_evidence=True` passing under the Null Hypothesis) MUST strictly retain `source_quotes = None`. Expanding the citation contract to multi-segment tuples ($1 \le m \le 3$) applies strictly and exclusively to positive empirical evidence; multi-segment extraction MUST NEVER emit phantom quotes for verified absences.

### 2.3 Compliance & Modernity Gates
- **100% Pydantic V2 Strict Mode**: All modified DTOs enforce `ConfigDict(strict=True, extra="forbid", frozen=True)`.
- **Zero Permissive Typing**: Absolute prohibition of naked dicts (`dict[str, Any]`), `cast(Any, ...)`, `# noqa` suppressions, or `# type: ignore` comments.
- **Fail-Fast Boundary Defense**: Missing required fields or ungrounded claims immediately raise `AppException` or Pydantic `ValidationError`. Zero silent fallbacks (`.get()`, `or`).
- **Single Sovereign Pipeline**: Zero bifurcated pipelines or legacy fallback escape hatches ("if multi-segment then X else old logic"). All propositions evaluate through the unified multi-segment schema where single-segment quotes are represented as 1-tuples (`m = 1`).
- **Red-Team Invariant 1 (Candidate $s_1$ Anchor Iteration & Bounded Gate 3–5 Coordinate Resolution)**: `AnchorValidationService._is_lexically_valid` iterates over all candidate occurrences $s_1^{(r)}$ of segment $q_1$ in `norm_doc` and chains segments $k > 1$ within the slice `norm_doc[prev_segment_end_idx : s_1 + 1000]`. Every validation gate (Gate 3 exact substring, Gate 4 RapidFuzz window, Gate 5 Snowball stemmed token span) MUST return a deterministic, immutable Pydantic V2 DTO `GateMatchResultDTO(is_valid=True, start_idx=start_norm_idx, end_idx=end_norm_idx)` in normalized document coordinate space (strictly banning anonymous 3-tuples under `ban_anonymous_state_tuples` and QGR015), preventing false-positive `SemanticEvidenceError` when $q_1$ repeats earlier in document introductions or when segments match via Gate 5 Finnish case inflections.
- **Red-Team Invariant 2 (Cross-Document Chimera Buffer Boundary Defense)**: Multi-segment bounding $(e_m - s_1) \le 1\,000$ characters is valid strictly and exclusively for segments resolving within the exact same physical source document buffer (specifically: `input_product_text.md`, `input_reflection_text.md`, or `input_chat_log_user_only.md` as segregated in @[scratch/diff_report_2026-10-16_2242.md]). If segments span across discrete documents, `AnchorValidationService` MUST reject the extraction with `SemanticEvidenceError`, eliminating cross-document chimera stitching.
- **Red-Team Invariant 3 (Pydantic Strict Ingress Deserialization)**: Ingress structured outputs enforce `model_validate_json()` and boundary conversion validators so that JSON arrays `["..."]` are safely parsed into immutable `tuple[str, ...] | None` without triggering Pydantic V2 `strict=True` list rejections.
- **Red-Team Invariant 4 (Cumulative Prior-Window Root Axiom Ordering)**: Sliding window axiom candidates at window $w > 0$ are evaluated over the cumulative directed graph $\mathcal{G}_{<w}$ discovered across prior windows $[0, w-1]$, strictly filtered to `Origin(v) == DELIVERABLE and InDegree(v) == 0` in $\mathcal{G}_{<w}$, and sorted deterministically by `(-OutDegree(v), atom_index_asc)` before slicing `[:K_eff]`, with window atom budget $M_{win} \le 20$.
- **Red-Team Invariant 5 (Whitespace & Unicode Normalization Invariance)**: In multi-segment lexical validation, each individual segment $q_k$ and the source document text MUST be normalized using identical Unicode/whitespace normalization (specifically: collapsing non-breaking spaces `\u00A0` and en-spaces `\u2002` observed in production trial pairs @[scratch/diff_report_2026-10-16_2242.md]) prior to substring offset computation, ensuring bounding span distance $(e_m - s_1) \le 1\,000$ characters is strictly computed in normalized coordinate space without drift.
- **Red-Team Invariant 6 (Pydantic V2 Pre-Validation Coercion Invariant `coerce_source_quotes_tuple`)**: When validating payloads where `source_quotes: tuple[str, ...] | None` under `ConfigDict(strict=True)`, standard Pydantic V2 rejects Python `list` inputs (which naturally arise from JSON array decoding in `json.loads` or mock dictionaries) with `ValidationError: Input should be a valid tuple`. All DTOs accepting `source_quotes` MUST decorate the field with `Annotated[tuple[str, ...] | None, BeforeValidator(coerce_source_quotes_tuple)]` or explicit `@field_validator("source_quotes", mode="before")` to safely coerce `list` into an immutable `tuple` prior to strict type validation.
- **Red-Team Invariant 7 (Jinja2 PDF Presentation Parity Invariant)**: In `backend_v2/templates/report_template.jinja2`, Jinja2 silently renders undefined attributes as empty strings (`""`) without error. If `QuoteEvidenceDTO.quote` is deprecated while the template continues to access `{{ quote.quote }}`, PDF reports will silently omit evidence quotes entirely. The Jinja2 macro MUST be updated to `{{ quote.source_quotes | join(' [...] ') if quote.source_quotes else '' }}` and verified via golden master tests.
- **Red-Team Invariant 8 (Sliding Window Dynamic Budget Allocation Invariant)**: When injecting deliverable root axioms ($InDegree(v)=0$) into `SlidingWindowLinker`, allocating a fixed $K_{axiom}^{max} = 8$ axioms into a window containing up to 15 current atoms could violate `linker_max_atoms_per_window = 20` (23 atoms). The linker MUST enforce a dynamic quota allocation: guaranteed minimum current window quota $W_{min} = 12$ atoms; dynamic root axiom allocation $K_{eff} = \min(8, \max(0, M_{win} - W_{current}))$, where candidate axioms are ranked deterministically by `(-OutDegree(v), atom_index_asc)`.
- **Red-Team Invariant 9 (String Shattering Prevention in `coerce_source_quotes_tuple`)**: When single string payloads are passed to `source_quotes` (from test mocks or legacy inputs), `coerce_source_quotes_tuple` in `backend_v2/models/core_base.py` MUST explicitly check `isinstance(v, str)` and wrap it into a 1-tuple `(v.strip(),)`, strictly preventing `tuple(str)` character splitting (`('q', 'u', 'o', 't', 'e', ...)`); it MUST also filter out empty/whitespace strings and safely coerce lists/iterables.
- **Red-Team Invariant 10 (Flutter Theme Sovereignty and Empty Multi-Segment Check)**: In Flutter citation widgets (`human_override_dialog.dart`, `sdui_matrix_table_widget.dart`, `atom_matrix_table_widget.dart`), multi-segment quotes MUST be guarded by `q.sourceQuotes != null && q.sourceQuotes!.isNotEmpty && q.sourceQuotes!.any((s) => s.trim().isNotEmpty)` before rendering enclosing quotation marks `""` to prevent phantom empty quote rendering `""""`. All hardcoded `const TextStyle` and `const SizedBox` in touched files MUST be replaced by `Theme.of(context).textTheme` and `AppSpacing` tokens per Flutter Theme Sovereignty.

### 2.4 Producer-Consumer Integration Check

| Domain Producer | Transport Contract | Domain Consumer | Parity & Validation Mechanism |
| :--- | :--- | :--- | :--- |
| `ExtractiveSensorService.evaluate_atom_boolean_batch` | `BooleanEvaluationResult.source_quotes` (`tuple[str, ...] \| None`) | `EnrichedDagExecutor` / `AtomExecutionState` | Pydantic V2 `@model_validator` enforcing Null Hypothesis invariants. |
| `AnchorValidationService.validate_evidence` | `extracted_quotes` (`list[tuple[str, ...]]`) | `ExtractiveSensorService` | Monotonic offset verification $[s_1, e_m] \le 1\,000$ chars via $\mathcal{M}_{idx}$ with single-document buffer boundary isolation. |
| `SlidingWindowLinker.link_graph` | `LinkedAtomGraph.atom.source_quotes` | `CausalDiscoveryEngine` / `TopologicalEvaluator` | `CausalGraphPayloadDTO.validate_referential_integrity`. |
| `Workflow` Domain Model | `default_lexical_strictness_level: int` | `ExecutionWorker` to `AnchorValidationService` | Direct dot-notation transit; verified in `test_workflow_strictness_decoupling`. |
| `ExportService` & `ExportEvidenceFormatter` | `ExportForensicAtomDTO.quotes: str` | Tabular CSV, Excel and Jinja2 PDF Artifacts | Deterministic join `" [...] ".join(source_quotes)` at export boundary. |
| `HydrationHook` / `result_projector.py` | `HydratedAtomDTO.source_quotes` (`tuple[str, ...] \| None`) | `StateReducer` / SDUI Mappers | Full-Duplex DTO parity via `backend_audit_loop.py`. |
| `StudioWorkflowService` | `WorkflowCreateDTO` / `WorkflowUpdateDTO` | Flutter Studio `WorkflowStrictnessTab` | Two-way reactive synchronization in Quorum Studio. |
| Backend REST API (`/reports/`) | `AtomResultDTO.source_quotes` | Flutter `AtomResultDTO.sourceQuotes` (`List<String>?`) | Full-Duplex DTO parity via `flutter_audit_loop.py --build`. |

### 2.5 5-Column Architectural Directive Table

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

### 2.6 Critical Deployment Sequence & Migration Order

To prevent runtime deserialization crashes (`disallowUnrecognizedKeys: true` on Flutter Freezed models and `ValidationError` under Pydantic V2 strict mode), the rollout across environments and execution phases MUST enforce the following linear order:

1. **Stage 1 (Pre-Flight Foundation & Test Scaffolding - Phase 1)**: Eliminate technical debt in touched target files (`truncate_source_quote_at_sentence` mutation in `BooleanEvaluationResult`, unannotated lambdas in `SlidingWindowLinker`, asymmetric quote extraction in `AnchorValidationService`).
2. **Stage 2 (Full-Duplex Contract Alignment & Coercion - Phase 2 & Phase 6 Consumer Models)**: Introduce `coerce_source_quotes_tuple` pre-validators across backend DTOs and synchronously update Flutter Freezed models to accept `sourceQuotes: List<String>?`. Client models must compile and support multi-segment arrays BEFORE backend producers stream them.
3. **Stage 3 (Core Extraction, Verification & Horizon Expansion - Phases 3, 4, 5)**: Deploy multi-segment coordinate verification ($s_1 < e_1 < s_2 < e_2 \le s_1 + 1\,000$) in `AnchorValidationService`, sovereign strictness decoupling ($\zeta_{lex}$ vs $\zeta_{score}$) in `Workflow` / `seed_data.json`, and deliverable root axiom anchoring ($K_{axiom}^{max} = 8$) in `SlidingWindowLinker`.
4. **Stage 4 (SDUI Presentation, Tabular Export & Jinja2 PDF Sync - Phase 6)**: Deploy Jinja2 report template multi-segment delimiter rendering (`{{ quote.source_quotes | join(' [...] ') }}`), export evidence formatters, and Studio UI dual sliders.
5. **Stage 5 (Empirical Benchmark & As-Built Architecture - Phases 7 & 8)**: Run the 220-frame offline ablation benchmark and live E2E gate, then execute parameterized `/tier7-describe-architecture` post-audit to update KIs, pillars, and `@[docs/tiede.md]`.

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Pre-Implementation Technical Debt Cleanups & Foundations
- **Objective**: Remediate discovered technical debt in touched target files, eliminate SSOT duplicate documents, and prepare test scaffolding before introducing multi-segment extraction logic.
- **Pre-Implementation Technical Debt Cleanups**:
  1. *Duplicate Epic Elimination*: [DELETE] verified physical removal of `@[docs/epic/EPIC_MULTI_SEGMENT_EVIDENCE_AND_CAUSAL_HORIZON.md]` to enforce `@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]` as the sole Single Source of Truth.
  2. *AnchorValidationService Coordinate Parity*: Remediate asymmetric quote extraction in `AnchorValidationService.validate_evidence` by enforcing symmetric start/end index resolution via `pdf_map` for both exact and fuzzy/stemmed matches, eliminating raw unmapped quote appending.
  3. *ExtractiveSensorService Immutable Invariant*: Deprecate and remove mutating `truncate_source_quote_at_sentence` pre-validator on `BooleanEvaluationResult` in favor of immutable boundary validation that asserts segment length limits without mutating source text.
  4. *SlidingWindowLinker Typed Initialization & Import Cleanup*: Replace unannotated lambda dictionary factory (`defaultdict(lambda: WindowCausalEdgesDTO(edges={}))`) and `defaultdict(list)` with strict typed collection initialization, and clean up unused module-level import `from backend_v2.settings import get_settings`.
  5. *ExportEvidenceFormatter Typing Strictness*: Eliminate union duck-typing in `format_text_observations(quotes: list[str] | str | None)` in `@[backend_v2/services/export_evidence_formatter.py]` in favor of strictly typed `format_text_observations(quotes: tuple[str, ...] | None) -> str`.
  6. *PrintableSourcesAdapter Pre-Migration Safeguard*: In `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]`, remediate direct scalar attribute access `eq.quote` on line 318 in favor of multi-segment iteration over `eq.source_quotes` to prevent `AttributeError` when `QuoteEvidenceDTO` is refactored.
  7. *TopologicalEvaluator State Copy Invariant*: In `@[backend_v2/services/orchestrator/topological_evaluator.py#L163]`, prepare wave evaluation state copy to transit `"source_quotes": res.source_quotes` safely without `ValidationError` on `extra='forbid'`.
  8. *DAGExecutor Node Quote Formatting*: In `@[backend_v2/services/orchestrator/dag_executor.py#L111]`, prepare `_flatten_nodes` extraction rule formatting for multi-segment tuples and `unsupported_count` audit for segment presence.
  9. *CausalDiscoveryEngine Paragraph Anchor Search*: In `@[backend_v2/services/orchestrator/engines/causal_discovery_engine.py#L182]`, remediate scalar `atom.source_quote` lookups in paragraph boundaries to iterate over `atom.source_quotes` (anchoring on primary segment `atom.source_quotes[0]`).
  10. *MatrixHook & DomainParser QuoteEvidenceDTO Safeguard*: In `@[backend_v2/hooks/scoring/matrix_hook.py#L421]` and `@[backend_v2/services/matrix_domain_parser.py#L479]`, remediate scalar `quote` keyword and dictionary key bindings when instantiating `QuoteEvidenceDTO`.
  11. *ReportService B2B Tabular Row Parity*: In `@[backend_v2/services/report_service.py#L636]`, prepare `get_report_rows` to project `quote=" [...] ".join(atom.source_quotes) if atom.source_quotes else None` into `ReportRowItemDTO`.
  12. *QuoteEvidenceDTO Annotated Syntax & Parsing Cleanup*: In `@[backend_v2/models/dtos/quote_evidence.py]`, replace bare `Field(...)` assignments with modern `Annotated[T, Field(...)]` syntax and eliminate unannotated `dict(data)` parsing in favor of strict typed validation.
  13. *HumanOverrideDialog Flutter Theme Sovereignty & Spacing*: In `@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L265-L286]`, replace `const TextStyle(fontSize: 13)`, `const TextStyle(fontWeight: FontWeight.bold, fontSize: 11)`, and `const SizedBox(height: 8)` with `Theme.of(context).textTheme` tokens and `AppSpacing.h8` per Flutter Theme Sovereignty, and replace hardcoded string `'HUMAN_OVERRIDE'` with `l10n.humanOverrideDefaultBadge`.
  14. *SduiMatrixTableWidget Flutter Theme Sovereignty*: In `@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart#L550]`, replace `const TextStyle(fontWeight: FontWeight.w600, fontSize: 10)` with `Theme.of(context).textTheme` tokens.
  15. *Centralized Coercion SSOT*: In `@[backend_v2/models/core_base.py]`, establish the canonical `coerce_source_quotes_tuple` SSOT validator (safely wrapping single string inputs into 1-tuples, stripping whitespace, and discarding empty strings) to prevent string shattering across all downstream DTOs.
  16. *GateMatchResultDTO Typed Anti-Tuple SSOT*: In `@[backend_v2/models/dtos/quote_evidence.py]`, create and define `GateMatchResultDTO` (`is_valid: bool, start_idx: int, end_idx: int`) to eradicate anonymous 3-tuples across `AnchorValidationService` lexical gates, satisfying rule `ban_anonymous_state_tuples` and QGR015.
  17. *CausalInspectorModal Localization Parity*: In `@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L503-L540]`, replace hardcoded strings `'CITATION EVIDENCE'` and `'Location: '` with `l10n.causalInspectorCitationEvidenceHeader` and `l10n.causalInspectorLocationPrefix`.
- **Target Boundaries**:
  - `[DELETE] @[docs/epic/EPIC_MULTI_SEGMENT_EVIDENCE_AND_CAUSAL_HORIZON.md]` (verified duplicate Epic file removed to enforce Single Source of Truth)
  - `[MODIFY] @[backend_v2/models/core_base.py]` (implement `coerce_source_quotes_tuple` SSOT pre-validator preventing string shattering)
  - `[MODIFY] @[backend_v2/models/dtos/quote_evidence.py]` (cleanup bare `Field` assignments to `Annotated` syntax, and create defined `GateMatchResultDTO` anti-tuple SSOT)
  - `[MODIFY] @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]` (remediate hardcoded TextStyle, SizedBox, and hardcoded string to theme tokens and l10n)
  - `[MODIFY] @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]` (remediate hardcoded TextStyle to theme token)
  - `[MODIFY] @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]` (remediate hardcoded strings to l10n)
  - `[MODIFY] @[backend_v2/services/orchestrator/anchor_validation_service.py]` (enforce symmetric start/end index resolution via `pdf_map` for both exact and fuzzy/stemmed matches, eliminating raw unmapped quote appending and returning typed `GateMatchResultDTO`)
  - `[MODIFY] @[backend_v2/services/orchestrator/extractive_sensor_service.py]` (refactor `truncate_source_quote_at_sentence` into an immutable validator function)
  - `[MODIFY] @[backend_v2/services/orchestrator/sliding_window_linker.py]` (replace unannotated lambda dictionary factory with typed collection and clean up unused import)
  - `[MODIFY] @[backend_v2/services/export_evidence_formatter.py]` (refactor `format_text_observations` to strictly accept `quotes: tuple[str, ...] | None`)
  - `[MODIFY] @[backend_v2/services/sdui/adapters/printable_sources_adapter.py]` (prepare quote iteration for `eq.source_quotes`)
  - `[NEW] @[backend_v2/tests/unit/services/orchestrator/test_multi_segment_quote_foundation.py]` (scaffolding test file for multi-segment validation rules)
- **Verification Gate**:
  - `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test --ast-strict`
  - All existing unit tests pass cleanly without regressions.

### Phase 2: Domain Model, DTO, Client Freezed Contract & Test Fixture Multi-Segment Schema Refactoring (WP1)
- **Objective**: Refactor proposition and DAG models to represent evidence quotes as ordered tuples ($1 \le m \le 3$), enforcing Full-Duplex Parity across backend models, blackboard schemas, execution engines, projection pipelines, 1-hop caller services, Flutter Freezed consumer models, test factories, unit test suites, and golden master fixtures. In accordance with Stage 2 Critical Deployment Sequence, Flutter Freezed models and dependent citation widgets are updated synchronously in this phase so consumers support multi-segment arrays before backend producers serialize them and the client test suite compiles without errors.
- **Target Boundaries**:
  - `[MODIFY] @[backend_v2/models/core_base.py]` (export canonical `coerce_source_quotes_tuple` SSOT pre-validator for downstream DTO `BeforeValidator` annotations)
  - `[MODIFY] @[backend_v2/services/orchestrator/extractive_sensor_service.py]` (update `BooleanEvaluationResult` and `PreFlightResult` to `source_quotes: tuple[str, ...] | None = None` with `coerce_source_quotes_tuple` pre-validation coercion, Null Hypothesis invariants, and segment length limits)
  - `[MODIFY] @[backend_v2/models/domain/blackboard.py]` (update `DraftExtractedAtom` to `source_quotes: tuple[str, ...] | None = None` with `coerce_source_quotes_tuple` and Null Hypothesis validator parity)
  - `[MODIFY] @[backend_v2/models/dtos/dag_models.py]` (`ExtractedAtom.source_quotes: tuple[str, ...] | None` with `coerce_source_quotes_tuple`)
  - `[MODIFY] @[backend_v2/models/dtos/dag_models.py]` (`AtomEvaluationResultDTO.source_quotes: tuple[str, ...] | None` with `coerce_source_quotes_tuple`)
  - `[MODIFY] @[backend_v2/models/dtos/dag_models.py]` (`AtomExecutionState.source_quotes: tuple[str, ...] | None` with `coerce_source_quotes_tuple`)
  - `[MODIFY] @[backend_v2/models/dtos/causal_discovery.py]` (`CausalNodeDTO.source_quotes: tuple[str, ...] | None` with `coerce_source_quotes_tuple`)
  - `[MODIFY] @[backend_v2/models/dtos/atom_result.py]` (`AtomResultDTO.source_quotes: tuple[str, ...] | None` with `coerce_source_quotes_tuple` and cognitive validator parity)
  - `[MODIFY] @[backend_v2/models/dtos/atom_result.py]` (`HydratedAtomDTO.source_quotes: tuple[str, ...] | None` with `coerce_source_quotes_tuple`)
  - `[MODIFY] @[backend_v2/models/dtos/atom_result.py]` (`EvaluatedAtomDTO.source_quotes: tuple[str, ...] | None` with `coerce_source_quotes_tuple`)
  - `[MODIFY] @[backend_v2/models/dtos/atom_evaluation.py]` (`ReducedAtomDTO.source_quotes: tuple[str, ...] | None` with `coerce_source_quotes_tuple`)
  - `[MODIFY] @[backend_v2/models/dtos/quote_evidence.py]` (`QuoteEvidenceDTO` refactoring `quote: str` to `source_quotes: tuple[str, ...] | None` with `coerce_source_quotes_tuple`)
  - `[MODIFY] @[backend_v2/models/dtos/matrix_scorecard.py]` (`ScorecardAtomDTO.exact_quotes` holding `QuoteEvidenceDTO` with `source_quotes`)
  - `[MODIFY] @[backend_v2/models/dtos/report_artifact.py]` (`ReportRowItemDTO` quote field documentation and validation alignment)
  - `[MODIFY] @[backend_v2/services/sdui/sdui_mapper_service.py]` (project `evidence.source_quotes` joined with `" [...] "` into `SduiQuoteCard` and `SduiWarningCard`)
  - `[MODIFY] @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]` (update `hydrated_references` construction on line 266 to pass `source_quotes=None` instead of `source_quote=None`)
  - `[MODIFY] @[backend_v2/services/orchestrator/topological_evaluator.py]` (update line 163 state copy from `"source_quote": res.source_quote` to `"source_quotes": res.source_quotes`)
  - `[MODIFY] @[backend_v2/services/orchestrator/dag_executor.py]` (update lines 110-112 to format `node.source_quotes` and line 224 to check `if not n.source_quotes`)
  - `[MODIFY] @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]` (update lines 182-198 to anchor on `atom.source_quotes[0]` across paragraphs and document directives, and lines 250 & 333 for graph node compilation)
  - `[MODIFY] @[backend_v2/hooks/scoring/matrix_hook.py]` (update lines 421-426 to construct `QuoteEvidenceDTO(source_quotes=ev_dto.source_quotes, ...)`)
  - `[MODIFY] @[backend_v2/services/matrix_domain_parser.py]` (update lines 479-484 to construct `QuoteEvidenceDTO(source_quotes=val_data.source_quotes, ...)`)
  - `[MODIFY] @[backend_v2/services/report_service.py]` (update line 636 to project `quote=" [...] ".join(atom.source_quotes) if atom.source_quotes else None` in `ReportRowItemDTO`)
  - `[MODIFY] @[backend_v2/services/orchestrator/synthesis_distiller.py]` (update synthesis distillation to preserve `source_quotes`)
  - `[MODIFY] @[backend_v2/services/orchestrator/synthesis_payload_compressor.py]` (update payload compression to handle multi-segment `source_quotes`)
  - `[MODIFY] @[backend_v2/services/orchestrator/matrix_explanation_service.py]` (update explanation service to format multi-segment quotes)
  - `[MODIFY] @[backend_v2/services/orchestrator/result_projector.py]` (project multi-segment `source_quotes` into `AtomResultDTO` and `HydratedAtomDTO`)
  - `[MODIFY] @[backend_v2/services/orchestrator/state_reducer.py]` (reduce multi-segment `source_quotes` in state reducer)
  - `[MODIFY] @[backend_v2/services/orchestrator/matrix_reducer.py]` (pass `source_quotes=atom.source_quotes` when compiling `ReducedAtomDTO` instances)
  - `[MODIFY] @[backend_v2/services/orchestrator/two_pass_atomizer.py]` (pass multi-segment quote extraction in two-pass atomizer for `ExtractedAtom` and `DraftExtractedAtom`)
  - `[MODIFY] @[backend_v2/services/orchestrator/engines/tda_engine.py]` (update `ExtractedAtom` instantiations to pass `source_quotes=None`)
  - `[MODIFY] @[backend_v2/services/studio/simulation_service.py]` (update `ExtractedAtom` instantiations to pass `source_quotes=None`)
  - `[MODIFY] @[backend_v2/services/orchestrator/prompts/atom_extraction.py]` (update atom extraction prompts for multi-segment quote guidance)
  - `[MODIFY] @[backend_v2/models/prompts/execution/field_prompts.py]` (update `DESC_SOURCE_QUOTE` to reflect ordered multi-segment JSON schema requirements)
  - `[MODIFY] @[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]` (`QuoteEvidenceDto` updating `quote: String` to `sourceQuotes: List<String>?`)
  - `[MODIFY] @[client_app_v2/lib/features/execution/models/atom_result_dto.dart]` (`AtomResultDTO` updating `sourceQuote: String?` to `sourceQuotes: List<String>?`)
  - `[MODIFY] @[client_app_v2/lib/features/execution/models/causal_discovery_dto.dart]` (`CausalNodeDto` updating `sourceQuote: String?` to `sourceQuotes: List<String>?`)
  - `[MODIFY] @[client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart]` (`HydratedAtomDto` updating `sourceQuote: String?` to `sourceQuotes: List<String>?`)
  - `[MODIFY] @[client_app_v2/lib/features/execution/models/human_override_request_dto.dart]` (`evidenceQuotes: List<QuoteEvidenceDto>` Freezed parity)
  - `[MODIFY] @[client_app_v2/lib/features/studio/models/workflow.dart]` (`Workflow` adding `defaultLexicalStrictnessLevel: int`)
  - `[MODIFY] @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]` (update line 264 display to `q.sourceQuotes?.join(' [...] ') ?? ''` and lines 291-295 to pass `sourceQuotes: [l10n.humanOverrideExpertNote]`)
  - `[MODIFY] @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]` (update line 697 uniqueKey and line 749 text to `q.sourceQuotes?.join(' [...] ') ?? ''`)
  - `[MODIFY] @[backend_v2/tests/factories/model_factories.py]` (atomically update model factories to `source_quotes: tuple[str, ...] | None`)
  - `[MODIFY] @[backend_v2/llm/mock_data.py]` (atomically update mock LLM responses with `source_quotes` tuples)
  - `[MODIFY] @[backend_v2/tests/fixtures/sdui_golden_master.json]` (atomically update golden master fixtures)
  - `[MODIFY] @[backend_v2/tests/test_data/report_data_dto_fixture.json]` (atomically update report data DTO fixtures)
  - `[MODIFY] @[backend_v2/tests/unit/models/domain/test_blackboard.py]` (atomically update blackboard model assertions to `source_quotes`)
  - `[MODIFY] @[backend_v2/tests/unit/models/dtos/test_atom_result.py]` (atomically update atom result DTO assertions to `source_quotes`)
  - `[MODIFY] @[backend_v2/tests/unit/models/dtos/test_atom_evaluation.py]` (atomically update atom evaluation DTO assertions to `source_quotes`)
  - `[MODIFY] @[backend_v2/tests/unit/models/dtos/test_dag_models.py]` (atomically update DAG model assertions to `source_quotes`)
  - `[MODIFY] @[backend_v2/tests/unit/models/dtos/test_quote_evidence.py]` (atomically update quote evidence DTO assertions from `quote` to `source_quotes`)
  - `[MODIFY] @[backend_v2/tests/unit/models/dtos/test_matrix_scorecard.py]` (atomically update matrix scorecard assertions to `source_quotes`)
  - `[MODIFY] @[backend_v2/tests/unit/models/test_atom_result_override_guard.py]` (atomically update override guard assertions to `source_quotes`)
- **Verification Gate**:
  - `uv run pytest backend_v2/tests/unit/models/dtos/test_causal_discovery_dtos.py`
  - `uv run pytest backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py`
  - `uv run pytest backend_v2/tests/unit/models/domain/test_blackboard.py`
  - `uv run pytest backend_v2/tests/unit/models/dtos/test_atom_result.py backend_v2/tests/unit/models/dtos/test_atom_evaluation.py backend_v2/tests/unit/models/dtos/test_dag_models.py backend_v2/tests/unit/models/dtos/test_quote_evidence.py backend_v2/tests/unit/models/dtos/test_matrix_scorecard.py backend_v2/tests/unit/models/test_atom_result_override_guard.py`
  - `uv run python scripts/backend_audit_loop.py backend_v2/models/ --test --ast-strict`
  - `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`

### Phase 3: Lexical Firewall Multi-Segment & Distance Verification (Gates 1–4, WP2)
- **Objective**: Upgrade `AnchorValidationService` to validate multi-segment citation tuples, enforcing $\mathcal{M}_{idx}$ bidirectional byte-mapping, forward-scan search monotonic ordering ($s_k < e_k < s_{k+1}$), single-document buffer boundary isolation, and global span limit ($(e_m - s_1) \le 1\,000$ characters).
- **Target Boundaries**:
  - `[MODIFY] @[backend_v2/services/orchestrator/anchor_validation_service.py]` (enhance `normalize_text_with_mapping` with byte-range index bounds tracking)
  - `[MODIFY] @[backend_v2/services/orchestrator/anchor_validation_service.py]` (update `strict_match` to accept multi-segment ordered tuples)
  - `[MODIFY] @[backend_v2/services/orchestrator/anchor_validation_service.py]` (enhance `_is_lexically_valid` with forward-scan search `norm_doc.find(norm_q_k, prev_segment_end_idx)` and single-document isolation)
  - `[MODIFY] @[backend_v2/services/orchestrator/anchor_validation_service.py]` (update `validate_evidence` for multi-segment validation and provenance stream isolation)
  - `[MODIFY] @[backend_v2/models/prompts/execution/matrix_evaluation.py]` (update `evidence_extraction_mandate` to allow 1–3 non-contiguous sentences while maintaining the Chimera and Ellipsis bans)
- **Verification Gate**:
  - `uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py`
  - ISTQB negative tests: inverted segment order ($s_2 < s_1$) raises `SemanticEvidenceError`; repeated phrase prior to $q_1$ does not cause false rejection; cross-document chimera raises `SemanticEvidenceError`; span exceeding 1 000 chars raises `SemanticEvidenceError`; segment $<30$ chars when $m > 1$ raises `ValidationError`.

### Phase 4: Strictness Decoupling SSOT & Gate 5 Morphological Calibration (WP2)
- **Objective**: Decouple lexical verification strictness ($\zeta_{lex}$) from scoring dampening strictness ($\zeta_{score}$), establishing independent `Workflow` and Studio DTO fields, synchronizing seed data, and calibrating Gate 5 Snowball stemming.
- **Target Boundaries**:
  - `[MODIFY] @[backend_v2/models/domain/workflow.py]` (add `default_lexical_strictness_level: int = Field(default=50, ge=0, le=100)`)
  - `[MODIFY] @[backend_v2/models/dtos/studio.py]` (add `default_lexical_strictness_level: int = Field(default=50, ge=0, le=100)`)
  - `[MODIFY] @[backend_v2/services/studio/workflow_service.py]` (transit `default_lexical_strictness_level` in Studio workflow CRUD operations)
  - `[MODIFY] @[backend_v2/seed/seed_data.json#L20538-L21331]` (atomically synchronize workflow seeds with `default_lexical_strictness_level: 50`)
  - `[MODIFY] @[backend_v2/settings.py]` (ensure `get_lexical_fuzz_threshold` incorporates decoupled lexical strictness parameter)
  - `[MODIFY] @[backend_v2/workers/execution_worker.py]` (extract both `strictness_level` and `lexical_strictness_level` from workflow and transit to DAG executor)
  - `[MODIFY] @[backend_v2/services/orchestrator/dag_executor.py]` (transit decoupled lexical strictness through execution context)
  - `[MODIFY] @[backend_v2/services/orchestrator/extractive_sensor_service.py]` (accept and pass `lexical_strictness_level` to `AnchorValidationService`)
  - `[MODIFY] @[backend_v2/l10n/fi.json]` & `[MODIFY] @[backend_v2/l10n/en.json]` (add localization strings for lexical strictness)
- **Verification Gate**:
  - `uv run pytest backend_v2/tests/unit/workers/test_execution_worker.py`
  - `uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py`
  - `uv run python backend_v2/seed/run_seed.py local --dry-run` validating all seeded workflows
  - Verification test asserting that high scoring strictness ($\zeta_{score} = 85$) with default lexical strictness ($\zeta_{lex} = 50$) permits valid Finnish grammatical case inflections via Snowball stemmer.

### Phase 5: Long-Range Causal Horizon Expansion & Global Context Anchor Header for Root Axioms (WP3)
- **Objective**: Upgrade `SlidingWindowLinker` to anchor deliverable root axioms ($InDegree(v)=0$) as a persistent Global Context Anchor header block across subsequent sliding windows (as formally specified in `@[docs/tiede.md]` Table 8 Row 4), eliminating the Sitra long-range truncation defect while enforcing dynamic budget allocation.
- **Target Boundaries**:
  - `[MODIFY] @[backend_v2/services/orchestrator/sliding_window_linker.py]` (implement bounded deliverable root axiom header injection with dynamic quota allocation: guaranteed minimum current window quota $W_{min} = 12$, dynamic root axiom allocation $K_{eff} = \min(8, \max(0, M_{win} - W_{current}))$, candidate sorting by `(-OutDegree(v), atom_index_asc)`, and hard budget guard $M_{win} \le 20$)
  - `[MODIFY] @[backend_v2/services/orchestrator/sliding_window_linker.py]` (support multi-segment Toulmin warrants $\lambda(W_{P'C}) = 1$ in `CausalEdge` creation)
  - `[MODIFY] @[backend_v2/services/orchestrator/causal_cohesion_evaluator.py]` (Algorithm 1 dual fault attribution: separate multi-segment warrant validation failure into `CausalRootCauseType.WARRANT_GROUNDING_FAILURE`)
  - `[MODIFY] @[backend_v2/settings.py]` (add `linker_max_global_root_axioms: int = 8`)
- **Verification Gate**:
  - `uv run pytest backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py`
  - `uv run pytest backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py`
  - Unit test verifying deterministic root axiom selection, dynamic budget allocation ($W_{min}=12, K_{eff} \le 8$), and that sliding window prompt atom count never exceeds `linker_max_atoms_per_window` even when $>20$ root axioms exist.

### Phase 6: Presentation Projection, Tabular Export, OpenAPI & Frontend UI Presentation Synchronization (WP1 & WP3)
- **Objective**: Synchronize presentation projection, tabular export streaming, Jinja2 PDF templates, and Studio UI controls with the multi-segment schema and decoupled strictness controls. Note: Client Freezed DTO schemas are synchronized ahead in Phase 2; Phase 6 focuses strictly on UI widgets, presentation adapters, and export compilation.
- **Target Boundaries**:
  - `[MODIFY] @[backend_v2/services/export_service.py]` (format multi-segment quotes as `" [...] ".join(source_quotes)` in `ExportForensicAtomDTO`)
  - `[MODIFY] @[backend_v2/services/export_evidence_formatter.py]` (ensure clean handling of multi-segment tuples with `" [...] ".join(quotes)`)
  - `[MODIFY] @[backend_v2/scripts/generate_openapi.py]` (synchronize OpenAPI generation script with multi-segment quote schema)
  - `[MODIFY] @[docs/swagger/openapi.json]` (regenerate OpenAPI schema artifact to reflect `source_quotes: tuple[str, ...] | None`)
  - `[MODIFY] @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]` (format multi-segment citations in SDUI XAI highlights)
  - `[MODIFY] @[backend_v2/services/sdui/adapters/printable_sources_adapter.py]` (format multi-segment citations in printable sources, iterating over `eq.source_quotes`)
  - `[MODIFY] @[backend_v2/templates/report_template.jinja2]` (update quote rendering in line 478 from scalar `{{ quote.quote }}` to multi-segment delimiter `{{ quote.source_quotes | join(' [...] ') if quote.source_quotes else '' }}`, eliminating silent empty quote omissions in PDF generation)
  - `[MODIFY] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_strictness_tab.dart]` (implement independent continuous slider for lexical strictness)
  - `[MODIFY] @[client_app_v2/lib/l10n/app_fi.arb]` & `[MODIFY] @[client_app_v2/lib/l10n/app_en.arb]` (add studio strictness and citation widget localization keys: `causalInspectorCitationEvidenceHeader`, `causalInspectorLocationPrefix`, `humanOverrideDefaultBadge`)
  - `[MODIFY] @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]` (update line 563 quote rendering to `"${q.sourceQuotes?.join(' [...] ') ?? ''}"`)
  - `[MODIFY] @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L499-L535]` (update lines 499-500 null check and line 530 scalar quote interpolation to `node.sourceQuotes?.join(' [...] ') ?? ''`)
- **Verification Gate**:
  - `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`
  - `uv run pytest backend_v2/tests/unit/test_report_headers_l10n_parity.py`
  - `uv run pytest backend_v2/tests/unit/test_pdf_generator.py` (assert rendered PDF/HTML contains non-empty multi-segment evidence quotes)

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

### Phase 8: As-Built Architectural Documentation & Scientific Manuscript Synchronization (`@[docs/tiede.md]`)
- **Objective**: Execute the post-implementation `/tier7-describe-architecture` audit to synchronize target Knowledge Items, timeless architecture pillars, directory references, and update `@[docs/tiede.md]` with rigorous academic prose, formal mathematical definitions, theorems, and verified empirical proofs.
- **Target Boundaries**:
  - `[MODIFY] @[.agents/rules/04_directory_reference.md]` (register newly created integration tests and updated service components)
  - `[MODIFY] @[docs/tiede.md]` (synchronize academic scientific manuscript: formalize Definition 1 ordered bounding span vector $\vec{\mathcal{C}}_i = (\mathcal{C}_{i,1}, \dots, \mathcal{C}_{i,m})$ where $1 \le m \le 3$, monotonic ordering $s_1 < e_1 < s_2 < e_2 \le s_1 + 1\,000$, and buffer boundary isolation; formalize Theorem on Lexical Specificity Invariant $\text{Specificity}_{lex} = 1.000$ under bounded spans; formalize Section 4.1.1 Gate 5 Epistemic Decoupling separating $\zeta_{lex}$ from $\zeta_{score}$; formalize Section 5 Bounded Deliverable Root Axiom Anchoring $K_{axiom}^{max} = 8$ with invariant header preserving the Local Causal Markov Condition; incorporate empirical findings in Section 8: reduction of $\widehat{FOR}$ from $13.33\%$ to $\le 2.00\%$, $FOR_{omission} \to 0.00\%$, $FOR_{rejection} \to 0.00\%$, ablation benchmark pass rate $\ge 56.4\%$, and $\bar{\kappa} \ge 0.9800$)
- **Execution Directives for Tier 7 Agent**:
  - Command: `/tier7-describe-architecture [NEW] @[docs/epic/EPIC_158_tracker.md] @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md] @[ki_structured_forensic_quotes.md] @[ki_topological_engine.md] @[ki_unified_matrix_scoring_strictness.md] @[ki_prompt_orchestration_and_matrix_evaluation.md]`
  - Directives:
    1. **Target KIs to Synchronize**: `@[ki_structured_forensic_quotes.md]`, `@[ki_topological_engine.md]`, `@[ki_unified_matrix_scoring_strictness.md]`, `@[ki_prompt_orchestration_and_matrix_evaluation.md]`.
    2. **Directory Reference Sync**: `@[.agents/rules/04_directory_reference.md]`.
    3. **Pillar Documentation Sync**: `@[docs/architecture/01_system_context_and_invariants.md]`, `@[docs/architecture/03_cognitive_orchestration_engine.md]`, `@[docs/architecture/04_server_driven_ui_and_presentation.md]`.
    4. **Scientific Manuscript Proof & Synthesis (`@[docs/tiede.md]`)**: Formalize the mathematical definitions, theorems, proofs, and empirical ablation tables in academic English with LaTeX notation parity.
- **Verification Gate**:
  - All target KIs updated with accurate `metadata.json` timestamps.
  - `docs/tiede.md` LaTeX syntax and mathematical equations render cleanly and reflect verified empirical results from Phase 7 benchmark.

---

## 4. Definition of Done (DoD) & Verification Plan

### 4.1 Definition of Done (DoD)
The epic is complete when:
1. `BooleanEvaluationResult`, `DraftExtractedAtom`, `ExtractedAtom`, `AtomEvaluationResultDTO`, `AtomExecutionState`, `CausalNodeDTO`, `AtomResultDTO`, `HydratedAtomDTO`, and `QuoteEvidenceDTO` transit evidence quotes as immutable `tuple[str, ...] | None` ($1 \le m \le 3$) with 100% Pydantic V2 strict typing and `coerce_source_quotes_tuple` pre-validation coercion.
2. `AnchorValidationService` verifies multi-segment quotes with bidirectional $\mathcal{M}_{idx}$ mapping, enforcing forward-scan monotonic byte order ($s_1 < e_1 < \dots < s_m < e_m$), span limit $(e_m - s_1) \le 1\,000$ characters, single-document buffer boundary isolation (`source_input_key`), and individual segment length $\ge 30$ characters for $m > 1$.
3. Lexical strictness $\zeta_{lex}$ and scoring strictness $\zeta_{score}$ operate as sovereign, decoupled fields on `Workflow` (`default_strictness_level` and `default_lexical_strictness_level`), synchronized across database seeds, Studio DTOs (`WorkflowCreateDTO`, `WorkflowUpdateDTO`, `WorkflowResponseDTO`), and Flutter Studio UI sliders.
4. `SlidingWindowLinker` anchors deliverable root axioms ($InDegree(v)=0$) with dynamic budget allocation ($W_{min}=12, K_{eff} \le 8, M_{win} \le 20$) and deterministic tie-breaking sort order `(-OutDegree(v), atom_index_asc)`, reducing deliverable isolation ratio in extended documents below $r_{L3}^{max} = 0.20$.
5. Algorithm 1 dual fault attribution categorizes ungrounded multi-segment warrants as `CausalRootCauseType.WARRANT_GROUNDING_FAILURE` without penalizing child node claims.
6. Export formatters (`ExportForensicAtomDTO`, `export_evidence_formatter.py`), SDUI adapters (`xai_highlights_adapter.py`, `printable_sources_adapter.py`), Jinja2 PDF templates (`report_template.jinja2#L478` rendering `{{ quote.source_quotes | join(' [...] ') }}`), and Flutter Freezed DTOs maintain 100% full-duplex cross-platform parity.
7. All automated quality gates, AST guardrails, and live integration tests pass with zero warnings, zero suppressions, and zero regressions.
8. **As-Built Architectural Documentation & Scientific Manuscript Synchronization**: The fully parameterized `/tier7-describe-architecture` command is executed, synchronizing target KIs (`ki_structured_forensic_quotes.md`, `ki_topological_engine.md`, `ki_unified_matrix_scoring_strictness.md`, `ki_prompt_orchestration_and_matrix_evaluation.md`), `.agents/rules/04_directory_reference.md`, architectural pillars (`01_`, `03_`, `04_`), and `docs/tiede.md` is updated with formal mathematical proofs (ordered bounding span vector, chimera invariance, epistemic decoupling, and bounded root axiom preservation of the Local Causal Markov Condition) and verified empirical benchmark results.

### 4.2 Automated Unit & Integration Tests
- **Backend Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`
- **Frontend Build & Parity Gate**: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`
- **Multi-Segment Lexical Tests**: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py -v`
- **Sensor Schema Tests**: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py -v`
- **Blackboard Schema Tests**: `uv run pytest backend_v2/tests/unit/models/domain/test_blackboard.py -v`
- **Causal Linking & Horizon Tests**: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py -v`
- **Fault Attribution Tests**: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_causal_cohesion_scoring.py -v`
- **Export Serializer Tests**: `uv run pytest backend_v2/tests/unit/models/dtos/test_export.py -v`
- **Jinja2 PDF Rendering Parity Tests**: `uv run pytest backend_v2/tests/unit/test_pdf_generator.py -v` and `uv run pytest backend_v2/tests/unit/test_sdui_template_parity.py -v`
- **ISTQB Boundary Coverage**:
  - Multi-segment span $>1\,000$ chars triggers `SemanticEvidenceError`.
  - Inverted segment order ($s_2 < s_1$) triggers `SemanticEvidenceError`.
  - Repeated phrase prior to $q_1$ does not cause false rejection via forward-scan search.
  - Cross-document segment stitching raises `SemanticEvidenceError` via buffer boundary check.
  - JSON array deserialization under Pydantic V2 `strict=True` resolves cleanly to immutable `tuple[str, ...]`.
  - Non-empty quote on `is_true=False` triggers Pydantic `ValidationError`.
  - Segment $<30$ chars when $m > 1$ triggers `ValidationError`.
  - Window atom count exceeding `linker_max_atoms_per_window` is safely bounded by dynamic allocation ($W_{min}=12, K_{eff} \le 8$) with deterministic tie-breaking.

### 4.3 AST Guardrails & Structural Tests
- `QGR001` - `QGR016`: Full enforcement via `_ast_guardrails.py` with zero `# noqa` or `# type: ignore` suppressions.
- Boundary Exemption Verification: Zero raw dictionary transit outside the canonical `BOUNDARY_EXEMPTION_FILES`.
- Freezed Model Parity: Exact synchronization between backend Python `source_quotes` and Dart `sourceQuotes`.

### 4.4 Manual Verification Steps
1. **Database Seeding Verification**: Run `uv run python backend_v2/seed/run_seed.py local --dry-run` to ensure all workflow configurations validate against the updated Pydantic schema with decoupled strictness fields.
2. **Tabular Export Inspection**: Generate CSV and Excel exports from a test run; verify that multi-segment quotes appear properly formatted (`" [...] "`) in the 14-column forensic atom sheet without truncating cell values.
3. **Studio UI Audit**: Verify that Quorum Studio Workflow Editor displays both strictness controls (Scoring Strictness and Lexical Strictness) with independent continuous sliders.
4. **Matrix Table & Inspector Citation Audit**: Verify in Quorum Client Desktop UI that `sdui_matrix_table_widget.dart` (line 563) and `causal_inspector_modal.dart` (lines 499-535) render multi-segment citations without truncation or unescaped brackets.
5. **Scientific Manuscript Verification (`docs/tiede.md`)**: Inspect `docs/tiede.md` for mathematical rigor, formal LaTeX notation parity, consistent theorem numbering, and exact empirical alignment with Phase 7 benchmark metrics.

### 4.5 Mandatory Final E2E REST API Verification Gate
```powershell
$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

---

## 5. Required Context & Governance (Rules & KI Registry)

See the canonical `<required_context_rules>` XML block at the top of this document for the authoritative registry of active rules and Knowledge Items.
