# Tracker: Sovereign Dynamic Model Discovery & Google Providers Decoupling
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Sovereign_Dynamic_Model_Discovery_and_Google_Providers_Decoupling.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Step Execution Status
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Sovereign_Dynamic_Model_Discovery_and_Google_Providers_Decoupling.md]
- [x] **[OK] Execution:** `/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Sovereign_Dynamic_Model_Discovery_and_Google_Providers_Decoupling.md] @[docs/implementationplans/TRACKER_Sovereign_Dynamic_Model_Discovery_and_Google_Providers_Decoupling.md]`
  - [x] Step 1: PRE_IMPLEMENTATION_TECHNICAL_DEBT_CLEANUP
  - [x] Step 2: ENUMS_MODERNIZATION_AND_DOCUMENT_ID_PURGE
  - [x] Step 3: SETTINGS_AND_CREDENTIAL_DECOUPLING
  - [x] Step 4: PROVIDER_FACTORY_AND_ADAPTER_SOVEREIGNTY
  - [x] Step 5: LIVE_MODEL_DISCOVERY_AND_VALIDATION_IN_HANDLER
  - [x] Step 6: DYNAMIC_DATABASE_MODEL_REGISTRY_REPOSITORY
  - [x] Step 7: WORKFLOW_AND_STUDIO_SERVICE_REGISTRY_BINDING
  - [x] Step 8: FLUTTER_FREEZED_MODEL_AND_LOCALIZATION_PARITY
  - [x] Step 9: QUORUM_STUDIO_MODEL_REGISTRY_VIEW_MODERNIZATION
  - [x] Step 10: UNIT_TEST_SUITE_AND_FIXTURE_HARMONIZATION
  - [x] Step 11: FLUTTER_WIDGET_TESTING_AND_AUDIT
  - [x] Step 12: SINGLE_RUN_E2E_VARIANCE_VERIFICATION
  - [x] Step 13: KNOWLEDGE_ITEM_SYNCHRONIZATION
  - [x] Step 14: AS_BUILT_ARCHITECTURE_DOCUMENTATION_SYNCHRONIZATION
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Sovereign_Dynamic_Model_Discovery_and_Google_Providers_Decoupling.md] @[docs/implementationplans/TRACKER_Sovereign_Dynamic_Model_Discovery_and_Google_Providers_Decoupling.md]`

### Post-Implementation Gates
- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [x] **[OK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified @-referenced production backend files:
  - [x] @[backend_v2/models/enums.py]
  - [x] @[backend_v2/settings.py]
  - [x] @[backend_v2/llm/adapters/adapter_factory.py]
  - [x] @[backend_v2/llm/adapters/base_adapter.py]
  - [x] @[backend_v2/llm/handler.py]
  - [x] @[backend_v2/llm/provider.py]
  - [x] @[backend_v2/models/v2_core.py]
  - [x] @[backend_v2/models/dtos/studio.py]
  - [x] @[backend_v2/services/studio/workflow_service.py]
  - [x] @[backend_v2/services/studio/system_config_service.py]
  - [x] @[backend_v2/database/repositories/system.py]
  - [x] @[backend_v2/seed/seed_data.json]
- [x] **[OK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified @-referenced production Flutter files:
  - [x] @[client_app_v2/lib/features/studio/models/model_config.dart]
  - [x] @[client_app_v2/lib/features/studio/models/workflow.dart]
  - [x] @[client_app_v2/lib/features/studio/views/model_registry_view.dart]
  - [x] @[client_app_v2/lib/l10n/app_en.arb]
  - [x] @[client_app_v2/lib/l10n/app_fi.arb]
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update
- [x] **[OK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to anchor physical implementation in `docs/architecture/` (scoped to relevant documents), update relevant Knowledge Items, and synchronize `.agents/rules/04_directory_reference.md`.
  - [x] Knowledge Item Updated: @[ki_provider_agnostic_caching.md] (Sovereign Google Vertex AI and Google AI Studio decoupling, typed relation invariants, live model discovery hub)
  - [x] Knowledge Item Updated: @[ki_desktop_pro_tool_studio_ux.md] (Desktop Pro Tool UX for Model Registry: dynamic availableModelsProvider dropdown and conditional regional dropdown)
  - [x] Architecture Document Updated: @[docs/architecture/01_system_context_and_invariants.md] (Decoupled credential injection and dynamic database-driven registry resolution)
  - [x] Architecture Document Updated: @[docs/architecture/03_cognitive_orchestration_engine.md] (Provider factory decoupling, adapter sovereignty, and live model discovery topology)
  - [x] Architecture Rule Synchronized: @[.agents/rules/04_directory_reference.md]

### Final Plan Audit
- [x] **[OK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Sovereign_Dynamic_Model_Discovery_and_Google_Providers_Decoupling.md] @[docs/implementationplans/TRACKER_Sovereign_Dynamic_Model_Discovery_and_Google_Providers_Decoupling.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent
- **Atomic Commit Mandate**: After each successful quality gate verification, commit changes atomically with strict Conventional Commits syntax (`<type>(<scope>): <summary>`). List all staged files explicitly.
- **Seeding Environment**: If database re-seeding is required, execute `uv run python backend_v2/seed/run_seed.py local`.
- **Quality Gates**:
  - For Python changes: `uv run python scripts/backend_audit_loop.py <target_path> --test`
  - For Flutter changes: `uv run python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
- **Execution Mode**: Supports Step-by-Step (default pause per step) and Continuous Full-Auto Mode (invoked via `/tier2-execute --full-auto`).
- **Context Budget Watchdog**: In Continuous Mode, proactively trigger `/tier5-session-handover` when the context budget limit is reached: >8 turns, 3 atomic commits, or >5 modified complex files.
- **Workflow Loop**: `/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Sovereign_Dynamic_Model_Discovery_and_Google_Providers_Decoupling.md] @[docs/implementationplans/TRACKER_Sovereign_Dynamic_Model_Discovery_and_Google_Providers_Decoupling.md]` -> `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Sovereign_Dynamic_Model_Discovery_and_Google_Providers_Decoupling.md] @[docs/implementationplans/TRACKER_Sovereign_Dynamic_Model_Discovery_and_Google_Providers_Decoupling.md]` -> Post-Implementation Hardening Gates (`/tier2-hardening-backend`, `/tier2-hardening-frontend`) -> `/tier7-describe-architecture`.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-01 | Pre-implementation technical debt cleanup: remove ad-hoc `os.environ.get`, delete LiteLLM catalog fallback loops, fix non-Vertex location requirement, replace magic constants | Step 1 | [x] |
| REQ-02 | Modernize enums: eradicate `GOOGLE = "google"`, add `VERTEX_AI` and `AI_STUDIO`, add `GCPVertexDiscoveryRegion`, eradicate `SystemConfigID.MODEL_REGISTRY` | Step 2 | [x] |
| REQ-03 | Decouple settings and credentials: GCP ADC for Vertex AI vs `google_api_key` for AI Studio, update `enabled_providers`, add `pacing_delay_ai_studio_seconds` | Step 3 | [x] |
| REQ-04 | Provider factory and adapter decoupling: route strictly by typed `provider_type`, update `LLMCacheAdapterFactory` and pacing in `BaseLLMAdapter` | Step 4 | [x] |
| REQ-05 | Live model discovery in `LLMHandler`: query Vertex AI via `"us-central1"` hub with live regional validation, query AI Studio via direct API key, derive platform strictly from provider | Step 5 | [x] |
| REQ-06 | Dynamic database model registry repository: require explicit non-empty `registry_id` (fail-fast), deterministic sorting `(name, id)`, preserve singleton in-place upsert | Step 6 | [x] |
| REQ-07 | Workflow and Studio service binding: eradicate hardcoded registry ID defaults from `Workflow` and `WorkflowCreateDTO`, dynamically bind active registry in `create_workflow_draft`, synchronize seed vault | Step 7 | [x] |
| REQ-08 | Flutter Freezed model and localization parity: update `ModelConfig.defaultProvider` to `'ai_studio'`, remove default registry ID from `Workflow`, synchronize `.arb` files and rebuild Freezed models | Step 8 | [x] |
| REQ-09 | Quorum Studio Model Registry view modernization: top-level sovereign `Oletustarjoaja` selector, dynamic model dropdown from `availableModelsProvider`, conditional location dropdown strictly for Vertex AI | Step 9 | [x] |
| REQ-10 | Unit test suite and fixture harmonization: create `test_google_providers_separation.py` covering ISTQB partitions, synchronize all 1-hop caller test fixtures, pass backend audit loop | Step 10 | [x] |
| REQ-11 | Flutter widget testing and audit: update `model_registry_view_test.dart` for dynamic dropdowns, conditional location, and error handling, pass flutter audit loop | Step 11 | [x] |
| REQ-12 | Single-run FinOps E2E variance verification: execute variance test with decoupled Vertex AI model registry stack | Step 12 | [x] |
| REQ-13 | Knowledge Item synchronization: update `ki_provider_agnostic_caching.md` and `ki_desktop_pro_tool_studio_ux.md` with decoupled provider contracts | Step 13 | [x] |
| REQ-14 | As-built architecture documentation synchronization: execute `/tier7-describe-architecture` for `01_system_context_and_invariants.md` and `03_cognitive_orchestration_engine.md` | Step 14 | [x] |

# Session Handover Context
## Achieved
- **Decoupled Google Providers:** Completely separated `LLMProvider.VERTEX_AI` (GCP ADC via `service-account.json` or workload identity) and `LLMProvider.AI_STUDIO` (`google_api_key`), eliminating the merged `"google"` pseudo-provider across enums, settings, adapters, repositories, and UI.
- **Dynamic Model Garden Discovery:** Implemented live discovery in `LLMHandler` querying `us-central1` hub with live regional validation (`europe-north1` Hamina) for Vertex AI, and direct discovery for AI Studio and OpenAI.
- **Dynamic Database-Driven Registry Binding:** Eliminated hardcoded `SystemConfigID.MODEL_REGISTRY` and default registry IDs from `Workflow` and `WorkflowCreateDTO`.
- **Flutter Pro Tool UX Parity:** Implemented sovereign top-level provider dropdown (`Oletustarjoaja`), dynamic model dropdown via `availableModelsProvider`, and conditional regional selector for Vertex AI in `model_registry_view.dart`. Rebuilt Freezed models with 100% test pass.
- **Strict Quality Gates & 0 Suppressions:** Created comprehensive ISTQB tests in `test_google_providers_separation.py`, harmonized all caller fixtures, passed backend audit loop (Ruff, MyPy, Pytest) with >90% coverage on all modified targets, and passed Flutter widget test suite.
- **E2E FinOps Single-Run Verification:** Executed live E2E variance test `exe_3ea398339da44c06` with sovereign Vertex AI model registry (`sys_b1c2d3e4f5a60718`) producing 24 trace events with `PASSED` status.
- **Knowledge Base & Architecture Sync:** Synchronized `ki_provider_agnostic_caching.md`, `ki_desktop_pro_tool_studio_ux.md`, `01_system_context_and_invariants.md`, `03_cognitive_orchestration_engine.md`, and `.agents/rules/04_directory_reference.md` in timeless present tense.

## Learned
- Strict separation of Google providers eliminates credential leakage and silent fallback drift.
- Model Garden discovery via `us-central1` hub requires parallel live validation against target GCP regions to prevent runtime 404s.
- Model registry selection is 100% dynamic from database and UI without code-level document ID fallbacks.
- Unit test mock repositories must provide both `get_model_registry` and `get_all_model_registries` when exercising `LLMClient.from_tier`.

## Remaining
- None. Ready for /tier8-audit-plan.

## Resume Command
- Plan Audit:
  `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Sovereign_Dynamic_Model_Discovery_and_Google_Providers_Decoupling.md] @[docs/implementationplans/TRACKER_Sovereign_Dynamic_Model_Discovery_and_Google_Providers_Decoupling.md]`
