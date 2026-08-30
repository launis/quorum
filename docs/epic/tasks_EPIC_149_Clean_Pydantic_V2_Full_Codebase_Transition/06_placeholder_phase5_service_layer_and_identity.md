# Phase 5: Service Layer, Utility Services & Service Tests (CONSUMERS SECOND)

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_domain_model_prompt_separation.md]</knowledge_item>
  <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_app_error_boundary.md]</knowledge_item>
</required_context_rules>

**Phase Title:** Phase 5: Service Layer, Utility Services & Service Tests (CONSUMERS SECOND)
**Objective:** Eliminate ALL `getattr(initiator, "organization_id", None)` reflection chains, `hasattr()` dynamic interface discovery, `.get()` lazy fallbacks, and `isinstance(..., dict)` parsing branches from `backend_v2/services/execution.py` and all utility / studio services, modernizing service unit tests atomically to ensure 100% Pydantic V2 strictness.

**Source Reference:** @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L287-L306] (Phase 5: Service Layer, Utility Services & Service Tests)

**Target Files** (exhaustive — 11 production files + test suites):
- `[MODIFY]` @[backend_v2/services/execution.py#L81-L143] (`create_execution_record`)
- `[MODIFY]` @[backend_v2/services/execution.py#L146-L1388] (`ExecutionService`)
- `[MODIFY]` @[backend_v2/services/usage_service.py#L21-L321] (`UsageService`)
- `[MODIFY]` @[backend_v2/services/llm_task_executor.py#L29-L65] (`_validate_non_empty_payload`)
- `[MODIFY]` @[backend_v2/services/llm_task_executor.py#L68-L397] (`LLMTaskExecutor`)
- `[MODIFY]` @[backend_v2/services/translation_service.py#L17-L72] (`translate_text`)
- `[MODIFY]` @[backend_v2/services/source_verification_service.py#L37-L254] (`SourceVerificationService`)
- `[MODIFY]` @[backend_v2/services/blueprint.py#L62-L697] (`BlueprintTransformer`)
- `[MODIFY]` @[backend_v2/services/studio/system_config_service.py#L23-L453] (`StudioSystemConfigService`)
- `[MODIFY]` @[backend_v2/services/studio/workflow_service.py#L38-L635] (`StudioWorkflowService`)
- `[MODIFY]` @[backend_v2/services/studio/output_profile_service.py#L22-L275] (`StudioOutputProfileService`)
- `[MODIFY]` @[backend_v2/services/studio/prompt_block_service.py#L26-L257] (`StudioPromptBlockService`)
- `[MODIFY]` @[backend_v2/services/mcp/mcp_tool_loop.py#L130-L509] (`execute_tool_loop`)
- `[MODIFY]` @[backend_v2/tests/unit/services/test_execution.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_blueprint.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_blueprint_sdui_crash.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_llm_task_executor.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_translation_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_source_verification_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_matrix_domain_parser.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/studio/test_system_config_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/studio/test_workflow_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/studio/test_output_profile_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/studio/test_prompt_block_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/sdui/adapters/test_authenticity_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/sdui/adapters/test_metadata_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/sdui/adapters/test_printable_sources_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/sdui/adapters/test_variance_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py]

---

### Five-Axis Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Execution Service**<br>`@[backend_v2/services/execution.py#L146-L1388]` | Banned 11 instances of `getattr(initiator, "organization_id", None)`, `hasattr(s, "score")`, `getattr(internal_logic, ...)`, `getattr(block, "text", None)`, and `.get()` fallbacks in Excel export. | Access `initiator.organization_id` directly on typed `TokenData`. Evaluate `s.score is not None` on typed `ScaleOption`. Pass typed `ErrorCodes` to `AppException`. | Eliminate reflection fallback dictionaries and dynamic string resolution loops. | `uv run python scripts/_ast_guardrails.py backend_v2/services/execution.py --strict` passes with 0 violations. |
| **Usage & LLM Task Executor**<br>`@[backend_v2/services/usage_service.py#L21-L321]`<br>`@[backend_v2/services/llm_task_executor.py#L68-L397]` | Banned `hasattr(self.audit_repo, ...)` dynamic method discovery, `getattr(model_pricing_config, "caching_strategy", None)`, `getattr(usage, "cached_tokens", 0)`, `hasattr(e, "token_usage")`, and `.get()` fallbacks. | Access `audit_repo` methods directly via Protocol contract. Access `PricingConfig.caching_strategy` and `TokenUsage.cached_tokens` via typed dot-notation. | Prune duck-typing checks on guaranteed Protocol and Pydantic V2 models. | `uv run pytest backend_v2/tests/unit/services/test_usage_service.py backend_v2/tests/unit/services/test_llm_task_executor.py` passes 100%. |
| **Translation, Verification & MCP**<br>`@[backend_v2/services/translation_service.py#L17-L72]`<br>`@[backend_v2/services/source_verification_service.py#L37-L254]`<br>`@[backend_v2/services/mcp/mcp_tool_loop.py#L130-L509]` | Banned `eval_res.get("content", "")`, `translated_res.get("content", "")`, and `repo = getattr(executor, "repository", None)`. | Unpack structured `tuple[str, TokenUsage]` directly from `execute_chat_task()`. Pass `repository: BaseRepository \| None = None` explicitly. | Remove double-parsing wrappers around `execute_chat_task` responses. | `uv run pytest backend_v2/tests/unit/services/test_translation_service.py backend_v2/tests/unit/services/test_source_verification_service.py` passes 100%. |
| **Blueprint & Presentation**<br>`@[backend_v2/services/blueprint.py#L62-L697]` | Banned `hasattr(strat_enum, "value")`, `isinstance(user_obj, dict)`, and raw dictionary token extraction loops. | Access `strat_enum.value` on typed `ScoringStrategy`. Access `user_obj.name` on typed `User` domain model. | Eliminate legacy dictionary fallbacks in user and scoring resolution. | `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py` passes 100%. |
| **Studio Config, Workflow & Profiles**<br>`@[backend_v2/services/studio/system_config_service.py#L23-L453]`<br>`@[backend_v2/services/studio/workflow_service.py#L38-L635]`<br>`@[backend_v2/services/studio/output_profile_service.py#L22-L275]`<br>`@[backend_v2/services/studio/prompt_block_service.py#L26-L257]` | Banned `getattr(initiator.role, "value", ...)` and `.get()` fallback chains during workflow/step/profile cloning. | Access `initiator.role.value` directly. Mutate typed `I18nText` models using typed dictionary comprehensions. Accept strictly typed `OutputProfile` domain models. | Eliminate `model_dump(mode="json")` roundtrip cycles followed by untyped dictionary mutations. | `uv run python scripts/_ast_guardrails.py backend_v2/services/studio/ --strict` passes with 0 violations. |
| **Atomic Service Test Suites**<br>`@[backend_v2/tests/unit/services/]` | Banned untyped mock dicts, missing `target_locale="fi"` in `ExecutionRecord` fixtures, and skipped test assertions. | Instantiate typed `TokenData`, `ExecutionRecord(target_locale="fi")`, `ExecutionMetadata`, and `TokenUsage` fixtures. | Eliminate ad-hoc dictionary mock helpers across test suites. | `uv run python scripts/backend_audit_loop.py backend_v2/services/ backend_v2/tests/unit/services/ --test` passes >90% coverage. |

---

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK &amp; PRE-FLIGHT VERIFICATION">
    <action>Look backward: Verify codebase state left by Phase 4. Verify orchestrator strategies use strict DTOs and all repositories return typed Pydantic V2 domain models.</action>
    <action>Look forward: Verify service layer consumers against AST Guardrails report (QGR001 reflection, QGR002 .get(), QGR007 ConfigDict, QGR009 ErrorCodes) across all files in @[backend_v2/services/].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md]) and the Tracker document (@[docs/epic/EPIC_149_tracker.md]), and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <step id="1" name="PRE-IMPLEMENTATION TECHNICAL DEBT CLEANUPS &amp; AST REMEDIATION">
    <action>Pre-emptively remediate discovered AST violations and modernize legacy test fixtures across @[backend_v2/tests/unit/services/]:
      1. Fix `ExecutionRecord` fixture instantiations in @[backend_v2/tests/unit/services/test_blueprint.py], @[backend_v2/tests/unit/services/test_blueprint_sdui_crash.py], @[backend_v2/tests/unit/services/test_matrix_domain_parser.py], and @[backend_v2/tests/unit/services/sdui/adapters/] to include mandatory `target_locale="fi"` and `metadata=ExecutionMetadata(target_locale="fi")`.
      2. In @[backend_v2/services/llm_task_executor.py#L29-L65]: modernize `_validate_non_empty_payload` to validate message dictionaries using direct key access without `.get()` fallbacks.
      3. In @[backend_v2/services/mcp/mcp_tool_loop.py#L130-L509]: replace broad `except Exception:` handlers with structured logging and re-raising or specific exception trapping.</action>
    <constraint invariant="the_duct_tape_ban">Eliminate all silent exception handlers and legacy missing target_locale fixtures.</constraint>
  </step>

  <step id="2" name="EXECUTION SERVICE DUCK-TYPING ELIMINATION">
    <action>Refactor @[backend_v2/services/execution.py#L146-L1388]:
      1. Replace all 11 instances of `getattr(initiator, "organization_id", None)` with direct typed attribute access `initiator.organization_id`. `TokenData` natively guarantees typed `organization_id: str | None = None`.
      2. In `create_execution`: pass `organization_id=initiator.organization_id` directly to `ExecutionMetadata`, `create_execution_record`, and `arq_pool.enqueue_job`.
      3. In `generate_sdui_from_inputs`: replace `hasattr(s, "score")` with direct `s.score` evaluation (`s.score is not None`) on typed `ScaleOption` models.
      4. In Excel report export (`export_excel_report`): replace `getattr(internal_logic, "step_1_identify_premise", "")` and `getattr(internal_logic, "step_3_evaluate_anti_patterns", "")` with typed attribute access on `InternalLogic` or typed dict access. Replace `l10n.get()` calls with typed localization mappings.
      5. In `get_sdui_view`: replace `getattr(block, "text", None)` with typed polymorphic matching or attribute checks on `MarkdownBlock` / `ParagraphBlock`.
      6. In `ExecutionService` constructor and methods: ensure all `ErrorCodes` passed to `AppException` are typed Enum members (satisfying QGR009, specifically line 998).</action>
    <constraint invariant="zero_service_layer_fallbacks">Never use getattr(obj, key, default) or .get(key, default) in Service layer.</constraint>
    <constraint invariant="rfc7807_dual_reporting_mandate">All AppException instances must be preceded by structured logger.error and use ErrorCodes enum members.</constraint>
  </step>

  <step id="3" name="USAGE &amp; LLM TASK EXECUTOR SERVICE REFACTORING">
    <action>Refactor @[backend_v2/services/usage_service.py#L21-L321] and @[backend_v2/services/llm_task_executor.py#L68-L397]:
      1. In `UsageService`: eliminate `hasattr(self.audit_repo, "upsert_usage_aggregate")`, `hasattr(self.audit_repo, "get_usage_records")`, and `hasattr(self.audit_repo, "get_usage_aggregate")`. The `AuditRepository` protocol guarantees these methods natively.
      2. In `UsageService`: eliminate `getattr(model_pricing_config, "caching_strategy", None)`. `model_pricing_config` is strictly `PricingConfig` from LiteLLM registry; access `model_pricing_config.caching_strategy` directly. Pass typed `ErrorCodes` to `AppException` (lines 184, 238).
      3. In `LLMTaskExecutor`: replace `getattr(usage, "cached_tokens", 0)` and `getattr(usage, "total_tokens", 0)` with direct typed access on `TokenUsage` (`usage.cached_tokens`, `usage.total_tokens`).
      4. In `LLMTaskExecutor`: replace `getattr(validated_model, "contextual_override", False)` and `getattr(validated_model, "override_reason", ...)` with direct model attributes or typed DTO access.
      5. In `LLMTaskExecutor`: replace `hasattr(e, "token_usage")` with direct `e.token_usage` check on `LLMSchemaValidationError`.</action>
    <constraint invariant="the_duct_tape_ban">Eliminate all hasattr/getattr dynamic interface discovery.</constraint>
    <constraint invariant="litellm_pricing_registry_ssot_mandate">PricingConfig is the sole authoritative SSOT.</constraint>
  </step>

  <step id="4" name="TRANSLATION, VERIFICATION &amp; MCP TOOL LOOP REFACTORING">
    <action>Refactor @[backend_v2/services/translation_service.py#L17-L72], @[backend_v2/services/source_verification_service.py#L37-L254], and @[backend_v2/services/mcp/mcp_tool_loop.py#L130-L509]:
      1. In `translate_text`: `temp_executor.execute_chat_task()` returns `tuple[str, TokenUsage]`. Unpack `translated_str, _ = await temp_executor.execute_chat_task(...)` directly, eliminating `translated_res.get("content", "")` and broad exception handlers.
      2. In `SourceVerificationService`: `self.task_executor.execute_chat_task()` returns `tuple[str, TokenUsage]`. Unpack `eval_res_str, _ = await self.task_executor.execute_chat_task(...)` directly, eliminating `eval_res.get("content", "")` and extracting clean status string.
      3. In `execute_tool_loop`: replace `repo = getattr(executor, "repository", None)` with direct `getattr` removal by passing `repository: BaseRepository | None = None` explicitly or accessing `executor.repository` if defined on executor.</action>
    <constraint invariant="strict_attribute_integrity">Never convert strict dot-notation attribute access into dynamic getattr() fallbacks.</constraint>
    <constraint invariant="the_duct_tape_ban">Eliminate all isinstance(..., dict) parsing on structured return types.</constraint>
  </step>

  <step id="5" name="BLUEPRINT &amp; PRESENTATION SERVICE REFACTORING">
    <action>Refactor @[backend_v2/services/blueprint.py#L62-L697]:
      1. In `BlueprintTransformer`: replace `s_strat = strat_enum.value if hasattr(strat_enum, "value") else str(strat_enum)` with typed enum conversion `strat_enum.value` (since `LaxScoringStrategy` is typed `ScoringStrategy | str`).
      2. In user resolution: eliminate `isinstance(user_obj, dict)` branch and access `user_obj.name` directly on typed `User` domain model.
      3. Modernize MCP audit trace impact mapping: iterate directly over typed `StepOutputDTO` instances and typed payload models.</action>
    <constraint invariant="strict_enum_hydration_and_validation">Pass native Enum objects and access .value strictly for primitive serialization.</constraint>
    <constraint invariant="sdui_contract_fracture_prevention">Verify SDUI semantic parity after blueprint changes.</constraint>
  </step>

  <step id="6" name="STUDIO CONFIG, WORKFLOW &amp; PROFILE SERVICES REFACTORING">
    <action>Refactor @[backend_v2/services/studio/system_config_service.py#L23-L453], @[backend_v2/services/studio/workflow_service.py#L38-L635], @[backend_v2/services/studio/output_profile_service.py#L22-L275], and @[backend_v2/services/studio/prompt_block_service.py#L26-L257]:
      1. In `StudioSystemConfigService`: replace `getattr(initiator.role, "value", initiator.role)` with `initiator.role.value`.
      2. In `StudioSystemConfigService.clone_system_config`: replace `getattr(cloned_data["description"], "strip", None)` with typed string check `if isinstance(cloned_data.get("description"), str):`.
      3. In `StudioWorkflowService`: in `get_workflow_output_extensions`, `get_prompt_block_by_id` returns typed `PromptBlockBase`; check `isinstance(block, MatrixPromptBlock)` cleanly without `PromptBlockAdapter.validate_python(strict=False)` re-parsing.
      4. In `StudioWorkflowService.clone_workflow` &amp; `clone_step`: update I18nText mutation to use typed `I18nText` model methods or structured dictionary mutations on `wf.name.translations`, eliminating `.get()` fallback chains.
      5. In `StudioOutputProfileService.save_output_profile`: eliminate `if isinstance(data, dict):` fallback; accept strictly typed `OutputProfile` domain model.
      6. In `StudioOutputProfileService.clone_output_profile`: update deep copying of `I18nText` name translations to use strict Pydantic V2 typing without `.get()`.
      7. In `StudioPromptBlockService.clone_prompt_block`: update label translation cloning with typed `I18nText` access without `.get()`.</action>
    <constraint invariant="strict_enum_hydration_and_validation">Access enum .value directly on typed UserRole / LLMPlatformType.</constraint>
    <constraint invariant="dynamic_vs_static_localization_ssot_mandate">I18nText fields resolved via typed domain model methods.</constraint>
  </step>

  <step id="7" name="ATOMIC SERVICE TEST SUITE MODERNIZATION &amp; QUALITY GATES">
    <action>Modernize all unit test suites in @[backend_v2/tests/unit/services/]:
      1. In @[backend_v2/tests/unit/services/test_execution.py]: eliminate raw dictionary mocks and replace with typed `TokenData`, `ExecutionRecord`, and `ExecutionMetadata` instances.
      2. In @[backend_v2/tests/unit/services/test_blueprint.py] &amp; @[backend_v2/tests/unit/services/test_blueprint_sdui_crash.py]: update all `ExecutionRecord` fixtures with mandatory `target_locale="fi"` and valid Pydantic V2 schemas.
      3. In @[backend_v2/tests/unit/services/test_llm_task_executor.py]: eliminate `hasattr`/`getattr` mock workarounds; assert clean `TokenUsage` accumulation and `AppException` Fail-Fast.
      4. In @[backend_v2/tests/unit/services/test_translation_service.py]: mock `execute_chat_task` returning `("Translated Text", TokenUsage())`.
      5. In @[backend_v2/tests/unit/services/test_source_verification_service.py]: mock `execute_chat_task` returning `("VERIFIED", TokenUsage())`.
      6. In @[backend_v2/tests/unit/services/studio/test_system_config_service.py], @[backend_v2/tests/unit/services/studio/test_workflow_service.py], @[backend_v2/tests/unit/services/studio/test_output_profile_service.py], and @[backend_v2/tests/unit/services/studio/test_prompt_block_service.py]: replace legacy dict fixtures with typed Pydantic V2 domain model fixtures.
      7. In @[backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py]: update tests to pass typed `TokenUsage` and `CitationExtractionResult` models.
      8. Run full backend quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/services/ backend_v2/tests/unit/services/ --test`.
      9. Run SDUI semantic parity gate: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.</action>
    <constraint invariant="fragmented_quality_gates_prevention">Run full backend audit loop across all services and tests.</constraint>
    <constraint invariant="anti_happy_path_mandate">Verify at least 2 negative test cases per service endpoint (AppException on invalid inputs).</constraint>
  </step>

  <dod_checklist>
    - [x] `getattr(initiator, "organization_id", None)` replaced with direct `initiator.organization_id` access across all 11 instances in @[backend_v2/services/execution.py].
    - [x] `hasattr()` interface discovery removed in @[backend_v2/services/usage_service.py], @[backend_v2/services/llm_task_executor.py], and @[backend_v2/services/blueprint.py].
    - [x] All `.get()` and `isinstance(..., dict)` fallbacks eliminated from studio, translation, and source verification services.
    - [x] Service unit tests in @[backend_v2/tests/unit/services/] modernized atomically with `target_locale="fi"`.
    - [x] Quality gate passes: `uv run python scripts/backend_audit_loop.py backend_v2/services/ --test`.
    - [x] SDUI semantic parity gate passes: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.
  </dod_checklist>

  <touched_artifacts>
    <backend>@[backend_v2/services/execution.py]</backend>
    <backend>@[backend_v2/services/usage_service.py]</backend>
    <backend>@[backend_v2/services/llm_task_executor.py]</backend>
    <backend>@[backend_v2/services/translation_service.py]</backend>
    <backend>@[backend_v2/services/source_verification_service.py]</backend>
    <backend>@[backend_v2/services/blueprint.py]</backend>
    <backend>@[backend_v2/services/studio/output_profile_service.py]</backend>
    <backend>@[backend_v2/services/studio/prompt_block_service.py]</backend>
    <backend>@[backend_v2/services/studio/workflow_service.py]</backend>
    <backend>@[backend_v2/services/studio/system_config_service.py]</backend>
    <backend>@[backend_v2/services/mcp/mcp_tool_loop.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `backend_v2/worker.py` in Phase 5 (reserved for Phase 6).
    - Do NOT re-introduce `getattr`/`hasattr` fallback reflection.
  </anti_targets>

  <validation_gate>
    uv run python scripts/backend_audit_loop.py backend_v2/services/ backend_v2/tests/unit/services/ --test
  </validation_gate>
</execution_protocol>
