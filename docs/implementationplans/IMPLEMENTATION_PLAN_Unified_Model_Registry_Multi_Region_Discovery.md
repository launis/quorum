> **STATUS: COMPLETED / TOTEUTETTU (100% Implemented & Verified)**

# IMPLEMENTATION PLAN: Unified Model Registry Platform & Multi-Region Discovery

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

## 1. Executive Summary & Objective

### Objective
Provide a unified, highly intuitive Model Registry interface and robust backend discovery engine in Quorum:
1. **Google AI Studio (Direct Gemini API)**: Support fetching and running Google models directly via `GOOGLE_API_KEY` / `GEMINI_API_KEY` without requiring GCP service accounts, project IDs, or regional constraints.
2. **Google Vertex AI Multi-Region**: Allow selecting target GCP regions (specifically: `europe-north1` [Hamina, FI], `europe-west1` [Belgium], `europe-west4` [Netherlands], `europe-west3` [Frankfurt], `us-central1` [Iowa], `us-east4` [Virginia]) dynamically from the UI, executing existing parallel validation in the chosen region.
3. **Unified Platform & Location UI in `ModelRegistryView`**: Provide a clean selector for Platform (`Google Vertex AI`, `Google AI Studio`, `OpenAI`, `Anthropic`). When `Google Vertex AI` is chosen, present the Location dropdown. Dynamically fetch and populate available models based on the selected platform and location.
4. **Zero-Fallback Caching and Rate Pacing Integration**: Ensure that strategies configured with AI Studio (`google`) or Vertex AI (`vertex_ai`) route to appropriate caching adapters (`LLMCacheAdapterFactory`), rate limiters, and pricing models without runtime ambiguity.

---

## 2. Tri-Axis Dialectical Audit & Root Cause Analysis

### Root Cause Analysis
- **Root Cause**: Historically, model discovery in `LLMHandler` was coupled strictly to GCP service account authentication and the single `settings.vertex_location`. Users wanting to evaluate Gemini models via direct API keys (Google AI Studio) or test deployment availability across alternative European/US GCP regions were blocked by hardcoded region lookups and missing dual-path platform filtering.
- **Architectural Justification**: Decoupling platform selection (`LLMPlatformType`) and regional targeting (`GCPVertexLocation`) in `LLMHandler` while maintaining strict Pydantic DTOs and Riverpod provider families guarantees 100% Fail-Fast deterministic routing across Enterprise (Vertex) and Developer (AI Studio) pipelines.

### Tri-Axis Dialectical Audit
1. **PROSECUTION (Over-Engineering & YAGNI Advocate)**:
   - *Attack*: Why introduce a dedicated `/locations` endpoint and family-based Riverpod providers instead of just hardcoding region strings in the Flutter UI?
   - *Mandatory Deletion Test*: If `/locations` endpoint were cut, Flutter would rely on client-side hardcoded strings. If GCP adds a region, client and backend drift immediately. Centralizing `GCPVertexLocation` in backend `enums.py` and exposing `GET studio/model-registry/locations` guarantees backend SSOT authority.
2. **DEFENSE (Architectural Sovereignty & Fail-Fast Advocate)**:
   - *Defense*: Strict separation of `LLMPlatformType` (`vertex_ai`, `ai_studio`, `openai`, `anthropic`) and `GCPVertexLocation` prevents string mismatches, ensures Pydantic validation on query parameters, and avoids the catastrophic "e.g." ban in configuration models.
3. **REALIST (Duct-Tape & Blast Radius Interrogator)**:
   - *Blast Radius*: We must verify `LLMFactory.create_provider` and `VertexCacheAdapter` so that setting `vertex_location` dynamically in strategy `additional_params` doesn't collide with `settings.vertex_location`. In `handler.py`, the regional model existence check must inspect the target location configured in `additional_params['vertex_location']` rather than blindly asserting against `settings.vertex_location`.
4. **BINDING VERDICT**:
   - Approved Best Practice: Dynamic region & platform filtering with strict backend SSOT enums and Riverpod family invalidation. Pre-requisite technical debt in `handler.py` (legacy hardcoded checks) must be cleaned up in Phase 1.

---

## 3. Touched Scope & Bounded Files

### TARGET Files
- `[MODIFY]` @[backend_v2/models/enums.py#L442-L451]
- `[MODIFY]` @[backend_v2/models/dtos/studio.py]
- `[MODIFY]` @[backend_v2/llm/handler.py#L35-L613]
- `[MODIFY]` @[backend_v2/api/routers/studio/model_registry.py#L21-L44]
- `[MODIFY]` @[backend_v2/services/studio/system_config_service.py#L23-L481]
- `[MODIFY]` @[client_app_v2/lib/core/api/studio_client.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/controllers/model_registry_controller.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/model_registry_view.dart]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_en.arb]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_fi.arb]
- `[NEW]` @[backend_v2/tests/unit/test_model_registry_discovery.py]

### CONTEXT Files (Read-Only)
- `[READ]` @[backend_v2/settings.py#L51-L746]
- `[READ]` @[backend_v2/llm/provider.py#L1219-L1383]
- `[READ]` @[backend_v2/models/v2_core.py#L380-L390]
- `[READ]` @[client_app_v2/lib/features/studio/models/model_config.dart]

---

## 4. Detailed Execution Plan

```xml
<execution_protocol version="1.0">
  <metadata>
    <task_id>unified_model_registry_discovery</task_id>
    <title>Unified Model Registry Platform & Multi-Region Discovery</title>
  </metadata>

  <phase id="1" name="BACKEND ENUMS, DUAL-PATH DISCOVERY & API PARAMETERIZATION">
    <step id="1.0" name="Pre-Implementation Technical Debt Cleanups in LLMHandler">
      <action>
        In `backend_v2/llm/handler.py`:
        1. Refactor lines 438-461: Replace the rigid check `model_name not in valid_models` against `settings.vertex_location` with dynamic location resolution from `cd.get("additional_params", {}).get("vertex_location") or cd.get("vertex_location") or settings.vertex_location`.
        2. Remove any remaining raw string conversions or loose dictionary access.
      </action>
      <constraint invariant="the_duct_tape_ban">No silent fallbacks; exact root cause resolution for regional validation.</constraint>
    </step>

    <step id="1.1" name="Define GCP Region SSOT Enum and Platform Types in enums.py">
      <action>
        Add `GCPVertexLocation(StrEnum)` in `backend_v2/models/enums.py` with supported regions:
        - `EUROPE_NORTH1 = "europe-north1"` (Hamina, Finland)
        - `EUROPE_WEST1 = "europe-west1"` (Belgium)
        - `EUROPE_WEST4 = "europe-west4"` (Netherlands)
        - `EUROPE_WEST3 = "europe-west3"` (Frankfurt)
        - `US_CENTRAL1 = "us-central1"` (Iowa)
        - `US_EAST4 = "us-east4"` (Virginia)
        Add `LLMPlatformType(StrEnum)`:
        - `VERTEX_AI = "vertex_ai"`
        - `AI_STUDIO = "ai_studio"`
        - `OPENAI = "openai"`
        - `ANTHROPIC = "anthropic"`
        - `ALL = "all"`
        Add DTO in `backend_v2/models/dtos/studio.py`:
        `GCPLocationDTO(BaseModel)` with `id: str`, `label: str`, `description: str`.
      </action>
      <constraint invariant="strict_configuration_segregation">Centralize taxonomy in enums.py with zero magic strings.</constraint>
    </step>

    <step id="1.2" name="Refactor LLMHandler for Vertex AI and Google AI Studio Discovery">
      <action>
        In `backend_v2/llm/handler.py`:
        1. Split Google discovery into two dedicated private helpers:
           - `_fetch_vertex_models(target_location: str)`: Validates LiteLLM candidates in `target_location` via `genai.Client(vertexai=True, location=target_location)` and Model Garden publisher URLs.
           - `_fetch_ai_studio_models()`: Validates models using `settings.google_api_key` or `os.environ.get("GEMINI_API_KEY")` via `genai.Client(api_key=...)` or LiteLLM Gemini list. Prefixed as `gemini/` or `google/`.
        2. In `fetch_all_available_models(providers, location, platform)`:
           - If `platform == LLMPlatformType.VERTEX_AI` or `"vertex_ai"`, query `_fetch_vertex_models(location)`.
           - If `platform == LLMPlatformType.AI_STUDIO` or `"ai_studio"`, query `_fetch_ai_studio_models()`.
           - If `platform == LLMPlatformType.OPENAI` or `"openai"`, query `_fetch_openai_models()`.
           - If `platform == LLMPlatformType.ANTHROPIC` or `"anthropic"`, query `_fetch_anthropic_models()`.
           - If `platform == LLMPlatformType.ALL` or unspecified, aggregate enabled providers according to configured credentials.
      </action>
      <constraint invariant="the_duct_tape_ban">No silent fallbacks; log explicit error codes on missing credentials.</constraint>
    </step>

    <step id="1.3" name="Parameterize Router and Service Endpoints">
      <action>
        1. In `backend_v2/api/routers/studio/model_registry.py`:
           - Update `GET /available-models` to accept query params:
             `platform: LLMPlatformType = Query(default=LLMPlatformType.ALL)`
             `location: str | None = Query(default=None)`
           - Add `GET /locations`, response_model=`list[GCPLocationDTO]` returning list of supported GCP regions.
        2. In `backend_v2/services/studio/system_config_service.py`:
           - Update `get_available_models(initiator, llm_handler, platform, location)` to forward parameters to `llm_handler.fetch_all_available_models()`.
           - Add `get_supported_locations(initiator)` returning `list[GCPLocationDTO]`.
      </action>
      <constraint invariant="anemic_routers">Routers only validate HTTP inputs and delegate to Service layer.</constraint>
    </step>
  </phase>

  <phase id="2" name="FRONTEND CLIENT, RIVERPOD STATE & UNIFIED MODEL REGISTRY VIEW">
    <step id="2.1" name="Update StudioClient and Controller Providers with Riverpod Families">
      <action>
        1. In `client_app_v2/lib/core/api/studio_client.dart`:
           - Update `getAvailableModels({String? platform, String? location})` passing query parameters `platform` and `location`.
           - Add `getSupportedLocations()` calling `GET studio/model-registry/locations`.
        2. In `client_app_v2/lib/features/studio/controllers/model_registry_controller.dart`:
           - Convert `availableModelsProvider` to family:
             `@riverpod Future<List<String>> availableModels(Ref ref, {String? platform, String? location})`
           - Add `@riverpod Future<List<Map<String, dynamic>>> supportedLocations(Ref ref)`.
      </action>
      <constraint invariant="desktop_memory_leak_prevention">Use standard autoDispose Riverpod providers.</constraint>
    </step>

    <step id="2.2" name="Add Localization Strings in app_en.arb and app_fi.arb">
      <action>
        Add keys in `app_en.arb` and `app_fi.arb`:
        - `platformLabel`: "Platform" / "Alusta"
        - `locationLabel`: "Location / Region" / "Alue / Lokaatio"
        - `platformVertexAi`: "Google Vertex AI (Enterprise)" / "Google Vertex AI (GCP)"
        - `platformAiStudio`: "Google AI Studio (Gemini Developer API)" / "Google AI Studio (Gemini API)"
        - `platformOpenAi`: "OpenAI" / "OpenAI"
        - `platformAnthropic`: "Anthropic (Direct)" / "Anthropic (Direct)"
      </action>
      <constraint invariant="no_magic_strings_l10n">All UI labels must be localized in .arb files.</constraint>
    </step>

    <step id="2.3" name="Refactor ModelRegistryView with Unified Platform & Location Selectors">
      <action>
        In `client_app_v2/lib/features/studio/views/model_registry_view.dart`:
        1. In the strategy configuration card, determine the initial platform:
           - If `cfg.provider == "google"` and `cfg.modelName.startsWith("vertex_ai/")` -> `vertex_ai`
           - If `cfg.modelName.startsWith("gemini/")` or `cfg.provider == "ai_studio"` -> `ai_studio`
           - If `cfg.provider == "openai"` -> `openai`
           - If `cfg.provider == "anthropic"` -> `anthropic`
        2. Add **Platform Selector Dropdown**:
           - Wrapped in `LayoutBuilder` / `Expanded(isExpanded: true)`.
           - On change: updates `provider` and triggers refetch of `availableModelsProvider` with new platform.
        3. Add **Location Dropdown** (shown when platform == `vertex_ai`):
           - Populated from `supportedLocationsProvider`.
           - Default: `europe-north1` (or existing `cfg.additionalParams['vertex_location']`).
           - On change: re-triggers `availableModelsProvider` with the selected region and updates `cfg.additionalParams['vertex_location']`.
        4. **Model Name Dropdown**:
           - Watches `availableModelsProvider(platform: currentPlatform, location: currentLocation)`.
           - Displays the validated candidates with `isExpanded: true`.
      </action>
      <constraint invariant="horizontal_overflow_prevention">All dropdowns must have isExpanded: true and be wrapped in layout containers.</constraint>
    </step>
  </phase>

  <phase id="3" name="VERIFICATION & QUALITY GATES">
    <step id="3.1" name="Unit & Negative ISTQB Tests for Model Discovery">
      <action>
        In `backend_v2/tests/unit/test_model_registry_discovery.py`:
        1. Positive Partition: Test `_fetch_vertex_models` with mock responses for `europe-north1`, `europe-west1`, and `us-central1`.
        2. Positive Partition: Test `_fetch_ai_studio_models` with `google_api_key`.
        3. Routing Partition: Test query parameter filtering (`platform=vertex_ai&location=europe-west1`, `platform=ai_studio`) through `GET /available-models`.
        4. Negative Boundary 1: Missing API key returns `SERVICE_DEPENDENCY_MISSING` / `ConfigurationError`.
        5. Negative Boundary 2: Unsupported region or invalid platform throws 422 Unprocessable Entity via Pydantic validation.
      </action>
      <constraint invariant="anti_happy_path_mandate">Enforce minimum 2 negative boundary test cases per feature path.</constraint>
    </step>

    <step id="3.2" name="Execute Universal Quality Gates">
      <action>
        1. Run Backend Quality Gate:
           `uv run python scripts/backend_audit_loop.py backend_v2 --test`
        2. Run Flutter Localization Generator:
           `flutter gen-l10n` in `client_app_v2/`
        3. Run Frontend Quality Gate:
           `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/model_registry_view.dart --build`
      </action>
      <constraint invariant="quality_gate_execution">Audit loops must pass with zero lint errors and zero type warnings.</constraint>
    </step>
  </phase>
</execution_protocol>
```

---

## 5. Verification Plan

### Automated Tests
- `uv run pytest backend_v2/tests/unit/test_model_registry_discovery.py`
- `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build`

### Manual Verification
- Open Admin Studio -> Model Registry in the Flutter UI (`ModelRegistryView`).
- Select `Google Vertex AI` -> verify that Location dropdown appears (Hamina, Belgium, Netherlands, etc.) and models are prefixed with `vertex_ai/`.
- Switch to `Google AI Studio` -> verify that Location dropdown disappears and models are listed as `gemini/...`.
- Select `OpenAI` -> verify models list shows GPT models.
- Save a strategy and verify that it persists and executes properly.

# Session Handover Context
- achieved:
  - Implemented Unified Model Registry Discovery engine with dual-path Google AI Studio (`gemini/...`) and Vertex AI multi-region (`vertex_ai/...`) support.
  - Added dynamic location filtering across 6 GCP regions (`europe-north1`, `europe-west1`, `europe-west4`, `europe-west3`, `us-central1`, `us-east4`) in `LLMHandler`, `StudioSystemConfigService`, and `ModelRegistryView`.
  - Added UI platform selector and dynamic location dropdowns with complete English & Finnish localization (`app_en.arb`, `app_fi.arb`).
  - Passed Universal Quality Gate with 100% pass rate across backend and Flutter audit loops.
- learned:
  - Decoupling platform selection (`LLMPlatformType`) from region resolution guarantees clean Zero-Fallback routing and deterministic caching in `LLMCacheAdapterFactory`.
- remaining:
  - Plan successfully executed, verified, and certified.
