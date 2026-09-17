# Implementation Plan: Sovereign Dynamic Model Discovery & Google Providers Decoupling

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

Restore fully dynamic, live provider-driven model discovery and location querying in Quorum Studio's Model Registry (`Mallirekisteri`).

**Absolute Sovereign SSOT, Typed Relations & Zero-Fallback Mandate:**
- **Typed Relations Only (`startswith` & Substrings Strictly Banned):** Ban all `model_name.startswith(...)`, `"gemini" in model_name`, `"openai/" in model_name`, and heuristic prefix parsing. Provider routing and credential binding MUST be resolved 100% by the explicit, typed relation `provider_type: LLMProvider` (or `config.provider`). `model_name` is treated strictly as an opaque target identifier passed to the downstream SDK, NEVER an analytical payload parsed to guess or override provider types. This constraint is permanently anchored in `AGENTS.md`, `00-antigravity-core.md`, `05_llm_architecture.md`, and `ki_provider_agnostic_caching.md`.
- **Zero Fallback Chains:** Ban all `or`, `.get(key, default)`, `try A else B`, offline catalog stuffing (purging `litellm.model_list` fallback loops), and legacy bridge aliases. Every operation has exactly ONE authoritative path, ONE credential source, and ONE deterministic execution pipeline. If credentials or upstream connections are missing, fail-fast immediately with typed `AppException`.
- **Zero Alternative Methods:** Every provider discovery and provider creation operates via a single direct method without secondary fallback pathways.
- **Complete Eradication of Merged `"google"` Pseudo-Provider:** `LLMProvider` and `LLMProviderName` strictly define `VERTEX_AI = "vertex_ai"` and `AI_STUDIO = "ai_studio"`. The merged `"google"` pseudo-provider is completely purged from all enums, services, seed stacks, and tests.

---

## 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Zero Fallback Mandate) | 3. Approved Best Practice (Sovereign SSOT Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Backend Enums (`@[backend_v2/models/enums.py#L149-L156]`, `@[backend_v2/models/enums.py#L199-L203]`, `@[backend_v2/models/enums.py#L477-L486]`, `@[backend_v2/models/enums.py#L500-L507]`)** | Ban merged `"google"` pseudo-provider, ban legacy bridge aliases, ban arbitrary discovery region strings. Ban heuristic string parsing. Ban hardcoded database document IDs in Python enums (`SystemConfigID.MODEL_REGISTRY`). | Explicit sovereign members: `LLMProvider.VERTEX_AI = "vertex_ai"` and `LLMProvider.AI_STUDIO = "ai_studio"`. Dedicated SSOT enum `GCPVertexDiscoveryRegion(StrEnum)` with `US_CENTRAL1 = "us-central1"`. Purge `GOOGLE = "google"` completely from `LLMProvider` and `LLMProviderName`. Purge `SystemConfigID.MODEL_REGISTRY = "sys_e26807f3bfa3454d"` entirely (database document IDs exist only in persistent state, never hardcoded in code enums). Update `SystemConfigModelRegistry.default_provider` default to `LLMProvider.AI_STUDIO`. | Align `LLMProvider`, `LLMProviderName`, and `LLMPlatformType` contracts 1:1. Zero duplicate platform definitions; zero hardcoded document IDs in code. | `test_google_providers_separation.py` asserts exact enum members and strict serialization. |
| **Backend Settings (`@[backend_v2/settings.py#L51-L818]`, `@[backend_v2/settings.py#L716-L741]`)** | Ban ad-hoc `os.environ.get()` calls, multi-key fallback chains, and injecting API keys into Vertex AI. Ban returning legacy `"google"` in `enabled_providers`. Ban magic code-level default registry IDs (`default_model_registry_id`). | Strictly decoupled credential SSOT: 1) Vertex AI uses GCP ADC via `GOOGLE_APPLICATION_CREDENTIALS` (`service-account.json` in root). 2) AI Studio uses `google_api_key` loaded from `.env` via `validation_alias=AliasChoices("google_api_key", "gemini_api_key")`. 3) OpenAI uses `openai_api_key`. 4) Anthropic uses `anthropic_api_key`. Default `discovery_location` = "us-central1" (GCPVertexDiscoveryRegion US_CENTRAL1 value). The `Settings.enabled_providers` property computes sovereign `vertex_ai` and `ai_studio` independently. Zero `default_model_registry_id` in settings: registry selection is 100% dynamic from UI & database. | Zero fallback loaders; zero alternative methods; single declarative Pydantic settings attribute. | Unit test in `test_google_providers_separation.py` verifying direct credential mapping, fail-fast when missing, and `enabled_providers` separation. |
| **LLM Provider Factory (`@[backend_v2/llm/provider.py#L1427-L1605]`, `@[backend_v2/llm/provider.py#L1430-L1605]`)** | **BAN `startswith` AND SUBSTRING INSPECTION**: Ban `model_name.startswith(...)`, `"gemini" in model_name`, `"openai/" in model_name.lower()`, fallback match statements, and `os.getenv()`. | **Typed Relation Sovereignty**: Credential routing and provider creation are governed 100% by typed `provider_type: LLMProvider` (or `config.provider`). `provider_type == "vertex_ai"` -> `api_key = None` (GCP ADC). `provider_type == "ai_studio"` -> `api_key = settings.google_api_key`. `provider_type == "openai"` -> `api_key = settings.openai_api_key`. `provider_type == "anthropic"` -> `api_key = settings.anthropic_api_key`. If missing, immediately raise `ConfigurationError(ErrorCodes.CONFIGURATION_ERROR)`. | Prune 3 nested fallback branches, `startswith` mutations, and regex/substring checks. | `test_google_providers_separation.py` asserts Vertex AI receives no API key, AI Studio fails fast without API key, and provider routing does not inspect model_name strings. |
| **LLM Cache Adapter Factory (`@[backend_v2/llm/adapters/adapter_factory.py#L19-L155]`, `@[backend_v2/llm/adapters/adapter_factory.py#L27-L155]`)** | Ban umbrella `"google"` case falling back to `model_name` substring check (`"vertex_ai/" in model_name`). | Clean 1:1 match cases: `case LLMProviderName.VERTEX_AI | "vertex_ai": VertexCacheAdapter()` and `case LLMProviderName.AI_STUDIO | "ai_studio": GoogleAIStudioCacheAdapter()`. Eradicate `case LLMProviderName.GOOGLE | "google":` entirely. | Prune substring matching block in `adapter_factory.py`. Zero analytical model_name inspection. | `test_google_providers_separation.py` asserts `LLMCacheAdapterFactory.get_adapter("vertex_ai")` and `get_adapter("ai_studio")` return sovereign adapters. |
| **Base Adapter Provider Pacing (`@[backend_v2/llm/adapters/base_adapter.py#L75-L136]`)** | Ban merged `"google"` in pacing delays (`case LLMProviderName.VERTEX_AI.value \| LLMProviderName.GOOGLE.value`). | Explicit pacing branches: `case LLMProviderName.VERTEX_AI.value: delay = settings.pacing_delay_vertex_seconds` and `case LLMProviderName.AI_STUDIO.value: delay = pacing_delay_ai_studio_seconds`. | Eliminate shared pacing state and fallbacks. | `test_base_adapter.py` asserting independent pacing values per sovereign provider. |
| **LLM Handler Discovery & Validation (`@[backend_v2/llm/handler.py#L92-L227]`, `@[backend_v2/llm/handler.py#L229-L289]`, `@[backend_v2/llm/handler.py#L300-L369]`, `@[backend_v2/llm/handler.py#L371-L400]`, `@[backend_v2/llm/handler.py#L402-L477]`, `@[backend_v2/llm/handler.py#L531-L655]`)** | Ban LiteLLM offline catalog fallbacks (`litellm.model_list` fallback), ban provider aliases (`models["google"] = ...`), ban premature `ValueError` on `target_location` when querying non-Vertex providers, ban `model_name.startswith` checks in model validation, and ban raw `os.environ.get()`. | Pure live discovery: 1) Vertex AI discovers from Google Model Garden via central hub "us-central1" and validates live in `target_location`. 2) AI Studio queries `genai.Client(api_key=settings.google_api_key).models.list()`. 3) OpenAI queries `openai.OpenAI(api_key=settings.openai_api_key).models.list()`. 4) Anthropic queries official catalog. Zero fallback catalog stuffing. Require `target_location` ONLY when Vertex AI is queried. Strict model validation routes `platform` strictly from `provider`. Replace magic constants (`DEFAULT_HTTP_TIMEOUT = 10`, `MAX_DISCOVERY_CONCURRENCY = 20`). | Prune LiteLLM catalog fallback loops, delete `_fetch_google_models`, prune redundant multi-provider dictionary mergers (`models["google"]`), prune `startswith` parsing in validation. | `test_handler.py` and `test_google_providers_separation.py` asserting live model discovery, isolation of regional checks, and fail-fast errors on missing dependencies. |
| **Studio System Config Service (`@[backend_v2/services/studio/system_config_service.py#L43-L91]`, `@[backend_v2/services/studio/system_config_service.py#L93-L145]`, `@[backend_v2/services/studio/system_config_service.py#L147-L189]`, `@[backend_v2/services/studio/system_config_service.py#L276-L318]`)** | Ban hardcoded `default_provider=LLMProvider.GOOGLE` in draft creations. | Draft creation sets `default_provider=LLMProvider.AI_STUDIO`, tier profiles use `provider="ai_studio"`. `get_supported_platforms` returns distinct `vertex_ai` and `ai_studio` platform DTOs. | Single unified draft factory; zero legacy fallback aliases. | `test_system_config_service.py` asserting draft creation conforms to Pydantic schema with `ai_studio`. |
| **Frontend ModelConfig DTO (`@[client_app_v2/lib/features/studio/models/model_config.dart]`)** | Ban default `'google'` fallback in Freezed client model annotations. | `@JsonKey(name: 'default_provider') @Default('ai_studio') String defaultProvider` ensures 1:1 cross-domain parity with backend `v2_core.py`. | Zero client-side translation layers; direct serialization parity. | Flutter domain parity tests and build runner generation. |
| **Model Registry View (`@[client_app_v2/lib/features/studio/views/model_registry_view.dart]`)** | Ban duplicate tier-level platform dropdowns, tier-level location dropdowns, hardcoded text fields for model names, and arbitrary string defaults. | Top-level `defaultProvider` in `_buildSystemAttributes` is sovereign for the stack. Dynamic `DropdownButtonFormField<String>` (`isExpanded: true`) populated directly from `availableModelsProvider`. Location dropdown rendered strictly for Vertex AI. | Prune 4 redundant platform selectors, 4 redundant location selectors, and arbitrary tier fallback instances. | `model_registry_view_test.dart` verifies regional dropdown visibility, dynamic model dropdown population, and zero false-positive discard dialogs. |
| **Localization (`@[client_app_v2/lib/l10n/app_en.arb]`, `@[client_app_v2/lib/l10n/app_fi.arb]`)** | Ban hardcoded English UI strings in dropdown menus and labels. | Localized keys (`platformVertexAi`, `platformAiStudio`, `platformOpenAi`, `platformAnthropic`) in both `app_en.arb` and `app_fi.arb`. | Direct lookup via `AppLocalizations.of(context)`; no parallel translation dictionaries. | Flutter audit loop checks `.arb` compile-time parity and AST completeness. |
| **Seed Vault (`@[backend_v2/seed/seed_data.json]`)** | Ban conflated `"google"` provider definitions where Vertex AI and AI Studio are mixed into a single stack. | Maintain sovereign stacks: `sys_e26807f3bfa3454d` for Google AI Studio (`default_provider: "ai_studio"`) and `sys_b1c2d3e4f5a60718` for Google Cloud Vertex AI (`default_provider: "vertex_ai"`, Hamina `europe-north1`). | Prune duplicate/dead stack configurations. Stored database records hold their own IDs; code never hardcodes them. | `uv run python scripts/audit_database_atoms.py --strict` and `run_seed.py local --dry-run`. |
| **Backend System Repository & Workflow Binding (`@[backend_v2/database/repositories/system.py#L31-L62]`, `@[backend_v2/database/repositories/system.py#L64-L75]`, `@[backend_v2/database/repositories/system.py#L77-L91]`, `@[backend_v2/database/repositories/system.py#L129-L149]`, `@[backend_v2/models/v2_core.py#L1379-L1545]`, `@[backend_v2/services/studio/workflow_service.py#L281-L308]`)** | Ban hardcoded raw string literals (`"sys_e26807f3bfa3454d"`), ban code-level default registry IDs (`default_model_registry_id`), and ban backend guessing/fallback chains. | **Pure Dynamic Database-Driven Architecture**: 1) `get_model_registry(self, registry_id: str)` strictly requires `registry_id: str` and raises `ResourceNotFoundError` immediately if missing or non-existent (Fail-Fast). 2) `get_all_model_registries(self)` sorts deterministically by `(m.name, m.id)` without magic priority hacks. 3) `Workflow.model_registry_id` has no hardcoded default in domain models (`v2_core.py`) or DTOs (`studio.py`). 4) Quorum Studio UI and `WorkflowService.create_workflow_draft` query active registries from the database dynamically and bind the first active registry ID. 5) Preserve singleton in-place upsert (`res_list[0]["id"]`) in `update_mcp_gateways`. | Zero code-level default IDs; zero fallback ladders; 100% dynamic UI and database model parameterization. | `test_system_model_registry.py` and `test_workflow_service.py` verify fail-fast error on missing registry ID and dynamic registry binding. |
| **1-Hop Caller Test Fakes & Fixtures (`@[backend_v2/tests/fakes/in_memory_repositories.py#L248-L375]`, `@[backend_v2/tests/unit/database/repositories/test_system.py#L20-L35]`, `@[backend_v2/tests/unit/database/repositories/test_system_model_registry.py#L50-L62]`, `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py#L24-L32]`, `@[backend_v2/tests/unit/test_model_registry.py#L24-L39]`, `@[backend_v2/tests/unit/test_model_registry_discovery.py#L36-L273]`, `@[backend_v2/tests/unit/models/test_v2_core.py#L931-L969]`, `@[backend_v2/tests/unit/database/test_repository.py#L136-L302]`, `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L161-L185]`)** | Ban legacy `LLMProvider.GOOGLE` in test fakes, mocks, and test assertions. | All fixtures synchronized to sovereign `LLMProvider.AI_STUDIO` or `LLMProvider.VERTEX_AI`. | Zero mock-level legacy shims. | Pytest suite passes 100% without deprecation or schema warnings. |
| **Knowledge Base & As-Built Architecture (`@[ki_provider_agnostic_caching.md]`, `@[ki_desktop_pro_tool_studio_ux.md]`, `@[docs/architecture/01_system_context_and_invariants.md]`, `@[docs/architecture/03_cognitive_orchestration_engine.md]`)** | Ban architectural drift, outdated Knowledge Items, and historical logs or phase markers in architecture docs. | Update `ki_provider_agnostic_caching.md` and `ki_desktop_pro_tool_studio_ux.md`. Execute `/tier7-describe-architecture` for `01_system_context_and_invariants.md` and `03_cognitive_orchestration_engine.md` maintaining strictly timeless present-tense narrative. | Pure as-built documentation; zero project phase markers or artificial Law labels. | `audit_markdown_boundaries.py` passes 100% on all documentation references. |

---

## Phase 1: Pre-Implementation Cleanups (Zero-Fallback & Discovered Tech Debt Eradication)

1. **Remove ad-hoc `os.environ.get`, `os.getenv`, and multi-variable fallback chains**:
   - In `@[backend_v2/llm/handler.py#L229-L289]`, remove `os.environ.get("GEMINI_API_KEY")`. Rely strictly on typed `settings.google_api_key`.
   - In `@[backend_v2/llm/handler.py#L229-L289]`, **delete LiteLLM catalog fallback loop** (`for lm in litellm.model_list:`). If AI Studio API returns no models or fails, raise fail-fast `ServiceUnavailableError`. Zero fallback guessing.
   - In `@[backend_v2/llm/handler.py#L300-L369]`, remove `os.environ.get("OPENAI_API_KEY")`. Rely strictly on typed `settings.openai_api_key`.
   - In `@[backend_v2/llm/provider.py#L1430-L1605]`, eradicate fallback match statements and `os.getenv("OPENAI_API_KEY")` / `os.getenv("ANTHROPIC_API_KEY")`.
2. **Eradicate `startswith` and prefix mutations in `provider.py` and `handler.py`**:
   - In `@[backend_v2/llm/provider.py#L1430-L1605]`, delete `if provider_type == "anthropic" and not model_name.startswith("anthropic/"): model_name = f"anthropic/{model_name}"`. Model names must not be heuristically prefixed or mutated.
   - In `@[backend_v2/llm/provider.py#L1430-L1605]`, delete substring inspections (`"gemini" in model_name`, `"gpt" in model_name`, `"claude" in model_name`).
   - In `@[backend_v2/llm/provider.py#L1430-L1605]`, delete `"openai/" in model_name.lower()`.
   - In `@[backend_v2/llm/provider.py#L1430-L1605]`, eradicate `case "gemini" | "vertex_ai": resolved_api_key = settings.google_api_key`. Vertex AI receives `api_key = None`. AI Studio receives `settings.google_api_key`.
   - In `@[backend_v2/llm/handler.py#L531-L655]`, eradicate `platform=LLMPlatformType.VERTEX_AI.value if model_name.startswith("vertex_ai/") else (LLMPlatformType.AI_STUDIO.value if model_name.startswith("gemini/") else None)`. Derive `platform` 100% from `provider`: `platform=LLMPlatformType.VERTEX_AI.value` if `provider == LLMProviderName.VERTEX_AI.value` else `LLMPlatformType.AI_STUDIO.value`.
3. **Fix Premature `ValueError` on `target_location` in `handler.py` for Non-Vertex Providers**:
   - In `@[backend_v2/llm/handler.py#L402-L477]`, do NOT require `target_location` unconditionally at the top of `fetch_all_available_models`. Enforce `target_location` check ONLY when `norm_platform in [LLMPlatformType.VERTEX_AI.value, LLMPlatformType.ALL.value]` or `LLMPlatformType.VERTEX_AI.value in active_providers`. This allows AI Studio, OpenAI, and Anthropic discovery to proceed cleanly without requiring dummy or missing `vertex_location`.
4. **Purge Magic Numbers and Timeouts in `handler.py`**:
   - In `@[backend_v2/llm/handler.py#L92-L227]`, replace magic timeout `timeout=5` with explicit constant `DEFAULT_HTTP_TIMEOUT = 10`.
   - In `@[backend_v2/llm/handler.py#L92-L227]`, replace magic worker pool size `max_workers=20` with declared top-level constant `MAX_DISCOVERY_CONCURRENCY = 20`.
5. **Purge merged `"google"` pseudo-provider from Enums, Adapter Factory, Handler, Settings, and Models**:
   - In `@[backend_v2/models/enums.py#L149-L156]`, eradicate `GOOGLE = "google"` from `LLMProvider`. Add `VERTEX_AI = "vertex_ai"` and `AI_STUDIO = "ai_studio"`.
   - In `@[backend_v2/models/enums.py#L477-L486]`, eradicate `GOOGLE = "google"` from `LLMProviderName`.
   - In `@[backend_v2/models/v2_core.py#L464-L488]`, update `default_provider` default in `SystemConfigModelRegistry` from `LLMProvider.GOOGLE` to `LLMProvider.AI_STUDIO`.
   - In `@[backend_v2/llm/adapters/adapter_factory.py#L27-L155]`, eradicate `case LLMProviderName.GOOGLE | "google":` and its model name substring checks.
   - In `@[backend_v2/llm/adapters/base_adapter.py#L75-L136]`, eradicate `LLMProviderName.GOOGLE.value` from pacing matching and decouple `vertex_ai` and `ai_studio`.
   - In `@[backend_v2/settings.py#L716-L741]`, update `enabled_providers` property: append `"vertex_ai"` and `"ai_studio"` separately instead of `"google"`.
   - In `@[backend_v2/llm/handler.py#L402-L477]`, eradicate `models[LLMProviderName.GOOGLE.value] = ...` double-binding.
   - In `@[backend_v2/llm/handler.py#L402-L477]`, eradicate `_fetch_google_models` and route `vertex_ai` and `ai_studio` directly.
   - In `@[backend_v2/services/studio/system_config_service.py#L276-L318]`, update `create_system_config_draft` to use `default_provider=LLMProvider.AI_STUDIO` and tier provider `"ai_studio"`.
6. **Eliminate hardcoded dropdown options and arbitrary defaults in `model_registry_view.dart` & `model_config.dart`**:
   - In `@[client_app_v2/lib/features/studio/models/model_config.dart]`, update default provider from `'google'` to `'ai_studio'`.
   - In `@[client_app_v2/lib/features/studio/views/model_registry_view.dart]`, eradicate hardcoded strings `'Google Vertex / AI Studio'`, `'OpenAI'`, `'Anthropic'`. Bind strictly to `l10n.platformVertexAi`, `l10n.platformAiStudio`, `l10n.platformOpenAi`, `l10n.platformAnthropic`.
   - In `@[client_app_v2/lib/features/studio/views/model_registry_view.dart]`, remove arbitrary ternary model fallbacks (`payload.defaultProvider == 'openai' ? 'openai/gpt-4o' : 'gemini/gemini-3.8-flash'`).
7. **Ensure `AliasChoices` and SSOT Discovery Region in `Settings`**:
   - In `@[backend_v2/settings.py#L51-L818]`, ensure `google_api_key` uses `validation_alias=AliasChoices("google_api_key", "gemini_api_key")`.
   - Default `discovery_location` to "us-central1".
   - Add `pacing_delay_ai_studio_seconds: Annotated[int, Field(description="Forced delay between Google AI Studio requests")] = 0`.
8. **Harmonize Test Fixtures & Fakes across 1-Hop Callers**:
   - In `@[backend_v2/tests/fakes/in_memory_repositories.py#L248-L375]`, update default registry fixture to `LLMProvider.AI_STUDIO`.
   - In `@[backend_v2/tests/unit/database/repositories/test_system.py#L20-L35]`, update `default_provider` fixture from `LLMProvider.GOOGLE` to `LLMProvider.AI_STUDIO`.
   - In `@[backend_v2/tests/unit/database/repositories/test_system_model_registry.py#L50-L62]`, update test registry fixtures and assertions to `LLMProvider.AI_STUDIO`.
   - In `@[backend_v2/tests/unit/database/test_repository.py#L136-L302]`, update dummy registry fixture to `LLMProvider.AI_STUDIO`.
   - In `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py#L24-L32]`, update tests to verify `LLMProvider.AI_STUDIO` and assert `client.provider_name == "ai_studio"`.
   - In `@[backend_v2/tests/unit/services/studio/test_system_config_service.py#L210-L222]`, update dummy registry to `LLMProvider.AI_STUDIO`.
   - In `@[backend_v2/tests/unit/llm/adapters/test_adapter_factory.py#L35-L47]`, modernize tests to assert sovereign resolution for `VERTEX_AI` and `AI_STUDIO` and verify `GOOGLE` is completely rejected.
   - In `@[backend_v2/tests/unit/test_model_registry.py#L24-L39]`, update dummy registry fixture from `provider="google"` to `provider="ai_studio"`.
   - In `@[backend_v2/tests/unit/test_model_registry_discovery.py#L36-L273]`, update `ModelProfile` fixtures from `provider="google"` to `provider="vertex_ai"` or `provider="ai_studio"`.
   - In `@[backend_v2/tests/unit/models/test_v2_core.py#L931-L969]`, update dummy profile fixture from `provider="google"` to `provider="ai_studio"`.
   - In `@[backend_v2/tests/unit/models/dtos/test_system.py#L37-L110]`, update dummy profile fixture from `provider="google"` to `provider="ai_studio"`.
   - In `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L161-L185]`, update `ModelProfile` fixture from `provider="google"` to `provider="ai_studio"`.
9. **Eradicate Hardcoded Model Registry ID & Magic Fallbacks via Pure Dynamic Database-Driven Architecture**:
   - In `@[backend_v2/database/repositories/system.py#L31-L62]`, eradicate raw string literal `"sys_e26807f3bfa3454d"`.
   - Make `get_model_registry(self, registry_id: str)` require an explicit, non-empty `registry_id: str`. If `registry_id` is missing, empty, or not found in `system_config`, immediately raise `ResourceNotFoundError(resource_type="system_config", resource_id=registry_id)`. Zero fallback guessing, zero magic defaults.
   - In `@[backend_v2/database/repositories/system.py#L64-L75]`, delete the sorting hack. Sort deterministically purely by `(m.name, m.id)`.
   - In `@[backend_v2/database/repositories/system.py#L77-L91]`, update `doc_id = registry_data.id` directly.
   - In `@[backend_v2/models/enums.py#L199-L203]`, eradicate hardcoded `SystemConfigID.MODEL_REGISTRY = "sys_e26807f3bfa3454d"`. System configuration document IDs are database entities, never hardcoded Python constants.
   - In `@[backend_v2/models/v2_core.py#L1379-L1545]`, remove hardcoded default `default="sys_e26807f3bfa3454d"` from `Workflow.model_registry_id`.
   - In `@[backend_v2/models/dtos/studio.py#L99-L157]`, remove hardcoded default `"sys_e26807f3bfa3454d"` from `WorkflowCreateDTO.model_registry_id`.
   - In `@[client_app_v2/lib/features/studio/models/workflow.dart]`, remove `@Default("sys_e26807f3bfa3454d")` from `modelRegistryId`.
   - Do NOT add `default_model_registry_id` to `settings.py`. Zero magic guessing in configuration.
   - **Dynamic Studio UI & Backend Creation Binding**:
     - When drafting a new workflow in Quorum Studio UI, the UI fetches active registries from the database via `modelRegistriesProvider` and dynamically sets `modelRegistryId` to the first active registry ID.
     - In `@[backend_v2/services/studio/workflow_service.py#L281-L308]`, `create_workflow_draft` queries `await self.system_repo.get_all_model_registries()` dynamically and binds `active_registries[0].id`. If no registries exist in the database, raise Fail-Fast `ResourceNotFoundError`.
   - **In-Place Singleton Upsert Lifecycle (`@[backend_v2/database/repositories/system.py#L129-L149]`)**:
     Preserve singleton document ID in `res_list[0]["id"]` query (`doc_id = str(res_list[0]["id"])`) so in-place upsert modifies existing singleton document without generating redundant duplicate IDs.

---

## User Review Required

> [!IMPORTANT]
> **Key Architectural Guarantees (Sovereign SSOT & Zero-Fallback):**
> 1. **Typed Relation Sovereignty (`startswith` & Substring Parsing Strictly Banned)**:
>    - `LLMFactory.create_provider` and `handler.py` resolve providers and credentials **strictly and exclusively** from the typed relation `provider_type: LLMProvider` (or `config.provider`).
>    - Checking `model_name.startswith("vertex_ai/")`, `model_name.startswith("gemini/")`, `"gemini" in model_name`, or `"openai/" in model_name` is **strictly forbidden**.
>    - This mandate is synchronized and enforced in:
>      - `AGENTS.md` (`ban_heuristic_identifier_matching`)
>      - `.agents/rules/00-antigravity-core.md` (`ban_heuristic_identifier_matching`)
>      - `.agents/rules/05_llm_architecture.md` (`ban_heuristic_identifier_matching`)
>      - `ki_provider_agnostic_caching.md` (`typed_provider_relation_sovereignty`)
>
> 2. **Strict Decoupling of Credential Sources & Zero-Hardcoding Mandate (`credential_hardcoding_ban`)**:
>    - **Zero-Hardcoding Law**: NEVER hardcode API keys, bearer tokens, service account credentials, or secrets in source code (`.py`, `.dart`), tests, fixtures, seed files, or git commits. Locally they MUST be resolved strictly through `.env` (via typed `Settings`) or `service-account.json` (via `GOOGLE_APPLICATION_CREDENTIALS`), and in cloud environments via Cloud Secret Managers (GCP Secret Manager, Vault, or container runtime environment variables).
>    - **Google Cloud Vertex AI (`vertex_ai`)**:
>      - **NEVER uses API keys.**
>      - Authenticates strictly and exclusively via Google Cloud Application Default Credentials (ADC) backed by `service-account.json` in the project root (or `GOOGLE_APPLICATION_CREDENTIALS` environment variable set in `run_local.bat` / Docker / Cloud Secret Manager).
>      - Model discovery runs via `google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])` and calls `google.genai.Client(vertexai=True, project=project, location=target_location)`.
>    - **Google AI Studio (`ai_studio`)**:
>      - **NEVER uses service-account.json or GCP projects.**
>      - Authenticates strictly and exclusively via direct API key from `.env` (`GEMINI_API_KEY` or `GOOGLE_API_KEY`), loaded via Pydantic `settings.google_api_key`.
>      - Model discovery runs via `google.genai.Client(api_key=settings.google_api_key).models.list()`. **No LiteLLM catalog fallback.**
>    - **OpenAI (`openai`)**:
>      - Authenticates strictly via `OPENAI_API_KEY` in `.env` / Cloud Secrets, loaded via `settings.openai_api_key`.
>      - Model discovery runs via `openai.OpenAI(api_key=settings.openai_api_key).models.list()`.
>    - **Anthropic (`anthropic`)**:
>      - Authenticates strictly via `ANTHROPIC_API_KEY` in `.env` / Cloud Secrets, loaded via `settings.anthropic_api_key`.
>
> 3. **Deterministic Discovery Hub (SSOT Enum)**:
>    - Vertex AI candidate discovery uses Google's central Model Garden hub: "us-central1" (GCPVertexDiscoveryRegion).
>    - Candidates are validated live in parallel against the active GCP target location (`target_location`, specifically `europe-north1` Hamina).
>    - When the user changes region in the UI, `availableModelsProvider(platform: 'vertex_ai', location: newLocation)` re-validates and re-populates the model dropdown for all tiers.
>
> 4. **Single Top-Level Sovereign Provider Selection**:
>    - `Oletustarjoaja` at the top of the stack (`_buildSystemAttributes`) defines the platform for the entire stack.
>    - The redundant `Alusta` dropdown repeating the platform 4 times across FAST, BALANCED, DEEP, and REASONING is removed.
>    - When `Oletustarjoaja` changes: updates `defaultProvider`, synchronizes `provider` on all 4 tiers, and updates model names to the first available model discovered for the new platform.
>
> 5. **Zero Fallback Dropdown Execution**:
>    - If a tier already has a valid saved `modelName`, it is included in the dropdown items. Discovered models from the live provider API populate the list. No hardcoded mock models are injected.
>
> 6. **Pure Database-Driven Resolution without Backend Guessing (Complete Eradication of Magic Code-Level Document IDs)**:
>    - **Zero hardcoded ID string literals in code**: Eliminate all `sys_e26807f3bfa3454d` string occurrences from codebase logic.
>      - `SystemConfigID.MODEL_REGISTRY` is completely purged from `enums.py`.
>      - `Workflow.model_registry_id` default (`default="sys_e26807f3bfa3454d"`) is removed from domain models (`v2_core.py`) and DTOs (`models/dtos/studio.py`).
>      - `Workflow.modelRegistryId` default (`@Default("sys_e26807f3bfa3454d")`) is removed from Flutter client (`workflow.dart`).
>    - **Zero `default_model_registry_id` setting**:
>      - Do not add default registry setting to `settings.py`.
>      - Do not create multi-level fallback ladders (`settings or enum or first`).
>    - **Fail-Fast `get_model_registry(registry_id: str)`**:
>      - Method strictly requires an explicit, non-empty `registry_id` string.
>      - If `registry_id` is missing or the corresponding document does not exist in database, immediately raise `ResourceNotFoundError(resource_type="system_config", resource_id=registry_id)`.
>    - **Deterministic sorting without privileged code-level IDs**:
>      - `get_all_model_registries()` sorts purely by name and ID: `key=lambda m: (m.name, m.id)`.
>    - **UI and database models guide selection**:
>      - When creating a new workflow, Quorum Studio UI queries active model registries from database (`modelRegistriesProvider`) and binds the first active registry ID directly to `modelRegistryId`.
>      - Backend `create_workflow_draft` queries active registries dynamically from database and binds the first found registry ID. If no registries exist in database, raises Fail-Fast `ResourceNotFoundError`.
>    - **Singleton In-Place Upsert (`system.py#L129-L149`)**:
>      Query `limit=1` preserves existing singleton document ID (`res_list[0]["id"]`), ensuring in-place upsert targets the exact existing record rather than generating duplicate documents.

---

## Proposed Changes

### Frontend (Flutter Client `client_app_v2`)

#### [MODIFY] [model_config.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/models/model_config.dart)

- Update `defaultProvider` default annotation in `ModelConfig`:
  - Change `@Default('google')` to `@Default('ai_studio')` to maintain strict 1:1 cross-domain serialization parity with backend `v2_core.py`.
  - Regenerate Freezed and JSON serialization models via `flutter_audit_loop.py --build`.

#### [MODIFY] [workflow.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/models/workflow.dart)

- Remove hardcoded default `@Default("sys_e26807f3bfa3454d")` from `modelRegistryId`:
  ```dart
  @JsonKey(name: 'model_registry_id')
  String modelRegistryId,
  ```
- Regenerate Freezed and JSON serialization models via `flutter_audit_loop.py --build`.

#### [MODIFY] [model_registry_view.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/views/model_registry_view.dart)

- **Default Provider Dropdown (`_buildSystemAttributes`)**:
  - Replace the merged `"Google Vertex / AI Studio"` item with distinct choices:
    - `vertex_ai`: `l10n.platformVertexAi` ("Google Vertex AI (GCP)")
    - `ai_studio`: `l10n.platformAiStudio` ("Google AI Studio (Gemini API)")
    - `openai`: `l10n.platformOpenAi` ("OpenAI")
    - `anthropic`: `l10n.platformAnthropic` ("Anthropic (Direct)")
  - On provider change: update `defaultProvider`, synchronize `provider` on all 4 tiers, and update model names to the first available model discovered for the new platform.
  - **Dynamic Location Dropdown (Vertex AI Only)**:
    - If `data.defaultProvider == 'vertex_ai'`: fetch `ref.watch(supportedLocationsProvider)` and render the `Alue / Lokaatio` dropdown in `_buildSystemAttributes`.
    - Initial value defaults to first tier's `vertex_location` or `'europe-north1'`.
    - When changed: updates `vertex_location` in `additionalParams` across all tiers in the stack. This triggers `availableModelsProvider` to re-fetch models for the newly selected region.
    - If not `vertex_ai`: do not watch `supportedLocationsProvider`, and do not render the location field.

- **Dynamic Tier Cards (`_buildTierCardsSection`)**:
  - Remove redundant `Alusta` (`platformLabel`) dropdown from each tier card.
  - Remove duplicate tier-level location dropdown.
  - **Dynamic Model Name Dropdown (`Mallin nimi`)**:
    - Replace `TextFormField` with `DropdownButtonFormField<String>` (`isExpanded: true`).
    - Populate items dynamically from:
      `final modelsAsync = ref.watch(availableModelsProvider(platform: payload.defaultProvider, location: hasRegions ? activeLocation : null));`
      `final dynamicModels = modelsAsync.value ?? [];`
    - Items include all discovered models for that platform and region, plus the persisted `cfg.modelName` if present.
    - When changed, updates `cfg.modelName`.
  - Display loading indicator inside the dropdown while models are being fetched from the provider API.

#### [MODIFY] [app_en.arb](file:///c:/src/quorum/client_app_v2/lib/l10n/app_en.arb) & [app_fi.arb](file:///c:/src/quorum/client_app_v2/lib/l10n/app_fi.arb)

- Verify and maintain localized platform labels:
  - `platformVertexAi`: "Google Vertex AI (Enterprise)" / "Google Vertex AI (GCP)"
  - `platformAiStudio`: "Google AI Studio (Gemini Developer API)" / "Google AI Studio (Gemini API)"
  - `platformOpenAi`: "OpenAI" / "OpenAI"
  - `platformAnthropic`: "Anthropic (Direct)" / "Anthropic (Direct)"

---

### Backend (Python `backend_v2`)

#### [MODIFY] [enums.py](file:///c:/src/quorum/backend_v2/models/enums.py#L149-L156) & [enums.py](file:///c:/src/quorum/backend_v2/models/enums.py#L477-L486)

- Replace `GOOGLE = "google"` in `LLMProvider` and `LLMProviderName` with explicit sovereign members:
  - `VERTEX_AI = "vertex_ai"`
  - `AI_STUDIO = "ai_studio"`
  - `OPENAI = "openai"`
  - `ANTHROPIC = "anthropic"`
- Add explicit `GCPVertexDiscoveryRegion(StrEnum)`:
  ```python
  class GCPVertexDiscoveryRegion(StrEnum):
      """Authoritative Google Cloud Vertex AI central hub for Model Garden discovery."""

      US_CENTRAL1 = "us-central1"  # Council Bluffs, Iowa (Google AI Model Garden primary launch region)
  ```

#### [MODIFY] [enums.py](file:///c:/src/quorum/backend_v2/models/enums.py#L199-L203)

- Eradicate `MODEL_REGISTRY = "sys_e26807f3bfa3454d"` from `SystemConfigID`. Database document IDs belong strictly in persistent state, never hardcoded in Python enums.

#### [MODIFY] [settings.py](file:///c:/src/quorum/backend_v2/settings.py#L51-L818) & [settings.py](file:///c:/src/quorum/backend_v2/settings.py#L716-L741)

- Configure `google_api_key` in `Settings` with `validation_alias=AliasChoices("google_api_key", "gemini_api_key")` to reliably load `GEMINI_API_KEY` from `.env`.
- Default `discovery_location` to `GCPVertexDiscoveryRegion.US_CENTRAL1.value` (`"us-central1"`).
- In `Settings.enabled_providers` property, compute sovereign `"vertex_ai"` (when GCP ADC / service-account.json is present) and `"ai_studio"` (when google_api_key is present) separately. Eradicate legacy `"google"`.
- Add `pacing_delay_ai_studio_seconds: Annotated[int, Field(description="Forced delay between Google AI Studio requests")] = 0`.
- (Do NOT add `default_model_registry_id` — eradicated all magic defaults and fallback chains).

#### [MODIFY] [adapter_factory.py](file:///c:/src/quorum/backend_v2/llm/adapters/adapter_factory.py#L19-L155) & [adapter_factory.py](file:///c:/src/quorum/backend_v2/llm/adapters/adapter_factory.py#L27-L155)

- Eradicate `case LLMProviderName.GOOGLE | "google":` and the model name substring check (`"vertex_ai/" in model_name`).
- Support direct sovereign resolution: `case LLMProviderName.VERTEX_AI | "vertex_ai"` and `case LLMProviderName.AI_STUDIO | "ai_studio"`.

#### [MODIFY] [base_adapter.py](file:///c:/src/quorum/backend_v2/llm/adapters/base_adapter.py#L75-L136)

- In `apply_provider_pacing`:
  - Eradicate `LLMProviderName.GOOGLE.value` from pattern matching.
  - Route `case LLMProviderName.VERTEX_AI.value:` to `settings.pacing_delay_vertex_seconds`.
  - Route `case LLMProviderName.AI_STUDIO.value:` to `pacing_delay_ai_studio_seconds`.

#### [MODIFY] [handler.py](file:///c:/src/quorum/backend_v2/llm/handler.py#L92-L227), [handler.py](file:///c:/src/quorum/backend_v2/llm/handler.py#L229-L289), [handler.py](file:///c:/src/quorum/backend_v2/llm/handler.py#L300-L369), [handler.py](file:///c:/src/quorum/backend_v2/llm/handler.py#L371-L400), [handler.py](file:///c:/src/quorum/backend_v2/llm/handler.py#L402-L477) & [handler.py](file:///c:/src/quorum/backend_v2/llm/handler.py#L531-L655)

- In `_fetch_vertex_models` (`#L92-L227`): bind candidate gathering directly to "us-central1". Uses GCP ADC credentials (`service-account.json`). Replace magic timeout `timeout=5` with `DEFAULT_HTTP_TIMEOUT = 10`. Replace magic pool size `max_workers=20` with constant `MAX_DISCOVERY_CONCURRENCY = 20`.
- In `_fetch_ai_studio_models` (`#L229-L289`): read `settings.google_api_key` strictly from `.env` via `settings`. **Remove LiteLLM catalog fallback loop completely.**
- In `_fetch_openai_models` (`#L300-L369`): read `settings.openai_api_key` strictly from `.env` via `settings`.
- In `_fetch_anthropic_models` (`#L371-L400`): read `settings.anthropic_api_key` strictly from `.env` via `settings`.
- Clean up direct `os.environ.get("GEMINI_API_KEY")` and `os.environ.get("OPENAI_API_KEY")`. Rely strictly on typed `settings`.
- In `fetch_all_available_models` (`#L402-L477`):
  - Enforce `target_location` check ONLY when `norm_platform in [LLMPlatformType.VERTEX_AI.value, LLMPlatformType.ALL.value]` or `LLMPlatformType.VERTEX_AI.value in active_providers`. Do not raise `ValueError` for AI Studio, OpenAI, or Anthropic when location is unset.
  - Eradicate `models["google"] = ...` alias. Map 1:1 to requested platform (`vertex_ai`, `ai_studio`, `openai`, `anthropic`). Eradicate `_fetch_google_models`.
- In `create_provider_for_strategy` (`#L531-L655`):
  - Eradicate `startswith` string checks (`model_name.startswith("vertex_ai/")`, `model_name.startswith("gemini/")`).
  - Derive `platform` 100% from typed `provider`: `platform=LLMPlatformType.VERTEX_AI.value` if `provider == LLMProviderName.VERTEX_AI.value` else `LLMPlatformType.AI_STUDIO.value`.

#### [MODIFY] [provider.py](file:///c:/src/quorum/backend_v2/llm/provider.py#L1427-L1605) & [provider.py](file:///c:/src/quorum/backend_v2/llm/provider.py#L1430-L1605)

- In `LLMFactory.create_provider`:
  - **Eradicate `startswith` and substring inspections entirely**:
    - Delete `if provider_type == "anthropic" and not model_name.startswith("anthropic/"): ...`
    - Delete `if "gemini" in model_name: ...`
    - Delete `elif "gpt" in model_name or "o1" in model_name: ...`
    - Delete `elif "claude" in model_name or "anthropic" in model_name: ...`
    - Delete `"openai/" in model_name.lower()`
  - **Strict Typed Relation Invariant**:
    - Resolve provider strictly from typed `provider_type` (which originates from `config.provider` or the typed enum `LLMProvider`).
    - `case LLMProvider.VERTEX_AI | "vertex_ai":`
      `resolved_api_key = None` (Vertex AI authenticates via GCP Application Default Credentials backed by `service-account.json`).
    - `case LLMProvider.AI_STUDIO | "ai_studio":`
      `resolved_api_key = settings.google_api_key` (loaded strictly from `.env`). If missing or empty, immediately raise `ConfigurationError(message="Fail-Fast: GEMINI_API_KEY / GOOGLE_API_KEY is not configured in settings or environment.", details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})`.
    - `case LLMProvider.OPENAI | "openai":`
      `resolved_api_key = settings.openai_api_key` (loaded strictly from `.env`). If missing or empty, immediately raise `ConfigurationError(message="Fail-Fast: OPENAI_API_KEY is not configured in settings or environment.", details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})`.
    - `case LLMProvider.ANTHROPIC | "anthropic":`
      `resolved_api_key = settings.anthropic_api_key` (loaded strictly from `.env`). If missing or empty, immediately raise `ConfigurationError(message="Fail-Fast: ANTHROPIC_API_KEY is not configured in settings or environment.", details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})`.

#### [MODIFY] [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py#L464-L488) & [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py#L1379-L1545)

- Update `SystemConfigModelRegistry.default_provider`: change default from `LLMProvider.GOOGLE` to `LLMProvider.AI_STUDIO`.
- In `Workflow.model_registry_id`: remove hardcoded default `default="sys_e26807f3bfa3454d"`:
  ```python
  model_registry_id: str = Field(
      pattern=r"^(sys_[a-fA-F0-9]{16,32}|cfg_model_registry_\d{2})$",
      description="System config ID of the attached model registry",
  )
  ```

#### [MODIFY] [studio.py](file:///c:/src/quorum/backend_v2/models/dtos/studio.py#L99-L157)

- In `WorkflowCreateDTO.model_registry_id`: remove hardcoded default `"sys_e26807f3bfa3454d"`:
  ```python
  model_registry_id: Annotated[
      str | None, Field(default=None, description="Model registry system config ID")
  ] = None
  ```

#### [MODIFY] [workflow_service.py](file:///c:/src/quorum/backend_v2/services/studio/workflow_service.py#L281-L308)

- In `create_workflow_draft`:
  - Dynamically query active model registries from the database:
    ```python
    active_registries = await self.system_repo.get_all_model_registries()
    if not active_registries:
        logger.error("[WorkflowService] No active model registry found in database.")
        raise ResourceNotFoundError(resource_type="system_config", resource_id="model_registry")
    chosen_registry_id = active_registries[0].id
    ```
  - Bind `model_registry_id=chosen_registry_id` dynamically instead of hardcoding `"sys_e26807f3bfa3454d"`.

#### [MODIFY] [system_config_service.py](file:///c:/src/quorum/backend_v2/services/studio/system_config_service.py#L43-L91), [system_config_service.py](file:///c:/src/quorum/backend_v2/services/studio/system_config_service.py#L93-L145), [system_config_service.py](file:///c:/src/quorum/backend_v2/services/studio/system_config_service.py#L147-L189) & [system_config_service.py](file:///c:/src/quorum/backend_v2/services/studio/system_config_service.py#L276-L318)

- In `get_available_models` (`#L43-L91`): ensure clean handling of `platform` filtering.
- In `get_supported_locations` (`#L93-L145`): preserve and return supported GCP Vertex AI locations.
- In `get_supported_platforms` (`#L147-L189`): return distinct `vertex_ai` and `ai_studio` platforms.
- In `create_system_config_draft` (`#L276-L318`): set `default_provider=LLMProvider.AI_STUDIO` and tier profile provider `"ai_studio"`.

#### [MODIFY] [system.py](file:///c:/src/quorum/backend_v2/database/repositories/system.py#L31-L62), [system.py](file:///c:/src/quorum/backend_v2/database/repositories/system.py#L64-L75), [system.py](file:///c:/src/quorum/backend_v2/database/repositories/system.py#L77-L91) & [system.py](file:///c:/src/quorum/backend_v2/database/repositories/system.py#L129-L149)

- In `get_model_registry(self, registry_id: str)` (`#L31-L62`):
  - Require explicit `registry_id: str`. If missing, empty, or not found, raise `ResourceNotFoundError` immediately (Fail-Fast).
  - Delete fallback logic and delete sorting priority hacks.
- In `get_all_model_registries(self)` (`#L64-L75`):
  - Sort deterministically purely by `(m.name, m.id)`.
- In `update_model_registry` (`#L77-L91`):
  - Use `doc_id = registry_data.id` directly without fallback ID enums.
- Document and preserve singleton in-place upsert logic in `update_mcp_gateways` (`#L129-L149`) (`limit=1` -> `res_list[0]["id"]`).

#### [MODIFY] [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json)

- Ensure `seed_data.json` provides distinct model registry stacks:
  1. `sys_e26807f3bfa3454d`: "Google AI Studio Stack" (`default_provider: "ai_studio"`, tiers using `provider: "ai_studio"`, `model_name: "gemini/gemini-2.5-flash"`).
  2. `sys_b1c2d3e4f5a60718`: "Google Cloud Vertex AI Sovereign Stack" (`default_provider: "vertex_ai"`, tiers using `provider: "vertex_ai"`, `model_name: "vertex_ai/gemini-2.5-flash"`, `vertex_location: "europe-north1"`).
  3. `sys_6f8b1c4a2e0d49f1`: "OpenAI O-Series Stack" (`default_provider: "openai"`, tiers using `provider: "openai"`).

---

### Knowledge Items & As-Built Architecture Documentation

#### [MODIFY] [ki_provider_agnostic_caching.md](file:///c:/Users/risto/.gemini/antigravity-ide/knowledge/provider_agnostic_caching/artifacts/ki_provider_agnostic_caching.md)

- Update theoretical principles and invariant contracts:
  - Document sovereign decoupling of Google Vertex AI (`vertex_ai` via GCP ADC / `service-account.json`) and Google AI Studio (`ai_studio` via `.env` / `google_api_key`).
  - Document absolute eradication of merged `"google"` pseudo-provider from all enums, providers, and settings.
  - Document typed relation sovereignty (`provider_type: LLMProvider` / `config.provider`) and strict prohibition of `startswith` and substring parsing.
  - Document central Model Garden live discovery hub ("us-central1") with live regional validation against target locations.

#### [MODIFY] [ki_desktop_pro_tool_studio_ux.md](file:///c:/Users/risto/.gemini/antigravity-ide/knowledge/desktop_pro_tool_studio_ux/artifacts/ki_desktop_pro_tool_studio_ux.md)

- Update Model Registry Studio UX standards:
  - Document top-level `Oletustarjoaja` sovereign stack selection synchronizing the entire stack.
  - Document dynamic `DropdownButtonFormField<String>` for model selection populated directly from `availableModelsProvider`.
  - Document conditional `Alue / Lokaatio` dropdown rendered strictly for Vertex AI.
  - Document removal of redundant tier-level platform and location dropdowns.

#### [MODIFY] [01_system_context_and_invariants.md](file:///c:/src/quorum/docs/architecture/01_system_context_and_invariants.md)

- Execute `/tier7-describe-architecture` synchronization:
  - Document decoupled credential topology: GCP Application Default Credentials (`service-account.json`) for Vertex AI versus direct environment API keys for AI Studio, OpenAI, and Anthropic.
  - Document zero hardcoded database entity IDs in code and pure dynamic database-driven registry resolution.
  - Maintain strictly timeless present-tense narrative; enforce `timeless_as_built_mandate`.

#### [MODIFY] [03_cognitive_orchestration_engine.md](file:///c:/src/quorum/docs/architecture/03_cognitive_orchestration_engine.md)

- Execute `/tier7-describe-architecture` synchronization:
  - Document decoupled LLM provider factory architecture, cache adapter factory, and pacing synchronization.
  - Document live dynamic model discovery via central hub "us-central1" with regional validation.
  - Document dynamic workflow-to-model-registry binding.
  - Maintain strictly timeless present-tense narrative; enforce `timeless_as_built_mandate`.

---

## Tests & ISTQB Falsification Checklist

### Red-Team Falsification & Attack Scenarios

1. **Red-Team Attack 1: Regional Desynchronization & Model Garden Drift (Location Poisoning)**:
   - **Vulnerability**: Vertex AI candidate gathering discovers models from central Model Garden (`us-central1`), which may include preview models not launched in target GCP region (Hamina `europe-north1`). If candidates were returned without live regional validation, selecting them causes unhandled 404 errors during runtime execution.
   - **Mitigation & Proof Anchor**: `_fetch_vertex_models` executes parallel live validation via `ThreadPoolExecutor` against target region (`target_location`) using `modern_client.models.get` (for Google models) and publisher endpoints (for third-party models). If model is unavailable in selected target location, it is discarded immediately. If 0 models validate, `logger.error` logs regional void and raises `ServiceUnavailableError(ErrorCodes.MODEL_LIST_FAILED)`. Tested by `test_google_providers_separation.py::test_vertex_model_discovery_regional_validation`.

2. **Red-Team Attack 2: Credential Conflation & Silent Key Leakage across Decoupled Providers**:
   - **Vulnerability**: Legacy code grouped `case "gemini" | "vertex_ai": resolved_api_key = settings.google_api_key`, leaking direct API keys to Vertex AI, and inspected `model_name` strings to guess providers. If user configured `vertex_ai` without GCP ADC, system attempted to use `GEMINI_API_KEY`, causing credential leakage or cryptic 401 errors.
   - **Mitigation & Proof Anchor**: Strict typed relation isolation in `LLMFactory.create_provider`:
     - `case LLMProvider.VERTEX_AI | "vertex_ai": api_key = None` (GCP ADC only). If `service-account.json` and ADC env vars are missing, Vertex discovery and execution fail fast immediately with `ConfigurationError(ErrorCodes.AUTHENTICATION_FAILED)`.
     - `case LLMProvider.AI_STUDIO | "ai_studio": api_key = settings.google_api_key`. If missing, immediately raises `ConfigurationError(ErrorCodes.CONFIGURATION_ERROR)`.
     - String prefix guessing (`startswith`, `"gemini" in model_name`) is 100% eradicated. Tested by `test_google_providers_separation.py::test_create_provider_strict_credential_routing`.

3. **Red-Team Attack 3: Non-Vertex Location Starvation (Premature Validation Crash)**:
   - **Vulnerability**: In `handler.py`, `target_location` was checked unconditionally at entry point of `fetch_all_available_models`. When user queried AI Studio, OpenAI, or Anthropic on environment without `VERTEX_LOCATION` configured, entire query threw `ValueError` and crashed Studio Model Registry UI.
   - **Mitigation & Proof Anchor**: `target_location` validation is scoped strictly to Vertex AI queries (`norm_platform in [LLMPlatformType.VERTEX_AI.value, LLMPlatformType.ALL.value]` or `LLMPlatformType.VERTEX_AI.value in active_providers`). AI Studio, OpenAI, and Anthropic discovery proceed seamlessly without requiring GCP location. Tested by `test_google_providers_separation.py::test_non_vertex_discovery_without_location`.

#### [MODIFY] [model_registry_view_test.dart](file:///c:/src/quorum/client_app_v2/test/features/studio/views/model_registry_view_test.dart)

- Update widget tests:
  1. Verify `Mallin nimi` renders as dynamic dropdown populated from `availableModelsProvider`.
  2. Verify Location is queried and rendered **only** when `defaultProvider == 'vertex_ai'`.
  3. Verify switching Location re-queries `availableModelsProvider` with new region.
  4. Verify switching provider from `vertex_ai` to `ai_studio` hides Location and queries `availableModelsProvider(platform: 'ai_studio', location: null)`.
  5. **ISTQB Boundary Test 1 (Negative Partition)**: Verify that when `availableModelsProvider` returns an empty list or error, view displays inline warning without crashing Flutter form.
  6. **ISTQB Boundary Test 2 (Negative Partition)**: Verify that when switching to an unsupported provider, model name is cleanly reset or preserved in safe state.

#### [NEW] [test_google_providers_separation.py](file:///c:/src/quorum/backend_v2/tests/unit/llm/test_google_providers_separation.py)

- Unit test verifying:
  1. `LLMCacheAdapterFactory.get_adapter("vertex_ai")` returns `VertexCacheAdapter`.
  2. `LLMCacheAdapterFactory.get_adapter("ai_studio")` returns `GoogleAIStudioCacheAdapter`.
  3. `LLMCacheAdapterFactory.get_adapter("google")` raises `AppException` (ErrorCodes.VALIDATION_FAILED) - verifying absolute purge of umbrella pseudo-provider.
  4. `LLMFactory.create_provider` routes Vertex AI without API key (service-account.json) and AI Studio with `GEMINI_API_KEY` from `.env`, driven strictly by `provider_type` without `startswith` or substring guessing.
  5. Regional validation in `_fetch_vertex_models` correctly uses "us-central1" hub and queries target region.
  6. **ISTQB Boundary Test 1 (Negative Partition - Missing Key)**: AI Studio creation raises `ConfigurationError` when `google_api_key` / `GEMINI_API_KEY` is completely missing from `.env` / `settings`.
  7. **ISTQB Boundary Test 2 (Negative Partition - Missing GCP ADC)**: Querying Vertex AI discovery without valid GCP credentials / `service-account.json` raises `ConfigurationError(ErrorCodes.AUTHENTICATION_FAILED)`.
  8. **ISTQB Boundary Test 3 (Equivalence Partition - Independence)**: `Settings.enabled_providers` property computes sovereign `vertex_ai` and `ai_studio` independently without conflated `google`.
  9. **ISTQB Boundary Test 4 (Isolation Boundary - Location Independence)**: `fetch_all_available_models(platform="ai_studio", location=None)` succeeds and does not require `vertex_location` to be set in environment or settings.
  10. **ISTQB Boundary Test 5 (Anti-Heuristic Boundary)**: Model availability validation resolves platform strictly from `provider` without inspecting `model_name` string prefixes.

#### [MODIFY] 1-Hop Caller Unit Tests Harmonization:
- `@[backend_v2/tests/unit/llm/adapters/test_adapter_factory.py#L35-L47]`: Purge `GOOGLE` tests; assert sovereign `VERTEX_AI` and `AI_STUDIO` resolution.
- `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py#L24-L32]`: Update provider binding to `LLMProvider.AI_STUDIO`, assert `client.provider_name == "ai_studio"`.
- `@[backend_v2/tests/unit/database/repositories/test_system_model_registry.py#L50-L62]`: Update test registry fixtures and assertions to `LLMProvider.AI_STUDIO`. Verify `get_model_registry(registry_id)` fails fast on missing or non-existent ID, and `get_all_model_registries` sorts deterministically by `(m.name, m.id)`.
- `@[backend_v2/tests/unit/services/studio/test_workflow_service.py#L282-L304]`: Update `create_workflow_draft` tests to assert dynamic binding of first active model registry from database.
- `@[backend_v2/tests/unit/services/studio/test_system_config_service.py#L210-L222]`: Update `_make_dummy_registry` default to `LLMProvider.AI_STUDIO`.
- `@[backend_v2/tests/unit/database/repositories/test_system.py#L20-L35]`: Update sample model registry fixture default to `LLMProvider.AI_STUDIO`.
- `@[backend_v2/tests/unit/database/test_repository.py#L136-L302]`: Update dummy registry fixture default to `LLMProvider.AI_STUDIO`.
- `@[backend_v2/tests/fakes/in_memory_repositories.py#L248-L375]`: Update default in-memory registry default to `LLMProvider.AI_STUDIO`.
- `@[backend_v2/tests/unit/test_model_registry.py#L24-L39]`: Update `_make_dummy_registry` fixture from `provider="google"` to `provider="ai_studio"`.
- `@[backend_v2/tests/unit/test_model_registry_discovery.py#L36-L273]`: Update `ModelProfile` fixtures from `provider="google"` to `provider="vertex_ai"` or `provider="ai_studio"`.
- `@[backend_v2/tests/unit/models/test_v2_core.py#L931-L969]`: Update `dummy_profile` fixture from `provider="google"` to `provider="ai_studio"`. Update workflow model tests to provide explicit `model_registry_id`.
- `@[backend_v2/tests/unit/models/dtos/test_system.py#L37-L110]`: Update `dummy_profile` fixture from `provider="google"` to `provider="ai_studio"`.
- `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L161-L185]`: Synchronize `ModelProfile` fixture from `provider="google"` to `provider="ai_studio"`.

---

## Canonical Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="PRE_IMPLEMENTATION_TECHNICAL_DEBT_CLEANUP">
    <action>Audit and clean up legacy anti-patterns in handler.py, provider.py, and base_adapter.py before introducing functional decoupling.</action>
    <action>Remove ad-hoc os.environ.get calls and replace with typed Settings references.</action>
    <action>Delete LiteLLM catalog fallback loop in _fetch_ai_studio_models.</action>
    <action>Delete heuristic startswith and substring matching blocks in create_provider.</action>
    <action>Scope target_location requirement in fetch_all_available_models strictly to Vertex AI platform queries.</action>
    <action>Replace magic timeout and pool numbers in handler.py with explicit constants DEFAULT_HTTP_TIMEOUT and MAX_DISCOVERY_CONCURRENCY.</action>
    <constraint invariant="zero_backward_compatibility_planning_ban">Ban fallback chains, legacy aliases, and catalog guessing.</constraint>
    <constraint invariant="ban_heuristic_identifier_matching">Ban startswith and substring checks for provider resolution.</constraint>
  </step>

  <step id="2" name="ENUMS_MODERNIZATION_AND_DOCUMENT_ID_PURGE">
    <action>Update LLMProvider and LLMProviderName in backend_v2/models/enums.py: eradicate GOOGLE = 'google', add explicit VERTEX_AI = 'vertex_ai' and AI_STUDIO = 'ai_studio'.</action>
    <action>Add GCPVertexDiscoveryRegion(StrEnum) with US_CENTRAL1 = 'us-central1'.</action>
    <action>Eradicate SystemConfigID.MODEL_REGISTRY from backend_v2/models/enums.py.</action>
    <constraint invariant="anti_semantic_drift_renaming">Enums represent permanent SSOT contracts.</constraint>
  </step>

  <step id="3" name="SETTINGS_AND_CREDENTIAL_DECOUPLING">
    <action>Update backend_v2/settings.py: ensure google_api_key uses AliasChoices('google_api_key', 'gemini_api_key').</action>
    <action>Set discovery_location default to 'us-central1'.</action>
    <action>Update Settings.enabled_providers property to calculate vertex_ai and ai_studio independently.</action>
    <action>Add pacing_delay_ai_studio_seconds to Settings.</action>
    <constraint invariant="credential_hardcoding_ban">Credentials resolved strictly via environment injection or GCP ADC.</constraint>
  </step>

  <step id="4" name="PROVIDER_FACTORY_AND_ADAPTER_SOVEREIGNTY">
    <action>Refactor LLMFactory.create_provider in backend_v2/llm/provider.py to resolve credentials and provider instances strictly by typed provider_type.</action>
    <action>Update LLMCacheAdapterFactory in backend_v2/llm/adapters/adapter_factory.py: remove GOOGLE case and model_name substring checks; add 1:1 match cases for VERTEX_AI and AI_STUDIO.</action>
    <action>Update apply_provider_pacing in backend_v2/llm/adapters/base_adapter.py to handle VERTEX_AI and AI_STUDIO independently.</action>
    <constraint invariant="single_pipeline_invariant_mandate">All execution paths flow through one deterministic typed pipeline.</constraint>
  </step>

  <step id="5" name="LIVE_MODEL_DISCOVERY_AND_VALIDATION_IN_HANDLER">
    <action>Refactor _fetch_vertex_models in backend_v2/llm/handler.py to discover candidates via US_CENTRAL1 and validate live in target_location.</action>
    <action>Refactor _fetch_ai_studio_models to query genai.Client with google_api_key without LiteLLM fallback.</action>
    <action>Refactor fetch_all_available_models to require target_location only for Vertex AI.</action>
    <action>Refactor create_provider_for_strategy to derive platform directly from typed provider.</action>
    <constraint invariant="universal_fail_fast">Fail-Fast if upstream provider API fails or credentials missing.</constraint>
  </step>

  <step id="6" name="DYNAMIC_DATABASE_MODEL_REGISTRY_REPOSITORY">
    <action>Refactor get_model_registry in backend_v2/database/repositories/system.py to require non-empty registry_id and raise ResourceNotFoundError if not found.</action>
    <action>Refactor get_all_model_registries to sort deterministically by (m.name, m.id).</action>
    <action>Update update_model_registry to use registry_data.id directly without fallback constants.</action>
    <action>Preserve singleton in-place upsert in update_mcp_gateways.</action>
    <constraint invariant="database_schema_hallucination">Database entities resolved dynamically from persistence layer.</constraint>
  </step>

  <step id="7" name="WORKFLOW_AND_STUDIO_SERVICE_REGISTRY_BINDING">
    <action>Remove default='sys_e26807f3bfa3454d' from Workflow.model_registry_id in backend_v2/models/v2_core.py.</action>
    <action>Remove default='sys_e26807f3bfa3454d' from WorkflowCreateDTO.model_registry_id in backend_v2/models/dtos/studio.py.</action>
    <action>Update create_workflow_draft in backend_v2/services/studio/workflow_service.py to query active model registries dynamically and bind the first active registry ID.</action>
    <action>Update create_system_config_draft in backend_v2/services/studio/system_config_service.py to use AI_STUDIO as default provider.</action>
    <action>Synchronize backend_v2/seed/seed_data.json with decoupled stacks.</action>
    <constraint invariant="studio_driven_parameterization_mandate">Pipelines driven 100% by dynamic Studio UI configurations.</constraint>
  </step>

  <step id="8" name="FLUTTER_FREEZED_MODEL_AND_LOCALIZATION_PARITY">
    <action>Update ModelConfig default provider in client_app_v2/lib/features/studio/models/model_config.dart to 'ai_studio'.</action>
    <action>Remove hardcoded default from modelRegistryId in client_app_v2/lib/features/studio/models/workflow.dart.</action>
    <action>Verify localization keys in client_app_v2/lib/l10n/app_en.arb and app_fi.arb.</action>
    <action>Run flutter_audit_loop.py with --build to regenerate Freezed and JSON models.</action>
    <constraint invariant="sdui_contract_fracture_prevention">Enforce 1:1 cross-domain serialization parity.</constraint>
  </step>

  <step id="9" name="QUORUM_STUDIO_MODEL_REGISTRY_VIEW_MODERNIZATION">
    <action>Refactor _buildSystemAttributes in client_app_v2/lib/features/studio/views/model_registry_view.dart: render decoupled default provider dropdown.</action>
    <action>Render Alue / Lokaatio dropdown conditionally only when defaultProvider == 'vertex_ai'.</action>
    <action>Refactor _buildTierCardsSection: remove redundant tier-level platform and location dropdowns; implement dynamic DropdownButtonFormField for model selection backed by availableModelsProvider.</action>
    <constraint invariant="desktop_pro_tool_studio_ux">Follow desktop-class Pro Tool UX standards with instant reactive feedback.</constraint>
  </step>

  <step id="10" name="UNIT_TEST_SUITE_AND_FIXTURE_HARMONIZATION">
    <action>Create backend_v2/tests/unit/llm/test_google_providers_separation.py covering all ISTQB positive, negative, and isolation partitions.</action>
    <action>Synchronize 1-hop caller test fixtures across test_adapter_factory.py, test_llm_client_tiers.py, test_system_model_registry.py, test_workflow_service.py, test_system_config_service.py, test_system.py, test_repository.py, in_memory_repositories.py, test_model_registry.py, test_model_registry_discovery.py, test_v2_core.py, test_system dtos, and test_ai_studio_adapter.py.</action>
    <action>Execute backend_audit_loop.py across all touched backend targets.</action>
    <constraint invariant="zero_tolerance_audit_loop">Run automated audit loop verifying Ruff, MyPy, and Pytest.</constraint>
  </step>

  <step id="11" name="FLUTTER_WIDGET_TESTING_AND_AUDIT">
    <action>Update client_app_v2/test/features/studio/views/model_registry_view_test.dart covering dynamic model dropdown, conditional location rendering, and negative boundary error handling.</action>
    <action>Execute flutter_audit_loop.py across all touched Flutter targets.</action>
    <constraint invariant="zero_tolerance_audit_loop">Enforce strict Flutter format, analyze, and test verification.</constraint>
  </step>

  <step id="12" name="SINGLE_RUN_E2E_VARIANCE_VERIFICATION">
    <action>Execute single-run live variance test verifying end-to-end execution with decoupled Vertex AI model registry stack.</action>
    <constraint invariant="ai_testing_standards">FinOps strictly gated: maximum 1 live execution run.</constraint>
  </step>

  <step id="13" name="KNOWLEDGE_ITEM_SYNCHRONIZATION">
    <action>Update ki_provider_agnostic_caching.md: document sovereign Google Vertex AI and Google AI Studio decoupling, typed relation invariants, live model discovery hub, and fail-fast credential contracts.</action>
    <action>Update ki_desktop_pro_tool_studio_ux.md: document Quorum Studio Model Registry UX standards, top-level sovereign provider synchronization, dynamic model dropdowns from availableModelsProvider, and conditional location dropdown strictly for Vertex AI.</action>
    <constraint invariant="knowledge_base_mandate">Synchronize authoritative Knowledge Items to preserve architectural Single Source of Truth.</constraint>
  </step>

  <step id="14" name="AS_BUILT_ARCHITECTURE_DOCUMENTATION_SYNCHRONIZATION">
    <action>Execute /tier7-describe-architecture workflow for docs/architecture/01_system_context_and_invariants.md to reflect decoupled credentials injection and dynamic database-driven registry resolution.</action>
    <action>Execute /tier7-describe-architecture workflow for docs/architecture/03_cognitive_orchestration_engine.md to reflect decoupled provider factory, adapter sovereignty, and live model discovery topology.</action>
    <action>Synchronize .agents/rules/04_directory_reference.md if any component cluster boundaries shifted.</action>
    <constraint invariant="timeless_as_built_mandate">Describe purely and timelessly what the system currently has in present tense; ban project phases, dates, historical comparisons, and artificial Law labels.</constraint>
    <constraint invariant="dual_axis_documentation_mandate">Route human-facing documentation updates strictly through tier7 workflow.</constraint>
  </step>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
1. Backend audit & unit tests:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/llm/test_google_providers_separation.py --test
   uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/database/repositories/test_system.py --test
   uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/llm/test_llm_client_tiers.py --test
   uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/llm/adapters/test_adapter_factory.py --test
   ```
2. Frontend audit & widget tests:
   ```powershell
   flutter test test/features/studio/views/model_registry_view_test.dart
   uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/model_registry_view.dart --build
   ```
3. Single-Run E2E Pipeline Smoke Test (FinOps Strictly Gated: Max 1 Run across entire plan):
   ```powershell
   uv run python scripts/run_e2e_variance_test.py inputs/ --num-runs 1 --dev --model-registry sys_b1c2d3e4f5a60718
   ```
4. As-Built Architecture & Knowledge Item Verification:
   - Verify `ki_provider_agnostic_caching.md` and `ki_desktop_pro_tool_studio_ux.md` reflect current decoupled architecture.
   - Run `/tier7-describe-architecture` for `docs/architecture/01_system_context_and_invariants.md` and `docs/architecture/03_cognitive_orchestration_engine.md`.
   - Verify all modified architecture documents adhere strictly to present-tense timelessness (zero "Phase X", zero historical comparisons, zero artificial Law labels).

### Manual Verification
- In Quorum Studio UI -> `Mallirekisteri`:
  - Open stack configured with `Google Vertex AI (GCP)`:
    - Verify location dropdown is visible and lists supported GCP regions (specifically `europe-north1` Hamina).
    - Verify `Mallin nimi` dropdown queries and displays active Vertex models for selected region using `service-account.json` credentials.
    - Switch region: verify model list updates dynamically for newly selected region.
  - Switch `Oletustarjoaja` -> `Google AI Studio (Gemini API)`:
    - Verify location dropdown is hidden.
    - Verify `Mallin nimi` dropdown queries global Gemini models via `.env` API key.
