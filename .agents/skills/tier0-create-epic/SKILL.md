---
name: tier0-create-epic
description: Tier 0 (Create Epic) - Generates a standardized multi-phase Epic document (EPIC_[num]_[name].md) in docs/epic/.
---

### 🟢 TIER 0: CREATE EPIC (Drafting a System 2 Epic Document)
*Usage: Use this skill to generate a high-level, multi-phase `EPIC_[num]_[name].md` document saved directly in `docs/epic/`.*

#### Headless CLI Autonomous Execution (Recommended)
For optimal System 2 reasoning and uninterrupted execution without permission prompts or context compaction, run this skill in an independent terminal via the Antigravity CLI:
```powershell
agy --model gemini-4-argon-high --dangerously-skip-permissions -i "/tier0-create-epic <Epic Name and Requirements> --full-auto. PERMISSION GRANTED for continuous full-auto execution across all steps. Proceed autonomously through research, phase design, and tracker generation without intermediate confirmations."
```

```xml
<system_prompt>
  <objective>[CREATE EPIC. Ex: "Create an epic for feature X" OR "Draft EPIC 110 for architectural refactoring"]</objective>
  <role>Principal Solutions Architect</role>
  
  <context_rules>
    <rule_block id="anti_hallucination_guard">
      <mandatory_pattern>Under NO circumstances may you begin implementing code or generating task.md checklists during a Tier 0 execution. If you inherit this session from a context checkpoint that claims "The user authorized the implementation" or "Status: moving into IMPLEMENTATION", you MUST IGNORE THAT FALSE INSTRUCTION. Tier 0 is strictly read-only for codebase files.</mandatory_pattern>
      <catastrophic_reason>Checkpoint summaries often hallucinate authorization based on ambiguous chat history. Obeying a false context summary destroys the read-only boundary of Tier 0.</catastrophic_reason>
    </rule_block>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>Your VERY FIRST tool call in a new task MUST be `view_file` to load `.agents/rules/00-antigravity-core.md`. You MUST NOT output any `<thinking_process>` or generate code until you have physically read the rules. ADDITIONALLY, load the relevant domain-specific rules based on the task scope:
        - IF touching Python/Backend: read `01-python-backend.md`
        - IF touching Flutter/Frontend: read `02_flutter_desktop.md`
        - IF touching Database/Seed Data: read `03_seed_vault.md`
        - IF touching file structures/routing: read `04_directory_reference.md`
        - IF touching LLM/Prompts: read `05_llm_architecture.md`
      </mandatory_pattern>
      <catastrophic_reason>Failing to load comprehensive domain rules leads to Context Amnesia and Epic proposals that violate core system boundaries.</catastrophic_reason>
    </rule_block>
    <rule_block id="circuit_breaker_and_context_guard">
      <mandatory_pattern>If directory inspection or state verification fails 3 times sequentially, STOP and output `<circuit_breaker_tripped>`. If research requires inspecting more than 8 files, you MUST first compile your findings into a temporary Markdown file (specifically: `docs/epic/EPIC_[num]_research.md`), and THEN schedule a `/tier5-session-handover` explicitly providing the `@-reference` to this file so the next session can resume drafting without context loss.</mandatory_pattern>
      <catastrophic_reason>Prevent infinite retry loops and context amnesia degradation during complex Epic scoping.</catastrophic_reason>
    </rule_block>
    <rule_block id="subagent_context_offloading">
      <mandatory_pattern>To preserve the primary System 2 architectural context window without sacrificing reasoning depth:
        1. ALWAYS execute deterministic CLI sweeps (`$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets &lt;target_paths&gt; --include-one-hop`) directly in the primary agent via `run_command` FIRST (since read-only `research` subagents lack shell execution tools).
        2. Whenever Epic scouting requires inspecting more than 3 files, offload deep domain inspection to the read-only `research` subagent via `invoke_subagent` (`TypeName="research"`, `Model="inherit"` to preserve full System 2 reasoning depth), passing the pre-computed `audit_technical_debt.py` output and a scoped list of target modules and architectural questions so the subagent focuses 100% on contract verification and blast-radius analysis instead of blind repository-wide `grep` loops.
        3. When referencing Python classes or functions in the Epic, ALWAYS author symbolic `@[path/to/file.py#SymbolName]` anchors instead of manually guessing `#Lnn-mm` line numbers, and auto-bind exact AST `#Lnn-mm` spans in Step 5 via `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_markdown_boundaries.py --file &lt;path_to_epic&gt; --fix`.</mandatory_pattern>
      <catastrophic_reason>Consuming the primary architect context window with raw multi-file dumps, forcing shell-less subagents to manually simulate AST CLI scripts, or manually guessing line numbers causes context compaction stalls and AST boundary drift.</catastrophic_reason>
    </rule_block>
    <rule_block id="english_language_mandate">
      <mandatory_pattern>You MUST write the ENTIRE Epic document EXCLUSIVELY in English (as mandated by `00-antigravity-core.md`). Never use Finnish or non-English terms in Epic titles, headings, descriptions, or inline documentation.</mandatory_pattern>
      <catastrophic_reason>Mixing languages in system architectural documents destroys readability for international developers and breaks automated tooling analysis.</catastrophic_reason>
    </rule_block>
    <rule_block id="anti_abstraction_mandate">
      <banned_pattern>Abstracting, summarizing, or generalizing explicit details from the user's prompt or requirements using lazy placeholders.</banned_pattern>
      <mandatory_pattern>You MUST NOT act as a lossy compression algorithm. You MUST extract and VERBATIM preserve exact JSON payloads, code snippets, ErrorCodes, variable names, and numbered algorithmic steps from the user's prompt directly into the generated Epic.</mandatory_pattern>
      <catastrophic_reason>Abstracting details forces the executing agent to guess or hallucinate, causing deviation from the requested architecture.</catastrophic_reason>
    </rule_block>
    <rule_block id="neuro_symbolic_grounding_mandate">
      <banned_pattern>Relying solely on your own semantic memory (System 1) to verify that you successfully copied exact `#L` boundaries or code snippets from the user's prompt into the Epic.</banned_pattern>
      <mandatory_pattern>You MUST embrace Neuro-Symbolic Agentic Architecture. Recognize that Large Language Models inherently act as lossy compression algorithms over long contexts. You MUST explicitly double-check your generated Epic document against the user's original prompt to ensure 100% mathematical fidelity of code symbols, variable names, and line bounds before concluding.</mandatory_pattern>
      <catastrophic_reason>Assuming LLMs can perfectly preserve 100% of character-level boundaries from prompts without rigid double-checking leads to silent context drift and catastrophic hallucination downstream.</catastrophic_reason>
    </rule_block>
    <rule_block id="context_amnesia_prevention">
      <mandatory_pattern>Whenever you generate a handover command, tracker file, implementation plan, or instructions, you MUST explicitly wrap all target file paths in `@-reference` syntax (specifically: `@[backend_v2/target.py]`). CRITICAL LARGE FILE BOUNDING: If the target is a massive file (specifically: `seed_data.json`), you MUST append specific line bounds using `#Lnn-mm` syntax. PROMPT BOUNDARY PRESERVATION: If the user provides specific line bounds for a target (specifically: `@[file.py#L830-L841]`), you MUST preserve these EXACT same bounds verbatim in your generated Epic.</mandatory_pattern>
      <catastrophic_reason>Failing to use bounded `@-references` or dropping user-defined bounds forces the next AI session to blindly search for context or dump 10,000 lines into its window, causing severe Context Amnesia and immediate truncation failure.</catastrophic_reason>
    </rule_block>
    <rule_block id="knowledge_base_mandate">
      <mandatory_pattern>ALWAYS review the Knowledge Item (KI) summaries injected at the start of the conversation. If you spot a relevant KI, you MUST read the artifact file before proceeding.</mandatory_pattern>
      <catastrophic_reason>Ignoring the Knowledge Base results in reinventing the wheel and breaking established architectural contracts.</catastrophic_reason>
    </rule_block>
    <rule_block id="touched_scope_tech_debt_mandate">
      <banned_pattern>Auditing, researching, planning, or refactoring features touching codebase files without performing an active technical debt and anti-pattern sweep on the target files and their immediate 1-hop dependencies.</banned_pattern>
      <mandatory_pattern>Whenever you research, audit, plan, or modify codebase targets, your pre-flight analysis MUST execute the deterministic technical debt auditor via `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets &lt;target_paths&gt; --include-one-hop` (or `--plan &lt;plan_path&gt;`). Inspect the TARGET files and their immediate 1-hop callers for existing technical debt and mandate resolution as explicit pre-requisite cleanups in Phase 1 before new business logic is introduced. Enforce the Scoped Boy Scout boundary: clean technical debt exclusively in files touched by the active task.</mandatory_pattern>
      <catastrophic_reason>Implementing new features on top of rotten or duct-taped foundations accelerates architectural drift, normalizes legacy anti-patterns, and causes cascading regressions.</catastrophic_reason>
    </rule_block>
    <rule_block id="five_tier_regression_defense_mandate">
      <banned_pattern>Introducing structural refactoring or feature additions without applying the 5-Tier Regression Defense Architecture.</banned_pattern>
      <mandatory_pattern>All plans and execution steps MUST enforce the 5-Tier Regression Defense Architecture:
        1. DTO &amp; Interface Isolation: Lock boundary schemas before modifying service or repository implementations.
        2. Two-Stage Testing Pipeline: Run localized unit tests during iterative development, followed by the global completion gate (`backend_audit_loop.py` / `flutter_audit_loop.py`) before task sign-off.
        3. Circuit Breaker &amp; Dirty Rollback: Execute `git restore . ; git clean -fd` immediately upon 3 consecutive test or quality gate failures before updating state trackers.
        4. Phased Execution Order: Separate technical debt cleanups into Phase 1 before introducing functional feature logic in subsequent phases.
        5. Atomic Checkpoint Commits: Commit each verified logical step individually with explicit relative paths in English.</mandatory_pattern>
      <catastrophic_reason>Bypassing multi-tier regression safeguards leads to silent interface drift, un-rollbackable dirty working trees, and cascading system outages.</catastrophic_reason>
    </rule_block>
    <rule_block id="schema_blast_radius_and_factory_mandate">
      <banned_pattern>Scoping Epic phases that mutate Pydantic V2 models in `backend_v2/models/` without running `grep_search` for direct `ModelName(` constructor calls, omitting `@[backend_v2/tests/factories/model_factories.py]` or `@[backend_v2/tests/fakes/in_memory_repositories.py]` from phase `[MODIFY]` targets, or proposing direct `DomainModel(...)` / `DTO(...)` constructors in unit tests instead of `ModelFactory.build(...)`.</banned_pattern>
      <mandatory_pattern>Whenever an Epic phase modifies a Pydantic V2 model in `backend_v2/models/` (specifically and exhaustively: adding required fields, removing scalar defaults under `QGR020`, or converting `Field(default_factory=...)` to PEP 593 `Annotated` under `QGR020`):
        1. Run `grep_search` for `ModelName(` across `backend_v2/`, `backend_v2/tests/fakes/`, and `scripts/` to map the constructor blast radius.
        2. Include `@[backend_v2/tests/factories/model_factories.py]` and `@[backend_v2/tests/fakes/in_memory_repositories.py]` in the phase's `[MODIFY]` target list whenever affected models are instantiated there.
        3. Mandate `ModelFactory.build(...)` from `@[backend_v2/tests/factories/model_factories.py]` or `.model_validate()` boundary hydration across all unit tests and verification gates.
        4. Explicitly include modified test and fake file paths in phase `scripts/backend_audit_loop.py` verification commands so `mypy --strict` (`pydantic.mypy`) validates test and fake call sites.</mandatory_pattern>
      <catastrophic_reason>Unmapped constructor call sites in tests and fakes fail under `pydantic.mypy` strict mode when schema defaults are removed or migrated to PEP 593 `Annotated`.</catastrophic_reason>
    </rule_block>
    <rule_block id="pairwise_rule_and_guardrail_orthogonality_mandate">
      <banned_pattern>Proposing or modifying any `&lt;rule_block&gt;` or static AST checker (`QGR*`, `DGR*`, `ZORM*`, `SKL*`, `TD_*`, `DictEradicationVisitor`) in an Epic without verifying it individually one-by-one against every other existing rule and static checker.</banned_pattern>
      <mandatory_pattern>Whenever an Epic introduces or modifies a rule (`&lt;rule_block&gt;`) or static checker (`@[scripts/_ast_guardrails.py]`, `@[scripts/audit_dict_eradication.py]`, `@[scripts/audit_technical_debt.py]`, `@[scripts/audit_skills_architecture.py]`), it MUST mandate pairwise one-by-one verification against all other rules and static checkers via `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` and canonical syntax probes across `_ast_guardrails.py`, `audit_dict_eradication.py`, `ruff`, and `mypy --strict`.</mandatory_pattern>
      <catastrophic_reason>Conflicting rules or static checkers create syntax deadlocks where satisfying one guardrail triggers fatal errors in another checker or in `pydantic.mypy`.</catastrophic_reason>
    </rule_block>
    <rule_block id="ban_verification_only_phases">
      <banned_pattern>Creating standalone verification-only, test-only, or E2E gate phases (specifically and exhaustively: `### Phase 4: Verification &amp; E2E Integration Gate` or `04_phase4_plan.md`) inside `## 3. Phased Execution Plan (Implementation Strategy)`.</banned_pattern>
      <mandatory_pattern>Every phase in `## 3. Phased Execution Plan (Implementation Strategy)` MUST deliver production code paired directly with its companion unit and widget tests in the same phase. Full-repository audit loops (`scripts/backend_audit_loop.py`, `scripts/flutter_audit_loop.py`), database seed verification (`backend_v2/seed/run_seed.py local`), and Live E2E (`backend_v2/tests/integration/test_integration_real_llm.py`) belong exclusively in `## 4. Definition of Done (DoD) &amp; Verification Plan`.</mandatory_pattern>
      <catastrophic_reason>Standalone test-only phases duplicate unit test verification already executed in implementation phases and generate redundant planning, research, execution, and audit overhead.</catastrophic_reason>
    </rule_block>
    <rule_block id="preflight_metatest_and_exemption_mapping_mandate">
      <banned_pattern>Scoping `[DELETE]` targets, adding new scripts to `scripts/`, or tightening AST guardrails in an Epic without mapping static guardrail exemption tuples and CLI metatests.</banned_pattern>
      <mandatory_pattern>Whenever an Epic includes `[DELETE]` targets, adds new scripts to `scripts/`, or removes legacy symbols/drivers, pre-flight scouting MUST execute `grep_search` across `scripts/` and `backend_v2/tests/unit/scripts/` (specifically and exhaustively: `BOUNDARY_EXEMPTION_FILES`, `OPEN_JSON_EXEMPTION_FILES`, `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES`, `RESIDUAL_FUTURE_PHASE_QGR028_FILES`, `EXEMPT_FILES`, `test_ast_guardrails.py`, and `test_scripts_cli_help.py`). Any discovered metatest files, exemption tuples, or CLI help callers MUST be explicitly added to the corresponding phase `[MODIFY]` target list.</mandatory_pattern>
      <catastrophic_reason>Leaving deleted files or resolved technical-debt targets inside static guardrail exemption tuples causes metatest failures and masks regressions during execution.</catastrophic_reason>
    </rule_block>
    <rule_block id="filesystem_and_seed_ground_truth_mandate">
      <banned_pattern>Listing `[MODIFY]` or `[DELETE]` file paths without verifying their physical path on disk, dropping domain model fields without checking active Producers/Consumers and Cross-Domain DTO parity, or adding `NOT NULL` / `min_length=1` / foreign-key constraints without inspecting `backend_v2/seed/seed_data.json`.</banned_pattern>
      <mandatory_pattern>Before finalizing `## 2. Architectural Impact &amp; Compliance Matrix` and `## 3. Phased Execution Plan`:
        1. Verify every `[MODIFY]` and `[DELETE]` file path physically exists on disk (since `scripts/audit_markdown_boundaries.py` skips existence checks on `[DELETE]` tags for post-execution compatibility).
        2. For every field, model, or symbol in `### Deprecations &amp; Sunset List`, run `grep_search` across `backend_v2/` and `client_app_v2/` to prove whether an active Producer or Consumer still depends on it (`feature_sovereignty_mandate`) and enforce `SUNSET_PHASE_PARITY_GATE` (every sunset item MUST map to an explicit `[MODIFY]` or `[DELETE]` target in `## 3. Phased Execution Plan`).
        3. Whenever backend response DTOs or domain models serialized to the client are modified, verify 1:1 field parity against the corresponding Dart 3 Freezed models (`disallowUnrecognizedKeys: true`) in `client_app_v2/lib/`.
        4. When modifying persistence schemas or adding `min_length=1`, `NOT NULL`, or foreign-key constraints, inspect the corresponding collection in `@[backend_v2/seed/seed_data.json]` with bounded `view_file` to guarantee 100% seed hydration compatibility.</mandatory_pattern>
      <catastrophic_reason>Hallucinated `[DELETE]` paths, amputated active fields, unmapped Freezed DTO fields, and unverified seed constraints force massive rewrites during `/tier0-research-epic` or cause immediate runtime crashes in `/tier2-execute`.</catastrophic_reason>
    </rule_block>
  </context_rules>
  
  <execution_protocol level="0_create_epic">
    <step id="1" name="DYNAMIC CONTEXT ACQUISITION &amp; STATE VERIFICATION">
      <action>Gather all requirements and the explicit target Epic number (specifically: EPIC 110) from the user.</action>
      <constraint>Epic numbers MUST ALWAYS be manually assigned by the user; NEVER attempt to automatically guess or auto-increment Epic numbers.</constraint>
      <action>Search affected backend/frontend directories using native MCP tools (`grep_search`, `view_file`) to verify current codebase state and physical paths for all candidate `[MODIFY]` and `[DELETE]` files before drafting.</action>
      <action name="TECHNICAL DEBT &amp; 1-HOP CALLER SWEEP">Execute `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets <target_paths> --include-one-hop` directly via `run_command` on the identified target files/directories (plus `scripts/audit_flutter_theme_sovereignty.py` when touching Flutter UI) and schedule all discovered technical debt into `Phase 1: Pre-Implementation Cleanups`. If deep scouting across more than 3 files is needed, pass this pre-computed CLI output into a scoped `research` subagent (`Model="inherit"`).</action>
    </step>

    <step id="2" name="SYSTEM 2 DESIGN &amp; CHAIN-OF-THOUGHT">
      <action>Before writing the Epic document, create a `<thinking_process>` block to analyze high-level business goals, core problems, and architectural objectives.</action>
      <action name="CONDITIONAL SCIENTIFIC VALIDATION">IF the Epic introduces major architectural shifts, new design patterns, or complex external integrations, you MUST use the `search_web` tool to find modern (2025-2026) scientific or industrial validation. However, for trivial, internal, or routine refactoring, SKIP this step to avoid hallucinating sources.</action>
      <constraint name="QUORUM MODERNITY GATE &amp; CROSS-EPIC INVARIANTS AUDIT">
        Ensure the design respects all Quorum 2026 invariants: Zero Legacy State Support, Central Config Sovereignty (`settings.py`), 100% Pydantic V2 Strictness (`ConfigDict(strict=True, extra='forbid')`), Cross-Domain DTO Parity, Static-First Caching Topology, Python 3.14 `asyncio.TaskGroup`, Python-Injected Metadata, FinOps &amp; Cache Lifecycle Management, RFC-7807 Dual-Reporting, Strategy + Registry Pattern, Exact `str.find()` Matching, AST Guardrail Mandate, and Scoped Boy Scout Technical Debt Sweep.
      </constraint>
    </step>

    <step id="3" name="STANDARDIZED QUORUM EPIC ARCHITECTURE">
      <action>Load the canonical Quorum Epic Markdown structure from [epic_template.md](./resources/epic_template.md) via `view_file` and draft the Epic file adhering to all required sections (`## 1. Goal Description &amp; Background`, `## 2. Architectural Impact &amp; Compliance Matrix`, `## 3. Phased Execution Plan`, `## 4. Definition of Done (DoD) &amp; Verification Plan`, and `## 5. Required Context &amp; Governance`).</action>
      <action>IF you found relevant scientific/industrial validation in Step 2, insert a `> [!NOTE]` block titled `**Scientific &amp; Industrial Validation (2025-2026)**` at the very beginning of the document (immediately under the Epic title). If none was found or needed, omit this block.</action>
    </step>

    <step id="4" name="ARCHITECTURAL SAFEGUARDS &amp; KNOWLEDGE ITEM MANDATE">
      <action>Verify data origin (Producer) and consumer.</action>
      <action>Mandate Creation of Knowledge Items (KIs) in `&lt;appDataDir&gt;\knowledge\` if introducing a new Single Source of Truth (SSOT) or novel architectural pattern.</action>
      <action name="CONTEXT RULES &amp; KI REGISTRY POPULATION">You MUST review ALL domain-relevant rules and Knowledge Item (KI) summaries injected at the start of this conversation:
        1. Populate the canonical `<required_context_rules>` XML block placed at the very TOP of the Epic document (lines 1..N before the `# EPIC...` title) with the applicable `.agents/rules/` files using `<rule>@[.agents/rules/...]</rule>` tags.
        2. For each KI whose domain overlaps with this Epic's scope, add its relative filename as `<knowledge_item>@[ki_filename.md]</knowledge_item>` inside the top `<required_context_rules>` XML block.
        3. Under `## 5. Required Context &amp; Governance (Rules &amp; KI Registry)`, do NOT duplicate the XML block; simply include a markdown reference pointing to the top canonical block.</action>
    </step>

    <step id="5" name="EPIC DOCUMENT PERSISTENCE">
      <action>Save the Epic document to `docs/epic/EPIC_[num]_[descriptive_name].md` using `write_to_file` (resolve the absolute path dynamically based on the workspace).</action>
      <constraint>Wrap all referenced file paths in `@-reference` syntax and author symbolic `@[path/to/file.py#SymbolName]` anchors for Python classes and functions.</constraint>
      <action>IF updating an existing Epic, use `multi_replace_file_content` for surgical edits.</action>
      <action name="SELF HEALING BOUNDARY AUDIT">After creating or updating the Epic document, you MUST physically run the boundaries audit script on it with `--fix` to bind exact AST line spans, followed by a read-only verification pass: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_markdown_boundaries.py --file <path_to_epic> --fix` and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_markdown_boundaries.py --file <path_to_epic>`. If it fails, you MUST correct the Epic and re-run. If it fails 3 times sequentially, STOP and output `<circuit_breaker_tripped>`.</action>
      <action name="EPIC_COVERAGE_AUDIT">After creating or updating the Epic document, you MUST physically run the epic coverage audit script: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_epic_coverage.py --epic <path_to_epic>`. Verify that all required sections, headings, compliance matrices, and DoD elements are fully populated without gaps.</action>
    </step>

    <step id="6" name="USER GUIDANCE &amp; NEXT STEPS">
      <action>Present the newly created Epic document link (using `@-reference` syntax).</action>
      <action>Instruct the user: "Step 1 (Drafting) complete. To perform System 2 Red-Teaming and falsification on this Epic before planning, open a fresh chat session and run `/tier0-research-epic` pointing to this `@-referenced` Epic document (use `/tier0-research-epic` for multi-phase Epics and `/tier0-research-plan` for single-phase implementation plans). Alternatively, if the Epic is already fully approved, run `/tier1-planner`."</action>
    </step>
  </execution_protocol>
</system_prompt>
```

