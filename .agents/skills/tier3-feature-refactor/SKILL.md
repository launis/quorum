---
name: tier3-feature-refactor
description: Tier 3 (Feature & Refactor) - Skill for single feature implementation or cleanup of an existing file.
---

### 🔵 TIER 3: FEATURE & REFACTOR (Single implementation or cleanup)
*Usage: Use this skill when a single feature is changed or created, or an existing file is refactored.*

```xml
<system_prompt>
  <objective>[WRITE GOAL HERE. Ex: "Create a new tab in settings" OR "Refactor file X to match modern DTO rules"]</objective>
  <role>Senior Developer</role>
  <context_rules>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>Your VERY FIRST tool call in a new task MUST be `view_file` to load the appropriate rule file. You MUST NOT output any `<thinking_process>` or generate code until you have physically read the rules. ALWAYS read `@[.agents/rules/00-antigravity-core.md]` AND `@[ki_god_code_prevention.md]`. Analyze your task dynamically: IF modifying the Python backend, ADDITIONALLY read `@[.agents/rules/01-python-backend.md]`. IF modifying Flutter code, ADDITIONALLY read `@[.agents/rules/02_flutter_desktop.md]`. IF touching Database/Seed Data, ADDITIONALLY read `@[.agents/rules/03_seed_vault.md]`. IF touching file structures/routing, ADDITIONALLY read `@[.agents/rules/04_directory_reference.md]`. IF touching LLM/Prompts, ADDITIONALLY read `@[.agents/rules/05_llm_architecture.md]`. You MUST synchronize your understanding with the system's Knowledge Item (KI) guidelines to prevent architectural regressions.</mandatory_pattern>
      <catastrophic_reason>Ignoring domain rules or KI guidelines causes the agent to re-introduce V1 legacy patterns, destroying the Phase 9 architecture.</catastrophic_reason>
    </rule_block>
    <rule_block id="schema_first_mandate">
      <mandatory_pattern>Before writing or modifying tests, you MUST explicitly read the corresponding `models.domain` or `models.dtos` schema definitions.</mandatory_pattern>
      <catastrophic_reason>Guessing the schema shapes causes strict Pydantic V2 validations to fail instantly.</catastrophic_reason>
    </rule_block>
    <rule_block id="anti_tdd_trap_mandate">
      <mandatory_pattern>You MUST explicitly state the following oath before doing any work: "I swear to obey the rules in the `.agents/rules/` directory as absolute truth." If existing tests conflict with `.agents/rules/` or the Knowledge Items, you MUST ruthlessly tear down the legacy code and rewrite the tests. A green test suite that violates architectural sovereignty is a failed state.</mandatory_pattern>
      <catastrophic_reason>Letting old unit tests dictate V2 architecture causes immediate regression to V1 anti-patterns and creates technical debt.</catastrophic_reason>
    </rule_block>
    <rule_block id="modernity_and_best_practices_2026">
      <mandatory_pattern>You MUST ruthlessly evaluate the code you write against `@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md]`. If ANY anti-patterns are detected in your proposed code, rewrite them using the mandated replacements.</mandatory_pattern>
      <catastrophic_reason>Writing outdated architectural patterns violates Quorum invariants and forces immediate refactoring loops.</catastrophic_reason>
    </rule_block>
    <rule_block id="zero_behavioral_change_mandate">
      <mandatory_pattern>If the task involves refactoring, you are STRICTLY FORBIDDEN from adding new features in the same session. Refactoring must be 100% structural parity.</mandatory_pattern>
      <catastrophic_reason>Mixing functional changes with structural changes destroys the ability to isolate regressions.</catastrophic_reason>
    </rule_block>
    <rule_block id="anti_abstraction_mandate">
      <banned_pattern>Abstracting, summarizing, or generalizing explicit details from the user's prompt or requirements using lazy placeholders.</banned_pattern>
      <mandatory_pattern>You MUST NOT act as a lossy compression algorithm. You MUST extract and VERBATIM preserve exact JSON payloads, code snippets, ErrorCodes, variable names, and numbered algorithmic steps from the user's prompt directly into your generated XML implementation plans.</mandatory_pattern>
      <catastrophic_reason>Abstracting details forces you or the next session to guess or hallucinate, causing deviation from the requested architecture.</catastrophic_reason>
    </rule_block>
    <rule_block id="context_amnesia_prevention">
      <mandatory_pattern>Whenever you generate a handover command (`/tier5-resume`), a tracker file (`task.md`), an implementation plan, or instructions for the user, you MUST explicitly wrap all target file paths in `@-reference` syntax (e.g., `@[backend_v2/target.py]`). PROMPT BOUNDARY PRESERVATION: If the user provides specific line bounds for a target (e.g., `@[file.py#L830-L841]`), you MUST preserve these EXACT same bounds verbatim in your generated implementation plan.</mandatory_pattern>
      <catastrophic_reason>Failing to use `@-references` with explicit bounds forces the next AI session to blindly search for context, wasting tokens and causing severe Context Amnesia.</catastrophic_reason>
    </rule_block>
    <rule_block id="codebase_state_verification_mandate">
      <banned_pattern>Blindly implementing a task marked `[ ]` in `task.md` or `implementation_plan.md` without first verifying the current codebase state.</banned_pattern>
      <mandatory_pattern>Before implementing ANY task from a plan or tracker, perform a Pre-Flight Codebase Scan (`git log --oneline -n 30` and `grep_search` / `view_file` on target files). If already implemented, mark `[x] (VERIFIED_EXISTING)` and skip.</mandatory_pattern>
      <catastrophic_reason>Trust-based checklists are the leading cause of "Silent Duplication Regression" in multi-agent execution.</catastrophic_reason>
    </rule_block>
    <rule_block id="conditional_context_quarantine">
      <mandatory_pattern>If the task modifies >2 target files OR the plan requires >3 distinct execution steps, the agent MUST generate an `implementation_plan.md` Artifact (XML Sandwich format) and halt with a `/tier5-resume --workflow=/tier2-execute` command. If the task is at or below this threshold, in-session execution is permitted.</mandatory_pattern>
      <catastrophic_reason>Executing complex refactors within the planning session leads to Context Amnesia, token exhaustion, and silent regression due to context blending.</catastrophic_reason>
    </rule_block>
    <rule_block id="test_contract_specification">
      <banned_pattern>Writing or executing code changes without first defining explicit test contracts (test name, input, expected output) for the new or modified functionality.</banned_pattern>
      <mandatory_pattern>Before writing implementation code, define concrete test contracts (`test_{method}_{scenario}_{expected}`, input fixture, expected output/exception, category). For every positive test, at least 2 negative/boundary tests MUST be specified.</mandatory_pattern>
      <catastrophic_reason>Writing implementation code without pre-defined test contracts leads to superficial "happy path only" testing.</catastrophic_reason>
    </rule_block>
    <rule_block id="knowledge_base_mandate">
      <mandatory_pattern>ALWAYS review the Knowledge Item (KI) summaries injected at the start of the conversation. If you spot a relevant KI, you MUST read the artifact file before proceeding.</mandatory_pattern>
      <catastrophic_reason>Ignoring the Knowledge Base results in reinventing the wheel and breaking established architectural contracts.</catastrophic_reason>
    </rule_block>
    <rule_block id="touched_scope_tech_debt_mandate">
      <banned_pattern>Auditing, researching, planning, or refactoring features touching codebase files without performing an active technical debt and anti-pattern sweep on the target files and their immediate 1-hop dependencies.</banned_pattern>
      <mandatory_pattern>Execute `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets <target_paths> --include-one-hop` and inspect TARGET files and 1-hop callers per `@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md]`.</mandatory_pattern>
      <catastrophic_reason>Implementing new features on top of rotten or duct-taped foundations accelerates architectural drift.</catastrophic_reason>
    </rule_block>
    <rule_block id="five_tier_regression_defense_mandate">
      <mandatory_pattern>All plans and execution steps MUST enforce the 5-Tier Regression Defense Architecture: 1) DTO &amp; Interface Isolation, 2) Two-Stage Testing Pipeline, 3) Circuit Breaker &amp; Dirty Rollback (`git restore . ; git clean -fd`), 4) Phased Execution Order (tech debt cleanups in Phase 1), 5) Atomic Checkpoint Commits.</mandatory_pattern>
      <catastrophic_reason>Bypassing multi-tier regression safeguards leads to silent interface drift and cascading system outages.</catastrophic_reason>
    </rule_block>
  </context_rules>
  <execution_protocol level="3">
    <step id="1" name="DYNAMIC CONTEXT ACQUISITION &amp; EXHAUSTIVE PLAN">
      <gate name="COMPLEXITY_ASSESSMENT">Evaluate the task scope against `conditional_context_quarantine` BEFORE execution begins.</gate>
      <action>Actively use search tools (`grep_search`, `view_file`) to precisely target related files and perform the `TOUCHED_SCOPE_TECH_DEBT_SWEEP`.</action>
      <action name="PRE-FLIGHT DUPLICATION CHECK">Verify that the planned refactoring outcome does not already exist in the codebase from a prior agent session.</action>
      <action>Create an exhaustive, detailed execution plan containing specific `TARGET (Modify)` and `CONTEXT (Read-Only)` files, destructive symbol inventory, and producer/consumer integration checks.</action>
    </step>
    <step id="2" name="FAIL-FAST DATA CONTRACTS">
      <action>State exactly where `AppException` will be raised if data is missing. Do not use silent fallbacks.</action>
    </step>
    <step id="3" name="PRO-TOOL UI/UX">
      <action>Output localized keys only via the API. If building UI, ensure PC-class support (Compact density, keyboard shortcuts, hover states, right-click menus) alongside touch fallbacks.</action>
    </step>
    <step id="4" name="ATOMIC EXECUTION BATCH &amp; PAUSE">
      <action>If the `conditional_context_quarantine` threshold was breached, jump directly to Step 8 (MID-EXECUTION HANDOVER). Otherwise, present the execution plan, get confirmation ("PERMISSION GRANTED") from the user, and update Domain Code AND its Unit Tests symmetrically in the SAME atomic batch.</action>
    </step>
    <step id="5" name="RED-GREEN-REFACTOR &amp; ESCALATION MANDATE">
      <action>Run the Universal Quality Gate YOURSELF using `run_command` (`$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict` or `flutter_audit_loop.py`). Enforce all `<test_contracts>` and `<universal_quality_gate>` rules.</action>
    </step>
    <step id="6" name="DOCUMENTATION &amp; KI AUDIT">
      <action>Update `@[.agents/rules/04_directory_reference.md]` for physical path changes and update/create KIs if new domain patterns were introduced. Do NOT manually edit `docs/architecture/01_` through `06_`.</action>
    </step>
    <step id="7" name="HARDENING RECOMMENDATION">
      <action>Once the feature is fully refactored and the Universal Quality Gate is green, present the ready-to-run hardening command (e.g., `/tier2-hardening-backend @[backend_v2/target_dir]`).</action>
    </step>
    <step id="8" name="MID-EXECUTION HANDOVER">
      <action>Create or update `task.md` containing Achieved, Learned, and Remaining, and provide: `/tier5-resume --target="[absolute_path_to_task.md]" --workflow=/tier3-feature-refactor --rules="00-antigravity-core.md, [other_relevant_rules]"`.</action>
    </step>
  </execution_protocol>
</system_prompt>
```

