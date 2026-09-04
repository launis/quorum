> **STATUS: COMPLETED / TOTEUTETTU (100% Implemented & Verified across all 13 matrices)**

# Implementation Plan: Theory-Grounding Matrix Calibration & Micro-Slice Isolation Engine

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
</required_context_rules>

## Objective

Build a deterministic **Theory-Grounding Calibration & Micro-Slice Isolation Engine** for Quorum evaluation matrices. This tool enables extracting isolated, single-matrix JSON slices (~200 lines) from `backend_v2/seed/seed_data.json`, detecting and auditing legacy empirical run contamination (polluted Finnish examples and domain-specific corporate data leaking from past execution runs into calibration examples), formatting high-cognition Theory Opponent Cards for LLM review against academic literature to derive 100% theory-grounded domain-agnostic criteria in English, and atomically patching calibrated matrix definitions back into `seed_data.json` with in-memory pre-flight Pydantic V2 verification and automatic rollback. Furthermore, the engine systematically audits and theory-grounds all atom-level cognitive steering controls (`aggregation_mode`, `acceptance_criteria`, `syntactic_anchors`, `enforce_pre_flight`, and `inverse_evidence`), defining what "all conditions must comply" (`ALL_MUST_COMPLY`) mathematically means across document reduction chunks, syntactic anchors, and reasoning chains, and proving why and when each control is mandated by academic literature. This eliminates LLM context window saturation (context rot) and evaluator bias during matrix hardening.

## Scope & Boundaries

### Target Files
- `[NEW]` @[scripts/matrix_slice_engine.py] (Isolated slice exporter, empirical run contamination detector, theory card compiler, atomic patcher with in-memory verification, and theory explanation compendium appender; <= 250 lines)
- `[MODIFY]` @[scripts/matrix_hardening_loop.py#L23-L39] (Module imports and `__all__` export registration)
- `[MODIFY]` @[scripts/matrix_hardening_loop.py#L110-L138] (Technical debt remediation: `I18nText.resolve()` in `audit_matrix()` and contamination audit reporting)
- `[MODIFY]` @[scripts/matrix_hardening_loop.py#L160-L175] (Technical debt remediation: structured error logging replacing silent pass in `build_or_load_state()`)
- `[MODIFY]` @[scripts/matrix_hardening_loop.py#L290-L314] (CLI routing facade for `--slice`, `--theory-card`, `--patch`, `--explain`, `--audit-contamination`)
- `[MODIFY]` @[backend_v2/models/v2_core.py#L170-L240] (TDAAssertion `@model_validator(mode="after")` cross-field coherence enforcement)
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart#L750-L920] (Studio UX Guardrails: Reactive validation prohibiting conflicting/invalid configurations on screen)
- `[NEW]` @[client_app_v2/test/features/studio/views/widgets/scale_editor_modal_test.dart] (Widget test verifying reactive UI guardrails)
- `[NEW]` @[backend_v2/tests/unit/scripts/test_matrix_slice_engine.py] (Comprehensive unit and anti-happy-path test suite covering 15 contracts including empirical contamination detection, coherence auditing, and steering control grounding)
- `[NEW]` @[docs/architecture/08_matrix_explanations.md] (Architectural compendium of 2-paragraph English theory explanations for each hardened matrix)

### Context Files (Read-Only)
- @[backend_v2/models/domain/prompt_blocks.py#L38-L110] (PromptBlockBase, MatrixPromptBlock SSOT schema and extrema computing)
- @[backend_v2/models/core_base.py#L39-L105] (I18nText SSOT and `.resolve()` method)
- @[backend_v2/seed/seed_data.json#L340-L450] (Master seed vault matrices)
- @[scripts/sanitize_seed_vault.py#L226-L274] (create_vault_backup and atomic_save_seed_data SSOT functions)
- @[scripts/audit_database_atoms.py#L844-L895] (run_full_database_audit programmatic in-memory verification linter)

---

## 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Slice Exporter (`scripts/matrix_slice_engine.py::export_matrix_slice`)** | Banned: raw dict slicing without validation, assuming matrix exists, saving unformatted JSON, hardcoding output paths without parameter override, or leaking non-matrix blocks. | Mandatory: Validate extracted slice with `MatrixPromptBlock.model_validate(raw)`. Default output to `tmp/slices/{matrix_id}.json` while accepting optional `output_path: Path`. Fail fast with `ValueError` if ID not found or `category_id != "matrix"`. | Pruned: Multi-matrix bundle exporters, zip compressors, streaming JSON serializers, or git status inspectors. Single isolated matrix file output only. | Proven via: `test_export_matrix_slice_valid` (produces valid file that re-validates into `MatrixPromptBlock`), `test_export_matrix_slice_invalid_id_raises` (raises `ValueError`), and `test_export_matrix_slice_non_matrix_category_raises` (raises `ValueError`). |
| **Theory Opponent Card & Contamination Auditor (`scripts/matrix_slice_engine.py::generate_theory_opponent_card` & `detect_empirical_contamination`)** | Banned: Unconditional attribute access `matrix.theory_grounding.source_url` (crashes when `None`), unstructured prose prompts, Finnish prompts, string formatting with f-strings in system directives, retaining legacy empirical run artifacts (such as Finnish case study sentences on remote work, revenue percentages, or product pilots), or configuring steering controls (`aggregation_mode`, `acceptance_criteria`, `syntactic_anchors`, `enforce_pre_flight`, `inverse_evidence`) arbitrarily without theoretical literature derivation (including pairing `inverse_evidence=True` with `ALL_MUST_COMPLY`). | Mandatory: Enforce 4-Layer Clean Stack (`05_llm_architecture.md`: Static Evaluator Mandate, Academic Theory Grounding, Extraction Protocol, BARS Level Specs). Implement `detect_empirical_contamination()` to audit all `contrastive_example` strings for Finnish empirical run text and corporate case specificity. Compile `<theory_calibration_audit>` and `<control_theory_grounding>` sections within the Theory Opponent Card: 1) mandating the rewrite of contaminated examples into pure, domain-agnostic, theory-grounded contrastive pairs in English derived from cited literature; 2) mathematically defining and challenging `aggregation_mode` (`ALL_MUST_COMPLY` as a systemic invariant across all chunks vs `EXISTS` as existential competence/error radar) and reasoning chains (`acceptance_criteria`). Handle `theory_grounding is None` gracefully. Static XML framing generated by engine. | Pruned: Live internet scraping of citation URLs, LLM chat client instantiation in the generator script, live execution against external LLM providers. Pure functional prompt card string compiler and regex/heuristic contamination linter. | Proven via: `test_generate_theory_opponent_card_content` (asserts Markdown/XML sections, citations, scale 1-5 claims), `test_generate_theory_opponent_card_missing_grounding_resilience` (asserts warning section when `theory_grounding=None`), `test_detect_empirical_contamination_flags_run_artifacts` (identifies contaminated Finnish run sentences), `test_generate_theory_opponent_card_includes_contamination_audit` (asserts `<theory_calibration_audit>` presence), and `test_generate_theory_opponent_card_explains_aggregation_and_steering_controls`. |
| **Atomic Slice Patcher (`scripts/matrix_slice_engine.py::apply_matrix_slice`)** | Banned: In-place direct writes to `seed_data.json`, skipping backup, applying unvalidated JSON, leaving corrupted database on failure, silent `except: pass`, shell-out subprocesses (`run_command` in production code). | Mandatory: 1) Validate slice with `MatrixPromptBlock.model_validate()`. 2) Create timestamped backup in `backend_v2/seed/backups/` using `create_vault_backup()`. 3) Write to temporary file and swap atomically using `atomic_save_seed_data()`. 4) Execute in-memory pre-flight verification directly via `run_full_database_audit(seed_path)`; rollback immediately on `report.all_passed is False` and raise `RuntimeError`. | Pruned: Interactive CLI confirmation prompts, Git commit automation, automatic diff viewers, subprocess invocation of external Python shells. Pure deterministic in-memory verified file patcher. | Proven via: `test_apply_matrix_slice_success` (atomic replacement with backup) and `test_apply_matrix_slice_corrupted_rolls_back` (failed pre-flight restores backup and raises `RuntimeError`). |
| **CLI Facade (`scripts/matrix_hardening_loop.py#L290-L314`)** | Banned: Inlining slice logic into `matrix_hardening_loop.py` (>315 lines approaching God Code limit), adding loose helper functions, breaking existing CLI argument parsers. | Mandatory: Expose strictly delegated argparse flags `--slice`, `--theory-card`, `--patch`, `--explain`, `--audit-contamination` in `main()` delegating 1:1 to `scripts.matrix_slice_engine`. Keep `matrix_hardening_loop.py` <= 335 lines. | Pruned: Interactive sub-menus, cursor navigation, terminal TUI frameworks. Standard CLI flags only. | Proven via: `test_cli_flags_slice_theory_and_patch` asserting `sys.argv` routing for all CLI flags. |
| **Technical Debt Remediation (`scripts/matrix_hardening_loop.py#L110-L175`)** | Banned: Chained `.get("fi") or .get("en") or default` fallbacks (L112, L115, L124) and silent `except (OSError, json.JSONDecodeError, KeyError): pass` (L169-L170). | Mandatory: Use `matrix.label.resolve(target_locale="fi")`, `matrix.description.resolve(target_locale="fi") if matrix.description is not None else "Ei kuvausta"`, and `s.name.resolve(target_locale="fi") if s.name is not None else f"Taso {lvl_score}"`. Replace silent `except: pass` with structured error logging via `logging.getLogger(__name__)`. | Pruned: Rewriting the entire audit table UI or restructuring `HardeningStateDTO`. Target cleanups strictly at the violated lines. | Proven via: `test_build_or_load_state_and_mark_done` and `backend_audit_loop.py` passing with zero duct-tape violations. |
| **Atom Model Schema (`backend_v2/models/v2_core.py::TDAAssertion`)** | Banned: Permissive schema allowing conflicting flags (`inverse_evidence=True` with `ALL_MUST_COMPLY`, `enforce_pre_flight=True` with empty `syntactic_anchors`). | Mandatory: Strict Pydantic V2 `@model_validator(mode="after")` enforcing logical compatibility between steering controls and evaluation tracks. | Pruned: Complex dynamic constraint-solving solvers or runtime retry loops. Simple deterministic Pydantic validator. | Proven via: `test_tda_assertion_cross_field_validation` asserting `ValidationError` on conflicting flag pairs. |
| **Studio Scale Editor UX Guardrails (`scale_editor_modal.dart`)** | Banned: Allowing users on the screen to toggle contradictory states (e.g. enabling `inverse_evidence=True` while selecting `ALL_MUST_COMPLY`, enabling `enforce_pre_flight=True` with empty `syntactic_anchors`, entering Finnish/non-English text into calibration prompt fields without warning, or saving without cross-field validation). | Mandatory: Reactive form validation and smart auto-correction in the UI: 1) When `inverse_evidence` is enabled, automatically force `aggregation_mode` to `EXISTS`, disable `ALL_MUST_COMPLY` in dropdown, and show an explanatory info tooltip. 2) When `enforce_pre_flight` is toggled on, show an inline validation error if `syntactic_anchors` is empty and disable save. 3) Real-time language linter on `TextFormField` (warning badge if Finnish non-ASCII characters or common Finnish words are typed in `extractionRule` or `contrastiveExample`). 4) Save button disabled (`onPressed: _isCoherent ? _save : null`) or displays inline error banner summarizing any cross-field incoherence. | Pruned: Server-roundtrip validation on every keystroke, modal popups blocking navigation. Pure reactive client-side form state validation with real-time feedback. | Proven via: `testWidgets` in `client_app_v2/test/features/studio/views/widgets/scale_editor_modal_test.dart` verifying that toggling `inverse_evidence` locks `aggregation_mode` to `EXISTS` and validates empty anchors. |
| **Matrix Theory Compendium (`docs/architecture/08_matrix_explanations.md` & `scripts/matrix_slice_engine.py::append_matrix_theory_explanation`)** | Banned: Including system IDs (`blk_...`, `tda_...`), dense academic jargon, Finnish text in architecture manifestos, or mutating `seed_data.json` schemas for documentation notes. | Mandatory: 2-paragraph English synthesis per hardened matrix titled with English name (`### {matrix.label.resolve('en')}`). Paragraph 1: Theory, design choices, meaning, strategic outcome. Paragraph 2: Specific matrix controls (`allow_contextual_override`, `bounding_box_scope`, `ALL_MUST_COMPLY`) and parameter effects. | Pruned: Extra relational tables, individual per-matrix files. Consolidated single compendium file in `docs/architecture/08_matrix_explanations.md`. | Proven via: `test_append_matrix_theory_explanation_compendium` asserting file creation, section upsert, and strict 2-paragraph English rubric. |

---

## Technical Debt & Anti-Pattern Elimination

In accordance with `ki_god_code_prevention.md` and `the_duct_tape_ban`:
1. `scripts/matrix_hardening_loop.py` currently stands at 314 lines. Adding slice management directly would bloat it past the God Code threshold. All slice logic is isolated in `scripts/matrix_slice_engine.py` (strictly <= 250 lines).
2. Existing duct-tape in `scripts/matrix_hardening_loop.py` (lines 112, 115, 124 using `.get()` with chained `or` fallbacks) is refactored in Phase 1 to use `I18nText.resolve()`.
3. Silent exception swallowing in `scripts/matrix_hardening_loop.py` (lines 169-170) is replaced with structured logging using standard library `logging`.
4. No raw dictionaries or duck typing are permitted; all slice operations transit through `MatrixPromptBlock`.
5. Pre-flight verification in `apply_matrix_slice` avoids invoking shell subprocesses (`run_command`), instead directly calling the programmatic in-memory API `run_full_database_audit(seed_path)` from `scripts.audit_database_atoms` for deterministic zero-overhead validation.
6. **UI Terminology Modernization & Conceptual Harmonization**: Studio Scale Editor UI (`scale_editor_modal.dart` and `client_app_v2/lib/l10n/`) modernized TDA terminology into intuitive cognitive mental models: *Evidence Search Distance* for `bounding_box_scope`, *Error Radar / Disqualification Inversion* for `inverse_evidence`, *Scope Requirement (Strict vs. Flexible)* for `aggregation_mode`, *Linguistic Focal Point* for `anchor_target`, *AI Reasoning Chain* for `acceptance_criteria`, and *Fast-Reject Pre-flight* for `enforce_syntactic_preflight`. While backend schema fields remain locked to SSOT property names (`anti_semantic_drift_renaming`), documentation compilers (`docs/architecture/08_matrix_explanations.md`) and Theory Opponent Cards (`generate_theory_opponent_card`) harmoniously adopt these clear conceptual definitions rather than obsolete technical jargon.
7. **Empirical Run Contamination & Case-Specific Anchor Purge**: Auditing existing evaluation matrices in `seed_data.json` reveals significant historical contamination in `contrastive_example` strings (for example, `tda_69cc84e0b0c44996a8a95e09b356c692` in `blk_440a5fef9331451b` containing Finnish empirical case data: `UNACCEPTABLE: "Etätyö heikensi tiimien välistä tiedonkulkua 40 % mittausten mukaan, minkä vuoksi läsnäolopäivien lisääminen parantaa koordinaatiota."` and `ACCEPTABLE: "Yrityksen liikevaihto kasvoi 15 %..."`). This violates `cross_language_mapping_mandate` and `05_llm_architecture.md`, which mandate that system prompt criteria and contrastive examples must be formulated in universal English as domain-agnostic theoretical exemplars. Embedding past customer runs or specific corporate scenarios overfits the LLM evaluator to narrow topics, biases analysis of documents from different industries, and prevents generalizable cross-language evaluation. All calibration examples must be derived systematically from the academic theory grounding (such as Toulmin's structural Claim-Data-Warrant framework).
8. **Theory-First Grounding of Cognitive Steering Controls & Semantics of `ALL_MUST_COMPLY`**: A critical source of evaluation fragility is setting atom control flags (`aggregation_mode`, `acceptance_criteria`, `syntactic_anchors`, `enforce_pre_flight`, `inverse_evidence`) arbitrarily without grounding them in the cited academic literature.
   - **Mathematical Meaning of `ALL_MUST_COMPLY` ("Kaikkien ehtojen on täytyttävä samanaikaisesti") in Quorum**:
     1. *Document Chunk Reduction (`matrix_reducer.py::reduce_all_must_comply`)*: When a document is evaluated across multiple text chunks/windows, `ALL_MUST_COMPLY` enforces `ANY(Failed) -> Failed; ANY(DLQ) -> DLQ; ALL(Passed) -> Passed`. This means the assertion must hold true across *every single analyzed passage* of the entire document without exception.
     2. *Syntactic Anchor Completeness (`extractive_sensor_service.py`)*: If `aggregation_mode == "ALL_MUST_COMPLY"` and syntactic anchors are specified, finding fewer anchors than required triggers an immediate fail (`len(found) < len(tda.syntactic_anchors)`), whereas `EXISTS` passes if any single anchor is found.
     3. *Reasoning Chain Conjunction (`acceptance_criteria`)*: The LLM evaluator must verify that all steps in the criterion's reasoning sequence are simultaneously satisfied.
   - **Why and When to Use `ALL_MUST_COMPLY` vs. `EXISTS` (Theory Derivation)**:
     - *When `ALL_MUST_COMPLY` is Mandated by Theory*: Only when the academic framework defines a *Universal Structural Invariant*—a standard where a single omission invalidates the entire level (for example, formal deductive logic where any broken syllogism invalidates the conclusion, or Level 5 Toulmin Argumentation where every major claim must be grounded in data and backing).
     - *When `EXISTS` is Mandated by Theory*: When the literature measures a *Demonstrated Competence* (for example, demonstrating that the author possesses the cognitive ability to employ epistemic qualifiers or provide empirical backing). Demanding `ALL_MUST_COMPLY` on such constructs would artificially penalize natural text and force robotic repetition.
     - *The Error Radar Inversion Anti-Pattern*: When `inverse_evidence == True` (Error Radar / Virhetutka searching for flaws like dogmatic absolutes or missing warrants), setting `aggregation_mode = "ALL_MUST_COMPLY"` is a catastrophic design error: it would require *every single chunk in the document* to contain the flaw before flagging the error! An error radar must almost always be `EXISTS` (a single fallacy is sufficient to trigger the penalty).
9. **Discovery & Theoretical Transformation Protocol for Matrix Atoms**:
   To eliminate ad-hoc, informal, or empirical run definitions, every atom must undergo a systematic Two-Stage Discovery and Transformation process:
   - **Stage 1: Automated Discovery (Static Linter & Heuristic Scan)**:
     1. *Empirical / Run-Specific Pollution*: Flags Finnish vocabulary, case study metrics (revenue %, remote work memos), or specific customer test data.
     2. *Theoretical Grounding Vacuity*: Flags concept descriptions or rules lacking explicit formal constructs (e.g. generic "find proof" vs explicit "Pearl Rung 2 intervention do(X) vs baseline" or "Toulmin structural warrant").
     3. *Search Distance Misalignment*: Flags `bounding_box_scope` incongruent with the cognitive phenomenon (e.g., multi-step causal mechanisms squeezed into a single `sentence`, or localized warrant checks diluted across `document`).
     4. *Control Flag Desynchronization*: Flags `inverse_evidence=True` paired with `ALL_MUST_COMPLY`, or `COGNITIVE_JUDGEMENT` paired with `enforce_pre_flight=True`.
   - **Stage 2: Six-Field Theoretical Transformation Protocol**:
     Every atom's fields are systematically rewritten through the cited academic literature:
     1. `concept_description`: Explicitly name the theoretical construct (e.g., "Applies Pearl's Rung 2 intervention logic (do(X)), evaluating what occurs when an active intervention is applied compared against a control/baseline condition.").
     2. `anchor_target`: Anchor attention to the rhetorical or syntactic marker characteristic of the theory (e.g., "Find active intervention evaluation comparing against baseline.").
     3. `bounding_box_scope`: Calibrate the search window strictly to the unit of the phenomenon (e.g. `sentence` for dogmatic markers; `paragraph` for intervention-control contrasts and claim-data-warrant triads).
     4. `extraction_rule`: Formulate a strict necessary-and-sufficient truth condition (e.g. "The text frames causation through an active intervention (do(X)), systematically contrasting the outcome of a deliberate operational manipulation against an explicit untreated baseline.").
     5. `acceptance_criteria`: Sequence ordered deductive verification steps derived from the theory's methodological validation procedure.
     6. `contrastive_example`: Provide clean, domain-agnostic English contrastive pairs (`ACCEPTABLE: "..." \n UNACCEPTABLE: "..."`) illustrating the presence versus absence of the theoretical construct.
   - **Stage 3: Cross-Field Synergistic Coherence & Isomorphism Contract**:
     To guarantee that the contents of the fields do not contradict each other and work synergistically, every atom must satisfy the **Six-Point Isomorphic Chain**:
     1. *Epistemic Continuity (`concept_description` $\leftrightarrow$ `extraction_rule`)*: The `extraction_rule` must be the formal operationalization of the theoretical construct named in `concept_description`. If the concept specifies Toulmin's Warrant, the extraction rule cannot test mere statistical correlation.
     2. *Attention Alignment (`anchor_target` $\leftrightarrow$ `extraction_rule`)*: The `anchor_target` must point the transformer's attention to the specific syntactic/rhetorical token that the `extraction_rule` verifies.
     3. *Physical Feasibility (`bounding_box_scope` $\leftrightarrow$ `extraction_rule`)*: The search distance must be physically capable of containing the phenomenon. If `extraction_rule` evaluates an intervention versus an untreated baseline or a claim-data-warrant triad, `bounding_box_scope` MUST be `paragraph`. Squeezing multi-state relational logic into a `sentence` scope is an architectural defect.
     4. *Deductive Parity (`extraction_rule` $\leftrightarrow$ `acceptance_criteria`)*: The step-by-step sequence in `acceptance_criteria` must constitute the complete proof of the necessary-and-sufficient truth condition in `extraction_rule`.
     5. *Isolated Discriminative Boundary (`extraction_rule` $\leftrightarrow$ `contrastive_example`)*: The `contrastive_example` must contain both `ACCEPTABLE:` and `UNACCEPTABLE:` blocks. The `UNACCEPTABLE` snippet must fail *exclusively* because it violates the specific truth condition in `extraction_rule`, isolating the single theoretical construct without confounding noise.
     6. *Aggregation Law (`extraction_rule` $\leftrightarrow$ `aggregation_mode`)*: If the theoretical construct measures a universal invariant across the entire document, `aggregation_mode` is `ALL_MUST_COMPLY`. If it measures a demonstrated competence or error radar (`inverse_evidence=True`), `aggregation_mode` MUST be `EXISTS`.
10. **Studio UI Form Incoherence & Screen Guardrail Architecture**:
    To prevent users from physically configuring or saving invalid, conflicting, or non-English content on the screen in Studio (`scale_editor_modal.dart`), four reactive UI guardrails are established:
    - **Guardrail 1: Error Radar Auto-Lock**: When `inverse_evidence` (Käänteinen tulkinta / Virhetutka) is enabled, the UI automatically sets `aggregation_mode = AggregationMode.exists` and disables the `ALL_MUST_COMPLY` option in the dropdown. An informative badge is rendered (*"Virhetutka vaatii 'Yksikin havainto riittää' -tilan"*), explaining that requiring an error in 100% of chunks disables detection.
    - **Guardrail 2: Pre-Flight Anchor Dependency Guard**: When `enforce_pre_flight` is toggled on, if `syntactic_anchors` is empty, the UI displays a prominent red validation warning (*"Pikahylkäys vaatii vähintään yhden tunnistussanan"*), and the modal's Save button is disabled until at least one anchor word is entered.
    - **Guardrail 3: English System Language Linter**: As the user types into `extraction_rule` or `contrastive_example`, a real-time regex validator scans for Finnish non-ASCII characters (`ä, ö, å`) and common Finnish vocabulary. If detected, an amber warning banner appears: *"Kehotesääntöjen ja esimerkkien tulee olla englanniksi (System Language) yleispätevyyden ja tekoälyn suorituskyvyn varmistamiseksi."*
    - **Guardrail 4: Comparative Scope Warning**: If `extraction_rule` or `concept_description` contains comparative state attribution (e.g. terms like `baseline`, `control`, `compared to`, `intervention`) while `bounding_box_scope == 'sentence'`, an inline amber warning suggests upgrading the scope to `paragraph` to prevent impossible sentence-level comparisons.
    - **Save Action Interceptor**: The modal's Save button executes `_isCoherent()`. If any atom possesses an ungrounded or contradictory configuration, save is prevented and an inline error summary card guides the user to the offending field.

---

## Red-Team Falsification & Critical Failure Modes

Two concrete failure modes were identified and eliminated through System 2 adversarial cross-examination:

1. **Failure Mode 1: Pre-Flight Shell-Out Brittle Pathing & Encoding Divergence**
   - *Risk:* If `apply_matrix_slice` executes `run_command` or `subprocess.run("uv run python scripts/audit_database_atoms.py ...")` on Windows PowerShell, path separator differences, virtual environment resolution discrepancies, and UTF-16 stdout corruption can cause false-positive failures, triggering unnecessary rollbacks or hanging background workers.
   - *Mitigation:* `apply_matrix_slice` imports and calls `run_full_database_audit(seed_path)` directly in-process. If `report.all_passed` is `False`, the backup is immediately restored and `RuntimeError` is raised with the formatted audit report findings. Zero subprocess execution; 100% deterministic in-memory audit.

2. **Failure Mode 2: Orphaned Slice Collision & Stale State Poisoning**
   - *Risk:* If multiple slices are generated into `tmp/slices/` across sessions without ID checks, a modified slice could overwrite or corrupt an unrelated matrix if `slice.id` is tampered with or mismatched from its filename.
   - *Mitigation:* `apply_matrix_slice` strictly validates that `slice.id` matches an existing block in `data["prompt_blocks"]` with `category_id == "matrix"` before any backup or write occurs. Furthermore, `export_matrix_slice` fails fast if `matrix_id` does not exist or has a category other than `matrix`.

3. **Failure Mode 3: Empirical Run Contamination & Case-Specific Anchor Leaks (Context Poisoning)**
   - *Risk:* When matrices retain Finnish empirical examples from past customer runs (for example, corporate memos on remote work or software sprint metrics), the LLM evaluator overfits to those specific business contexts rather than evaluating abstract rhetorical/cognitive structures. This causes semantic drift and false rejections when processing documents from healthcare, legal, public sector, or technical engineering domains. Furthermore, Finnish criteria in prompt blocks break the English system language invariant (`cross_language_mapping_mandate`).
   - *Mitigation:* `scripts/matrix_slice_engine.py` incorporates `detect_empirical_contamination(matrix)`, which scans all `contrastive_example` texts for empirical run patterns (non-English characters, Finnish business vocabulary, specific corporate operational metrics). The Opponent Card generator embeds a mandatory `<theory_calibration_audit>` directive instructing the Theory Opponent reviewer to purge empirical run artifacts and replace them with pure, domain-agnostic theoretical contrastive pairs in English derived from the cited academic literature.

4. **Failure Mode 4: Steering Control Desynchronization & The `ALL_MUST_COMPLY` Inversion Paradox**
   - *Risk:* If `aggregation_mode` is misconfigured without theoretical understanding—such as setting `ALL_MUST_COMPLY` on an error detector (`inverse_evidence=True`), or setting `ALL_MUST_COMPLY` on a qualitative stylistic competence—the evaluation engine produces catastrophic false results (e.g. error detectors never triggering, or competent texts scoring 0 because a specific qualifier wasn't repeated in every paragraph).
   - *Mitigation:* The Theory Opponent Card generator deterministically checks for semantic consistency (flagging `inverse_evidence=True` paired with `ALL_MUST_COMPLY` as a structural defect) and forces the LLM reviewer to explicitly ground `aggregation_mode`, `acceptance_criteria`, `syntactic_anchors`, and `enforce_pre_flight` in the literature citation.

5. **Failure Mode 5: Permissive UI Screen Input Permitting Conflicting Runtime State**
   - *Risk:* Without screen-level constraints in Studio (`scale_editor_modal.dart`), authors can toggle contradictory flags (such as activating an error radar with strict all-chunks compliance, or enabling fast pre-flight reject without entering anchor words). This saves defective atom definitions to the backend, causing silent runtime failures during document analysis.
   - *Mitigation:* Implement dual-layer protection: 1) Client-side reactive UI guardrails in `scale_editor_modal.dart` that dynamically auto-lock `aggregation_mode` to `EXISTS` when `inverse_evidence` is toggled on, block save if `enforce_pre_flight` lacks anchors, and display real-time language warnings on Finnish text; 2) Backend Pydantic `@model_validator` in `backend_v2/models/v2_core.py` acting as an impenetrable fail-fast firewall.

---

## Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Phase 1: Pre-Implementation Cleanups & Technical Debt Remediation">
    <action>Execute existing test suite for matrix hardening to verify green baseline: `uv run pytest backend_v2/tests/unit/scripts/test_matrix_hardening_loop.py`.</action>
    <action>Remediate 3 technical debt items in `scripts/matrix_hardening_loop.py`:</action>
    <substep id="1.1" name="Eradicate Chained Dict Fallbacks">
      <instruction>In `audit_matrix()` (`#L110-L138`), replace `.translations.get("fi") or ...` with:
        - `name = matrix.label.resolve(target_locale="fi")`
        - `desc = matrix.description.resolve(target_locale="fi") if matrix.description is not None else "Ei kuvausta"`
        - `lvl_name = s.name.resolve(target_locale="fi") if s.name is not None else f"Taso {lvl_score}"`
      </instruction>
    </substep>
    <substep id="1.2" name="Eradicate Silent Exception Pass">
      <instruction>In `build_or_load_state()` (`#L160-L175`), add standard library `logging` import and logger (`logger = logging.getLogger(__name__)`). Replace `except (OSError, json.JSONDecodeError, KeyError): pass` with explicit error logging (`logger.warning("Failed to parse existing state file %s; re-initializing state.", STATE_PATH)`).</instruction>
    </substep>
    <substep id="1.3" name="Temporary Directory Guard">
      <instruction>Ensure `tmp/slices/` directory exists for holding temporary single-matrix JSON slices and verify it is untracked in version control (`.gitignore` line 272).</instruction>
    </substep>
    <constraint invariant="atomic_checkpoint_mandate">Verify `uv run pytest backend_v2/tests/unit/scripts/test_matrix_hardening_loop.py` passes cleanly before proceeding to Step 2.</constraint>
  </step>

  <step id="2" name="Phase 2: Core Matrix Slice Engine Implementation">
    <action>Create `scripts/matrix_slice_engine.py` containing five public functions:</action>
    <substep id="2.1" name="Slice Exporter">
      <instruction>Implement `export_matrix_slice(matrix_id: str, output_path: Path | None = None, seed_path: Path = Path("backend_v2/seed/seed_data.json")) -> Path`:
        1. Reads and parses `seed_path` using UTF-8 encoding.
        2. Scans `prompt_blocks` collection for the block where `b["id"] == matrix_id` and `b.get("category_id") == "matrix"`.
        3. Validates the raw block into `MatrixPromptBlock.model_validate(raw)`.
        4. Resolves destination file: `dest = output_path or Path("tmp/slices") / f"{matrix_id}.json"`.
        5. Creates parent directory (`dest.parent.mkdir(parents=True, exist_ok=True)`).
        6. Writes formatted JSON with 2-space indentation and newline: `dest.write_text(validated.model_dump_json(indent=2) + "\n", encoding="utf-8")`.
        7. Returns destination `Path`.
        8. Raises `ValueError(f"Matrix with ID '{matrix_id}' not found in {seed_path} or is not category 'matrix'")` if missing.
      </instruction>
    </substep>
    <substep id="2.2" name="Empirical Contamination Detector & Coherence Auditor">
      <instruction>Implement `detect_empirical_contamination(matrix: MatrixPromptBlock) -> list[dict[str, str]]` and `audit_atom_coherence(matrix: MatrixPromptBlock) -> list[dict[str, str]]`:
        1. `detect_empirical_contamination()` iterates through `matrix.scales` -> `claims` -> `tda_assertions`:
           - Inspects `contrastive_example`, `concept_description`, and `extraction_rule`.
           - Detects Finnish characters (`ä, ö, å`), Finnish grammatical endings, and domain-specific corporate metrics (remote work, revenue %, Slack).
           - Returns structured contamination records.
        2. `audit_atom_coherence()` performs deterministic cross-field coherence analysis enforcing the Six-Point Isomorphic Chain:
           - Check 1 (Inversion Paradox): Flags `inverse_evidence == True` paired with `aggregation_mode == ALL_MUST_COMPLY` (`issue="INVERSION_PARADOX"`).
           - Check 2 (Pre-flight Choke-Point): Flags `enforce_pre_flight == True` when `len(syntactic_anchors) == 0` (`issue="PREFLIGHT_CHOKEPOINT"`).
           - Check 3 (Scope-Rule Compression Paradox): Flags `bounding_box_scope == "sentence"` when `extraction_rule` or `concept_description` contains comparative/relational keywords (`baseline`, `control`, `compared to`, `intervention`, `counterfactual`, `pre-`, `post-`) (`issue="SCOPE_RULE_MISMATCH"`).
           - Check 4 (Exemplar Structure & Symmetry): Flags `contrastive_example` missing `ACCEPTABLE:` or `UNACCEPTABLE:` markers, or containing Finnish tokens (`issue="EXEMPLAR_DEFECT"`).
           - Check 5 (Criteria-Rule Parity): Flags empty or vacuous `acceptance_criteria` when `extraction_rule` specifies formal multi-step logic (`issue="CRITERIA_RULE_DISCORDANCE"`).
           - Returns structured coherence findings: `{"tda_id": tda.tda_id, "issue": issue, "description": description}`.
      </instruction>
    </substep>
    <substep id="2.3" name="Theory Opponent Card Generator">
      <instruction>Implement `generate_theory_opponent_card(matrix_id: str, seed_path: Path = Path("backend_v2/seed/seed_data.json")) -> str`:
        1. Loads and validates the target `MatrixPromptBlock` using `load_matrix_by_id(matrix_id, seed_path)`.
        2. Safely extracts `theory_grounding`:
           - If `matrix.theory_grounding is not None`: extract `source_url` and `citation_reference`.
           - If `matrix.theory_grounding is None`: format an explicit missing-theory alert: `[THEORY GROUNDING ABSENT: Matrix requires academic literature grounding before final calibration]`.
        3. Extracts operational flags: `allow_contextual_override`, `is_evaluative`, `is_lightweight_protocol`.
        4. Runs `detect_empirical_contamination(matrix)` and `audit_atom_coherence(matrix)`:
           - Lists contaminated `tda_id`s and coherence warnings in `<theory_calibration_audit>`.
           - Explicitly instructs the LLM evaluator to purge empirical run data and resolve cross-field incoherence.
        5. Formats an explicit `<control_theory_grounding>` section with an Epistemic Ontology Table:
           - Displays the 6-field cognitive mapping: Target (`concept_description`), Saliency (`anchor_target`), Text Window (`bounding_box_scope`), Truth Condition (`extraction_rule`), Deductive Sequence (`acceptance_criteria`), and Decision Boundary (`contrastive_example`).
           - Embeds the Six-Point Isomorphic Chain rubric, requiring the reviewer to certify that `concept_description`, `anchor_target`, `bounding_box_scope`, `extraction_rule`, `acceptance_criteria`, and `contrastive_example` form an unbroken, non-contradictory logical chain.
           - Explains the mathematical semantics of `aggregation_mode`: `ALL_MUST_COMPLY` vs `EXISTS`.
           - Warns of any anti-pattern pairing.
        6. Embeds the Six-Field Theoretical Transformation Protocol in `<theory_transformation_protocol>`:
           - Instructs the Theory Opponent reviewer to re-ground all 6 fields directly in the cited literature citation.
        7. Compiles structured Markdown Opponent Card following Four-Layer Clean Stack (`05_llm_architecture.md`):
           - `<evaluator_mandate>`: Adversarial System 2 reviewer instructions, BARS extrema evaluation, zero-trust citation audit.
           - `<theory_context>`: Academic literature citation, theoretical framework, and methodological anchor.
           - `<matrix_metadata>`: Matrix ID, Finnish/English labels, operational flags.
           - `<bars_scale_specifications>`: Levels 1 to 5 with claims, descriptions, TDA assertions, extraction rules, and contrastive examples.
           - `<theory_calibration_audit>`: Contamination findings and coherence audit.
           - `<control_theory_grounding>`: Epistemic ontology table and steering controls justification.
           - `<theory_transformation_protocol>`: Explicit 6-field theoretical transformation instructions.
      </instruction>
    </substep>
    <substep id="2.4" name="Atomic Slice Patcher with Coherence Rollback Guard">
      <instruction>Implement `apply_matrix_slice(slice_path: Path, seed_path: Path = Path("backend_v2/seed/seed_data.json"), dry_run: bool = False) -> None`:
        1. Reads `slice_path` and validates via `MatrixPromptBlock.model_validate_json(raw_json)`.
        2. Verifies `slice.category_id == PromptBlockCategory.MATRIX`.
        3. Executes `audit_atom_coherence(slice)`. If any fatal incoherence (such as Error Radar Inversion) is detected, raises `ValueError(f"Slice {slice.id} contains fatal field incoherence: {findings}")` and aborts before touching seed data.
        4. Reads full `seed_path` into memory via UTF-8 JSON parsing.
        5. Finds index of `b` in `data["prompt_blocks"]` where `b["id"] == slice.id`. If not found, raises `ValueError`.
        6. If not `dry_run`:
           a. Creates timestamped backup using `create_vault_backup(seed_path)`.
           b. Replaces block at matching index with `slice.model_dump(mode="json", exclude_none=True)`.
           c. Atomically writes to `seed_path` using `atomic_save_seed_data(data, seed_path)`.
           d. Executes in-memory pre-flight verification: `report = run_full_database_audit(seed_path)`.
           e. If `report.all_passed is False`, restores backup immediately from `backup_file` via `shutil.copyfile(backup_file, seed_path)` and raises `RuntimeError(f"Pre-flight audit failed for slice {slice.id}; restored backup from {backup_file}")`.
           f. If pre-flight passes and `tmp/matrix_hardening_state.json` exists, marks status `DONE` for `slice.id` via `mark_done(slice.id)`.
      </instruction>
    </substep>
    <substep id="2.5" name="Backend Pydantic Cross-Field Validator">
      <instruction>Add `@model_validator(mode="after")` to `TDAAssertion` in `backend_v2/models/v2_core.py`:
        1. Asserts: if `self.inverse_evidence is True and self.aggregation_mode == AggregationMode.ALL_MUST_COMPLY`, raises `ValueError("inverse_evidence=True cannot be paired with aggregation_mode='ALL_MUST_COMPLY'")`.
        2. Asserts: if `self.enforce_pre_flight is True and len(self.syntactic_anchors) == 0`, raises `ValueError("enforce_pre_flight=True requires at least one syntactic anchor")`.
      </instruction>
    </substep>
    <substep id="2.5" name="Theory Compendium Appender">
      <instruction>Implement `append_matrix_theory_explanation(matrix_id: str, compendium_path: Path = Path("docs/architecture/08_matrix_explanations.md"), seed_path: Path = Path("backend_v2/seed/seed_data.json")) -> None`:
        1. Loads validated `MatrixPromptBlock`.
        2. Formats English matrix title (`### {matrix.label.resolve('en')}`).
        3. Compiles strictly 2 paragraphs in clear English without IDs or dense jargon:
           - Paragraph 1: Foundational theory, BARS 1-5 mapping, elimination of rhetorical fluff, and objective fact-anchored conclusions.
           - Paragraph 2: Matrix-specific steering controls (contextual overrides, evidence search distance via `bounding_box_scope`, error radar via `inverse_evidence`, and strictness via `aggregation_mode`) and their operational effects.
        4. If `compendium_path` does not exist, initializes it with standard metadata header.
        5. Upserts or appends the 2-paragraph section under the matrix title in `compendium_path`.
      </instruction>
    </substep>
    <constraint invariant="the_zero_compromise_pledge">Strict Pydantic V2 parsing only; zero unvalidated raw dictionary mutations.</constraint>
    <constraint invariant="god_code_prevention">Keep scripts/matrix_slice_engine.py <= 250 lines.</constraint>
  </step>

  <step id="3" name="Phase 3: Studio UI Guardrails & CLI Facade Integration">
    <substep id="3.1" name="Studio Scale Editor Reactive Guardrails">
      <action>Modify `client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart` (`#L750-L920`):</action>
      <instruction>
        1. In `inverse_evidence` switch `onChanged`:
           - When toggled to `true`, automatically set `tda.aggregationMode = AggregationMode.exists`.
           - In `aggregation_mode` dropdown `items`: disable or hide `ALL_MUST_COMPLY` when `tda.inverseEvidence == true`.
           - Render an informative chip/text below the dropdown: `Text("Virhetutka vaatii 'Yksikin havainto riittää' -tilan", style: TextStyle(color: theme.colorScheme.primary, fontSize: 11))`.
        2. In `enforce_pre_flight` switch `onChanged`:
           - If `tda.syntacticAnchors.isEmpty`, display inline error text: `"Pikahylkäys vaatii vähintään yhden tunnistussanan"` and keep switch disabled until an anchor is typed.
        3. In `contrastive_example` and `extraction_rule` text fields:
           - Add real-time regex check for non-ASCII Finnish characters (`RegExp(r'[äöåÄÖÅ]')`).
           - If detected, display an amber helper warning: `"Huom: Kehotteiden ja esimerkkien tulee olla englanniksi (System Language)."`
        4. In modal save method:
           - Validate that no atom has `inverseEvidence == true && aggregationMode == AggregationMode.allMustComply`.
           - Validate that no atom has `enforcePreFlight == true && syntacticAnchors.isEmpty`.
      </instruction>
    </substep>
    <substep id="3.2" name="CLI Facade Integration in Matrix Hardening Loop">
      <action>Modify `scripts/matrix_hardening_loop.py` (`#L23-L39` imports and `#L290-L314` `main()`):</action>
      <instruction>
        1. Import `export_matrix_slice`, `detect_empirical_contamination`, `audit_atom_coherence`, `generate_theory_opponent_card`, `apply_matrix_slice`, and `append_matrix_theory_explanation` from `scripts.matrix_slice_engine`.
        2. Export the new symbols in `__all__`.
        3. In `main()`, add arguments:
           - `--slice` (type=str, metavar="MATRIX_ID", help="Export single matrix slice JSON to tmp/slices/<id>.json")
           - `--theory-card` (type=str, metavar="MATRIX_ID", help="Generate Theory Opponent Card prompt for matrix")
           - `--patch` (type=str, metavar="SLICE_FILE", help="Atomically patch matrix slice back into seed_data.json")
           - `--explain` (type=str, metavar="MATRIX_ID", help="Generate and append 2-paragraph English theory explanation to docs/architecture/08_matrix_explanations.md")
           - `--audit-contamination` (type=str, nargs="?", const="ALL", metavar="MATRIX_ID", help="Audit matrix for empirical run artifacts and Finnish case examples (defaults to ALL matrices)")
        4. Connect CLI routing:
           ```python
           if args.slice:
               out = export_matrix_slice(args.slice)
               print(f"SUCCESS: Exported matrix slice to {out}")
           elif args.theory_card:
               card = generate_theory_opponent_card(args.theory_card)
               print(card)
           elif args.patch:
               apply_matrix_slice(Path(args.patch))
               print(f"SUCCESS: Atomically applied slice {args.patch} to seed vault.")
           elif args.explain:
               append_matrix_theory_explanation(args.explain)
               print(f"SUCCESS: Appended theory explanation for {args.explain} to docs/architecture/08_matrix_explanations.md")
           elif args.audit_contamination:
               audit_matrix_contamination(args.audit_contamination)
           ```
      </instruction>
    </substep>
    <constraint invariant="surgical_precision_edits">Keep scripts/matrix_hardening_loop.py <= 335 lines.</constraint>
  </step>

  <step id="4" name="Phase 4: Comprehensive Unit & Anti-Happy-Path Testing">
    <action>Create `backend_v2/tests/unit/scripts/test_matrix_slice_engine.py` implementing the 11 locked test contracts:</action>
    <test_contracts>
      <contract id="TC-SLICE-01" category="positive">
        <name>test_export_matrix_slice_valid</name>
        <scenario>Export valid matrix block (e.g. blk_440a5fef9331451b) to custom tmp_path.</scenario>
        <expected>File exists, contains valid JSON, validates cleanly into MatrixPromptBlock with matching ID and >= 1 scale.</expected>
      </contract>
      <contract id="TC-SLICE-02" category="negative_error_path">
        <name>test_export_matrix_slice_invalid_id_raises</name>
        <scenario>Export non-existent matrix ID "blk_nonexistent_99999".</scenario>
        <expected>Raises ValueError containing "not found".</expected>
      </contract>
      <contract id="TC-SLICE-03" category="negative_boundary">
        <name>test_export_matrix_slice_non_matrix_category_raises</name>
        <scenario>Export an existing block that has category_id="persona" rather than "matrix".</scenario>
        <expected>Raises ValueError indicating block is not a matrix.</expected>
      </contract>
      <contract id="TC-SLICE-04" category="positive">
        <name>test_generate_theory_opponent_card_with_grounding</name>
        <scenario>Generate theory card for matrix with established theory grounding (Toulmin blk_440a5fef9331451b).</scenario>
        <expected>Output string contains theory citation, source URL, operational flags, and levels 1 to 5.</expected>
      </contract>
      <contract id="TC-SLICE-05" category="edge_case_resilience">
        <name>test_generate_theory_opponent_card_missing_grounding_resilience</name>
        <scenario>Generate theory card for a mock matrix where theory_grounding is None.</scenario>
        <expected>Function succeeds without AttributeError; output contains explicit alert "[THEORY GROUNDING ABSENT".</expected>
      </contract>
      <contract id="TC-SLICE-06" category="positive">
        <name>test_apply_matrix_slice_success</name>
        <scenario>Atomically patch a valid modified matrix slice into a temporary seed_data.json copy.</scenario>
        <expected>Target block is updated in mock seed_data.json; backup file is created in backups/ directory.</expected>
      </contract>
      <contract id="TC-SLICE-07" category="negative_rollback">
        <name>test_apply_matrix_slice_corrupted_rolls_back</name>
        <scenario>Attempt to patch a slice that causes pre-flight audit failure (simulated via mock or corrupted criteria).</scenario>
        <expected>Raises RuntimeError; seed_data.json is restored to original state; backup file remains intact.</expected>
      </contract>
      <contract id="TC-SLICE-08" category="cli_routing">
        <name>test_cli_flags_slice_theory_and_patch</name>
        <scenario>Invoke loop_main() via monkeypatched sys.argv with --slice, --theory-card, --patch, --explain, and --audit-contamination.</scenario>
        <expected>Each branch executes its corresponding engine function cleanly.</expected>
      </contract>
      <contract id="TC-SLICE-09" category="compendium_documentation">
        <name>test_append_matrix_theory_explanation_compendium</name>
        <scenario>Generate and append theory explanation for blk_440a5fef9331451b to a temporary compendium file.</scenario>
        <expected>Compendium contains "### Toulmin Argumentation Model" with exactly 2 paragraphs, no raw IDs, and valid rubric contents.</expected>
      </contract>
      <contract id="TC-SLICE-10" category="empirical_contamination_detection">
        <name>test_detect_empirical_contamination_flags_run_artifacts</name>
        <scenario>Execute detect_empirical_contamination on Toulmin matrix (blk_440a5fef9331451b) containing historical Finnish remote-work examples.</scenario>
        <expected>Returns findings identifying tda_69cc84e0b0c44996a8a95e09b356c692 and related atoms with non-English/empirical run text.</expected>
      </contract>
      <contract id="TC-SLICE-11" category="opponent_card_contamination_audit">
        <name>test_generate_theory_opponent_card_includes_contamination_audit</name>
        <scenario>Generate theory opponent card for a matrix with empirical contamination.</scenario>
        <expected>Card output string contains `<theory_calibration_audit>` tag specifying contaminated atom IDs and explicit instructions to derive domain-agnostic English exemplars from theory.</expected>
      </contract>
      <contract id="TC-SLICE-12" category="opponent_card_control_grounding">
        <name>test_generate_theory_opponent_card_explains_aggregation_and_steering_controls</name>
        <scenario>Generate theory opponent card for a matrix with mixed aggregation_mode and inverse_evidence atoms.</scenario>
        <expected>Card output string contains `<control_theory_grounding>` tag defining ALL_MUST_COMPLY vs EXISTS semantics and requiring theory-first justification for each steering control.</expected>
      </contract>
      <contract id="TC-SLICE-13" category="coherence_audit">
        <name>test_audit_atom_coherence_flags_inversion_paradox</name>
        <scenario>Execute audit_atom_coherence on a matrix containing inverse_evidence=True paired with ALL_MUST_COMPLY.</scenario>
        <expected>Returns findings identifying INVERSION_PARADOX and explaining that error radars require EXISTS.</expected>
      </contract>
      <contract id="TC-SLICE-14" category="pydantic_cross_validation">
        <name>test_tda_assertion_cross_field_validation_rejects_conflicting_flags</name>
        <scenario>Instantiate TDAAssertion with inverse_evidence=True and aggregation_mode="ALL_MUST_COMPLY", or enforce_pre_flight=True with empty syntactic_anchors.</scenario>
        <expected>Raises pydantic.ValidationError with specific field error message.</expected>
      </contract>
      <contract id="TC-SLICE-15" category="slice_patcher_coherence_guard">
        <name>test_apply_matrix_slice_rejects_incoherent_controls</name>
        <scenario>Attempt to apply a matrix slice JSON containing an incoherent atom configuration.</scenario>
        <expected>Raises ValueError; seed vault backup is untouched; aborts before writing.</expected>
      </contract>
      <contract id="TC-UI-01" category="flutter_widget_guardrail">
        <name>test_scale_editor_modal_locks_aggregation_mode_on_inverse_evidence</name>
        <scenario>Render ScaleEditorModal; toggle inverse_evidence switch to true.</scenario>
        <expected>aggregation_mode dropdown changes to 'exists' and 'all_must_comply' option is disabled.</expected>
      </contract>
    </test_contracts>
    <constraint invariant="anti_happy_path_mandate">Includes 9 negative and boundary error-path contracts (TC-SLICE-02, TC-SLICE-03, TC-SLICE-05, TC-SLICE-07, TC-SLICE-10, TC-SLICE-12, TC-SLICE-13, TC-SLICE-14, TC-SLICE-15).</constraint>
  </step>

  <step id="5" name="Phase 5: Quality Gate Auditing & Pilot Slice Execution">
    <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py scripts/matrix_slice_engine.py --test`.</action>
    <action>Run matrix hardening test suite: `uv run pytest backend_v2/tests/unit/scripts/test_matrix_slice_engine.py` and `uv run pytest backend_v2/tests/unit/scripts/test_matrix_hardening_loop.py`.</action>
    <action>Execute live pilot export: `uv run python scripts/matrix_hardening_loop.py --slice blk_440a5fef9331451b`.</action>
    <action>Verify `tmp/slices/blk_440a5fef9331451b.json` is <= 250 lines and re-validates into `MatrixPromptBlock`.</action>
    <action>Audit empirical contamination on Toulmin pilot: `uv run python scripts/matrix_hardening_loop.py --audit-contamination blk_440a5fef9331451b` (proves detection of contaminated Finnish remote-work data at tda_69cc84e0b0c44996a8a95e09b356c692).</action>
    <action>Execute physical database calibration patch on `blk_440a5fef9331451b` in `seed_data.json`:
      1. Calibrate `tmp/slices/blk_440a5fef9331451b.json` strictly through Stephen Toulmin (1958) argumentation theory:
         - Purge all Finnish case text; rewrite `contrastive_example` into pure domain-agnostic English theoretical pairs (Claim-Data-Warrant triads, Epistemic Qualifiers, Rebuttals).
         - Re-align `concept_description` and `extraction_rule` to Toulmin's structural definitions.
         - Calibrate `bounding_box_scope`: `sentence` for dogmatic assertions; `paragraph` for warrant bridges.
         - Enforce `aggregation_mode`: `EXISTS` on qualitative qualifiers (Level 3-4) and error radars (`inverse_evidence=True`); `ALL_MUST_COMPLY` on universal structural validity (Level 5).
      2. Apply calibrated slice atomically to database: `uv run python scripts/matrix_hardening_loop.py --patch tmp/slices/blk_440a5fef9331451b.json`.
      3. Verify pre-flight in-memory audit passes and backup is preserved in `backend_v2/seed/backups/`.
    </action>
    <action>Initialize `docs/architecture/08_matrix_explanations.md` with the Toulmin Argumentation Model reference entry via `uv run python scripts/matrix_hardening_loop.py --explain blk_440a5fef9331451b`.</action>
    <action>Run database atom verification linter: `uv run python scripts/audit_database_atoms.py --strict` (asserts 100% clean database state with zero contamination and zero incoherent controls).</action>
  </step>
</execution_protocol>
```

---

## Verification Plan

### Automated Testing
1. **Python Unit & Regression Tests (All 15 Backend Test Contracts):**
   ```powershell
   uv run pytest backend_v2/tests/unit/scripts/test_matrix_slice_engine.py -v
   ```
2. **Flutter Widget Test (Screen Guardrail Contract TC-UI-01):**
   ```powershell
   flutter test client_app_v2/test/features/studio/views/widgets/scale_editor_modal_test.dart
   ```
3. **Matrix Hardening Regression Suite:**
   ```powershell
   uv run pytest backend_v2/tests/unit/scripts/test_matrix_hardening_loop.py -v
   ```
4. **Backend Audit Loop (Ruff formatting, MyPy strict typing, Pytest coverage >= 90%):**
   ```powershell
   uv run python scripts/backend_audit_loop.py scripts/matrix_slice_engine.py --test
   ```
5. **Database Atoms Linter Verification:**
   ```powershell
   uv run python scripts/audit_database_atoms.py --strict
   ```

### Manual Verification
1. **Export a single matrix slice via CLI:**
   ```powershell
   uv run python scripts/matrix_hardening_loop.py --slice blk_440a5fef9331451b
   ```
2. **Audit empirical contamination in single matrix or all matrices:**
   ```powershell
   uv run python scripts/matrix_hardening_loop.py --audit-contamination blk_440a5fef9331451b
   ```
3. **Generate the Theory Opponent Card with Contamination Audit:**
   ```powershell
   uv run python scripts/matrix_hardening_loop.py --theory-card blk_440a5fef9331451b
   ```
4. **Verify slice payload bounds:**
   Verify that the exported slice in `tmp/slices/blk_440a5fef9331451b.json` is completely self-contained, valid JSON, under 250 lines, and loads in <1,500 tokens.
