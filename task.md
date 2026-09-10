# Task Tracker: Targeted CDATA Prompt Injection Hardening

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
</required_context_rules>

Implementation Plan: @[c:\Users\risto\.gemini\antigravity-ide\brain\51393ce4-83e7-4adb-997f-7ab78478034e\implementation_plan.md]

## Pre-Flight Checklist (<constraint> tags)
- [x] Constraint 1 (`cdata_template_shielding_mandate`): All dynamic prompt insertions MUST be mediated exclusively through `TemplateProcessor.encapsulate_payload()` or `TemplateProcessor.safe_interpolate()`.
- [x] Constraint 2 (`breakout_shielding`): Every payload MUST be shielded against CDATA breakout by replacing `]]>` with `]]]]><![CDATA[>` before wrapping in `<![CDATA[ ... ]]>`.
- [x] Constraint 3 (`static_first_dynamic_last_topology`): Keep static prompt directives intact and preserve context caching prefix boundaries.
- [x] Constraint 4 (`the_zero_compromise_pledge`): Zero permissive typing, zero ad-hoc string fallbacks, zero naked dicts.
- [x] Constraint 5 (`verbatim_verifier_preserved`): `ChatParserService` anchor phrase matching operates monotonically against raw unescaped `raw_paste`.
- [x] Constraint 6 (`ast_guardrail_mandate`): AST guardrail test to statically enforce `TemplateProcessor` usage and ban unshielded f-strings into `<source_data>` or `<user_payload>`.

## Execution Tasks

### PHASE 1: PRE-IMPLEMENTATION CLEANUPS & TEST ASSERTIONS
- [x] **Step 1: Technical Debt Sweep in Existing Tests & Services**
  - [x] Update `backend_v2/tests/unit/services/test_source_verification_service.py` (`test_extract_source_claims_xml_injection_escaped`) to assert CDATA encapsulation and breakout neutralization.
  - [x] Update `backend_v2/tests/unit/services/test_chat_parser.py` (`test_chat_parser_role_segregation_and_success`) to assert `<![CDATA[` presence in dynamic message.
  - [x] Remove unused `import html` in `backend_v2/services/source_verification_service.py`.

### PHASE 2: CDATA ENCAPSULATION IMPLEMENTATION ACROSS 6 SERVICES & HOOKS
- [x] **Step 2: Core Backend Services & Hooks Hardening**
  - [x] **2.1: `backend_v2/services/chat_parser.py`**: Encapsulate `raw_paste` using `TemplateProcessor.encapsulate_payload(raw_paste)` inside `<source_data>`.
  - [x] **2.2: `backend_v2/services/orchestrator/two_pass_atomizer.py`**: Encapsulate `hydrated_text` with `TemplateProcessor.encapsulate_payload` in `execute_phase_0`, `execute_phase_1`, and `execute_phase_1_drafts`.
  - [x] **2.3: `backend_v2/services/orchestrator/sliding_window_linker.py`**: Replace direct `.format()` with `TemplateProcessor.safe_interpolate(LINKER_USER_PROMPT, global_ontology_map=ontology_text, claims_window=claims_text.strip())`.
  - [x] **2.4: `backend_v2/services/source_verification_service.py`**: Replace `html.escape` with `TemplateProcessor.encapsulate_payload(text[: settings.source_extraction_max_chars].strip())`.
  - [x] **2.5: `backend_v2/hooks/interaction_hook.py`**: Encapsulate `chat_log` using `TemplateProcessor.encapsulate_payload(chat_log)` inside `<user_payload>`.
  - [x] **2.6: `backend_v2/hooks/linguistics.py`**: Encapsulate `text_to_scan` using `TemplateProcessor.encapsulate_payload(text_to_scan)` before prompt formatting.

### PHASE 3: COMPREHENSIVE TESTS & AST GUARDRAILS
- [x] **Step 3: Guardrail & Unit Testing**
  - [x] Create `backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py` with AST guardrail and unit tests covering all 6 components.
  - [x] Run targeted unit test suite for all 6 components (64/64 passing).
  - [x] Run `backend_audit_loop.py` quality gate (100% pass, 0 errors, 95% coverage).

### PHASE 4: VERIFICATION & COMMIT CHECKPOINT
- [x] **Step 4: Audit & Commit**
  - [x] Full backend audit loop.
  - [x] Atomic git commit instructions.

## Session Handover Context
- **Achieved**: 100% completion of Targeted CDATA Prompt Injection Hardening across all 6 backend services and hooks (`chat_parser.py`, `two_pass_atomizer.py`, `sliding_window_linker.py`, `source_verification_service.py`, `interaction_hook.py`, and `linguistics.py`). Added AST guardrail and comprehensive test suite in `backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py`. All 64 unit and guardrail tests pass with exit code 0. Full backend audit loop passed cleanly with 95% coverage and 0 lint/mypy/AST issues.
- **Learned**: In XML prompt construction, `TemplateProcessor._apply_breakout_shield` replaces `]]>` with `]]]]><![CDATA[>`, creating adjacent valid CDATA sections that prevent tag injection without altering the underlying character sequence decoded by downstream models or parsers.
- **Remaining**: Mandatory Tier 8 System 2 Red-Team Audit (`/tier8-audit-plan`).
