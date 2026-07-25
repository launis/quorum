# EPIC 114: Shift-Left Testing & QA Architecture

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
> External validation confirms that embedding quality constraints directly inside the AI agent's decision loop ("Shift-In Testing", an evolution of "Shift-Left") combined with strict "Anti-Happy Path" (negative testing) constraints is the most modern and effective methodology for validating AI-generated code. AI coding agents inherently optimize for speed and frequently produce "confident lies"—code that looks correct but fails on boundary conditions or edge cases. By enforcing ISTQB-standard Equivalence Partitioning (EP) and Boundary Value Analysis (BVA) directly within the AI's execution loop, organizations can prevent the explosion of technical debt. Relying on agents to just "write tests" without explicit negative test constraints (Sad Path / Edge Cases) results in "fake confidence" where tests only validate the AI's own flawed assumptions. Furthermore, maintaining a Single Source of Truth for these rules (like `AGENTS.md`) is considered a critical architectural pattern (Agentic AI Foundation, 2026) to prevent Agentic Drift.

## 1. Goal Description & Background (Objective & Problem Statement)
**Problem Statement:** 
The greatest pitfall of AI-Driven Development is that Language Models inherently optimize for speed over quality. When operating freely, agents (e.g., Cursor, Cline, Aider) default to writing "happy path" code, systematically neglecting edge cases, robust error handling, and automated testing. In a highly complex environment like Quorum—featuring a FastAPI backend, Flutter frontend, Server-Driven UI (SDUI), and DAG-based LLM orchestration—omitting rigorous testing leads to an immediate and catastrophic explosion of technical debt.

**SSOT Context (Red-Team Correction):**
Quorum already possesses substantial testing mandates in `@[c:\src\quorum\.agents\rules\00-antigravity-core.md]` (`tdd_mandate`, `mocking_mandate_for_llm`, `deterministic_testing_delegation`, `fragmented_quality_gates_prevention`, `anti_tdd_trap`), plus embedded mandates in `@[c:\src\quorum\.agents\workflows\tier2-execute.md]` (Step 4: TDD), `@[c:\src\quorum\.agents\workflows\tier4-bug-hunting.md]` (Step 2: Regression Test), and `@[c:\src\quorum\.agents\workflows\tier1-planner.md]` (Step 10: Testing Strategy). The root problem is therefore NOT missing rules but **incomplete enforcement of existing rules** combined with **a single genuine gap**: no explicit mandate for negative/edge-case testing (anti-happy-path coverage).

**Objective:**
To counteract "Agentic Drift" toward untested code, this Epic closes the **single genuine gap** (anti-happy-path mandate) and strengthens the **compliance routing** between existing workflows and the `<universal_quality_gate>` in `@[c:\src\quorum\.agents\rules\00-antigravity-core.md]`. It additionally introduces a genuinely novel QA workflow for ISTQB-based test coverage expansion. 

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (What We Will REMOVE)
- **"Happy Path" Only Deliveries:** Delivery of features without corresponding negative tests and edge-case coverage will be blocked by a NEW `anti_happy_path_mandate` rule block. (This is the genuinely novel contribution of this Epic.)

### Retained SSOT Invariants (What We Will RETAIN)
- **ALL existing testing mandates** in `00-antigravity-core.md` (`tdd_mandate`, `mocking_mandate_for_llm`, `deterministic_testing_delegation`, `fragmented_quality_gates_prevention`, `anti_tdd_trap`) are RETAINED as the Single Source of Truth. This Epic does NOT duplicate or rephrase them.
- Existing execution workflows (Tiers 0-4) are retained with targeted compliance routing additions (NOT broad rewrites).
- The E2E SDUI Parity Testing Architecture (documented in KI `ki_e2e_sdui_parity_architecture.md`) and `sdui_contract_fracture_prevention` rule are RETAINED as the SSOT for contract testing.

### Compliance & Modernity Gates
- **Mandatory TDD:** ✅ ALREADY ENFORCED by `tdd_mandate` in `00-antigravity-core.md` (L182-185) and `tier2-execute.md` Step 4.
- **SDUI Contract Testing:** ✅ ALREADY ENFORCED by `sdui_contract_fracture_prevention` (L165-169), `cross_language_enum_parity` (01-python-backend.md L228-232), and `flutter_audit_loop.py --build`.
- **LLM Determinism Mocking:** ✅ ALREADY ENFORCED by `mocking_mandate_for_llm` (L193-196).
- **Anti-Happy-Path Coverage:** 🆕 NEW mandate to be added by this Epic.

### Producer-Consumer Integration Check
- **Workflow Producer:** The agent drafting implementation plans or executing code.
- **Validation Consumer:** The existing automated Quality Gate scripts (`backend_audit_loop.py`, `flutter_audit_loop.py`) enforced via the strengthened compliance routing.

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Targeted Compliance Routing Augmentation (ZERO BEHAVIORAL CHANGE)
**Architectural Constraint:** This phase performs ONLY structural routing additions — NO new testing logic, NO new rules. The goal is to ensure existing workflows explicitly cross-reference the `<universal_quality_gate>` in `00-antigravity-core.md` so agents cannot claim ignorance.

- **@[c:\src\quorum\.agents\workflows\tier0-create-plan.md] & @[c:\src\quorum\.agents\workflows\tier1-planner.md] (Test Scenario Mandate):**
  - Add a compliance routing instruction: "Every implementation plan MUST include explicit test scenarios with concrete inputs and expected outputs for BOTH success AND failure paths (minimum 2 negative scenarios per feature)."
  - Note: Test Pyramid alignment (Unit/Integration/E2E) is ALREADY mandated by `tier1-planner.md` Step 10. DO NOT duplicate.
- **@[c:\src\quorum\.agents\workflows\tier2-execute.md] (Compliance Routing):**
  - TDD Red-Green-Refactor is ALREADY enforced in Step 4. Add a single routing line: "You MUST enforce ALL rule blocks in the `<universal_quality_gate>` section of `00-antigravity-core.md` — no rule block may be skipped."
- **@[c:\src\quorum\.agents\workflows\tier4-bug-hunting.md] (Already Compliant):**
  - Step 2 (REGRESSION TEST MANDATE) already mandates a failing test before any production code modification. NO changes required. Verify by reading the file.

### Phase 2: Establish Test Coverage Expansion Workflow (NEW)
Create a single genuinely novel workflow:
- **@[c:\src\quorum\.agents\workflows\tier8-test-coverage-expansion.md] (Edge Cases & ISTQB):**
  - Prompt the AI to apply ISTQB techniques: Boundary Value Analysis and Equivalence Partitioning.
  - Require at least two negative test cases (e.g., missing inputs, incorrect types, `AppException` paths) for every successful test.
  - Include a `polyfactory` fixture generation mandate for randomized schema-compliant data.
  - Include explicit routing to the Universal Quality Gate and `backend_audit_loop.py` / `flutter_audit_loop.py` for coverage verification.

**REMOVED (Red-Team Correction):**
- ~~`tier8-contract-testing.md`~~: **REMOVED.** SDUI contract integrity is already enforced by `sdui_contract_fracture_prevention` rule + `cross_language_enum_parity` rule + E2E SDUI Parity KI (`ki_e2e_sdui_parity_architecture.md`) + `flutter_audit_loop.py --build`. A separate workflow would create SSOT fragmentation.
- ~~`tier8-mutation-testing.md`~~: **REMOVED.** Intentionally breaking production code conflicts with `atomic_checkpoint_mandate` (no safe revert protocol exists), `explicit_scope_write` (modifications must be purposeful), and risks leaving the workspace in a dirty state. DEFER until a safe mutation sandbox protocol is designed.

### Phase 3: AI Testing Standards Knowledge Item (Reference Document)
**CORRECTED (Red-Team):** Instead of creating a competing rule file (`06-ai-testing-standards.md`) that would duplicate existing mandates, create a **Knowledge Item** (KI) that consolidates testing best practices as reference documentation.

- **Create KI:** `ki_ai_testing_standards.md` in `<appDataDir>/knowledge/ai_testing_standards/artifacts/`
- **Contents (Reference, NOT Rules):**
  - **Mock Infrastructure Map:** Quorum's mock infrastructure consists of `@[c:\src\quorum\backend_v2\llm\mock.py]` (MockLLMService), `@[c:\src\quorum\backend_v2\llm\mock_data.py]` (typed mock data store), and `MockProvider` in `@[c:\src\quorum\backend_v2\llm\provider.py#L840-L1000]`. The `@[c:\src\quorum\backend_v2\llm\adapters\mock_adapter.py]` contains `MockCacheAdapter` for cache-specific testing only.
  - **Non-Deterministic Data Testing:** Never use exact string matching for LLM outputs. Test the structural response (Pydantic `.model_validate()`) or use semantic keyword assertions.
  - **UI Visual Testing (Flutter):** Reference the E2E SDUI Parity Architecture KI for contract testing methodology.
  - **XAI Audit Trail Testing:** Validate that `quote_evidence` and source references pass `str.find()` exact forensic matching (per `strict_physical_anchoring_mandate`).

### Phase 4: SSOT Quality Gate Mutator (Core Rule Enhancement)
**CRITICAL ARCHITECTURAL CORRECTION:** The original proposal to inject raw Markdown `### QUALITY GATE` blocks directly into workflows like `tier5-session-handover.md` violates the Single Source of Truth (SSOT) principle. `00-antigravity-core.md` already contains a `<universal_quality_gate>` block.
Instead of duplicating text across workflows, this Epic will:
1. **Mutate `@[c:\src\quorum\.agents\rules\00-antigravity-core.md]`:** Add a new `anti_happy_path_mandate` rule block inside the `<universal_quality_gate>` enforcing that edge cases and negative scenarios must be tested, and coverage must not decrease.
2. **Update Workflows:** Ensure workflows like **@[c:\src\quorum\.agents\workflows\tier5-session-handover.md]** and **@[c:\src\quorum\.agents\workflows\tier6-execution-monitor.md]** use a strict routing mandate (e.g., "You MUST enforce ALL rule blocks in the `<universal_quality_gate>` section of `00-antigravity-core.md`") rather than duplicating the physical checklist.

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
- `anti_happy_path_mandate` rule block is present in `<universal_quality_gate>` of `@[c:\src\quorum\.agents\rules\00-antigravity-core.md]`.
- Compliance routing instructions are present in `@[c:\src\quorum\.agents\workflows\tier0-create-plan.md]`, `@[c:\src\quorum\.agents\workflows\tier1-planner.md]`, and `@[c:\src\quorum\.agents\workflows\tier2-execute.md]`.
- New `@[c:\src\quorum\.agents\workflows\tier8-test-coverage-expansion.md]` workflow is created and registered in `AGENTS.md` workflow routing.
- Knowledge Item `ki_ai_testing_standards.md` is created with accurate mock infrastructure paths.
- NO new rule files (`06-*.md`) are created — testing rules remain consolidated in `00-antigravity-core.md`.

### Automated Verification
- **Code Audits:** While editing rule files does not directly trigger `pytest`, all AI-generated code moving forward MUST pass the `backend_audit_loop.py` or `flutter_audit_loop.py` quality gates enforced by the updated workflows.
- **SSOT Integrity Check:** `grep_search` for `tdd_mandate` must return results ONLY from `00-antigravity-core.md` — zero duplication in workflow files.

### Manual Verification
- Execute a test run using `/tier2-execute` to implement a dummy feature and observe whether the agent intrinsically forces the creation of a failing test before writing domain code, AND produces at least 2 negative test cases per feature.
