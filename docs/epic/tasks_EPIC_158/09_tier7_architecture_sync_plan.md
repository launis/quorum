# Tier 7 Plan: As-Built Architectural Documentation & Knowledge Item Synchronization (Epic 158)

<domain_boundary>
  <role>AS-BUILT ARCHITECTURE SYNCHRONIZATION PLAN</role>
  <instruction>This implementation plan governs the post-implementation Tier 7 architectural synchronization for Epic 158. It anchors physical code implementations to theoretical Knowledge Items (Top-Down), synchronizes timeless architecture pillars in docs/architecture/, registers new physical modules in .agents/rules/04_directory_reference.md, and formalizes scientific definitions and benchmark proofs in docs/tiede.md.</instruction>
</domain_boundary>

<system_context>
  <epic>@[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md]</epic>
  <tracker>@[docs/epic/EPIC_158_tracker.md]</tracker>
  <command>/tier7-describe-architecture @[docs/epic/EPIC_158_tracker.md] @[docs/epic/EPIC_158_multi_segment_evidence_and_causal_horizon.md] @[ki_structured_forensic_quotes.md] @[ki_topological_engine.md] @[ki_unified_matrix_scoring_strictness.md] @[ki_prompt_orchestration_and_matrix_evaluation.md]</command>
</system_context>

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
  <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
  <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
</required_context_rules>

## Target Scope & Boundaries

### 1. Target Knowledge Items (`<appDataDir>/knowledge/`)
- `[MODIFY]` @[ki_structured_forensic_quotes.md] (artifacts + `metadata.json` updated timestamp and references)
- `[MODIFY]` @[ki_topological_engine.md] (artifacts + `metadata.json` updated timestamp and references)
- `[MODIFY]` @[ki_unified_matrix_scoring_strictness.md] (artifacts + `metadata.json` updated timestamp and references)
- `[MODIFY]` @[ki_prompt_orchestration_and_matrix_evaluation.md] (artifacts + `metadata.json` updated timestamp and references)

### 2. Directory Reference Laws
- `[MODIFY]` @[.agents/rules/04_directory_reference.md#L25-L30] (Register `backend_v2/tests/integration/test_multi_segment_causal_e2e.py`)
- `[MODIFY]` @[.agents/rules/04_directory_reference.md#L62-L72] (Register `backend_v2/models/dtos/quote_evidence.py`)
- `[MODIFY]` @[.agents/rules/04_directory_reference.md#L118-L122] (Register `scripts/run_ablation_benchmark.py`)

### 3. Timeless Architecture Pillars (`docs/architecture/`)
- `[MODIFY]` @[docs/architecture/01_system_context_and_invariants.md] (Incorporate Multi-Segment Forensic Quote Invariant and Decoupled Strictness Invariant into Section 3 System Invariants)
- `[MODIFY]` @[docs/architecture/03_cognitive_orchestration_engine.md] (Incorporate Bounded Deliverable Root Axiom Anchoring and SlidingWindowLinker dynamic quota allocation into topological evaluation narratives)
- `[MODIFY]` @[docs/architecture/04_server_driven_ui_and_presentation.md] (Incorporate multi-segment evidence citation rendering `join(' [...] ')` and continuous strictness slider into SDUI presentation narratives)

### 4. Scientific Manuscript (`docs/tiede.md`)
- `[MODIFY]` @[docs/tiede.md#L66-L83] (Definition 1: Ordered Bounding Span Vector)
- `[MODIFY]` @[docs/tiede.md#L84-L93] (Theorem: Lexical Specificity Invariant $\text{Specificity}_{lex} = 1.000$)
- `[MODIFY]` @[docs/tiede.md#L214-L222] (Section 4.1.1: Gate 5 Epistemic Strictness Decoupling)
- `[MODIFY]` @[docs/tiede.md#L236-L241] (Section 4.2: Bounded Deliverable Root Axiom Anchoring)
- `[MODIFY]` @[docs/tiede.md#L876-L936] (Section 8: Empirical Benchmark and False Omission Reduction Verification)

---

## Five-Column Architectural Directives

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Directory Reference Registration**<br>`04_directory_reference.md` | Omitting newly created test suites and DTOs from the directory index, forcing AI agents to guess paths. | Register `test_multi_segment_causal_e2e.py`, `quote_evidence.py`, and `run_ablation_benchmark.py` under their canonical section indices. | Ban redundant cross-category duplicate index entries. | `test_directory_reference_drift_detector_negative` in `test_phase8_documentation_contracts.py`. |
| **Knowledge Item Synchronization**<br>`ki_*.md` + `metadata.json` | Leaving KI summaries and timestamps stale after physical architectural modernization. | Synchronize all 4 KIs with exact physical models, update `metadata.json` references and ISO 8601 timestamps. | Keep KIs focused strictly on domain contracts; ban speculative future notes. | Verify all 4 `metadata.json` files parse as valid JSON with current references. |
| **Timeless Pillar Sync**<br>`docs/architecture/01, 03, 04` | Appending "Changelogs", development phases ("Phase 1-8"), Epic IDs ("Epic 158"), or "- **Law:**" labels. | Integrate modern multi-segment and decoupled strictness invariants seamlessly into existing narrative flow in present tense. | Strict adherence to `timeless_as_built_mandate` (pure present tense, zero Epic IDs, zero Law labels). | Zero occurrence of "Epic 158", "Phase 1", or "- **Law:**" in `docs/architecture/`. |
| **Scientific Manuscript Sync**<br>`docs/tiede.md` | Hand-waving mathematical claims without formal definitions or reporting unverified ablation numbers. | Formalize Definition 1 ($\vec{\mathcal{C}}_i$, $1 \le m \le 3$, monotonic spatial order, buffer isolation), prove Theorem on Lexical Specificity, and report verified empirical benchmarks. | Maintain clean mathematical elegance separating lexical containment from semantic entailment. | `test_tiede_latex_syntax_validity` passes with 0 syntax errors or unbalanced math environments. |

---

## Step-by-Step Execution Plan

### Step 1: Directory Reference Registration (`04_directory_reference.md`)
1. Register `backend_v2/tests/integration/test_multi_segment_causal_e2e.py` under the Python Backend Integration Tests directory index (lines 25-30).
2. Register `quote_evidence.py` under `backend_v2/models/dtos/` as SSOT for forensic evidence quote structures (`QuoteEvidenceDTO`, `GateMatchResultDTO`) (lines 62-72).
3. Register `scripts/run_ablation_benchmark.py (Offline Multi-Segment & Chimera Ablation Benchmark Suite)` under scripts/ module index (lines 118-125).

### Step 2: Knowledge Item Synchronization (4 Target KIs)
1. Verify and update `ki_structured_forensic_quotes.md` artifacts and `metadata.json`:
   - Monotonic ordering ($s_1 < e_1 < s_2 < e_2 \le s_1 + 1\,000$), buffer boundary isolation, immutable `source_quotes: tuple[str, ...] | None`.
   - Update `updated_at` timestamp.
2. Verify and update `ki_topological_engine.md` artifacts and `metadata.json`:
   - Bounded deliverable root axiom injection ($K_{axiom}^{max} = 8$ axioms where $InDegree(v)=0$), dynamic quota allocation ($W_{min} = 12, M_{win} \le 20$), Algorithm 1 dual fault attribution.
   - Update `updated_at` timestamp.
3. Verify and update `ki_unified_matrix_scoring_strictness.md` artifacts and `metadata.json`:
   - Gate 5 Epistemic Strictness Decoupling (`Workflow.default_lexical_strictness_level`), continuous Studio slider, and Gate 5 Snowball morphological calibration.
   - Update `updated_at` timestamp.
4. Verify and update `ki_prompt_orchestration_and_matrix_evaluation.md` artifacts and `metadata.json`:
   - Ordered 1–3 non-contiguous sentence extraction directives with strict anti-chimera validation.
   - Update `updated_at` timestamp.

### Step 3: Timeless Architecture Pillars Synchronization
1. `docs/architecture/01_system_context_and_invariants.md`:
   - Seamlessly describe Multi-Segment Forensic Evidence Vectors and Decoupled Strictness Invariant in present tense.
   - Assert zero historical phase progression language or Law/Enforcement meta-labels.
2. `docs/architecture/03_cognitive_orchestration_engine.md`:
   - Seamlessly describe Bounded Deliverable Root Axiom Anchoring ($K_{axiom}^{max} = 8$), dynamic quota allocation ($W_{min} = 12, M_{win} \le 20$), and Gate 5 Epistemic Strictness Decoupling.
3. `docs/architecture/04_server_driven_ui_and_presentation.md`:
   - Seamlessly describe Dumb Painter multi-segment quote rendering (`join(' [...] ')`), interactive CausalInspectorModal desktop canvas, and continuous strictness slider with 4 consequence zones.

### Step 4: Scientific Manuscript Formalization (`docs/tiede.md`)
1. Insert Definition 1: Ordered Bounding Span Vector $\vec{\mathcal{C}}_i = (\mathcal{C}_{i,1}, \dots, \mathcal{C}_{i,m})$ where $1 \le m \le 3$, monotonic ordering $s_1 < e_1 < s_2 < e_2 \le s_1 + 1\,000$, and buffer boundary isolation across source documents.
2. Insert Theorem on Lexical Specificity Invariant $\text{Specificity}_{lex} = 1.000$ with formal proof.
3. Insert Section 4.1.1 Gate 5 Epistemic Decoupling ($\zeta_{lex}$ vs $\zeta_{score}$).
4. Insert Section 4.2 Bounded Deliverable Root Axiom Anchoring ($K_{axiom}^{max} = 8, W_{min} = 12, M_{win} \le 20$).
5. Insert verified Phase 7 empirical benchmark table: reduction of $\widehat{\text{FOR}}$ from $13.33\%$ to $\le 2.00\%$, offline ablation pass rate $58.2\% \ge 56.4\%$, and $\bar{\kappa} \ge 0.9800$.

### Step 5: Verification & Quality Gate Execution
1. Run `uv run pytest backend_v2/tests/unit/test_phase8_documentation_contracts.py` to assert 100% LaTeX syntax validity and directory reference adherence.
2. Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_phase8_documentation_contracts.py --test --ast-strict`.
3. Update `docs/epic/EPIC_158_tracker.md` to transition `Documentation & Knowledge Item Update` from `[NOK]` to `[OK]`.
