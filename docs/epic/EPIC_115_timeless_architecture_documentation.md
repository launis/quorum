# EPIC 115: Timeless Architecture Documentation Reform

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
>
> The "Living Documentation" paradigm is the dominant 2026 industry mandate: architecture documentation must be treated as a critical, evolving asset synchronized with the codebase, not a static one-time deliverable ([docs-as-code best practices, 2026 industry reports](https://www.writethedocs.org/guide/docs-as-code/)). The **Dual-Axis Documentation Model** — separating machine-readable knowledge (Knowledge Items, `.agents/rules/`) from human-readable narrative (`docs/architecture/`) — directly aligns with the 2025-2026 AI-Readable Architecture (SysMARA) trend, where structural constraints are formally defined machine-traversable artifacts and human documentation is a derived, coherent projection ([AI-Readable Architecture, KM 2026](https://doi.org/10.1007/978-3-031-00000-0_1)). Key validation sources:
> - **"As-Built" vs. "Design Intent" Separation:** Modern engineering distinguishes forensic records of what is actually running from design aspirations. EPIC 115 enforces that the 6 pillar documents describe the system exactly as it exists today — an objective, factual state.
> - **Architecture Decision Records (ADRs):** Capture the "why" to prevent "architectural amnesia" and repeated debates. EPIC 115 routes all structural reasoning through Knowledge Items (KIs) rather than embedding project history in the pillar narratives.
> - **AI-Assisted Documentation Automation:** The `/tier7-describe-architecture` workflow acts as the automated CI engine for pillar synchronization, validated against live KI state — aligning with 2026 CI/CD documentation validation pipelines.
> - **Targeted Views for Different Audiences:** Machine-readable KIs serve AI agents for execution logic; human-readable pillars serve developers for narrative understanding — eliminating the "ineffective zone" of forcing a single document to serve both audiences.

---

## 1. Goal Description & Background (Objective & Problem Statement)

Evolve the `docs/architecture/` directory into a strict, timeless "As-Built" source of truth. The documentation must explain the architecture purely based on current capabilities and Knowledge Items (KIs), absolutely free from historical narratives, temporal contexts (e.g., "currently we are building", "previously this was"), or project tracking (e.g., Epic IDs, Jira tickets).

**Core Objectives:**
1. **Structural Scrubbing:** Remove all temporal contamination (Epic IDs, dates, legacy migration language) and physical file paths from the 6 architecture pillar documents.
2. **Dual-Axis Documentation Paradigm:** Establish a formal boundary — AI agents read `rules/` and KIs for execution logic; humans read `docs/architecture/` for narrative understanding.
3. **Meta-Governance Document:** Create a guiding `00_README_META_ARCHITECTURE.md` to enforce timelessness permanently.
4. **Tier 7 Workflow Hardening:** Harden the `/tier7-describe-architecture` workflow to enforce the timeless mandate at the orchestration level.
5. **Execution Workflow Re-routing:** Surgically re-route all execution workflows (Tier 2/3/4/5) from direct pillar file editing to KI creation + Tier 7 delegation.

---

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (`What We Will REMOVE`)

| Deprecated Element | Location | Rationale |
|---|---|---|
| Physical Implementation Map sections | All 6 pillar documents (`01_`–`06_`) | File paths belong exclusively in @[c:\src\quorum\.agents\rules\04_directory_reference.md]; cluttering timeless pillars violates As-Built purity |
| Inline `**Path:** backend_v2/...` references | @[c:\src\quorum\docs\architecture\06_enriched_atom_graph_engine.md] (lines 8, 12, 20, 24) | Same as above |
| Inline physical file paths in Pillar 02 Section 2.5 | @[c:\src\quorum\docs\architecture\02_data_seeding_and_ontology.md] (line 28) | Paths `backend_v2/models/v2_core.py` and `client_app_v2/lib/shared/models/i18n_text.dart` must be removed |
| All historical references | All 6 pillar documents | Epic IDs, dates, version migration language ("V1 to V2"), "previously"/"legacy"/"backward compatibility" comparisons |
| Temporal contamination in Pillar 02 Line 20 | @[c:\src\quorum\docs\architecture\02_data_seeding_and_ontology.md] | 4 violations: `from V1 to V2 paradigms`, `backward compatibility`, `older JSON definitions`, `legacy parsing logic` |
| "Following the Universal DTO Bridge (Epic 91.5)" | @[c:\src\quorum\docs\architecture\06_enriched_atom_graph_engine.md] (line 29) | Epic ID reference violates timelessness |
| `__pycache__/` directory | `docs/architecture/__pycache__/` | Rogue filesystem pollution |
| Direct `docs\architecture\` modification mandates | 6 execution workflows (see Phase 2 table) | Replaced by KI creation + Tier 7 delegation pattern |

### Retained SSOT Invariants (`What We Will RETAIN`)

| Retained Element | Rationale |
|---|---|
| 6 Capability-Driven Pillar documents (01–06) | Core As-Built narrative architecture; timeless theoretical descriptions preserved |
| All theoretical component descriptions in pillars | Conceptual knowledge about component names, responsibilities, data flows — only inline paths are removed |
| Knowledge Item (KI) database in `<appDataDir>\knowledge\` | Machine-readable truth backbone; unchanged by this Epic |
| `.agents/rules/` machine-readable rules | Execution logic for AI agents; unchanged by this Epic |
| @[c:\src\quorum\.agents\rules\04_directory_reference.md] as physical path SSOT | All physical paths route here exclusively |
| `documentation_present_tense_mandate` in @[c:\src\quorum\.agents\rules\00-antigravity-core.md] | Global foundation rule; EPIC 115 extends it with domain-specific enforcement |

### Compliance & Modernity Gates

| Quorum Invariant | EPIC 115 Compliance |
|---|---|
| Zero Legacy State Support | ✅ This Epic actively purges all legacy/historical language from architecture docs |
| Central Config Sovereignty | ✅ No config changes; all structural paths routed to `04_directory_reference.md` |
| Cross-Domain DTO Parity | ✅ No Pydantic/Freezed model changes |
| Static-First Caching Topology | ✅ No prompt changes |

### Producer-Consumer Integration Check

| Producer | Consumer | Contract |
|---|---|---|
| Knowledge Items (KIs) in `<appDataDir>\knowledge\` | `/tier7-describe-architecture` workflow | Tier 7 reads KI database and synchronizes English narrative in pillar documents |
| @[c:\src\quorum\.agents\rules\00-antigravity-core.md] `dual_axis_documentation_mandate` | All execution workflows (Tier 2/3/4/5) | Workflows delegate doc updates to KI creation + Tier 7, never edit pillars directly |
| @[c:\src\quorum\docs\architecture\00_README_META_ARCHITECTURE.md] | Human developers & AI agents entering `docs/architecture/` | Meta-governance document enforces timelessness rules before any pillar interaction |

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 0: Prerequisites & Rogue Cleanup

#### Task 0.1: Delete Rogue `__pycache__/`
Delete the `__pycache__/` directory inside `docs/architecture/`. This is rogue filesystem pollution.

---

### Phase 1: Structural Scrubbing (Zero-Behavioral Change)

> **Constraint:** This phase MUST be purely structural. No new features, no new rule files, no new documents. Only removal of violations and synthesis of existing knowledge into compliant form.

#### Task 1.1: Synthesize Physical Implementation Map Knowledge

Before removing any Physical Implementation Map sections, the executing agent MUST verify that the conceptual knowledge they contain (component names, responsibilities, data flows) is already described in the theoretical sections of each pillar document. If any component mentioned ONLY in the Physical Implementation Map has no theoretical description, synthesize it into the appropriate section as clear, descriptive text (without file paths).

**Special Handling — Pillar 06 (@[c:\src\quorum\docs\architecture\06_enriched_atom_graph_engine.md]):**
Pillar 06 is structurally unique: it embeds `**Path:** backend_v2/...` references **inline** within its component descriptions (lines 8, 12, 20, 24). The executing agent MUST:
1. Preserve the conceptual descriptions of each component (Extractive Sensor Service, Topological Evaluator, Result Projector, Sliding Window Linker).
2. Remove the inline `**Path:** ...` lines.
3. Verify that @[c:\src\quorum\.agents\rules\04_directory_reference.md] already covers these paths under the `backend_v2/services/` module.

**Special Handling — Pillar 02 (@[c:\src\quorum\docs\architecture\02_data_seeding_and_ontology.md]):**
Pillar 02 line 28 (Section 2.5 — Universal I18n Domain Model) embeds inline physical file paths (`backend_v2/models/v2_core.py` and `client_app_v2/lib/shared/models/i18n_text.dart`) within the theoretical I18nText description. The executing agent MUST remove these inline paths and verify that @[c:\src\quorum\.agents\rules\04_directory_reference.md] already covers them under the `backend_v2/models/` and `client_app_v2/lib/shared/` modules.

**General Sweep — ALL Pillars:**
After handling the Pillar 06 and Pillar 02 special cases above, the executing agent MUST `grep_search` ALL 6 pillar documents for any remaining inline file path patterns (e.g., `backend_v2/`, `client_app_v2/`, `.py`, `.dart`) in the theoretical body text (not the Physical Implementation Map sections, which are removed separately in Task 1.2). Any discovered paths MUST be removed and verified to exist in @[c:\src\quorum\.agents\rules\04_directory_reference.md].

#### Task 1.2: Remove Temporal Contamination & Physical Implementation Maps

Execute on all 6 architecture pillar documents:
1. Remove all Physical Implementation Map sections (verified to exist in all 6 pillars).
2. Remove all historical references: Epic IDs, dates, version migration language ("V1 to V2"), "previously"/"legacy"/"backward compatibility" comparisons. The executing agent MUST `grep_search` each pillar for the patterns `Epic`, `V1`, `legacy`, `backward`, `previously`, `migration`, `older`, `Phase \d` after scrubbing to verify zero remaining violations.
3. **Specific Fix — @[c:\src\quorum\docs\architecture\02_data_seeding_and_ontology.md] Line 20:** The entire sentence contains 4 violations (`from V1 to V2 paradigms`, `backward compatibility`, `older JSON definitions`, `legacy parsing logic`). Replace the full sentence:
   - **Before:** `"The system uses a Y-Funnel architecture where Pre-Hooks manage structural migrations (e.g., from V1 to V2 paradigms) *before* data enters the domain validation phase. This ensures backward compatibility for older JSON definitions without polluting the strict Pydantic V2 Domain Models with legacy parsing logic."`
   - **After:** `"The system uses a Y-Funnel architecture where Pre-Hooks perform structural data normalization *before* data enters the domain validation phase. This ensures heterogeneous JSON definitions are canonicalized into strict Pydantic V2 Domain Models without polluting the domain layer with transformation logic."`
4. **Specific Fix — @[c:\src\quorum\docs\architecture\06_enriched_atom_graph_engine.md] Line 29:** Remove "Following the Universal DTO Bridge (Epic 91.5)" — replace with a timeless factual statement about the DTO decoupling requirement (e.g., "The engine strictly decouples logical graph execution from server-driven UI elements.").

#### Task 1.3: Fix Pillar Count References

Update all instances of "5 pillar" / "5 core capabilities" to "6 pillar" / "6 core capabilities" (including Enriched Atom Graph Engine) in:
1. @[c:\src\quorum\.agents\workflows\tier7-describe-architecture.md] — 5 occurrences at lines 15, 16, 42, 46, 48.
2. @[c:\src\quorum\.agents\rules\04_directory_reference.md] — line 113: update to "6 Capability-Driven Pillar documents (System Context, Ontology, Orchestration, SDUI, Resilience, Enriched Atom Graph Engine)".

---

### Phase 2: Orchestration, Registry & Architectural Feature Hardening (Dual-Axis Documentation Paradigm)

> **Constraint:** This phase introduces new features: the Meta README, the Dual-Axis mandate, and the workflow re-routing. It MUST only execute after Phase 1 is complete and verified.

#### Task 2.1: [NEW] Create Meta-Governance Document

**File:** @[c:\src\quorum\docs\architecture\00_README_META_ARCHITECTURE.md]

Create a new English narrative file inside the architecture directory to guide developers and AI agents.

**Content Outline:**
1. **The Dual-Axis Documentation Paradigm:** Explain the fundamental separation between Machine-Readable Truth (KIs and `.agents/rules` for the AI) and Human-Readable Truth (the 6 pillars for humans).
2. **The Purpose:** Explain that this directory contains the 6 pillars of the Capability-Driven Architecture. These are timeless, stateless documents that describe "What is", not "How we got here".
3. **The Golden Rule (Timelessness):** Explicitly ban Epic IDs (e.g., EPIC_92), dates (e.g., "in 2026"), historical comparisons ("unlike the old legacy code"), and future plans ("we will build").
4. **Not a Pillar:** Explicitly state that this file is a META governance document, not the 7th pillar. The 6 pillars are 01-06.
5. **How to Update (Continuous Integration via Tier 7):**
   - Describe how the `/tier7-describe-architecture` workflow acts as the continuous integration engine for these files.
   - Any time a Knowledge Item (KI) is added, modified, or deleted in `knowledge/`, Tier 7 reads the KI database and updates the English theory in the relevant pillar to match. **Crucially:** These updates MUST be seamlessly integrated into the cohesive narrative of the document. Appending bulleted lists of changes or changelogs is strictly forbidden.
   - Tier 7 ensures all structural constraints are mapped to @[c:\src\quorum\.agents\rules\04_directory_reference.md] instead of cluttering the timeless pillars with physical paths.

#### Task 2.2: [MODIFY] Harden Tier 7 Workflow

**File:** @[c:\src\quorum\.agents\workflows\tier7-describe-architecture.md]

Add a strict new rule block to the Tier 7 system prompt to enforce the timeless mandate at the orchestration level.

**Changes:**
1. Add `<rule_block id="timeless_as_built_mandate">` to `<context_rules>`:
   ```xml
    <rule_block id="timeless_as_built_mandate">
      <mandatory_pattern>All theoretical descriptions in the architecture pillars MUST be strictly timeless and read as cohesive narratives. When updating documents based on new KIs, you MUST integrate the new information seamlessly into the relevant sections. You are FORBIDDEN from simply appending bulleted lists, changelogs, or "recent changes" to the bottom of the document. You are also FORBIDDEN from including project identifiers (e.g., "Epic 94", "Phase 3"), dates (e.g., "2025"), historical context (e.g., "Previously we used X, now we use Y"), or future plans (e.g., "We will implement Z"). Describe the system exactly as it exists today as an objective, factual state. NOTE: This rule is the domain-specific extension of the global `documentation_present_tense_mandate` in `00-antigravity-core.md`.</mandatory_pattern>
      <catastrophic_reason>Including historical data or appending unintegrated changelogs rapidly turns architecture documentation into a stale, fragmented project log rather than a pure Source of Truth, breaking the AI's ability to understand the current structural invariants.</catastrophic_reason>
   </rule_block>
   ```
2. Update `<step id="5">` to explicitly mention running timelessness cleanup while modifying theory.
3. **Pillar Count Fix:** All references to "5 pillar documents" or "5 core capabilities" MUST be updated to "6 pillar documents" and "6 core capabilities" (already tracked in Task 1.3, but Tier 7 modifications in Phase 2 should use the corrected count).

#### Task 2.3: [MODIFY] Introduce Dual-Axis Documentation Mandate in Core Rules

**File:** @[c:\src\quorum\.agents\rules\00-antigravity-core.md]

**Changes:**
1. Add a `<rule_block id="dual_axis_documentation_mandate">` to `<ide_orchestration_protocol>`. This rule MUST:
   - Define the boundary: AI agents read `rules/` and KIs for execution logic; humans read `docs/architecture/` for narrative understanding.
   - Strictly forbid standard AI coding workflows from manually editing the 6 architecture pillar documents (`01_` through `06_`).
   - Route all structural documentation updates through: (a) KI creation/update → (b) `/tier7-describe-architecture` automated sync.
   - Permit direct updates ONLY to @[c:\src\quorum\.agents\rules\04_directory_reference.md] for physical path changes.

#### Task 2.4: [MODIFY] Re-route Execution Workflows

**Files:** 6 execution workflows in @[c:\src\quorum\.agents\workflows\]

Audit and update the core execution workflows to align with the Dual-Axis Documentation Paradigm. The existing "DOCUMENTATION AUDIT MANDATE" steps in 6 workflows currently instruct agents to "physically modify the documents in `docs/architecture/`". These MUST be surgically re-routed.

**Exact Workflows and Replacement Pattern:**

| Workflow File | Step | Required Change |
|---|---|---|
| @[c:\src\quorum\.agents\workflows\tier2-execute.md] | Step 7 | Replace `docs\architecture\` modification mandate with KI creation + Tier 7 delegation. Keep `04_directory_reference.md` direct update. |
| @[c:\src\quorum\.agents\workflows\tier3-feature-refactor.md] | Step 6 | Same pattern as above. |
| @[c:\src\quorum\.agents\workflows\tier2-hardening-backend.md] | Step 9 | Same pattern as above. |
| @[c:\src\quorum\.agents\workflows\tier2-hardening-frontend.md] | Step 3 | Same pattern as above. |
| @[c:\src\quorum\.agents\workflows\tier4-bug-hunting.md] | Step 7 | Same pattern as above. |
| @[c:\src\quorum\.agents\workflows\tier5-session-handover.md] | Step 2 | Replace `docs\architecture\` verification with KI audit check. Keep `04_directory_reference.md` verification. |

> **Standard Replacement Text (to be adapted per workflow's existing phrasing):**
> "DOCUMENTATION & KI AUDIT: If the [operation] introduced new systems, modified data flows, or shifted architectural boundaries, you MUST create or update a Knowledge Item (KI) documenting the new pattern. The `/tier7-describe-architecture` workflow handles narrative sync to `docs/architecture/` automatically. You MUST still directly update `.agents/rules/04_directory_reference.md` for physical path changes. Do NOT manually edit the 6 architecture pillar documents (`docs/architecture/01_` through `06_`)."

> **Execution Constraint:** When modifying these 6 workflow files, the executing AI MUST strictly use the `multi_replace_file_content` tool for surgical edits. Full file overwrites (`write_to_file`) are strictly forbidden due to the large size and complexity of these system prompt files.

> **NOTE:** @[c:\src\quorum\.agents\workflows\tier1-planner.md] does not currently contain any documentation audit mandate referencing `docs\architecture\`. No re-routing is needed for this workflow.

#### Task 2.5: [MODIFY] Update Directory Reference

**File:** @[c:\src\quorum\.agents\rules\04_directory_reference.md]

1. Update the `docs/architecture/` module definition to reflect **6 Capability-Driven Pillar documents** (including Enriched Atom Graph Engine), correcting the outdated reference to 5 pillars.
2. Add `00_README_META_ARCHITECTURE.md` as a meta-governance document (not a pillar).

---

### Phase 3: Verification & E2E Integration Gate

> **Constraint:** This phase MUST only execute after Phase 1 and Phase 2 are complete and verified.

#### Task 3.1: Phase 1 Verification (Structural Scrubbing)

1. Verify all 6 pillar documents contain zero Epic IDs, dates, or "backward compatibility" language via `grep_search` for patterns: `Epic`, `V1`, `legacy`, `backward`, `previously`, `migration`, `older`, `Phase \d`.
2. Verify all 6 pillar documents have no Physical Implementation Map sections.
3. Verify all 6 pillar documents have no inline file paths (`backend_v2/`, `client_app_v2/`, `.py`, `.dart`) in theoretical body text.
4. Verify @[c:\src\quorum\.agents\rules\04_directory_reference.md] covers all previously inline-referenced paths.

#### Task 3.2: Phase 2 Verification (Dual-Axis Paradigm)

1. Trigger `/tier7-describe-architecture` to confirm the workflow operates correctly with the new `timeless_as_built_mandate` rule and correct 6-pillar count.
2. Verify no execution workflow (Tier 2/3/4/5) contains instructions to manually edit `docs/architecture/` pillar files.
3. Verify @[c:\src\quorum\docs\architecture\00_README_META_ARCHITECTURE.md] exists and contains the Dual-Axis Paradigm, Golden Rule, and Tier 7 CI integration sections.
4. Verify @[c:\src\quorum\.agents\rules\00-antigravity-core.md] contains the `dual_axis_documentation_mandate` rule block.

---

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)

- [ ] All 6 architecture pillar documents are 100% free from temporal contamination (Epic IDs, dates, legacy migration language, "previously"/"backward compatibility" comparisons).
- [ ] All Physical Implementation Map sections removed from all 6 pillar documents.
- [ ] All inline file paths removed from pillar theoretical text; verified present in @[c:\src\quorum\.agents\rules\04_directory_reference.md].
- [ ] Pillar count corrected from "5" to "6" in @[c:\src\quorum\.agents\workflows\tier7-describe-architecture.md] and @[c:\src\quorum\.agents\rules\04_directory_reference.md].
- [ ] @[c:\src\quorum\docs\architecture\00_README_META_ARCHITECTURE.md] created with Dual-Axis Paradigm, Golden Rule (Timelessness), and Tier 7 CI integration guidance.
- [ ] `timeless_as_built_mandate` rule block added to @[c:\src\quorum\.agents\workflows\tier7-describe-architecture.md].
- [ ] `dual_axis_documentation_mandate` rule block added to @[c:\src\quorum\.agents\rules\00-antigravity-core.md].
- [ ] All 6 affected execution workflows re-routed from direct pillar editing to KI creation + Tier 7 delegation.
- [ ] `__pycache__/` removed from `docs/architecture/`.
- [ ] Pillar 02 Line 20 sentence replaced (Y-Funnel temporal contamination fix).
- [ ] Pillar 06 Line 29 Epic reference replaced with timeless factual statement.

### Automated Unit Tests

No domain code changes in this Epic; no `backend_audit_loop.py` or `flutter_audit_loop.py` runs required.

### Manual Verification Steps

1. After Phase 1 execution, `grep_search` all 6 pillar documents for patterns: `Epic`, `V1`, `legacy`, `backward`, `previously`, `migration`, `older`, `Phase \d` — expect zero matches.
2. After Phase 1 execution, verify all 6 pillar documents have no Physical Implementation Map sections.
3. After Phase 2 execution, trigger `/tier7-describe-architecture` to confirm the workflow operates correctly with the new `timeless_as_built_mandate` rule and correct 6-pillar count.
4. After Phase 2 execution, `grep_search` all execution workflows for `docs\\architecture\\` modification mandates — expect zero matches (only KI creation + Tier 7 delegation references should remain).
5. After Phase 2 execution, verify @[c:\src\quorum\docs\architecture\00_README_META_ARCHITECTURE.md] contains the 5 content sections specified in Task 2.1.

### MANDATORY Final E2E Verification Gate

Since this Epic contains no domain code changes, the standard E2E REST API test gate (`$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`) is not applicable. The E2E verification is replaced by the comprehensive manual `grep_search` sweeps defined above, confirming zero temporal contamination across all affected files.
