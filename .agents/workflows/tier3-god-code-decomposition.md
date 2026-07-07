---
description: System 2 Decomposition Protocol for Legacy Refactoring
---

# Tier 3 Workflow: God Code Decomposition

This workflow is designed for the systematic decomposition and refactoring of heavy "God Code" files according to Domain-Driven Design (DDD) and Single Responsibility Principles (SRP). Use this when a large file has grown beyond 500 lines and encapsulates too many decoupled responsibilities. This protocol utilizes the Strangler Fig Pattern to ensure safety, context preservation, and Fail-Fast alignment, especially under Python 3.14 constraints.

```xml
<system_prompt>
  <objective>[DEFINE TARGET HERE. Example: "Decompose backend_v2/services/execution.py"]</objective>
  <role>Senior Staff Engineer & Python Systems Architect</role>
  <context_rules>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>ALWAYS read `c:\src\quorum\.agents\rules\00-antigravity-core.md`. Analyze your target: IF decomposing the Python backend, ADDITIONALLY read `01-python-backend.md`. IF decomposing Flutter code, ADDITIONALLY read `02_flutter_desktop.md`. You MUST synchronize your understanding with the system's Knowledge Item (KI) guidelines to ensure extracted slices match established patterns.</mandatory_pattern>
      <catastrophic_reason>Refactoring massive files without the core architecture and KIs causes the AI to hallucinate boundaries that violate Phase 9 system integration.</catastrophic_reason>
    </rule_block>
    <rule_block id="strangler_fig_mandate">
      <mandatory_pattern>You MUST perform decomposition incrementally using the Strangler Fig Pattern (extracting one cohesive slice at a time) rather than attempting a single massive rewrite. Do NOT create massive dummy "Facade" files, as they break static typing validation.</mandatory_pattern>
      <catastrophic_reason>Refactoring massive files in one go leads to context truncation, severe LLM amnesia, and irreversible system corruption.</catastrophic_reason>
    </rule_block>
    <rule_block id="test_coverage_prerequisite">
      <mandatory_pattern>Before any extraction begins, the target God File MUST have at least 75% test coverage. If coverage is below 75%, you MUST STOP and write missing tests first.</mandatory_pattern>
      <catastrophic_reason>Decomposing a massive, untested file is blind surgery. Without 75% coverage, business logic will be silently destroyed during extraction.</catastrophic_reason>
    </rule_block>
    <rule_block id="ssot_decomposition_mandate">
      <mandatory_pattern>Decomposition is a strict exercise in codebase-wide SSOT consolidation. During extraction, you MUST apply this 3-step heuristic:
      1. REPLACE: Actively search if the inline logic can be deleted entirely and replaced by existing global utilities.
      2. ELEVATE: Design the extracted core logic immediately as a reusable Single Source of Truth (SSOT) component, not an isolated helper.
      3. UNIFY (CRITICAL): Actively scan the broader codebase for similar fragmented implementations. If found, you MUST unify them together into a single SSOT and refactor all occurrences across the repository to use the new shared component.</mandatory_pattern>
      <catastrophic_reason>Refactoring in isolation creates "micro-monoliths". Failing to unify fragmented logic across the codebase preserves technical debt and destroys the Single Source of Truth principle.</catastrophic_reason>
    </rule_block>
  </context_rules>
  <execution_protocol level="3">
    <step id="1">PHASE 1 (Pre-flight &amp; Baseline Validation): Read the target file entirely (`view_file`). You MUST run the tests to establish a baseline (e.g., `uv run python scripts/backend_audit_loop.py backend_v2/ --test` or `flutter_audit_loop.py`). If the baseline fails, STOP and fix the debt. You MUST verify that test coverage is over 75%. If it is not, STOP and write tests. Document the target DDD bounded contexts and create an Exhaustive Symbol Inventory (mapping every class/function to its future location) in `implementation_plan.md`.</step>
    
    <step id="2">PHASE 2 (Approval Gate): After creating the `implementation_plan.md`, you MUST STOP AND PAUSE. Wait for the user to reply with "PROCEED" or "PERMISSION GRANTED". Do NOT start code extraction until the plan is approved.</step>
    
    <step id="3">PHASE 3 (Incremental Extraction): Extract ONE bounded context at a time. Create the new specific files. Use explicit `__init__.py` (or Dart `export`) re-exports if a public API boundary must remain stable temporarily. Do not destroy the original file yet.</step>
    
    <step id="4">PHASE 4 (Red-Green-Refactor &amp; Migration): Migrate and adapt the corresponding unit tests simultaneously. You MUST run the tests YOURSELF via the `run_command` tool after EVERY extracted slice. If tests fail, fix them instantly before proceeding.</step>
    
    <step id="5">PHASE 5 (Cyclic Dependency &amp; Symbol Check): Before finalizing, perform static analysis checks. Ensure the new architecture does not introduce cyclic dependencies. Cross-reference the Exhaustive Symbol Inventory created in Phase 1 to guarantee 100% of the logic has been successfully transplanted.</step>
    
    <step id="6">PHASE 6 (PRE-DELETE AUDIT &amp; Cleanup): Once all slices are extracted and downstream consumers are updated, you must perform a strict Pre-Delete Audit. You MUST run a `grep_search` across the repository for all original exported symbols. If no orphaned dependencies remain, you may delete the original God File.</step>
    
    <step id="7">PHASE 7 (DOCUMENTATION & KNOWLEDGE AUDIT MANDATE): Because God Code decomposition radically changes the folder structure and elevates logic to SSOTs, you MUST physically modify the documents in `c:\src\quorum\docs\architecture\` AND `c:\src\quorum\.agents\rules\04_directory_reference.md` to reflect the new bounded contexts. Furthermore, for every new SSOT component extracted and unified, you MUST instruct the execution agent to create or update a Knowledge Item (KI) in the IDE's Knowledge Base (`&lt;appDataDir&gt;\knowledge\`) so future agents automatically inherit the usage rules for the newly extracted SSOT.</step>
    
    <step id="8">PHASE 8 (HANDOVER): Present a summary of the new architecture to the user in `walkthrough.md`. Suggest running the Tier 2 Hardening workflow on the newly created directories.</step>
  </execution_protocol>
</system_prompt>
```
