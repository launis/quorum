<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
</required_context_rules>

# Phase 3A: Hook Subsystem Suppression & Duck-Typing Eradication

## Overview

Eradicate all `# noqa: QGR012` inline suppressions, `dict[str, Any]` annotations, and `isinstance(..., dict)` duck-typing checks across all 18 files in the Hook subsystem (`backend_v2/hooks/`). Implement the 3-Tiered Anti-Duck-Typing Protocol: direct DTO attribute access for typed upstream state, guarded `TypeAdapter` validation with RFC-7807 `AppException(VALIDATION_FAILED, status_code=422)` conversion for untrusted boundary payloads, and category pre-filtering for polymorphic state. Expand unit test suites to resolve coverage gaps and achieve >90% code coverage.

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Scoring Hooks Core**<br>`@[backend_v2/hooks/scoring/falsifier_hook.py#L34-L307]`<br>`@[backend_v2/hooks/scoring/matrix_hook.py#L37-L484]`<br>`@[backend_v2/hooks/scoring/normalization_hook.py#L37-L386]`<br>`@[backend_v2/hooks/scoring/passivity_hook.py#L37-L202]` | Banned 14 `# noqa: QGR012` suppressions, `extra="ignore"` pseudo-token shields on `ScoringPayloadWrapper` and `StateInputWrapper`, `dict[str, Any]` on `_extract_payloads` / `recalculate`, and `isinstance(..., dict)` checks on `_evaluative_matrices`, `judge_model`, and `valid_dto.payload`. | Direct DTO attribute access (`state.inputs.raw_inputs`, `state.inputs.dynamic_inputs`). `ScoringPayloadWrapper` and `StateInputWrapper` enforce `ConfigDict(strict=True, extra="forbid", frozen=True)`. Discriminated Union / Category Pre-Filtering for matrix state. | Pruned raw dictionary laundering loops. Reuse existing SSOT models (`StepOutputDTO`, `LightweightMatrixOutput`, `AtomResultDTO`, `HookDeltaDTO`). | `uv run python scripts/_ast_guardrails.py backend_v2/hooks/scoring/ --strict`<br>`uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring/ --test` |
| **Validation & Processing Hooks**<br>`@[backend_v2/hooks/validation.py#L29-L359]`<br>`@[backend_v2/hooks/input_processing.py#L35-L419]`<br>`@[backend_v2/hooks/integrity.py#L90-L346]`<br>`@[backend_v2/hooks/source_verification_hook.py#L35-L202]`<br>`@[backend_v2/hooks/security.py#L29-L143]` | Banned `TypeAdapter(dict[str, Any])` adapters, `fields_to_validate: dict[str, Any]`, silent `except ValidationError: pass` swallowing, and loose dict typing on `resolve_input` / `_process_questionnaire`. | Guarded `TypeAdapter(Model).validate_python()` with RFC-7807 `AppException(VALIDATION_FAILED, status_code=422)` conversion. Strongly typed `GuidedReflectionInputDTO` and `SourceVerificationInputsDTO`. | Pruned generic `_dict_adapter` / `_list_adapter` type adapters. Direct model validation via SSOT schemas. | `uv run python scripts/_ast_guardrails.py backend_v2/hooks/validation.py backend_v2/hooks/input_processing.py backend_v2/hooks/integrity.py backend_v2/hooks/source_verification_hook.py backend_v2/hooks/security.py --strict` |
| **Context, State & Telemetry Hooks**<br>`@[backend_v2/hooks/llm.py#L25-L196]`<br>`@[backend_v2/hooks/dlq_guard.py#L21-L99]`<br>`@[backend_v2/hooks/atom_flattening.py#L32-L210]`<br>`@[backend_v2/hooks/context_mapper.py#L18-L105]`<br>`@[backend_v2/hooks/archival.py#L24-L182]`<br>`@[backend_v2/hooks/hydration.py#L19-L71]`<br>`@[backend_v2/hooks/metadata.py#L20-L104]`<br>`@[backend_v2/hooks/metrics.py#L32-L343]`<br>`@[backend_v2/hooks/references.py#L30-L182]` | Banned `content_payload: dict[str, Any]`, `all_blocks: list[Any]`, loose `knowledge_base: dict[str, object]`, and raw dict manipulations. | Strongly typed `list[PromptBlockBase]`, `StepMetadataDTO`, `HydrationInputSourceDTO`, and `TextMetricsDTO`. Direct dot-notation access to `state.inputs.raw_inputs`. | Pruned speculative dictionary wrapper layers. Co-locate DTO schemas directly in domain modules. | `uv run python scripts/_ast_guardrails.py backend_v2/hooks/ --strict` |
| **Hook Unit Test Suites**<br>`@[backend_v2/tests/unit/hooks/]` | Banned coverage deficit (<90%), skipped tests, and raw dictionary message fixtures. | Comprehensive ISTQB negative boundary and equivalence partition test coverage for all 18 hook files (>90% overall line coverage). | Pruned duplicate test cases; assert strictly typed DTO models and explicit `AppException` error codes. | `uv run python scripts/backend_audit_loop.py backend_v2/hooks/ --test` |

## Target Files

- `[MODIFY]` `@[backend_v2/hooks/scoring/falsifier_hook.py#L34-L307]`
- `[MODIFY]` `@[backend_v2/hooks/scoring/matrix_hook.py#L37-L484]`
- `[MODIFY]` `@[backend_v2/hooks/scoring/normalization_hook.py#L37-L386]`
- `[MODIFY]` `@[backend_v2/hooks/scoring/passivity_hook.py#L37-L202]`
- `[MODIFY]` `@[backend_v2/hooks/validation.py#L29-L359]`
- `[MODIFY]` `@[backend_v2/hooks/llm.py#L25-L196]`
- `[MODIFY]` `@[backend_v2/hooks/dlq_guard.py#L21-L99]`
- `[MODIFY]` `@[backend_v2/hooks/input_processing.py#L35-L419]`
- `[MODIFY]` `@[backend_v2/hooks/integrity.py#L90-L346]`
- `[MODIFY]` `@[backend_v2/hooks/source_verification_hook.py#L35-L202]`
- `[MODIFY]` `@[backend_v2/hooks/atom_flattening.py#L32-L210]`
- `[MODIFY]` `@[backend_v2/hooks/context_mapper.py#L18-L105]`
- `[MODIFY]` `@[backend_v2/hooks/archival.py#L24-L182]`
- `[MODIFY]` `@[backend_v2/hooks/security.py#L29-L143]`
- `[MODIFY]` `@[backend_v2/hooks/hydration.py#L19-L71]`
- `[MODIFY]` `@[backend_v2/hooks/metadata.py#L20-L104]`
- `[MODIFY]` `@[backend_v2/hooks/metrics.py#L32-L343]`
- `[MODIFY]` `@[backend_v2/hooks/references.py#L30-L182]`
- `[MODIFY]` `@[backend_v2/tests/unit/hooks/test_scoring.py]`
- `[NEW]` `@[backend_v2/tests/unit/hooks/test_validation.py]`
- `[NEW]` `@[backend_v2/tests/unit/hooks/test_context_mapper.py]`
- `[NEW]` `@[backend_v2/tests/unit/hooks/test_security.py]`
- `[NEW]` `@[backend_v2/tests/unit/hooks/test_references.py]`
- `[NEW]` `@[backend_v2/tests/unit/hooks/test_metadata.py]`

```xml
<execution_protocol>
  <metadata>
    <epic_anchor>@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md#Phase 3: Hooks, Orchestrator & Repository Suppression Eradication]</epic_anchor>
    <touched_artifacts>
      <backend>@[backend_v2/hooks/scoring/falsifier_hook.py#L34-L307]</backend>
      <backend>@[backend_v2/hooks/scoring/matrix_hook.py#L37-L484]</backend>
      <backend>@[backend_v2/hooks/scoring/normalization_hook.py#L37-L386]</backend>
      <backend>@[backend_v2/hooks/scoring/passivity_hook.py#L37-L202]</backend>
      <backend>@[backend_v2/hooks/validation.py#L29-L359]</backend>
      <backend>@[backend_v2/hooks/llm.py#L25-L196]</backend>
      <backend>@[backend_v2/hooks/dlq_guard.py#L21-L99]</backend>
      <backend>@[backend_v2/hooks/input_processing.py#L35-L419]</backend>
      <backend>@[backend_v2/hooks/integrity.py#L90-L346]</backend>
      <backend>@[backend_v2/hooks/source_verification_hook.py#L35-L202]</backend>
      <backend>@[backend_v2/hooks/atom_flattening.py#L32-L210]</backend>
      <backend>@[backend_v2/hooks/context_mapper.py#L18-L105]</backend>
      <backend>@[backend_v2/hooks/archival.py#L24-L182]</backend>
      <backend>@[backend_v2/hooks/security.py#L29-L143]</backend>
      <backend>@[backend_v2/hooks/hydration.py#L19-L71]</backend>
      <backend>@[backend_v2/hooks/metadata.py#L20-L104]</backend>
      <backend>@[backend_v2/hooks/metrics.py#L32-L343]</backend>
      <backend>@[backend_v2/hooks/references.py#L30-L182]</backend>
      <test>@[backend_v2/tests/unit/hooks/test_scoring.py]</test>
      <test>@[backend_v2/tests/unit/hooks/test_validation.py]</test>
      <test>@[backend_v2/tests/unit/hooks/test_context_mapper.py]</test>
      <test>@[backend_v2/tests/unit/hooks/test_security.py]</test>
      <test>@[backend_v2/tests/unit/hooks/test_references.py]</test>
      <test>@[backend_v2/tests/unit/hooks/test_metadata.py]</test>
    </touched_artifacts>
  </metadata>

  <contract_freeze>
    <interface id="HookAntiDuckTypingProtocol">
      # Pattern 1: Direct DTO dot-notation access on ExecutionInputsDTO and GlobalContextVarsDTO
      # Pattern 2: Guarded TypeAdapter hydration with RFC-7807 AppException(VALIDATION_FAILED, status_code=422)
      # Pattern 3: Category pre-filtering before polymorphic schema hydration (PromptBlockCategory.MATRIX)
      # Pattern 4: Strict Pydantic V2 schemas with ConfigDict(strict=True, extra="forbid", frozen=True)
    </interface>
  </contract_freeze>

  <anti_targets>
    <file>@[backend_v2/services/orchestrator/]</file>
    <file>@[backend_v2/database/repositories/]</file>
    <file>@[client_app_v2/]</file>
  </anti_targets>

  <dod_checklist>
    <item>Zero # noqa: QGR012, QGR002, or QGR001 suppressions across all 18 hook files</item>
    <item>Zero isinstance(..., dict) duck-typing checks across backend_v2/hooks/</item>
    <item>Zero extra="ignore" or extra="allow" models across backend_v2/hooks/ (strict ConfigDict on all wrappers)</item>
    <item>All DLQ handlers log structured errors via logger.error(..., extra={"error_code": ...})</item>
    <item>AST guardrails pass 100% clean on backend_v2/hooks/ in --strict mode (0 violations, 0 suppressions)</item>
    <item>Overall test coverage for backend_v2/hooks/ exceeds 90% in backend_audit_loop.py</item>
  </dod_checklist>

  <step id="0" name="STRATEGIC ALIGNMENT CHECK & PRE-IMPLEMENTATION CLEANUPS">
    <action>Verify that Phase 2 quality gates pass cleanly and run baseline AST check.</action>
    <action>In @[backend_v2/hooks/scoring/falsifier_hook.py#L34-L54], refactor `ScoringPayloadWrapper` and `StateInputWrapper` to enforce `ConfigDict(strict=True, extra="forbid", frozen=True)` and replace `dict[str, Any]` fields with `ExecutionInputsDTO | None`.</action>
    <action>In @[backend_v2/hooks/context_mapper.py#L22], update `all_blocks` signature from `list[Any] | None` to `list[PromptBlockBase] | None`.</action>
    <action>In @[backend_v2/hooks/references.py#L30], update `knowledge_base` signature to typed `dict[str, str] | None`.</action>
  </step>

  <step id="1" name="HARDEN SCORING HOOKS">
    <action>In @[backend_v2/hooks/scoring/falsifier_hook.py#L56-L307], eliminate 5 dict[str, Any] annotations and 3 QGR012 suppressions via direct DTO attribute access.</action>
    <action>In @[backend_v2/hooks/scoring/matrix_hook.py#L37-L484], eliminate 1 dict[str, Any] annotation and 5 QGR012 suppressions by replacing isinstance(ev, dict) with direct AtomResultDTO hydration and category pre-filtering.</action>
    <action>In @[backend_v2/hooks/scoring/normalization_hook.py#L37-L386], eliminate 1 dict[str, Any] annotation and 3 QGR012 suppressions by typing `recalculate()` and using direct DTO attribute access on `_evaluative_matrices`.</action>
    <action>In @[backend_v2/hooks/scoring/passivity_hook.py#L37-L202], eliminate 1 dict[str, Any] annotation and 3 QGR012 suppressions via direct ExecutionInputsDTO property access.</action>
  </step>

  <step id="2" name="HARDEN PROCESSING, VALIDATION & TELEMETRY HOOKS">
    <action>In @[backend_v2/hooks/validation.py#L29-L359], eliminate all loose dict annotations (`fields_to_validate`, `delta`), replace silent `except ValidationError: pass` with explicit error logging and structured validation, and strongly type input extraction.</action>
    <action>In @[backend_v2/hooks/llm.py#L25-L196], eradicate `_str_dict_adapter` and `config_data: dict[str, Any]` via typed `SystemConfigModelRegistry` and `LLMProviderConfig`.</action>
    <action>In @[backend_v2/hooks/dlq_guard.py#L21-L99], replace `content_payload: dict[str, Any]` with direct `state.inputs.raw_inputs` attribute access.</action>
    <action>In @[backend_v2/hooks/input_processing.py#L35-L419], strongly type `resolve_input` and `_process_questionnaire` with `GuidedReflectionInputDTO`.</action>
    <action>In @[backend_v2/hooks/integrity.py#L90-L346], eliminate `dict[str, Any]` union in `_gather_rag_context`.</action>
    <action>In @[backend_v2/hooks/source_verification_hook.py#L35-L202], eradicate `_dict_adapter` and `_list_adapter` by validating directly against `SourceVerificationInputsDTO`.</action>
    <action>In @[backend_v2/hooks/atom_flattening.py#L32-L210], @[backend_v2/hooks/archival.py#L24-L182], @[backend_v2/hooks/security.py#L29-L143], @[backend_v2/hooks/hydration.py#L19-L71], @[backend_v2/hooks/metadata.py#L20-L104], and @[backend_v2/hooks/metrics.py#L32-L343], replace raw dict transformations with typed DTO access.</action>
  </step>

  <step id="3" name="COMPREHENSIVE TEST EXPANSION & AST GUARDRAIL VALIDATION">
    <action>Create `@[backend_v2/tests/unit/hooks/test_validation.py]` covering `verify_structure`, `verify_length`, and `verify_guttman_distribution` with ISTQB negative boundary partitions (missing inputs, empty inputs, short text, malformed payloads).</action>
    <action>Create `@[backend_v2/tests/unit/hooks/test_context_mapper.py]` covering `ContextMapper.build_ordinal_mapping` and `ContextMapper.build_global_mapping` with 100% branch coverage.</action>
    <action>Create `@[backend_v2/tests/unit/hooks/test_security.py]` covering `sanitize_text_hook` with PII detection, language validation, and exception handling.</action>
    <action>Create `@[backend_v2/tests/unit/hooks/test_references.py]` covering `generate_bibliography` and `extract_references_hook`.</action>
    <action>Create `@[backend_v2/tests/unit/hooks/test_metadata.py]` covering `inject_step_metadata` with strict state validation.</action>
    <action>Run strict AST guardrail scan and backend audit loop to mathematically verify >90% coverage and 0 violations.</action>
  </step>

  <test_contracts>
    <contract id="1" name="test_hook_guarded_hydration_raises_app_exception">
      <input>malformed input payload to hook validator</input>
      <expected>raises AppException(VALIDATION_FAILED, status_code=422)</expected>
      <category>negative</category>
    </contract>
    <contract id="2" name="test_scoring_hooks_process_typed_dto_state">
      <input>ExecutionInputsDTO with valid typed dynamic inputs</input>
      <expected>returns HookDeltaDTO with strictly typed modifications</expected>
      <category>positive</category>
    </contract>
    <contract id="3" name="test_validation_hook_boundary_partitions">
      <input>State with empty string, missing required inputs, or non-matching Guttman structure</input>
      <expected>raises AppException with ErrorCodes.EMPTY_INPUT or ErrorCodes.VALIDATION_FAILED</expected>
      <category>negative</category>
    </contract>
    <contract id="4" name="test_context_mapper_non_prompt_block_raises">
      <input>all_blocks containing invalid non-PromptBlock objects</input>
      <expected>raises AppException with ErrorCodes.DATA_CORRUPTION</expected>
      <category>negative</category>
    </contract>
  </test_contracts>

  <validation_gate>
    <action>Run AST guardrail scan in strict mode and full backend audit loop with >90% coverage requirement:</action>
    <command>uv run python scripts/_ast_guardrails.py backend_v2/hooks/ --strict</command>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/hooks/ --test</command>
  </validation_gate>
</execution_protocol>

