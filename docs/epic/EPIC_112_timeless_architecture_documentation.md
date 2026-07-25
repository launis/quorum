# EPIC 112: Timeless Architecture Documentation Reform

## Goal
Evolve the `docs/architecture` directory into a strict, timeless "As-Built" source of truth. The documentation must explain the architecture purely based on current capabilities and Knowledge Items (KIs), absolutely free from historical narratives, temporal contexts (e.g., "currently we are building", "previously this was"), or project tracking (e.g., Epic IDs, Jira tickets). We will create a guiding Meta-README, introduce a Dual-Axis Documentation Paradigm, and harden the Tier 7 workflow to enforce this permanently.

## Open Questions
- Should the `00_README_META_ARCHITECTURE.md` be the very first file an AI reads when entering the `docs/architecture` folder, or should we include its rules directly in the Tier 7 workflow? (The proposed plan does both for maximum safety).

---

## Phase A: Structural Scrubbing (Zero-Behavioral Change)

> **Constraint:** This phase MUST be purely structural. No new features, no new rule files, no new documents. Only removal of violations and synthesis of existing knowledge into compliant form.

### Phase A.1: Synthesize Physical Implementation Map Knowledge

Before removing any Physical Implementation Map sections, the executing agent MUST verify that the conceptual knowledge they contain (component names, responsibilities, data flows) is already described in the theoretical sections of each pillar document. If any component mentioned ONLY in the Physical Implementation Map has no theoretical description, synthesize it into the appropriate section as clear, descriptive text (without file paths).

**Special Handling — Pillar 06 ([06_enriched_atom_graph_engine.md](file:///c:/src/quorum/docs/architecture/06_enriched_atom_graph_engine.md)):**
Pillar 06 is structurally unique: it embeds `**Path:** backend_v2/...` references **inline** within its component descriptions (lines 8, 12, 20, 24). The executing agent MUST:
1. Preserve the conceptual descriptions of each component (Extractive Sensor Service, Topological Evaluator, Result Projector, Sliding Window Linker).
2. Remove the inline `**Path:** ...` lines.
3. Verify that `04_directory_reference.md` already covers these paths under the `backend_v2/services/` module.

**Special Handling — Pillar 02 ([02_data_seeding_and_ontology.md](file:///c:/src/quorum/docs/architecture/02_data_seeding_and_ontology.md)):**
Pillar 02 line 28 (Section 2.5 — Universal I18n Domain Model) embeds inline physical file paths (`backend_v2/models/v2_core.py` and `client_app_v2/lib/shared/models/i18n_text.dart`) within the theoretical I18nText description. The executing agent MUST remove these inline paths and verify that `04_directory_reference.md` already covers them under the `backend_v2/models/` and `client_app_v2/lib/shared/` modules.

**General Sweep — ALL Pillars:**
After handling the Pillar 06 and Pillar 02 special cases above, the executing agent MUST `grep_search` ALL 6 pillar documents for any remaining inline file path patterns (e.g., `backend_v2/`, `client_app_v2/`, `.py`, `.dart`) in the theoretical body text (not the Physical Implementation Map sections, which are removed separately in Phase A.2). Any discovered paths MUST be removed and verified to exist in `04_directory_reference.md`.

### Phase A.2: Remove Temporal Contamination & Physical Implementation Maps

Execute on all 6 architecture pillar documents:
1. Remove all Physical Implementation Map sections (verified to exist in all 6 pillars).
2. Remove all historical references: Epic IDs, dates, version migration language ("V1 to V2"), "previously"/"legacy"/"backward compatibility" comparisons. The executing agent MUST `grep_search` each pillar for the patterns `Epic`, `V1`, `legacy`, `backward`, `previously`, `migration`, `older`, `Phase \d` after scrubbing to verify zero remaining violations.
3. **Specific Fix — [02_data_seeding_and_ontology.md](file:///c:/src/quorum/docs/architecture/02_data_seeding_and_ontology.md) Line 20:** The entire sentence contains 4 violations (`from V1 to V2 paradigms`, `backward compatibility`, `older JSON definitions`, `legacy parsing logic`). Replace the full sentence:
   - **Before:** `"The system uses a Y-Funnel architecture where Pre-Hooks manage structural migrations (e.g., from V1 to V2 paradigms) *before* data enters the domain validation phase. This ensures backward compatibility for older JSON definitions without polluting the strict Pydantic V2 Domain Models with legacy parsing logic."`
   - **After:** `"The system uses a Y-Funnel architecture where Pre-Hooks perform structural data normalization *before* data enters the domain validation phase. This ensures heterogeneous JSON definitions are canonicalized into strict Pydantic V2 Domain Models without polluting the domain layer with transformation logic."`
4. **Specific Fix — [06_enriched_atom_graph_engine.md](file:///c:/src/quorum/docs/architecture/06_enriched_atom_graph_engine.md) Line 29:** Remove "Following the Universal DTO Bridge (Epic 91.5)" — replace with a timeless factual statement about the DTO decoupling requirement (e.g., "The engine strictly decouples logical graph execution from server-driven UI elements.").

### Phase A.3: Fix Pillar Count References

Update all instances of "5 pillar" / "5 core capabilities" to "6 pillar" / "6 core capabilities" (including Enriched Atom Graph Engine) in:
1. [tier7-describe-architecture.md](file:///c:/src/quorum/.agents/workflows/tier7-describe-architecture.md) — 5 occurrences at lines 15, 16, 42, 46, 48.
2. [04_directory_reference.md](file:///c:/src/quorum/.agents/rules/04_directory_reference.md) — line 113: update to "6 Capability-Driven Pillar documents (System Context, Ontology, Orchestration, SDUI, Resilience, Enriched Atom Graph Engine)".

### Phase A.4: Rogue Cleanup

Delete the `__pycache__/` directory inside `docs/architecture/`. This is rogue filesystem pollution.

---

## Phase B: New Architectural Features (Dual-Axis Documentation Paradigm)

> **Constraint:** This phase introduces new features: the Meta README, the Dual-Axis mandate, and the workflow re-routing. It MUST only execute after Phase A is complete and verified.

### [NEW] [00_README_META_ARCHITECTURE.md](file:///c:/src/quorum/docs/architecture/00_README_META_ARCHITECTURE.md)
Create a new English narrative file inside the architecture directory to guide developers and AI agents.

**Content Outline:**
1. **The Dual-Axis Documentation Paradigm:** Explain the fundamental separation between Machine-Readable Truth (KIs and `.agents/rules` for the AI) and Human-Readable Truth (the 6 pillars for humans).
2. **The Purpose:** Explain that this directory contains the 6 pillars of the Capability-Driven Architecture. These are timeless, stateless documents that describe "What is", not "How we got here".
3. **The Golden Rule (Timelessness):** Explicitly ban Epic IDs (e.g., EPIC_92), dates (e.g., "in 2026"), historical comparisons ("unlike the old legacy code"), and future plans ("we will build").
4. **Not a Pillar:** Explicitly state that this file is a META governance document, not the 7th pillar. The 6 pillars are 01-06.
5. **How to Update (Continuous Integration via Tier 7):**
   - Describe how the `/tier7-describe-architecture` workflow acts as the continuous integration engine for these files.
   - Any time a Knowledge Item (KI) is added, modified, or deleted in `knowledge/`, Tier 7 reads the KI database and updates the English theory in the relevant pillar to match. **Crucially:** These updates MUST be seamlessly integrated into the cohesive narrative of the document. Appending bulleted lists of changes or changelogs is strictly forbidden.
   - Tier 7 ensures all structural constraints are mapped to `04_directory_reference.md` instead of cluttering the timeless pillars with physical paths.

---

### [MODIFY] [tier7-describe-architecture.md](file:///c:/src/quorum/.agents/workflows/tier7-describe-architecture.md)
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
3. **Pillar Count Fix:** All references to "5 pillar documents" or "5 core capabilities" MUST be updated to "6 pillar documents" and "6 core capabilities" (already tracked in Phase A.3, but Tier 7 modifications in Phase B should use the corrected count).

---

### [MODIFY] [00-antigravity-core.md](file:///c:/src/quorum/.agents/rules/00-antigravity-core.md)
Introduce the "Dual-Axis Documentation Mandate" to the core IDE environment rules.

**Changes:**
1. Add a `<rule_block id="dual_axis_documentation_mandate">` to `<ide_orchestration_protocol>`. This rule MUST:
   - Define the boundary: AI agents read `rules/` and KIs for execution logic; humans read `docs/architecture/` for narrative understanding.
   - Strictly forbid standard AI coding workflows from manually editing the 6 architecture pillar documents (`01_` through `06_`).
   - Route all structural documentation updates through: (a) KI creation/update → (b) `/tier7-describe-architecture` automated sync.
   - Permit direct updates ONLY to `.agents/rules/04_directory_reference.md` for physical path changes.

---

### [MODIFY] `.agents/workflows/*` (Execution Workflow Re-routing)
Audit and update the core execution workflows to align with the Dual-Axis Documentation Paradigm. The existing "DOCUMENTATION AUDIT MANDATE" steps in 6 workflows currently instruct agents to "physically modify the documents in `docs/architecture/`". These MUST be surgically re-routed.

**Exact Workflows and Replacement Pattern:**

| Workflow File | Step | Required Change |
|---|---|---|
| [tier2-execute.md](file:///c:/src/quorum/.agents/workflows/tier2-execute.md) | Step 7 | Replace `docs\architecture\` modification mandate with KI creation + Tier 7 delegation. Keep `04_directory_reference.md` direct update. |
| [tier3-feature-refactor.md](file:///c:/src/quorum/.agents/workflows/tier3-feature-refactor.md) | Step 6 | Same pattern as above. |
| [tier2-hardening-backend.md](file:///c:/src/quorum/.agents/workflows/tier2-hardening-backend.md) | Step 9 | Same pattern as above. |
| [tier2-hardening-frontend.md](file:///c:/src/quorum/.agents/workflows/tier2-hardening-frontend.md) | Step 3 | Same pattern as above. |
| [tier4-bug-hunting.md](file:///c:/src/quorum/.agents/workflows/tier4-bug-hunting.md) | Step 7 | Same pattern as above. |
| [tier5-session-handover.md](file:///c:/src/quorum/.agents/workflows/tier5-session-handover.md) | Step 2 | Replace `docs\architecture\` verification with KI audit check. Keep `04_directory_reference.md` verification. |

**Standard Replacement Text (to be adapted per workflow's existing phrasing):**
> "DOCUMENTATION & KI AUDIT: If the [operation] introduced new systems, modified data flows, or shifted architectural boundaries, you MUST create or update a Knowledge Item (KI) documenting the new pattern. The `/tier7-describe-architecture` workflow handles narrative sync to `docs/architecture/` automatically. You MUST still directly update `.agents/rules/04_directory_reference.md` for physical path changes. Do NOT manually edit the 6 architecture pillar documents (`docs/architecture/01_` through `06_`)."

> **NOTE:** [tier1-planner.md](file:///c:/src/quorum/.agents/workflows/tier1-planner.md) does not currently contain any documentation audit mandate referencing `docs\architecture\`. No re-routing is needed for this workflow.

---

### [MODIFY] [04_directory_reference.md](file:///c:/src/quorum/.agents/rules/04_directory_reference.md)
1. Update the `docs/architecture/` module definition to reflect **6 Capability-Driven Pillar documents** (including Enriched Atom Graph Engine), correcting the outdated reference to 5 pillars.
2. Add `00_README_META_ARCHITECTURE.md` as a meta-governance document (not a pillar).

---

## Verification Plan

### Manual Verification
- After Phase A execution, verify all 6 pillar documents contain zero Epic IDs, dates, or "backward compatibility" language via `grep_search`.
- After Phase A execution, verify all 6 pillar documents have no Physical Implementation Map sections.
- After Phase B execution, trigger `/tier7-describe-architecture` to confirm the workflow operates correctly with the new `timeless_as_built_mandate` rule and correct 6-pillar count.
- After Phase B execution, verify no execution workflow (Tier 2/3/4/5) contains instructions to manually edit `docs/architecture/` pillar files.
