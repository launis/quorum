<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
  <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
  <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
</required_context_rules>

# EPIC 157: Zero Permissive Typing & Test Persistence Modernization

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
> - **Domain-Driven Design (DDD) Value Objects & Primitive Obsession Eradication (Evans, Fowler, 2025-2026)**: Replacing untyped dictionaries (`dict[str, Any]`, `list[dict]`) with immutable, frozen Pydantic V2 Value Objects ensures domain invariant self-validation and compile-time contract enforcement.
> - **Hexagonal Architecture (Ports & Adapters) Boundary Isolation (Cockburn, 2025)**: Permissive dictionaries and raw JSON representations are quarantined strictly to driving and driven physical infrastructure drivers enumerated by the path-based `BOUNDARY_EXEMPTION_FILES` set, guaranteeing that the core domain remains completely untainted by transport-layer serialization details.
> - **Stateful Test Double Isolation (Beck, Fowler, Google Testing on the Toilet)**: Replacing deceptive mocks (`AsyncMock(return_value={...})`) with stateful In-Memory Fakes (`InMemoryRepository`) eliminates green-test deception, enforcing real state persistence verification across roundtrip CRUD lifecycles.

---

## 1. Goal Description & Background (Objective & Problem Statement)

### 1.1 Objective
The objective of EPIC 157 is to eliminate permissive typing, primitive obsession, and deceptive persistence testing across the Quorum architecture. Specifically and exhaustively:
1. Replace the `basename`-keyed exemption sets `BOUNDARY_EXEMPTION_FILES` (`scripts/_ast_guardrails.py:84`) and `LOCKED_PHYSICAL_DRIVERS` (`scripts/audit_dict_eradication.py:38`) with ONE `frozenset[str]` of 15 workspace-relative POSIX paths named `BOUNDARY_EXEMPTION_FILES`, defined in `scripts/_ast_guardrails.py` and imported by `scripts/audit_dict_eradication.py`. Delete the `LOCKED_PHYSICAL_DRIVERS` symbol.
2. Remediate all 86 non-exempt violations reported by `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` (127 total minus 41 inside the 6 exempted physical boundary files), applying the Field Classification Gate defined in Section 2.4 to every field.
3. Eradicate the mock-emulation layer `DynamicRepoMethod` and `InMemoryBlueprintTransformerRepository` (`backend_v2/tests/fakes/in_memory_repositories.py:1747-1890`), migrating all 861 `<repo>.<method>.return_value` / `.side_effect` assignments across 49 test files, 68 `<repo>.<attr> = AsyncMock(...)` / `MagicMock(...)` / `Mock(...)` attribute replacements across 12 test files, 7 `patch.object(<repo>, ...)` / `monkeypatch.setattr(<repo>, ...)` calls across 3 test files, and 11 `AsyncMock`/`MagicMock` repository fixtures across 10 test files to typed seeding of stateful In-Memory fakes. All 46 test files importing `InMemoryBlueprintTransformerRepository` are allocated to Phases 3-7.
4. Harden AST Guardrail `QGR014` to statically prohibit (a) fixture functions returning `AsyncMock`/`MagicMock`/`Mock` under repository identifiers, (b) `.return_value` / `.side_effect` assignments on repository identifiers, (c) attribute-replacement assignments `<repo>.<attr> = AsyncMock(...)` / `MagicMock(...)` / `Mock(...)`, and (d) `patch.object(<repo>, ...)` / `monkeypatch.setattr(<repo>, ...)` calls, landing at FATAL severity only after the last migration batch.
5. Integrate `scripts/audit_warning_baseline.py` (Residual Debt Ceiling Ledger) as Stage 9/10 of `scripts/backend_audit_loop.py` in Phase 1 to guarantee no residual bypass or suppression vector grows, and integrate `scripts/audit_dict_eradication.py backend_v2 --strict` as Stage 10/10 in Phase 8; Phase 11 extends the Stage 10 targets to `backend_v2 scripts`.
6. Synchronize the Flutter producers and consumers of retyped wire fields (`mock_inputs`, `input_schema`) under Full-Duplex DTO Parity.
7. Eradicate the three residual deceptive persistence vectors that census A/B/C and the existing `QGR014` do not detect: census D (821 keyword-injected repository mocks `<repo>=AsyncMock(...)` / `MagicMock(...)` / `Mock(...)` inside `HookDependencies(...)`, `HookContext(...)`, and executor constructor calls across 32 test files), census F (50 string-target `patch("<module>.<RepositoryClass>")` calls across 6 worker test files, invisible to the existing `QGR014` branch because it fires only when `"service"` occurs in the file path), and census K (25 hand-written ad-hoc repository classes across 7 hook test files, injected through `cast(Any, ...)`). Migration runs in Phases 3-6; `QGR014` gains detections (e), (f), and (g) in Phase 7.
8. Eradicate every type-checker and linter suppression in `backend_v2/` and `scripts/`: 76 `# noqa` comment tokens (38 `QGR001`/`QGR012` suppressions in 7 files, 38 Ruff suppressions in 23 files), 804 `cast(Any, ...)` calls across 13 files, 409 `# type: ignore` comments across 155 files, the `[[tool.mypy.overrides]]` block disabling `warn_unused_ignores`, and 5 stale entries in `per-file-ignores`. Delete the AST inline suppressor from `scripts/_ast_guardrails.py` and `scripts/backend_audit_loop.py`. `scripts/audit_dict_eradication.py` rejects `# noqa` and `cast(Any, ...)` at FATAL severity from Phase 9 and `# type: ignore` plus unapproved config suppressions from Phase 10.
9. Extend dict eradication beyond production modules: 304 `dict[str, Any]` / `dict[str, object]` lines across 80 test files, 86 lines across 9 `scripts/` files, and 10 production sites across 6 files that `scripts/audit_dict_eradication.py` cannot see (no `Mapping` / `MutableMapping` detection; basename `name.startswith("test_")` exclusion of the production module `backend_v2/core/test_settings.py`).
10. Retype the 193 non-codec `Map<String, dynamic>` occurrences across 48 hand-written `client_app_v2/lib/` files to Freezed DTOs mirroring backend contracts, or to `Map<String, Object?>` for OPEN-JSON fields. The 67 codec signatures (`fromJson(Map<String, dynamic> json)`, `Map<String, dynamic> toJson()`) across 34 files are the `json_serializable` boundary contract and are retained. Prohibit loose maps and lint suppressions unconditionally by introducing `DGR005` in `scripts/_dart_guardrails.py` and promoting `DGR001`, `DGR004`, and `DGR005` to unconditional FATAL severity in `scripts/flutter_audit_loop.py` (Phase 12).
11. Delete the 7 unconditional `@pytest.mark.skip` tests and remove the 4 `@pytest.mark.xfail` markers in Phase 1, so that no test reports green or expected-failure without executing its assertions. Introduce `QGR026` in `scripts/_ast_guardrails.py` to statically prohibit unconditional skip/xfail decorators, module-level skip/xfail markers, and `pytest.xfail()` calls at FATAL severity from Phase 1 onward.

### Quantitative Scope & Archetype Breakdown Table
Baseline command: `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` (2026-10-05). Global metric split: 98 naked dict annotations, 21 Primitive Obsession nested dicts, 5 duck-typing checks, 3 reflection calls = **127 violations**. Per-file totals are exact; per-file metric splits are produced by the same command.

| Archetype Category | Target Files (violations per file) | Files | Violations | Disposition |
| :--- | :--- | :--- | :--- | :--- |
| **Domain & DTO Models** | `models/domain/`: `analyst.py` (1), `archivist.py` (1), `base.py` (2), `integrity.py` (1), `mcp.py` (3), `metrics.py` (1), `security.py` (1), `system_config.py` (4), `validation.py` (2), `xai.py` (2); `models/dtos/`: `atom_evaluation.py` (2), `mcp.py` (1), `prompt_context.py` (1), `studio.py` (4), `system.py` (1), `trace.py` (1); `models/llm.py` (2) | 17 | 30 | Remediate (Phase 1) |
| **Core, LLM & Orchestration Services** | `core/rate_limit.py` (1), `core/registry.py` (4), `llm/caching_service.py` (2), `llm/client.py` (1), `llm/ingress_pipeline.py` (2), `llm/mock_data.py` (2), `llm/schema_builder.py` (3), `services/orchestrator/matrix_explanation_service.py` (1), `services/orchestrator/matrix_reducer.py` (1) | 9 | 17 | Remediate (Phase 1: reducer + explanation service as 1-hop consumers; Phase 2: remainder) |
| **Execution Hooks** | `hooks/linguistics.py` (1), `hooks/scoring/matrix_hook.py` (3), `hooks/scoring/passivity_hook.py` (1), `hooks/source_verification_hook.py` (1) | 4 | 6 | Remediate (Phase 2) |
| **System Exception RFC 7807** | `exceptions.py` (14) | 1 | 14 | Remediate (Phase 2) |
| **Database Seeder Boundary** | `seed/run_seed.py` (11) | 1 | 11 | Remediate (Phase 1 cleanup) |
| **OpenAPI Generation Script** | `scripts/generate_openapi.py` (1) | 1 | 1 | Remediate (Phase 1 cleanup) |
| **Repository Implementations** | `database/repositories/execution.py` (3), `database/repositories/workflow.py` (1) | 2 | 4 | Remediate (Phase 1 cleanup) |
| **Test Fakes & Guardrail Tests (reflection)** | `tests/fakes/in_memory_repositories.py` (1), `tests/unit/test_ast_engine_dispatch_guardrails.py` (2) | 2 | 3 | Remediate (Phase 1 cleanup: guardrail test; Phase 7: fake) |
| **Physical Boundary Drivers & SDK Adapters** | `database/driver.py` (5), `llm/adapters/anthropic_adapter.py` (12), `llm/adapters/base_adapter.py` (11), `llm/adapters/deepseek_adapter.py` (2), `llm/adapters/mock_adapter.py` (4), `llm/adapters/openai_adapter.py` (7) | 6 | 41 | Exempt via path-based `BOUNDARY_EXEMPTION_FILES` (Phase 1). The unified 15-path set hides 160 violations in total: these 41 plus 119 currently hidden by basename `LOCKED_PHYSICAL_DRIVERS` (`llm/provider.py` 51, `database/wrapper.py` 32, `database/tinydb_driver.py` 8, `llm/adapters/vertex_adapter.py` 7, `database/firestore_driver.py` 6, `llm/adapters/ai_studio_adapter.py` 6, `llm/handler.py` 5, `logging_config.py` 4). 12 of the 160 are `prepare_caching_payload` signatures rewritten in Phase 2 and verified by the Phase 2 adapter gate |
| **TOTALS** | **all paths relative to `backend_v2/`** | **43** | **127** | **86 remediated, 41 exempted** |

### Test Persistence Census Table
Census command A (PowerShell): `Get-ChildItem backend_v2/tests -Recurse -Filter "*.py" | Select-String -Pattern "\b(\w*repo\w*)\.\w+\.(return_value|side_effect)\s*=" | Where-Object { $_.Matches[0].Groups[1].Value -notmatch "report|response" }`.

Census command B (attribute replacement): `Get-ChildItem backend_v2/tests -Recurse -Filter "*.py" | Select-String -Pattern "\b(\w*repo\w*)\.\w+\s*=\s*(AsyncMock|MagicMock|Mock)\(" | Where-Object { $_.Matches[0].Groups[1].Value -notmatch "report|response" }`.
Census command C (object patching): `Get-ChildItem backend_v2/tests -Recurse -Filter "*.py" | Select-String -Pattern "\b(patch\.object|monkeypatch\.setattr)\(\s*(\w*repo\w*)\s*," | Where-Object { $_.Matches[0].Groups[2].Value -notmatch "report|response" }`.
Census command I (emulation-fake imports): `Get-ChildItem backend_v2/tests -Recurse -Filter "*.py" | Where-Object { $_.FullName -notmatch "\\tests\\fakes\\|\\tests\\unit\\fakes\\" } | Select-String -Pattern "InMemoryBlueprintTransformerRepository" -List`.

| Pattern | Files | Occurrences | Disposition |
| :--- | :--- | :--- | :--- |
| `.return_value` / `.side_effect` assignments on repository identifiers (`InMemoryBlueprintTransformerRepository` instances) | 49 | 861 | Phases 3-6 |
| Census B: attribute replacements `<repo>.<attr> = AsyncMock(...)` / `MagicMock(...)` / `Mock(...)` | 12 | 68 (Phase 3: 13, Phase 4: 45, Phase 5: 10) | Phases 3-5 |
| Census C: `patch.object(<repo>, ...)` / `monkeypatch.setattr(<repo>, ...)` | 3 | 7 | Phase 4 |
| Fixture functions returning `AsyncMock`/`MagicMock` repositories | 10 | 11 fixtures (Phase 3: 3, Phase 4: 6, Phase 5: 2) | Phases 3-5 |
| Driver-level persistence mock (`mock_driver: AsyncMock`) in `tests/unit/test_repositories_v2.py` | 1 | 7 tests | Phase 4 |
| Census I: test files importing `InMemoryBlueprintTransformerRepository` | 46 (45 via census I + `tests/unit/fakes/test_in_memory_repositories.py`) | 46 | Phases 3-6 migrate 45 files (including 4 import-only files with 0 census A hits); Phase 7 migrates the fake's own test and deletes the class |
| `dict_to_obj(` helper (`tests/unit/services/test_blueprint.py:141`) | 8 | 8 | Phase 4 |

### Residual Permissive Typing & Test Bypass Ledger (Verification Census)
Baseline 2026-10-05. Every row is a verification anchor: its census command MUST return the Target value at the gate of the Eradicating Phase and at every subsequent phase gate, and no phase may increase any count. The per-file allocation of every row is recorded in @[docs/epic/EPIC_157_residual_ledger.md].

Census command D (keyword-injected repository mocks; sum of matches): `Get-ChildItem backend_v2/tests -Recurse -Filter "*.py" | Select-String -Pattern "\b(\w*repo\w*)=(AsyncMock|MagicMock|Mock)\(" -AllMatches | Where-Object { $_.Matches[0].Groups[1].Value -notmatch "report|response" }`.
Census command F (string-target repository patches): `Get-ChildItem backend_v2/tests -Recurse -Filter "*.py" | Where-Object { $_.FullName -notmatch "\\tests\\unit\\scripts\\" } | Select-String -Pattern 'patch\(\s*["''][\w\.]*\.(\w*Repository)["'']'`.
Census command K (ad-hoc repository classes): `Get-ChildItem backend_v2/tests -Recurse -Filter "*.py" | Where-Object { $_.FullName -notmatch "\\tests\\fakes\\|\\tests\\unit\\fakes\\|test_ast_engine_dispatch_guardrails" } | Select-String -Pattern "^\s*class\s+(\w*Repo\w*)\b" | Where-Object { $_.Matches[0].Groups[1].Value -notmatch "Report|Response" }`.
Census command X (`cast(Any, ...)`; sum of matches): `Get-ChildItem backend_v2, scripts -Recurse -Filter "*.py" | Select-String -Pattern 'cast\(\s*Any\b' -AllMatches`.
Census command N (`# noqa` comment tokens): the `Unauthorized # noqa Suppressions` line of `uv run python scripts/audit_dict_eradication.py backend_v2 scripts --strict` after the Phase 9 hardening. Only `tokenize` COMMENT tokens count; `# noqa` text inside string literals of guardrail test fixtures is not a comment. Baseline measured with the same `tokenize` rule.
Census command T (`# type: ignore`): `Get-ChildItem backend_v2, scripts -Recurse -Filter "*.py" | Select-String -Pattern "#\s*type:\s*ignore"`.
Census command P (naked dicts outside production modules): `Get-ChildItem backend_v2/tests, scripts -Recurse -Filter "*.py" | Select-String -Pattern "\b[Dd]ict\[\s*str\s*,\s*(Any|object)\s*\]"`.
Census command M (production `Mapping` sites plus `test_`-named production module dicts; sum of both commands): `Get-ChildItem backend_v2 -Recurse -Filter "*.py" | Where-Object { $_.FullName -notmatch "\\backend_v2\\tests\\" } | Select-String -Pattern "\b(Mutable)?Mapping\[\s*str\s*,\s*(Any|object)\s*\]"` and `Select-String -Path backend_v2/core/test_settings.py -Pattern "\b[Dd]ict\[\s*str\s*,\s*(Any|object)\s*\]"`. Baseline: 8 + 2 = 10; none of the 8 `Mapping` hits lies inside `BOUNDARY_EXEMPTION_FILES`.
Census command R (non-codec Dart maps; sum of matches): `Get-ChildItem client_app_v2/lib -Recurse -Filter "*.dart" | Where-Object { $_.Name -notmatch "\.(g|freezed)\.dart$" } | Select-String -Pattern "Map<String,\s*dynamic>" -AllMatches | Where-Object { $_.Line -notmatch "fromJson\(\s*Map<String,\s*dynamic>\s+\w+\s*\)|Map<String,\s*dynamic>\s+toJson\(" }`.
Census command S (unconditional skip / xfail markers): `Get-ChildItem backend_v2/tests -Recurse -Filter "*.py" | Select-String -Pattern "@pytest\.mark\.(skip|xfail)\b"`.

| ID | Pattern | Files | Occurrences | Eradicating Phase (occurrences) | Target | Enforcing Gate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| D | Keyword-injected repository mocks `<repo>=AsyncMock(...)` / `MagicMock(...)` / `Mock(...)` | 32 | 821 | Phase 3: 379, Phase 4: 269, Phase 5: 152, Phase 6: 21 | 0 | `QGR014` (e) |
| F | `patch("<module>.<RepositoryClass>")` bound to a mock | 6 | 50 | Phase 6: 50 | 0 | `QGR014` (f) |
| K | Ad-hoc repository classes in test modules | 7 | 25 classes | Phase 3: 25 | 0 | `QGR014` (g) |
| X | `cast(Any, ...)` | 13 | 804 | Phase 3: 792, Phase 5: 1, Phase 9: 11 | 0 | `audit_dict_eradication.py` call audit |
| N | `# noqa` comment tokens | 30 | 76 (38 `QGR001`/`QGR012` in 7 files; 38 Ruff `E501`/`F401`/`E402`/`F403` in 23 files) | Phase 9: 76 | 0 | `audit_dict_eradication.py` comment audit |
| T | `# type: ignore` | 155 | 409 (production 67 in 25 files, `scripts/` 4 in 3 files, tests 338 in 127 files) | Phase 10: 409 | 0 | `audit_dict_eradication.py` comment audit; mypy `warn_unused_ignores = true` globally |
| P | `dict[str, Any]` / `dict[str, object]` in tests and `scripts/` | 89 | 390 (tests 304 in 80 files, `scripts/` 86 in 9 files) | Phase 1: 5 (deletion of `backend_v2/tests/unit/llm/test_fallback_caching.py` 3 and `backend_v2/tests/unit/test_provider_rate_limit.py` 2), Phase 11: 385 | 0 | `audit_dict_eradication.py backend_v2 scripts --strict` |
| M | Production `Mapping[str, Any \| object]` sites and `test_`-named production module dicts | 6 | 10 | Phase 11: 10 | 0 | `audit_dict_eradication.py backend_v2 scripts --strict` |
| R | Non-codec `Map<String, dynamic>` in hand-written Dart | 48 | 193 | Phase 12: 193 | 0 | `DGR005` in `scripts/_dart_guardrails.py` and `scripts/flutter_audit_loop.py` |
| S | Unconditional `@pytest.mark.skip` / `@pytest.mark.xfail` | 7 | 11 (7 skip, 4 xfail) | Phase 1: 11 | 0 | `QGR026` in `scripts/_ast_guardrails.py` |

Recorded and retained (Section 2.6): 75 driver-level `get_driver` / `get_storage_driver` patches in 11 test files, 54 assertion-free test functions in 32 files (53 after the Phase 1 deletion of `backend_v2/tests/architecture/test_boundaries.py`), 13 environment-gated skips in 7 files, 67 Dart codec signatures in 34 files, non-persistence service and SDK doubles, and the 160 dict violations inside the 15 `BOUNDARY_EXEMPTION_FILES`.

### Change Footprint (Scope Size Verification)
Computed 2026-10-05 as the union of every MODIFY, DELETE, and NEW Target Boundary path of Phases 1-13 and the per-file sets of @[docs/epic/EPIC_157_residual_ledger.md] allocated to Phases 9-12 (census N to Phase 9, census T to Phase 10, census P and M to Phase 11, census R to Phase 12), excluding files deleted in Phase 1 from later sets. Column `First Touch` counts files not targeted by an earlier phase; its sum equals the unique total. The implementation plan and tracker MUST reproduce these per-phase file counts; a deviation triggers STOP and an Epic resync.

| Phase | Files | Production `backend_v2/` | Tests `backend_v2/tests/` | `scripts/` | Dart `client_app_v2/lib/` | `pyproject.toml` | First Touch |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 51 | 29 | 18 (4 deleted) | 4 | 0 | 0 | 51 |
| 2 | 26 | 23 | 3 | 0 | 0 | 0 | 26 |
| 3 | 30 | 0 | 30 | 0 | 0 | 0 | 29 |
| 4 | 23 | 0 | 23 | 0 | 0 | 0 | 22 |
| 5 | 20 | 0 | 20 | 0 | 0 | 0 | 20 |
| 6 | 15 | 0 | 15 | 0 | 0 | 0 | 15 |
| 7 | 5 | 0 | 4 | 1 | 0 | 0 | 3 |
| 8 | 6 | 0 | 1 | 2 | 3 | 0 | 4 |
| 9 | 38 | 7 | 25 | 6 | 0 | 0 | 24 |
| 10 | 158 | 25 | 128 | 4 | 0 | 1 | 105 |
| 11 | 96 | 6 | 79 | 11 | 0 | 0 | 47 |
| 12 | 52 | 0 | 1 | 3 | 48 | 0 | 48 |
| 13 | 1 | 0 | 0 | 1 | 0 | 0 | 0 |
| **Unique** | **394** | **77** | **249** | **19** | **48** | **1** | **394** |

File operations: 390 modified, 4 deleted, 0 new; 95 files are targeted by more than one phase. Eradicated occurrence volume: 3,847 individual sites, specifically and exhaustively: 86 dict-audit violations, 861 census A, 68 census B, 7 census C, 11 repository fixtures, 821 census D, 50 census F, 25 census K classes, 804 census X, 76 census N, 409 census T, 390 census P, 10 census M, 193 census R, 11 census S, 25 Dart lint suppressions (`// ignore:`).

### 1.2 Problem Statement
Verified root causes (2026-10-05 baseline):
- **Runtime Deserialization Failures**: Models declaring `meta: dict[str, Any]` or `data: dict[str, Any] | None` bypass static type checking in both Python (`mypy --strict`) and Flutter (`dart analyze`), leaking untyped payloads across API boundaries and causing silent runtime crashes when schema structures shift.
- **Mock-Emulation Fake (Root Cause of Deceptive Persistence)**: `InMemoryBlueprintTransformerRepository` overrides `__getattribute__` / `__setattr__` and wraps every method in `DynamicRepoMethod`, a `MagicMock` facade. It synthesizes non-existent methods that return `None`, bypasses the `IUnifiedWorkflowRepository` contract, and accepts raw dictionaries via `.return_value`. 861 assignments across 49 files rely on it. Existing `QGR014` (`scripts/_ast_guardrails.py:692-747`, `:1319-1341`) detects only `spec=I*Repository` mocks, `@patch` on repositories, and `repo = AsyncMock()` assignments, so this layer is invisible to the gate.
- **Census Blind Spots**: The census A regex and the hardened `QGR014` predicates (a)-(b) do not detect 68 attribute replacements (`exec_repo.get_execution = AsyncMock(return_value=rec)`) or 7 `patch.object` / `monkeypatch.setattr` calls on repositories. 4 test files (`backend_v2/tests/unit/test_dependencies.py`, `backend_v2/tests/unit/services/execution/test_override_service.py`, `backend_v2/tests/unit/llm/test_structured_retry.py`, `backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py`) import `InMemoryBlueprintTransformerRepository` with 0 census A hits; without explicit allocation, Phase 7 class deletion raises `ImportError` at the gate.
- **Residual Persistence Vectors**: `QGR014` (`scripts/_ast_guardrails.py:692-747`, `:1319-1341`) inspects no keyword argument, so 821 `exec_repo=MagicMock()` injections pass; its `patch()` branch fires only when `"service"` occurs in the test path, so 50 `patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository")` calls in worker tests pass; it inspects no class definition, so 25 ad-hoc repository classes returning raw `dict[str, Any]` (`MockRepoWaterfall` in `backend_v2/tests/unit/hooks/test_scoring.py`) pass. 792 of the 804 `cast(Any, ...)` calls exist solely to inject these ad-hoc classes into typed `HookDependencies` fields.
- **Suppression Debt**: `scripts/audit_dict_eradication.py` accepts any `# noqa: QGR` comment carrying a `[REASON: ...]` tag, contradicting the `the_zero_compromise_pledge` ban on `# noqa: QGR` suppressions; 38 such comments exist (`backend_v2/llm/provider.py` 27). No gate inspects `# type: ignore` or `cast(Any, ...)`. `pyproject.toml` overrides `warn_unused_ignores = false` for two database modules and excludes `backend_v2/tests/` from mypy, so all 338 test-side `# type: ignore` comments are inert.
- **Scripted Gate Blind Spots & Inline Suppressors**: `scripts/_ast_guardrails.py` contains an inline suppression engine (`CommentSuppressor` parsing `# noqa: QGRxxx [REASON: ...]`) and `scripts/backend_audit_loop.py` filters `v.is_suppressed` at line 400, creating an unauthorized escape hatch. Stage 4 scans only command-line `targets` rather than the global codebase, allowing regressions in untouched files to go unnoticed during single-file audits. `_is_test_file` in `scripts/_ast_guardrails.py:339-341` uses the heuristic `"tests" in path_parts or name.startswith("test_")`, accidentally classifying the production file `backend_v2/core/test_settings.py` as a test and exempting it from production AST rules. In `scripts/flutter_audit_loop.py`, `_dart_guardrails.py` runs with advisory severity unless `--strict` is explicitly passed on the CLI, allowing 66 Dart violations (including 25 `// ignore:` suppressions) to evade standard audit runs. `pyproject.toml` contains 5 dead entries in `per-file-ignores` targeting removed legacy files.
- **Dict Audit Blind Spots**: `_is_naked_dict_subscript` (`scripts/audit_dict_eradication.py:175-206`) matches only `dict` / `Dict`, so `Mapping[str, object]` and the duck-typing union `HookState | Mapping[str, Any]` (`backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py:240`) pass. `is_test` (`scripts/audit_dict_eradication.py:146`) excludes every basename starting with `test_`, so the production module `backend_v2/core/test_settings.py` is never scanned. Annotation checks skip every file under `tests/`, and `scripts/` is outside the Stage 10 target.
- **Client Permissive Maps**: 193 non-codec `Map<String, dynamic>` occurrences in 48 Flutter files bypass Freezed typing, including `contextVariables` and `executionTrace` in `client_app_v2/lib/features/execution/models/execution_record.dart`, whose backend counterparts are already typed (`context_variables: ContextVariablesDTO` and `execution_trace: list[ErrorTraceEvent | TombstoneEvent | TraceEvent]` in `backend_v2/models/domain/execution.py:197-199`).
- **Fake Test Bypasses**: 7 unconditional `@pytest.mark.skip` markers permanently disable 7 tests (4 whole files and 2 functions). 4 `@pytest.mark.xfail` markers in `backend_v2/tests/unit/hooks/test_scoring.py` carry the stale reason "MatrixDomainParser evaluates Enum as truthy": 2 tests XPASS, and 2 tests XFAIL because their fixtures pass raw evaluation dicts into `ExecutionInputsDTO.raw_inputs` (95 `ValidationError`s), not because of a parser defect (verified 2026-10-05 with `--runxfail`). No AST guardrail checks for `@pytest.mark.skip` or `@pytest.mark.xfail`.
- **Basename Exemption Leak**: Both exemption sets match on `Path(filepath).name`. `telemetry.py` currently exempts `backend_v2/api/routers/system/telemetry.py` and `backend_v2/models/dtos/telemetry.py`; `base_adapter.py` exempts `backend_v2/services/sdui/adapters/base_adapter.py`. These are domain files silently excluded from every QGR rule.
- **Exemption Set Drift**: `BOUNDARY_EXEMPTION_FILES` (6 entries) and `LOCKED_PHYSICAL_DRIVERS` (8 entries) diverged, so the same file is exempt in one scanner and fatal in the other.
- **Inconsistent Quality Gate Coverage**: `scripts/backend_audit_loop.py` runs 8 stages (7/8 clean imports, 8/8 DTO parity); neither `scripts/audit_warning_baseline.py` nor `scripts/audit_dict_eradication.py` is wired, so 127 violations accumulate undetected and debt ceilings are unmonitored.

---

## 2. Architectural Impact & Compliance Matrix

### 2.1 Deprecations & Sunset List (`What We Will REMOVE`)
Specifically and exhaustively, the following patterns and symbols are designated for permanent deprecation and removal. Column `Class` binds each row to the Field Classification Gate (Section 2.4): `CLOSED` = [NEW] or reused frozen DTO; `OPEN-JSON` = `dict[str, JsonValue]` (Pydantic recursive JSON type); `INGRESS` = `IngressInputValue` (`backend_v2/models/domain/inputs.py:84`); `DOMAIN` = `DomainInputValue` (`backend_v2/models/domain/inputs.py:89`); `REUSE` = existing SSOT model; `DROP` = intentionally dropped; `DELETE` = symbol removed.

| Symbol / Pattern | Target File | Class | Destination / Replacement | Phase |
| :--- | :--- | :--- | :--- | :--- |
| `LOCKED_PHYSICAL_DRIVERS: set[str]` (basename) | `@[scripts/audit_dict_eradication.py]` | DELETE | `from scripts._ast_guardrails import BOUNDARY_EXEMPTION_FILES` | 1 |
| `BOUNDARY_EXEMPTION_FILES: set[str]` (basename) | `@[scripts/_ast_guardrails.py]` | CLOSED | `BOUNDARY_EXEMPTION_FILES: frozenset[str]` of 15 workspace-relative POSIX paths (Section 2.2 item 1) | 1 |
| `validate_all_seed_collections -> dict[str, list[dict[str, Any]]]` and `seed_data: dict[str, Any]` | `@[backend_v2/seed/run_seed.py]` | CLOSED | [NEW] `ValidatedSeedBufferDTO` (one typed list field per seed collection) hydrated via `ValidatedSeedBufferDTO.model_validate_json(path.read_bytes())` | 1 |
| `dict[str, Any]` OpenAPI spec | `@[backend_v2/scripts/generate_openapi.py#L50]` | OPEN-JSON | `dict[str, JsonValue]` | 1 |
| Naked dict returns (3) | `@[backend_v2/database/repositories/execution.py]` | CLOSED | Typed domain models per `repository_reconstitution_mandate` | 1 |
| Naked dict return (1) | `@[backend_v2/database/repositories/workflow.py]` | CLOSED | Typed domain models per `repository_reconstitution_mandate` | 1 |
| `getattr(val.value, 'id', '')` (2) | `@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py#L311-L353]` | [DELETE] | `match` on typed `ast` node classes | 1 |
| `raw_extra: dict[str, Any] \| None` on `ProviderMetadataDTO` | `@[backend_v2/models/llm.py]` | OPEN-JSON | `dict[str, JsonValue] \| None` (provider-native payload) | 1 |
| `model_params: dict[str, Any]` on `AdHocTestRequest` | `@[backend_v2/models/llm.py]` | DROP | INTENTIONALLY DROPPED: 0 producers in `backend_v2/`, 0 `"model_params"` keys in `backend_v2/seed/seed_data.json`, 0 `model_params` / `modelParams` references in `client_app_v2/lib/` (verified 2026-10-05). Any new reference found at execution time triggers STOP and a `PERMISSION GRANTED` request | 1 |
| `trace: dict[str, Any]` (2: L350, L533) | `@[backend_v2/models/dtos/studio.py]` | REUSE | `StepSimulationTraceDTO` (promoted to typed DTO; permissive `dict[str, JsonValue]` strictly banned by `QGR027`) | 1 |
| `mock_inputs: dict[str, Any]` (2: L384, L482) | `@[backend_v2/models/dtos/studio.py]` | INGRESS | `dict[str, IngressInputValue]`; values proven by origin trace to be upstream step outputs bind to `dict[str, IngressInputValue \| DomainInputValue]` | 1 |
| `parameters: dict[str, Any]` (JSON Schema) | `@[backend_v2/models/dtos/mcp.py#L54]` | OPEN-JSON | `dict[str, JsonValue]` | 1 |
| `arguments: str \| dict[str, Any]` | `@[backend_v2/models/domain/mcp.py#L27]` | OPEN-JSON | `dict[str, JsonValue]`; JSON-string decoding moves to exempt boundary `backend_v2/llm/provider.py` | 1 |
| `provider_specific_fields: dict[str, Any] \| None` | `@[backend_v2/models/domain/mcp.py#L46]` | OPEN-JSON | `dict[str, JsonValue] \| None` | 1 |
| `result_data: dict[str, Any]` | `@[backend_v2/models/domain/mcp.py#L86]` | OPEN-JSON | `dict[str, JsonValue]` | 1 |
| `options: list[dict[str, Any]] \| None` | `@[backend_v2/models/domain/system_config.py#L70]` | CLOSED | [NEW] `list[SystemConfigOptionDTO] \| None` | 1 |
| `validation_rules: dict[str, Any] \| None` | `@[backend_v2/models/domain/system_config.py#L71]` | CLOSED | [NEW] `SystemValidationRulesDTO \| None`; sole producer `@[backend_v2/services/execution/ingress_service.py#L146-L250]` writes key `max` | 1 |
| `input_schema: dict[str, Any]` (JSON Schema) | `@[backend_v2/models/domain/system_config.py#L158]` | OPEN-JSON | `dict[str, JsonValue]` | 1 |
| `root: dict[str, Any]` | `@[backend_v2/models/domain/validation.py#L38]` | INGRESS | Origin trace binds `IngressInputValue` or `DomainInputValue` | 1 |
| `meta: dict[str, Any]` | `@[backend_v2/models/domain/validation.py#L98]` | CLOSED | [NEW] `ValidationContextMetadataDTO` when producer key-set is finite; otherwise `dict[str, JsonValue]` | 1 |
| `data: dict[str, Any] \| None` on `ReportResult` | `@[backend_v2/models/domain/xai.py]` | REUSE | `ReportDataDTO \| None` | 1 |
| `flat_report: dict[str, Any] \| None` on `XAIOutput` | `@[backend_v2/models/domain/xai.py]` | DROP | INTENTIONALLY DROPPED: field self-documents as legacy `extra='allow'` boundary; sole instantiation `MOCK_XAI_OUTPUT` (`backend_v2/llm/mock_data.py:257`) omits it; 0 `flat_report` keys in `backend_v2/seed/seed_data.json` and `data/db_v2.json`; sole `client_app_v2/lib/` hit is a code comment (`client_app_v2/lib/shared/widgets/result_dashboard.dart:726`). Any new reference found at execution time triggers STOP and a `PERMISSION GRANTED` request | 1 |
| `context: dict[str, Any] \| None` | `@[backend_v2/models/domain/base.py#L37]` | CLOSED | [NEW] `DomainExecutionContextDTO \| None` when producer key-set is finite; otherwise `dict[str, JsonValue] \| None` | 1 |
| `provider_metadata: dict[str, Any] \| None` | `@[backend_v2/models/domain/base.py]` | REUSE | `ProviderMetadataDTO \| None` (`backend_v2/models/llm.py:63`) | 1 |
| `dynamic_inputs: dict[str, Any]` | `@[backend_v2/models/domain/archivist.py]` | INGRESS | `dict[str, IngressInputValue]` (resolves input values while decoupling import cycle between archivist and inputs) | 1 |
| `dynamic_inputs: dict[str, Any]` | `@[backend_v2/models/domain/analyst.py]` | INGRESS | `dict[str, IngressInputValue]` (resolves input values while decoupling import cycle between analyst and inputs) | 1 |
| `evaluated_matrices: list[dict[str, JsonValue]]` | `@[backend_v2/models/dtos/atom_evaluation.py#L50]` | CLOSED | REUSE check against `backend_v2/models/dtos/context_variables.py`; else [NEW] `list[EvaluatedMatrixRefDTO]` | 1 |
| `raw_extensions: list[dict[str, JsonValue]]` | `@[backend_v2/models/dtos/atom_evaluation.py#L54]` | CLOSED | [NEW] `list[RawXAIExtensionDTO]` | 1 |
| `list[dict[str, JsonValue]]` consumer of `evaluated_matrices` | `@[backend_v2/services/orchestrator/matrix_reducer.py#L116]` | CLOSED | Same DTO as `atom_evaluation.py` | 1 |
| `dict[str, Any]` local | `@[backend_v2/services/orchestrator/matrix_explanation_service.py#L170]` | CLOSED | Same DTO as `atom_evaluation.py` | 1 |
| `context_data: dict[str, object]` | `@[backend_v2/models/dtos/system.py#L79]` | OPEN-JSON | `dict[str, JsonValue]` (client error dump) | 1 |
| `root: dict[str, Any]` in `SanitizationInput` | `@[backend_v2/models/domain/security.py]` | INGRESS | `dict[str, IngressInputValue]` (origin trace mandatory) | 1 |
| `root: dict[str, Any]` in `MetricsInputPayload` | `@[backend_v2/models/domain/metrics.py]` | DOMAIN | Origin trace binds `IngressInputValue` or `DomainInputValue` | 1 |
| `raw_inputs: dict[str, Any] \| None` | `@[backend_v2/models/domain/integrity.py]` | INGRESS | `dict[str, IngressInputValue] \| None` (docstring: database-boundary envelope) | 1 |
| `metadata: dict[str, Any]` | `@[backend_v2/models/dtos/prompt_context.py#L11-L33]` | CLOSED | [NEW] DTO when producer key-set is finite; otherwise `dict[str, float]` when all values are scores; otherwise `dict[str, JsonValue]` | 1 |
| `model_validate` override with `extracted: dict[str, Any]` and `_step_metadata` / `step_metadata` dual-key fallback | `@[backend_v2/models/dtos/trace.py#L157-L194]` | [DELETE] | Override removed; single canonical key. Pre-condition: `Select-String -Path data/db_v2.json -Pattern '"_step_metadata"'` count recorded; non-zero count triggers STOP and a user decision | 1 |
| `details: dict[str, Any] \| None` | `@[backend_v2/exceptions.py]` | OPEN-JSON | `dict[str, JsonValue] \| None` (RFC 7807 extension members); blast radius (scratch mypy probe 2026-10-05) = 32 errors in 5 files: 27 in `backend_v2/exceptions.py` (invariant typed locals `dict[str, str]`, `dict[str, ErrorCodes]`, `dict[str, object]`, `dict[str, str \| None]` inside subclass constructors), 1 in `backend_v2/database/repositories/components/prompt_block.py`, 2 in `backend_v2/services/ingress/smart_ingress_resolver.py`, 1 in `backend_v2/hooks/validation.py`, 1 in `backend_v2/hooks/input_processing.py` | 2 |
| `def to_problem_detail -> dict[str, Any]` | `@[backend_v2/exceptions.py]` | CLOSED | [NEW] `ProblemDetailDTO` with exhaustive fields `type: str`, `title: str`, `status: int`, `detail: str`, `instance: str \| None`, `extensions: dict[str, JsonValue]`, serialized at the network boundary via `.model_dump(mode="json", exclude_none=True)` to preserve the wire shape consumed by `client_app_v2/lib/core/error/app_exception.dart`; test callers `backend_v2/tests/unit/test_exceptions.py` (2); callers `@[backend_v2/main.py#L314-L342]`, `@[backend_v2/main.py#L441-L470]`, `@[backend_v2/core/rate_limit.py#L21-L50]` | 2 |
| `dict[str, dict[float, LevelStatsDTO]]`, `dict[str, dict[str, ExecutionStatus]]`, `dict[str, dict[str, list[str]]]` (3 parallel maps) | `@[backend_v2/hooks/scoring/matrix_hook.py#L83-L564]` | CLOSED | [NEW] `dict[str, MatrixAggregationStateDTO]` (one DTO with 3 typed fields) when the 3 outer keys share the matrix-ID domain; otherwise one [NEW] DTO per map | 2 |
| `tuple[list[LLMMessageDTO] \| list[dict[str, Any]], dict[str, Any]]` (`prepare_caching_payload`) | `@[backend_v2/llm/caching_service.py#L35-L61]` | CLOSED | [NEW] `CachingPayloadResultDTO` owned by `BaseLLMAdapter.prepare_caching_payload` contract | 2 |
| Naked dict / PO annotations | `@[backend_v2/hooks/linguistics.py]`, `@[backend_v2/hooks/scoring/passivity_hook.py]`, `@[backend_v2/hooks/source_verification_hook.py]`, `@[backend_v2/llm/client.py]`, `@[backend_v2/llm/ingress_pipeline.py]`, `@[backend_v2/llm/schema_builder.py]`, `@[backend_v2/core/registry.py]`, `@[backend_v2/core/rate_limit.py]` | CLOSED | Classification Gate per annotation; `linguistics.py` binds [NEW] `LinguisticAnalysisDTO` | 2 |
| `MOCK_REGISTRY: dict[type[Any], Any]` | `@[backend_v2/llm/mock_data.py]` | CLOSED | `dict[type[BaseModel], BaseModel]` | 2 |
| `def get_fallback_data(key: str) -> dict[str, Any]` | `@[backend_v2/llm/mock_data.py]` | CLOSED | Returns typed `BaseModel` mock instances | 2 |
| `class DynamicRepoMethod` (`MagicMock` facade) | `@[backend_v2/tests/fakes/in_memory_repositories.py#L1747-L1835]` | [DELETE] | None (test setup seeds state via typed repository write methods) | 7 |
| `class InMemoryBlueprintTransformerRepository` (`__getattribute__` / `__setattr__` method synthesis) | `@[backend_v2/tests/fakes/in_memory_repositories.py#L1838-L1889]` | [DELETE] | `InMemoryUnifiedWorkflowRepository` (`backend_v2/tests/fakes/in_memory_repositories.py:1283`) | 7 |
| `getattr(self, method_name, None)` in `inject_fault` | `@[backend_v2/tests/fakes/in_memory_repositories.py#L128-L133]` | [DELETE] | Positive fault registry keyed by the bound method `__name__` | 7 |
| `def dict_to_obj(d: Any) -> Any` | `@[backend_v2/tests/unit/services/test_blueprint.py#L141-L164]` | [DELETE] | Typed domain model construction (`Workflow(...)`, `Step(...)`) | 4 |
| `def mock_repo() -> AsyncMock` | `@[backend_v2/tests/unit/test_epic66_multi_provider.py#L12-L14]` | [DELETE] | `InMemoryUnifiedWorkflowRepository` | 3 |
| `def mock_repo() -> AsyncMock` | `@[backend_v2/tests/unit/test_handler.py#L31-L34]` | [DELETE] | `InMemoryUnifiedWorkflowRepository` | 3 |
| `def mock_repository() -> AsyncMock` | `@[backend_v2/tests/unit/hooks/test_interaction_hook.py#L24-L26]` | [DELETE] | `InMemorySystemRepository` | 3 |
| `def mock_repository() -> AsyncMock` | `@[backend_v2/tests/unit/test_security.py#L20-L22]` | [DELETE] | `InMemorySystemRepository` | 4 |
| `def mock_repository() -> AsyncMock` | `@[backend_v2/tests/unit/services/test_chat_parser.py#L20-L23]` | [DELETE] | `InMemorySystemRepository` | 4 |
| `def mock_output_profile_repo() -> AsyncMock` | `@[backend_v2/tests/unit/services/studio/test_output_profile_service.py#L18-L20]` | [DELETE] | `InMemoryOutputProfileRepository` | 4 |
| `def mock_workflow_repo() -> AsyncMock`, `def mock_output_profile_repo() -> AsyncMock`, `def mock_prompt_block_repo() -> AsyncMock` | `@[backend_v2/tests/unit/services/studio/test_workflow_service.py#L42-L44]`, `@[backend_v2/tests/unit/services/studio/test_workflow_service.py#L47-L49]`, `@[backend_v2/tests/unit/services/studio/test_workflow_service.py#L52-L54]` | [DELETE] | `InMemoryWorkflowRepository`, `InMemoryOutputProfileRepository`, `InMemoryPromptBlockRepository` (conftest fixtures `fake_workflow_repo`, `fake_output_profile_repo`, `fake_prompt_block_repo`) | 4 |
| `mock_driver: AsyncMock` driver-level persistence mock | `@[backend_v2/tests/unit/test_repositories_v2.py]` | [DELETE] | Real `TinyDBDriver(db_client)` (`backend_v2/database/tinydb_driver.py:26`) over a pytest `tmp_path` database | 4 |
| `def mock_repo() -> MagicMock` | `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py#L20-L22]` | [DELETE] | `InMemoryUnifiedWorkflowRepository` | 5 |
| `def mock_repos() -> dict[str, Any]` | `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py#L19-L57]` | [DELETE] | `InMemoryUnifiedWorkflowRepository` | 5 |
| 861 `<repo>.<method>.return_value` / `.side_effect` assignments | 49 files enumerated in Phases 3-6 | [DELETE] | Typed seeding through `IUnifiedWorkflowRepository` write methods; faults through `inject_fault()` | 3-6 |
| 68 `<repo>.<attr> = AsyncMock(...)` / `MagicMock(...)` / `Mock(...)` attribute replacements (census B) | 12 files enumerated in Phases 3-5 | [DELETE] | Typed seeding through in-memory fake write methods; faults through `inject_fault()`; the 3 `repo._increment_version = MagicMock(...)` partial mocks in `backend_v2/tests/unit/database/repositories/components/` replaced by version roundtrip assertions over a real `TinyDBDriver` on `tmp_path` | 3-5 |
| 821 keyword-injected repository mocks `<repo>=AsyncMock(...)` / `MagicMock(...)` / `Mock(...)` (census D) | 32 files enumerated in Phases 3-6 and @[docs/epic/EPIC_157_residual_ledger.md] | [DELETE] | Conftest in-memory fakes (`fake_workflow_repo`, `fake_prompt_block_repo`, `fake_output_profile_repo`, `fake_system_repo`) and `InMemory*Repository` instances from `backend_v2/tests/fakes/in_memory_repositories.py` passed to `HookDependencies`, `HookContext`, and executor constructors | 3-6 |
| 50 `patch("<module>.<RepositoryClass>")` mocks (census F) | 6 worker test files enumerated in Phase 6 | [DELETE] | `patch("<module>.<RepositoryClass>", return_value=<InMemory*Repository instance>)` seeded through typed write methods | 6 |
| 25 ad-hoc repository classes (census K) and their 792 `cast(Any, ...)` injections | `@[backend_v2/tests/unit/hooks/test_scoring.py]` (15), `@[backend_v2/tests/unit/hooks/test_input_processing.py]` (4), `@[backend_v2/tests/unit/test_input_processing.py]` (2), `@[backend_v2/tests/unit/hooks/test_dlq_guard.py]` (1), `@[backend_v2/tests/unit/hooks/test_metadata.py]` (1), `@[backend_v2/tests/unit/hooks/test_references.py]` (1), `@[backend_v2/tests/unit/hooks/test_security.py]` (1) | [DELETE] | `InMemory*Repository` fakes typed against the `backend_v2/database/interfaces.py` Protocols; no `cast` | 3 |
| `[REASON: ...]` authorization of `# noqa: QGR` comments | `@[scripts/audit_dict_eradication.py]` | [DELETE] | Every `# noqa` comment token is a violation | 9 |
| `CommentSuppressor` class and `# noqa: QGRxxx [REASON: ...]` parsing | `@[scripts/_ast_guardrails.py#L205-L322]` | [DELETE] | AST inline suppression eradicated; all QGR rules evaluated unconditionally | 9 |
| `is_suppressed` filtering in Stage 4 and baseline ledger | `@[scripts/backend_audit_loop.py#L400]`, `@[scripts/audit_warning_baseline.py#L83]` | [DELETE] | Unsuppressed list equals raw violations list; no suppression filter | 9 |
| 38 `# noqa: QGR001` / `# noqa: QGR012` comments | `@[backend_v2/llm/provider.py]` (27), `@[backend_v2/llm/adapters/base_adapter.py]` (5), `@[backend_v2/database/firestore_driver.py]` (1), `@[backend_v2/database/tinydb_driver.py]` (1), `@[backend_v2/logging_config.py]` (1), `@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py]` (2), `@[backend_v2/tests/fakes/in_memory_repositories.py]` (1) | [DELETE] | Third-party attribute reads through Pydantic V2 adapter DTOs validated with `model_validate(obj, from_attributes=True)`; SDK exception attributes through `isinstance` on the concrete SDK exception class followed by direct attribute access | 9 |
| 38 Ruff `# noqa` comments (`E501`, `F401`, `E402`, `F403`) | 23 files enumerated in @[docs/epic/EPIC_157_residual_ledger.md] | [DELETE] | Line wrapping (`E501`); PEP 484 explicit re-export `from x import Y as Y` (`F401`); top-of-module imports (`E402`); explicit named imports (`F403`) | 9 |
| `exec_record = cast(Any, exec_record_raw)` and 10 residual test `cast(Any, ...)` calls | `@[backend_v2/services/orchestrator/strategies/llm.py]`, 4 test files enumerated in Phase 9 | [DELETE] | `ExecutionRecord.model_validate(...)` at the persistence boundary; typed test construction | 9 |
| 409 `# type: ignore` comments and `[[tool.mypy.overrides]]` with `warn_unused_ignores = false` | 155 files enumerated in @[docs/epic/EPIC_157_residual_ledger.md]; `@[pyproject.toml#L131-L136]` | [DELETE] | Type-correct code; negative tests build invalid input through `Model.model_validate({...})`; `[[tool.mypy.overrides]]` deleted; `warn_unused_ignores = true` globally; the 20 `[prop-decorator]` sites (`backend_v2/settings.py` 18, `backend_v2/models/domain/overseer.py` 2) resolve through ONE `disable_error_code = ["prop-decorator"]` entry (Section 2.2 item 7) | 10 |
| 5 dead `per-file-ignores` entries | `@[pyproject.toml#L98-L101]`, `@[pyproject.toml#L116]` | [DELETE] | Removed from `tool.ruff.lint.per-file-ignores` | 10 |
| 390 `dict[str, Any]` / `dict[str, object]` lines in tests and `scripts/` | 89 files enumerated in @[docs/epic/EPIC_157_residual_ledger.md] | OPEN-JSON / CLOSED | `dict[str, JsonValue]` for JSON payload fixtures; existing domain DTOs for typed fixtures | 11 |
| `Mapping[str, object]` (7), `HookState \| Mapping[str, Any]` (1), `dict[str, Any]` in a `test_`-named production module (2) | `@[backend_v2/hooks/input_processing.py]` (2), `@[backend_v2/services/orchestrator/strategies/llm.py]` (2), `@[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]` (2), `@[backend_v2/services/ingress/pdf_chat_extractor.py]` (1), `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]` (1), `@[backend_v2/core/test_settings.py]` (2) | CLOSED / OPEN-JSON | Field Classification Gate per site; `context_builder.py` accepts `HookState` only | 11 |
| 193 non-codec `Map<String, dynamic>` occurrences | 48 files enumerated in @[docs/epic/EPIC_157_residual_ledger.md] | CLOSED / OPEN-JSON | Freezed DTOs mirroring backend CLOSED models (verified by `scripts/audit_dto_parity.py`); `Map<String, Object?>` for backend OPEN-JSON fields | 12 |
| 25 hand-written Dart `// ignore:` / `// ignore_for_file:` comments (DGR004) | 23 files in `client_app_v2/lib/` | [DELETE] | Lint suppressions removed; underlying issues fixed; DGR004 promoted to unconditional FATAL | 12 |
| 7 unconditional `@pytest.mark.skip` tests | Files `@[backend_v2/tests/architecture/test_boundaries.py]`, `@[backend_v2/tests/unit/test_epic_61_hardening.py]`, `@[backend_v2/tests/unit/test_provider_rate_limit.py]`, `@[backend_v2/tests/unit/llm/test_fallback_caching.py]`; functions `test_aspirational_html_escape` in `@[backend_v2/tests/unit/test_ast_domain_security_guardrails.py]` and `test_all_ok_matrices_have_exactly_three_claims` in `@[backend_v2/tests/unit/test_matrix_data_integrity.py]` | [DELETE] | INTENTIONALLY DROPPED: permanently skipped tests execute no assertion; their skip reasons cite obsolete legacy architecture or unimplemented features | 1 |
| 4 `@pytest.mark.xfail` markers | `@[backend_v2/tests/unit/hooks/test_scoring.py]` (`test_scoring_matrix_namespace_isolation`, `test_scoring_regular_tda_path_bypasses_namespace_check`, `test_failed_atom_with_override_does_not_inflate_score`, `test_matrix_scoring_hook_illegal_override_penalty`) | [DELETE] | Markers removed; the 2 XFAIL tests receive typed `ExecutionInputsDTO.raw_inputs` fixtures. An assertion failure after fixture migration is a production defect and triggers STOP and a `PERMISSION GRANTED` request (behavioral change) | 1 |
| 7 `patch.object(<repo>, ...)` / `monkeypatch.setattr(<repo>, ...)` calls (census C) | `@[backend_v2/tests/unit/services/studio/test_system_config_service.py]` (5), `@[backend_v2/tests/unit/test_repo_deletion.py]` (1), `@[backend_v2/tests/unit/services/studio/test_prompt_block_service.py]` (1) | [DELETE] | Absent-entity state expressed by not seeding `InMemorySystemRepository` / `InMemoryPromptBlockRepository`; failures through `inject_fault()` | 4 |

### 2.2 Retained SSOT Invariants (`What We Will RETAIN`)
Specifically and exhaustively:
1. **Path-Based Physical Boundary SSOT (`BOUNDARY_EXEMPTION_FILES`)**: ONE `frozenset[str]` defined in `scripts/_ast_guardrails.py` and imported by `scripts/audit_dict_eradication.py`. Membership is evaluated as `Path(filepath).resolve().relative_to(WORKSPACE_ROOT).as_posix() in BOUNDARY_EXEMPTION_FILES`. The set is exhaustively: `backend_v2/database/tinydb_driver.py`, `backend_v2/database/firestore_driver.py`, `backend_v2/database/driver.py`, `backend_v2/database/wrapper.py`, `backend_v2/llm/provider.py`, `backend_v2/llm/handler.py`, `backend_v2/logging_config.py`, `backend_v2/core/telemetry.py`, `backend_v2/llm/adapters/base_adapter.py`, `backend_v2/llm/adapters/vertex_adapter.py`, `backend_v2/llm/adapters/ai_studio_adapter.py`, `backend_v2/llm/adapters/openai_adapter.py`, `backend_v2/llm/adapters/anthropic_adapter.py`, `backend_v2/llm/adapters/deepseek_adapter.py`, `backend_v2/llm/adapters/mock_adapter.py`. Files losing their accidental basename exemption (`backend_v2/models/dtos/telemetry.py`, `backend_v2/api/routers/system/telemetry.py`, `backend_v2/services/sdui/adapters/base_adapter.py`) are remediated in Phase 1. **Admission Ratchet**: the 9 members absent from the pre-Epic AST exemption set (`backend_v2/database/driver.py`, `backend_v2/database/wrapper.py`, `backend_v2/llm/handler.py`, `backend_v2/llm/adapters/vertex_adapter.py`, `backend_v2/llm/adapters/ai_studio_adapter.py`, `backend_v2/llm/adapters/openai_adapter.py`, `backend_v2/llm/adapters/anthropic_adapter.py`, `backend_v2/llm/adapters/deepseek_adapter.py`, `backend_v2/llm/adapters/mock_adapter.py`) MUST report 0 AST guardrail violations when scanned with an empty exemption set (baseline 2026-10-05: 0 for all 9). Membership therefore never licenses new QGR000, QGR003, QGR023, QGR024, or QGR025 violations in these files.
2. **Strongly Typed Registers**: High-performance O(1) hash maps utilizing strict domain key-value types (`dict[str, Workflow]`, `dict[str, Step]`, `dict[str, AtomEvaluationResultDTO]`, `dict[str, LevelStatsDTO]`) are fully retained.
3. **ExecutionInputsDTO & Input Value Unions**: `ExecutionInputsDTO.raw_inputs: Mapping[str, DomainInputValue]` (`backend_v2/models/dtos/hook_state.py:48`), `IngressInputValue` and `DomainInputValue` (`backend_v2/models/domain/inputs.py:84-89`) remain the SSOT for dynamic Studio-authored inputs. No per-workflow Python classes are generated.
4. **Router Unit Test Isolation**: FastAPI router unit tests (`backend_v2/tests/unit/api/routers/execution/test_executions.py`, `backend_v2/tests/unit/api/routers/execution/test_reports.py`) retain isolated service mocks (`mock_execution_service`, `mock_report_service`) to verify HTTP ingress routing, status codes, and RBAC. These are service mocks, not persistence mocks; the hardened `QGR014` repository-identifier predicate excludes the `report` and `response` tokens exactly as the existing predicate at `scripts/_ast_guardrails.py:1326-1327`.
5. **Fault Injection API**: `BaseInMemoryRepository.inject_fault()` (`backend_v2/tests/fakes/in_memory_repositories.py:128`) is retained as the sole mechanism for simulating persistence failures; only its reflection lookup is replaced.
6. **Dart Codec Signature Boundary**: The 67 `fromJson(Map<String, dynamic> json)` / `Map<String, dynamic> toJson()` signatures across 34 Freezed model files are retained. `json_serializable` generates `_$XFromJson(Map<String, dynamic> json)` and requires this exact parameter type; the signatures are the Dart counterpart of `Model.model_validate(raw)` at the network boundary.
7. **Central `prop-decorator` Configuration**: mypy cannot type decorators stacked on `@property` (the `@computed_field` over `@property` pattern documented by Pydantic V2). The error code `prop-decorator` fires exclusively for this construct and never relaxes value typing, so the 20 inline suppressions are replaced by ONE `disable_error_code = ["prop-decorator"]` entry in `[tool.mypy]` of `pyproject.toml`. No other mypy error code may be disabled.
8. **Non-Persistence Test Doubles**: `AsyncMock` / `MagicMock` doubles of injected services, LLM clients, and SDK clients remain governed by `partial_mocking_srp_ban` (mock the injected service class). `QGR014` applies exclusively to repository identifiers, to repository classes resolved from `backend_v2/database/interfaces.py` and `backend_v2/database/repositories/`, and to ad-hoc repository classes.

### 2.3 5-Column Architectural Directive Table
Specifically and exhaustively, the following architectural directives govern the execution of this Epic across all five System 2 dimensions:

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Physical Boundary SSOT** (`scripts/_ast_guardrails.py`, `scripts/audit_dict_eradication.py`) | Banned basename matching (`Path(filepath).name in ...`) that exempts any file sharing a name. Banned two divergent exemption sets. Banned exempting files under `backend_v2/models/`, `backend_v2/services/`, `backend_v2/hooks/`, `backend_v2/api/`. | ONE `frozenset[str]` `BOUNDARY_EXEMPTION_FILES` of 15 workspace-relative POSIX paths, imported by identity into `audit_dict_eradication.py`. | Deleted `LOCKED_PHYSICAL_DRIVERS` symbol; no regex or glob discovery. | `backend_v2/tests/unit/scripts/test_ast_guardrails.py`: (1) every set member exists on disk; (2) a fixture file `models/dtos/telemetry.py` is NOT exempt; (3) no member starts with `backend_v2/models/`, `backend_v2/services/`, `backend_v2/hooks/`, `backend_v2/api/`. `backend_v2/tests/unit/scripts/test_audit_dict_eradication.py`: `audit_dict_eradication.BOUNDARY_EXEMPTION_FILES is _ast_guardrails.BOUNDARY_EXEMPTION_FILES`. Admission ratchet in `test_ast_guardrails.py`: each of the 9 newly admitted paths (Section 2.2 item 1) scanned through `scan_file_for_guardrails` with `BOUNDARY_EXEMPTION_FILES` monkeypatched to `frozenset()` returns 0 violations. |
| **Domain & DTO Models with 1-hop consumers** (17 model files; consumers `backend_v2/models/dtos/context_variables.py`, `backend_v2/services/orchestrator/engines/synthesis_engine.py`, `backend_v2/services/orchestrator/matrix_reducer.py`, `backend_v2/services/orchestrator/matrix_explanation_service.py`, `backend_v2/services/execution/ingress_service.py`, `backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py`, `backend_v2/tests/unit/services/execution/test_ingress_service.py`) | Banned `dict[str, Any]`, `dict[str, object]`, `list[dict[...]]`, `dict[..., dict[...]]`. Banned unauthorized `dict[..., JsonValue]` in internal domain models and execution traces. Banned closed `extra="forbid"` DTOs invented for open JSON Schema / provider payloads. Banned assigning `DomainInputValue` to ingress-origin values without origin trace. Banned schema change without same-phase consumer migration. | Field Classification Gate (Section 2.4). Closed DTOs use `ConfigDict(strict=True, extra="forbid", frozen=True)`. Open JSON (`dict[str, JsonValue]`) is restricted strictly to approved external specifications in `OPEN_JSON_EXEMPTION_FILES`. Internal simulation traces promote to `StepSimulationTraceDTO`. Banned unauthorized `dict[..., JsonValue]` statically via AST rule `QGR027` (FATAL) and Metric 11 in `scripts/audit_dict_eradication.py`. Reuse `ProviderMetadataDTO`, `ReportDataDTO`, `StepSimulationTraceDTO`, `IngressInputValue`, `DomainInputValue`. | Pruned [NEW] DTOs: `LLMProviderRawExtraDTO`, `ModelParametersDTO`, `StudioMockInputsDTO`, `MCPParameterSchemaDTO`, `MCPInvocationArgumentsDTO`, `MCPProviderFieldsDTO`, `MCPResultPayloadDTO`, `SystemInputSchemaDTO`, `ProviderExecutionMetadataDTO`, `ClientErrorContextDTO`, `FlatReportSummaryDTO`, `RawSeedDatabaseDTO`. Dropped dead fields `model_params`, `flat_report`. | `uv run python scripts/audit_dict_eradication.py backend_v2/models --strict` = 0 with 0 unauthorized open JSON annotations. Per retyped field: 1 positive + 2 negative tests (malformed nested value raises `ValidationError`; unknown key raises `ValidationError` on CLOSED DTOs). Atomic test migration verifies `test_synthesis_engine.py` and `test_ingress_service.py#L226`. Global `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` green at phase end. |
| **Exceptions, Hooks, LLM & Core** (`backend_v2/exceptions.py`, 4 hooks, `backend_v2/llm/caching_service.py`, `backend_v2/llm/client.py`, 6 adapters, `backend_v2/core/registry.py`, `backend_v2/core/rate_limit.py`, `backend_v2/main.py`) | Banned dual-branch `ExceptionDetailsDTO \| dict[str, JsonValue]` contract. Banned union return `list[LLMMessageDTO] \| list[dict[str, Any]]`. Banned 3 parallel nested maps keyed by the same matrix ID. Banned passing raw DTOs to Starlette `JSONResponse` without `.model_dump(mode="json")`. | `AppException.details: dict[str, JsonValue] \| None`; `to_problem_detail() -> ProblemDetailDTO`; `BaseLLMAdapter.prepare_caching_payload() -> CachingPayloadResultDTO` with provider-native dict materialization confined to exempt adapter files and `backend_v2/llm/provider.py`. At network boundary in `main.py` and `rate_limit.py`, call `.model_dump(mode="json", exclude_none=True)` before passing to `JSONResponse` (preserves the omitted-`instance` wire shape). | Pruned [NEW] `ExceptionDetailsDTO`. Pruned `MatrixScoreLevelsDTO` + `MatrixStatusMapDTO` in favor of one `MatrixAggregationStateDTO` when outer keys coincide. Typed dynamic model field dictionaries in `registry.py`. | `uv run mypy backend_v2` = 0 errors after `details` retyping (baseline probe: 32 errors in 5 files, Section 2.1). `backend_v2/tests/unit/test_exceptions.py`: `ProblemDetailDTO` round-trip + non-JSON `details` value rejected by mypy fixture. `uv run python scripts/audit_dict_eradication.py backend_v2/llm/caching_service.py backend_v2/llm/client.py --strict` = 0. |
| **Test Persistence Doubles** (`backend_v2/tests/fakes/in_memory_repositories.py`, 49 census A files, 12 census B files, 3 census C files, 10 fixture files, 4 import-only files, `backend_v2/tests/unit/test_repositories_v2.py`) | Banned `DynamicRepoMethod`, `__getattribute__` method synthesis, `.return_value` / `.side_effect` on repositories, attribute replacement `<repo>.<attr> = AsyncMock(...)`, `patch.object` / `monkeypatch.setattr` on repositories, raw-dict seeding, `dict_to_obj`, `getattr` in `inject_fault`, driver mocks. | Stateful `InMemoryUnifiedWorkflowRepository` and per-entity fakes seeded through typed `IUnifiedWorkflowRepository` write methods; failures via `inject_fault()`; roundtrip `save` then `get` assertions; real `TinyDBDriver` over `tmp_path`. | Deleted `InMemoryBlueprintTransformerRepository` subclass; no replacement wrapper class; reuse conftest fixtures `fake_workflow_repo`, `fake_prompt_block_repo`, `fake_output_profile_repo`, `fake_system_repo`. | Per batch: census command scoped to the batch file list returns 0. Phase 7: hardened `QGR014` FATAL + `uv run python scripts/_ast_guardrails.py backend_v2/tests/ --strict` = 0; `Select-String -Path backend_v2 -Pattern "DynamicRepoMethod|InMemoryBlueprintTransformerRepository|dict_to_obj" -Recurse` = 0. `backend_v2/tests/unit/scripts/test_ast_guardrails.py`: 4 negative fixtures (fixture `return AsyncMock()`, `repo.get_step.return_value = {}`, `exec_repo.get_execution = AsyncMock(return_value=rec)`, `monkeypatch.setattr(system_repo, "get_model_registry", AsyncMock())`) raise `QGR014`; 2 positive fixtures (`mock_report_service.x.return_value`, `monkeypatch.setattr("backend_v2.services.execution.stream_service.get_settings", factory)`) pass. Census commands A, B, C, and I return 0 before Phase 7 starts. |
| **Universal Quality Gate & Client Parity** (`scripts/backend_audit_loop.py`, `client_app_v2/lib/features/studio/models/step_simulation.dart`, `client_app_v2/lib/features/studio/models/prompt_block_simulation.dart`, `client_app_v2/lib/features/studio/models/mcp_gateway.dart`) | Banned unwired scanners. Banned `Map<String, dynamic>` producers sending values the backend `IngressInputValue` union rejects. Banned client edits unrelated to retyped backend fields. | Stage 10/10 `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` returning exit 1 on any violation. Dart models mirror the backend union for `mock_inputs`; `input_schema` stays open JSON (`Map<String, Object?>`). | Removed `execution_record.dart` / `execution_metadata.dart` from scope (no backend counterpart changes; recorded in Section 2.6). | `backend_v2/tests/unit/scripts/test_backend_audit_loop.py` asserts Stage 10 invocation and non-zero exit propagation. `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build` and `uv run python scripts/audit_dto_parity.py` pass. |
| **Residual Persistence Vectors** (census D 32 files, census F 6 files, census K 7 files; `scripts/_ast_guardrails.py` QGR014) | Banned keyword-injected repository mocks, string-target repository-class patches bound to mocks, ad-hoc repository classes in test modules, `cast(Any, ...)` injection of non-conforming doubles. | Conftest in-memory fakes passed through `HookDependencies`, `HookContext`, and executor constructors; `patch("<module>.<RepositoryClass>", return_value=<InMemory*Repository instance>)` where the worker constructs its own repository. | No new fake classes. QGR014 (f) resolves repository class names from a positive set built from `backend_v2/database/interfaces.py` and `backend_v2/database/repositories/` instead of the substring predicate; (g) resolves interface method names from the `backend_v2/database/interfaces.py` Protocols. | Census D, F, K = 0 per batch. `test_ast_guardrails.py`: 3 negative fixtures (`HookDependencies(exec_repo=MagicMock())`, `patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository")`, class `MockRepoWaterfall` defining `get_output_profile_by_id`) raise `QGR014`; 2 positive fixtures (`patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=InMemoryUnifiedWorkflowRepository())`, `patch("backend_v2.database.repositories.execution.get_storage_driver")`) pass. |
| **Suppression & Cast Eradication** (`scripts/audit_dict_eradication.py`, `pyproject.toml`, 30 `# noqa` files, 13 `cast(Any, ...)` files, 155 `# type: ignore` files, `scripts/_ast_guardrails.py`, `scripts/backend_audit_loop.py`) | Banned `# noqa` of any code, `[REASON: ...]` suppression authorization, AST inline suppressors, `cast(Any, ...)`, `# type: ignore`, `warn_unused_ignores = false`. | Pydantic V2 adapter DTOs with `model_validate(obj, from_attributes=True)` for third-party attribute reads; `Model.model_validate({...})` for intentionally invalid test input; one central `prop-decorator` entry (Section 2.2 item 7); Config Suppression Ratchet in `audit_dict_eradication.py`. | No per-file allowlist; no new QGR rule identifier (detection extends the existing comment and call audits of `audit_dict_eradication.py`). | Census N, X, T = 0. `test_audit_dict_eradication.py`: negative fixtures `# noqa: QGR001 [REASON: x]`, `# noqa: E501`, `cast(Any, x)`, `# type: ignore[arg-type]` each produce exactly 1 violation; a positive fixture containing `"# noqa"` inside a string literal produces 0. `uv run mypy backend_v2` = 0 with `warn_unused_ignores = true`. |
| **Extended Dict Eradication** (tests 80 files, `scripts/` 9 files, production 6 files; `scripts/audit_dict_eradication.py`, `scripts/backend_audit_loop.py`, `scripts/_ast_guardrails.py`) | Banned `Mapping[str, Any]`, `Mapping[str, object]`, `MutableMapping[...]` with `Any` / `object` values, duck-typing union `HookState \| Mapping[str, Any]`, basename `test_` exclusion in AST and dict scanners, annotation-check exemption for tests, Stage 10 blindness to `scripts/`. | `is_test` and `_is_test_file` = path under `backend_v2/tests/`; `dict`, `Dict`, `Mapping`, `MutableMapping` with `Any` / `object` values flagged in every file outside `BOUNDARY_EXEMPTION_FILES`; Stage 10 runs `audit_dict_eradication.py backend_v2 scripts --strict`. | No separate test-only scanner. | Census P, M = 0; `audit_dict_eradication.py backend_v2 scripts --strict` = 0; `test_audit_dict_eradication.py` negative fixtures (`Mapping[str, object]` annotation; production module at path `backend_v2/core/test_settings.py`) produce violations. |
| **Client Permissive Map Eradication** (48 Flutter files; `scripts/_dart_guardrails.py`, `scripts/flutter_audit_loop.py`) | Banned non-codec `Map<String, dynamic>`; banned advisory-only Dart guardrails. | Freezed DTOs mirroring backend CLOSED models; `Map<String, Object?>` for OPEN-JSON fields. New rule `DGR005` in `_dart_guardrails.py`. Rules `DGR001`, `DGR004`, and `DGR005` enforced as unconditional FATAL in `flutter_audit_loop.py` without requiring `--strict`. | Codec signatures retained (Section 2.2 item 6); no hand-written JSON parsers. | Census R = 0; `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`; `uv run python scripts/audit_dto_parity.py`. |
| **Fake Test Bypass Eradication** (7 skip markers, 4 xfail markers; `scripts/_ast_guardrails.py`) | Banned unconditional `@pytest.mark.skip` / `@pytest.mark.xfail`; stale expected-failure reasons. | Environment-gated `pytest.mark.skipif` / runtime `pytest.skip` for missing credentials, input files, or SDKs remain (13 sites, Section 2.6). New AST rule `QGR026` (FATAL) in `_ast_guardrails.py` prohibits unconditional skip/xfail markers and `pytest.xfail()` calls. | No quarantine mechanism. | Census S = 0 from Phase 1; `QGR026` enforced in Stage 4 of `backend_audit_loop.py`. |
| **Permanent Scripted Gates & Residual Ratchet** (`scripts/backend_audit_loop.py`, `scripts/audit_warning_baseline.py`, `scripts/_ast_guardrails.py`, `scripts/audit_dict_eradication.py`, `scripts/_dart_guardrails.py`, `scripts/flutter_audit_loop.py`, `pyproject.toml`) | Banned inline AST suppression (`[REASON: ...]`), unratcheted debt ceilings, advisory Dart guardrails that permit bypasses without `--strict`, heuristic test file classification (`test_settings.py`), and unverified config-level ignore creep. | `audit_warning_baseline.py` implements a typed `ResidualDebtCeilingsDTO` with exact-equality ceiling assertions for every census category (D, F, K, X, N, T, P, M, R, S) wired as Stage 9/10 of `backend_audit_loop.py` from Phase 1. `QGR026` prohibits unconditional skip/xfail; `DGR005` prohibits loose Dart maps and `DGR001`/`DGR004`/`DGR005` become unconditional FATAL in `_dart_guardrails.py` and `flutter_audit_loop.py`; Config Suppression Ratchet in `audit_dict_eradication.py` asserts frozen approved sets for `pyproject.toml` and `analysis_options.yaml`. | No separate standalone ledger test runner (native script stages provide SSOT enforcement). | `backend_audit_loop.py` Stage 9/10 and Stage 10/10 fail fast if any ceiling is exceeded or violation detected. `flutter_audit_loop.py` fails on any DGR001, DGR004, or DGR005 violation without needing `--strict`. Admission ratchet in `test_audit_dict_eradication.py` parses `pyproject.toml` with `tomllib`. |

### 2.4 Compliance & Modernity Gates
Specifically and exhaustively, all changes must comply with:
1. **The Zero-Compromise Pledge**: 100% Pydantic V2 models configured with `ConfigDict(strict=True, extra="forbid", frozen=True)`.
2. **Universal Fail-Fast**: If required schema properties are omitted or malformed, the system triggers Fail-Fast `AppException` with RFC 7807 dual logging.
3. **Field Classification Gate (TRACE UPSTREAM before typing)**: For every retyped field the executing agent records the union of keys written at ALL producer sites (`grep_search` across `backend_v2/`, `backend_v2/seed/seed_data.json`, `client_app_v2/lib/`). Decision procedure: (a) finite key-set → `CLOSED` DTO, reusing an existing model when its fields are a superset; (b) key-set defined by an external open specification (JSON Schema, provider SDK payload, OpenAPI document, RFC 7807 extension members, client error dump) → `OPEN-JSON` `dict[str, JsonValue]` EXCLUSIVELY for files in the frozen `OPEN_JSON_EXEMPTION_FILES` SSOT whitelist; (c) internal simulation traces and models MUST use dedicated Pydantic V2 DTOs (specifically `StepSimulationTraceDTO` on `PromptBlockSimulationResponse` and `WorkflowSimulationResponse` in `studio.py`); (d) keys are Studio-authored input keys → `INGRESS` (`IngressInputValue`) or `DOMAIN` (`DomainInputValue`), with import cycles between models cleanly decoupled via `IngressInputValue`; (e) zero producers and zero consumers → `DROP` subject to the client/database reference check in the Sunset List. The decision and producer list are recorded in the implementation plan.
4. **Hardened QGR014 Enforcement**: Prohibits (a) fixture functions returning `AsyncMock`/`MagicMock`/`Mock`, (b) `.return_value` / `.side_effect` assignments, (c) attribute-replacement assignments `<repo>.<attr> = AsyncMock(...)` / `MagicMock(...)` / `Mock(...)`, (d) `patch.object(<repo>, ...)` / `monkeypatch.setattr(<repo>, ...)` calls on repository identifiers, (e) keyword arguments whose name satisfies `_is_repository_identifier` bound to `AsyncMock(...)` / `MagicMock(...)` / `Mock(...)`, (f) `patch("<module>.<Class>")` where `<Class>` belongs to the positive repository-class set resolved from `backend_v2/database/interfaces.py` and `backend_v2/database/repositories/` and neither `return_value` nor `new` is bound to an instance of a class defined in `backend_v2/tests/fakes/in_memory_repositories.py` (replacing the `"service" in self.filepath` condition and the substring target predicate at `scripts/_ast_guardrails.py:727-747`), and (g) class definitions in test modules outside `backend_v2/tests/fakes/` that define at least one method whose name belongs to the method-name set of the `backend_v2/database/interfaces.py` Protocols. ONE extracted predicate `_is_repository_identifier(name: str) -> bool` is shared by every identifier-based QGR014 detection site (`visit_Call`, `visit_Return`, `visit_Assign`); (f) and (g) use positive sets built once per scan.
5. **Orchestrator Permission Gate**: Phase 1 modifies `backend_v2/services/orchestrator/matrix_reducer.py`, `backend_v2/services/orchestrator/matrix_explanation_service.py`, and `backend_v2/services/orchestrator/engines/synthesis_engine.py`; Phases 9 and 11 modify `backend_v2/services/orchestrator/strategies/llm.py`, `backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py`, and `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py`. Per `orchestrator_god_object_fragility`, execution of each of these phases requires the user statement "PERMISSION GRANTED to mutate DAG Orchestrator ecosystem" and a full `backend_v2/` audit loop.
6. **Full-Duplex Parity**: Synchronization of shared models between `backend_v2/models/` and `client_app_v2/lib/` verified via `scripts/audit_dto_parity.py`.
7. **Atomic Data & Test Migration**: Every phase's gate runs the GLOBAL `backend_v2/` test suite. Any test broken by a schema change is migrated to typed construction in the same phase.
8. **Residual Debt Ceiling Ledger & Monotonic Ratchet**: From Phase 1, Stage 9/10 of `scripts/backend_audit_loop.py` executes `scripts/audit_warning_baseline.py --verify-zero` which enforces `ResidualDebtCeilingsDTO` exact-equality ceilings across all census categories (D, F, K, X, N, T, P, M, R, S) and retained debt. Any increase in any count immediately fails the quality gate; any decrease requires atomically lowering the ceiling in `scripts/audit_warning_baseline.py` within the same commit. From Phase 9, `scripts/audit_dict_eradication.py` reports every `# noqa` comment token and every `cast(Any, ...)` call as a FATAL violation; from Phase 10, every `# type: ignore` comment token and any unapproved configuration ignore in `pyproject.toml`.
9. **AST Guardrail QGR027 (FATAL) & Open-JSON Whitelist SSOT**: Prohibits `dict[..., JsonValue]` in all domain and DTO models outside the frozen `OPEN_JSON_EXEMPTION_FILES` set (with `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` forming a monotonic ratchet that shrinks as subsequent phases complete). Also tracked as Metric 11 (`unauthorized_open_json_annotations`) in `scripts/audit_dict_eradication.py`.

### 2.5 Producer-Consumer Integration Check
- **Producers**: API ingress controllers, ontology seed loaders, and LLM structured outputs produce strongly typed Pydantic V2 DTOs. Flutter Studio simulation dialogs produce `mock_inputs` (Flutter is the producer; backend is the consumer).
- **Consumers**: Downstream orchestrators, workers, and Flutter SDUI presentation layers consume models via static dot-notation property access without dictionary indexing.
- **Wire Compatibility**: Retyping `mock_inputs` to `dict[str, IngressInputValue]` preserves the JSON wire shape for primitive values; nested-map or `null` values become HTTP 422 (Fail-Fast). Phase 1 adds 2 negative router tests asserting 422 for nested-map and `null` values before Phase 8 types the Dart producers.

### 2.6 Out-of-Scope Register (Recorded Technical Debt)
| Item | Location | Reason |
| :--- | :--- | :--- |
| Driver-level `patch("<module>.get_driver")` (51) and `patch("<module>.get_storage_driver")` (24) | 11 test files enumerated in @[docs/epic/EPIC_157_residual_ledger.md] | Infrastructure connection isolation, not repository seeding; outside census A-K and user decisions Q6-Q8. Baseline 75 MUST NOT increase; replacement with a real `TinyDBDriver` over `tmp_path` requires a separate user decision. |
| 54 assertion-free test functions (no `assert`, `pytest.raises`, `pytest.warns`, `pytest.fail`, or `assert_*` call) | 32 files enumerated in @[docs/epic/EPIC_157_residual_ledger.md] | Recorded per user decision Q8; baseline 54 MUST NOT increase. No-op teardown and lazy-import smoke tests dominate. |
| 13 environment-gated skips (`TAVILY_API_KEY`, missing PDF inputs, Flutter SDK, live-LLM flag) | 7 files under `backend_v2/tests/integration/` and `backend_v2/tests/unit/` | Legitimate environment gating; not unconditional. |
| Non-persistence `AsyncMock` / `MagicMock` doubles of services, LLM clients, and SDK clients | `backend_v2/tests/` | Permitted by `partial_mocking_srp_ban` (Section 2.2 item 8). |
| mypy excludes `backend_v2/tests/` (`[tool.mypy] exclude`) | `@[pyproject.toml]` | Test-side typing is enforced by the extended dict audit (Phase 11) and the zero-suppression audit (Phases 9-10); enabling mypy on tests is a separate Epic decision. |
| Architecture rule "routers must not import the database layer" loses its only test when the permanently skipped `backend_v2/tests/architecture/test_boundaries.py` is deleted | `backend_v2/api/routers/` | The skipped test enforced nothing; re-introducing the rule as an AST guardrail is a separate decision. |
| KI drift: `ExecutionInputsDTO.raw_inputs` documented as `dict[str, Any]`; `BOUNDARY_EXEMPTION_FILES` documented as 6 basenames | `@[ki_zero_permissive_typing.md]` | Synchronized through the parameterized `/tier7-describe-architecture` command in Phase 13. |

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Physical Boundary SSOT, Pre-Implementation Cleanups & Model Typing with 1-hop Consumers
- **Objective**: Replace basename exemptions with the path-based `BOUNDARY_EXEMPTION_FILES` SSOT, wire `scripts/audit_warning_baseline.py` (Residual Debt Ceiling Ledger) as Stage 9/10 of `scripts/backend_audit_loop.py`, introduce `QGR026` (FATAL skip/xfail ban) and `QGR027` (FATAL unauthorized Open-JSON ban) in `scripts/_ast_guardrails.py`, resolve seed/OpenAPI/repository/guardrail-test debt, promote `studio.py` simulation traces to `StepSimulationTraceDTO`, and retype all 30 model violations together with their 1-hop consumers and test fixtures in the same phase.
- **Execution Pre-Conditions**: (1) User statement "PERMISSION GRANTED to mutate DAG Orchestrator ecosystem" (Section 2.4 item 5). (2) `Select-String -Path data/db_v2.json -Pattern '"_step_metadata"'` count recorded (Sunset row `trace.py`). (3) `grep_search` for `model_params` and `flat_report` across `client_app_v2/lib/` recorded (Sunset `DROP` rows).
- **Pre-Implementation Technical Debt Cleanups**:
  - `[CLEANUP] Convert BOUNDARY_EXEMPTION_FILES in scripts/_ast_guardrails.py to a frozenset of 15 workspace-relative POSIX paths; delete LOCKED_PHYSICAL_DRIVERS and import the shared set in scripts/audit_dict_eradication.py.`
  - `[CLEANUP] Implement ResidualDebtCeilingsDTO in scripts/audit_warning_baseline.py and wire as Stage 9/10 of scripts/backend_audit_loop.py, enforcing exact-equality ceilings on all census categories.`
  - `[CLEANUP] Implement QGR026 in scripts/_ast_guardrails.py to statically ban unconditional @pytest.mark.skip, @pytest.mark.xfail, module-level skip/xfail markers, and pytest.xfail() calls at FATAL severity.`
  - `[CLEANUP] Implement QGR027 in scripts/_ast_guardrails.py and Metric 11 in scripts/audit_dict_eradication.py to statically ban unauthorized dict[..., JsonValue] outside the frozen OPEN_JSON_EXEMPTION_FILES SSOT whitelist at FATAL severity.`
  - `[CLEANUP] Retype simulation traces in backend_v2/models/dtos/studio.py to StepSimulationTraceDTO and simulation service calls in backend_v2/services/studio/simulation_service.py to eliminate trace={}.`
  - `[CLEANUP] Verify zero residual AST and dict-audit violations in backend_v2/models/dtos/telemetry.py, backend_v2/api/routers/system/telemetry.py, backend_v2/services/sdui/adapters/base_adapter.py (pre-flight verified clean at 0 violations) after losing accidental basename exemption.`
  - `[CLEANUP] Replace validate_all_seed_collections buffers in backend_v2/seed/run_seed.py with ValidatedSeedBufferDTO.`
  - `[CLEANUP] Type the OpenAPI spec in backend_v2/scripts/generate_openapi.py as dict[str, JsonValue].`
  - `[CLEANUP] Return typed domain models from backend_v2/database/repositories/execution.py and backend_v2/database/repositories/workflow.py.`
  - `[CLEANUP] Replace getattr reflection in backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py with typed ast node matching.`
  - `[CLEANUP] Delete the 4 permanently skipped test files backend_v2/tests/architecture/test_boundaries.py, backend_v2/tests/unit/test_epic_61_hardening.py, backend_v2/tests/unit/test_provider_rate_limit.py, backend_v2/tests/unit/llm/test_fallback_caching.py (user decision Q8).`
  - `[CLEANUP] Delete the skipped functions test_aspirational_html_escape in backend_v2/tests/unit/test_ast_domain_security_guardrails.py and test_all_ok_matrices_have_exactly_three_claims in backend_v2/tests/unit/test_matrix_data_integrity.py (user decision Q8).`
  - `[CLEANUP] Remove the 4 @pytest.mark.xfail markers in backend_v2/tests/unit/hooks/test_scoring.py; migrate the raw evaluation dicts of test_failed_atom_with_override_does_not_inflate_score and test_matrix_scoring_hook_illegal_override_penalty to typed ExecutionInputsDTO.raw_inputs values. An assertion failure after the fixture migration triggers STOP and a PERMISSION GRANTED request (user decision Q8).`
- **Target Boundaries**:
  - `[MODIFY] @[scripts/_ast_guardrails.py]` (QGR026 and QGR027 definitions, `BOUNDARY_EXEMPTION_FILES`, and `OPEN_JSON_EXEMPTION_FILES`)
  - `[MODIFY] @[scripts/audit_dict_eradication.py]` (Metric 11 Open-JSON detection)
  - `[MODIFY] @[backend_v2/services/studio/simulation_service.py]` (trace=StepSimulationTraceDTO)

  - `[MODIFY] @[scripts/audit_warning_baseline.py]` (defining `ResidualDebtCeilingsDTO` and ceiling enforcement)
  - `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_warning_baseline.py]`
  - `[MODIFY] @[scripts/backend_audit_loop.py]` (Stage 9/10 wiring)
  - `[MODIFY] @[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]`
  - `[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`
  - `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]`
  - `[MODIFY] @[backend_v2/models/dtos/telemetry.py]`
  - `[MODIFY] @[backend_v2/api/routers/system/telemetry.py]`
  - `[MODIFY] @[backend_v2/services/sdui/adapters/base_adapter.py]`
  - `[MODIFY] @[backend_v2/scripts/generate_openapi.py]`
  - `[MODIFY] @[backend_v2/seed/run_seed.py]`
  - `[MODIFY] @[backend_v2/database/repositories/execution.py]`
  - `[MODIFY] @[backend_v2/database/repositories/workflow.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py]`
  - `[MODIFY] @[backend_v2/models/domain/base.py]`
  - `[MODIFY] @[backend_v2/models/domain/analyst.py]`
  - `[MODIFY] @[backend_v2/models/domain/archivist.py]`
  - `[MODIFY] @[backend_v2/models/domain/integrity.py]`
  - `[MODIFY] @[backend_v2/models/domain/mcp.py]`
  - `[MODIFY] @[backend_v2/models/domain/metrics.py]`
  - `[MODIFY] @[backend_v2/models/domain/security.py]`
  - `[MODIFY] @[backend_v2/models/domain/system_config.py]`
  - `[MODIFY] @[backend_v2/models/domain/validation.py]`
  - `[MODIFY] @[backend_v2/models/domain/xai.py]`
  - `[MODIFY] @[backend_v2/models/dtos/atom_evaluation.py]`
  - `[MODIFY] @[backend_v2/models/dtos/mcp.py]`
  - `[MODIFY] @[backend_v2/models/dtos/prompt_context.py]`
  - `[MODIFY] @[backend_v2/models/dtos/studio.py]`
  - `[MODIFY] @[backend_v2/models/dtos/system.py]`
  - `[MODIFY] @[backend_v2/models/dtos/trace.py]`
  - `[MODIFY] @[backend_v2/models/llm.py]`
  - `[MODIFY] @[backend_v2/models/dtos/context_variables.py]`
  - `[MODIFY] @[backend_v2/services/orchestrator/engines/synthesis_engine.py]`
  - `[MODIFY] @[backend_v2/services/orchestrator/matrix_reducer.py]`
  - `[MODIFY] @[backend_v2/services/orchestrator/matrix_explanation_service.py]`
  - `[MODIFY] @[backend_v2/services/execution/ingress_service.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`
  - `[MODIFY] @[backend_v2/tests/unit/models/dtos/test_atom_evaluation.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/execution/test_ingress_service.py]`
  - `[MODIFY] @[backend_v2/tests/unit/models/test_trace_envelope.py]`
  - `[MODIFY] @[backend_v2/tests/unit/models/dtos/test_trace.py]`
  - `[MODIFY] @[backend_v2/tests/unit/seed/test_run_seed.py]`
  - `[DELETE] @[backend_v2/tests/architecture/test_boundaries.py]`
  - `[DELETE] @[backend_v2/tests/unit/test_epic_61_hardening.py]`
  - `[DELETE] @[backend_v2/tests/unit/test_provider_rate_limit.py]`
  - `[DELETE] @[backend_v2/tests/unit/llm/test_fallback_caching.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_ast_domain_security_guardrails.py]` (delete `test_aspirational_html_escape`)
  - `[MODIFY] @[backend_v2/tests/unit/test_matrix_data_integrity.py]` (delete `test_all_ok_matrices_have_exactly_three_claims`)
  - `[MODIFY] @[backend_v2/tests/unit/hooks/test_scoring.py]` (remove 4 `@pytest.mark.xfail` markers; typed `ExecutionInputsDTO.raw_inputs` fixtures for the 2 XFAIL tests)
- **Verification Gate**:
  - Census command S (Residual Ledger) returns 0 matches; QGR026 reports 0 violations; `uv run pytest backend_v2/tests/unit/hooks/test_scoring.py -rxX` reports 0 xfailed and 0 xpassed.
  - `uv run python scripts/audit_dict_eradication.py backend_v2/models backend_v2/seed backend_v2/scripts backend_v2/database/repositories --strict`
  - `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`
  - `uv run python backend_v2/seed/run_seed.py local`
  - `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` (Stages 1-9/10 clean)

### Phase 2: System Exceptions, Hooks, LLM Caching Contract & Core Lockdown
- **Objective**: Retype `AppException.details` to `dict[str, JsonValue] | None` (blast radius: 32 mypy errors in 5 files, Section 2.1), introduce `ProblemDetailDTO` with explicit `.model_dump(mode="json", exclude_none=True)` serialization at the FastAPI network boundary (`main.py`, `core/rate_limit.py`), move `prepare_caching_payload` to a `CachingPayloadResultDTO` contract owned by `BaseLLMAdapter`, and eradicate the remaining hook, LLM, and core violations (including dynamic model field dictionary typing in `core/registry.py`).
- **Target Boundaries**:
  - `[MODIFY] @[backend_v2/exceptions.py]`
  - `[MODIFY] @[backend_v2/main.py]`
  - `[MODIFY] @[backend_v2/core/rate_limit.py]`
  - `[MODIFY] @[backend_v2/core/registry.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_exceptions.py]`
  - `[MODIFY] @[backend_v2/database/repositories/components/prompt_block.py]` (`details` value `list[str]`)
  - `[MODIFY] @[backend_v2/services/ingress/smart_ingress_resolver.py]` (`details` values `dict[str, Sequence[str]]` and `list[str]`)
  - `[MODIFY] @[backend_v2/hooks/validation.py]` (`details` value `list[dict[str, Any]]` warnings)
  - `[MODIFY] @[backend_v2/hooks/input_processing.py]` (`details` value `list[ErrorDetails]` from `ValidationError.errors()`)
  - `[MODIFY] @[backend_v2/hooks/scoring/matrix_hook.py]`
  - `[MODIFY] @[backend_v2/hooks/scoring/passivity_hook.py]`
  - `[MODIFY] @[backend_v2/hooks/linguistics.py]`
  - `[MODIFY] @[backend_v2/hooks/source_verification_hook.py]`
  - `[MODIFY] @[backend_v2/llm/caching_service.py]`
  - `[MODIFY] @[backend_v2/llm/client.py]` (`run_structured_task` and `run_chat` call sites of `prepare_caching_payload`)
  - `[MODIFY] @[backend_v2/llm/adapters/base_adapter.py]`
  - `[MODIFY] @[backend_v2/llm/adapters/ai_studio_adapter.py]`
  - `[MODIFY] @[backend_v2/llm/adapters/anthropic_adapter.py]`
  - `[MODIFY] @[backend_v2/llm/adapters/mock_adapter.py]`
  - `[MODIFY] @[backend_v2/llm/adapters/openai_adapter.py]`
  - `[MODIFY] @[backend_v2/llm/adapters/vertex_adapter.py]`
  - `[MODIFY] @[backend_v2/llm/ingress_pipeline.py]`
  - `[MODIFY] @[backend_v2/llm/schema_builder.py]`
  - `[MODIFY] @[backend_v2/llm/mock_data.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_mock_data.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_mock.py]`
- **Verification Gate**:
  - `uv run mypy backend_v2` (0 errors; baseline probe 32 errors in 5 files)
  - `Select-String -Path backend_v2/llm/adapters/*.py, backend_v2/llm/caching_service.py -Pattern "tuple\[list\[LLMMessageDTO\]"` returns 0 matches (proves the `CachingPayloadResultDTO` rewrite inside exempt adapter files that the dict audit does not scan)
  - `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` (residual violations limited to `backend_v2/tests/fakes/in_memory_repositories.py:130`)
  - `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`

### Phase 3: Test Persistence Migration — Hooks & LLM
- **Objective**: Replace `InMemoryBlueprintTransformerRepository` `.return_value` / `.side_effect` seeding and `AsyncMock` repository fixtures with typed seeding of `InMemoryUnifiedWorkflowRepository` / `InMemorySystemRepository`, asserting roundtrip state. 82 census A assignments + 13 census B attribute replacements (`backend_v2/tests/unit/hooks/test_matrix_hook.py`) + 3 fixtures, plus 2 import-only files (`test_structured_retry.py`, `test_cdata_hardening_comprehensive.py`). Residual Ledger share: census D 379 keyword-injected repository mocks, census K 25 ad-hoc repository classes, census X 792 `cast(Any, ...)` injections (`test_scoring.py` 688, `hooks/test_security.py` 41, `hooks/test_metadata.py` 25, `hooks/test_references.py` 25, `hooks/test_input_processing.py` 8, `unit/test_input_processing.py` 3, `hooks/test_passivity_hook.py` 2).
- **Target Boundaries**:
  - `[MODIFY] @[backend_v2/tests/unit/hooks/test_archival.py]`
  - `[MODIFY] @[backend_v2/tests/unit/hooks/test_atom_flattening.py]`
  - `[MODIFY] @[backend_v2/tests/unit/hooks/test_atom_sampling_determinism.py]`
  - `[MODIFY] @[backend_v2/tests/unit/hooks/test_input_processing.py]`
  - `[MODIFY] @[backend_v2/tests/unit/hooks/test_integrity.py]`
  - `[MODIFY] @[backend_v2/tests/unit/hooks/test_matrix_hook.py]`
  - `[MODIFY] @[backend_v2/tests/unit/hooks/test_passivity_hook.py]`
  - `[MODIFY] @[backend_v2/tests/unit/hooks/test_scoring.py]`
  - `[MODIFY] @[backend_v2/tests/unit/hooks/test_interaction_hook.py]`
  - `[MODIFY] @[backend_v2/tests/unit/llm/test_client.py]`
  - `[MODIFY] @[backend_v2/tests/unit/llm/test_llm_client_tiers.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_handler.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_llm_context_bounds.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_epic66_multi_provider.py]`
  - `[MODIFY] @[backend_v2/tests/unit/llm/test_structured_retry.py]`
  - `[MODIFY] @[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]`
  - `[MODIFY] @[backend_v2/tests/unit/hooks/test_validation.py]`
  - `[MODIFY] @[backend_v2/tests/unit/hooks/test_source_verification_hook.py]`
  - `[MODIFY] @[backend_v2/tests/unit/hooks/test_linguistics.py]`
  - `[MODIFY] @[backend_v2/tests/unit/hooks/test_metadata.py]`
  - `[MODIFY] @[backend_v2/tests/unit/hooks/test_references.py]`
  - `[MODIFY] @[backend_v2/tests/unit/hooks/test_security.py]`
  - `[MODIFY] @[backend_v2/tests/unit/hooks/test_dlq_guard.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_input_processing.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_metadata.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_metrics.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_references.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_synthesis_distiller_hook.py]`
  - `[MODIFY] @[backend_v2/tests/unit/core/test_hook_registry.py]`
  - `[MODIFY] @[backend_v2/tests/unit/llm/test_google_providers_separation.py]`
- **Verification Gate**:
  - Census commands A, B, C, and I (Section 1, Test Persistence Census Table) restricted to the 30 target files return 0 matches.
  - Census commands D, K, and X (Residual Ledger) restricted to the 30 target files return 0 matches.
  - `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`

### Phase 4: Test Persistence Migration — Services, Studio, Execution & Database
- **Objective**: Migrate 419 census A assignments + 45 census B attribute replacements + 7 census C object patches + 6 fixtures + 269 census D keyword-injected repository mocks, migrate 2 import-only files (`test_dependencies.py`, `test_override_service.py`), delete `dict_to_obj`, replace the 3 `repo._increment_version = MagicMock(...)` partial mocks with version roundtrip assertions over a real `TinyDBDriver` on `tmp_path`, and replace the driver-level mock in `test_repositories_v2.py` with a real `TinyDBDriver` over `tmp_path`.
- **Target Boundaries**:
  - `[MODIFY] @[backend_v2/tests/unit/services/test_blueprint.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/test_execution.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/test_execution_resumability.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/test_report_service.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/test_chat_parser.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/execution/test_ingress_service.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/execution/test_lifecycle_service.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/studio/test_output_profile_service.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/studio/test_workflow_service.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_auth.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_security.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_usage_service.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_repo_deletion.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_repositories_v2.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_dependencies.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/execution/test_override_service.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/execution/test_stream_service.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/studio/test_system_config_service.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/studio/test_prompt_block_service.py]`
  - `[MODIFY] @[backend_v2/tests/unit/database/repositories/components/test_agent.py]`
  - `[MODIFY] @[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]`
  - `[MODIFY] @[backend_v2/tests/unit/database/repositories/components/test_task_blueprint.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/execution/test_legacy_render_service.py]`
- **Verification Gate**:
  - Census commands A, B, C, I, and D restricted to the 23 target files return 0 matches; `Select-String -Path backend_v2/tests -Pattern "dict_to_obj" -Recurse` returns 0.
  - `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`

### Phase 5: Test Persistence Migration — Orchestrator & DAG
- **Objective**: Migrate 162 census A assignments + 10 census B attribute replacements + 2 fixtures + 152 census D keyword-injected repository mocks + 1 census X `cast(Any, ...)` (`test_rag_preflight_service.py`) across DAG executor, strategy, and concurrency tests.
- **Target Boundaries**:
  - `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_service.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_dag_taskgroup.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_concurrency_fuzzer.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_logic.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_base.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_registry.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_telemetry.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_chat_inflation.py]`
  - `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]`
- **Verification Gate**:
  - Census commands A, B, C, I, D, and X restricted to the 20 target files return 0 matches.
  - `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`

### Phase 6: Test Persistence Migration — Workers, API & Integration
- **Objective**: Migrate the remaining 198 census A assignments, 21 census D keyword-injected repository mocks, and 50 census F string-target repository patches (`test_worker.py` 22, `test_worker_synthesis.py` 16, `workers/test_report_worker.py` 4, `workers/test_synthesis_worker.py` 4, `workers/test_synthesis_reducers.py` 3, `test_worker_synthesis_accumulation.py` 1). Each census F patch binds `return_value` to a typed-seeded `InMemory*Repository` instance.
- **Target Boundaries**:
  - `[MODIFY] @[backend_v2/tests/unit/workers/test_execution_worker.py]`
  - `[MODIFY] @[backend_v2/tests/unit/workers/test_report_worker.py]`
  - `[MODIFY] @[backend_v2/tests/unit/workers/test_synthesis_reducers.py]`
  - `[MODIFY] @[backend_v2/tests/unit/workers/test_synthesis_worker.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_worker.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_worker_synthesis.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_finops_telemetry.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_progress.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py]`
  - `[MODIFY] @[backend_v2/tests/integration/test_epic_chain_e2e.py]`
  - `[MODIFY] @[backend_v2/tests/test_fastdev_frozen.py]`
  - `[MODIFY] @[backend_v2/tests/test_worker_models_used.py]`
  - `[MODIFY] @[backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py]`
  - `[MODIFY] @[backend_v2/tests/integration/test_tavily_live.py]`
- **Verification Gate**:
  - Census commands A, B, C, and I over `backend_v2/tests` excluding `backend_v2/tests/fakes/` and `backend_v2/tests/unit/fakes/` return 0 matches. Census I = 0 is the mandatory pre-Phase 7 proof that no test outside the fake's own test imports `InMemoryBlueprintTransformerRepository`.
  - Census commands D, F, and K (Residual Ledger) over the full `backend_v2/tests` tree return 0 matches; this is the mandatory pre-Phase 7 proof that `QGR014` (e), (f), and (g) land at FATAL severity without violations.
  - `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`

### Phase 7: Mock-Emulation Sunset & QGR014 FATAL Hardening
- **Objective**: Delete `DynamicRepoMethod` and `InMemoryBlueprintTransformerRepository`, replace `inject_fault` reflection with a positive registry, and land the hardened `QGR014` detections (a)-(g) (Section 2.4 item 4) at FATAL severity in the same commit: (a) fixture-return detection in `visit_Return`; (b) `.return_value` / `.side_effect` and (c) `<repo>.<attr> = AsyncMock(...)` / `MagicMock(...)` / `Mock(...)` attribute-replacement detection in `visit_Assign`; (d) `patch.object(<repo>, ...)` / `monkeypatch.setattr(<repo>, ...)`, (e) keyword-injected repository mocks, and (f) string-target repository-class patches without an in-memory fake binding in `visit_Call`; (g) ad-hoc repository classes in `visit_ClassDef`. Identifier-based detections share one `_is_repository_identifier` predicate; (f) and (g) use positive sets resolved from `backend_v2/database/interfaces.py` and `backend_v2/database/repositories/`.
- **Target Boundaries**:
  - `[MODIFY] @[backend_v2/tests/fakes/in_memory_repositories.py]` (delete `DynamicRepoMethod` and `InMemoryBlueprintTransformerRepository`; `inject_fault` reflection removal)
  - `[MODIFY] @[backend_v2/tests/fakes/__init__.py]`
  - `[MODIFY] @[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]`
  - `[MODIFY] @[scripts/_ast_guardrails.py]` (hardened QGR014 detections (a)-(g); positive repository-class and interface-method sets)
  - `[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` (negative fixtures for (a)-(g); positive fixtures from Section 2.3)
- **Verification Gate**:
  - `Select-String -Path backend_v2 -Pattern "DynamicRepoMethod|InMemoryBlueprintTransformerRepository|dict_to_obj" -Recurse` returns 0 matches.
  - `uv run python scripts/_ast_guardrails.py backend_v2/tests/ --strict`
  - `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` reports `TOTAL VIOLATIONS: 0`.
  - `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`

### Phase 8: Universal Quality Gate Stage 10 Integration & Full-Duplex Client Parity
- **Objective**: Wire `scripts/audit_dict_eradication.py backend_v2 --strict` as Stage 10/10 of `scripts/backend_audit_loop.py` and type the Flutter producers/consumers of retyped backend fields (including `StepSimulationTraceDto` alignment on `PromptBlockSimulationResponse`). Knowledge Base synchronization runs in Phase 13.
- **Target Boundaries**:
  - `[MODIFY] @[scripts/backend_audit_loop.py]` (`main`: 10-stage pipeline counter and Stage 10/10 invocation)
  - `[MODIFY] @[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]`
  - `[MODIFY] @[scripts/audit_dto_parity.py]`
  - `[MODIFY] @[client_app_v2/lib/features/studio/models/step_simulation.dart]`
  - `[MODIFY] @[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart]`
  - `[MODIFY] @[client_app_v2/lib/features/studio/models/mcp_gateway.dart]`
- **Verification Gate**:
  - `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` (10/10 stages)
  - `uv run python scripts/audit_dict_eradication.py backend_v2 --strict`
  - `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`

### Phase 9: Suppression & Cast Eradication (`# noqa`, `cast(Any, ...)`)
- **Objective**: Delete the `[REASON: ...]` authorization so that every `# noqa` comment token is a FATAL violation; delete the AST inline suppressor (`CommentSuppressor`) from `scripts/_ast_guardrails.py`, `scripts/backend_audit_loop.py#L400`, and `scripts/audit_warning_baseline.py#L83`; add `cast(Any, ...)` detection to the call audit; and eradicate census N (76 comment tokens in 30 files) and the residual census X (11 calls in 5 files). Third-party attribute reads in `backend_v2/llm/provider.py` and `backend_v2/llm/adapters/base_adapter.py` move to Pydantic V2 adapter DTOs validated with `model_validate(obj, from_attributes=True)`. The 23 Ruff `# noqa` files are enumerated in @[docs/epic/EPIC_157_residual_ledger.md] and form part of this phase's target boundary.
- **Execution Pre-Conditions**: User statement "PERMISSION GRANTED to mutate DAG Orchestrator ecosystem" (Section 2.4 item 5) for `backend_v2/services/orchestrator/strategies/llm.py`.
- **Target Boundaries**:
  - `[MODIFY] @[scripts/audit_dict_eradication.py]` (`audit_file_comments`: every `# noqa` comment token is a violation; `visit_Call`: `cast(Any, ...)` detection)
  - `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]`
  - `[MODIFY] @[scripts/_ast_guardrails.py]` (remove `CommentSuppressor`, inline `# noqa: QGRxxx [REASON: ...]` parser, and `is_suppressed` field)
  - `[MODIFY] @[scripts/backend_audit_loop.py]` (remove `v.is_suppressed` filtering in Stage 4)
  - `[MODIFY] @[scripts/audit_warning_baseline.py]` (remove `v.is_suppressed` filtering)
  - `[MODIFY] @[backend_v2/llm/provider.py]`
  - `[MODIFY] @[backend_v2/llm/adapters/base_adapter.py]`
  - `[MODIFY] @[backend_v2/database/firestore_driver.py]`
  - `[MODIFY] @[backend_v2/database/tinydb_driver.py]`
  - `[MODIFY] @[backend_v2/logging_config.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py]`
  - `[MODIFY] @[backend_v2/tests/fakes/in_memory_repositories.py]`
  - `[MODIFY] @[backend_v2/services/orchestrator/strategies/llm.py]` (`cast(Any, exec_record_raw)`)
  - `[MODIFY] @[backend_v2/tests/integration/test_caching_integration.py]`
  - `[MODIFY] @[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py]`
  - `[MODIFY] @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py]`
  - `[MODIFY] @[backend_v2/tests/unit/test_context_mapper.py]`
- **Verification Gate**:
  - Census commands N and X (Residual Ledger) return 0.
  - `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` reports `TOTAL VIOLATIONS: 0`.
  - `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`

### Phase 10: `# type: ignore` Eradication & Strict mypy Ignore Accounting
- **Objective**: Eradicate census T (409 `# type: ignore` comments in 155 files); delete `[[tool.mypy.overrides]]` for `firestore_driver` and `factory` so `warn_unused_ignores = true` applies globally; remove the 5 dead entries in `per-file-ignores`; replace the 20 `[prop-decorator]` suppressions with ONE `disable_error_code = ["prop-decorator"]` entry (Section 2.2 item 7); extend the comment audit of `scripts/audit_dict_eradication.py` to reject `# type: ignore` at FATAL severity; and add the Config Suppression Ratchet in `scripts/audit_dict_eradication.py` to verify frozen approved sets in `pyproject.toml` and `analysis_options.yaml` via `tomllib`. The 155 files are enumerated in @[docs/epic/EPIC_157_residual_ledger.md] and form part of this phase's target boundary. Batch 10.1 covers 25 production files and 3 `scripts/` files (71 comments); Batch 10.2 covers 127 test files (338 comments). Negative tests construct invalid input through `Model.model_validate({...})` instead of suppressing `call-arg` / `arg-type`.
- **Target Boundaries**:
  - `[MODIFY] @[pyproject.toml]` (`warn_unused_ignores = true` globally; delete `[[tool.mypy.overrides]]`; remove 5 dead `per-file-ignores`; `disable_error_code = ["prop-decorator"]`)
  - `[MODIFY] @[scripts/audit_dict_eradication.py]` (`# type: ignore` comment detection; Config Suppression Ratchet via `tomllib`)
  - `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]`
  - `[MODIFY] @[backend_v2/settings.py]`
  - `[MODIFY] @[backend_v2/models/domain/overseer.py]`
- **Verification Gate**:
  - Census command T (Residual Ledger) returns 0 after each batch for the batch file list and over `backend_v2, scripts` at phase end.
  - `uv run mypy backend_v2` reports 0 errors with `warn_unused_ignores = true`.
  - Config Suppression Ratchet in `audit_dict_eradication.py` reports 0 unapproved config ignores.
  - `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`

### Phase 11: Extended Dict Eradication (Tests, `scripts/`, `Mapping`)
- **Objective**: Close the dict-audit blind spots: `_is_naked_dict_subscript` matches `dict`, `Dict`, `Mapping`, and `MutableMapping` with `Any` / `object` values; fix `_is_test_file` in `scripts/_ast_guardrails.py` and `is_test` in `scripts/audit_dict_eradication.py` to use path check `backend_v2/tests/` (so `test_settings.py` is scanned as production); annotation checks run in test files; Stage 10 runs `audit_dict_eradication.py backend_v2 scripts --strict`. Eradicate census P (390 lines: tests 304 in 80 files, `scripts/` 86 in 9 files; enumerated in @[docs/epic/EPIC_157_residual_ledger.md] and part of this phase's target boundary) and census M (10 production sites in 6 files).
- **Execution Pre-Conditions**: User statement "PERMISSION GRANTED to mutate DAG Orchestrator ecosystem" (Section 2.4 item 5) for `backend_v2/services/orchestrator/strategies/llm.py`, `source_document_packer.py`, and `context_builder.py`.
- **Target Boundaries**:
  - `[MODIFY] @[scripts/audit_dict_eradication.py]` (`_is_naked_dict_subscript`, `is_test`, test annotation checks)
  - `[MODIFY] @[scripts/_ast_guardrails.py]` (`_is_test_file` path check)
  - `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]`
  - `[MODIFY] @[scripts/backend_audit_loop.py]` (Stage 10 arguments `backend_v2 scripts`)
  - `[MODIFY] @[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]`
  - `[MODIFY] @[backend_v2/core/test_settings.py]`
  - `[MODIFY] @[backend_v2/hooks/input_processing.py]` (`Mapping[str, object]` locals at lines 66-67)
  - `[MODIFY] @[backend_v2/services/orchestrator/strategies/llm.py]`
  - `[MODIFY] @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]`
  - `[MODIFY] @[backend_v2/services/ingress/pdf_chat_extractor.py]`
  - `[MODIFY] @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]` (accept `HookState` only)
- **Verification Gate**:
  - Census commands P and M (Residual Ledger) return 0.
  - `uv run python scripts/audit_dict_eradication.py backend_v2 scripts --strict` reports `TOTAL VIOLATIONS: 0`.
  - `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` (Stage 10 over `backend_v2 scripts`)

### Phase 12: Client Permissive Map Eradication (Dart)
- **Objective**: Retype census R (193 non-codec `Map<String, dynamic>` occurrences in 48 hand-written files, ratcheted down to 186 across 45 files following Phase 8; enumerated in @[docs/epic/EPIC_157_residual_ledger.md] and part of this phase's target boundary) to Freezed DTOs mirroring backend CLOSED models, or to `Map<String, Object?>` for backend OPEN-JSON fields. Implement `DGR005` in `scripts/_dart_guardrails.py` banning non-codec `Map<String, dynamic>`; promote `DGR001`, `DGR004` (Dart lint suppressions), and `DGR005` to unconditional FATAL severity in `scripts/_dart_guardrails.py` and `scripts/flutter_audit_loop.py`; and eradicate the 25 `// ignore:` suppressions across 23 files. `ExecutionRecord.contextVariables` and `ExecutionRecord.executionTrace` mirror the already typed backend fields `context_variables: ContextVariablesDTO` and `execution_trace: list[ErrorTraceEvent | TombstoneEvent | TraceEvent]`. The 67 codec signatures remain (Section 2.2 item 6).
- **Target Boundaries**:
  - `[MODIFY] @[scripts/_dart_guardrails.py]` (rule `DGR005`; unconditional FATAL severity for DGR001, DGR004, DGR005)
  - `[MODIFY] @[scripts/flutter_audit_loop.py]` (unconditional FATAL enforcement of DGR001, DGR004, DGR005)
  - `[MODIFY] @[backend_v2/tests/unit/scripts/test_dart_guardrails.py]`
  - `[MODIFY] @[client_app_v2/lib/features/execution/models/execution_record.dart]`
  - `[MODIFY] @[client_app_v2/lib/features/execution/models/execution_metadata.dart]`
  - `[MODIFY] @[scripts/audit_dto_parity.py]`
  - `[MODIFY] @[scripts/audit_warning_baseline.py]` (ratchet `CURRENT_RESIDUAL_CEILINGS.r = 0`)
- **Verification Gate**:
  - Census command R (Residual Ledger) returns 0.
  - DGR004 (Dart lint suppressions) reports 0 occurrences across `client_app_v2/lib/`.
  - `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build` (enforces DGR001, DGR004, DGR005 as unconditional FATAL gates)
  - `uv run python scripts/audit_dto_parity.py`

### Phase 13: Zero-Bypass Final Gate & Knowledge Synchronization
- **Objective**: Re-run every census command of the Test Persistence Census Table and the Residual Ledger through the 10-stage `scripts/backend_audit_loop.py` and `scripts/flutter_audit_loop.py`, verifying all ceilings are 0, and synchronize the Knowledge Base.
- **Target Boundaries**:
  - `[MODIFY] @[scripts/audit_warning_baseline.py]` (final lock: all residual ceilings asserted at strictly 0)
- **Verification Gate**:
  - Census commands A, B, C, I, D, F, K, X, N, T, P, M, R, and S return 0.
  - `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` (all 10 stages clean)
  - `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`
- **Knowledge Synchronization Command**:
  - `/tier7-describe-architecture @[docs/epic/EPIC_157_tracker.md] @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] @[ki_zero_permissive_typing.md]` with directives: Target KIs to Synchronize = `@[ki_zero_permissive_typing.md]` (path-based `BOUNDARY_EXEMPTION_FILES` replacing item 27 together with the 9-path Admission Ratchet test; 10-stage audit loop with Stage 9 Residual Debt Ceiling Ledger and Stage 10 Dict Eradication Audit over `backend_v2 scripts` replacing item 30; hardened `QGR014` covering detections (a) fixture returns, (b) `.return_value`/`.side_effect` seeding, (c) repository attribute replacement, (d) `patch.object`/`monkeypatch.setattr` on repositories, (e) keyword-injected repository mocks, (f) string-target repository-class patches, and (g) ad-hoc repository classes; `QGR026` skip/xfail ban; `DGR005` loose map ban and unconditional FATAL Dart guardrails; Zero Suppression Gate rejecting every `# noqa`, `cast(Any, ...)`, `# type: ignore`, and unapproved config ignores; extended dict audit covering `Mapping` / `MutableMapping`, test files, and `scripts/`; Dart codec signature boundary; `ExecutionInputsDTO.raw_inputs: Mapping[str, DomainInputValue]`; Field Classification Gate); Directory Reference Sync = `@[.agents/rules/04_directory_reference.md]` (removal of `InMemoryBlueprintTransformerRepository`); Pillar Documentation Sync = none.

### Circuit Breaker Protocol (All Phases)
Three consecutive failures of the same test or quality gate trigger `<circuit_breaker_tripped>` and `git restore . ; git clean -fd` (excluding `data/db_v2.json`, which is never restored). Each verified phase (Phases 1-13) is committed atomically with explicit relative paths and an English Conventional Commit message.

---

## 4. Definition of Done (DoD) & Verification Plan

### 4.1 Definition of Done (DoD)
The epic is complete when:
1. `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` reports `TOTAL VIOLATIONS: 0` (baseline 127).
2. `scripts/audit_dict_eradication.py` defines no exemption set; `BOUNDARY_EXEMPTION_FILES` in `scripts/_ast_guardrails.py` is a `frozenset[str]` of exactly the 15 paths in Section 2.2 item 1.
3. Test Persistence Census commands A, B, C, and I return 0 matches (baselines 861, 68, 7, 45) and `Select-String -Path backend_v2 -Pattern "DynamicRepoMethod|InMemoryBlueprintTransformerRepository|dict_to_obj" -Recurse` returns 0 matches.
4. Hardened `QGR014` runs at FATAL severity and `uv run python scripts/_ast_guardrails.py backend_v2/tests/ --strict` reports 0 violations.
5. `scripts/backend_audit_loop.py` executes 10 stages with zero errors and test coverage exceeds 90%.
6. `uv run mypy backend_v2` reports 0 errors with `AppException.details: dict[str, JsonValue] | None` and `warn_unused_ignores = true` globally; `[[tool.mypy.overrides]]` removed; `pyproject.toml` disables no mypy error code other than `prop-decorator`.
7. DTO Parity audit passes cleanly between Python Pydantic V2 and Dart Freezed models for `mock_inputs`, `input_schema`, and every model retyped in Phase 12.
8. Residual Ledger census commands D, F, K, X, N, T, P, M, R, and S return 0 (baselines 821, 50, 25, 804, 76, 409, 390, 10, 193, 11); Stage 9/10 `scripts/audit_warning_baseline.py` reports zero residual debt across all ceilings.
9. Stage 10 of `scripts/backend_audit_loop.py` runs `uv run python scripts/audit_dict_eradication.py backend_v2 scripts --strict` and reports `TOTAL VIOLATIONS: 0`.
10. `scripts/_ast_guardrails.py` rule `QGR026` (banning unconditional skip/xfail) and `scripts/_dart_guardrails.py` rule `DGR005` (banning loose maps) pass cleanly; `scripts/flutter_audit_loop.py` enforces DGR001, DGR004, and DGR005 as unconditional FATAL gates without requiring `--strict`.
11. The Section 2.6 baselines do not increase: 75 driver-level patches, 54 assertion-free test functions, 13 environment-gated skips.
12. Config Suppression Ratchet in `scripts/audit_dict_eradication.py` verifies zero unapproved ignores in `pyproject.toml` and `analysis_options.yaml`.

### 4.2 Automated Unit & Integration Tests
- Python Unit Testing: `uv run pytest backend_v2/tests/unit/ -v --cov=backend_v2`
- AST Strict Guardrails: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`
- Dict Eradication Audit: `uv run python scripts/audit_dict_eradication.py backend_v2 --strict`
- SDUI Parity: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`
- Frontend Build & Freezed Parity: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`
- ISTQB Negative Partitions (minimum 2 per feature): exemption set rejects basename-collision paths and non-existent paths; `QGR014` flags fixture `return AsyncMock()`, `repo.<method>.return_value =`, `repo.<method> = AsyncMock(...)`, and `monkeypatch.setattr(<repo>, ...)`; the admission ratchet fails when any of the 9 newly admitted boundary paths reports an AST violation under an empty exemption set; CLOSED DTOs reject unknown keys; `IngressInputValue` maps reject nested maps and `null`; `ValidatedSeedBufferDTO` rejects an unknown collection key and a malformed record; `QGR014` flags `HookDependencies(exec_repo=MagicMock())`, `patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository")` without an in-memory fake binding, and a test-module class defining an `IUnifiedWorkflowRepository` method name; `audit_dict_eradication.py` flags `# noqa: QGR001 [REASON: x]`, `# noqa: E501`, `cast(Any, x)`, `# type: ignore[arg-type]`, a `Mapping[str, object]` annotation, and a production module at path `backend_v2/core/test_settings.py`, while `"# noqa"` inside a string literal produces 0 violations; `QGR026` flags a temporary `@pytest.mark.skip` module; `DGR005` flags a temporary non-codec `Map<String, dynamic>` Dart file; Config Suppression Ratchet flags an unapproved entry in `tool.ruff.lint.ignore` or `per-file-ignores`.

### 4.3 AST Guardrails & Structural Tests
- `QGR014`: Prohibits detections (a)-(g) of Section 2.4 item 4: `AsyncMock`/`MagicMock`/`Mock` repository fixtures (assignment and fixture return), `.return_value` / `.side_effect` assignments, `<repo>.<attr> = AsyncMock(...)` / `MagicMock(...)` / `Mock(...)` attribute replacements, `patch.object(<repo>, ...)` / `monkeypatch.setattr(<repo>, ...)` calls, keyword-injected repository mocks, string-target repository-class patches without an in-memory fake binding, and ad-hoc repository classes in test modules, via one `_is_repository_identifier` predicate excluding `report` and `response` tokens plus positive repository-class and interface-method sets.
- `QGR026`: Prohibits unconditional `@pytest.mark.skip` / `@pytest.mark.xfail` decorators, module-level skip/xfail markers, and `pytest.xfail()` calls at FATAL severity.
- `audit_dict_eradication.py`: Enforces zero naked `dict` / `Dict` / `Mapping` / `MutableMapping` annotations with `Any` / `object` values (production, tests, and `scripts/`), zero primitive obsession nested dicts, zero `# noqa` comment tokens, zero `cast(Any, ...)` calls, zero `# type: ignore` comment tokens, zero internal `.get()` calls, zero reflection calls outside the path-based `BOUNDARY_EXEMPTION_FILES`, and zero unapproved ignores in `pyproject.toml`.
- `audit_warning_baseline.py`: Enforces `ResidualDebtCeilingsDTO` exact-equality monotonic reduction across all census categories as Stage 9/10 of `backend_audit_loop.py`.
- `_dart_guardrails.py` & `flutter_audit_loop.py`: Enforce `DGR001`, `DGR004` (zero `// ignore:` suppressions), and `DGR005` (zero non-codec `Map<String, dynamic>`) as unconditional FATAL gates.

### 4.4 Manual Verification Steps
1. Database Re-seed: Execute `uv run python backend_v2/seed/run_seed.py local` to verify clean-slate validation.
2. REST API Check: Execute FastAPI startup to ensure OpenAPI JSON generates without schema validation errors.

### 4.5 Mandatory Final E2E REST API Verification Gate
- Windows PowerShell:
  ```powershell
  $env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
  ```

---

## 5. Required Context & Governance (Rules & KI Registry)

See the canonical `<required_context_rules>` XML block at the top of this document for the authoritative registry of active rules and Knowledge Items.
