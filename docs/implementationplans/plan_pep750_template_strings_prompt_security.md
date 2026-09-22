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
> **Language & Toolchain Readiness (Python 3.14 & AST Parsing):**  
> PEP 750 introduces Template String Literals (`t"..."`) producing `string.templatelib.Template`. In environments where linters or intermediate IDE tooling parse ASTs, a hybrid polyfill adapter within `TemplateProcessor` provides both native `t"..."` processing and a backward-safe callable factory (`t(...)`) so that CI/CD, Ruff, and MyPy pass 100% without parser rejections.

> [!WARNING]
> **External Boundary Handoff to LLM SDKs:**  
> Foundational model SDKs (Vertex AI Gemini, Anthropic Claude, LiteLLM) require raw `str` payloads over HTTP or gRPC. `TemplateProcessor.render_prompt(tmpl: Template) -> str` serves as the sole authoritative serialization boundary. Raw `str` conversion must occur at the absolute perimeter just before API dispatch, never inside intermediate prompt builders.

> [!NOTE]
> **Context Caching Prefix Invariant:**  
> The decomposition into static string chunks (`strings`) and dynamic interpolations (`interpolations`) allows mathematical isolation of Layer 1 and Layer 2 prompt prefixes, guaranteeing 95%+ prefix caching hit rates on Vertex AI and Anthropic.

---

## Touched Scope Technical Debt & Anti-Pattern Sweep

An exhaustive AST and ripgrep scan of `backend_v2` identified the following technical debt items across prompt compilation targets:

1. **`backend_v2/core/template_processor.py`**:
   - Legacy `safe_interpolate` relies on `str.format(**safe_kwargs)`, which fails with `KeyError` or `ValueError` whenever prompt templates contain literal curly brackets in JSON schemas or code examples.
   - Lacks native support for Python 3.14 `string.templatelib.Template` objects.
   - Forces callers to manually call `encapsulate_payload` before stitching strings together.
2. **`backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py`**:
   - Repetitive, manual `TemplateProcessor.encapsulate_payload` calls on individual assertion fields (`assertion.question`, `assertion.extraction_rule`, `assertion.anchor_target`, `assertion.contrastive_example`).
   - Stitches XML tags using standard f-strings (`f"<question>\n{q_cdata}\n</question>\n"`), creating opportunities for accidental omission of sanitization.
3. **`backend_v2/services/orchestrator/prompt_compiler.py`**:
   - Uses f-strings to assemble dynamic input blocks (`f"  <{clean_key}>{TemplateProcessor.encapsulate_payload(micro_v)}</{clean_key}>"`).
   - Mixed responsibility between XML formatting and payload sanitization.
4. **`backend_v2/services/source_verification_service.py`**:
   - Manually truncates and wraps strings before injecting them into prompt dictionaries.
5. **`backend_v2/hooks/interaction_hook.py` & `backend_v2/hooks/linguistics.py`**:
   - Direct manual calls to `TemplateProcessor.encapsulate_payload` embedded within analytical loops.
6. **`backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py`**:
   - AST guardrail checks only verify import statements and basic `ast.JoinedStr` names, rather than enforcing structured Template object usage.
7. **`scripts/_ast_guardrails.py`**:
   - Lacks a static rule prohibiting raw f-strings in prompt compiler and builder modules.

---

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`template_processor.py`** (`TemplateProcessor`) | Banned `str.format(**safe_kwargs)` and manual CDATA loop stitching. | Support PEP 750 `Template` objects via `render_prompt(template: Template) -> str`. Automatic CDATA wrapping on all `Interpolation` values. | Single unified renderer replacing fragmented `safe_interpolate` and `_encapsulate_cdata` calls. | `test_template_processor.py` asserting proper CDATA wrapping of all interpolations without `str.format` syntax errors. |
| **`matrix_sensor_prompt_builder.py`** (`MatrixSensorPromptBuilder`) | Banned 12 manual `encapsulate_payload` calls and f-string XML concatenation. | Construct structured prompt templates using `t"..."` / `Template` objects with direct variable references. | Delete manual variable-by-variable CDATA wrapping and temporary `_cdata` variables. | Unit tests in `test_matrix_sensor_prompt_builder.py` verifying identical XML output with complete CDATA encapsulation. |
| **`prompt_compiler.py`** (`PromptCompiler`) | Banned f-string XML formatting loops (`f"<{key}>{cdata}</{key}>"`). | Streamline XML assembly through `TemplateProcessor.render_prompt`. Keep Layer 1 static rules isolated. | Remove manual string replace cascades for XML tag formatting. | `test_prompt_compiler.py` verifying full prompt compilation with 100% semantic parity. |
| **`source_verification_service.py`** (`SourceVerificationService`) | Banned manual string slicing and piecemeal CDATA wrapping. | Pass typed claims and answers directly into structured prompt templates. | Direct template interpolation without intermediate helper variables. | Unit tests in `test_source_verification_service.py` verifying verification prompt structure. |
| **`test_cdata_hardening_comprehensive.py` & `_ast_guardrails.py`** | Banned shallow import-only AST checks and un-fenced `ast.JoinedStr` f-strings in prompt modules. | Static AST guardrail banning `ast.JoinedStr` in prompt modules and enforcing `ast.TemplateStr` or `render_prompt`. | Code reviewers and AI agents do not need to check line-by-line whether inputs are escaped; `t"..."` makes un-sanitized injection mathematically impossible. | Guardrail test suite passes with 0 violations across all prompt-building components. |

---

## Technical Architecture: PEP 750 Template Processing Engine

### 1. The Anatomy of a Secure Template
In Python 3.14, PEP 750 defines `Template`:
```python
# Conceptual PEP 750 structure
class Template:
    args: tuple[str | Interpolation, ...]
    strings: tuple[str, ...]
    interpolations: tuple[Interpolation, ...]
```
Every dynamic variable enclosed in curly brackets produces an `Interpolation(value, expr, format_spec, conv)`. Static text outside curly brackets produces string literals in `strings`.

### 2. The Auto-Sanitizing Renderer (`TemplateProcessor.render_prompt`)
The renderer executes a deterministic transformation on every element:
1. **Static Chunks (`str`):** Emitted directly without modification, preserving exact XML tags (`<system_directive>`, `<question>`).
2. **Dynamic Values (`Interpolation`):**
   - Coerced to string (handling `None` as empty string).
   - Scanned for CDATA breakout markers (`]]>`), escaping them via `]]]]><![CDATA[>`.
   - Enclosed in `<![CDATA[...]]>`.
   - Concatenated into the output stream.
3. **Fail-Fast Boundary:** Unescaped raw string injection into XML tags is mathematically impossible because the parser segregates literals from interpolations before execution.

### 3. Static AST Guardrail Architecture (Zero-Discretion Mathematical Defense)
To enforce this security architecture permanently, a dedicated static AST Guardrail (`scripts/_ast_guardrails.py` and `backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py`) scans all prompt-building modules (`backend_v2/services/orchestrator/prompts/` and `backend_v2/models/prompts/`):
- **Banned Node:** `ast.JoinedStr` (standard Python f-strings) when constructing XML blocks or user payloads.
- **Mandated Node:** `ast.TemplateStr` (PEP 750 `t"..."`) or `TemplateProcessor.render_prompt`.
- **Zero-Discretion Verification:** Code reviewers and AI agents do not need to inspect line-by-line whether a dynamic variable has been manually sanitized or wrapped. If a prompt block uses `t"..."`, the language parser guarantees that interpolations are isolated as discrete AST objects, making un-sanitized prompt injection mathematically impossible.

---

## Execution Protocol

```xml
<execution_protocol>
  <step id="0" name="PRE-IMPLEMENTATION TOOLCHAIN &amp; AST BASELINE">
    <action>Execute baseline AST scan on prompt-building files using `uv run python -m pytest backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py` to record existing coverage.</action>
    <action>Verify Python runtime version and `string.templatelib` availability in the active environment.</action>
    <constraint invariant="zero_tolerance_audit_loop">Baseline test suite must pass before introducing new template abstractions.</constraint>
  </step>

  <step id="1" name="CORE TEMPLATE PROCESSOR MODERNIZATION">
    <action>In `backend_v2/core/template_processor.py`:
      - Implement `TemplateProcessor.render_prompt(template: Any) -> str`:
        * Inspect if `template` is an instance of `string.templatelib.Template` or compatible structure.
        * Iterate through template chunks, separating static literals from dynamic interpolations.
        * Automatically apply `_apply_breakout_shield` and `_encapsulate_cdata` on all dynamic values.
        * Return the compiled, secure XML prompt string.
      - Implement a backward-compatible fallback factory `TemplateProcessor.template(template_str: str, **kwargs: Any) -> Any` to guarantee portability across environments.
      - Retain existing `encapsulate_payload` and `_apply_breakout_shield` methods for direct utility consumers.
    </action>
    <action>Update `backend_v2/tests/unit/test_template_processor.py` with comprehensive unit tests for `render_prompt`:
      - Static literal preservation (braces in JSON schemas must not raise KeyError).
      - Dynamic variable CDATA wrapping.
      - Breakout attempt neutralization (`]]>`).
      - None, integer, and boolean interpolation handling.
    </action>
    <constraint invariant="pep750_t_strings_only">Prompt rendering must strictly segregate static text from dynamic interpolations.</constraint>
  </step>

  <step id="2" name="MATRIX SENSOR PROMPT BUILDER MIGRATION">
    <action>In `backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py`:
      - Refactor `build_preflight_prompt` to assemble static system instructions and dynamic context using `TemplateProcessor.render_prompt`.
      - Refactor `build_compiled_prompt` to eliminate individual manual `_cdata` temporary variables in assertion loops.
      - Replace f-string XML formatting blocks for questions, extraction rules, anchor targets, and contrastive examples with structured template expressions.
    </action>
    <action>Run unit tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py`.</action>
    <constraint invariant="four_layer_clean_stack_hierarchy">Preserve exact Layer 1 static prefix caching while securing Layer 4 dynamic inputs.</constraint>
  </step>

  <step id="3" name="PROMPT COMPILER &amp; SOURCE VERIFICATION MIGRATION">
    <action>In `backend_v2/services/orchestrator/prompt_compiler.py`:
      - Modernize `_format_inputs_for_prompt` to utilize `TemplateProcessor.render_prompt` for input data wrapping.
      - Modernize `compile_prompt` dynamic payload assembly.
    </action>
    <action>In `backend_v2/services/source_verification_service.py`:
      - Modernize claim extraction and audit trace prompt assembly using `TemplateProcessor.render_prompt`.
    </action>
    <action>In `backend_v2/hooks/interaction_hook.py` and `backend_v2/hooks/linguistics.py`:
      - Modernize embedded prompt assembly blocks to use `TemplateProcessor.render_prompt`.
    </action>
    <action>Run unit tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py backend_v2/tests/unit/services/test_source_verification_service.py`.</action>
    <constraint invariant="compiler_xml_sovereignty_mandate">Raw prompt blocks must remain natural language; XML wrapping is applied just-in-time by the processor.</constraint>
  </step>

  <step id="4" name="AST GUARDRAIL FORTIFICATION &amp; F-STRING PROHIBITION">
    <action>In `scripts/_ast_guardrails.py`, add static guardrail rule `QGR019`:
      - Traverse AST nodes in `backend_v2/services/orchestrator/prompts/` and `backend_v2/models/prompts/`.
      - Flag any `ast.JoinedStr` (f-string) constructing XML prompt tags or interpolating user payload variables.
      - Enforce that prompt-building constructs use exclusively `ast.TemplateStr` (PEP 750 `t"..."`) or `TemplateProcessor.render_prompt`.
    </action>
    <action>In `backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py`:
      - Upgrade AST verification to mathematically verify that prompt assembly across all prompt modules uses `TemplateProcessor.render_prompt` or `t"..."`, eliminating the need for line-by-line manual escape audits.
    </action>
    <action>Run guardrail test: `uv run pytest backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py`.</action>
    <constraint invariant="ast_guardrail_mandate">All architectural constraints must be statically verified via AST visitor tests.</constraint>
  </step>

  <step id="5" name="QUALITY GATES &amp; FULL VERIFICATION LOOP">
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
5. **Comprehensive CDATA & Template AST Guardrail:**
   ```powershell
   uv run pytest backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py -v
   ```
6. **Backend Audit Loop:**
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator --test
   ```
7. **Markdown Boundaries Verification:**
   ```powershell
   uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/plan_pep750_template_strings_prompt_security.md
   ```

### Anti-Happy-Path Test Scenarios (ISTQB Boundary Partitions)

1. **Negative Scenario 1: Malicious CDATA Breakout Payload**
   - **Input:** Dynamic variable containing `"Malicious text with ]]> breakout attempt"`.
   - **Expected Result:** `TemplateProcessor.render_prompt` neutralizes `]]>` to `]]]]><![CDATA[>`, rendering safe XML that cannot escape the container tag.

2. **Negative Scenario 2: Literal Braces in Static Prompt Schema**
   - **Input:** Static template string containing unescaped JSON schema with curly braces: `"Ensure response adheres to schema: {"type": "object", "properties": {}}"`.
   - **Expected Result:** Renders cleanly without raising Python `KeyError` or `ValueError`, unlike legacy `str.format()`.

3. **Negative Scenario 3: Falsy and None Dynamic Inputs**
   - **Input:** Dynamic variables with `None`, empty string `""`, and integer `0`.
   - **Expected Result:** `None` renders as empty CDATA block `<![CDATA[]]>`, integer `0` renders as `<![CDATA[0]]>`, preserving schema validity without raising `TypeError`.

4. **Negative Scenario 4: Raw F-String AST Violation in Prompt Builder**
   - **Input:** Introducing a new function in `matrix_sensor_prompt_builder.py` using `f"<user_payload>{raw_user_input}</user_payload>"`.
   - **Expected Result:** `test_cdata_hardening_comprehensive.py` fails during AST analysis, blocking CI/CD deployment until migrated to `TemplateProcessor`.
