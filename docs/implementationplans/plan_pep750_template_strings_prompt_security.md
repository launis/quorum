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

## Touched Scope Technical Debt & Anti-Pattern Sweep

An exhaustive AST and ripgrep scan of `backend_v2` identified the following technical debt items across prompt compilation targets and 1-hop callers:

1. **`@[backend_v2/core/template_processor.py#L10-L73]` (`TemplateProcessor`)**:
   - Legacy `safe_interpolate` relies on `str.format(**safe_kwargs)`, which fails with `KeyError` or `ValueError` whenever prompt templates contain literal curly brackets in JSON schemas or code examples.
   - Lacks native support for Python 3.14 `string.templatelib.Template` objects.
   - Forces callers to manually call `encapsulate_payload` before stitching strings together.
2. **`@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L28-L284]` (`MatrixSensorPromptBuilder`)**:
   - Repetitive, manual `TemplateProcessor.encapsulate_payload` calls on 12+ individual assertion fields (`assertion.question`, `assertion.extraction_rule`, `assertion.anchor_target`, `assertion.contrastive_example`, `assertion.target_speaker`, `dep.edge_reasoning`).
   - Stitches XML tags using standard f-strings (`f"<question>\n{q_cdata}\n</question>\n"`), creating opportunities for accidental omission of sanitization.
   - Double CDATA encapsulation bug: passes pre-formatted XML strings (`deps_str`, `claims_str`) into `TemplateProcessor.safe_interpolate`, which re-wraps structural tags inside CDATA.
3. **`@[backend_v2/services/orchestrator/prompt_compiler.py#L79-L606]` (`PromptCompiler`)**:
   - `build_xml_context` (`#L206-L316`) stitches metadata and input tags using piecemeal f-strings (`f"<matrix_input source_id=\"{source_id_to_use}\">\n{desc_text}{wrapped_val}\n</matrix_input>"`).
   - `_extract_value_from_state` (`#L318-L482`) uses f-strings to assemble dynamic input blocks (`f"  <{clean_key.replace(' ', '_')}>{TemplateProcessor.encapsulate_payload(micro_v)}</{clean_key.replace(' ', '_')}>"`).
4. **`@[backend_v2/services/source_verification_service.py#L38-L261]` (`SourceVerificationService`)**:
   - `_extract_source_claims` (`#L55-L93`) manually truncates and wraps strings with `encapsulate_payload` before injecting into f-strings (`f"<source_data>\n{safe_text}\n</source_data>"`).
   - `_verify_single_claim` (`#L95-L183`) manually builds multi-line f-strings with intermediate `encapsulated_claim` and `encapsulated_answer` variables.
5. **`@[backend_v2/hooks/interaction_hook.py#L41-L163]` (`analyze_interaction_role`)**:
   - Direct manual call to `TemplateProcessor.encapsulate_payload` followed by un-fenced multi-line f-string XML concatenation (`#L120-L133`).
6. **`@[backend_v2/hooks/linguistics.py#L53-L198]` (`detect_performative_patterns`)**:
   - Manual `encapsulate_payload` call followed by `str.format` substitution (`#L140-L143`).
7. **`@[scripts/_ast_guardrails.py]` (`_ast_guardrails.py`)**:
   - Rule code collision: existing plan proposed `QGR019`, which is already assigned to `.pop()` dictionary in-place mutation ban (`#L722-L748`). The new prompt construction guardrail must be allocated as `QGR021`.
8. **`@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]`**:
   - AST guardrail checks only verify import statements and basic variable names (`banned_raw_names`), rather than mathematically enforcing structured `ast.TemplateStr` or `TemplateProcessor.render_prompt` usage.

---

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[backend_v2/core/template_processor.py#L10-L73]`** (`TemplateProcessor`) | Banned `str.format(**safe_kwargs)`, speculative callable fallback factories, and manual string concatenation. | Support native PEP 750 `string.templatelib.Template` objects via `render_prompt(template: Template) -> str`. Automatic CDATA wrapping and breakout shielding on all `Interpolation` values with Fail-Fast type checking. | Single unified renderer replacing fragmented `safe_interpolate` and `_encapsulate_cdata` calls without speculative `template()` polyfills. | `@[backend_v2/tests/unit/test_template_processor.py#L10-L48]` asserting CDATA wrapping, breakout neutralization, and literal brace preservation without `str.format` exceptions. |
| **`@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L28-L284]`** (`MatrixSensorPromptBuilder`) | Banned 12 manual `encapsulate_payload` temporary variables, chained f-string XML concatenation, and double-interpolation bugs on `deps_str`. | Construct structured prompt templates using native `t"..."` Template literals with direct variable references rendered via `TemplateProcessor.render_prompt`. | Delete manual variable-by-variable CDATA wrapping and 12 temporary `_cdata` variables. | `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]` verifying identical XML output with complete CDATA encapsulation. |
| **`@[backend_v2/services/orchestrator/prompt_compiler.py#L79-L606]`** (`PromptCompiler`) | Banned f-string XML formatting loops (`f"<{key}>{cdata}</{key}>"`) and piecemeal metadata assembly in `build_xml_context` and `_extract_value_from_state`. | Streamline XML assembly through `TemplateProcessor.render_prompt` and native `t"..."` literals. Preserve Layer 1 static rules prefix caching. | Remove manual string replace cascades for XML tag formatting. | Unit tests in `test_prompt_compiler.py` verifying full prompt compilation with 100% semantic parity. |
| **`@[backend_v2/services/source_verification_service.py#L38-L261]`** (`SourceVerificationService`) | Banned manual string slicing, piecemeal CDATA wrapping, and f-string user message assembly in `_extract_source_claims` and `_verify_single_claim`. | Pass claims and answers directly into structured `t"..."` prompt templates rendered via `TemplateProcessor.render_prompt`. | Direct template interpolation without intermediate helper variables. | Unit tests in `test_source_verification_service.py` verifying verification prompt structure and CDATA shielding. |
| **`@[backend_v2/hooks/interaction_hook.py#L41-L163]`** (`analyze_interaction_role`) | Banned manual `encapsulate_payload` temporary variables and un-fenced f-string XML concatenation. | Assemble dynamic user messages using native `t"..."` literals with `TemplateProcessor.render_prompt`. | Eliminate intermediate string variables and manual tag formatting. | Unit tests in `test_interaction_hook.py` verifying structured execution and CDATA wrapping. |
| **`@[backend_v2/hooks/linguistics.py#L53-L198]`** (`detect_performative_patterns`) | Banned `DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE.format(...)` and manual `encapsulate_payload` calls. | Modernize dynamic performative prompt assembly to native `t"..."` template rendered via `TemplateProcessor.render_prompt`. | Eliminate legacy string template format placeholders. | Unit tests in `test_linguistics.py` verifying lexical extraction and CDATA wrapping. |
| **`@[scripts/_ast_guardrails.py]`** (`_ast_guardrails.py`) & **`@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]`** | Banned rule code collision on `QGR019`, shallow import-only AST checks, and un-fenced `ast.JoinedStr` f-strings in prompt modules. | Static AST guardrail rule `QGR021` banning `ast.JoinedStr` in prompt modules and enforcing `ast.TemplateStr` or `render_prompt`. | Zero manual code review needed for prompt injection; language parser guarantees interpolations are isolated as discrete AST nodes. | `test_cdata_hardening_comprehensive.py` passes with 0 violations across all prompt-building components. |

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
    format_spec: str | None
    conversion: str
```
Every dynamic variable enclosed in curly brackets in a `t"..."` literal produces an `Interpolation(value, expression, format_spec, conversion)`. Static text outside curly brackets produces string literals in `strings`. The mathematical invariant holds: `len(strings) == len(interpolations) + 1`.

### 2. The Auto-Sanitizing Renderer (`TemplateProcessor.render_prompt`)
The renderer executes a deterministic transformation on every element:
1. **Static Chunks (`str`):** Emitted directly without modification, preserving exact structural XML tags (`<system_directive>`, `<question>`).
2. **Dynamic Values (`Interpolation`):**
   - Extracted from `interp.value`.
   - Handled cleanly: `None` values are coerced to empty string `""` without emitting empty CDATA blocks.
   - String representations are scanned for CDATA breakout markers (`]]>`), escaping them via `]]]]><![CDATA[>`.
   - Enclosed in `<![CDATA[...]]>`.
   - Concatenated with adjacent static chunks:
     ```python
     chunks: list[str] = []
     for s, interp in zip(template.strings[:-1], template.interpolations, strict=True):
         chunks.append(s)
         if interp.value is not None:
             chunks.append(cls._encapsulate_cdata(str(interp.value)))
     chunks.append(template.strings[-1])
     return "".join(chunks)
     ```
3. **Fail-Fast Boundary:** Unescaped raw string injection into XML tags is mathematically impossible because the Python parser segregates literals from interpolations before execution. Passing any non-`Template` object into `render_prompt` raises an immediate `AppException(ErrorCodes.VALIDATION_FAILED)`.

### 3. Static AST Guardrail Architecture (Zero-Discretion Mathematical Defense)
To enforce this security architecture permanently, a dedicated static AST Guardrail rule `QGR021` in `@[scripts/_ast_guardrails.py]` and `@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]` scans all prompt-building modules (`backend_v2/services/orchestrator/prompts/` and `backend_v2/models/prompts/`):
- **Banned Node:** `ast.JoinedStr` (standard Python f-strings) when constructing XML prompt tags or user payloads.
- **Mandated Node:** `ast.TemplateStr` (PEP 750 `t"..."`) or `TemplateProcessor.render_prompt`.
- **Zero-Discretion Verification:** Code reviewers and AI agents do not need to inspect line-by-line whether a dynamic variable has been manually sanitized or wrapped. If a prompt block uses `t"..."`, the language parser guarantees that interpolations are isolated as discrete AST objects, making un-sanitized prompt injection mathematically impossible.

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
    <action>Run baseline unit tests across `@[backend_v2/tests/unit/test_template_processor.py#L10-L48]` and `@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]` to verify existing CDATA behavior.</action>
    <action>Audit and catalog all 12 manual temporary `_cdata` variables in `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L28-L284]` targeted for elimination.</action>
    <action>Audit `@[backend_v2/services/orchestrator/prompt_compiler.py#L79-L606]` (`build_xml_context` and `_extract_value_from_state`) to prepare structured template replacement for f-string XML concatenation.</action>
    <constraint invariant="touched_scope_tech_debt_mandate">All pre-implementation debts must be cataloged and baselined prior to modifying domain files.</constraint>
  </step>

  <step id="2" name="CORE TEMPLATE PROCESSOR MODERNIZATION">
    <action>In `@[backend_v2/core/template_processor.py#L10-L73]`:
      - Implement `TemplateProcessor.render_prompt(template: Template) -> str`:
        * Enforce Fail-Fast type check that `template` is strictly an instance of `string.templatelib.Template`.
        * Iterate over `zip(template.strings[:-1], template.interpolations, strict=True)`, appending static string chunks and CDATA-encapsulated values.
        * Coerce `interp.value` cleanly: `None` evaluates to empty string `""` without CDATA wrapping; all non-None values pass through `_apply_breakout_shield` and `_encapsulate_cdata`.
        * Append `template.strings[-1]` and return the compiled XML string.
      - Retain existing `encapsulate_payload` and `_apply_breakout_shield` methods for direct utility consumers.
      - Mark legacy `safe_interpolate` as deprecated in favor of `render_prompt`.
    </action>
    <action>Update `@[backend_v2/tests/unit/test_template_processor.py#L10-L48]` with comprehensive unit tests for `render_prompt`:
      - Static literal preservation (braces in JSON schemas must not raise KeyError).
      - Dynamic variable CDATA wrapping.
      - Breakout attempt neutralization (`]]>`).
      - None, integer, and boolean interpolation handling.
      - Fail-Fast assertion when passing non-Template object.
    </action>
    <constraint invariant="pep750_t_strings_only">Prompt rendering must strictly segregate static text from dynamic interpolations.</constraint>
  </step>

  <step id="3" name="MATRIX SENSOR PROMPT BUILDER MIGRATION">
    <action>In `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L28-L284]`:
      - Refactor `build_caching_prefix` (`#L31-L81`) to construct `<matrix_objective>`, `<theory_context>`, and `<context>` blocks using native `t"..."` literals with `TemplateProcessor.render_prompt`.
      - Refactor `build_compiled_prompt` (`#L83-L284`) to eliminate all 12 manual `_cdata` temporary variables.
      - Replace f-string XML formatting blocks for questions, extraction rules, anchor targets, contrastive examples, acceptance criteria, anti-patterns, syntactic anchors, and causal dependencies with structured `t"..."` expressions.
      - Fix double-interpolation bug where XML structures were passed into `safe_interpolate`.
    </action>
    <action>Run unit tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py`.</action>
    <constraint invariant="four_layer_clean_stack_hierarchy">Preserve exact Layer 1 static prefix caching while securing Layer 4 dynamic inputs.</constraint>
  </step>

  <step id="4" name="PROMPT COMPILER &amp; SOURCE VERIFICATION MIGRATION">
    <action>In `@[backend_v2/services/orchestrator/prompt_compiler.py#L79-L606]`:
      - Modernize `build_xml_context` (`#L206-L316`) metadata and input payload tags using `t"..."` literals and `TemplateProcessor.render_prompt`.
      - Modernize `_extract_value_from_state` (`#L318-L482`) nested dict tag formatting using structured template expressions.
    </action>
    <action>In `@[backend_v2/services/source_verification_service.py#L38-L261]`:
      - Modernize `_extract_source_claims` (`#L55-L93`) `<source_data>` assembly using `TemplateProcessor.render_prompt(t"<source_data>\n{text[:max_chars]}\n</source_data>")`.
      - Modernize `_verify_single_claim` (`#L95-L183`) claim and search results prompt assembly using native `t"..."` literals.
    </action>
    <action>Run unit tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py backend_v2/tests/unit/services/test_source_verification_service.py`.</action>
    <constraint invariant="compiler_xml_sovereignty_mandate">Raw prompt blocks must remain natural language; XML wrapping is applied just-in-time by the processor.</constraint>
  </step>

  <step id="5" name="ANALYTICAL HOOKS MIGRATION">
    <action>In `@[backend_v2/hooks/interaction_hook.py#L41-L163]`:
      - Modernize `analyze_interaction_role` user prompt assembly (`#L120-L133`) to use `t"..."` literals and `TemplateProcessor.render_prompt`.
    </action>
    <action>In `@[backend_v2/hooks/linguistics.py#L53-L198]`:
      - Modernize `detect_performative_patterns` (`#L140-L143`) prompt assembly to use `t"..."` literals and `TemplateProcessor.render_prompt`.
    </action>
    <action>Run hook unit tests: `uv run pytest backend_v2/tests/unit/hooks/test_interaction_hook.py backend_v2/tests/unit/hooks/test_linguistics.py`.</action>
    <constraint invariant="single_pipeline_invariant_mandate">All prompt construction across hooks and services must route through the single authoritative renderer.</constraint>
  </step>

  <step id="6" name="AST GUARDRAIL FORTIFICATION &amp; QGR021 IMPLEMENTATION">
    <action>In `@[scripts/_ast_guardrails.py]`, add static guardrail rule `QGR021`:
      - Avoid rule code collision with existing `QGR019` (`.pop()` ban) and `QGR020` (duplicate field ban).
      - Traverse AST nodes in `backend_v2/services/orchestrator/prompts/` and `backend_v2/models/prompts/`.
      - Flag any `ast.JoinedStr` (f-string) constructing XML prompt tags or interpolating user payload variables.
      - Enforce that prompt-building constructs use exclusively `ast.TemplateStr` (PEP 750 `t"..."`) or `TemplateProcessor.render_prompt`.
      - Set rule severity to FATAL in domain code.
    </action>
    <action>In `@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]`:
      - Upgrade AST verification to mathematically verify that prompt assembly across all prompt modules uses `TemplateProcessor.render_prompt` or `t"..."`, eliminating the need for line-by-line manual escape audits.
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
   uv run pytest backend_v2/tests/unit/test_template_processor.py -v
   ```
2. **Matrix Sensor Prompt Builder Tests:**
   ```powershell
   uv run pytest backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py -v
   ```
3. **Prompt Compiler Tests:**
   ```powershell
   uv run pytest backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py -v
   ```
4. **Source Verification Tests:**
   ```powershell
   uv run pytest backend_v2/tests/unit/services/test_source_verification_service.py -v
   ```
5. **Analytical Hooks Tests:**
   ```powershell
   uv run pytest backend_v2/tests/unit/hooks/test_interaction_hook.py backend_v2/tests/unit/hooks/test_linguistics.py -v
   ```
6. **Comprehensive CDATA & Template AST Guardrail:**
   ```powershell
   uv run pytest backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py -v
   ```
7. **Backend Audit Loop:**
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator --test
   ```
8. **Markdown Boundaries Verification:**
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

5. **Negative Scenario 5: Raw F-String AST Violation in Prompt Modules (QGR021)**
   - **Input:** Introducing a new function in `matrix_sensor_prompt_builder.py` using `f"<user_payload>{raw_user_input}</user_payload>"`.
   - **Expected Result:** `test_cdata_hardening_comprehensive.py` and `scripts/_ast_guardrails.py` flag the `ast.JoinedStr` node with rule `QGR021` as FATAL severity, blocking CI/CD deployment.
   - **Verification:** AST visitor test asserts fatal `QGR021` finding on prohibited nodes.
