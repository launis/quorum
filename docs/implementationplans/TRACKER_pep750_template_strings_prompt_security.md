> **STATUS: IN_PROGRESS / KÄYNNISSÄ (2/8 steps executed — 6/23 tasks)**

# Tracker: PEP 750 (t"...") Template Strings & Language-Level Prompt Injection Defense
**Plan:** @[docs/implementationplans/plan_pep750_template_strings_prompt_security.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
</required_context_rules>

## Step Execution Status
**Plan:** @[docs/implementationplans/plan_pep750_template_strings_prompt_security.md]
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/implementationplans/plan_pep750_template_strings_prompt_security.md] @[docs/implementationplans/TRACKER_pep750_template_strings_prompt_security.md]`
  - [x] Step 0: PRE-IMPLEMENTATION TOOLCHAIN & AST BASELINE
  - [x] Step 1: PHASE 1: PRE-IMPLEMENTATION CLEANUPS & BASELINE VERIFICATION
  - [ ] Step 2: CORE TEMPLATE PROCESSOR MODERNIZATION
  - [ ] Step 3: MATRIX SENSOR PROMPT BUILDER MIGRATION
  - [ ] Step 4: PROMPT COMPILER & SOURCE VERIFICATION MIGRATION
  - [ ] Step 5: ANALYTICAL HOOKS, GRAPH LINKER, ENGINES & INGRESS MIGRATION
  - [ ] Step 6: AST GUARDRAIL FORTIFICATION & QGR022 IMPLEMENTATION
  - [ ] Step 7: QUALITY GATES & FULL VERIFICATION LOOP
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/plan_pep750_template_strings_prompt_security.md] @[docs/implementationplans/TRACKER_pep750_template_strings_prompt_security.md]`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified @-referenced production backend files:
  - [ ] @[backend_v2/core/template_processor.py]
  - [ ] @[backend_v2/hooks/interaction_hook.py]
  - [ ] @[backend_v2/hooks/linguistics.py]
  - [ ] @[backend_v2/models/prompts/execution/dynamic_linguistics.py]
  - [ ] @[backend_v2/services/chat_parser.py]
  - [ ] @[backend_v2/services/orchestrator/engines/synthesis_engine.py]
  - [ ] @[backend_v2/services/orchestrator/prompt_compiler.py]
  - [ ] @[backend_v2/services/orchestrator/prompts/atom_extraction.py]
  - [ ] @[backend_v2/services/orchestrator/prompts/graph_linking.py]
  - [ ] @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]
  - [ ] @[backend_v2/services/orchestrator/sliding_window_linker.py]
  - [ ] @[backend_v2/services/orchestrator/two_pass_atomizer.py]
  - [ ] @[backend_v2/services/source_verification_service.py]
  - [ ] @[scripts/_ast_guardrails.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified @-referenced production Flutter files:
  - (No production Dart files modified in this plan; pure backend prompt security infrastructure)
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to anchor physical implementation in `docs/architecture/` (scoped to relevant documents), update relevant Knowledge Items, and synchronize `.agents/rules/04_directory_reference.md`.
  - [ ] Synchronize Existing Knowledge Items: `@[ki_python_314_concurrency_strictness.md]`, `@[ki_zero_permissive_typing.md]`
  - [ ] Synchronize Architecture Rule: `@[.agents/rules/04_directory_reference.md]`

### Final Plan Audit
- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/plan_pep750_template_strings_prompt_security.md] @[docs/implementationplans/TRACKER_pep750_template_strings_prompt_security.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent
- **Atomic Commit Mandate**: After each successful step or cohesive logical block verification, commit changes atomically with strict Conventional Commits syntax (`<type>(<scope>): <summary>`). Explicitly list all staged files.
- **Single Source of Truth**: All prompt compilation and dynamic value sanitization must flow through `TemplateProcessor.render_prompt(tmpl: Template) -> str`. Fragmented f-strings or manual CDATA concatenations are strictly banned.
- **Zero Permissive Typing**: Enforce strict Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`). No naked dictionaries (`dict[str, Any]`), lazy `.get()` calls, or silent exception swallowing.
- **Quality Gates**:
  - Python tests & static analysis: `uv run python scripts/backend_audit_loop.py <target_path> --test`
  - Guardrail verification: `uv run pytest backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py`
  - Markdown boundary audit: `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/plan_pep750_template_strings_prompt_security.md`
- **Execution Mode**: Supports Step-by-Step execution (default pause per step) and Continuous Full-Auto Mode (invoked via `/tier2-execute --full-auto`).
- **Context Budget Watchdog**: In Continuous Mode, proactively trigger `/tier5-session-handover` when context budget limit is reached: >8 turns, 3 atomic commits, or >5 modified complex files.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-01 | Baseline AST scan and Python 3.14.6 runtime `string.templatelib.Template` verification | Step 0 | [x] |
| REQ-02 | Consolidate duplicate unit test `test_template_processor.py` into canonical `tests/unit/core/test_template_processor.py` | Step 1 | [x] |
| REQ-03 | Consolidate duplicate unit test `test_matrix_sensor_prompt_builder.py` into canonical `tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py` | Step 1 | [x] |
| REQ-04 | Remediate AST strict debts in `prompt_compiler.py` (QGR020 duplicate `Field()`, QGR012 duck-typing) | Step 1 | [x] |
| REQ-05 | Remediate AST strict debts in `source_verification_service.py` (QGR016 lazy fallback) and `linguistics.py` (QGR016 ternary fallback) | Step 1 | [x] |
| REQ-06 | Remediate AST strict debts in `sliding_window_linker.py` (3x QGR020 duplicate `Field()` assignments) | Step 1 | [x] |
| REQ-07 | Implement `TemplateProcessor.render_prompt(template: Template) -> str` supporting native PEP 750 Template strings with Fail-Fast type checking | Step 2 | [ ] |
| REQ-08 | Automatic CDATA wrapping, `]]>` breakout shielding, and empty string coercion for falsy/None values | Step 2 | [ ] |
| REQ-09 | Attribute-context XML escaping via `xml.sax.saxutils.escape` without invalid CDATA injection inside quotes | Step 2 | [ ] |
| REQ-10 | Recursive rendering of nested `Template` instances and `:raw` format specifier support | Step 2 | [ ] |
| REQ-11 | Comprehensive unit test suite in `backend_v2/tests/unit/core/test_template_processor.py` verifying literal brace preservation and CDATA boundaries | Step 2 | [ ] |
| REQ-12 | Modernize `MatrixSensorPromptBuilder.build_caching_prefix` to construct XML blocks using `t"..."` literals with `render_prompt`, preserving Layer 1 cacheability | Step 3 | [ ] |
| REQ-13 | Refactor `MatrixSensorPromptBuilder.build_compiled_prompt` eliminating 12 manual `_cdata` variables and fixing double-interpolation bug | Step 3 | [ ] |
| REQ-14 | Modernize `PromptCompiler` (`build_xml_context`, `_extract_value_from_state`, `compile_chunk_payload_instruction`) with native `t"..."` literals | Step 4 | [ ] |
| REQ-15 | Modernize `SourceVerificationService` claim extraction and verification prompt assembly with native `t"..."` literals | Step 4 | [ ] |
| REQ-16 | Modernize `analyze_interaction_role` in `interaction_hook.py` with native `t"..."` literals and `render_prompt` | Step 5 | [ ] |
| REQ-17 | Refactor `DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE` into typed prompt builder function `build_dynamic_performative_user_prompt` in `dynamic_linguistics.py` and hook caller | Step 5 | [ ] |
| REQ-18 | Refactor `LINKER_USER_PROMPT` into typed prompt builder function `build_linker_user_prompt` in `graph_linking.py` and eradicate `safe_interpolate` in `sliding_window_linker.py` | Step 5 | [ ] |
| REQ-19 | Refactor `PHASE_1_SYSTEM_PROMPT` into typed prompt builder function `build_phase_1_system_prompt` in `atom_extraction.py` and modernize `two_pass_atomizer.py` | Step 5 | [ ] |
| REQ-20 | Modernize dialogue encapsulation in `chat_parser.py` and user payload compilation in `synthesis_engine.py` with native `t"..."` literals | Step 5 | [ ] |
| REQ-21 | Add static AST guardrail rule `QGR022` to `scripts/_ast_guardrails.py` banning unshielded `ast.JoinedStr` in prompt modules | Step 6 | [ ] |
| REQ-22 | Modernize `backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py` to assert `QGR022` and test `render_prompt` integration | Step 6 | [ ] |
| REQ-23 | Execute full backend audit loop `backend_audit_loop.py` and markdown boundary verification ensuring 100% test pass | Step 7 | [ ] |

# Session Handover Context
## Achieved
- Plan @[docs/implementationplans/plan_pep750_template_strings_prompt_security.md] researched, verified, and established with 100% AST line bound compliance.
- Granular 5-Column Architectural Directives Table and Falsification Red-Team Analysis embedded within implementation plan.
- Double-entry bookkeeping tracker created at @[docs/implementationplans/TRACKER_pep750_template_strings_prompt_security.md] with 1:1 step tracking (Step 0 to Step 7), 14 production hardening targets, and 23-row Requirements Traceability Matrix.
- Empirical runtime dry-runs verified Python 3.14.6 native support for PEP 750 `string.templatelib.Template` and `ast.TemplateStr`.
- All markdown boundary audits (MBD001-MBD009) and structural tracker audits pass with 0 errors.

## Learned
- **Language-Level Prompt Injection Firewall:** PEP 750 Template Strings (`t"..."`) physically segregate static string chunks from dynamic variables before evaluation, eliminating prompt injection vulnerabilities at the language parser level without relying on manual variable-by-variable sanitization.
- **XML Attribute Context Escaping:** Interpolating dynamic variables into XML attribute quotes (specifically: `source_id="{id}"`) requires standard XML entity escaping (`xml.sax.saxutils.escape`) rather than CDATA block delimiters to avoid generating invalid XML syntax.
- **Lexical Scope Binding for Templates:** Module-level template constants with unbound variable names raise `NameError` at module import time; parameterized prompt templates must be encapsulated into typed prompt builder functions.
- **Authoritative Perimeter Serialization Boundary:** Foundational model APIs require primitive `str` HTTP/gRPC payloads. `TemplateProcessor.render_prompt(tmpl: Template) -> str` serves as the sole authoritative perimeter serialization boundary immediately prior to dispatch.

## Remaining
- Execute Step 0 through Step 7 via `/tier2-execute @[docs/implementationplans/plan_pep750_template_strings_prompt_security.md] @[docs/implementationplans/TRACKER_pep750_template_strings_prompt_security.md]`.
- Complete Post-Implementation Hardening Gates and System 2 Red-Team Audit (`/tier8-audit-plan`).

## Resume Command
```powershell
/tier2-execute @[docs/implementationplans/plan_pep750_template_strings_prompt_security.md] @[docs/implementationplans/TRACKER_pep750_template_strings_prompt_security.md]
```
