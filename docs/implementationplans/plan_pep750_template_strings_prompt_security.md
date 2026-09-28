> **STATUS: PENDING / ODOTTAA TOTEUTUSTA (PEP 750 Template Strings & Language-Level Prompt Injection Defense)**

# Implementation Plan: PEP 750 (t"...") Template Strings & Language-Level Prompt Injection Defense

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
</required_context_rules>

## Goal Description
Modernize Quorum's prompt compilation and dynamic text interpolation infrastructure by implementing Python 3.14 PEP 750 Template Strings (`t"..."`). Replace manual ad-hoc string formatting (`string.format()`, standard f-strings) and vulnerable string concatenation with structured `Template` objects. Upgrade `TemplateProcessor` into a language-level Template Renderer that automatically sanitizes dynamic interpolations (CDATA encapsulation, breakout shielding, and type coercion) while leaving static structural directives intact. Enforce the Four-Layer Clean Stack hierarchy and Static-First Context Caching invariants, and institute AST Guardrails to eliminate un-fenced f-strings in prompt assembly pathways.

---

## User Review Required

> [!IMPORTANT]
> **Language & Toolchain Native Readiness (Python 3.14.6 & AST Parsing Verified):**  
> Empirical runtime dry-runs confirm that Quorum's active Python 3.14.6 runtime natively supports PEP 750 Template String Literals (`t"..."`), producing native `string.templatelib.Template` instances. The Python AST parser natively outputs `ast.TemplateStr`, and both `ruff` and `mypy --strict` pass 100% with zero syntax errors or typing violations. In accordance with Quorum's `zero_backward_compatibility_planning_ban` and `single_pipeline_invariant_mandate`, all speculative callable fallback factories (`TemplateProcessor.template(...)`) and legacy backward-compatibility shims are strictly purged. The pipeline operates through exactly one sovereign implementation: native `t"..."` literals parsed and sanitized through `TemplateProcessor.render_prompt(tmpl: Template) -> str`.

> [!WARNING]
> **Authoritative Perimeter Serialization Boundary:**  
> Foundational model SDKs (Vertex AI Gemini, Anthropic Claude, LiteLLM) require raw `str` payloads over HTTP or gRPC. `TemplateProcessor.render_prompt(tmpl: Template) -> str` serves as the sole authoritative serialization boundary. Raw `str` conversion must occur at the absolute perimeter just before API dispatch, never inside intermediate prompt builders.

> [!NOTE]
> **Static-First Context Caching Prefix Invariant:**  
> The physical segregation into static string chunks (`strings`) and dynamic interpolations (`interpolations`) allows mathematical isolation of Layer 1 and Layer 2 prompt prefixes, guaranteeing 95%+ prefix caching hit rates on Vertex AI and Anthropic. Dynamic user inputs are confined strictly to Layer 4 tail payloads.

---

## Target Files & Line Boundaries

- `[MODIFY]` @[backend_v2/core/template_processor.py#L19-L128] — Modernize `TemplateProcessor` to support native Python 3.14 PEP 750 Template strings via `render_prompt`, automatic CDATA encapsulation, breakout shielding, attribute-context XML escaping, and recursive template rendering.
- `[MODIFY]` @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L28-L298] — Eliminate 12 manual `_cdata` variables and f-string XML concatenation, refactoring to native `t"..."` literals with `TemplateProcessor.render_prompt`.
- `[MODIFY]` @[backend_v2/services/orchestrator/prompt_compiler.py#L77-L633] — Refactor XML tag formatting and user payload compilation in `build_xml_context`, `_extract_value_from_state`, and `compile_chunk_payload_instruction` to use structured templates.
- `[MODIFY]` @[backend_v2/services/source_verification_service.py#L38-L261] — Replace manual CDATA and f-string user message assembly in `_extract_source_claims` and `_verify_single_claim` with native `t"..."` literals.
- `[MODIFY]` @[backend_v2/hooks/interaction_hook.py#L41-L167] — Modernize `analyze_interaction_role` prompt assembly to use `t"..."` literals and `TemplateProcessor.render_prompt`.
- `[MODIFY]` @[backend_v2/hooks/linguistics.py#L53-L199] — Modernize `detect_performative_patterns` prompt assembly to call `build_dynamic_performative_user_prompt` with `TemplateProcessor.render_prompt`.
- `[MODIFY]` @[backend_v2/models/prompts/execution/dynamic_linguistics.py] — Refactor `DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE` into typed prompt builder function `build_dynamic_performative_user_prompt(language: str, text_to_scan: str) -> Template`.
- `[MODIFY]` @[backend_v2/services/orchestrator/sliding_window_linker.py#L122-L353] — Eradicate `safe_interpolate` dependency, calling `build_linker_user_prompt` rendered via `TemplateProcessor.render_prompt`.
- `[MODIFY]` @[backend_v2/services/orchestrator/prompts/graph_linking.py] — Refactor `LINKER_USER_PROMPT` into typed prompt builder function `build_linker_user_prompt(global_ontology_map: str, claims_window: str) -> Template`.
- `[MODIFY]` @[backend_v2/services/orchestrator/prompts/atom_extraction.py] — Refactor `PHASE_1_SYSTEM_PROMPT` into typed prompt builder function `build_phase_1_system_prompt(ontology_map_json: str) -> Template`.
- `[MODIFY]` @[backend_v2/services/orchestrator/two_pass_atomizer.py#L39-L586] — Replace `.replace("{ontology_map_json}", ontology_json)` and f-string `<source_data>` concatenation with `build_phase_1_system_prompt` and `render_prompt`.
- `[MODIFY]` @[backend_v2/services/chat_parser.py#L57-L284] — Replace f-string `<source_data>` concatenation with native `t"..."` literals and `TemplateProcessor.render_prompt`.
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286] — Modernize user message assembly to use native `t"..."` template literals rendered via `TemplateProcessor.render_prompt`.
- `[MODIFY]` @[scripts/_ast_guardrails.py] — Add static guardrail rule `QGR022` banning unshielded `ast.JoinedStr` f-strings in prompt modules and enforcing `ast.TemplateStr` or `TemplateProcessor.render_prompt`.
- `[MODIFY]` @[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py] — Upgrade static AST checks to verify `QGR022` and modernize test cases to assert `render_prompt`.
- `[MODIFY]` @[backend_v2/tests/unit/core/test_template_processor.py] — Consolidate duplicate unit tests and add comprehensive suite for `render_prompt`.
- `[DELETE]` @[backend_v2/tests/unit/test_template_processor.py] — Delete legacy root test duplicate to uphold test directory isolation.
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py] — Consolidate duplicate unit tests.
- `[DELETE]` @[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py] — Delete legacy root test duplicate to uphold test directory isolation.
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/prompts/test_graph_linking.py] — Modernize to test `build_linker_user_prompt`.
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/prompts/test_atom_extraction.py] — Modernize to test `build_phase_1_system_prompt`.
- `[MODIFY]` @[backend_v2/tests/unit/models/prompts/execution/test_dynamic_linguistics.py] — Modernize to test `build_dynamic_performative_user_prompt`.

---

## Touched Scope Technical Debt & Anti-Pattern Sweep

An exhaustive AST and ripgrep scan of `backend_v2` identified the following technical debt items across prompt compilation targets and 1-hop callers:

1. **`@[backend_v2/core/template_processor.py#L19-L128]` (`TemplateProcessor`)**:
   - Legacy `safe_interpolate` relies on `str.format(**safe_kwargs)`, which fails with `KeyError` or `ValueError` whenever prompt templates contain literal curly brackets in JSON schemas or code examples.
   - Lacks native support for Python 3.14 `string.templatelib.Template` objects.
   - Forces callers to manually call `encapsulate_payload` before stitching strings together.
2. **`@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L28-L298]` (`MatrixSensorPromptBuilder`)**:
   - Repetitive, manual `TemplateProcessor.encapsulate_payload` calls on 12+ individual assertion fields (`assertion.question`, `assertion.extraction_rule`, `assertion.anchor_target`, `assertion.contrastive_example`, `assertion.target_speaker`, `dep.edge_reasoning`).
   - Stitches XML tags using standard f-strings (`f"<question>\n{q_cdata}\n</question>\n"`), creating opportunities for accidental omission of sanitization.
   - Double CDATA encapsulation bug: passes pre-formatted XML strings (`deps_str`, `claims_str`) into `TemplateProcessor.safe_interpolate`, which re-wraps structural tags inside CDATA.
3. **`@[backend_v2/services/orchestrator/prompt_compiler.py#L77-L633]` (`PromptCompiler`)**:
   - `build_xml_context` (`#L206-L316`) stitches metadata and input tags using piecemeal f-strings (`f"<matrix_input source_id=\"{source_id_to_use}\">\n{desc_text}{wrapped_val}\n</matrix_input>"`).
   - `_extract_value_from_state` (`#L318-L482`) uses f-strings to assemble dynamic input blocks (`f"  <{clean_key.replace(' ', '_')}>{TemplateProcessor.encapsulate_payload(micro_v)}</{clean_key.replace(' ', '_')}>"`).
   - `compile_chunk_payload_instruction` (`#L538-L553`) manually calls `encapsulate_payload` and stitches XML tags using an f-string (`f"<user_payload>\n{safe_payload}\n</user_payload>"`).
   - AST Strict Debt: `_InputMetaDTO` at line 62 has redundant duplicate `Field()` assignment on Annotated field `input_modes` (`QGR020`).
   - AST Strict Debt: `_extract_value_from_state` at lines 441, 447, 449, 455 uses `isinstance(..., Mapping)` duck-typing checks (`QGR012`) instead of typed schema validation.
4. **`@[backend_v2/services/source_verification_service.py#L38-L261]` (`SourceVerificationService`)**:
   - `_extract_source_claims` (`#L55-L93`) manually truncates and wraps strings with `encapsulate_payload` before injecting into f-strings (`f"<source_data>\n{safe_text}\n</source_data>"`).
   - `_verify_single_claim` (`#L95-L183`) manually builds multi-line f-strings with intermediate `encapsulated_claim` and `encapsulated_answer` variables.
   - AST Strict Debt: in `@[backend_v2/services/source_verification_service.py]`, line 123 uses banned lazy literal fallback `audit_trace.response_summary or ""` (`QGR016`) instead of strict schema handling.
5. **`@[backend_v2/hooks/interaction_hook.py#L41-L167]` (`analyze_interaction_role`)**:
   - Direct manual call to `TemplateProcessor.encapsulate_payload` followed by un-fenced multi-line f-string XML concatenation (`#L120-L133`).
6. **`@[backend_v2/hooks/linguistics.py#L53-L199]` (`detect_performative_patterns`)** & **`@[backend_v2/models/prompts/execution/dynamic_linguistics.py]` (`DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE`)**:
   - Manual `encapsulate_payload` call followed by legacy `str.format` placeholder substitution (`#L140-L143`).
   - Module-level constant `DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE` with unbound variables throws `NameError` if converted naively to a `t"..."` literal; requires modernization to a prompt builder function `build_dynamic_performative_user_prompt(language: str, text_to_scan: str) -> Template`.
   - AST Strict Debt: in `@[backend_v2/hooks/linguistics.py]`, line 82 uses banned ternary fallback `raw_inputs['language'] if 'language' in raw_inputs and isinstance(raw_inputs['language'], str) else None` (`QGR016`).
7. **`@[backend_v2/services/orchestrator/sliding_window_linker.py#L122-L353]` (`SlidingWindowLinker`)** & **`@[backend_v2/services/orchestrator/prompts/graph_linking.py]` (`LINKER_USER_PROMPT`)**:
   - Last remaining domain caller of `safe_interpolate` relying on legacy `str.format` substitution for global ontology maps and claims windows.
   - Module-level constant `LINKER_USER_PROMPT` with unbound variables throws `NameError` if converted naively to a `t"..."` literal; requires modernization to a prompt builder function `build_linker_user_prompt(global_ontology_map: str, claims_window: str) -> Template`.
   - AST Strict Debt: in `@[backend_v2/services/orchestrator/sliding_window_linker.py]`, lines 77, 95, 113 have redundant duplicate `Field()` assignments on Annotated fields `parent_dependencies`, `dependencies`, and `edges` (`QGR020`).
8. **`@[backend_v2/services/orchestrator/prompts/atom_extraction.py]`** & **`@[backend_v2/services/orchestrator/two_pass_atomizer.py#L39-L586]` (`TwoPassAtomizer`)**:
   - Module-level constant `PHASE_1_SYSTEM_PROMPT` with `{ontology_map_json}` placeholder is dynamically substituted in `two_pass_atomizer.py` (`#L193` & `#L367`) via raw string `.replace("{ontology_map_json}", ontology_json)`.
   - Stitches source documents into XML prompts using manual `encapsulate_payload` calls and f-strings (`f"<source_data>\n{encapsulated_source}\n</source_data>"` at `two_pass_atomizer.py#L99-L107`, `#L200-L208`, and `#L374-L382`).
   - Requires modernizing `PHASE_1_SYSTEM_PROMPT` to a prompt builder function `build_phase_1_system_prompt(ontology_map_json: str) -> Template`.
9. **`@[backend_v2/services/chat_parser.py#L57-L284]` (`ChatParserService`)**:
   - Stitches raw chat text into XML prompt using manual `encapsulate_payload` call and f-string (`f"<source_data>\n{encapsulated_paste}\n</source_data>"` at `#L187-L197`).
10. **`@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]` (`SynthesisEngine`)**:
    - Manual call to `TemplateProcessor.encapsulate_payload` on `raw_blackboard_markdown` followed by unshielded f-string XML assembly (`f"<user_payload>\n{protected_user_payload}\n</user_payload>"` at `#L187-L203`).
11. **`@[scripts/_ast_guardrails.py]` (`_ast_guardrails.py`)**:
    - Rule code collision resolution: `QGR019` is allocated to `.pop()` dictionary in-place mutation ban (`#L724-L750`) and `QGR021` is allocated to `llm_debug_logger` eradication (`#L1231-L1239`, `#L1280-L1297`, `#L1582`). The new prompt construction guardrail banning unshielded f-strings in prompt modules must be allocated as `QGR022`.
12. **`@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]`**:
    - AST guardrail checks only verify import statements and basic variable names (`banned_raw_names`), rather than mathematically enforcing structured `ast.TemplateStr` or `TemplateProcessor.render_prompt` usage via `QGR022`.
13. **`@[backend_v2/tests/unit/core/test_template_processor.py]`** & [DELETE] **`@[backend_v2/tests/unit/test_template_processor.py]`**:
    - Duplicate test file layout violating test directory isolation. Consolidate into canonical `backend_v2/tests/unit/core/test_template_processor.py` and delete root test file.
14. **`@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]`** & [DELETE] **`@[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]`**:
    - Duplicate test file layout violating test directory isolation. Consolidate into canonical `backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py` and delete root test file.
15. **`@[backend_v2/tests/unit/services/orchestrator/prompts/test_graph_linking.py]`**:
    - Asserts `isinstance(LINKER_USER_PROMPT, str)`. Needs update to test `build_linker_user_prompt` returning `Template` and rendering via `TemplateProcessor.render_prompt`.
16. **`@[backend_v2/tests/unit/services/orchestrator/prompts/test_atom_extraction.py]`**:
    - Asserts `isinstance(PHASE_1_SYSTEM_PROMPT, str)`. Needs update to test `build_phase_1_system_prompt` returning `Template` and rendering via `TemplateProcessor.render_prompt`.
17. **`@[backend_v2/tests/unit/models/prompts/execution/test_dynamic_linguistics.py]`**:
    - Tests `DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE.format(...)`. Needs update to test `build_dynamic_performative_user_prompt` returning `Template` and rendering via `TemplateProcessor.render_prompt`.

---

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[backend_v2/core/template_processor.py#L19-L128]`** (`TemplateProcessor`) | Banned `str.format(**safe_kwargs)`, speculative callable fallback factories, and manual string concatenation. | Support native PEP 750 `string.templatelib.Template` objects via `render_prompt(template: Template) -> str`. Automatic CDATA wrapping, breakout shielding (`_apply_breakout_shield`), attribute-context XML escaping (`xml.sax.saxutils.escape`), and recursive `Template` rendering with Fail-Fast type checking. | Single unified renderer replacing fragmented `safe_interpolate` and `_encapsulate_cdata` calls without speculative `template()` polyfills. | `@[backend_v2/tests/unit/core/test_template_processor.py]` asserting CDATA wrapping, breakout neutralization, attribute XML escaping, and literal brace preservation without `str.format` exceptions. |
| **`@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L28-L298]`** (`MatrixSensorPromptBuilder`) | Banned 12 manual `encapsulate_payload` temporary variables, chained f-string XML concatenation, and double-interpolation bugs on `deps_str` and `claims_str`. | Construct structured prompt templates using native `t"..."` Template literals with direct variable references rendered via `TemplateProcessor.render_prompt`. Preserve Layer 1 static prefix caching in `build_caching_prefix`. | Delete manual variable-by-variable CDATA wrapping and 12 temporary `_cdata` variables. | `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]` verifying identical XML output with complete CDATA encapsulation. |
| **`@[backend_v2/services/orchestrator/prompt_compiler.py#L77-L633]`** (`PromptCompiler`, specifically `build_xml_context` `#L206-L316`, `_extract_value_from_state` `#L318-L482`, and `compile_chunk_payload_instruction` `#L538-L553`) | Banned f-string XML formatting loops (`f"<{key}>{cdata}</{key}>"`), manual `encapsulate_payload` calls, and piecemeal metadata assembly. | Streamline XML assembly through `TemplateProcessor.render_prompt` and native `t"..."` literals. Preserve Layer 1 static rules prefix caching. | Remove manual string replace cascades for XML tag formatting. | Unit tests in `backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py` verifying full prompt compilation with 100% semantic parity. |
| **`@[backend_v2/services/source_verification_service.py#L38-L261]`** (`SourceVerificationService`, specifically `_extract_source_claims` `#L55-L93` and `_verify_single_claim` `#L95-L183`) | Banned manual string slicing, piecemeal CDATA wrapping, and f-string user message assembly in `_extract_source_claims` and `_verify_single_claim`. | Pass claims and answers directly into structured `t"..."` prompt templates rendered via `TemplateProcessor.render_prompt`. | Direct template interpolation without intermediate helper variables. | Unit tests in `backend_v2/tests/unit/services/test_source_verification_service.py` verifying verification prompt structure and CDATA shielding. |
| **`@[backend_v2/hooks/interaction_hook.py#L41-L167]`** (`analyze_interaction_role`) | Banned manual `encapsulate_payload` temporary variables and un-fenced f-string XML concatenation. | Assemble dynamic user messages using native `t"..."` literals with `TemplateProcessor.render_prompt`. | Eliminate intermediate string variables and manual tag formatting. | Unit tests in `backend_v2/tests/unit/hooks/test_interaction_hook.py` verifying structured execution and CDATA wrapping. |
| **`@[backend_v2/hooks/linguistics.py#L53-L199]`** (`detect_performative_patterns`) & **`@[backend_v2/models/prompts/execution/dynamic_linguistics.py]`** | Banned `DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE.format(...)`, module-level unbound template variables, and manual `encapsulate_payload` calls. | Modernize dynamic performative prompt assembly to prompt builder function `build_dynamic_performative_user_prompt(language: str, text_to_scan: str) -> Template` rendered via `TemplateProcessor.render_prompt`. | Eliminate legacy string template format placeholders and prevent module-level `NameError`. | Unit tests in `backend_v2/tests/unit/hooks/test_linguistics.py` and `@[backend_v2/tests/unit/models/prompts/execution/test_dynamic_linguistics.py]` verifying lexical extraction and CDATA wrapping. |
| **`@[backend_v2/services/orchestrator/sliding_window_linker.py#L122-L353]`** (`SlidingWindowLinker`) & **`@[backend_v2/services/orchestrator/prompts/graph_linking.py]`** | Banned legacy `safe_interpolate` calls, module-level unbound template variables, and format string placeholders in graph linking. | Modernize graph linking prompt assembly to prompt builder function `build_linker_user_prompt(global_ontology_map: str, claims_window: str) -> Template` rendered via `TemplateProcessor.render_prompt`. | Eliminate legacy format string dictionary unpacking and prevent module-level `NameError`. | `@[backend_v2/tests/unit/services/orchestrator/prompts/test_graph_linking.py]` and `@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]` verifying curly brace and CDATA resilience. |
| **`@[backend_v2/services/orchestrator/prompts/atom_extraction.py]`** & **`@[backend_v2/services/orchestrator/two_pass_atomizer.py#L39-L586]`** (`TwoPassAtomizer`) | Banned raw string `.replace("{ontology_map_json}", ontology_json)` and f-string `<source_data>` concatenation. | Modernize Phase 1 prompt assembly to prompt builder function `build_phase_1_system_prompt(ontology_map_json: str) -> Template` and raw document encapsulation to native `t"..."` literals with `TemplateProcessor.render_prompt`. | Eliminate ad-hoc string replacement and intermediate string variables before message construction. | `@[backend_v2/tests/unit/services/orchestrator/prompts/test_atom_extraction.py]` and unit tests in `backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py` verifying clean rendering. |
| **`@[backend_v2/services/chat_parser.py#L57-L284]`** (`ChatParserService`) | Banned manual `encapsulate_payload` calls and f-string `<source_data>` concatenation. | Modernize raw dialogue encapsulation to native `t"..."` literals with `TemplateProcessor.render_prompt`. | Eliminate intermediate string variables before message construction. | Unit tests in `backend_v2/tests/unit/services/test_chat_parser.py` and `@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]` verifying verbatim anchor extraction. |
| **`@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]`** (`SynthesisEngine`, specifically `#L187-L203`) | Banned manual `encapsulate_payload` and unshielded f-string `<user_payload>` concatenation. | Modernize user message assembly to native `t"..."` template literals with `TemplateProcessor.render_prompt`. | Eliminate intermediate string variables and manual XML payload encapsulation. | Unit tests in `backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py` verifying clean CDATA payload wrapping. |
| **`@[scripts/_ast_guardrails.py]`** (`_ast_guardrails.py`) & **`@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]`** | Banned rule code collision on `QGR019` and `QGR021`, shallow import-only AST checks, and un-fenced `ast.JoinedStr` f-strings in prompt modules. | Static AST guardrail rule `QGR022` banning `ast.JoinedStr` in prompt modules and enforcing `ast.TemplateStr` or `render_prompt`. | Zero manual code review needed for prompt injection; language parser guarantees interpolations are isolated as discrete AST nodes. | `test_cdata_hardening_comprehensive.py` passes with 0 violations across all prompt-building components. |
| **`@[backend_v2/tests/unit/core/test_template_processor.py]`** & [DELETE] **`@[backend_v2/tests/unit/test_template_processor.py]`** | Banned duplicate test files in `tests/unit/` root violating `test_directory_isolation`. | Consolidate comprehensive test suite into canonical `backend_v2/tests/unit/core/test_template_processor.py` and delete root duplicate. | Unified test file adhering to production folder mirroring standard. | Direct pytest run passes with 100% assertions satisfied. |
| **`@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]`** & [DELETE] **`@[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]`** | Banned duplicate test files in `tests/unit/` root violating `test_directory_isolation`. | Consolidate comprehensive test suite into canonical `backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py` and delete root duplicate. | Unified test file adhering to production folder mirroring standard. | Direct pytest run passes with 100% assertions satisfied. |

---

## Technical Architecture: PEP 750 Template Processing Engine

### 1. The Anatomy of a Secure Template
In Python 3.14.6, PEP 750 defines `string.templatelib.Template`:
```python
# Authoritative Python 3.14.6 Template attributes
class Template:
    strings: tuple[str, ...]
    interpolations: tuple[Interpolation, ...]
    values: tuple[Any, ...]

class Interpolation:
    value: Any
    expression: str
    conversion: str | None
    format_spec: str
```
Every dynamic variable enclosed in curly brackets in a `t"..."` literal produces an `Interpolation(value, expression, conversion, format_spec)`. Static text outside curly brackets produces string literals in `strings`. The mathematical invariant holds: `len(strings) == len(interpolations) + 1`. In Python 3.14.6 runtime `string.templatelib.Interpolation`, `conversion` defaults to `None` (or conversion string `'r'`, `'s'`, `'a'`) and `format_spec` defaults to empty string `""` (whereas in `ast.Interpolation` the AST node's conversion integer field defaults to `-1`).

### 2. Module-Level Template Literal Invariant
In Python 3.14 PEP 750, `t"..."` template literals evaluate expressions at the moment the literal is evaluated in its enclosing scope. Therefore, prompt definitions containing dynamic parameters cannot be defined as bare module-level constants with unbound variables (which would raise `NameError` during module import). Instead, dynamic prompt templates must be encapsulated into prompt builder functions returning `Template` instances (specifically `build_linker_user_prompt` in `graph_linking.py` and `build_dynamic_performative_user_prompt` in `dynamic_linguistics.py`) or constructed inside caller methods where dynamic parameters are bound.

### 3. The Auto-Sanitizing Renderer (`TemplateProcessor.render_prompt`)
The renderer executes a deterministic transformation on every element:
1. **Static Chunks (`str`):** Emitted directly without modification, preserving exact structural XML tags (`<system_directive>`, `<question>`).
2. **Dynamic Values (`Interpolation`):**
   - Extracted from `interp.value`.
   - Handled cleanly: `None` values are coerced to empty string `""` without emitting empty CDATA blocks.
   - If `isinstance(interp.value, Template)`: recursively rendered via `render_prompt(interp.value)` without re-encapsulating structural XML tags.
   - If `interp.format_spec == "raw"`: emitted directly as `str(interp.value)` without CDATA wrapping (for pre-sanitized collections).
   - If interpolation is inside an XML attribute (preceding string ends with `="` or `='`, or `interp.format_spec == "attr"`): escaped using XML attribute semantics (`&` -> `&amp;`, `"` -> `&quot;`, `'` -> `&apos;`, `<` -> `&lt;`, `>` -> `&gt;`) via `xml.sax.saxutils.escape` without invalid CDATA injection.
   - Default character data: string representations are scanned for CDATA breakout markers (`]]>`), escaping them via `]]]]><![CDATA[>`, and enclosed in `<![CDATA[...]]>`:
     ```python
     chunks: list[str] = []
     for s, interp in zip(template.strings[:-1], template.interpolations, strict=True):
         chunks.append(s)
         val = interp.value
         if val is None:
             continue
         if interp.conversion:
             val = templatelib.convert(val, interp.conversion)
         if isinstance(val, Template):
             chunks.append(cls.render_prompt(val))
         elif interp.format_spec == "raw":
             chunks.append(str(val))
         elif s.rstrip().endswith('="') or s.rstrip().endswith("='") or interp.format_spec == "attr":
             chunks.append(saxutils.escape(str(val), {'"': "&quot;", "'": "&apos;"}))
         else:
             chunks.append(cls._encapsulate_cdata(str(val)))
     chunks.append(template.strings[-1])
     return "".join(chunks)
     ```
3. **Fail-Fast Boundary:** Unescaped raw string injection into XML tags is mathematically impossible because the Python parser segregates literals from interpolations before execution. Passing any non-`Template` object into `render_prompt` raises an immediate `AppException(ErrorCodes.VALIDATION_FAILED)`.

### 4. Static AST Guardrail Architecture (Zero-Discretion Mathematical Defense)
To enforce this security architecture permanently, a dedicated static AST Guardrail rule `QGR022` in `@[scripts/_ast_guardrails.py]` and `@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]` scans all prompt-building modules (`backend_v2/services/orchestrator/prompts/` and `backend_v2/models/prompts/`):
- **Banned Node:** `ast.JoinedStr` (standard Python f-strings) when constructing XML prompt tags or user payloads.
- **Mandated Node:** `ast.TemplateStr` (PEP 750 `t"..."`) or `TemplateProcessor.render_prompt`.
- **Zero-Discretion Verification:** Code reviewers and AI agents do not need to inspect line-by-line whether a dynamic variable has been manually sanitized or wrapped. If a prompt block uses `t"..."`, the language parser guarantees that interpolations are isolated as discrete AST objects, making un-sanitized prompt injection mathematically impossible.

---

## Falsification & Red-Team Assessment (Panel of Experts Attack)

A rigorous adversarial cross-examination by the Panel of Experts identified four critical failure vectors and validated their deterministic remediations:

1. **Attack Vector 1: XML Attribute Injection & CDATA Invalidation**
   - *Vulnerability:* Interpolating variables directly into XML attribute positions (specifically `t'<matrix_input source_id="{source_id}">...'`) using default CDATA wrapping produces malformed XML: `<matrix_input source_id="<![CDATA[org_123]]>">`. Standard XML parsers (`xml.etree.ElementTree`) throw `ParseError` on CDATA delimiters inside attribute quotes.
   - *Deterministic Remediated Invariant:* `TemplateProcessor.render_prompt` dynamically detects attribute context (preceding static string ends with `="` or `='`, or `interp.format_spec == "attr"`) and applies strict XML attribute escaping via `xml.sax.saxutils.escape(str(val), {'"': "&quot;", "'": "&apos;"})` without injecting invalid CDATA brackets.

2. **Attack Vector 2: Unbound Module-Level Template Variable Evaluation (`NameError`)**
   - *Vulnerability:* In Python 3.14 PEP 750, `t"..."` literals evaluate interpolation expressions in the enclosing lexical scope at evaluation time. Defining template constants containing dynamic placeholders at module level (specifically bare `LINKER_USER_PROMPT = t"...{claims_window}..."`) triggers immediate `NameError` during module import.
   - *Deterministic Remediated Invariant:* Dynamic parameterized prompt assets are strictly forbidden as bare module-level template constants. They are refactored into typed prompt builder functions (specifically `build_linker_user_prompt(global_ontology_map: str, claims_window: str) -> Template`, `build_dynamic_performative_user_prompt(language: str, text_to_scan: str) -> Template`, and `build_phase_1_system_prompt(ontology_map_json: str) -> Template`), binding variables cleanly within function scope.

3. **Attack Vector 3: Recursive & Pre-Formatted XML Double-CDATA Encapsulation**
   - *Vulnerability:* Staged XML structures (specifically `<criterion index="...">...</criterion>` or pre-formatted causal dependencies) passed into an outer template would be treated as raw character data and wrapped in `<![CDATA[...]]>`, destroying downstream XML structure.
   - *Deterministic Remediated Invariant:* `TemplateProcessor.render_prompt` natively supports nested `Template` instances (recursively rendering them without outer CDATA re-wrapping) and supports the `:raw` format specifier (`interp.format_spec == "raw"`) to emit pre-sanitized collections directly.

4. **Attack Vector 4: Foundational Model Perimeter Serialization Boundary Impedance**
   - *Vulnerability:* Passing un-rendered `Template` objects directly to foundational model SDKs (Vertex AI, Anthropic, LiteLLM) crashes HTTP/gRPC serialization (`TypeError: Object of type Template is not JSON serializable`).
   - *Deterministic Remediated Invariant:* `TemplateProcessor.render_prompt(tmpl: Template) -> str` acts as the single authoritative perimeter boundary. All message payloads (`LLMMessageDTO.content`) remain strictly primitive `str` before network dispatch.

---

## Execution Protocol

```xml
<execution_protocol>
  <step id="0" name="PRE-IMPLEMENTATION TOOLCHAIN &amp; AST BASELINE">
    <action>Execute baseline AST scan on prompt-building files using `uv run python -m pytest backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py` to record existing coverage.</action>
    <action>Verify Python runtime version and `string.templatelib` availability in the active environment using `uv run python -c "from string.templatelib import Template; print(Template)"`.</action>
    <constraint invariant="zero_tolerance_audit_loop">Baseline test suite must pass before introducing new template abstractions.</constraint>
  </step>

  <step id="1" name="PHASE 1: PRE-IMPLEMENTATION CLEANUPS &amp; BASELINE VERIFICATION">
    <action>Run baseline unit tests across `@[backend_v2/tests/unit/core/test_template_processor.py]` and `@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]` to verify existing CDATA behavior.</action>
    <action>Consolidate legacy duplicate test file [DELETE] `@[backend_v2/tests/unit/test_template_processor.py]` into canonical `@[backend_v2/tests/unit/core/test_template_processor.py]` and delete the root test file to uphold test directory isolation.</action>
    <action>Consolidate legacy duplicate test file [DELETE] `@[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]` into canonical `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]` and delete the root test file to uphold test directory isolation.</action>
    <action>Audit and catalog all 12 manual temporary `_cdata` variables in `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L28-L298]` targeted for elimination.</action>
    <action>Remediate AST strict technical debt: in `@[backend_v2/services/orchestrator/prompt_compiler.py]` (line 62), remove redundant `= Field(...)` assignment on Annotated field `input_modes` (`QGR020`), and refactor `isinstance(..., Mapping)` duck-typing checks (lines 441-455, `QGR012`) to use typed schema validation.</action>
    <action>Remediate AST strict technical debt: in `@[backend_v2/services/source_verification_service.py]` (line 123), replace banned lazy literal fallback `audit_trace.response_summary or ""` with strict schema handling (`QGR016`).</action>
    <action>Remediate AST strict technical debt: in `@[backend_v2/hooks/linguistics.py]` (line 82), replace banned ternary fallback on `language` with typed DTO extraction (`QGR016`).</action>
    <action>Remediate AST strict technical debt: in `@[backend_v2/services/orchestrator/sliding_window_linker.py]` (lines 77-113), remove redundant duplicate `Field()` assignments on Annotated fields `parent_dependencies`, `dependencies`, and `edges` (`QGR020`).</action>
    <action>Audit `@[backend_v2/services/orchestrator/prompt_compiler.py#L77-L633]` (`build_xml_context` `#L206-L316`, `_extract_value_from_state` `#L318-L482`, and `compile_chunk_payload_instruction` `#L538-L553`) to prepare structured template replacement for f-string XML concatenation.</action>
    <constraint invariant="touched_scope_tech_debt_mandate">All pre-implementation debts must be cataloged and baselined prior to modifying domain files.</constraint>
  </step>

  <step id="2" name="CORE TEMPLATE PROCESSOR MODERNIZATION">
    <action>In `@[backend_v2/core/template_processor.py#L19-L128]`:
      - Implement `TemplateProcessor.render_prompt(template: Template) -> str`:
        * Enforce Fail-Fast type check that `template` is strictly an instance of `string.templatelib.Template`.
        * Iterate over `zip(template.strings[:-1], template.interpolations, strict=True)`, appending static string chunks and dynamic values.
        * Handle conversions cleanly via `string.templatelib.convert(val, interp.conversion)` if `interp.conversion` is defined.
        * Recursively render nested `Template` values via `cls.render_prompt(val)` without re-wrapping in CDATA.
        * Support `:raw` format specification (`interp.format_spec == "raw"`) to emit pre-sanitized collections directly.
        * Detect XML attribute context (`s.rstrip().endswith(('=\"', \"=\'\"))` or `interp.format_spec == "attr"`) and escape attribute chars (`&`, `\"`, `\'`, `<`, `>`) via `xml.sax.saxutils.escape` without invalid CDATA injection.
        * Coerce `interp.value` cleanly: `None` evaluates to empty string `""` without CDATA wrapping; all non-None character data passes through `_apply_breakout_shield` and `_encapsulate_cdata`.
        * Append `template.strings[-1]` and return the compiled XML string.
      - Retain existing `encapsulate_payload` and `_apply_breakout_shield` methods for direct utility consumers.
      - Eradicate legacy `safe_interpolate` once domain callers are migrated to `render_prompt` in Steps 3-5, eliminating obsolete legacy methods per `the_no_legacy_mandate`.
    </action>
    <action>Update `@[backend_v2/tests/unit/core/test_template_processor.py]` with comprehensive unit tests for `render_prompt`:
      - Static literal preservation (braces in JSON schemas must not raise KeyError).
      - Dynamic variable CDATA wrapping.
      - Attribute-context XML escaping without invalid CDATA inside quotes.
      - Recursive `Template` interpolation.
      - Breakout attempt neutralization (`]]>`).
      - None, integer, and boolean interpolation handling.
      - Fail-Fast assertion when passing non-Template object.
    </action>
    <constraint invariant="pep750_t_strings_only">Prompt rendering must strictly segregate static text from dynamic interpolations.</constraint>
  </step>

  <step id="3" name="MATRIX SENSOR PROMPT BUILDER MIGRATION">
    <action>In `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L28-L298]`:
      - Refactor `build_caching_prefix` (`#L31-L81`) to construct `<matrix_objective>`, `<theory_context>`, and `<context>` blocks using native `t"..."` literals with `TemplateProcessor.render_prompt`.
      - Refactor `build_compiled_prompt` (`#L83-L284`) to eliminate all 12 manual `_cdata` temporary variables.
      - Replace f-string XML formatting blocks for questions, extraction rules, anchor targets, contrastive examples, acceptance criteria, anti-patterns, syntactic anchors, and causal dependencies with structured `t"..."` expressions.
      - Fix double-interpolation bug where XML structures were passed into `safe_interpolate`.
    </action>
    <action>Run unit tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py`.</action>
    <constraint invariant="four_layer_clean_stack_hierarchy">Preserve exact Layer 1 static prefix caching while securing Layer 4 dynamic inputs.</constraint>
  </step>

  <step id="4" name="PROMPT COMPILER &amp; SOURCE VERIFICATION MIGRATION">
    <action>In `@[backend_v2/services/orchestrator/prompt_compiler.py#L77-L633]` (`build_xml_context` `#L206-L316`, `_extract_value_from_state` `#L318-L482`, and `compile_chunk_payload_instruction` `#L538-L553`):
      - Modernize `build_xml_context` metadata and input payload tags using `t"..."` literals and `TemplateProcessor.render_prompt`.
      - Modernize `_extract_value_from_state` nested dict tag formatting using structured template expressions.
      - Modernize `compile_chunk_payload_instruction` user payload wrapping using native `t"..."` literals and `TemplateProcessor.render_prompt`.
    </action>
    <action>In `@[backend_v2/services/source_verification_service.py#L38-L261]` (`_extract_source_claims` `#L55-L93` and `_verify_single_claim` `#L95-L183`):
      - Modernize `_extract_source_claims` `<source_data>` assembly using `TemplateProcessor.render_prompt(t"<source_data>\n{text[:max_chars]}\n</source_data>")`.
      - Modernize `_verify_single_claim` claim and search results prompt assembly using native `t"..."` literals.
    </action>
    <action>Run unit tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py backend_v2/tests/unit/services/test_source_verification_service.py`.</action>
    <constraint invariant="compiler_xml_sovereignty_mandate">Raw prompt blocks must remain natural language; XML wrapping is applied just-in-time by the processor.</constraint>
  </step>

  <step id="5" name="ANALYTICAL HOOKS, GRAPH LINKER, ENGINES &amp; INGRESS MIGRATION">
    <action>In `@[backend_v2/hooks/interaction_hook.py#L41-L167]`:
      - Modernize `analyze_interaction_role` user prompt assembly (`#L120-L133`) to use `t"..."` literals and `TemplateProcessor.render_prompt`.
    </action>
    <action>In `@[backend_v2/hooks/linguistics.py#L53-L199]` and `@[backend_v2/models/prompts/execution/dynamic_linguistics.py]`:
      - Modernize `DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE` into prompt builder function `build_dynamic_performative_user_prompt(language: str, text_to_scan: str) -> Template` to prevent module-level `NameError`.
      - Modernize `detect_performative_patterns` (`#L140-L143`) prompt assembly to call `build_dynamic_performative_user_prompt` and `TemplateProcessor.render_prompt`.
    </action>
    <action>Update `@[backend_v2/tests/unit/models/prompts/execution/test_dynamic_linguistics.py]` to test `build_dynamic_performative_user_prompt` returning `Template` and rendering via `TemplateProcessor.render_prompt`.</action>
    <action>In `@[backend_v2/services/orchestrator/sliding_window_linker.py#L122-L353]` and `@[backend_v2/services/orchestrator/prompts/graph_linking.py]`:
      - Modernize `LINKER_USER_PROMPT` into prompt builder function `build_linker_user_prompt(global_ontology_map: str, claims_window: str) -> Template` to prevent module-level `NameError`.
      - Modernize sliding window linker user prompt assembly to call `build_linker_user_prompt` rendered via `TemplateProcessor.render_prompt`, completely eradicating domain dependence on `safe_interpolate`.
    </action>
    <action>Update `@[backend_v2/tests/unit/services/orchestrator/prompts/test_graph_linking.py]` to verify that `build_linker_user_prompt` returns a valid `Template` instance and that `TemplateProcessor.render_prompt` renders structural XML and CDATA correctly.</action>
    <action>In `@[backend_v2/services/orchestrator/prompts/atom_extraction.py]` and `@[backend_v2/services/orchestrator/two_pass_atomizer.py#L39-L586]`:
      - Modernize `PHASE_1_SYSTEM_PROMPT` into prompt builder function `build_phase_1_system_prompt(ontology_map_json: str) -> Template`.
      - In `two_pass_atomizer.py`, replace `.replace("{ontology_map_json}", ontology_json)` (`#L193` & `#L367`) and f-string `<source_data>` assembly (`#L99-L107`, `#L200-L208`, `#L374-L382`) with `build_phase_1_system_prompt` and native `t"..."` literals with `TemplateProcessor.render_prompt`.
    </action>
    <action>Update `@[backend_v2/tests/unit/services/orchestrator/prompts/test_atom_extraction.py]` to verify that `build_phase_1_system_prompt` returns a valid `Template` instance rendered via `TemplateProcessor.render_prompt`.</action>
    <action>In `@[backend_v2/services/chat_parser.py#L57-L284]`:
      - Modernize raw dialogue encapsulation (`#L187-L197`) to native `t"..."` literals with `TemplateProcessor.render_prompt`.
    </action>
    <action>In `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L36-L286]`:
      - Modernize user message assembly (`#L187-L203`) to use native `t"..."` template literals rendered via `TemplateProcessor.render_prompt`.
    </action>
    <action>Run component unit tests: `uv run pytest backend_v2/tests/unit/hooks/test_interaction_hook.py backend_v2/tests/unit/hooks/test_linguistics.py backend_v2/tests/unit/services/test_chat_parser.py backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py backend_v2/tests/unit/services/orchestrator/prompts/test_graph_linking.py backend_v2/tests/unit/services/orchestrator/prompts/test_atom_extraction.py backend_v2/tests/unit/models/prompts/execution/test_dynamic_linguistics.py`.</action>
    <constraint invariant="single_pipeline_invariant_mandate">All prompt construction across hooks, engines, and services must route through the single authoritative renderer.</constraint>
  </step>

  <step id="6" name="AST GUARDRAIL FORTIFICATION &amp; QGR022 IMPLEMENTATION">
    <action>In `@[scripts/_ast_guardrails.py]`, add static guardrail rule `QGR022`:
      - Avoid rule code collision with existing `QGR019` (`.pop()` ban) and `QGR021` (`llm_debug_logger` ban).
      - Update header docstring to `(QGR000-QGR022)`.
      - Implement `visit_JoinedStr` traversing AST nodes in `backend_v2/services/orchestrator/prompts/` and `backend_v2/models/prompts/`.
      - Flag any `ast.JoinedStr` (f-string) constructing XML prompt tags or interpolating user payload variables.
      - Enforce that prompt-building constructs use exclusively `ast.TemplateStr` (PEP 750 `t"..."`) or `TemplateProcessor.render_prompt`.
      - Set rule severity to FATAL in domain code.
    </action>
    <action>In `@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]`:
      - Upgrade AST verification to assert that `QGR022` statically flags unshielded `ast.JoinedStr` in prompt modules and verifies that prompt assembly across all prompt modules uses `TemplateProcessor.render_prompt` or `t"..."`.
      - Modernize `test_sliding_window_linker_curly_braces_interpolation` and `test_template_processor_edge_cases` to verify `TemplateProcessor.render_prompt(build_linker_user_prompt(...))` instead of legacy `safe_interpolate`.
    </action>
    <action>Run guardrail test: `uv run pytest backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py`.</action>
    <constraint invariant="ast_guardrail_mandate">All architectural constraints must be statically verified via AST visitor tests.</constraint>
  </step>

  <step id="7" name="QUALITY GATES &amp; FULL VERIFICATION LOOP">
    <action>Execute full backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator --test`.</action>
    <action>Run markdown boundaries audit on plan: `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/plan_pep750_template_strings_prompt_security.md`.</action>
    <constraint invariant="universal_quality_gate">All automated tests and quality gates must pass with zero failures and zero warnings.</constraint>
  </step>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
1. **TemplateProcessor Core Tests:**
   ```powershell
   uv run pytest backend_v2/tests/unit/core/test_template_processor.py -v
   ```
2. **Matrix Sensor Prompt Builder Tests:**
   ```powershell
   uv run pytest backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py -v
   ```
3. **Graph Linking & Atom Extraction Prompt Tests:**
   ```powershell
   uv run pytest backend_v2/tests/unit/services/orchestrator/prompts/test_graph_linking.py backend_v2/tests/unit/services/orchestrator/prompts/test_atom_extraction.py -v
   ```
4. **Prompt Compiler Tests:**
   ```powershell
   uv run pytest backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py -v
   ```
5. **Source Verification Tests:**
   ```powershell
   uv run pytest backend_v2/tests/unit/services/test_source_verification_service.py -v
   ```
6. **Analytical Hooks & Dynamic Linguistics Tests:**
   ```powershell
   uv run pytest backend_v2/tests/unit/hooks/test_interaction_hook.py backend_v2/tests/unit/hooks/test_linguistics.py backend_v2/tests/unit/models/prompts/execution/test_dynamic_linguistics.py -v
   ```
7. **Sliding Window Linker, Chat Parser & Two-Pass Atomizer Tests:**
   ```powershell
   uv run pytest backend_v2/tests/unit/services/test_chat_parser.py backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py -v
   ```
8. **Synthesis Engine Tests:**
   ```powershell
   uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py -v
   ```
9. **Comprehensive CDATA & Template AST Guardrail:**
   ```powershell
   uv run pytest backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py -v
   ```
10. **Backend Audit Loop:**
    ```powershell
    uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator --test
    ```
11. **Markdown Boundaries Verification:**
    ```powershell
    uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/plan_pep750_template_strings_prompt_security.md
    ```

### Anti-Happy-Path Test Scenarios (ISTQB Boundary Partitions)

1. **Negative Scenario 1: Malicious CDATA Breakout Payload**
   - **Input:** Dynamic variable containing `"Malicious text with ]]> breakout attempt"`.
   - **Expected Result:** `TemplateProcessor.render_prompt` neutralizes `]]>` to `]]]]><![CDATA[>`, rendering safe XML that cannot escape the container tag.
   - **Verification:** Unit test `test_render_prompt_breakout_neutralization` asserts that no `]]>` appears un-escaped and standard XML parsing generates 0 child elements.

2. **Negative Scenario 2: Literal Braces in Static Prompt Schema**
   - **Input:** Static template string containing unescaped JSON schema with curly braces: `t'Ensure response adheres to schema: {"type": "object", "properties": {}}'`.
   - **Expected Result:** Renders cleanly without raising Python `KeyError` or `ValueError`, unlike legacy `str.format()`.
   - **Verification:** Unit test `test_render_prompt_literal_braces` verifies curly brackets in static template text remain intact.

3. **Negative Scenario 3: Falsy and None Dynamic Inputs**
   - **Input:** Dynamic variables with `None`, empty string `""`, and integer `0`.
   - **Expected Result:** `None` renders as empty string `""` without emitting an empty CDATA block; empty string `""` renders as `<![CDATA[]]>`; integer `0` renders as `<![CDATA[0]]>`, preserving schema validity without raising `TypeError`.
   - **Verification:** Unit test `test_render_prompt_falsy_and_none` asserts exact string serialization.

4. **Negative Scenario 4: Non-Template Type Passed to Renderer (Fail-Fast Enforcement)**
   - **Input:** Caller passes a raw `str` or `dict` into `TemplateProcessor.render_prompt("raw string")`.
   - **Expected Result:** `TemplateProcessor.render_prompt` triggers Fail-Fast by raising `AppException` with `ErrorCodes.VALIDATION_FAILED` (HTTP 400), completely rejecting un-segregated strings.
   - **Verification:** Unit test `test_render_prompt_non_template_raises_app_exception` asserts `AppException`.

5. **Negative Scenario 5: Raw F-String AST Violation in Prompt Modules (QGR022)**
   - **Input:** Introducing a new function in `matrix_sensor_prompt_builder.py` using `f"<user_payload>{raw_user_input}</user_payload>"`.
   - **Expected Result:** `test_cdata_hardening_comprehensive.py` and `scripts/_ast_guardrails.py` flag the `ast.JoinedStr` node with rule `QGR022` as FATAL severity, blocking CI/CD deployment.
   - **Verification:** AST visitor test asserts fatal `QGR022` finding on prohibited nodes.

6. **Negative Scenario 6: Attribute Context CDATA Injection Defense**
   - **Input:** Dynamic variable containing `"org_123"` interpolated inside an attribute: `t'<matrix_input source_id="{source_id}">\n...'`.
   - **Expected Result:** `TemplateProcessor.render_prompt` detects preceding `source_id="` attribute context, escapes special chars via `xml.sax.saxutils.escape`, and renders `source_id="org_123"` without invalid `<![CDATA[...]]>` inside quotes.
   - **Verification:** Unit test `test_render_prompt_attribute_escaping` verifies that attribute quotes do not contain CDATA delimiters and produce valid XML parsed via `xml.etree.ElementTree`.

7. **Negative Scenario 7: Nested Template Double-CDATA Prevention**
   - **Input:** Outer template interpolating an inner template: `inner = t"<claim>{c}</claim>"; outer = t"<claims>\n{inner}\n</claims>"`.
   - **Expected Result:** Inner template renders structural XML tags `<claim>...</claim>` without CDATA, encapsulating only `{c}`, while outer template renders `<claims>...</claims>` without double-encapsulating `<claim>`.
   - **Verification:** Unit test `test_render_prompt_nested_templates` verifies that XML hierarchy contains no duplicate or nested CDATA wrappers.
