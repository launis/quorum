# Task: Workflow MCP-Gateway & Output Profile Relational Architecture (Clean Pydantic V2)

- [x] **Phase 1: Pre-Implementation Technical Debt Cleanups & Schema Alignment**
  - [x] Step 1.1: Clean up `PRINTABLE_SOURCES_RULES["mcp_tools"]` in `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]`
  - [x] Step 1.2: Add `mcp_gateway_id` to `Workflow` model in `@[backend_v2/models/v2_core.py]`
  - [x] Step 1.3: Update `seed_data.json` with `"mcp_gateway_id": "sys_8172bda70c8641c5"` on workflow `wf_9d68c573802341db` in `@[backend_v2/seed/seed_data.json]`
  - [x] Step 1.4: Run database audit & seed verification

- [x] **Phase 2: Database Repository, Service Layer & SDUI Integration**
  - [x] Step 2.1: Update `ISystemRepository.get_mcp_gateways` in `@[backend_v2/database/interfaces.py]`
  - [x] Step 2.2: Implement ID filtering and `ResourceNotFoundError` in `@[backend_v2/database/repositories/system.py]`
  - [x] Step 2.3: Clean up `SystemConfigService.get_mcp_gateways` in `@[backend_v2/services/studio/system_config_service.py]`
  - [x] Step 2.4: Add `mcp_tools_map` to `AdapterContext` in `@[backend_v2/services/sdui/adapters/base_adapter.py]`
  - [x] Step 2.5: Inject `mcp_tools_map` in `BlueprintTransformer` in `@[backend_v2/services/blueprint.py]`
  - [x] Step 2.6: Dynamically resolve tool names in `PrintableSourcesAdapter` in `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]`
  - [x] Step 2.7: Update & expand unit tests across `test_printable_sources_adapter.py`, `test_repository.py`, `test_studio.py`

- [x] **Phase 3: Client App Model & UI Support**
  - [x] Step 3.1: Add `mcpGatewayId` to Flutter `Workflow` Freezed model in `@[client_app_v2/lib/features/studio/models/workflow.dart]` and run Freezed build
  - [x] Step 3.2: Add MCP Gateway dropdown selector in `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_general_tab.dart]`
  - [x] Step 3.3: Update ARB localization files in `@[client_app_v2/lib/l10n/app_en.arb]` and `@[client_app_v2/lib/l10n/app_fi.arb]`

- [x] **Phase 4: Universal Quality Gates & E2E Validation**
  - [x] Step 4.1: Run `backend_audit_loop.py` on all modified Python files
  - [x] Step 4.2: Run `flutter_audit_loop.py` on all modified Dart files
  - [x] Step 4.3: Run E2E SDUI semantic parity test `test_sdui_semantic_parity.py` and Tavily E2E pipeline test `test_tavily_e2e_full_pipeline.py`
