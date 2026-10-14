# IMPLEMENTATION PLAN: Dual-Track Rubric Refactoring & Scoring Architecture Synchronization

<required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
</required_context_rules>

---

## 1. Title & Executive Objective

### Title
**Dual-Track Rubric Refactoring, Seed Vault Sanitization, Multi-Surface Presentation Parity, and Scoring Architecture Documentation Synchronization**

### Executive Objective
Systematically eliminate the **Inverted Rubric Paradox** across all 13 affected evaluation matrices in `backend_v2/seed/seed_data.json` (across the 14-matrix ontology, with `matrix_toulmin` serving as golden reference), institute the mathematically rigorous **Dual-Track Rubric Standard** (Track A: Dreyfus/Bloom Progressive Competence with positive Level 1 novice baselines vs. Track B: Toulmin/Diagnostic Malus Error Radars with `inverse_evidence: True` on Levels 1–2), expand unit test verification in `backend_v2/tests/unit/utils/scoring/test_unified_engine.py` and `backend_v2/tests/unit/hooks/test_scoring.py`, synchronize central Knowledge Items (`ki_unified_matrix_scoring_strictness.md` and `ki_prompt_orchestration_and_matrix_evaluation.md`), and update the complete architectural documentation suite (`docs/architecture/08_matrix_explanations.md`, `03_cognitive_orchestration_engine.md`, `02_data_seeding_and_ontology.md`, `04_server_driven_ui_and_presentation.md`, and `06_enriched_atom_graph_engine.md`) to guarantee 100% conceptual, mathematical, and multi-surface presentation parity across Flutter Desktop UI, PDF reports, Corporate Excel workbooks (Tab 1 Summary & Tab 2 Raw Data), and rectangular 22-column machine-readable CSV streaming without numbering collisions or legacy regression.

---

## 2. Target Scope & Modification Boundaries

### Target Files (Read-Write Boundaries)
* `[MODIFY]` `@[backend_v2/seed/seed_data.json#L357-L20275]` - Central static seed vault containing prompt blocks, scales, claims, and TDA assertions for all 14 matrices.
* `[MODIFY]` `@[backend_v2/tests/unit/utils/scoring/test_unified_engine.py]` - Unit tests for `UnifiedScoringEngine` verifying cumulative novice scoring, strictness exponents, and error radar dynamics.
* `[MODIFY]` `@[backend_v2/tests/unit/hooks/test_scoring.py]` - Integration tests for matrix hook scoring verifying inverse evidence passage and level breakdown.
* `[MODIFY]` `@[ki_unified_matrix_scoring_strictness.md#L1-L176]` - SSOT Knowledge Item governing matrix scoring, strictness power curves, and the Dual-Track standard.
* `[MODIFY]` `@[ki_prompt_orchestration_and_matrix_evaluation.md#L1-L144]` - SSOT Knowledge Item governing TDA assertion compilation and inverse error radars.
* `[MODIFY]` `@[docs/architecture/08_matrix_explanations.md#L1-L625]` - Matrix Theory Explanations Compendium detailing BARS progressions and scoring mechanics.
* `[MODIFY]` `@[docs/architecture/03_cognitive_orchestration_engine.md#L1-L339]` - Cognitive Orchestration Engine documentation detailing scoring and normalization hooks.
* `[MODIFY]` `@[docs/architecture/02_data_seeding_and_ontology.md#L1-L74]` - Data Seeding & Ontology documentation detailing matrix schema rules and inverse evidence constraints.
* `[MODIFY]` `@[docs/architecture/04_server_driven_ui_and_presentation.md#L1-L240]` - Server-Driven UI documentation detailing Tab 1 matrix summary presentation, Tab 2 evidence badge formatting, Excel 2-tab export parity, and 22-column rectangular machine-readable CSV streaming.
* `[MODIFY]` `@[docs/architecture/06_enriched_atom_graph_engine.md#L1-L163]` - Enriched Atom Graph Engine documentation detailing matrix DAG evaluation and hit ratios.

### Context Files (Strictly Read-Only)
* `@[backend_v2/utils/scoring/unified_engine.py]` - Mathematical core of the unified weighted ratio scoring engine.
* `@[backend_v2/hooks/scoring/matrix_hook.py]` - Execution hook calculating matrix hits, DLQs, and raw scores.
* `@[backend_v2/hooks/scoring/normalization_hook.py]` - Execution hook normalizing raw matrix scores to the 0–100 scale.
* `@[backend_v2/hooks/scoring/falsifier_hook.py]` - Post-hook aggregating normalized matrix scores into `global_score` with passivity penalties.
* `@[backend_v2/services/blueprint.py]` - Blueprint transformer projecting `global_score` into presentation artifacts.
* `@[backend_v2/services/export_service.py]` - Export service generating corporate 2-tab Excel workbooks and 22-column denormalized CSV streaming.
* `@[backend_v2/services/localization.py]` - SSOT ReportHeaderResolver resolving localized column and sheet headers.
* `@[backend_v2/templates/report_template.jinja2]` - Server-side Jinja2 template rendering PDF reports and HTML preview tables.

---

## 3. Five-Column Architectural Directives & Pre-Implementation Cleanups

### 3.1 Five-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[backend_v2/seed/seed_data.json]`**<br>*(Track A: 6 Developmental Matrices: Bloom, HACM, Goodhart, Judge, Clarity, XAI-Reporter)* | Banned: Inverted Rubric Paradox (penalizing candidates who lack errors while rewarding novices with negative labels). Banned: Setting `inverse_evidence: true` on developmental Level 1 criteria. | Mandatory: Cumulative Guttman Invariant ($L_1 \subseteq L_2 \subseteq L_3 \subseteq L_4 \subseteq L_5$). Level 1 represents positive novice baseline capabilities with `inverse_evidence: false` and positive declarative claims. | Pruned: Redundant parallel rubric schemas or secondary scale-weight tables. Evaluated strictly via `UnifiedScoringEngine` weighted level ratios. | `uv run python backend_v2/seed/run_seed.py local --dry-run`<br>`uv run python scripts/audit_database_atoms.py --strict` |
| **`@[backend_v2/seed/seed_data.json]`**<br>*(Track B: 8 Diagnostic Matrices: Toulmin, Causal Analyst, Kahneman, Falsifier, Taskguard, Archivist, Causal Abductive, Epistemic Humility)* | Banned: Awarding positive capability points for simply not committing errors on Levels 1-2. Banned: Setting `inverse_evidence: false` on error radar criteria. | Mandatory: Two-Factor Orthogonal Malus. Levels 1-2 locked as "Kriittinen virhe / Vakava harhaluulo / Fatal Flaw" with `inverse_evidence: true` and `aggregation_mode: "EXISTS"`. Points accrue solely from positive mastery (Levels 3-5). | Pruned: Multi-engine branching or discrete heuristic threshold switches. Relies strictly on `UnifiedScoringEngine` orthogonal penalty deductions. | `uv run python backend_v2/seed/run_seed.py local --dry-run`<br>`uv run python scripts/audit_database_atoms.py --strict` |
| **`@[backend_v2/tests/unit/utils/scoring/test_unified_engine.py]`** | Banned: Writing self-validating, tautological unit tests or assuming positive Level 1 points give 0 score. Banned: Dict-based score assertions. | Mandatory: ISTQB boundary tests proving that a candidate fulfilling only Level 1 receives exactly $6.7\%$ linear score ($1.7\%$ under 70% strictness), and an expert fulfilling Levels 1-5 receives 100.0%. | Pruned: Complex mock frameworks. Uses pure in-memory `LevelStatsDTO` and direct `UnifiedScoringEngine.calculate()` invocation. | `uv run pytest backend_v2/tests/unit/utils/scoring/test_unified_engine.py -v` |
| **`@[backend_v2/tests/unit/hooks/test_scoring.py]`** | Banned: Deceptive persistence mocking or bypassing matrix hook verification of inverse evidence handling. | Mandatory: Integration tests verifying that inverse evidence passage on Levels 1-2 satisfies baseline checks without awarding positive points, and inverse evidence failure triggers orthogonal malus deduction. | Pruned: Complex multi-step workflow fixtures. Uses localized `InMemoryUnifiedWorkflowRepository` and direct `matrix_scoring_hook` execution. | `uv run pytest backend_v2/tests/unit/hooks/test_scoring.py -v` |
| **`@[ki_unified_matrix_scoring_strictness.md]` & `@[ki_prompt_orchestration_and_matrix_evaluation.md]`** | Banned: Leaving the Inverted Rubric Paradox undocumented in the Knowledge Base or conflating developmental and diagnostic evaluation paths. | Mandatory: Document Section 5 'Dual-Track Rubric Architecture: Progressive Novice vs Malus Error Radar' and 13 canonical TDA parameter boundaries for positive vs inverse evidence. | Pruned: Speculative architectural proposals or duplicate scoring formula explanations. Directly links to `UnifiedScoringEngine` SSOT. | `uv run python scripts/audit_markdown_boundaries.py` |
| **`@[docs/architecture/08_matrix_explanations.md]`** | Banned: Duplicate section numbering. Banned: Orphaned trailing text snippets (specifically: lines 620-625 in 08_matrix_explanations.md). | Mandatory: Present-tense authoritative documentation of current state. Section 2 updated with Track A/B column and Section 8.4 updated with exact weighted ratio and continuous dampening scoring formulas. | Pruned: Historical project phase narratives ("vaiheet", "Phase 1"), meta-rule headers ("The Laws"), and speculative future feature proposals. | `uv run python scripts/audit_markdown_boundaries.py --file docs/architecture/08_matrix_explanations.md` |
| **`@[docs/architecture/03_cognitive_orchestration_engine.md]`** | Banned: Adding duplicate or colliding subsection numbering (specifically: adding duplicate Section 2.12 colliding with existing Section 2.12). | Mandatory: Present-tense authoritative documentation of current state. Update Section 2.19 and Section 2.20 with Dual-Track mechanics and append Section 2.22 for commensurate multi-matrix global score aggregation without numbering collision. | Pruned: Historical narratives and speculative roadmap mentions. Pure present-tense operational description. | `uv run python scripts/audit_markdown_boundaries.py --file docs/architecture/03_cognitive_orchestration_engine.md` |
| **`@[docs/architecture/02_data_seeding_and_ontology.md]`** | Banned: Documenting permissive fallback schemas or unvalidated inverse evidence flags. | Mandatory: Document strict schema rules for `MatrixPromptBlock`, `MatrixScale`, and `TDAAssertion`, enforcing mandatory `inverse_evidence` boolean constraints. | Pruned: Speculative future schema proposals. Reflects active Pydantic V2 definitions. | `uv run python scripts/audit_markdown_boundaries.py --file docs/architecture/02_data_seeding_and_ontology.md` |
| **`@[docs/architecture/04_server_driven_ui_and_presentation.md]`** | Banned: Documenting client-side scoring recalculations or presentation-layer semantic badge mutation. Banned: Treating error radar levels 1-2 as positive capability points or allowing phantom 12.2% normalized scores on zero-competence outputs. | Mandatory: Document multi-surface presentation parity across Flutter UI, PDF, 2-tab Excel (`openpyxl`), and rectangular 22-column CSV (`export_flat_csv`). In Tab 1, Track A shows progressive competence percentages while Track B shows 0.0% clean baseline (no false positive 12.2% glitch) with explicit error findings. In Tab 2, positive claims show `+1 p` / `0 p` (`points_awarded: 1.0 / 0.0`); inverse claims show `Puhdas` / `Negatiivinen löydös` (`points_awarded: 0.0`). In CSV, enforce strict numeric typing (`is_inverse: 1/0`, `result_status: 1/0`, `points_awarded: 1.0/0.0`) and ML-ready causal graph attributes. | Pruned: Client-side logic heuristics. Pure declarative presentation block mapping. | `uv run python scripts/audit_markdown_boundaries.py --file docs/architecture/04_server_driven_ui_and_presentation.md` |
| **`@[docs/architecture/06_enriched_atom_graph_engine.md]`** | Banned: Conflating dynamic causal propositions with evaluative matrix scoring atoms. | Mandatory: Document the structural decoupling between causal graph propositions (result_status = 1 with 0.0 matrix points) and evaluative matrix TDA atoms. | Pruned: Speculative graph linking heuristics. Documents active wave-based topological evaluation. | `uv run python scripts/audit_markdown_boundaries.py --file docs/architecture/06_enriched_atom_graph_engine.md` |

### 3.2 Phase 1: Pre-Implementation Cleanups (Technical Debt Sweep)

Before introducing modified matrix definitions and documentation updates, the following pre-flight cleanups must be executed across touched files and 1-hop callers:
1. **Timestamped Seed Vault Backup:** Create an uncompressed, atomic backup copy of `backend_v2/seed/seed_data.json` inside `backend_v2/seed/backups/seed_data_backup_dual_track.json`.
2. **Pre-flight Schema Linter Validation:** Run `uv run python backend_v2/seed/run_seed.py local --dry-run` and `uv run python scripts/audit_database_atoms.py --strict` to verify 100% baseline schema integrity before any modification.
3. **Documentation Cleanup of Orphaned Snippet:** Remove the orphaned trailing Toulmin text at lines 620-625 of `docs/architecture/08_matrix_explanations.md`.
4. **Codebase Audit of 1-Hop Callers:** Verify zero `getattr/hasattr`, `.get(`, silent `except:`, `model_copy(update=)` in `backend_v2/utils/scoring/unified_engine.py`, `backend_v2/hooks/scoring/matrix_hook.py`, and `backend_v2/hooks/scoring/normalization_hook.py`.
5. **ISTQB Boundary Partitioning:** Verify all test cases enforce strict negative boundary conditions (clean baseline without positive points, detected error triggering orthogonal malus deduction) without tautological mocking.

---

## 4. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="SEED_VAULT_BACKUP_AND_PREFLIGHT_VERIFICATION">
    <action>Create a timestamped backup of the current seed vault @[backend_v2/seed/seed_data.json] before making modifications.</action>
    <command>Copy-Item backend_v2/seed/seed_data.json backend_v2/seed/backups/seed_data_backup_dual_track.json</command>
    <action>Run the seed database linter in dry-run mode to establish clean baseline status on @[backend_v2/seed/seed_data.json].</action>
    <command>uv run python backend_v2/seed/run_seed.py local --dry-run</command>
    <command>uv run python scripts/audit_database_atoms.py --strict</command>
    <constraint invariant="root_cause_first_over_reseed_mandate">Verify zero baseline corruption before modifying seed collections.</constraint>
  </step>

  <step id="2" name="SEED_VAULT_DUAL_TRACK_RUBRIC_REFACTORING">
    <action>Refactor the 13 flawed matrices in @[backend_v2/seed/seed_data.json] following the Dual-Track Rubric Standard.</action>
    
    <!-- TRACK A: 6 DEVELOPMENTAL MATRICES -->
    <substep id="2.1" name="REFACTOR_TRACK_A_DEVELOPMENTAL_MATRICES">
      <description>For each of the 6 developmental matrices in @[backend_v2/seed/seed_data.json], rename Level 1 to 'Alustava / Noviisi / Tunnistava' and rewrite its claims to represent cumulative positive baseline capabilities (inverse_evidence: false):
        1. blk_f921c7c0989b47e8 (matrix_bloom): Rename Level 1 to 'Muistaminen ja nimeäminen (Remembering)', convert claim to positive declarative recall of domain nomenclature.
        2. blk_7d8e9f0a1b2c3d4e (matrix_hacm): Rename Level 1 to 'Alustava ohjaus (Noviisi)', set claim to specifying clear core task and primary topic.
        3. blk_53f32679aa514fcb (matrix_goodhart): Rename Level 1 to 'Perusvuorovaikutus (Noviisi)', set claim to opening conversation with explicit question or assignment.
        4. blk_ff72c2d79edb4ebf (matrix_judge): Rename Level 1 to 'Pinnallinen arviointi (Noviisi)', set claim to providing explicit pass/fail decision with justification.
        5. blk_f6e286f050c94d60 (matrix_taskxai_clarity): Rename Level 1 to 'Alustava jäsentely (Noviisi)', set claim to identifying communicative goal and core theme.
        6. blk_6b8c766185294f7e (matrix_xai_reporter): Rename Level 1 to 'Peruskonsensus (Noviisi)', set claim to identifying basic shared findings across viewpoints.
      </description>
      <constraint invariant="prompt_preservation_mandate">Qualitative coaching philosophy must be preserved; refine level rubrics and criteria without amputating prompt texts.</constraint>
    </substep>

    <!-- TRACK B: 8 DIAGNOSTIC / ERROR RADAR MATRICES -->
    <substep id="2.2" name="REFACTOR_TRACK_B_DIAGNOSTIC_MATRICES">
      <description>For each of the 8 diagnostic matrices in @[backend_v2/seed/seed_data.json], retain Level 1-2 titles as 'Kriittinen virhe / Vakava harhaluulo / Fatal Flaw', and strictly set inverse_evidence: true on all Level 1 and Level 2 TDA assertions:
        1. blk_c5804a9143c34cb1 (matrix_causal_analyst): Set inverse_evidence: true on Level 1-2 correlation-as-causation fallacy atoms.
        2. blk_109dab5b6b3f403a (matrix_kahneman): Set inverse_evidence: true on Level 1-2 uncritical System 1 heuristic bias atoms.
        3. blk_b476f89fb732448c (matrix_falsifier): Set inverse_evidence: true on Level 1-2 confirmation bias and uncritical acceptance atoms.
        4. blk_80732a33fe1947ee (matrix_taskguard): Set inverse_evidence: true on Level 1-2 boundary violation and safety risk atoms.
        5. blk_fb15f8dcf23f4865 (matrix_archivist): Set inverse_evidence: true on Level 1-2 source disregard and ungrounded factual contradiction atoms.
        6. blk_c3bc5f3eb8e74110 (matrix_causal_abductive): Set inverse_evidence: true on Level 1-2 post-hoc rationalization and weak traceability atoms.
        7. blk_22e3598e06414409 (matrix_epistemic_humility): Set inverse_evidence: true on Level 1-2 overconfidence and dogmatic infallibility atoms.
        (Note: blk_440a5fef9331451b matrix_toulmin is already 100% compliant with 0 pos, 5 inv on L1-L2 and serves as golden reference.)
      </description>
      <constraint invariant="the_zero_compromise_pledge">Zero positive assertions permitted on Levels 1-2 of diagnostic error radar matrices.</constraint>
    </substep>
  </step>

  <step id="3" name="SCORING_UNIT_AND_PROPERTY_TEST_EXPANSION">
    <action>Expand test coverage in @[backend_v2/tests/unit/utils/scoring/test_unified_engine.py] and @[backend_v2/tests/unit/hooks/test_scoring.py] to mathematically prove the Dual-Track behavior.</action>
    <description>Add ISTQB-compliant test cases covering:
      1. test_dreyfus_cumulative_novice_scoring in @[backend_v2/tests/unit/utils/scoring/test_unified_engine.py]: Verifies that a candidate fulfilling only Level 1 receives exactly 6.7% linear score (1.7% under 70% strictness) and expert fulfilling Levels 1-5 receives 100.0%.
      2. test_dreyfus_expert_satisfies_novice_invariant in @[backend_v2/tests/unit/utils/scoring/test_unified_engine.py]: Verifies that an expert does not lose points on Level 1.
      3. test_toulmin_error_radar_clean_baseline in @[backend_v2/tests/unit/hooks/test_scoring.py]: Verifies that an execution with zero detected errors on Levels 1-2 receives 100% pass on inverse atoms and accrues positive points solely from Levels 3-5.
      4. test_toulmin_fatal_flaw_penalty_deduction in @[backend_v2/tests/unit/hooks/test_scoring.py]: Verifies that detecting a Level 1 error suppresses Level 1 points and triggers malus deduction.
    </description>
    <command>uv run pytest backend_v2/tests/unit/utils/scoring/test_unified_engine.py backend_v2/tests/unit/hooks/test_scoring.py -v</command>
    <constraint invariant="zero_tolerance_audit_loop">Automated tests must pass 100% before modifying documentation.</constraint>
  </step>

  <step id="4" name="KNOWLEDGE_ITEMS_SYNCHRONIZATION">
    <action>Update SSOT Knowledge Items @[ki_unified_matrix_scoring_strictness.md] and @[ki_prompt_orchestration_and_matrix_evaluation.md] to document the Dual-Track standard and eradicate legacy ambiguity.</action>
    <substep id="4.1" name="UPDATE_KI_UNIFIED_MATRIX_SCORING_STRICTNESS">
      <target>@[ki_unified_matrix_scoring_strictness.md]</target>
      <description>Incorporate Section 5: 'Dual-Track Rubric Architecture: Progressive Novice vs Malus Error Radar', detailing:
        - Exact mathematical hit ratio behavior for Track A vs Track B.
        - Cumulative Guttman Invariant (L1 in L2 in L3 in L4 in L5).
        - Inverted Rubric Paradox root cause and permanent prohibition.
        - Normalization and global score aggregation formula: average_score = sum(normalized_scores) / N * (1.0 - penalties).
      </description>
    </substep>
    <substep id="4.2" name="UPDATE_KI_PROMPT_ORCHESTRATION_AND_MATRIX_EVALUATION">
      <target>@[ki_prompt_orchestration_and_matrix_evaluation.md]</target>
      <description>Update matrix evaluation parameter guidelines to document the mandatory dichotomy: Developmental TDA atoms require positive evidence extraction; Diagnostic TDA atoms require inverse error radar falsification.</description>
    </substep>
  </step>

  <step id="5" name="ARCHITECTURE_COMPENDIUM_UPDATE_08_MATRIX_EXPLANATIONS">
    <action>Update @[docs/architecture/08_matrix_explanations.md] to reflect the refactored BARS progressions and scoring mechanics, and excise orphaned text.</action>
    <target>@[docs/architecture/08_matrix_explanations.md]</target>
    <description>Specifically update:
      1. Section 2 (Canonical Matrix Overview): Add 'Rubric Track' column designating Track A (Progressive Competence) vs Track B (Error Radar).
      2. Sections 3.2, 3.4, 3.6, 3.7, 3.8: Update BARS Level 1 descriptions to match refactored seed vault definitions (Track A Level 1 = Novice positive baseline; Track B Level 1-2 = Inverse error radar).
      3. Section 8.4 (Mathematical Bottom-Up Scoring &amp; Distribution): Expand mathematical documentation with the exact formulas for weighted level ratios, piecewise exponent dampening, per-matrix normalization, and multi-matrix global score aggregation.
      4. Excise orphaned duplicate Toulmin snippet at lines 620-625.
    </description>
    <constraint invariant="documentation_present_tense_mandate">Document exclusively in authoritative present tense describing current system state.</constraint>
  </step>

  <step id="6" name="ARCHITECTURE_PILLARS_DOCUMENTATION_SYNCHRONIZATION">
    <action>Synchronize scoring, matrix evaluation, multi-surface presentation parity, and machine-readability architecture sections across @[docs/architecture/03_cognitive_orchestration_engine.md], @[docs/architecture/02_data_seeding_and_ontology.md], @[docs/architecture/04_server_driven_ui_and_presentation.md], and @[docs/architecture/06_enriched_atom_graph_engine.md].</action>
    <substep id="6.1" name="UPDATE_03_COGNITIVE_ORCHESTRATION_ENGINE">
      <target>@[docs/architecture/03_cognitive_orchestration_engine.md]</target>
      <description>Update Section 2.19 (Continuous Strictness &amp; Unified Matrix Scoring Engine) and Section 2.20 (Automated Score Deduction Penalties &amp; Holistic Scoring Engine) to reflect the Dual-Track Rubric standard (Track A: Progressive Competence vs Track B: Two-Factor Orthogonal Malus Error Radars), exact weighted level ratio formulas, normalization hook behavior, and passivity penalty post-hook wiring; append Section 2.22 ('Commensurate Multi-Matrix Global Score Aggregation') preserving all existing sections 2.1 through 2.21 without numbering collision.</description>
    </substep>
    <substep id="6.2" name="UPDATE_02_DATA_SEEDING_AND_ONTOLOGY">
      <target>@[docs/architecture/02_data_seeding_and_ontology.md]</target>
      <description>Document schema requirements for MatrixPromptBlock, MatrixScale, and TDAAssertion, specifying mandatory inverse_evidence boolean constraints.</description>
    </substep>
    <substep id="6.3" name="UPDATE_04_SERVER_DRIVEN_UI_AND_PRESENTATION">
      <target>@[docs/architecture/04_server_driven_ui_and_presentation.md]</target>
      <description>Document comprehensive Dumb Painter presentation parity and machine readability across all four presentation surfaces:
        1. UI and PDF Tab 1 (Matrix Summary Table):
           - In Track A (Developmental Competence): Displays progressive level mastery with positive novice percentages (specifically 17.9% for HACM novice baseline). Jakauma displays standard progression (specifically: 1 - Matkustaja: 2/2, 2 - Reaktiivinen viilaaja: 1/2).
           - In Track B (Diagnostic Error Radars): Normalisoitu pisteytys resolves strictly to 0.0% if no positive mastery is demonstrated on levels 3-5, eliminating the legacy 12.2% phantom score glitch. Jakauma displays explicit diagnostic labels (specifically: 1 - Mahdoton (Kriittinen virhe): 1/1 (Havaittu virhe) when error occurs, or 0/1 (Puhdas) when clean).
        2. UI, PDF Tab 2 and Excel Tab 2 (Forensic Atom Breakdown):
           - Decoupled semantic badge rules via ReportAtomColumn and is_inverse_evidence:
             - Positive Claims (is_inverse: false): Passed atom displays '+1 p' (points_awarded: 1.0); unfulfilled atom displays '0 p' (points_awarded: 0.0).
             - Inverse Claims (is_inverse: true): Passed/clean atom (no error) displays 'Puhdas' (points_awarded: 0.0, zero false positive points); failed/detected error atom displays 'Negatiivinen löydös' with red visual alert, exact lexical quote citation, and triggers orthogonal malus deduction (points_awarded: 0.0).
        3. Excel Tab 1 (Yhteenveto):
           - Sarakkeet: Suoritustunniste, Logiikkamatriisi, Arvioinnin kohde, Jakauma, Osumat, Kriteerejä yhteensä, Osumasuhde, Pisteet, Maksimipisteet, Normalisoitu pisteytys, Selitys, Kriteerit, Lähde.
           - Track B Levels 1-2 hits do NOT count as positive capability points; total hits strictly reflect positive levels 3-5 (specifically: 0 / 8 instead of legacy 3 / 11), aligning normalized score at 0.0%.
        4. CSV 22-Column Rectangular Machine-Readability Standard (export_flat_csv):
           - Rectangular, denormalized, strictly typed 22 columns:
             1. Suoritustunniste (execution_id), 2. Logiikkamatriisi (matrix_label), 3. Arvioinnin kohde (context_target), 4. Jakauma (distribution), 5. Osumat (hits), 6. Kriteerejä yhteensä (total_atoms), 7. Osumasuhde (hit_ratio), 8. Pisteet (raw_score), 9. Maksimipisteet (scale_max), 10. Normalisoitu pisteytys (normalized_score), 11. Taso (level: 1..5), 12. Tason nimi (level_name), 13. Arviointikriteeri (criterion), 14. Väitetyyppi (claim_type: 'Positiivinen kyvykkyys' vs 'Virhedetektori / Anti-pattern'), 15. Käänteinen ehto (is_inverse: 1 or 0), 16. Saadut pisteet (points_awarded: 1.0 or 0.0), 17. Tulos (result_status: 1 or 0), 18. Tekstin havainto (quotes), 19. Selitys (ai_reasoning), 20. Kausaalistatus (causal_status: ROOT_CAUSE, ISOLATED, BLAMED, NORMAL), 21. Juurisyyn tunnus (blame_parent_id), 22. Riippuvuuksien lkm (dependent_count).
           - Mathematical scoring identity: points_awarded_val = 1.0 if (atom.status == PASSED and not is_inverse_claim) else 0.0.
           - Total mathematical insulation for automated ML/data pipelines: SUM(Saadut pisteet) never accumulates error detections as points.
      </description>
    </substep>
    <substep id="6.4" name="UPDATE_06_ENRICHED_ATOM_GRAPH_ENGINE">
      <target>@[docs/architecture/06_enriched_atom_graph_engine.md]</target>
      <description>Document the decoupling between causal graph propositions (result_status = 1 with 0.0 matrix points) and evaluative matrix TDA atoms.</description>
    </substep>
  </step>

  <step id="7" name="SEED_VAULT_IN_MEMORY_AUDIT_AND_ATOMIC_RESEED">
    <action>Execute two-phase pre-flight in-memory validation followed by atomic database synchronization on @[backend_v2/seed/seed_data.json].</action>
    <command>uv run python backend_v2/seed/run_seed.py local --dry-run</command>
    <command>uv run python scripts/audit_database_atoms.py --strict</command>
    <command>uv run python scripts/sanitize_seed_vault.py --reseed --test</command>
    <constraint invariant="vault_mutation_protocol">In-memory validation must achieve 100% pass before physical database sync.</constraint>
  </step>

  <step id="8" name="UNIVERSAL_QUALITY_GATES_AND_BOUNDARY_AUDIT">
    <action>Run the full automated quality gate loops and verify Markdown boundaries across all updated architecture documents: @[docs/architecture/08_matrix_explanations.md], @[docs/architecture/03_cognitive_orchestration_engine.md], @[docs/architecture/02_data_seeding_and_ontology.md], @[docs/architecture/04_server_driven_ui_and_presentation.md], and @[docs/architecture/06_enriched_atom_graph_engine.md].</action>
    <command>uv run python scripts/backend_audit_loop.py backend_v2 --test --ast-strict</command>
    <command>uv run python scripts/audit_markdown_boundaries.py --file docs/architecture/08_matrix_explanations.md</command>
    <command>uv run python scripts/audit_markdown_boundaries.py --file docs/architecture/03_cognitive_orchestration_engine.md</command>
    <command>uv run python scripts/audit_markdown_boundaries.py --file docs/architecture/02_data_seeding_and_ontology.md</command>
    <command>uv run python scripts/audit_markdown_boundaries.py --file docs/architecture/04_server_driven_ui_and_presentation.md</command>
    <command>uv run python scripts/audit_markdown_boundaries.py --file docs/architecture/06_enriched_atom_graph_engine.md</command>
    <constraint invariant="zero_tolerance_audit_loop">100% pass rate required across Ruff, MyPy, Pytest, and AST strict checks.</constraint>
  </step>
</execution_protocol>
```

---

## 5. Architectural Safeguards & Verification Plan

### Test Scenarios & ISTQB Partitions
1. **Positive Baseline Novice Partition (Track A):**
   - *Input:* Chat log with 1 prompt containing a clear task and topic, zero subsequent challenge.
   - *Expected:* Matrix 3 (`blk_53f32679aa514fcb`) passes Level 1 (2/2 hits). Pts awarded: $2/30$ ($6.7\%$ linear, $1.7\%$ curved under 70% strictness). Matrix score rises above zero to $1.1 / 5.0$ ($2.5 / 100$).
2. **Expert Superset Partition (Track A):**
   - *Input:* Rigorous 30-turn Socratic dialogue with challenge, edge cases, and reflection.
   - *Expected:* Matrix 3 passes Levels 1–5 ($30/30$ hits). Score: $5.0 / 5.0$ ($100.0 / 100$). No docked points for being an expert.
3. **Clean Error Radar Partition (Track B):**
   - *Input:* Logical argument without ad hominem or correlation-as-causation fallacies.
   - *Expected:* Toulmin Level 1–2 inverse atoms pass ($100\%$). Score reflects absence of defects without awarding false positive points. Tab 1 displays 0.0% normalized score (if no L3-5 claims demonstrated), Tab 2 displays `Puhdas` badges with `points_awarded: 0.0`, and CSV reflects `is_inverse: 1, result_status: 0, points_awarded: 0.0`.
4. **Fatal Flaw Detection Partition (Track B):**
   - *Input:* Argument containing explicit correlation-as-causation fallacies and dogmatic assertions on Levels 1-2, but no valid L3-5 inferences (User Screenshot Scenario).
   - *Expected:* Causal Analyst Level 1-2 atoms fail (`result_status: 1`, quote extracted). Normalized score is strictly 0.0% (suppressing legacy 12.2% phantom score) plus triggers malus penalty deduction. Tab 2 displays `Negatiivinen löydös` with `points_awarded: 0.0`, and CSV reflects `is_inverse: 1, result_status: 1, points_awarded: 0.0`.
5. **Multi-Surface Presentation Parity Partition:**
   - *Input:* Execution evaluated across Track A and Track B matrices.
   - *Expected:* Exact 1:1 numerical and semantic correspondence between Flutter UI table, PDF Jinja2 table, Corporate Excel 2-tab export, and rectangular CSV stream:
     - Track A: Level 1 shows `+1 p` / `points_awarded: 1.0` when passed.
     - Track B: Level 1-2 shows `Puhdas` / `points_awarded: 0.0` when clean, and `Negatiivinen löydös` / `points_awarded: 0.0` when detected.
6. **Machine-Readable CSV Invariance Partition:**
   - *Input:* Denormalized CSV dataset generated via `export_flat_csv`.
   - *Expected:* `SUM(Saadut pisteet)` equals the exact mathematical sum of positive capability hits, with zero point leakage from inverse error radar detections. `Käänteinen ehto == 1` and `Tulos == 1` deterministically isolate all reasoning errors.

---

## 6. Execution Command

To execute this hardened implementation plan, start a clean session and run:
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Dual_Track_Rubric_Refactoring_and_Scoring_Synchronization.md] @[docs/implementationplans/TRACKER_Dual_Track_Rubric_Refactoring_and_Scoring_Synchronization.md]
```
