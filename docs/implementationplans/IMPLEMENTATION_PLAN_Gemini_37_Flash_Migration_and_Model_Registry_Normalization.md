# Implementation Plan: Gemini 3.7 Flash Migration & Multi-Provider Parameter Normalization

Migrate all Quorum Model Registry strategies (`fast`, `strict`, `deep`, `reasoning`, `synthesis`) in `seed_data.json` to **Gemini 3.7 Flash**, implement defensive parameter sanitization and `thinking_budget_tokens` normalization in the Backend Adapter layer across all providers (Google AI Studio, Vertex AI, Anthropic, OpenAI), and update the Flutter Admin Studio UI with a dedicated Thinking Budget control and explanatory parameter notices.

## User Review Required
> [!IMPORTANT]
> - **Platform Model Naming Convention (LiteLLM Prefixes):**
>   - **Google AI Studio (Direct Gemini API / `GEMINI_API_KEY`):** `gemini/gemini-3.7-flash`
>   - **Google Cloud Vertex AI (GCP / `VERTEX_LOCATION`):** `vertex_ai/gemini-3.7-flash`
> - `seed_data.json` will be updated with the explicit platform prefix (`vertex_ai/gemini-3.7-flash` as default for Vertex deployment or `gemini/gemini-3.7-flash` for direct AI Studio), with `temperature: 1.0` and role-differentiated `thinking_budget_tokens` (`fast`: 0, `strict`: 0, `synthesis`: 2048, `deep`: 4096, `reasoning`: 8192).
> - As requested, the Flutter UI (`ModelRegistryView`) will continue to render all parameter inputs normally, but will include inline warning/help notices informing the admin that legacy sampling parameters (`top_p`, `top_k`, penalties, `temperature < 1.0`) are not utilized or are overridden/deprecated for modern reasoning models.

## Proposed Changes

### Layer 1: Domain Models & Schema Parity
#### [MODIFY] [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py#L351-L379)
- Add optional `thinking_budget_tokens: int | None = Field(default=None, description="Reasoning/thinking token budget")` to `ModelProfile`.
- Ensure all sampling fields (`temperature`, `top_p`, `top_k`, `frequency_penalty`, `presence_penalty`) remain nullable/permissive so they can coexist without schema breakage.

#### [MODIFY] [model_config.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/models/model_config.dart#L24-L51)
- Add `@JsonKey(name: 'thinking_budget_tokens') int? thinkingBudgetTokens` to Dart Freezed model `LlmModelConfig`.

---

### Layer 2: LLM Provider Adapters (Backend Sanitization & Normalization)
#### [MODIFY] [base_adapter.py](file:///c:/src/quorum/backend_v2/llm/adapters/base_adapter.py#L244-L268)
- Define base protocol helper `sanitize_sampling_parameters(call_kwargs: dict[str, Any], model_name: str) -> dict[str, Any]` for defensive stripping of unsupported parameters.

#### [MODIFY] [vertex_adapter.py](file:///c:/src/quorum/backend_v2/llm/adapters/vertex_adapter.py#L381-L456)
- In `prepare_kwargs`:
  - Eradicate untyped dictionary lookups (`config.additional_params.get("thinking_budget_tokens")`) and access typed `config.thinking_budget_tokens`.
  - When `gemini-3*` is detected:
    - Map `thinking_budget_tokens` to `generationConfig.thinkingConfig.thinkingBudget`.
    - Enforce `temperature = 1.0` if `temperature < 1.0` was passed (logging a warning to prevent infinite thought loops).
    - Strip deprecated parameters (`top_k`, `frequency_penalty`, `presence_penalty`).

#### [MODIFY] [ai_studio_adapter.py](file:///c:/src/quorum/backend_v2/llm/adapters/ai_studio_adapter.py#L339-L382)
- In `prepare_kwargs`:
  - Eradicate untyped dictionary lookups (`config.additional_params.get("thinking_budget_tokens")`) and access typed `config.thinking_budget_tokens`.
  - When `gemini-3*` (model starting with `gemini/` or `gemini-3`) is detected:
    - Map `thinking_budget_tokens` to `generationConfig.thinkingConfig.thinkingBudget`.
    - Enforce `temperature = 1.0` if `temperature < 1.0` was passed.
    - Strip deprecated parameters (`top_k`, `frequency_penalty`, `presence_penalty`).

#### [MODIFY] [anthropic_adapter.py](file:///c:/src/quorum/backend_v2/llm/adapters/anthropic_adapter.py#L15-L208)
- Implement `prepare_kwargs`:
  - Translate `thinking_budget_tokens` -> `thinking: {"type": "enabled", "budget_tokens": N}` for `claude-3-7*`.
  - When thinking is active, automatically force `temperature = 1.0` to satisfy Anthropic API requirements.

#### [MODIFY] [openai_adapter.py](file:///c:/src/quorum/backend_v2/llm/adapters/openai_adapter.py#L17-L129)
- Implement `prepare_kwargs`:
  - Translate `thinking_budget_tokens` -> `reasoning_effort: "low" | "medium" | "high"` for o1/o3-series models.
  - Strip `temperature`, `top_p`, and penalty fields for reasoning models.

#### [MODIFY] [provider.py](file:///c:/src/quorum/backend_v2/llm/provider.py#L504-L520)
- Relax strict `temperature is None` crash to allow provider adapters to apply their canonical defaults for reasoning models (while maintaining fail-fast on standard models).

---

### Layer 3: Static Data Vault (`seed_data.json`)
#### [MODIFY] [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json#L1-L105)
- Update `system_config` model registry definitions based on configured platform (`vertex_ai/gemini-3.7-flash` for Vertex AI or `gemini/gemini-3.7-flash` for AI Studio):
  - `deep`: `model_name: "vertex_ai/gemini-3.7-flash"`, `temperature: 1.0`, `thinking_budget_tokens: 4096`, `max_tokens: 32768`, `top_p: null`, `top_k: null`, `frequency_penalty: null`, `presence_penalty: null`.
  - `synthesis`: `model_name: "vertex_ai/gemini-3.7-flash"`, `temperature: 1.0`, `thinking_budget_tokens: 2048`, `max_tokens: 32768`, `top_p: null`, `top_k: null`, `frequency_penalty: null`, `presence_penalty: null`.
  - `fast`: `model_name: "vertex_ai/gemini-3.7-flash"`, `temperature: 1.0`, `thinking_budget_tokens: 0`, `max_tokens: 8192`, `top_p: null`, `top_k: null`, `frequency_penalty: null`, `presence_penalty: null`.
  - `strict`: `model_name: "vertex_ai/gemini-3.7-flash"`, `temperature: 1.0`, `thinking_budget_tokens: 0`, `max_tokens: 16384`, `top_p: null`, `top_k: null`, `frequency_penalty: null`, `presence_penalty: null`.
  - `reasoning`: `model_name: "vertex_ai/gemini-3.7-flash"`, `temperature: 1.0`, `thinking_budget_tokens: 8192`, `max_tokens: 65536`, `top_p: null`, `top_k: null`, `frequency_penalty: null`, `presence_penalty: null`.

---

### Layer 4: Flutter Admin Studio UI & Localization
#### [MODIFY] [model_registry_view.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/views/model_registry_view.dart#L380-L450) & [L575-L705]
- Retain all input fields as requested.
- Update platform switch defaults so selecting `ai_studio` defaults to `gemini/gemini-3.7-flash` and selecting `vertex_ai` defaults to `vertex_ai/gemini-3.7-flash`.
- Add `thinking_budget_tokens` integer input field with preset helper hints (0 = Off, 2048 = Low, 4096 = Med, 8192 = High).
- Add contextual warning/helper text banners explaining that `top_p`, `top_k`, and penalty parameters are bypassed/deprecated on reasoning models (Gemini 3+, Claude 3.7 Thinking, OpenAI o-series).

#### [MODIFY] [app_en.arb](file:///c:/src/quorum/client_app_v2/lib/l10n/app_en.arb#L475-L520) & [app_fi.arb](file:///c:/src/quorum/client_app_v2/lib/l10n/app_fi.arb#L335-L375)
- Add localized strings: `thinkingBudgetTokensLabel`, `thinkingBudgetHelper`, `reasoningModelNotice`, `legacyParameterNotice`.

---

### Layer 5: Testing & Quality Gates
#### [NEW] [test_adapter_parameter_sanitization.py](file:///c:/src/quorum/backend_v2/tests/unit/llm/adapters/test_adapter_parameter_sanitization.py)
- Positive & negative unit tests for `VertexAdapter`, `AIStudioAdapter`, `AnthropicAdapter`, and `OpenAIAdapter` verifying correct parameter translation, `temperature = 1.0` enforcement, and sanitization of deprecated parameters.

#### [MODIFY] [model_registry_view_test.dart](file:///c:/src/quorum/client_app_v2/test/features/studio/views/model_registry_view_test.dart#L1-L100)
- Update widget tests to verify `thinking_budget_tokens` rendering, platform prefix defaults, and form saving.

---

## Architectural Invariants & 5-Column Directives

| 1. Kohdealue & Skoopit (Target Scope) | 2. 🚫 KIELLETTY PURKKA (Eradicated Duct-Tape) | 3. 🎯 TEE NÄIN (Approved Best Practice) | 4. ✂️ KARSITTU YLISUUNNITTELU (Pruned Over-Engineering) | 5. 🔒 VERIFIOINTI & FAIL-FAST (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Domain Models & DTOs** (`v2_core.py#L351-L379`, `model_config.dart#L24-L51`) | Älä piilota `thinking_budget_tokens` -kenttää vapaamuotoiseen `additional_params` -sanakirjaan ilman tyypitystä (`config.additional_params.get(...)`). | Määrittele `thinking_budget_tokens: int | None = Field(default=None)` suoraan `ModelProfile`- ja `LlmModelConfig`-malleihin. | Älä rakenna erillistä rinnakkaista mallialiluokkaa, vaan laajenna olemassa olevaa SSOT-mallia. | `ValidationError` heitetään jos kenttään syötetään virheellinen tyyppi. Dart `flutter_audit_loop.py --build` menee läpi. |
| **Provider Parameter Sanitization** (`vertex_adapter.py#L381-L456`, `ai_studio_adapter.py#L339-L382`) | Älä käytä `.get("key", default)` -ketjuja tai hiljaisia `try...except Exception: pass` -blokkeja ilman lokitusta. | Siivoa kielletyt parametrit (`top_k`, `penalties`) ja pakota `temperature=1.0` suoraan adapterin `prepare_kwargs`-metodissa. | Älä rakenna geneeristä dynaamista `ParameterSanitizerRuleEngine`-abstraktiota yhdelle malliperheelle. | Yksikkötesti syöttää `temperature=0.2` ja varmistaa, että `call_kwargs` sisältää `temperature=1.0` ja varoituslokitus suoritetaan. |
| **LiteLLM Provider Contract** (`provider.py#L504-L520`) | Älä kaada suoritusta suoraan jos malli ei vaadi lämpötilaa (esim. OpenAI o1/o3 reasoning models). | Salli `temperature is None` ainoastaan silloin kun adapteri on nimenomaisesti merkinnyt mallin reasoning-malliksi tai asettanut oletusarvon. | Älä poista `temperature is None` -tarkistusta kokonaan tavallisilta malleilta. | Testaa, että standardi `gemini-1.5-flash` ilman lämpötilaa kaatuu Fail-Fast `ConfigurationError`-virheeseen, mutta `gemini-3.7-flash` sanitoidaan. |
| **Admin UI & Localization** (`model_registry_view.dart#L380-L450`, `app_en.arb`, `app_fi.arb`) | Älä kovakoodaa varoitustekstejä tai ohjeita Dart-koodiin (`reasoningModelNotice`). | Lisää kaikki ilmoitukset ja kenttäkuvaukset `.arb`-tiedostoihin ja lue ne `AppLocalizations.of(context)` kautta. | Älä rakenna monimutkaista dynaamista validointimoottoria UI-kentille; luota backendin schema-validointiin. | Widget-testi todistaa, että kenttä renderöityy ja validointi näyttää oikean lokalisoidun varoituksen. |
| **Seed Data & Seeding** (`seed_data.json#L1-L105`) | Älä jätä strategioihin vanhoja Gemini 1.5 -malleja tai ristiriitaisia `top_p`/`top_k`-arvoja. | Päivitä kaikki 5 strategiaa `gemini-3.7-flash`-malliin `temperature: 1.0` ja roolikohtaisilla `thinking_budget_tokens` -arvoilla. | Älä luo rinnakkaisia "varastrategioita" seed_dataan. | `uv run python backend_v2/seed/run_seed.py local` ajaa tietokannan alustuksen ilman virheitä. |

---

## Canonical Execution Protocol

```xml
<execution_protocol>
  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_unified_model_multiplexing.md]</knowledge_item>
    <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  </required_context_rules>

  <phase id="1" name="PRE_IMPLEMENTATION_CLEANUPS_AND_SCHEMAS">
    <step id="1.1" name="ERADICATE_ADAPTER_DYNAMIC_LOOKUPS">
      <action>Clean up untyped `config.additional_params.get("thinking_budget_tokens")` duct-tape in @[backend_v2/llm/adapters/vertex_adapter.py#L381-L455] and @[backend_v2/llm/adapters/ai_studio_adapter.py#L339-L381].</action>
      <constraint invariant="zero_service_layer_fallbacks">Use strictly typed `config.thinking_budget_tokens` attribute access.</constraint>
    </step>
    <step id="1.2" name="UPDATE_BACKEND_MODEL_PROFILE">
      <action>Modify @[backend_v2/models/v2_core.py#L351-L377] to add `thinking_budget_tokens: int | None = Field(default=None)`.</action>
      <constraint invariant="pydantic_strictness">Maintain `ConfigDict(strict=True, extra="forbid")`.</constraint>
    </step>
    <step id="1.3" name="UPDATE_FRONTEND_LLM_MODEL_CONFIG">
      <action>Modify @[client_app_v2/lib/features/studio/models/model_config.dart#L24-L51] to add `thinkingBudgetTokens`.</action>
      <action>Run build runner: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/model_config.dart --build`.</action>
    </step>
  </phase>

  <phase id="2" name="ADAPTER_PARAMETER_SANITIZATION">
    <step id="2.1" name="UPDATE_VERTEX_AND_AI_STUDIO_ADAPTERS">
      <action>Modify @[backend_v2/llm/adapters/vertex_adapter.py#L381-L455] and @[backend_v2/llm/adapters/ai_studio_adapter.py#L339-L381] to sanitize `gemini-3*` parameters and translate `thinking_budget_tokens`.</action>
      <constraint invariant="provider_abstraction_mandate">Encapsulate all model-specific parameter logic in adapters.</constraint>
    </step>
    <step id="2.2" name="UPDATE_ANTHROPIC_AND_OPENAI_ADAPTERS">
      <action>Modify @[backend_v2/llm/adapters/anthropic_adapter.py#L15-L207] and @[backend_v2/llm/adapters/openai_adapter.py#L17-L128] to normalize thinking parameters and sanitize sampling fields.</action>
    </step>
    <step id="2.3" name="RELAX_PROVIDER_TEMPERATURE_CHECK">
      <action>Modify @[backend_v2/llm/provider.py#L436-L1017] so that provider adapters can safely handle default/optional temperature on reasoning models while keeping strictness on standard models.</action>
    </step>
    <step id="2.4" name="CREATE_ADAPTER_UNIT_TESTS">
      <action>Create [NEW] @[backend_v2/tests/unit/llm/adapters/test_adapter_parameter_sanitization.py] covering ISTQB positive and negative partitions (AI Studio Gemini 3.7, Vertex AI Gemini 3.7, Claude 3.7 thinking, o3-mini, legacy models).</action>
      <action>Run audit: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/llm/adapters/test_adapter_parameter_sanitization.py --test`.</action>
    </step>
  </phase>

  <phase id="3" name="SEED_DATA_VAULT_MUTATION">
    <step id="3.1" name="BACKUP_AND_MUTATE_SEED_DATA">
      <action>Execute vault backup: `New-Item -ItemType Directory -Force -Path backend_v2/seed/backups; Copy-Item backend_v2/seed/seed_data.json -Destination backend_v2/seed/backups/seed_data_gemini37_backup.json`.</action>
      <action>Modify @[backend_v2/seed/seed_data.json#L1-L105] to update all 5 strategies to `vertex_ai/gemini-3.7-flash` (or `gemini/gemini-3.7-flash`) with `temperature: 1.0` and appropriate thinking budgets.</action>
      <action>Verify backend audit: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.</action>
      <action>Re-seed local database: `uv run python backend_v2/seed/run_seed.py local`.</action>
    </step>
  </phase>

  <phase id="4" name="FRONTEND_UI_AND_L10N">
    <step id="4.1" name="UPDATE_LOCALIZATION_ARB_FILES">
      <action>Modify @[client_app_v2/lib/l10n/app_en.arb#L475-L520] and @[client_app_v2/lib/l10n/app_fi.arb#L335-L375] with new keys for thinking budget and reasoning parameter warnings.</action>
      <action>Generate l10n: `cd client_app_v2; flutter gen-l10n`.</action>
    </step>
    <step id="4.2" name="UPDATE_MODEL_REGISTRY_VIEW">
      <action>Modify @[client_app_v2/lib/features/studio/views/model_registry_view.dart#L380-L450] and @[client_app_v2/lib/features/studio/views/model_registry_view.dart#L575-L705] to add `thinking_budget_tokens` input, platform default model names, and explanatory warning banners.</action>
      <action>Run flutter audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/model_registry_view.dart`.</action>
    </step>
    <step id="4.3" name="VERIFY_FRONTEND_WIDGET_TESTS">
      <action>Update and run @[client_app_v2/test/features/studio/views/model_registry_view_test.dart#L1-L183].</action>
      <action>Run flutter audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/model_registry_view_test.dart`.</action>
    </step>
  </phase>

  <phase id="5" name="FINAL_COMPLETION_GATE">
    <step id="5.1" name="FULL_SYSTEM_AUDIT_LOOPS">
      <action>Run backend quality gate: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.</action>
      <action>Run flutter quality gate: `uv run python scripts/flutter_audit_loop.py client_app_v2`.</action>
    </step>
  </phase>
</execution_protocol>
```

## Verification Plan

### Automated Tests
- Unit tests for adapter parameter sanitization: `uv run pytest backend_v2/tests/unit/llm/adapters/test_adapter_parameter_sanitization.py -v`
- Full backend audit gate: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- Frontend widget tests & build verification: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`

### Manual Verification
1. Launch local stack via `run_local.bat`.
2. Open Flutter Admin Studio -> Model Registry.
3. Switch platform between `ai_studio` (`gemini/gemini-3.7-flash`) and `vertex_ai` (`vertex_ai/gemini-3.7-flash`) to verify default model name resolution.
4. Verify that `thinking_budget_tokens` is visible and editable.
5. Verify that explanatory notices display clearly for reasoning models.
6. Trigger an analysis execution and verify in `backend_debug.log` that `gemini-3.7-flash` executes smoothly without `temperature < 1.0` or `top_p`/`top_k` deprecation warnings.
