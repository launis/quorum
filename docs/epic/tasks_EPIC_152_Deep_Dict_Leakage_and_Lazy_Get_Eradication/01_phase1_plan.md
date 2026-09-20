# Phase 1: Architecture Baseline, AST Guardrail Definition & Pre-Implementation Technical Debt Cleanups

**Overview:** Establish the neuro-symbolic AST verification foundation (QGR018) for zero permissive typing, deep dictionary eradication, and lazy `.get()` eradication. Remediate foundational technical debt across settings, math utilities, logging, validation hooks, and persistence drivers to establish a strictly typed baseline before domain model hardening.
**Target Files:**
- `[MODIFY]` @[scripts/audit_dict_eradication.py#L290-L331]
- `[MODIFY]` @[scripts/_ast_guardrails.py#L123-L194]
- `[MODIFY]` @[scripts/run_e2e_variance_test.py#L133-L229]
- `[MODIFY]` @[backend_v2/hooks/validation.py#L30-L184]
- `[MODIFY]` @[backend_v2/settings.py#L617-L627]
- `[MODIFY]` @[backend_v2/utils/math_utils.py#L190-L221]
- `[MODIFY]` @[backend_v2/logging_config.py#L302-L339]
- `[MODIFY]` @[backend_v2/database/tinydb_driver.py#L28-L54]
- `[MODIFY]` @[backend_v2/database/firestore_driver.py#L24-L64]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the codebase baseline state and verify existing AST guardrails in @[scripts/_ast_guardrails.py].</action>
    <action>Look forward: Verify that subsequent phases (Phase 2 through 7) rely on the new QGR018 AST rules to prevent regression.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_152_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication/01_phase1_plan.md] @[docs/epic/EPIC_152_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>AST guardrail script @[scripts/audit_dict_eradication.py] is self-hardened and passes across all target files.</item>
    <item>Rule QGR018 and Python 3 tuple exception handling are enforced in @[scripts/_ast_guardrails.py].</item>
    <item>All getattr, hasattr, and defensive .get() calls are eradicated from target files.</item>
    <item>All dictionary-based normalization and silent exception swallowing in @[backend_v2/hooks/validation.py] are demolished.</item>
    <item>Settings and math utilities operate with 100% strongly typed interfaces and zero reflection.</item>
    <item>All unit and integration tests pass with zero regressions.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
    <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
    <knowledge_item>@[ki_cartesian_variance_and_authenticity.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_tda_best_of_three_flash.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_transient_error_resilience.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <forbidden>Do NOT modify domain execution models in @[backend_v2/models/domain/execution.py] during Phase 1 (reserved for Phase 2).</forbidden>
    <forbidden>Do NOT modify prompt compiler or DAG executor in @[backend_v2/services/orchestrator/prompt_compiler.py] during Phase 1 (reserved for Phase 5).</forbidden>
    <forbidden>Do NOT modify SDUI mappers or presentation models during Phase 1 (reserved for Phase 6).</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>@[scripts/audit_dict_eradication.py]</backend>
    <backend>@[scripts/_ast_guardrails.py]</backend>
    <backend>@[scripts/run_e2e_variance_test.py]</backend>
    <backend>@[backend_v2/hooks/validation.py]</backend>
    <backend>@[backend_v2/settings.py]</backend>
    <backend>@[backend_v2/utils/math_utils.py]</backend>
    <backend>@[backend_v2/logging_config.py]</backend>
    <backend>@[backend_v2/database/tinydb_driver.py]</backend>
    <backend>@[backend_v2/database/firestore_driver.py]</backend>
  </touched_artifacts>

  <!-- Phase 1: Pre-Implementation Cleanups (Scoped Boy Scout Rule) -->
  <pre_implementation_cleanups>
    <debt_item id="1" domain="backend" category="reflection">
      Eradicate `hasattr(data, "model_dump")` in @[backend_v2/database/tinydb_driver.py#L28-L54] and @[backend_v2/database/firestore_driver.py#L24-L64] in favor of `isinstance(data, BaseModel)`.
      Eradicate duck-typing `hasattr` and `getattr` on exceptions and LogRecord instances in @[backend_v2/logging_config.py#L302-L339] in favor of `isinstance(exc, AppException)` and `StructuredLogContextDTO`.
      Eradicate `hasattr(label_val, "get")` and `hasattr(translations_dict, "values")` in @[scripts/run_e2e_variance_test.py#L133-L229] in favor of `ExpectedInput.model_validate(item)`.
      Eradicate `curr.__dict__[part]` on BaseModel in @[backend_v2/utils/math_utils.py#L190-L221] in favor of `object.__getattribute__(curr, part)` to enforce AST rule QGR001 with zero `__dict__` reflection.
    </debt_item>
    <debt_item id="2" domain="backend" category="dict_get">
      Eradicate `inputs_dict.get("raw_inputs")`, `inputs_dict.get("inputs")`, and `inputs_source.get("_system_warnings")` in @[backend_v2/hooks/validation.py#L30-L184].
      Extend @[scripts/audit_dict_eradication.py#L290-L331] to statically detect `.get(` calls on internal variables across hooks, services, and workers.
    </debt_item>
    <debt_item id="3" domain="backend" category="silent_except">
      Eradicate silent `except ValidationError: pass` (Lines 88-91, 96-99), `except AttributeError, TypeError: raw_warnings = []` (Lines 279-280), and `except ValidationError: continue` (Lines 344-345) in @[backend_v2/hooks/validation.py#L30-L184].
      Self-harden @[scripts/audit_dict_eradication.py#L290-L331]: eliminate Line 285 (`except Exception: pass`) in comment auditing and Line 311 (`except Exception: continue`) in AST parsing.
      Eradicate Python 2 comma exceptions `except AttributeError, io.UnsupportedOperation:` (Line 40) and `except tokenize.TokenError, IndentationError, UnicodeDecodeError, SyntaxError:` (Line 193) in @[scripts/_ast_guardrails.py#L123-L194].
    </debt_item>
    <debt_item id="4" domain="backend" category="model_copy">
      Verify immutable updates and eliminate ad-hoc unvalidated model mutations across target modules.
    </debt_item>
    <debt_item id="5" domain="backend" category="magic_numbers">
      Ruthlessly delete dead computed property `model_strategies` returning naked empty dict in @[backend_v2/settings.py#L617-L627]; model strategies are loaded strictly from `system_config` table in the database (SSOT).
    </debt_item>
    <debt_item id="6" domain="backend" category="strict_dtos">
      Define [NEW] `StructuredLogContextDTO` in @[backend_v2/logging_config.py#L302-L339] with `ConfigDict(strict=True, extra="forbid", frozen=True)`.
      Ensure `verify_structure`, `verify_output_language`, and `verify_anomaly` use strict Pydantic V2 DTOs with guaranteed dot-notation access.
    </debt_item>
    <debt_item id="7" domain="istqb" category="negative_partitions">
      Add ISTQB negative boundary test cases covering malformed payloads in `validation.py`, `StructuredLogContextDTO` serialization in `logging_config.py`, and `resolve_dot_notation` in `math_utils.py`.
    </debt_item>
  </pre_implementation_cleanups>

  <!-- 5-Column Architectural Directives Table -->
  <directives_table>
| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[scripts/audit_dict_eradication.py#L290-L331]` | Silent exception swallowing `except Exception: pass` (Line 285) and `except Exception: continue` (Line 311). | Fail-Fast deterministic AST parsing; unparseable files fail audit with non-zero exit code (status code 1); extend visitor to detect `.get(` on internal variables in `hooks/`, `services/`, and `workers/`, reflection calls, and unraised exception swallowing. | Eliminate permissive silent error swallowing loops; keep audit script focused on deterministic AST visitor patterns. | `uv run python scripts/audit_dict_eradication.py` outputs non-zero exit code on unparseable files; unit test verifying syntax error detection. |
| `@[scripts/_ast_guardrails.py#L123-L194]` | Python 2 comma exception syntax `except AttributeError, io.UnsupportedOperation:` (Line 40) and `except tokenize.TokenError, IndentationError, UnicodeDecodeError, SyntaxError:` (Line 193). | Modern Python 3 tuple syntax `except (AttributeError, io.UnsupportedOperation):` and `except (tokenize.TokenError, IndentationError, UnicodeDecodeError, SyntaxError):`; enforce QGR018 rule across domain code. | Eliminate outdated Python 2 exception syntax; maintain static zero-reflection AST visitor architecture. | `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py` passes 100% (96 tests). |
| `@[backend_v2/hooks/validation.py#L30-L184]` | Chained `.get("raw_inputs")`, `.get("inputs")`, silent `except ValidationError: pass` (Lines 88-91, 96-99), `inputs_source.get("_system_warnings") or []` (Line 278), `except AttributeError, TypeError: raw_warnings = []` (Lines 279-280), and `except ValidationError: continue` (Lines 344-345). | Direct dot-notation access via `ExecutionInputsDTO.raw_inputs`, `ExecutionInputsDTO.dynamic_inputs`, and `ExecutionInputsDTO.system_warnings`; Fail-Fast raising `AppException(ErrorCodes.VALIDATION_FAILED)` on invalid structure or malformed atoms. | Eliminate redundant flat-payload fallback branches and manual dictionary key probing; rely on canonical `ExecutionInputsDTO` schema. | `uv run pytest backend_v2/tests/unit/hooks/test_validation.py` passes 100% (20 tests); ISTQB tests asserting Fail-Fast on invalid payloads. |
| `@[backend_v2/settings.py#L617-L627]` | `@computed_field @property def model_strategies(self) -> dict[str, Any]: return {}` dead property returning naked empty dictionary. | Ruthlessly delete dead computed property `model_strategies`; LLM model strategies are loaded strictly from `system_config` table in the database (SSOT). | Eradicate dead code and empty dictionary returns; reduce settings surface area (-11 lines). | `scripts/audit_dict_eradication.py` verifies zero naked dict annotations in `settings.py`. |
| `@[backend_v2/utils/math_utils.py#L190-L221]` | Dynamic `curr.__dict__[part]` attribute access on BaseModel instances in `resolve_dot_notation` (Line 210). | Direct attribute traversal via `object.__getattribute__(curr, part)` to comply with AST guardrail QGR001 with zero `__dict__` reflection. | Eliminate dynamic dictionary access on BaseModel fields while preserving safe dot-notation resolution for sequences, mappings, and Pydantic models. | `uv run pytest backend_v2/tests/unit/utils/test_math_utils.py` passes 100% (13 tests); AST guardrail confirms zero `__dict__` violations in `math_utils.py`. |
| `@[backend_v2/logging_config.py#L302-L339]` | Duck-typing reflection on exceptions and log records: `hasattr(exc, "error_code")`, `hasattr(exc, "details")`, `hasattr(exc, "detail")`, `hasattr(error_code, "name")`, `getattr(record, "execution_id", "SYSTEM")`, `getattr(record, "context_id", "SYSTEM")`, `hasattr(record, "error_code")`, `hasattr(record, "details")`. | Direct type narrowing via `isinstance(exc, AppException)` with typed property access; define `[NEW]` `StructuredLogContextDTO` for structured log context payloads; maintain `logging_config.py` in `BOUNDARY_EXEMPTION_FILES`. | Eradicate multi-branch reflection duck-typing on exception objects; replace with clean type check and structured DTO. | Unit tests in `test_logging_isolation.py` and `test_logging_config.py` asserting RFC 7807 compliance without reflection. |
| `@[backend_v2/database/tinydb_driver.py#L28-L54]` & `@[backend_v2/database/firestore_driver.py#L24-L64]` | `hasattr(data, "model_dump")` duck-typing check (Line 39 in TinyDB, Line 49 in Firestore). | Direct type narrowing via `isinstance(data, BaseModel)` followed by `self._serialize(data.model_dump())`; maintain both drivers in `BOUNDARY_EXEMPTION_FILES`. | Eliminate method existence reflection string checks on model objects. | `backend_audit_loop.py` and driver persistence tests passing 100%. |
| `@[scripts/run_e2e_variance_test.py#L133-L229]` | Duck-typing `hasattr(label_val, "get")` (Line 181) and `hasattr(translations_dict, "values")` (Line 183). | Direct Pydantic validation via `ExpectedInput.model_validate(item)` and dot-notation `item.label.translations.values()` in `_match_input_key`. | Eradicate scripted dictionary guessing and reflection in regression test harness. | `run_e2e_variance_test.py --help` runs without error; AST check verifies zero `hasattr` in input resolution. |
  </directives_table>

  <step id="1.1" name="AST Guardrail QGR018 Implementation &amp; Auditor Self-Hardening">
    <action>Self-harden @[scripts/audit_dict_eradication.py#L290-L331]: eradicate silent exception swallowing `except Exception: pass` (Line 285) in comment auditing and `except Exception: continue` (Line 311) in AST parsing. An unparseable file MUST fail the audit run with exit code 1 to eliminate Fake Green test suites.</action>
    <action>Update @[scripts/_ast_guardrails.py#L123-L194] to replace Python 2 comma exceptions (`except AttributeError, io.UnsupportedOperation:` and `except tokenize.TokenError, IndentationError, UnicodeDecodeError, SyntaxError:`) with Python 3 tuple syntax. Enforce rule QGR018 detecting type laundering via `TypeAdapter` with dictionary types.</action>
    <action>Extend @[scripts/audit_dict_eradication.py#L290-L331] to detect `.get(` calls on internal variables in `hooks/`, `services/`, and `workers/`, verify dynamic reflection calls (`getattr`, `hasattr`, `setattr`, `object.__setattr__`), verify exception inheritance from `AppException`, and audit unauthorized `# noqa: QGR*` suppressions.</action>
    <demolish>REMOVE: `hasattr` and `getattr` usage patterns across baseline scripts.</demolish>
    <constraint invariant="the_zero_compromise_pledge">Enforce Fail-Fast on any dynamic type inspection.</constraint>
  </step>

  <step id="1.2" name="Validation Hook Hardening">
    <action>Refactor @[backend_v2/hooks/validation.py#L30-L184]: eradicate `inputs_dict.get("raw_inputs")`, `inputs_dict.get("inputs")`, silent `except ValidationError: pass` (Lines 88-91, 96-99), `inputs_source.get("_system_warnings") or []` (Line 278), `except AttributeError, TypeError:` (Lines 279-280), and `except ValidationError: continue` (Lines 344-345).</action>
    <action>Replace legacy dictionary traversal with direct Pydantic V2 model attribute access (`ExecutionInputsDTO.raw_inputs`, `ExecutionInputsDTO.dynamic_inputs`, `ExecutionInputsDTO.system_warnings`) and Fail-Fast with typed `AppException(ErrorCodes.VALIDATION_FAILED)`.</action>
    <demolish>REMOVE: `hasattr`, `getattr`, `_normalize_result_item` in @[backend_v2/hooks/validation.py]. REPLACE WITH: direct Pydantic model validation and explicit AppException error handling.</demolish>
  </step>

  <step id="1.3" name="Settings &amp; Math Utilities Strictness">
    <action>Ruthlessly delete dead computed property `model_strategies` returning naked empty dict in @[backend_v2/settings.py#L617-L627]; model strategies are loaded strictly from `system_config` table in the database (SSOT).</action>
    <action>Refactor @[backend_v2/utils/math_utils.py#L190-L221] to eradicate `curr.__dict__[part]` on BaseModel (Line 210) in favor of `object.__getattribute__(curr, part)` to satisfy AST rule QGR001 with zero `__dict__` reflection.</action>
    <action>Ensure all configuration parameters and mathematical helper functions take strongly defined, typed arguments.</action>
  </step>

  <step id="1.4" name="Logging &amp; Database Driver Baseline Hardening">
    <action>Define [NEW] `StructuredLogContextDTO` in @[backend_v2/logging_config.py#L302-L339] with `ConfigDict(strict=True, extra="forbid", frozen=True)` for strongly typed structured log context data.</action>
    <action>Refactor @[backend_v2/logging_config.py#L302-L339] to eliminate reflection duck-typing (`hasattr(exc, "error_code")`, `hasattr(exc, "details")`, `getattr(record, ...)`) in favor of direct type narrowing via `isinstance(exc, AppException)`.</action>
    <action>Update @[backend_v2/database/tinydb_driver.py#L28-L54] (Line 39) and @[backend_v2/database/firestore_driver.py#L24-L64] (Line 49) to replace `hasattr(data, "model_dump")` with explicit `isinstance(data, BaseModel)`.</action>
  </step>

  <step id="1.5" name="E2E Variance Test Harness Typed Payload Parity">
    <action>Update @[scripts/run_e2e_variance_test.py#L133-L229] to eradicate `hasattr(label_val, "get")` (Line 181) and `hasattr(translations_dict, "values")` (Line 183) in favor of `ExpectedInput.model_validate(item)` and dot-notation `item.label.translations.values()` in `_match_input_key`.</action>
    <action>Verify end-to-end variance execution harness against the modernized baseline.</action>
  </step>

  <test_contracts>
    <test name="test_audit_dict_eradication_fails_on_syntax_error" category="error_path">
      <input>Malformed Python file causing AST parse failure.</input>
      <expected>Script terminates with non-zero exit code (1), eliminating Fake Green test runs.</expected>
    </test>
    <test name="test_ast_guardrails_python3_tuple_exceptions" category="positive">
      <input>Python AST guardrail test suite running under Python 3.14.</input>
      <expected>All 96 tests in test_ast_guardrails.py pass with zero syntax warnings or comma exception errors.</expected>
    </test>
    <test name="test_validation_hook_rejects_malformed_dto" category="error_path">
      <input>Invalid evaluation item missing mandatory score attribute.</input>
      <expected>Raises AppException with VALIDATION_FAILED code, zero defensive fallbacks.</expected>
    </test>
    <test name="test_math_utils_resolve_dot_notation_base_model_without_dict" category="positive">
      <input>Pydantic BaseModel instance queried via dot-notation path.</input>
      <expected>Resolves attribute via object.__getattribute__ with zero __dict__ reflection.</expected>
    </test>
    <test name="test_logging_config_structured_context_dto" category="positive">
      <input>Structured log event formatted with StructuredLogContextDTO.</input>
      <expected>Emits valid JSON log string containing execution_id and context_id without hasattr/getattr reflection.</expected>
    </test>
    <test name="test_storage_drivers_isinstance_base_model" category="positive">
      <input>Pydantic domain model passed to TinyDB and Firestore _serialize methods.</input>
      <expected>Serializes via isinstance(data, BaseModel) without hasattr(data, 'model_dump').</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run AST guardrails test suite: uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py -v</action>
    <action>Run validation hook unit tests: uv run pytest backend_v2/tests/unit/hooks/test_validation.py -v</action>
    <action>Run math utils unit tests: uv run pytest backend_v2/tests/unit/utils/test_math_utils.py -v</action>
    <action>Run backend audit loop on modified hook: uv run python scripts/backend_audit_loop.py backend_v2/hooks/validation.py --test</action>
    <action>Run planner output audit: uv run python scripts/audit_planner_output.py --epic docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md --plan-dir docs/epic/tasks_EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication</action>
  </validation_gate>
</execution_protocol>
```
