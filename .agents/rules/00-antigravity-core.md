---
trigger: always_on
---

# ANTIGRAVITY COMMAND CENTER

<domain_boundary>
    <role>GLOBAL SYSTEM & META-COGNITION</role>
    <instruction>These rules govern the overarching IDE environment, interaction formatting, global artifacts, and Git protocols. They apply universally across all contexts, but do NOT override language-specific constraints (Python/Flutter) or Database Seed operations.</instruction>
</domain_boundary>

<ide_orchestration_protocol>
    <rule_block id="permission_granted_workflow">
        <mandate>STOP after completing a single step in a plan by default, UNLESS the user explicitly invokes Continuous Full-Auto Mode (e.g., via `/tier2-execute --full-auto` or explicit continuous permission). In Continuous Mode, proceed autonomously across steps as long as quality gates pass 100%, and halt immediately on failure or when triggering `context_amnesia_prevention` handover.</mandate>
    </rule_block>
    <rule_block id="strict_execution_mode_mandate">
        <mandate>NEVER write domain code to execute an implementation plan without the user explicitly providing an execution slash command like `/tier2-execute` or `/tier2-hardening-backend`. Force the user to invoke the required execution workflow tier before execution starts.</mandate>
    </rule_block>
    <rule_block id="slash_command_routing">
        <mandate>When a user inputs a slash command (e.g. `/tier2-execute`), IMMEDIATELY use `view_file` on the corresponding workflow file in `.agents/workflows/` and strictly adopt its system prompt and execution protocol. NEVER guess command behavior or respond with conversational filler.</mandate>
    </rule_block>
    <rule_block id="anti_ambiguity_mandate">
        <mandate>Implementation plans, epics, research analysis, and bug hunting artifacts MUST be strictly programmatic and deterministic. NEVER use "e.g.", "such as", "like", "etc.", or open-ended "specifically:" lists. Use either an explicit closed list ("specifically and exhaustively: A, B, C") OR a programmatic reference to the Single Source of Truth (specifically ALL models inheriting from AnySduiBlock in models/view/sdui.py). When executing programmatic references, your absolute FIRST action MUST be to use `grep_search` to physically query and explicitly list all matching concrete entities. NEVER use generic model definitions, generic paths, visual string examples ("A" -> "B"), or ambiguous UI tree placements.</mandate>
    </rule_block>
    <rule_block id="absolute_path_context_amnesia_ban">
        <mandate>ALWAYS strictly normalize all file references to workspace-relative paths (e.g., `@[backend_v2/services/...]` and `@[ki_sdui_matrix_synthesis.md]`). NEVER use hardcoded local absolute paths (e.g., `c:\src\quorum\...` or `C:\Users\...`).</mandate>
    </rule_block>
    <rule_block id="context_rules_governance_mandate">
        <mandate>All Epic documents (header lines 1..N), implementation plans, and tracker files MUST declare rules and Knowledge Items inside a single, canonical `<required_context_rules>` XML block at the top using exclusively `<rule>@[.agents/rules/...]</rule>` and `<knowledge_item>@[ki_name.md]</knowledge_item>`. Governance sections MUST reference this top block. NEVER use `<ki>` or separate `<required_knowledge_items>` blocks.</mandate>
    </rule_block>
    <rule_block id="anti_apology">
        <mandate>When correcting mistakes based on user feedback, NEVER apologize or use conversational filler. Output a `<thinking_process>` block detailing root cause and immediately output the corrected code (instruct commit amendment if already committed).</mandate>
    </rule_block>
    <rule_block id="anti_hallucination_read">
        <mandate>ALWAYS use tools to read current context before proposing modifications. NEVER guess file contents.</mandate>
    </rule_block>
    <rule_block id="english_language_mandate">
        <mandate>ALL code-level artifacts (variables, functions, classes, docstrings, inline comments, git commit messages) MUST be written EXCLUSIVELY in English. NEVER mix Finnish or other languages in code artifacts even if the user speaks Finnish.</mandate>
    </rule_block>
    <rule_block id="documentation_present_tense_mandate">
        <mandate>ALWAYS document code and architecture in present tense describing CURRENT state and functionality. In `docs/architecture/` documents, NEVER describe project phases, development stages, or historical progressions (e.g., "Phase 1", "Phase 2", "vaiheet", "Epic XX brought this..."), and NEVER use artificial meta-rules like "- **Law:**" / "- **Enforcement:**" or label sections as "(The Laws)". Describe purely, directly, and authoritatively what the system currently has and how it operates right now ("kerro ainoastaan ja puhtaasti se mitä meillä on nyt").</mandate>
    </rule_block>
    <rule_block id="ssot_reuse_mandate">
        <mandate>1. INVESTIGATE: Identify code that can be abstracted into an SSOT. 2. MIGRATE: Refactor legacy code to the new SSOT immediately (timebox to wiring pipes without rewriting internal business rules). 3. NEVER build parallel systems, write new components without analyzing reusability, or force false unifications across decoupled domains.</mandate>
    </rule_block>
    <rule_block id="explicit_scope_write">
        <mandate>ONLY modify TARGET files. Treat CONTEXT files as strictly Read-Only.</mandate>
    </rule_block>
    <rule_block id="anti_duplication">
        <mandate>Explicitly DELETE or OVERWRITE old versions of code when modifying a file. NEVER append new code to the end of a file while leaving broken versions intact.</mandate>
    </rule_block>
    <rule_block id="atomic_checkpoint_mandate">
        <mandate>After ANY successful run of the `universal_quality_gate` audit script, ALWAYS instruct the user to perform an atomic `git commit` with English messages before proceeding to the next file or logic block. Exception: If a structural refactor mathematically requires modifying a coupled set of files (e.g., breaking circular imports) before the system compiles, modify that specific batch concurrently before running the quality gate and instructing the commit. NEVER propose `git add .` or modify multiple architectural domains (UI and Backend) concurrently without a save state.</mandate>
    </rule_block>
    <rule_block id="context_amnesia_prevention">
        <mandate>Proactively suggest executing `/tier5-session-handover` if you process >8 user prompts in a session, complete 3 atomic `git commit` operations, or modify >5 distinct complex files. NEVER silently persist across heavy multi-directory refactors.</mandate>
    </rule_block>
    <rule_block id="read_before_think_lock">
        <mandate>Your VERY FIRST tool call in a new task MUST be `view_file` to load the appropriate rule file (e.g. `00-antigravity-core.md`). NEVER output `<thinking_process>`, make assumptions, or generate code before reading rules.</mandate>
    </rule_block>
    <rule_block id="mandatory_chain_of_thought">
        <mandate>Wrap architectural thinking inside `<thinking_process>` XML tags BEFORE writing code (stating rules applied, root cause, execution plan). NEVER output code blocks or write tools immediately after receiving a prompt.</mandate>
    </rule_block>
    <rule_block id="surgical_precision_edits">
        <mandate>Provide entire compilable structural blocks or use precise search-and-replace tools. If `multi_replace_file_content` fails, fallback to `view_file` or use `write_to_file`. NEVER use lazy placeholders like `// ... rest of the file ...`.</mandate>
    </rule_block>
    <rule_block id="temporary_workspace_sandbox">
        <mandate>Write and execute all temporary files, debugging scripts, and ad-hoc migration programs EXCLUSIVELY in `<appDataDir>\brain\<conversation-id>/scratch/`. Epics and Implementation Plans MUST NOT list scratch files in TARGET boundaries. NEVER create scratch files in repository roots, `backend_v2`, `client_app_v2`, or legacy `tmp\`.</mandate>
    </rule_block>
    <rule_block id="logfire_delegation_mandate">
        <mandate>Investigate LLM token anomalies, latency, and hallucinations via local execution traces: use `grep_search` on `backend_debug.log` with the Execution ID. When reading `llm_debug_prompts.md` or `frozen_context.json`, use `grep_search` first and `view_file` with STRICT `StartLine`/`EndLine` bounds. NEVER read massive trace files blindly without line limits.</mandate>
    </rule_block>
    <rule_block id="forensic_execution_artifacts">
        <mandate>When querying `seed_data.json` or debug prompts, use `grep_search` first and `view_file` with strict line bounds. NEVER read multi-megabyte `execution_trace.json` directly (parse it via Python in `scratch/`). Output files like `report.pdf` or `inputs/` represent finalized state.</mandate>
    </rule_block>
    <rule_block id="dual_axis_documentation_mandate">
        <mandate>Follow the Dual-Axis Documentation Paradigm: AI agents read `rules/` and KIs; humans read `docs/architecture/`. NEVER manually edit `docs/architecture/01_` through `06_` during coding workflows (route structural updates via KI creation -> `/tier7-describe-architecture`). You MAY directly edit `.agents/rules/04_directory_reference.md` and `docs/architecture/00_README_META_ARCHITECTURE.md`.</mandate>
    </rule_block>
</ide_orchestration_protocol>

<catastrophic_system_bans>
    <rule_block id="feature_sovereignty_mandate">
        <mandate>Performance optimizations MUST be structural. If optimizing latency or tokens requires dropping a functional feature or data field expected in the UI/DB, you MUST STOP and explicitly ask for "PERMISSION GRANTED to deprecate feature X to solve Y". NEVER autonomously delete, bypass, or deprecate cognitive features, metrics, or matrix metadata.</mandate>
    </rule_block>
    <rule_block id="the_zero_compromise_pledge">
        <mandate>Enforce strict Pydantic V2/Freezed schemas and 100% typed domain transit. If an expected key is missing, raise an explicit `AppException` and CRASH. Zero tolerance for silent bypasses. NEVER implement backwards compatibility, fallback chains ("if A is missing, try B"), language-level defaults (`v.get('field', '')`), `hasattr()`, `isinstance(data, dict)`, `match/case dict`, `cast(Any, ...)`, naked dictionaries (`dict[str, Any]`, `list[dict]`, `TypedDict`), anonymous multi-value state tuples ("Tuple Hell"), `# noqa: QGR` suppressions, or recursive dictionary loops.</mandate>
    </rule_block>
    <rule_block id="the_duct_tape_ban">
        <mandate>Fix root causes instead of patching symptoms. If data is malformed, crash loudly. Extract deep mutation loops into pure, isolated, testable functions. NEVER write duct-tape code, return empty arrays `[]` / default dicts `{}`, hide UI elements with `SizedBox.shrink()`, or catch-all with `try...except Exception:`.</mandate>
    </rule_block>
    <rule_block id="zero_service_layer_fallbacks">
        <mandate>Domain definitions MUST be strictly typed using Enum overrides, 100% Pydantic V2 DTOs, and `@model_validator`s. Services MUST crash Fail-Fast if the Domain Model lacks a guaranteed value natively. NEVER use raw dictionaries for state transit (`no_naked_dicts_in_state`), and NEVER use `.get(key, default)`, `getattr(obj, key, default)`, or `if value is None: value = default` in Service or Controller layers. Raw dictionary conversions (`.model_dump(mode='json')` / `Model.model_validate(raw)`) are permitted EXCLUSIVELY at absolute external persistence and network boundaries.</mandate>
    </rule_block>
    <rule_block id="ban_anonymous_state_tuples">
        <mandate>NEVER use anonymous multi-value tuples (3+ elements or 2+ elements of identical primitive types), positional index access (`item[0]`, `res[1]`), or positional tuple unpacking (`a, b, c = ...`) for domain state transit or service layer returns ("Tuple Hell"). ALWAYS encapsulate multi-field return states and pipeline payloads into strictly typed, immutable Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`). 2-tuples are permitted EXCLUSIVELY for standard (payload, TokenUsage) or (key, value) pairs at low-level utility boundaries.</mandate>
    </rule_block>
    <rule_block id="the_no_legacy_mandate">
        <mandate>Legacy support is STRICTLY PROHIBITED. If data is missing or malformed, Fail-Fast. Ruthlessly delete obsolete code, fallback chains, and legacy test fixtures. NEVER maintain backwards compatibility with V1 structures, deprecated APIs, or legacy databases.</mandate>
    </rule_block>
    <rule_block id="database_schema_hallucination">
        <mandate>The SSOT structure in `seed_data.json` is immutable architectural law. If an API response requires nested data (e.g., workflows containing output_profiles), build a DTO (e.g., `WorkflowResponseDTO`). NEVER physically alter root persistence arrays in `seed_data.json` or embed duplicate models into domain layers without an explicit roadmap mandate.</mandate>
    </rule_block>
    <rule_block id="dependency_hallucination_firewall">
        <mandate>Zero-Trust dependency environment: solve problems using natively installed tools. If external libraries are mathematically necessary, wait for "PERMISSION GRANTED". NEVER autonomously propose new packages to `pubspec.yaml` or `uv.lock`.</mandate>
    </rule_block>
    <rule_block id="windows_powershell_mandate">
        <mandate>Exclusively use native Windows 11 PowerShell commands and syntax (use `;` to chain commands, `Remove-Item`/`del` instead of `rm`). NEVER use Unix/Linux commands (`rm`, `ls`, `cat`, `grep`, `sed`) or bash `&&` syntax in commands or examples.</mandate>
    </rule_block>
    <rule_block id="native_mcp_tooling">
        <mandate>ALWAYS prioritize native MCP tools (`view_file` to read, `grep_search` to find, `multi_replace_file_content` to edit, fallback to `write_to_file` if needed). NEVER use terminal text manipulation tools (`cat`, `grep`, `sed`) or instruct the user to run scripts manually.</mandate>
    </rule_block>
    <rule_block id="deceptive_persistence_mocking_ban">
        <mandate>NEVER mock repository persistence, save, or update methods with static return values or unverified `AsyncMock()` instances that fail to assert real state mutation. Persistence unit and integration tests MUST verify stateful roundtrip behavior: modifications saved to the repository layer MUST be physically verified via subsequent get/fetch operations returning the updated domain model. Zero tolerance for deceptive green tests that bypass persistence verification.</mandate>
    </rule_block>
</catastrophic_system_bans>

<architectural_invariants>
    <rule_block id="anti_semantic_drift_renaming">
        <mandate>Field and variable names are PERMANENT architectural contracts. Nomenclature between Python (Backend) and Flutter (Frontend) MUST remain 1:1 identical at serialization layer (Python `snake_case` mapped to Flutter `camelCase` via `@JsonKey(name: 'snake_case')`). NEVER arbitrarily invent new variable names, rename DTO fields, alter DB properties for subjective clarity, or swap the names of critical domain variables/concepts between each other. All names and terms MUST be derived directly from the Single Source of Truth (SSOT).</mandate>
    </rule_block>
    <rule_block id="universal_fail_fast">
        <mandate>Enforce Fail-Fast at every boundary: if data does not match Pydantic V2 or Dart 3 Freezed schema, the system MUST crash audibly and visibly (`AppException` or `AppErrorBoundary`). NEVER allow invalid data to pass silently or fix corrupted JSON visually in the UI.</mandate>
    </rule_block>
    <rule_block id="rfc7807_dual_reporting_mandate">
        <mandate>Implement RFC 7807 Dual-Reporting: every `AppException` thrown MUST be preceded by a structured `logger.error` containing the exact mathematical/logical reason and contextual parameters. NEVER crash without structured logging.</mandate>
    </rule_block>
    <rule_block id="output_format_requirements">
        <mandate>Prompts / Code Blocks MUST be in English. Explanations/Context MUST be in Finnish. Only comment WHY business logic exists using Imperative Mood. NEVER write code in other languages or explain mechanical WHAT in comments.</mandate>
    </rule_block>
    <rule_block id="mathematical_extrema_anchoring">
        <mandate>Dynamically resolve absolute mathematical extrema by extracting minimum and maximum `score` from the block's `scales` array directly at the Domain Model layer (e.g. `@property computed_min` and `computed_max` on `PromptBlock`). NEVER hardcode min/max scale values (e.g. 1 to 5) or rely on assumed defaults.</mandate>
    </rule_block>
    <rule_block id="cross_language_mapping_mandate">
        <mandate>LLM rules (Matrix scales, TDA Assertions, instructions) MUST ALWAYS be defined in English (System Language) and dynamically instructed to map against Localized Target Language (e.g., Finnish) source documents. Use generalized terms like "Localized Target Language" in schemas; NEVER hardcode Finnish as the only target language or write LLM rules in the target language.</mandate>
    </rule_block>
    <rule_block id="sdui_contract_fracture_prevention">
        <mandate>Enforce Cross-Domain DTO & SDUI Semantic Parity: Backend Python DTOs (in `models/dtos/`, `models/view/sdui.py`), PDF templates (`templates/`, `services/pdf_generator.py`), and Frontend Dart Freezed models (in `client_app_v2/.../models/`, `client_app_v2/.../sdui/`) are mathematically coupled. Modifying any SDUI model, adapter, template, or renderer requires synchronously running `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py` in addition to `backend_audit_loop.py` and `flutter_audit_loop.py` to mathematically verify 1:1 semantic parity between the Flutter UI and generated PDF. NEVER modify an SDUI model or adapter without running the semantic parity test.</mandate>
    </rule_block>
    <rule_block id="universal_ssot_and_normalization_mandate">
        <mandate>Enforce Absolute SSOT & Data Normalization: Every piece of state, telemetry metric, token count, pricing registry, financial cost, configuration mapping, and entity relation MUST have exactly ONE authoritative source and ONE canonical storage location across both Backend and Frontend. All data MUST be maximally normalized at rest and in transit (zero duplicate/denormalized sub-dictionaries, zero split-schema payloads). Both Python and Dart layers MUST consume data strictly from this single normalized location. NEVER define secondary shadow tables, local backup dictionaries, or parallel fallback access chains (`a.get('field') or a.get('sub', {}).get('field')`, `data['x'] ?? data['summary']['x']`, or custom pricing dictionaries duplicating an authoritative registry). If data or metadata is missing from the designated canonical SSOT, Fail-Fast loudly rather than guessing or maintaining shadow data.</mandate>
    </rule_block>
</architectural_invariants>

<universal_quality_gate>
    <rule_block id="quality_gate_execution">
        <mandate>ALWAYS enforce automated audit testing after completing a cohesive logical step. For `.py` files, run: `uv run python scripts/backend_audit_loop.py <target_path> --test`. For `.dart` files, run: `uv run python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build` (append --build when Freezed models need generation). NEVER run generic pytest/flutter test without global audit scripts, and NEVER bypass the audit loop assuming changes are "too small".</mandate>
    </rule_block>
    <rule_block id="zero_deprecation_mandate">
        <mandate>Proactively replace deprecated members. Resolve ALL syntax errors, typing errors, and warnings before completion. NEVER declare a step complete when syntax errors or deprecation warnings exist.</mandate>
    </rule_block>
    <rule_block id="tdd_mandate">
        <mandate>Write a failing test that reproduces the bug BEFORE fixing domain code. Code is complete only when a reliable test verifies the change. NEVER fix bugs or add features without writing tests first.</mandate>
    </rule_block>
    <rule_block id="anti_tdd_trap">
        <mandate>If a legacy test fails because it asserts outdated behavior (expecting raw `dict`, `asyncio.gather`), ruthlessly rewrite or delete the legacy test to comply with modern architectural invariants. NEVER patch modern domain code (reverting to dicts/removing strict types) to make legacy tests pass.</mandate>
    </rule_block>
    <rule_block id="anti_test_skipping_mandate">
        <mandate>If a test fails due to legacy architecture, UN-SKIP and FIX the test. NEVER silence failing tests by adding `@pytest.mark.skip` or commenting them out to achieve a green test suite.</mandate>
    </rule_block>
    <rule_block id="mocking_mandate_for_llm">
        <mandate>When testing LLM interfaces or network operations, ABSOLUTELY use mocked JSON fixtures via global `backend_v2/llm/mock.py` and `mock_data.py`. Direct HTTP/LLM calls during unit tests or CI/CD pipelines are STRICTLY FORBIDDEN.</mandate>
    </rule_block>
    <rule_block id="fragmented_quality_gates_prevention">
        <mandate>Enforce Two-Stage Testing: 1) Development Stage: run isolated tests (e.g. `uv run pytest path/to/test.py::test_name`). 2) Completion Gate Stage: run GLOBAL audit loops (`backend_audit_loop.py` and `flutter_audit_loop.py`) or the entire test suite before completion. NEVER run only localized subsets and declare completion ("Fake Green").</mandate>
    </rule_block>
    <rule_block id="circuit_breaker_protocol">
        <mandate>Implement the Rule of Three: if failing 3 times iteratively on the same Pytest or Flutter error, STOP immediately. Output `<circuit_breaker_tripped>`, instruct the user to run `git restore . ; git clean -fd`, explain the paradox, and wait for human guidance. NEVER leave the workspace in a broken state.</mandate>
    </rule_block>
    <rule_block id="deterministic_testing_delegation">
        <mandate>1) Use `polyfactory` for mock data. 2) `conftest.py` blocks networks. 3) `backend_audit_loop.py` enforces >90% coverage (analyze `Miss` column if failing). NEVER write manual JSON dictionary mock data or claim completion without passing coverage.</mandate>
    </rule_block>
    <rule_block id="anti_happy_path_mandate">
        <mandate>For every positive test case, write at least 2 negative test cases covering: 1) Missing/invalid required inputs triggering AppException, 2) Boundary values (min-1, max+1) or type violations per ISTQB Boundary Value Analysis. Coverage must not decrease. NEVER deliver features/fixes with only happy path coverage.</mandate>
    </rule_block>
    <rule_block id="anti_lazy_fallback_mandate">
        <mandate>Enforce Zero-Compromise Fail-Fast: if mandatory variables, headers, or state objects are missing, log the error and raise an explicit `AppException` (e.g. `ErrorCodes.VALIDATION_FAILED`) instantly. NEVER use lazy fallbacks (`accept_language or "en"`, `metadata.get("key") or {}`) to silently bypass missing state.</mandate>
    </rule_block>
    <rule_block id="ast_guardrail_mandate">
        <mandate>When defining new architectural rules or deprecating patterns, proactively build AST Guardrail tests (using Python `ast` module) to statically enforce rules before standard unit tests. NEVER introduce architectural constraints or ban functions (`hasattr`, `ResultProjector`) without an AST guardrail test.</mandate>
    </rule_block>
    <rule_block id="heterogeneous_payload_testing_mandate">
        <mandate>When testing components processing heterogeneous DAG state (`SynthesisPayloadCompressor`, `synthesis_distiller_hook`, `StepOutputDTO` consumers), tests MUST explicitly cover the 4 ISTQB Equivalence Partitions: 1) Structured JSON/Dict (`dict[str, Any]`), 2) List collections (`list[Any]`), 3) Pure String/Markdown (`str`), 4) Scalars/Primitives (`int`, `float`, `bool`) and falsy inputs (`None`, `""`, `{}`). For E2E integration bugs, write a failing test with the exact runtime payload before modifying domain logic. NEVER test heterogeneous state consumers with dicts only.</mandate>
    </rule_block>
    <rule_block id="preflight_schema_assertion_mandate">
        <mandate>Persistence unit and integration tests MUST assert that all stored and reconstituted documents pass root Pydantic V2 model validation without empty strings, missing foreign keys, or un-prefixed IDs. All entity IDs MUST strictly conform to `OPAQUE_STRIPE_ID_REGEX` and `EntityPrefix`. Tests asserting mock persistence MUST validate that the underlying payload matches the strict domain schema with `extra="forbid"` before accepting repository writes.</mandate>
    </rule_block>
</universal_quality_gate>