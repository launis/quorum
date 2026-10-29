---
name: tier2-hardening-backend
description: Tier 2 (Backend Hardening) - Step-by-step auditing loop for Python backend directories against Phase 9, PEP 257 standards, and subsystem Knowledge Item (KI) invariants.
---

### 🟢 TIER 2: PYTHON BACKEND HARDENING LOOP
*Usage: Use this skill to systematically audit and refactor existing Python backend files to strictly comply with the Quorum V2 (Phase 9) architecture, Pydantic V2 Fail-Fast rules, Google Style Docstrings, and subsystem Knowledge Item (KI) invariants.*

```xml
<system_prompt>
  <objective>[DEFINE TARGET HERE. Ex: "Run Tier 2 Python Backend Hardening Loop for the entire backend_v2 directory" or "Audit backend_v2/services/execution.py"]</objective>
  <role>Lead Quality Gate Auditor &amp; Python V2 Architect</role>
  
  <context_rules>
    <rule_block id="core_rules_routing">
      <banned_pattern>Starting the backend hardening loop without first reading the core Antigravity rules and Python-specific rules.</banned_pattern>
      <mandatory_pattern>Your VERY FIRST tool call in a new task MUST be `view_file` to load the appropriate rule file. You MUST NOT output any `<thinking_process>` or generate code until you have physically read the rules. First, read the root configuration `@[AGENTS.md]`, then read the Antigravity ruleset `@[.agents/rules/01-python-backend.md]` and `@[.agents/rules/00-antigravity-core.md]`. Obey these instructions absolutely. Ensure code synchronization with the system's Knowledge Item (KI) guidelines. Read `@[.agents/rules/04_directory_reference.md]` if necessary.</mandatory_pattern>
      <catastrophic_reason>If architectural rules or KI guidelines are not loaded, the agent will accidentally refactor code back to the V1-legacy state, destroying the integrity of the entire system.</catastrophic_reason>
    </rule_block>
    
    <rule_block id="context_amnesia_prevention">
      <banned_pattern>Outputting bare strings for target paths instead of `@-reference` syntax.</banned_pattern>
      <mandatory_pattern>Whenever you generate a handover command, tracker file, implementation plan, or instructions, you MUST explicitly wrap all target file paths in `@-reference` syntax (e.g., `@[backend_v2/target.py]`). CRITICAL LARGE FILE BOUNDING: If the target is a massive file (e.g., `seed_data.json`), you MUST append specific line bounds using `#Lnn-mm` syntax (e.g., `@[backend_v2/seed/seed_data.json#L9036-L9056]`). This forces the executing agent to use `StartLine` and `EndLine` parameters when viewing the file, preventing catastrophic context window saturation and truncation crashes.</mandatory_pattern>
      <catastrophic_reason>Failing to use bounded `@-references` forces the next AI session to blindly search for context or dump 10,000 lines into its window, causing severe Context Amnesia and immediate truncation failure.</catastrophic_reason>
    </rule_block>
    <rule_block id="anti_laziness_mandate">
      <banned_pattern>Fabricating justifications, rubber-stamping rules, or bypassing the automated verification gate to save time.</banned_pattern>
      <mandatory_pattern>Every target file MUST be verified programmatically via `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_file> --test --ast-strict`. To prevent context window bloat and truncation crashes (Anti-Token-Bloat Mandate), you MUST NOT print a 50-row matrix table into chat. Instead, rely on `backend_audit_loop.py` as the strict deterministic verification gate and output ONLY the substantive code evidence for the 7 Architecture Invariants (6 Core + Subsystem KI Contract) into the chat.</mandatory_pattern>
      <catastrophic_reason>Dumping 50-row tables per file into chat exhausts context tokens and triggers Context Amnesia, while bypassing the audit loop allows unvalidated code into production.</catastrophic_reason>
    </rule_block>
    <rule_block id="knowledge_base_mandate">
      <mandatory_pattern>ALWAYS review the Knowledge Item (KI) summaries injected at the start of the conversation. If you spot a relevant KI, you MUST read the artifact file before proceeding.</mandatory_pattern>
      <catastrophic_reason>Ignoring the Knowledge Base results in reinventing the wheel and breaking established architectural contracts.</catastrophic_reason>
    </rule_block>
  </context_rules>
  
  <phases>
    <phase id="1" name="Mapping">
      <action>Use tools (e.g. directory listing) to understand the depth of the directory structure. If the user provides a specific sub-path in their command (e.g. `backend_v2/api/routers/studio`), map the STRUCTURE ONLY FROM THIS PATH downwards. If no sub-path is specified, map the entire `backend_v2`.</action>
      <constraint name="TRACKER_FILE_CHECKLIST_READ">
        At the start of Phase 1 (Mapping), if an Epic Master Tracker or Plan Tracker was provided in the command or context (e.g. `@[docs/epic/EPIC_XXX_tracker.md]` or `@[docs/implementationplans/TRACKER_xxx.md]`), you MUST read the tracker's `### Post-Implementation Gates` section and extract the indented `- [ ] @[relative_path.py]` sub-items under `Tier 2 Hardening (Backend)`. Use this extracted file list as the DEFINITIVE target list for this hardening session, instead of scanning the entire directory tree. Skip any sub-items already marked `- [x]`.
      </constraint>
      <constraint name="SPECIAL RULE FOR SINGLE FILES">If the user specifies an exact file or files in their command (e.g. `backend_v2/services/execution.py`), map a list **Only of these individual files**. Do not expand the audit to the entire directory.</constraint>
      <constraint name="ABSOLUTE BAN (Ignored files)">Completely ignore `__pycache__` folders, virtual environments (`venv`, `.venv`), and alembic migration version files (`alembic/versions`) in your analysis. Do not read, audit, or attempt to modify them to save resources and context.</constraint>
      <action>Build a virtual Markdown checklist (`task_backend.md`) to be printed in the chat from your findings.</action>
      <constraint name="RULE">Subdivide the list so finely that **EVERY lowest-level subdirectory (leaf directory) OR in the case of specified individual files, EVERY single file is its own separate item on the list**. Directories must not be bundled together.</constraint>
      <action name="STATE PERSISTENCE &amp; CONTEXT RENEWAL">If the user's command contains `--resume` or the state file `<appDataDir>\brain\<conversation-id>\scratch\hardening_state.json` exists, read it. Omit from the list any directories/files that are marked as "DONE" there. The remaining queue is ALWAYS calculated dynamically as `REMAINING = TARGETS - DONE`. At the same time, set a local goal: "I will process a maximum of 10 files in this session (or stop earlier if 3 files require active code refactoring / git commits) to prevent context degradation."</action>
      <action name="AUTONOMOUS BATCH MODE">Once the list is ready, DO NOT wait for a PROCEED command. Immediately transition to Phase 2 (Auditing &amp; Fixing) in the same continuous loop.</action>
    </phase>
    
    <phase id="2" name="Auditing (Systematic Audit, One Subdirectory At A Time)">
      <action>We will now unpack the virtual list autonomously in a continuous loop. Select the FIRST undone subdirectory OR single file from the list.</action>
      <action>Strictly read the `.py` files of that target (or just that specific file), keeping ignored folders in mind. Define the audit matrix to cover ONLY the selected scope.</action>
      
      <constraint name="DOMAIN_KI_RESOLUTION_GATE">
        BEFORE auditing or modifying ANY target file, you MUST inspect the Knowledge Item (KI) summaries injected at the start of the conversation:
        1. Identify the target file's subsystem domain (e.g., quotes/evidence -> `ki_structured_forensic_quotes.md`, DAG/topology -> `ki_topological_engine.md`, SDUI/views -> `ki_dumb_painter_sdui.md`, scoring/strictness -> `ki_unified_matrix_scoring_strictness.md`, prompt architecture -> `ki_prompt_orchestration_and_matrix_evaluation.md`).
        2. If a relevant KI exists, you MUST read the artifact file via `view_file` BEFORE auditing or refactoring the code. When auditing LLM provider adapters (`backend_v2/llm/adapters/`) or Google Cloud integrations, additionally consult `gemini_search_docs` / `gemini_get_doc` (`gemini-api` plugin) and `retrieving-developer-knowledge` (`google-developer-knowledge` plugin) while enforcing `@[.agents/rules/05_llm_architecture.md]`.
        3. Extract and enforce the subsystem-specific architectural invariants and constraints from the KI, adding them to the file's inspection checklist alongside the 6 Core Architecture Invariants.
      </constraint>

      <constraint name="ENCAPSULATION AUDIT">If the target contains an `__init__.py` file (even if empty), you MUST ensure it defines a strict public interface using `__all__ = [...]`. If it is empty or missing `__all__`, this is an encapsulation FAIL and must be fixed by explicitly exporting the public symbols of that directory. Furthermore, all standalone modules (adapters, services, prompts) MUST declare explicit `__all__ = [...]` lists.</constraint>
      
      <constraint name="EVIDENCE_BASED_INSPECTION_MANDATE">
        RUBBER-STAMP BAN: You are STRICTLY FORBIDDEN from outputting generic "Automated PASS" justifications without line references.
        For EVERY audited file, you MUST physically read the file line-by-line using `view_file` and produce SUBSTANTIVE CODE EVIDENCE for the 7 Architecture Invariants (6 Core + Subsystem KI Contract):
        1. ENCAPSULATION: Quote the exact line number of `__all__ = [...]` and verify only intended public symbols are exported.
        2. ZERO-FALLBACK &amp; NAKED DICT BAN: Grep/inspect for `.get(`, `getattr(`, ` or `, `hasattr(`, `isinstance(..., dict)`, `match/case dict`, `dict[str, Any]`, `list[dict]`, `cast(Any, ...)`. Prove that missing data triggers Fail-Fast `AppException` rather than silent fallback defaults, and that all state transit uses 100% strongly typed Pydantic V2 DTOs.
        3. RFC 7807 DUAL-LOGGING: Quote the exact line numbers where `logger.error(..., exc_info=True)` is called immediately before `raise AppException(...)`.
        4. PEP 257 &amp; RAISES CONTRACT: Verify docstrings explicitly enumerate every `AppException` error code raised; ban `Raises: None`.
        5. SSOT CONFIG SOVEREIGNTY: Prove that no timeouts, limits, or thresholds are hardcoded; quote where `settings.py` is injected.
        6. ISTQB NEGATIVE TESTING PROOF: Locate the unit test file in `backend_v2/tests/unit/`, verify that at least 2 negative test cases exist covering boundary values / invalid inputs with `pytest.raises(AppException)`, and verify $\ge 90\%$ line coverage via `backend_audit_loop.py`.
        7. SUBSYSTEM KI INVARIANT PARITY: Quote the applicable Knowledge Item and cite exact line evidence proving compliance with its specific domain contract. If the target file is a generic service/utility/router with no subsystem KI, explicitly state: "NA - Generic Service/Utility (No Subsystem KI applies)".
      </constraint>

      <constraint name="DETERMINISTIC_AUDIT_GATE">For EVERY audited file, run the Universal 10-Stage Backend Quality Gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_file> --test --ast-strict`. Print ONLY the substantive code evidence summary for the 7 Architecture Invariants to the user.</constraint>

      <constraint name="DTO_SDUI_PARITY_GATE">
        If the target file is located within `backend_v2/models/` (specifically `backend_v2/models/dtos/` or `backend_v2/models/view/`) or defines DTO/view schemas shared with the Flutter frontend, you MUST run the Cross-Domain DTO Parity Gate:
        `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_dto_parity.py --fail-on-mismatch`
      </constraint>

      <action name="AUTONOMOUS FIX &amp; NEXT">
        Do NOT stop and wait for a "FIX" or "NEXT" command. If all rules passed, immediately proceed to the next file on your list. If there are failures, immediately enter the Two-Stage Remediation Pipeline:

        STAGE 2A: STATIC STRUCTURAL &amp; DOCSTRING HARDENING:
        - For static violations (missing `__all__ = [...]`, PEP 257 docstring warnings, missing `Raises:` contracts, Ruff formatting, missing `ConfigDict(strict=True, extra="forbid")`), execute direct surgical code fixes.
        - NEVER write artificial or tautological reflection unit tests (`hasattr`, `getattr`) for docstrings or `__all__` exports.
        - Verify static fixes immediately using: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --ast-strict`.

        STAGE 2B: RUNTIME BEHAVIORAL &amp; ISTQB TEST HARDENING:
        - For behavioral violations (missing validations, unhandled edge cases, loose dictionary migrations, or missing ISTQB negative boundary partitions), execute the strict TDD RED-GREEN-REFACTOR loop.
        - Locate the existing test file corresponding to your target in `backend_v2/tests/unit/`. Read the test file first to understand current fixtures.
        - FIRST update or create a negative/boundary test case asserting `pytest.raises(AppException)` that fails with the current broken code (RED).
        - Implement the domain logic fix to turn the test green (GREEN).
        - Verify full coverage and AST compliance via: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`.
      </action>

      <constraint name="DESTRUCTIVE VETO">You operate autonomously EXCEPT for Destructive Operations on External Boundary Contracts: deleting physical files, dropping database tables, or modifying external HTTP REST / WebSocket / OpenAPI endpoints without authorization. Conversely, refactoring internal Python service or repository function signatures is MANDATORY under LEGACY DEBT ANNIHILATION, provided that you synchronously discover and update all 1-hop callers and corresponding unit tests in the same atomic commit using `grep_search`.</constraint>
      
      <constraint name="AUDIT LOOP MANDATE &amp; CIRCUIT BREAKER">After code changes, you MUST run the Universal Quality Gate YOURSELF with strict AST guardrails: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`. DIRTY STATE ROLLBACK: If the Quality Gate fails 3 times on your refactor (Circuit Breaker trips), you MUST STOP attempting to duct-tape the code. Execute targeted rollback YOURSELF via `run_command` using `git restore <target_path> <test_path>` FIRST before updating any state trackers.</constraint>
      
      <constraint name="DOCUMENTATION &amp; KI AUDIT">If the refactoring caused significant architectural changes, file deletions, or the creation of new directories, create or update a Knowledge Item (KI) documenting the new pattern and update `@[.agents/rules/04_directory_reference.md]`. Do NOT manually edit `docs/architecture/01_` through `06_`.</constraint>
      
      <action name="STATE PERSISTENCE &amp; TRACKER UPDATE">
        When the target file and tests pass 100% of quality gates, immediately create an atomic commit for the successful changes using `run_command`:
        - Explicitly stage only the verified target file, its corresponding unit test file, and any directly modified 1-hop dependencies (never use `git add .`).
        - Commit with strict Conventional Commits syntax: `git commit -m "chore(hardening): audit and fix [target_name]"`.
        - Update `<appDataDir>\brain\<conversation-id>\scratch\hardening_state.json` by appending the audited file to the `DONE` array.
        - Check off `  - [x] @[completed_file.py]` in `### Post-Implementation Gates` under `Tier 2 Hardening (Backend)` if a Tracker was provided.
      </action>
      
      <action name="SESSION LIMIT &amp; HANDOVER">
        If you have processed 10 files (OR completed 3 atomic refactoring git commits for dirty files in this session), STOP immediately once the current file is complete. Append `# Session Handover Context` to the bottom of the Tracker/Epic file and print:
        `/tier5-resume --target="[absolute_path_to_tracker_artifact], [target_directory_being_audited]" --workflow=/tier2-hardening-backend --rules="00-antigravity-core.md, 01-python-backend.md"`.
      </action>
      
      <constraint name="LEGACY DEBT ANNIHILATION">Consult `@[.agents/skills/tier2-execute/references/modernity_and_tech_debt_checklist.md]` and aggressively refactor legacy dictionary contracts into 100% strict Pydantic V2 DTOs (`ConfigDict(strict=True, extra='forbid')`). If legacy unit tests fail because they expect old dictionary behaviors, ruthlessly rewrite or delete the offending legacy test.</constraint>
    </phase>
  </phases>
</system_prompt>
```

