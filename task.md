# Task Checklist: Dynamic Provider Discovery, Hardcoded Preset Eradication & Model Registry Canonical Restoration

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

- [x] **Phase 1: Pre-Implementation Cleanups & 1-Hop Caller Synchronization**
  - [x] 1.1 Backend Handler Caching, Timeout & Exception Hardening (`@[backend_v2/llm/handler.py]`)
  - [x] 1.2 Eliminate Lazy Fallback Chains in Vertex Adapter (`@[backend_v2/llm/adapters/vertex_adapter.py]`)
  - [x] 1.3 Deprecate static 6-item constraint in `GCPVertexLocation` (`@[backend_v2/models/enums.py]`)
  - [x] 1.4 Synchronize 1-Hop Test Suites for Injected Handler Signature (`@[backend_v2/tests/unit/services/studio/test_system_config_service.py]`, `@[backend_v2/tests/unit/test_model_registry.py]`, `@[backend_v2/tests/unit/test_model_registry_discovery.py]`)
  - [x] 1.5 Flutter L10n Tooltip Registration (`@[client_app_v2/lib/l10n/app_en.arb]`, `@[client_app_v2/lib/l10n/app_fi.arb]`)

- [x] **Phase 2: Dynamic Google Vertex AI Location Discovery & Backend Integration**
  - [x] 2.1 Implement `fetch_vertex_locations(settings)` in `@[backend_v2/llm/handler.py]`
  - [x] 2.2 Update `StudioSystemConfigService.get_supported_locations` in `@[backend_v2/services/studio/system_config_service.py]`
  - [x] 2.3 Update API route in `@[backend_v2/api/routers/studio/model_registry.py]` with `LLMHandlerDep`
  - [x] 2.4 Run backend unit tests and quality gate

- [x] **Phase 3: Seed Vault Canonical Stack Restoration & DB Sync**
  - [x] 3.1 Restore Google AI Studio Stack (`sys_e26807f3bfa3454d`) to `gemini/gemini-3.8-flash` in `@[backend_v2/seed/seed_data.json]`
  - [x] 3.2 Verify Google Cloud Vertex AI Sovereign Stack (`sys_b1c2d3e4f5a60718`) in `@[backend_v2/seed/seed_data.json]`
  - [x] 3.3 Two-Phase Pre-Flight In-Memory Validation & Reseed `@[data/db_v2.json]`
  - [x] 3.4 Verify seed architectural guardrails and provider separation tests

- [x] **Phase 4: Flutter Studio Desktop Pro Tool UX & Freezed GcpLocation**
  - [x] 4.1 Create strongly-typed Freezed model `@[client_app_v2/lib/features/studio/models/gcp_location.dart]`
  - [x] 4.2 Run Flutter code generation (`build_runner` and `gen-l10n`)
  - [x] 4.3 Update `@[client_app_v2/lib/core/api/studio_client.dart]` and `@[client_app_v2/lib/features/studio/controllers/model_registry_controller.dart]`
  - [x] 4.4 Upgrade `@[client_app_v2/lib/features/studio/views/model_registry_view.dart]` with Desktop Pro Tool UX
  - [x] 4.5 Run Flutter quality gate and verify widget/unit tests

- [x] **Phase 5: Global Audit Loops & Verification**
  - [x] 5.1 Run full backend audit loop
  - [x] 5.2 Run full flutter audit loop
  - [x] 5.3 Route to `/tier8-audit-plan`

# Session Handover Context
- Target Plan: `c:\Users\risto\.gemini\antigravity-ide\brain\42785eb8-aa27-453d-b3fa-cb91fa47c5c1\implementation_plan.md`
- Work Completed:
  - Dynamic GCP Vertex AI location discovery implemented in `backend_v2/llm/handler.py` and exposed via `StudioSystemConfigService.get_supported_locations` and `/studio/locations` endpoint.
  - Eradicated hardcoded 6-item location list and lazy fallbacks across backend and frontend.
  - Restored Google AI Studio Stack (`sys_e26807f3bfa3454d`) to `gemini/gemini-3.8-flash` across all 4 cognitive tiers in `seed_data.json` and synchronized `data/db_v2.json`.
  - Preserved EU Hamina (`europe-north1`) active regional models (`gemini-2.5-flash`, `gemini-2.5-pro`) on Vertex AI Sovereign Stack (`sys_b1c2d3e4f5a60718`).
  - Implemented Desktop Pro Tool UX in `ModelRegistryView` with typed `GcpLocation` Freezed model, inline refresh buttons, non-blocking loading states, error badges, and Riverpod `cacheFor`.
  - Quality gates passed 100%: Ruff formatting, MyPy strict typing, AST guardrails, Pytest suites, Dart formatting, Dart analysis, and Flutter widget tests.
