<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
</required_context_rules>

# Task Tracker: Autonomous Multi-Tier Ablation Benchmark Platform (`scripts/run_ablation_benchmark.py`)

## Session Handover Context
- **Achieved**: Fully implemented and validated the Autonomous Multi-Tier Ablation Benchmark Platform across all 4 phases. Created `scripts/ablation_live_executor.py` with 100% typed Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`), 4-Layer Clean Stack prompt builders, and `AblationLiveExecutor` engine. Modernized `scripts/run_ablation_benchmark.py` and `scripts/run_e2e_variance_test.py` with full parameter parity, structured ASCII telemetry banner, and shared model telemetry resolution. Implemented comprehensive test suites (23 tests in `test_ablation_live_executor.py` with 94% coverage; 29 tests in `test_run_ablation_benchmark.py` with 94% coverage; 91 tests in `test_run_e2e_variance_test.py` with 90% coverage). Passed all 10 stages of the backend audit loop on all targets with AST strict guardrails. Synchronized `.agents/rules/04_directory_reference.md`, `ki_ai_testing_standards.md`, and `docs/tiede.md` Section 8.5.
- **Learned**: Lexical verification requires individual segment floor of 30 characters when $m > 1$ per `MIN_MULTI_SEGMENT_FLOOR_CHARS` in `AnchorValidationService`. Cluster bootstrap requires at least 2 distinct clusters for non-parametric resampling. Reasoning models strip sampling parameters at adapter level, requiring exploratory variation to be driven via thinking budgets.
- **Remaining**: None. Plan execution is 100% complete and verified against Universal Quality Gates.
- **Resume Command**: Completed.

## Execution Steps
### Phase 1: Technical Debt Cleanup & DTO Contract Lock
- [x] Step 1.1: PRE_IMPLEMENTATION_TECHNICAL_DEBT_SWEEP: Modernize `AblationBenchmarkRunner.__init__`, eradicate banned lazy fallback operators (`or "both"`), update `verify_offline_ablation_benchmark` caller, purge `table_5_markdown` legacy alias and `format_table_5_markdown`, refactor trace loading in `run_configuration` via `TraceEvaluationRawDTO`, execute 7-item sweep on `resolve_model_telemetry`, modernize callers in `run_variance_test`, and modernize unit tests.
- [x] Step 1.2: DEFINE_LIVE_ABLATION_DTO_CONTRACTS: Define `AblationMode`, `AblationLiveExecutionConfigDTO`, `AblationPromptRequestDTO`, `AblationStructuredResponseDTO`, `AblationMonolithicItemDTO`, `AblationMonolithicResponseDTO`, `TraceEvaluationRawDTO`, `ModelTelemetryItemDTO` in `scripts/ablation_live_executor.py` / `scripts/run_ablation_benchmark.py`.
- [x] Step 1.3: ENVIRONMENT_TELEMETRY_AND_ADAPTER_SAMPLING_AUDIT: Refactor `resolve_model_telemetry` and `print_model_telemetry` in `scripts/run_e2e_variance_test.py` to hydrate typed `SystemConfigModelRegistry` and `ModelProfile`, reporting stripped sampling parameters for reasoning models.

### Phase 2: In-Process Async LLM Execution Engine
- [x] Step 2.1: IMPLEMENT_ABLATION_PROMPT_TEMPLATES: Implement Four-Layer Clean Stack prompt generators for the experimental configurations in `scripts/ablation_live_executor.py`.
- [x] Step 2.2: IMPLEMENT_ABLATION_LIVE_EXECUTOR: Implement `AblationLiveExecutor` class with in-process client initialization (`SystemRepositoryImpl`, `LLMClient.from_tier`), dual-client cross-model support, `asyncio.TaskGroup` + `asyncio.Semaphore`, `evaluate_atom_live` (Configs 1-4), and `evaluate_step_monolithic_live` (Config 5).

### Phase 3: CLI Driver Modernization & Telemetry Banner
- [x] Step 3.1: EXPAND_CLI_ARGUMENT_PARSER: Update `build_arg_parser` in `scripts/run_ablation_benchmark.py` with 100% parameter parity (`inputs_target`, `--inputs`, `--workflow`, `--num-runs`, `--mode`, `--dev`, `--sample`, `--tier`, `--strategies`, `--providers`, `--compare-providers`, `--compare-strategies`, `--output-file`, `--output-format`, `--concurrency`, `--export-manifest` group).
- [x] Step 3.2: INTEGRATE_TELEMETRY_BANNER_AND_ORCHESTRATOR: Implement structured ASCII banner and execution dispatcher in `run_ablation_benchmark` routing by `AblationMode` (`live`, `replay`, `in-silico`).
- [x] Step 3.3: DOCUMENT_TEST_DIFFERENCES_IN_MODULE_HEADERS: Expand module-level docstrings in `scripts/run_ablation_benchmark.py` and `scripts/run_e2e_variance_test.py` documenting the Dual Verification Architecture, Three Tiers of Scientific Honesty, Golden Standard, and Golden Pipeline.

### Phase 4: Test Harness & Directory Reference Registration
- [x] Step 4.1: IMPLEMENT_LIVE_EXECUTOR_UNIT_TESTS: Implement unit test suite in `backend_v2/tests/unit/scripts/test_ablation_live_executor.py` verifying all 5 configs, chimera handling, omission detection, and cross-model dispatch.
- [x] Step 4.2: UPDATE_RUN_ABLATION_BENCHMARK_UNIT_TESTS: Update CLI tests, table formatting tests, and synchronize telemetry unit tests in `backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py`.
- [x] Step 4.3: REGISTER_DIRECTORY_REFERENCES: Register `scripts/ablation_live_executor.py` and test file in `.agents/rules/04_directory_reference.md`.
- [x] Step 4.4: SYNCHRONIZE_KNOWLEDGE_ITEM_DOCUMENTATION: Document benchmark architecture and FinOps rules in `ki_ai_testing_standards.md`.
- [x] Step 4.5: SYNCHRONIZE_TIEDE_METHODOLOGY_DOCUMENTATION: Update Section 8.5 in `docs/tiede.md`.
