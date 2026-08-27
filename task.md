# Task: Gemini 3.7 Flash Migration & Multi-Provider Parameter Normalization

- [x] **Phase 1: Pre-Implementation Cleanups & Schemas**
  - [x] Step 1.1: Eradicate untyped `additional_params.get("thinking_budget_tokens")` in `vertex_adapter.py` and `ai_studio_adapter.py`
  - [x] Step 1.2: Add `thinking_budget_tokens: int | None = Field(default=None)` to `ModelProfile` in `v2_core.py`
  - [x] Step 1.3: Add `thinkingBudgetTokens` to `LlmModelConfig` in `model_config.dart` and run build runner
- [x] **Phase 2: Adapter Parameter Sanitization & Normalization**
  - [x] Step 2.1: Update `VertexAdapter` and `AIStudioAdapter` parameter sanitization & thinking translation
  - [x] Step 2.2: Update `AnthropicAdapter` and `OpenAIAdapter` parameter normalizations
  - [x] Step 2.3: Relax provider `temperature is None` check for reasoning models in `provider.py`
  - [x] Step 2.4: Create unit tests in `test_adapter_parameter_sanitization.py` and verify quality gate
- [x] **Phase 3: Seed Data Vault Mutation**
  - [x] Step 3.1: Backup and mutate `seed_data.json` with `gemini-3.7-flash` and re-seed local database
- [x] **Phase 4: Frontend UI & Localization**
  - [x] Step 4.1: Update localization `.arb` files (`app_en.arb`, `app_fi.arb`) and run `flutter gen-l10n`
  - [x] Step 4.2: Update `model_registry_view.dart` with thinking budget controls and reasoning notices
  - [x] Step 4.3: Update and verify `model_registry_view_test.dart`
- [x] **Phase 5: Final Completion Gate**
  - [x] Step 5.1: Run full system audit loops (`backend_audit_loop.py` & `flutter_audit_loop.py`)
