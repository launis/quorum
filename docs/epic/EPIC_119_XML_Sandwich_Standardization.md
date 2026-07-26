# EPIC 119: Universal XML Sandwich & Context Quarantine Standardization

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
> Recent industry research on Autonomous Agent architectures has confirmed that "bigger is not better" regarding LLM context windows. Relying on massive (1M+) token contexts leads to severe "context amnesia" and the "lost-in-the-middle" phenomenon (neuraltrust.ai, 2026). The production standard for 2026 is **Context Engineering** and **Agentic Isolation** (Context Quarantine) as documented by Anthropic's research on sub-agent isolation and the broader industry shift from "Prompt Engineering" to "System Design" (shareuhack.com, logrocket.com, 2026). By utilizing micro-chunking (small, isolated XML execution blocks) and strict session resets (wiping the "Scratchpad/Buffer" tier of memory), agents maintain mathematical precision and avoid cross-contamination of instructions. This Epic aligns Quorum's auxiliary workflows with these proven industry standards.

## 1. Goal Description & Background (Objective & Problem Statement)
**Objective:** Standardize the remaining execution and planning workflows (`tier3-feature-refactor`, `tier3-god-code-decomposition`, and `tier4-bug-hunting`) to fully adopt the **Hybrid XML Sandwich Architecture** and strict session handovers, using risk-proportional quarantine boundaries.

**Problem Statement:**
While major feature development (`tier1-planner` / `tier2-execute`) has successfully migrated to the micro-chunked XML architecture, smaller tasks and bug hunts still rely on on-the-fly execution within a single, continuously growing context window.
- In Tier 3 (God Code), decomposing massive files generates enormous context from symbol inventories and blast radius mapping. Attempting extraction in the same session risks amnesia-driven regressions.
- In Tier 3 (Feature), complex multi-file refactors accumulate context that degrades precision, while trivial single-file changes do NOT carry this risk.
- In Tier 4, the deep grep-searching required for Root Cause Analysis (RCA) saturates the context window. If the agent attempts to fix the bug in the same session, it frequently hallucinates or breaks unrelated code.

By standardizing workflows to generate atomic `<execution_protocol>` XML plans and forcing `/tier5-resume` handovers before execution (with a proportional exemption for trivial tasks), we ensure deterministic, amnesia-free coding across the entire project lifecycle.

---

## 2. Architectural Impact & Compliance Matrix

### What We Will REMOVE (Deprecations & Sunset List)
- **Unconditional On-the-fly Execution in Tier 3 God Code & Tier 4**: The ability for these high-risk workflows to diagnose AND write code in the same session will be strictly deprecated.
- **Unstructured Sub-plans in Tier 3 God Code**: The generation of plain-text markdown sub-plans during God Code decomposition will be sunset. All generated sub-plans must use the `<execution_protocol>` XML schema.

### What We Will RETAIN (Retained SSOT Invariants)
- The core investigative powers of `tier4-bug-hunting.md` (RCA, 5 Whys, grep tracing, regression test writing).
- The Strangler Fig methodology in `tier3-god-code-decomposition.md`.
- The ability for `tier3-feature-refactor.md` to execute trivial, low-risk changes (≤2 files, ≤1 milestone) in a single session.

### What We Will NOT Touch (Explicit Exclusions)
- **`tier2-hardening-backend.md` and `tier2-hardening-frontend.md`**: These workflows are already structured for iterative, single-file-at-a-time processing with built-in session handover triggers. Their context growth is inherently bounded. No changes required.
- **`tier0-create-plan.md`**: Already contains the `HYBRID_XML_SANDWICH_MANDATE`. No changes required.
- **`tier1-planner.md` / `tier2-execute.md`**: Already fully migrated. No changes required.

### Compliance & Modernity Gates
- **Context Quarantine Mandate**: All high-risk workflows must explicitly mandate a session handover (`/tier5-resume`) between the Planning/Analysis phase and the Execution phase.
- **Hybrid XML Sandwich Mandate**: Every generated plan, regardless of size, must contain an `<execution_protocol>` block inside a fenced ` ```xml ``` ` codeblock. This is the **plan-level** execution schema (not to be confused with the `<execution_block>` tags inside Epic documents, which are Epic-level constructs parsed by `/tier1-planner`).
- **Proportional Quarantine Gate**: `tier3-feature-refactor` uses a conditional threshold — only tasks exceeding 2 target files or 1 milestone trigger the mandatory session split.

### Producer-Consumer Integration Check
- **Producer**: `tier3` and `tier4` workflows will now act as **Producers** of XML micro-plans, saved as system Artifacts (in the Antigravity brain directory, consistent with `tier0-create-plan` behavior).
- **Consumer**: `tier2-execute` acts as the **Consumer** of these micro-plans via `/tier5-resume`. The plan artifact serves as the `implementation_plan.md` input. `tier2-execute` already has all required safety gates (Pre-Flight Codebase Scan, XML Sandwich Completeness Mandate, Circuit Breaker).

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Modernize God Code Decomposition
Update `@[c:\src\quorum\.agents\workflows\tier3-god-code-decomposition.md]`.
#### [MODIFY] tier3-god-code-decomposition.md
- **Action 1**: Inject the `HYBRID_XML_SANDWICH_MANDATE` as a new `<constraint>` inside Step 3 (`PHASE 2: Micro-Chunking & Lazy Plan Generation`).
- **Constraint**: Explicitly require that generated `phaseX_extraction.md` files wrap their step-by-step instructions in `<execution_protocol>` XML blocks inside fenced ` ```xml ``` ` codeblocks, matching the format produced by `tier0-create-plan`.
- **Action 2**: Update Step 5 (`PHASE 4 (Embedded Handover Context)`) and Step 6 (`PHASE 5 (Stop & Present)`) to reinforce that the agent MUST instruct the user to execute plans in a fresh context window via `/tier5-resume --workflow=/tier2-execute`.

### Phase 2: Restructure Feature Refactoring (Conditional Quarantine)
Update `@[c:\src\quorum\.agents\workflows\tier3-feature-refactor.md]`.
#### [MODIFY] tier3-feature-refactor.md
- **Action 1**: Add a new `<rule_block id="conditional_context_quarantine">` to `<context_rules>`. This rule defines the threshold: If the task modifies >2 target files OR the plan requires >3 distinct execution steps, the agent MUST generate an `implementation_plan.md` Artifact (XML Sandwich format) and halt with a `/tier5-resume --workflow=/tier2-execute` command. If the task is at or below this threshold, in-session execution is permitted.
- **Action 2**: Modify Step 1 to include a `<gate name="COMPLEXITY_ASSESSMENT">` that evaluates the task scope against the threshold BEFORE execution begins.
- **Action 3**: Add explicit conditional logic to Step 4 (`ATOMIC EXECUTION BATCH & PAUSE`). If the complexity threshold was breached, the agent MUST NOT execute the code. Instead, it must jump directly to a new `HANDOVER` step to stop the session.
- **Constraint**: The `HYBRID_XML_SANDWICH_MANDATE` applies to all generated plans regardless of whether execution continues in-session or is deferred.

### Phase 3: Context Quarantine for Bug Hunting
Update `@[c:\src\quorum\.agents\workflows\tier4-bug-hunting.md]`.
#### [MODIFY] tier4-bug-hunting.md
- **Action 1**: Add a new `<rule_block id="rca_quarantine_mandate">` to `<architectural_invariants>`. This rule mandates that the RCA session (Steps 1-3: identification, regression test writing, and proof of failure) stays in the current session. The fix itself MUST be deferred to a fresh session executing `tier2-execute`.
- **Action 2**: Modify Step 4 (`BLAST RADIUS ANALYSIS & THE 5 WHYS`). After the 5 Whys analysis and blast radius mapping, the agent MUST generate a `bug_fix_plan.md` Artifact using the XML Sandwich format, containing the precise fix instructions, `@-referenced` target files, and architectural constraints.
- **Action 3**: Add a new Step 5 (`QUARANTINE HANDOVER`) that halts execution and provides a `/tier5-resume --workflow=/tier2-execute` command pointing to the generated plan.
- **Action 4**: EXPLICITLY DELETE the old Step 5 (`FIX & VERIFY (GREEN)`), Step 6 (`END-TO-END SMOKE TEST`), and Step 7 (`DOCUMENTATION & KI AUDIT`). These actions are now the responsibility of the `tier2-execute` consumer session.
- **Constraint (Regression Test Preservation)**: The existing "ATOMIC INTERFACE EXCEPTION" in Step 2 is RETAINED. If writing the failing test requires a structural change (e.g., schema modification) to compile, the test AND the interface change are permitted in the RCA session. The quarantine boundary is AFTER the failing test passes (Step 3), not before.

---

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done
- All three target workflow files contain the `HYBRID_XML_SANDWICH_MANDATE` requiring `<execution_protocol>` blocks in generated plans.
- `tier3-god-code-decomposition.md` and `tier4-bug-hunting.md` contain unconditional quarantine gates (`/tier5-resume`) before code execution.
- `tier3-feature-refactor.md` contains a conditional quarantine gate with a clearly defined threshold (>2 files or >1 milestone).
- All generated plans are saved as system Artifacts (not in `docs/epic/`).

### Verification Steps
- **Automated Verification**: Run `/tier8-red-teaming-audit` against the three updated workflow files to ensure they contain no logical loopholes allowing uncontrolled single-session execution beyond the defined thresholds.
- **Manual Verification (Bug Hunting)**: Run a `/tier4-bug-hunting` session on a known bug. Verify it stops after RCA (Steps 1-3) and generates a machine-readable XML plan Artifact.
- **Manual Verification (Feature Refactor)**: Run a `/tier3-feature-refactor` session for a trivial change (1 file). Verify it executes in-session. Then run one for a complex change (3+ files). Verify it halts and produces a plan.
- **Manual Verification (God Code)**: Run a `/tier3-god-code-decomposition` session. Verify generated sub-plans contain `<execution_protocol>` XML blocks.
