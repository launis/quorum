> **STATUS: COMPLETED / TOTEUTETTU (100% Implemented & Verified)**

# Implementation Plan: Token Counter SSOT, FinOps Cost Calculation & Adapter DRY Harmonization

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_unified_model_multiplexing.md]</knowledge_item>
</required_context_rules>

## 1. Executive Summary & Root Cause Analysis

### 1.1 Root Cause Analysis: Miksi token-laskuri antoi näytöllä nollaa?
1. **Backend Metadata Hierarkiaepäsuhta (`backend_v2/worker.py`)**:
   - `worker.py` laski DAG-ajon valmistuttua kertyneet tokenit (`total_prompt_tokens`, `total_completion_tokens`, `total_cached_tokens`, `total_reasoning_tokens`), mutta asetti ne ainoastaan sisäkkäiseen `metadata["execution_summary"]["aggregated_usage"]` -rakenteeseen.
   - Se **EI** asettanut näitä avaimia suoraan `metadata`-sanakirjan juuritasolle (`metadata["total_tokens"]`, `metadata["prompt_tokens"]`, `metadata["completion_tokens"]`).
2. **Frontendin Oletus Juuritasosta (`client_app_v2`)**:
   - `dashboard_view.dart` ja `execution_status_card.dart` yrittävät lukea suoraan:
     ```dart
     final totalT = (metadata['total_tokens'] as num?)?.toInt() ?? 0;
     final promptT = (metadata['prompt_tokens'] as num?)?.toInt() ?? 0;
     final completionT = (metadata['completion_tokens'] as num?)?.toInt() ?? 0;
     ```
   - Koska avaimet olivat `null`, arvot nollaantuivat hiljaisesti.

---

### 1.2 Yksi Tapa ja Yksi Totuus: Vain `metadata`-Juuritaso (Zero Duplication & Zero Fallbacks)
1. **Päätös & Arkkitehtoninen Invariantti**:
   - **Vain yksi paikka**: Kaikki token- ja kustannusmetriikat tallennetaan ja luetaan **yksinomaan ja ainoastaan `metadata`-sanakirjan juuritasolta**:
     - `metadata["total_tokens"]`: Kokonaistokenit (`int`)
     - `metadata["prompt_tokens"]`: Syötetokenit (`int`)
     - `metadata["completion_tokens"]`: Vastaustokenit (`int`)
     - `metadata["cached_tokens"]`: Välimuistitetut tokenit (`int`)
     - `metadata["reasoning_tokens"]`: Päättelytokenit (`int`)
     - `metadata["cost_usd"]`: Kustannus USD (`float`)
   - Poistetaan redundantit rinnakkaisrakenteet ja fallback-ketjut (`aggregated_usage`). Sekä backend että frontend käyttävät identtistä 1:1 `metadata`-sopimusta.

---

### 1.3 FinOps-kustannuslaskenta: LiteLLM Pricing Registry SSOT & Adapter Caching Math
1. **Päätös & Yksi Totuus (`litellm_pricing_ssot_mandate`)**:
   - **LiteLLM:n hintatietokanta (`litellm.model_cost` / `litellm.get_model_info`) on AINOA yksikköhintojen lähde (SSOT)** koko järjestelmässä.
   - Ei ylläpidetä rinnakkaisia kovakoodattuja hinnastoja `settings.py`:ssä tai siementiedoissa.
   - **Kaksivaiheinen mallihaku (`self.model_name` ja `clean_model`)**: Haetaan hinnastosta ensin täydellä mallinimellä (`self.model_name`, esim. `vertex_ai/gemini-2.5-pro`) ja toissijaisesti puhtaalla nimellä (`clean_model`, esim. `gemini-2.5-pro`), mikä estää virheelliset nollahinnat.
   - **Deterministinen `PricingConfig(0.0, 0.0)` ja varoitusloki (`feature_audit_litellm_deterministic_pricing.md`)**: Jos mallia ei löydy rekisteristä tai sen yksikköhinnat ovat puutteellisia, muodostetaan deterministisesti tiukka `PricingConfig(input_token_price=0.0, output_token_price=0.0)` ja kirjataan `logger.warning` virhekoodilla `ErrorCodes.CONFIGURATION_WARNING`. Tämä takaa, ettei toissijainen telemetriapuute koskaan kaada onnistunutta LLM-inferenssiä tuotannossa (`KeyError`/`TypeError`-suojaus).
   - Kustannus (`cost_usd`) ja välimuistisäästöt (`estimated_savings_usd`) lasketaan **yksinomaan ja ainoastaan** kyseisen palveluntarjoajan `BaseLLMAdapter.calculate_cost(usage, pricing_config)` -menetelmällä.
   - @[backend_v2/llm/provider.py] ja @[backend_v2/services/usage_service.py] hyödyntävät suoraan tätä yhtä jaettua adapteritoteutusta.

---

### 1.4 DRY & SSOT -rikkomus adaptereissa
- `vertex_adapter.py`, `ai_studio_adapter.py` ja `anthropic_adapter.py` toteuttavat kaikki saman `static_messages`-sisällön merkkimäärän ja tokeniarvion laskennan (`total_chars // 4`).
- Tämä logiikka keskitetään `BaseLLMAdapter`-luokkaan jaetuksi apumetodiksi: `estimate_static_tokens(compiled_prompt, exclude_system=False)`.

### 1.5 Redundantit `*TokenUsage`-aliluokat (Tier 0 Discovery — Kaikki 5 Aliluokkaa)
- `VertexTokenUsage` (@[backend_v2/llm/adapters/vertex_adapter.py]), `GoogleAIStudioTokenUsage` (@[backend_v2/llm/adapters/ai_studio_adapter.py]), `AnthropicTokenUsage` (@[backend_v2/llm/adapters/anthropic_adapter.py]), `OpenAITokenUsage` (@[backend_v2/llm/adapters/openai_adapter.py]) ja `MockTokenUsage` (@[backend_v2/llm/adapters/mock_adapter.py]) ovat **kaikki redundantteja** — base `TokenUsage` (@[backend_v2/models/domain/usage.py]) sisältää jo kaikki tarvittavat kentät (`estimated_savings_usd`, `cache_creation_input_tokens`, `cost_usd`).
- Nämä 5 aliluokkaa poistetaan kokonaan ja kaikkien adapterien `calculate_cost` palauttaa suoraan `TokenUsage`-instanssin.
- **Anthropic `isinstance`-piilokytky**: @[backend_v2/llm/adapters/anthropic_adapter.py] poistetaan `if isinstance(usage, AnthropicTokenUsage)` -ehto ja luetaan `usage.cache_creation_input_tokens` suoraan, koska kenttä on jo base-luokassa.

### 1.6 `PricingConfig` Domain Model SSOT (Zero Naked Dicts)
- Poistetaan `no_naked_dicts_in_state` -antipatterni adapterien `calculate_cost(usage, pricing_config: PricingConfig)` -rajapinnasta.
- Määritellään tiukka Pydantic V2 -malli `PricingConfig` (@[backend_v2/models/domain/usage.py]):
  - `input_token_price: float`
  - `output_token_price: float`
  - `cached_input_token_price: float | None = None`
  - `cache_creation_input_token_price: float | None = None`
- Kaikki adapterit vastaanottavat `pricing_config: PricingConfig` ja hyödyntävät suoria attribuutteja (`pricing_config.input_token_price`, `pricing_config.cache_creation_input_token_price`), poistaen toistuvan `if "input_token_price" not in pricing_config` -tarkistuskoodin.
- Anthropic-adapteri hyödyntää `pricing_config.cache_creation_input_token_price` -kenttää suoraan välimuistin luontihintana (korvaten kovakoodatun 1.25-kertoimen, fallbackina $1.25 \times P_{in}$ jos kenttä puuttuu) ja laskee nettosäästöt turvallisesti nollatasoon suojattuna (`max(0.0, gross_savings - creation_surcharge)` per `feature_audit_pricing_config_cache_creation_cost.md`).
- @[backend_v2/services/usage_service.py#L87] päivitetään validoimaan `PricingConfig.model_validate(model_pricing_config)` ja poistetaan L90-91 hiljainen `except Exception` -duct tape.

### 1.7 Vanhentuneiden ja Ohitettujen Testien Palautus (`anti_test_skipping_mandate`)
- @[backend_v2/tests/unit/llm/adapters/test_openai_adapter.py] ja @[backend_v2/tests/unit/llm/adapters/test_deepseek_adapter.py] sisältävät tällä hetkellä kaikissa testeissään `@pytest.mark.skip("Legacy architecture obsolete")` -ohitukset.
- Nämä testit **UN-SKITATAAN ja modernisoidaan** `PricingConfig`-sopimukselle osana tätä tehtävää.

---

## 1.8 Tri-Axis Dialectical Audit & Red-Team Assessment (Tier 0 Validated)

### 1. PROSECUTION (Over-Engineering & YAGNI Advocate)
- **Challenge**: Is moving token character estimation to `BaseLLMAdapter` adding unnecessary complexity when each provider has subtly different requirements (specifically: Anthropic considers system messages while Vertex and Google AI Studio exclude them)?
- **Mandatory Deletion Test**: If we cut `estimate_static_tokens`, each adapter retains 15 lines of token counting loops. By abstracting it with an `exclude_system: bool` parameter, we eliminate 45 lines of duplicate boilerplate and establish a single point of maintenance.
- **Pruned**: The originally proposed `_extract_message_chars` as a separate method is over-engineering — it is only called from one location. Its content extraction logic is inlined directly within `estimate_static_tokens`.

### 2. DEFENSE (Architectural Sovereignty & Fail-Fast Advocate)
- **Proof 1**: Root-level metadata SSOT is non-negotiable — the current system has a structural fracture between backend (nested dict) and frontend (root reads), producing zero-value tokens in the UI.
- **Proof 2**: Eliminating `litellm.completion_cost` and centralizing in adapters ensures FinOps pricing accuracy is under our control (LiteLLM pricing tables lag behind provider updates).
- **Proof 3**: All 5 redundant `*TokenUsage` subclasses violate `schema_convergence_mandate` ("One Concept = One Schema"). Base `TokenUsage` already has every field. Subclasses MUST be deleted.
- **Proof 4**: Removing `isinstance(usage, AnthropicTokenUsage)` guard enforces Pydantic structural integrity — base class fields must be accessed directly without runtime type guards.

### 3. REALIST (Duct-Tape & Blast Radius Interrogator)
- **Challenge**: By enforcing LiteLLM as the single source for pricing, what happens if an uncataloged model is invoked?
- **Root Cause & Resolution**: As audited in `feature_audit_litellm_deterministic_pricing.md`, naive dictionary lookups would raise `KeyError` and crash the execution after tokens were spent. The realist architecture performs a 2-stage dictionary lookup (`self.model_name` -> `clean_model`), safely constructs `PricingConfig(input_token_price=0.0, output_token_price=0.0)` if unlisted, and logs a structured warning (`ErrorCodes.CONFIGURATION_WARNING`). Inferences succeed, telemetry remains type-safe, and DevOps is notified.
- **Blast Radius Analysis**:
  - `blueprint.py#L341-364` contains multiple duct-tape anti-patterns: relying on `execution.metadata.get("aggregated_usage", {})`, `getattr(execution, "cumulative_synthesis_cost", 0.0)`, `getattr(execution, "cumulative_synthesis_tokens", 0)`, and `getattr(profile, "scoring_strategy", ...)` chains. Since `ExecutionRecord` is a strict Pydantic model containing these fields natively, all `getattr` calls MUST be replaced with direct attribute access, and `metadata` must use strict key access (clean start — no historical data backward compatibility).
  - `vertex_adapter.py` and `ai_studio_adapter.py` currently contain `getattr(config, "additional_params", None)` and `getattr(config, "vertex_location", None)` which violate strict attribute access. We resolve this technical debt in Step 1.
  - **CRITICAL**: 9 monkeypatches of `litellm.completion_cost` exist across 8 test files. All 8 test files MUST be included in the target scope.
  - **CRITICAL**: `test_openai_adapter.py` and `test_deepseek_adapter.py` have ALL tests skipped with `@pytest.mark.skip`. They MUST be un-skipped and modernized per `anti_test_skipping_mandate`.
  - `usage_service.py#L90-91` contains a silent `except Exception` duct-tape block that must be replaced with explicit error handling. Dual cost calculation between provider and usage_service is unified so provider computes via adapter and usage_service records without recalculation.
  - **Deferred Tech Debt**: `provider.py` L760-806 contains 10+ `hasattr`/`getattr` calls on LiteLLM response objects (3rd-party boundary).

### 4. BINDING VERDICT & DECISION MATRIX
- **(A) Approved Best Practice**: Root-level `metadata` SSOT, LiteLLM Pricing Registry ainoana hintalähteenä (`litellm_pricing_ssot_mandate`), `PricingConfig` Pydantic-malli sisältäen `cache_creation_input_token_price` -tuen (`feature_audit_pricing_config_cache_creation_cost.md`, `no_naked_dicts_in_state`), DRY `estimate_static_tokens` helper.
- **(B) Pruned Over-Engineering**: `_extract_message_chars` merged inline into `estimate_static_tokens` — no separate method needed. No parallel pricing dictionaries in `settings.py`. No provider-specific pricing config subclasses.
- **(C) Eradicated Duct-Tape**: Delete ALL 5 redundant `*TokenUsage` subclasses (Vertex, GoogleAIStudio, Anthropic, OpenAI, Mock). Remove `getattr` checks in adapters and `blueprint.py`. Fix Anthropic `isinstance` coupling and replace 1.25 hardcoded multiplier with dynamic `pricing_config.cache_creation_input_token_price`. Remove dead DeepSeek branching from `openai_adapter.py`. Promote `usage_service.py` to `[MODIFY]` and eliminate silent `except Exception` duct tape. Update `blueprint.py` to strict root-level key access (Fail-Fast, clean start). Un-skip and fix all tests in `test_openai_adapter.py` and `test_deepseek_adapter.py`.
- **(D) Deferred**: `provider.py` L760-806 `hasattr`/`getattr` response parsing (LiteLLM boundary); typed Metadata DTO.

---

## 2. Target & Context Boundaries

### Target Files:
- `[MODIFY]` @[backend_v2/models/domain/usage.py]
- `[MODIFY]` @[backend_v2/llm/adapters/base_adapter.py]
- `[MODIFY]` @[backend_v2/llm/adapters/vertex_adapter.py]
- `[MODIFY]` @[backend_v2/llm/adapters/ai_studio_adapter.py]
- `[MODIFY]` @[backend_v2/llm/adapters/anthropic_adapter.py]
- `[MODIFY]` @[backend_v2/llm/adapters/openai_adapter.py]
- `[MODIFY]` @[backend_v2/llm/adapters/deepseek_adapter.py]
- `[MODIFY]` @[backend_v2/llm/adapters/mock_adapter.py]
- `[MODIFY]` @[backend_v2/llm/adapters/adapter_factory.py]
- `[MODIFY]` @[backend_v2/worker.py]
- `[MODIFY]` @[backend_v2/services/blueprint.py]
- `[MODIFY]` @[backend_v2/services/usage_service.py]
- `[MODIFY]` @[backend_v2/llm/provider.py]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/dashboard_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/execution_status_card.dart]

### Context & Test Files:
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_base_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_anthropic_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_openai_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_deepseek_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_mock_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/test_provider.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_provider_rate_limit.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_litellm_redis_timeout.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/test_transient_error_detection.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/test_provider_toolcalls.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/test_fallback_caching.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/test_adaptive_retry.py]
- `[MODIFY]` @[backend_v2/tests/test_provider_caching_scrub.py]

---

## 3. Execution Protocol (XML Sandwich)

```xml
<execution_protocol>
  <step id="1" name="PRE_REQUISITE_TECH_DEBT_CLEANUPS_AND_BASE_ADAPTER_SSOT">
    <action>In @[backend_v2/models/domain/usage.py], define strictly typed `PricingConfig(V2CoreBase)` with `input_token_price: float`, `output_token_price: float`, `cached_input_token_price: float | None = None`, and `cache_creation_input_token_price: float | None = None` (ConfigDict strict=True, extra="forbid").</action>
    <action>In @[backend_v2/services/blueprint.py], clean up pre-existing technical debt: replace `getattr(execution, "cumulative_synthesis_cost", 0.0)` and `getattr(execution, "cumulative_synthesis_tokens", 0)` with direct attribute access (`execution.cumulative_synthesis_cost`, `execution.cumulative_synthesis_tokens`), and replace `getattr(profile, "scoring_strategy", None)` fallback chain with direct property reads.</action>
    <action>In @[backend_v2/llm/adapters/vertex_adapter.py] and @[backend_v2/llm/adapters/ai_studio_adapter.py], replace legacy `getattr(config, "additional_params", None)` and `getattr(config, "vertex_location", None)` with direct attribute access (`config.additional_params`, `config.vertex_location`) since LLMProviderConfig is a strict Pydantic model.</action>
    <action>Delete redundant `VertexTokenUsage` class from @[backend_v2/llm/adapters/vertex_adapter.py] and update `calculate_cost` signature to accept `pricing_config: PricingConfig` and return `TokenUsage`.</action>
    <action>Delete redundant `GoogleAIStudioTokenUsage` class from @[backend_v2/llm/adapters/ai_studio_adapter.py] and update `calculate_cost` signature to accept `pricing_config: PricingConfig` and return `TokenUsage`.</action>
    <action>Delete redundant `AnthropicTokenUsage` class from @[backend_v2/llm/adapters/anthropic_adapter.py] and update `calculate_cost` signature to accept `pricing_config: PricingConfig` and return `TokenUsage`.</action>
    <action>In @[backend_v2/llm/adapters/anthropic_adapter.py], remove `if isinstance(usage, AnthropicTokenUsage)` guard and read `usage.cache_creation_input_tokens` directly.</action>
    <action>Delete redundant `OpenAITokenUsage` class from @[backend_v2/llm/adapters/openai_adapter.py] and update `calculate_cost` signature to accept `pricing_config: PricingConfig` and return `TokenUsage`.</action>
    <action>Delete redundant `MockTokenUsage` class from @[backend_v2/llm/adapters/mock_adapter.py] and update `calculate_cost` to return `TokenUsage(..., estimated_savings_usd=0.05)` directly.</action>
    <action>In @[backend_v2/llm/adapters/deepseek_adapter.py], update `calculate_cost` return type from `OpenAITokenUsage` to `TokenUsage` and remove the `OpenAITokenUsage` import.</action>
    <action>In @[backend_v2/llm/adapters/base_adapter.py], update abstract `calculate_cost(self, usage: TokenUsage, pricing_config: PricingConfig) -> TokenUsage` signature.</action>
    <action>Implement `estimate_static_tokens(compiled_prompt: CompiledPrompt, exclude_system: bool = False) -> tuple[int, bool]` on `BaseLLMAdapter` in @[backend_v2/llm/adapters/base_adapter.py]. Content char extraction logic (handling `str`, `list[dict]` text blocks, and raw objects) is inlined directly within this method — NO separate `_extract_message_chars` helper. Returns estimated token count (`total_chars // 4`) and boolean flag indicating whether non-system turns exist.</action>
    <constraint invariant="pydantic_strictness">PricingConfig and estimate_static_tokens must be pure, synchronous, and fully type-annotated without generic Any fallbacks.</constraint>
    <constraint invariant="schema_convergence_mandate">Zero redundant TokenUsage subclasses: base TokenUsage is the ONE schema for all 5 providers.</constraint>
  </step>

  <step id="2" name="REFACTOR_ADAPTERS_TO_USE_SSOT">
    <action>Refactor @[backend_v2/llm/adapters/vertex_adapter.py] to replace duplicated token loop with `self.estimate_static_tokens(compiled_prompt, exclude_system=True)` and use `pricing_config.input_token_price` / `pricing_config.output_token_price` in `calculate_cost`.</action>
    <action>Refactor @[backend_v2/llm/adapters/ai_studio_adapter.py] to replace duplicated token loop with `self.estimate_static_tokens(compiled_prompt, exclude_system=True)` and use `pricing_config.input_token_price` / `pricing_config.output_token_price` in `calculate_cost`.</action>
    <action>Refactor @[backend_v2/llm/adapters/anthropic_adapter.py] to replace duplicated token loop with `self.estimate_static_tokens(compiled_prompt, exclude_system=False)` and update `calculate_cost` to use `pricing_config.input_token_price`, `pricing_config.output_token_price`, `pricing_config.cached_input_token_price` (fallback $0.10 \times P_{in}$), and `pricing_config.cache_creation_input_token_price` (fallback $1.25 \times P_{in}$), clamping net estimated savings at $\ge 0.0$ via `max(0.0, gross_savings - creation_surcharge)`.</action>
    <action>Update @[backend_v2/llm/adapters/openai_adapter.py] `calculate_cost`: accept `pricing_config: PricingConfig`, read direct properties (`pricing_config.input_token_price`, `pricing_config.output_token_price`), use fixed OpenAI 50% read discount (`discount_factor = 0.50`, `savings_factor = 0.50`), and remove dead `is_deepseek` string-branching (L112-118) since DeepSeek has its own adapter.</action>
    <action>Update @[backend_v2/llm/adapters/deepseek_adapter.py] and @[backend_v2/llm/adapters/mock_adapter.py] `calculate_cost` methods to accept `pricing_config: PricingConfig` and read direct properties.</action>
    <action>In @[backend_v2/llm/adapters/adapter_factory.py], evaluate and remove the duplicate `LLMProviderName.VERTEX_AI` case branch at L60-80 if it is fully subsumed by the `LLMProviderName.GOOGLE | "google"` umbrella case at L82-96 with `is_vertex` disambiguation. If both branches are required for distinct routing paths, add a clarifying comment and leave intact.</action>
    <constraint invariant="dry_mandate">Zero duplicate token counting loop implementations across concrete adapter classes.</constraint>
  </step>

  <step id="3" name="BACKEND_WORKER_AND_BLUEPRINT_METADATA_ROOT_SSOT">
    <action>Update @[backend_v2/worker.py] to store all tokens and costs EXCLUSIVELY at the root of `updated_meta`:
      - `updated_meta["total_tokens"] = total_prompt_tokens + total_completion_tokens + total_reasoning_tokens`
      - `updated_meta["prompt_tokens"] = total_prompt_tokens`
      - `updated_meta["completion_tokens"] = total_completion_tokens`
      - `updated_meta["cached_tokens"] = total_cached_tokens`
      - `updated_meta["reasoning_tokens"] = total_reasoning_tokens`
      - `updated_meta["cost_usd"] = total_cost_usd`
      Remove the nested `"aggregated_usage"` sub-dictionary from `execution_summary` entirely.
    </action>
    <action>Ensure synthesis tokens and cost in `render_profile_job` update `metadata` root fields consistently in @[backend_v2/worker.py].</action>
    <action>Update @[backend_v2/services/blueprint.py] to read `total_exec_tokens` and `total_exec_cost` using STRICT key access (clean start — no historical data backward compatibility):
      - `total_exec_cost = float(metadata["cost_usd"])`
      - `total_exec_tokens = int(metadata["prompt_tokens"] + metadata["completion_tokens"] + metadata["reasoning_tokens"])`
      Remove all `.get("aggregated_usage", {})` chains and legacy fallbacks.
    </action>
    <constraint invariant="universal_fail_fast">Single Source of Truth: All execution telemetry exists directly on metadata root level. No duplicate nested aggregated_usage sub-dictionaries. Zero `.get()` fallbacks — Fail-Fast on missing keys (clean start mandate).</constraint>
  </step>

  <!-- SESSION HANDOVER CHECKPOINT: After Step 3 completes and backend audit passes, execute /tier5-session-handover before starting Step 5 (frontend). This plan touches 13+ files across backend and frontend domains. -->

  <step id="4" name="FINOPS_PROVIDER_COST_CALCULATION_SSOT">
    <action>Eliminate `litellm.completion_cost` entirely from @[backend_v2/llm/provider.py].</action>
    <action>In @[backend_v2/llm/provider.py], resolve provider adapter via `LLMCacheAdapterFactory.get_adapter(provider_name, model_name=self.model_name)`.</action>
    <action>Extract unit token prices directly from LiteLLM's pricing registry (`litellm.model_cost.get(self.model_name)` or `litellm.model_cost.get(clean_model)`). If found, construct `PricingConfig(input_token_price=float(raw_pricing.get("input_cost_per_token", 0.0)), output_token_price=float(raw_pricing.get("output_cost_per_token", 0.0)), cached_input_token_price=float(raw_pricing["cache_read_input_token_cost"]) if raw_pricing.get("cache_read_input_token_cost") is not None else None, cache_creation_input_token_price=float(raw_pricing["cache_creation_input_token_cost"]) if raw_pricing.get("cache_creation_input_token_cost") is not None else None)`. If pricing is missing from the registry, log a structured warning (`ErrorCodes.CONFIGURATION_WARNING`) and instantiate deterministic `PricingConfig(input_token_price=0.0, output_token_price=0.0)` so missing telemetry metadata never halts production LLM inferences.</action>
    <action>Delegate cost and savings calculation exclusively to `adapter.calculate_cost(token_usage, pricing_config)`.</action>
    <action>Pass the calculated `TokenUsage` directly to `self.usage_service.track_usage(...)` ensuring zero recalculation divergence.</action>
    <action>In @[backend_v2/services/usage_service.py], update `track_usage` to accept pre-calculated `cost_usd` and `estimated_savings_usd` from the caller without redundant recalculation. If `model_pricing_config` validation is executed, validate via `PricingConfig.model_validate(model_pricing_config)` and remove silent `except Exception` duct tape (L90-91), re-raising explicit `AppException`.</action>
    <constraint invariant="central_config_sovereignty">LiteLLM Pricing Registry + Adapter calculate_cost is the SOLE authorized method for computing cost_usd and estimated_savings_usd across the system. Zero parallel pricing dictionaries.</constraint>
  </step>

  <step id="5" name="FRONTEND_DASHBOARD_AND_STATUS_CARD_METADATA_ALIGNMENT">
    <action>Update @[client_app_v2/lib/features/execution/views/dashboard_view.dart] to read tokens and costs cleanly and directly from `metadata` root.</action>
    <action>In @[client_app_v2/lib/features/execution/views/dashboard_view.dart], perform Scoped Boy Scout technical debt cleanup per `touched_scope_tech_debt_mandate`: replace hardcoded `Colors.red` (L279) and `Colors.blue` (L329) with `Theme.of(context).colorScheme.error` and `Theme.of(context).colorScheme.primary`.</action>
    <action>Update @[client_app_v2/lib/features/execution/views/widgets/execution_status_card.dart] with identical clean root reads.</action>
    <action>In @[client_app_v2/lib/features/execution/views/widgets/execution_status_card.dart], perform Scoped Boy Scout technical debt cleanup per `touched_scope_tech_debt_mandate` and `design_token_absolute_rule`: replace hardcoded `Colors.green` (L113), `Colors.deepPurple` (L117), and raw colors in `_buildStatusIcon` / `_getStatusColor` (L204-238) with semantic `Theme.of(context).colorScheme` tokens (`primary`, `error`, `tertiary`, `outline`).</action>
    <constraint invariant="cross_domain_dto_parity">Flutter UI strictly reads metadata root contract without fallback branching.</constraint>
    <constraint invariant="design_token_absolute_rule">Zero hardcoded Colors.* references in touched Flutter files.</constraint>
  </step>

  <step id="6" name="AUTOMATED_TESTING_AND_QUALITY_GATES">
    <action>Add unit tests in @[backend_v2/tests/unit/llm/adapters/test_base_adapter.py] testing:
      - `estimate_static_tokens` happy path: mixed message types (strings, text blocks, mixed roles)
      - ISTQB Negative 1: Empty `static_messages` list → returns `(0, False)`
      - ISTQB Negative 2: Messages with only `role: system` and `exclude_system=True` → returns `(0, False)`
      - ISTQB Negative 3: Message with `content: None` → treated as 0 chars
      - ISTQB Negative 4: Message with `content: []` (empty list) → treated as 0 chars
      - `PricingConfig` validation: happy path pricing (with and without `cache_creation_input_token_price`), missing required fields raise ValidationError
    </action>
    <action>Update adapter test suites in @[backend_v2/tests/unit/llm/adapters/] (`test_vertex_adapter.py`, `test_ai_studio_adapter.py`, `test_anthropic_adapter.py`, `test_openai_adapter.py`, `test_deepseek_adapter.py`, `test_mock_adapter.py`):
      - Pass `PricingConfig` instances instead of raw dicts
      - In `test_anthropic_adapter.py`: assert exact cost calculation when `cache_creation_input_token_price` is provided vs default 1.25x fallback, and verify `estimated_savings_usd >= 0.0` when cache writes exceed reads
      - In `test_openai_adapter.py`: UN-SKIP all tests (remove `@pytest.mark.skip`), remove `OpenAITokenUsage` import, change `cast(OpenAITokenUsage, ...)` to `cast(TokenUsage, ...)`, change `isinstance(result, OpenAITokenUsage)` to `isinstance(result, TokenUsage)`, and remove obsolete `pricing_ds_name` dynamic recognition test (Scenario 3) per `anti_test_skipping_mandate`
      - In `test_deepseek_adapter.py`: UN-SKIP all tests (remove `@pytest.mark.skip`), remove `OpenAITokenUsage` import, and change `isinstance(result_ds, OpenAITokenUsage)` to `isinstance(result_ds, TokenUsage)` per `anti_test_skipping_mandate`
      - In `test_mock_adapter.py`, assert returned type is `TokenUsage` with `estimated_savings_usd == 0.05`
    </action>
    <action>Update @[backend_v2/tests/unit/llm/test_provider.py] to verify adapter-exclusive cost calculation without `litellm.completion_cost` monkeypatches:
      - ISTQB Positive 1: Model with known LiteLLM pricing computes exact cost and savings via adapter
      - ISTQB Negative 1: Uncataloged model string defaults to `0.0` cost and emits `ErrorCodes.CONFIGURATION_WARNING` log
      - ISTQB Equivalence 1: Qualified model string (`vertex_ai/gemini-2.5-pro`) and clean model string (`gemini-2.5-pro`) both resolve pricing cleanly
    </action>
    <action>Update ALL 7 additional test files (9 total monkeypatch locations across 8 test files) that monkeypatch `litellm.completion_cost` to use adapter-driven cost mocking instead:
      - @[backend_v2/tests/unit/test_provider_rate_limit.py]
      - @[backend_v2/tests/unit/test_litellm_redis_timeout.py]
      - @[backend_v2/tests/unit/llm/test_transient_error_detection.py]
      - @[backend_v2/tests/unit/llm/test_provider_toolcalls.py]
      - @[backend_v2/tests/unit/llm/test_fallback_caching.py]
      - @[backend_v2/tests/unit/llm/test_adaptive_retry.py]
      - @[backend_v2/tests/test_provider_caching_scrub.py]
    </action>
    <action>Verify all adapter tests pass via `uv run pytest backend_v2/tests/unit/llm/adapters/`.</action>
    <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/models/domain/usage.py --test`.</action>
    <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/llm/adapters/ --test`.</action>
    <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/worker.py --test`.</action>
    <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test`.</action>
    <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/usage_service.py --test`.</action>
    <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider.py --test`.</action>
    <action>Run flutter audit loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/`.</action>
    <constraint invariant="universal_quality_gate">All Ruff, MyPy, AST guardrails, and unit tests must pass with >90% coverage.</constraint>
    <constraint invariant="anti_happy_path_mandate">Minimum 4 ISTQB negative test cases for estimate_static_tokens as specified above.</constraint>
  </step>
</execution_protocol>
```

---

## 4. Verification Plan

### Automated Tests:
1. `uv run pytest backend_v2/tests/unit/llm/adapters/`
2. `uv run python scripts/backend_audit_loop.py backend_v2/llm/adapters/ --test`
3. `uv run python scripts/backend_audit_loop.py backend_v2/worker.py --test`
4. `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider.py --test`
5. `uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test`
6. `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/`

### Manual / Integration Verification:
1. Run a test execution trace and verify that `total_tokens`, `prompt_tokens`, `completion_tokens`, and `cost_estimate` appear in the Flutter dashboard card and status card.
2. Verify that blueprint SDUI rendering correctly displays token counts from metadata root.

---

## 5. Deferred Tech Debt (Out of Scope)

| Item | File | Rationale for Deferral |
|---|---|---|
| `hasattr`/`getattr` response parsing (10+ calls) | @[backend_v2/llm/provider.py] | LiteLLM 3rd-party boundary — response objects have inconsistent attributes across providers. Requires separate adapter-level refactor. |
| Typed Metadata DTO | @[backend_v2/services/blueprint.py] | Metadata is a raw NoSQL dict per `polymorphic_parsing_mandate`. Typed DTO would improve safety but is a larger cross-cutting refactor. |
