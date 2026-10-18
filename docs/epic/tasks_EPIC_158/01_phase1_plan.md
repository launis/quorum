# Phase 1: Pre-Implementation Technical Debt Cleanups & Foundations

**Overview:** Remediate discovered technical debt in touched target files, eliminate SSOT duplicate documents, establish canonical `coerce_source_quotes_tuple` and `GateMatchResultDTO` anti-tuple SSOTs, clean up unannotated collections, and prepare test scaffolding before introducing multi-segment extraction logic.

**Source:** @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md#L195-L231] Phase 1: Pre-Implementation Technical Debt Cleanups & Foundations

**Target Files:**
- `[DELETE]` @[docs/epic/EPIC_MULTI_SEGMENT_EVIDENCE_AND_CAUSAL_HORIZON.md]
- `[MODIFY]` @[backend_v2/models/core_base.py]
- `[MODIFY]` @[backend_v2/models/dtos/quote_evidence.py#L113-L206]
- `[MODIFY]` @[backend_v2/services/orchestrator/anchor_validation_service.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/extractive_sensor_service.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/sliding_window_linker.py]
- `[MODIFY]` @[backend_v2/services/export_evidence_formatter.py]
- `[MODIFY]` @[backend_v2/services/export_service.py]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/printable_sources_adapter.py]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L265-L286]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L503-L540]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_en.arb]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_fi.arb]
- `[MODIFY]` @[backend_v2/tests/unit/models/dtos/test_quote_evidence.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_export_evidence_formatter.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/test_multi_segment_quote_foundation.py]

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| [DELETE] `@[docs/epic/EPIC_MULTI_SEGMENT_EVIDENCE_AND_CAUSAL_HORIZON.md]` | Banned duplicate Epic documents competing with canonical specification. | Verify physical non-existence of duplicate file; maintain single SSOT in `@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]`. | Pruned dual tracking; enforce single authoritative Epic document. | File non-existence check on disk. |
| `@[backend_v2/models/core_base.py]` | Banned string shattering `tuple("str")` character splitting and unvalidated tuple construction. | Establish `coerce_source_quotes_tuple` SSOT pre-validator wrapping single string inputs into 1-tuples, stripping whitespace, and discarding empty strings. | Pruned multiple per-model string converters; centralize in core base. | `pytest backend_v2/tests/unit/services/orchestrator/test_multi_segment_quote_foundation.py` asserting string coercion to 1-tuple. |
| `@[backend_v2/models/dtos/quote_evidence.py#L113-L206]` | Banned bare `Field(...)` assignments, unannotated `dict(data)` parsing, and anonymous 3-tuples `(is_valid, start, end)` violating rule `ban_anonymous_state_tuples` and QGR015. | Replace bare `Field(...)` with `Annotated[T, Field(...)]` syntax, implement `get_quotes()` SSOT accessor, and define strongly typed immutable Pydantic V2 DTO `GateMatchResultDTO(is_valid: bool, start_idx: int, end_idx: int)`. | Pruned anonymous tuple unpacking; encapsulate coordinate matching results in typed DTO. | `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/quote_evidence.py --test --ast-strict`. |
| `@[backend_v2/services/orchestrator/anchor_validation_service.py]` | Banned asymmetric quote extraction where exact matches resolve coordinates but fuzzy/stemmed matches append raw unmapped quotes. | Enforce symmetric start/end index resolution via `pdf_map` for both exact and fuzzy/stemmed matches, returning strongly typed `GateMatchResultDTO`. | Pruned divergent extraction code paths; unified under symmetric coordinate mapper. | `pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py`. |
| `@[backend_v2/services/orchestrator/extractive_sensor_service.py]` | Banned mutating `truncate_source_quote_at_sentence` pre-validator clipping candidate quote strings. | Deprecate and remove mutating pre-validator in favor of immutable boundary validation that asserts segment length limits without mutating source text. | Pruned in-place mutation logic; enforce pure boundary assertions. | `pytest backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py`. |
| `@[backend_v2/services/orchestrator/sliding_window_linker.py]` | Banned unannotated lambda dictionary factory `defaultdict(lambda: WindowCausalEdgesDTO(edges={}))`, `defaultdict(list)`, and repeated `get_settings()` calls in loops. | Inject `settings: Settings | None = None` in `__init__`, access `self.max_atoms_per_window`, and replace `defaultdict` with explicit typed dictionary initialization. | Pruned anonymous factory closures and global settings fetches in loop; enforce clean DI. | `pytest backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py`. |
| `@[backend_v2/services/export_evidence_formatter.py]` | Banned union duck-typing in `format_text_observations(quotes: list[str] \| str \| None)`. | Refactor to strictly typed signature `format_text_observations(quotes: tuple[str, ...] \| None) -> str`. | Pruned loose type alternatives; lock signature to immutable tuple. | `pytest backend_v2/tests/unit/services/test_export_evidence_formatter.py`. |
| `@[backend_v2/services/export_service.py]` | Banned passing unvalidated raw scalar strings or loose lists into strictly typed formatter signatures. | Wrap raw quote collections with canonical `coerce_source_quotes_tuple(quote_raw)` before delegating to `format_text_observations`. | Pruned ad-hoc string inspections at export boundaries; delegate to core coercion SSOT. | `pytest backend_v2/tests/unit/services/test_export_service.py`. |
| `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]` | Banned direct scalar attribute access `eq.quote` risking runtime `AttributeError` or speculative access to unmigrated fields. | Iterate safely over `eq.get_quotes()` returning `tuple[str, ...]` with full forwards-compatibility and zero `hasattr`/`getattr` QGR violations. | Pruned unsafe scalar assumptions; encapsulate quote extraction in DTO method. | `pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`. |
| `@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L265-L286]`, `@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]`, `@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L503-L540]` | Banned hardcoded `const TextStyle`, `const SizedBox`, and unlocalized strings `'HUMAN_OVERRIDE'`, `'CITATION EVIDENCE'`, `'Location: '`. | Replace hardcoded typography and sizing with `Theme.of(context).textTheme` tokens and `AppSpacing.h8`; bind strings to `l10n.humanOverrideDefaultBadge`, `l10n.causalInspectorCitationEvidenceHeader`, and `l10n.causalInspectorLocationPrefix`. | Pruned bespoke widget styles; conform strictly to Flutter Theme Sovereignty. | `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`. |
| `@[client_app_v2/lib/l10n/app_en.arb]`, `@[client_app_v2/lib/l10n/app_fi.arb]` | Banned unlocalized strings and referencing non-existent localization getters in widgets. | Add `humanOverrideDefaultBadge`, `causalInspectorCitationEvidenceHeader`, and `causalInspectorLocationPrefix` with descriptive English and Finnish translations. | Pruned hardcoded UI literals; enforce compile-time Dual-Axis localization parity. | `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`. |
| [NEW] `@[backend_v2/tests/unit/services/orchestrator/test_multi_segment_quote_foundation.py]` | Banned developing multi-segment logic without dedicated pre-flight test scaffolding. | Implement comprehensive test suite covering `coerce_source_quotes_tuple`, `GateMatchResultDTO`, `get_quotes()` accessor, and coordinate symmetry. | Pruned scattered assertions; consolidate foundation verification into dedicated suite. | `pytest backend_v2/tests/unit/services/orchestrator/test_multi_segment_quote_foundation.py`. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state. Verify `EPIC_MULTI_SEGMENT_EVIDENCE_AND_CAUSAL_HORIZON.md` is removed to retain single SSOT in `EPIC_158_multi_segment_evidence_and_causal_horizon.md`.</action>
    <action>Look forward: Verify baseline state in @[backend_v2/models/core_base.py], @[backend_v2/models/dtos/quote_evidence.py#L113-L206], and @[backend_v2/services/orchestrator/anchor_validation_service.py] before introducing multi-segment extraction foundations.</action>
    <constraint invariant="universal_fail_fast">If alignment is broken or files are missing, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]) and the Tracker document (@[docs/epic/EPIC_158_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_158/01_phase1_plan.md] @[docs/epic/EPIC_158_tracker.md]`.</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/models/core_base.py]</backend>
    <backend>@[backend_v2/models/dtos/quote_evidence.py]</backend>
    <backend>@[backend_v2/services/orchestrator/anchor_validation_service.py]</backend>
    <backend>@[backend_v2/services/orchestrator/extractive_sensor_service.py]</backend>
    <backend>@[backend_v2/services/orchestrator/sliding_window_linker.py]</backend>
    <backend>@[backend_v2/services/export_evidence_formatter.py]</backend>
    <backend>@[backend_v2/services/export_service.py]</backend>
    <backend>@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]</backend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_en.arb]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_fi.arb]</frontend>
  </touched_artifacts>

  <dod_checklist>
    <item>Duplicate Epic [DELETE] @[docs/epic/EPIC_MULTI_SEGMENT_EVIDENCE_AND_CAUSAL_HORIZON.md] verified non-existent on disk to maintain single SSOT.</item>
    <item>Canonical `coerce_source_quotes_tuple` SSOT pre-validator implemented in @[backend_v2/models/core_base.py], wrapping single strings into 1-tuples, stripping whitespace, and rejecting empty strings.</item>
    <item>Bare `Field(...)` assignments replaced with `Annotated[T, Field(...)]`, `get_quotes()` accessor defined, and `GateMatchResultDTO` anti-tuple contract defined in @[backend_v2/models/dtos/quote_evidence.py#L113-L206].</item>
    <item>Asymmetric quote extraction in @[backend_v2/services/orchestrator/anchor_validation_service.py] remediated by enforcing symmetric start/end index resolution via `pdf_map` and returning `GateMatchResultDTO`.</item>
    <item>Mutating `truncate_source_quote_at_sentence` pre-validator removed from `BooleanEvaluationResult` in @[backend_v2/services/orchestrator/extractive_sensor_service.py].</item>
    <item>Unannotated lambda dictionary factory replaced with typed dictionary and settings injected via `__init__` in @[backend_v2/services/orchestrator/sliding_window_linker.py].</item>
    <item>Union duck-typing in `format_text_observations` eliminated in @[backend_v2/services/export_evidence_formatter.py] in favor of `quotes: tuple[str, ...] | None`, and 1-hop caller in @[backend_v2/services/export_service.py] updated with `coerce_source_quotes_tuple`.</item>
    <item>Direct scalar quote access `eq.quote` remediated in @[backend_v2/services/sdui/adapters/printable_sources_adapter.py] using `eq.get_quotes()`.</item>
    <item>Hardcoded typography, spacing, and strings replaced with Theme tokens, `AppSpacing.h8`, and `l10n` keys in @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L265-L286], @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart], and @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L503-L540].</item>
    <item>Missing localization keys added to @[client_app_v2/lib/l10n/app_en.arb] and @[client_app_v2/lib/l10n/app_fi.arb] with 100% Dual-Axis localization parity.</item>
    <item>Foundation test suite [NEW] @[backend_v2/tests/unit/services/orchestrator/test_multi_segment_quote_foundation.py] created and passing 100%.</item>
  </dod_checklist>

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

  <anti_targets>
    <anti_target>Do NOT introduce multi-segment extraction logic into prompt builders or execution workers in Phase 1.</anti_target>
    <anti_target>Do NOT mutate downstream DAG models or client Freezed contracts prior to Phase 2.</anti_target>
    <anti_target>Do NOT relax Pydantic strictness or introduce anonymous tuple returns.</anti_target>
  </anti_targets>

  <contract_freeze>
    <contract id="coerce_source_quotes_tuple">
      <signature>def coerce_source_quotes_tuple(v: object) -> tuple[str, ...] | None</signature>
      <invariants>Wraps string into 1-tuple; safely converts iterables; strips whitespace; returns None if empty.</invariants>
    </contract>
    <contract id="GateMatchResultDTO">
      <signature>class GateMatchResultDTO(BaseModel): is_valid: bool; start_idx: int; end_idx: int</signature>
      <invariants>Immutable Pydantic V2 model with ConfigDict(strict=True, extra="forbid", frozen=True).</invariants>
    </contract>
    <contract id="QuoteEvidenceDTO_get_quotes">
      <signature>def get_quotes(self) -> tuple[str, ...]</signature>
      <invariants>Extracts available quotes as immutable tuple without reflection or hasattr/getattr calls.</invariants>
    </contract>
  </contract_freeze>

  <step id="1" name="ELIMINATE DUPLICATE EPIC &amp; ESTABLISH CORE COERCION SSOT">
    <action>In [DELETE] @[docs/epic/EPIC_MULTI_SEGMENT_EVIDENCE_AND_CAUSAL_HORIZON.md]: Verify physical non-existence of duplicate Epic file on disk, ensuring `EPIC_158_multi_segment_evidence_and_causal_horizon.md` remains the sole SSOT.</action>
    <action>In @[backend_v2/models/core_base.py]: Implement and export `coerce_source_quotes_tuple(v: object) -> tuple[str, ...] | None`. Enforce explicit `isinstance(v, str)` check wrapping non-empty stripped string into `(v.strip(),)`, filter empty strings from sequences, and convert valid sequences into immutable tuples.</action>
    <constraint invariant="the_zero_compromise_pledge">Prevent string shattering `tuple("abc") -> ('a', 'b', 'c')` by explicitly checking for `str` type.</constraint>
  </step>

  <step id="2" name="MODERNIZE QUOTE EVIDENCE CONTRACT &amp; CREATE GATEMATCHRESULTDTO">
    <action>In @[backend_v2/models/dtos/quote_evidence.py#L113-L206]: Refactor bare `Field(...)` assignments to `Annotated[T, Field(...)]` syntax. Define strongly typed immutable model `GateMatchResultDTO(is_valid: bool, start_idx: int, end_idx: int)` with `ConfigDict(strict=True, extra="forbid", frozen=True)` to eradicate anonymous 3-tuples.</action>
    <action>In @[backend_v2/models/dtos/quote_evidence.py]: Implement `get_quotes()` accessor method returning `(self.quote,) if self.quote and self.quote.strip() else ()` for forwards-compatibility without reflection.</action>
    <action>In @[backend_v2/models/dtos/quote_evidence.py]: Eliminate unannotated `dict(data)` parsing in favor of strict typed validation.</action>
    <action>In @[backend_v2/tests/unit/models/dtos/test_quote_evidence.py]: Add unit test coverage for `get_quotes()` and `GateMatchResultDTO` validation.</action>
    <constraint invariant="ban_anonymous_state_tuples">Enforce QGR015 compliance by returning typed `GateMatchResultDTO` instead of `tuple[bool, int, int]`.</constraint>
  </step>

  <step id="3" name="REMEDIATE ANCHOR VALIDATION SERVICE COORDINATE PARITY">
    <action>In @[backend_v2/services/orchestrator/anchor_validation_service.py]: Remediate asymmetric quote extraction in `validate_evidence` by enforcing symmetric start and end index resolution via `pdf_map` for both exact and fuzzy/stemmed matches, eliminating raw unmapped quote appending.</action>
    <action>In @[backend_v2/services/orchestrator/anchor_validation_service.py]: Update lexical matching gates (`strict_match`, `_is_lexically_valid`) to return strongly typed `GateMatchResultDTO`.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]: Synchronize test assertions to reflect exact slice extraction from source text across fuzzy fallback gates.</action>
    <constraint invariant="single_pipeline_lexical_unification">All evidence matching gates must return normalized document coordinate bounds within `GateMatchResultDTO`.</constraint>
  </step>

  <step id="4" name="CLEAN UP SENSOR PRE-VALIDATOR &amp; LINKER UNANNOTATED FACTORIES">
    <action>In @[backend_v2/services/orchestrator/extractive_sensor_service.py]: Remove mutating `truncate_source_quote_at_sentence` pre-validator on `BooleanEvaluationResult`. Replace with pure boundary assertions enforcing string length limits without mutating text.</action>
    <action>In @[backend_v2/services/orchestrator/sliding_window_linker.py]: Replace unannotated lambda dictionary factory `defaultdict(lambda: WindowCausalEdgesDTO(edges={}))` and `defaultdict(list)` with explicit typed collection initialization.</action>
    <action>In @[backend_v2/services/orchestrator/sliding_window_linker.py]: Inject `settings: Settings | None = None` in `__init__`, binding `self.max_atoms_per_window = (settings or get_settings()).linker_max_atoms_per_window`, eliminating repeated calls to `get_settings()` in sliding window loops.</action>
    <constraint invariant="the_duct_tape_ban">Zero in-place string truncation mutations; zero unannotated lambda dictionary factories.</constraint>
  </step>

  <step id="5" name="REFINE EXPORT FORMATTER &amp; ADAPTER TYPING STRICTNESS">
    <action>In @[backend_v2/services/export_evidence_formatter.py]: Refactor `format_text_observations(quotes: list[str] | str | None)` to strictly typed signature `format_text_observations(quotes: tuple[str, ...] | None) -> str`.</action>
    <action>In @[backend_v2/services/export_service.py]: Update 1-hop callers of `format_text_observations` on lines 558, 610, 758, and 826 to wrap inputs using `coerce_source_quotes_tuple(quote_raw)`, ensuring strict tuple type passing without breaking runtime export generation.</action>
    <action>In @[backend_v2/services/sdui/adapters/printable_sources_adapter.py]: Remediate direct scalar attribute access `eq.quote` on line 318 in favor of safe iteration over `eq.get_quotes()` returning `tuple[str, ...]`, providing forward compatibility without reflection or QGR violations.</action>
    <action>In @[backend_v2/tests/unit/services/test_export_evidence_formatter.py]: Update unit tests to pass tuples instead of lists or strings, verifying full compatibility with coerce_source_quotes_tuple output.</action>
    <constraint invariant="zero_permissive_typing">Prohibit union duck-typing in export formatters.</constraint>
  </step>

  <step id="6" name="REMEDIATE FLUTTER THEME SOVEREIGNTY &amp; LOCALIZATION">
    <action>In @[client_app_v2/lib/l10n/app_en.arb] and @[client_app_v2/lib/l10n/app_fi.arb]: Add new localization keys `humanOverrideDefaultBadge` ("Human Override" / "Manuaalinen ohitus"), `causalInspectorCitationEvidenceHeader` ("Citation Evidence" / "Sitaattitodisteet"), and `causalInspectorLocationPrefix` ("Location: " / "Sijainti: ") with corresponding descriptions.</action>
    <action>In @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L265-L286]: Replace `const TextStyle(fontSize: 13)`, `const TextStyle(fontWeight: FontWeight.bold, fontSize: 11)`, and `const SizedBox(height: 8)` with `Theme.of(context).textTheme` tokens and `AppSpacing.h8`. Replace hardcoded string `'HUMAN_OVERRIDE'` with `l10n.humanOverrideDefaultBadge`.</action>
    <action>In @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]: Replace `const TextStyle(fontWeight: FontWeight.w600, fontSize: 10)` on line 550 with `Theme.of(context).textTheme` tokens.</action>
    <action>In @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart#L503-L540]: Replace hardcoded strings `'CITATION EVIDENCE'` and `'Location: '` with `l10n.causalInspectorCitationEvidenceHeader` and `l10n.causalInspectorLocationPrefix`.</action>
    <constraint invariant="flutter_theme_sovereignty">Eradicate raw TextStyle, SizedBox, and unlocalized UI strings in touched Flutter widgets.</constraint>
  </step>

  <step id="7" name="IMPLEMENT MULTI-SEGMENT FOUNDATION TEST SUITE">
    <action>In [NEW] @[backend_v2/tests/unit/services/orchestrator/test_multi_segment_quote_foundation.py]: Create dedicated test suite verifying: (1) `coerce_source_quotes_tuple` wraps strings into 1-tuples, strips whitespace, filters empty strings, and handles None; (2) `GateMatchResultDTO` strict Pydantic V2 validation; (3) Symmetric index resolution in `AnchorValidationService`.</action>
    <constraint invariant="universal_quality_gate">Test suite must achieve 100% pass rate with zero warnings.</constraint>
  </step>

  <test_contracts>
    <test name="test_coerce_source_quotes_tuple_single_string_returns_1tuple" category="positive">
      <input>"  Evidence sentence here.  "</input>
      <expected>("Evidence sentence here.",)</expected>
    </test>
    <test name="test_coerce_source_quotes_tuple_list_returns_tuple" category="positive">
      <input>["Sentence one.", "Sentence two."]</input>
      <expected>("Sentence one.", "Sentence two.")</expected>
    </test>
    <test name="test_coerce_source_quotes_tuple_empty_string_returns_none" category="boundary">
      <input>"   "</input>
      <expected>None</expected>
    </test>
    <test name="test_coerce_source_quotes_tuple_none_returns_none" category="boundary">
      <input>None</input>
      <expected>None</expected>
    </test>
    <test name="test_gate_match_result_dto_valid_instantiation" category="positive">
      <input>GateMatchResultDTO(is_valid=True, start_idx=10, end_idx=45)</input>
      <expected>Valid model instance with strict immutability</expected>
    </test>
    <test name="test_gate_match_result_dto_extra_fields_raises_validation_error" category="error_path">
      <input>{"is_valid": True, "start_idx": 10, "end_idx": 45, "extra_field": "illegal"}</input>
      <expected>raises ValidationError (extra='forbid')</expected>
    </test>
    <test name="test_quote_evidence_dto_get_quotes_with_quote" category="positive">
      <input>QuoteEvidenceDTO(quote="A valid evidence quote.", page=1)</input>
      <expected>("A valid evidence quote.",)</expected>
    </test>
    <test name="test_quote_evidence_dto_get_quotes_empty_or_none" category="boundary">
      <input>QuoteEvidenceDTO(quote="   ", page=1)</input>
      <expected>()</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_multi_segment_quote_foundation.py backend_v2/tests/unit/models/dtos/test_quote_evidence.py backend_v2/tests/unit/services/test_export_evidence_formatter.py`.</action>
    <action>Execute anchor validation tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py`.</action>
    <action>Execute backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/models/core_base.py backend_v2/models/dtos/quote_evidence.py backend_v2/services/orchestrator/anchor_validation_service.py backend_v2/services/orchestrator/extractive_sensor_service.py backend_v2/services/orchestrator/sliding_window_linker.py backend_v2/services/export_evidence_formatter.py backend_v2/services/export_service.py backend_v2/services/sdui/adapters/printable_sources_adapter.py --test --ast-strict`.</action>
    <action>Execute Flutter audit loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart --build`.</action>
  </validation_gate>
</execution_protocol>
```
