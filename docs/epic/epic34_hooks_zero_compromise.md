# Epic 34: Global Hooks Zero-Compromise Hardening

## 1. Description and Motivation
An audit of the dynamic execution hooks (`scoring.py`, `reporting.py`, `input_processing.py`, `atom_flattening.py`, and `context_mapper.py`) shows a clear dichotomy. While `atom_flattening.py` perfectly utilizes `TypeAdapter(Model).validate_python()`, the core reporting and scoring hooks are completely submerged in legacy "defensive programming" and massive dictionary-guessing algorithms.

**The Violations:**
- **`reporting.py` (The Silent Scavenger):** The report generator has no defined schema for what a `report_context` should look like. It simply hunts through `global_context_vars` using huge blocks of `isinstance(out, dict)` and `out.get("key", {})` to guess if an agent was present. If a field structure changes, it silently falls back to `None` or an empty list instead of leveraging strict Pydantic parsing.
- **`scoring.py` (Duck-Typed Key Matching):** The passivity penalty and normalization logic rely entirely on inspecting string prefixes (`if k.startswith("matrix_") and not k.endswith("_justification")`). Instead of having a structured `ExecutionTrace` input, scoring blindly loops over any float it finds in a dictionary. Furthermore, `normalize_matrix_scores_hook` flattens objects by manually mapping nested keys to root keys (e.g., `new_payload[f"{pb_id}_cited_text"] = raw["step_1_evidence"]`).
- **`input_processing.py` (Hardcoded Questionnaire Schema):** It natively guesses if input is a questionnaire bypassing Pydantic: `if isinstance(val, dict) and any(str(k).startswith("q"))`. It manually string-formats markdown `### Q:` based on magic prefixes.

**Objective:** Standardize all Hook payloads to Pydantic DTOs and destroy arbitrary dictionary-key sniffing, enforcing Fail-Fast architectural compliance.

## 2. Architectural Mandates Enforced (Rules Reference)
- **`the_zero_compromise_pledge` (`00-antigravity-core`):** Eradicate `.get(val, {})` chaining inside `reporting.py`. If data from `step_logician` is requested, it MUST be validated against `LogicianDTO`. If the type doesn't match, raise `AppException`.
- **`no_naked_dicts_in_state` (`01-python-backend`):** `HookState` currently sends `global_context_vars` as a `dict[str, Any]`. The Scoring and Reporting hooks should not dig into arbitrary contexts. The state schema needs to serialize outputs explicitly (e.g. `state.get_result(AgentRoles.OVERSEER)`).
- **`fail_fast` (`00-antigravity-core`):** Key sniffing (`k.startswith("matrix_")`) allows silent omissions if an ID prefix rule is accidentally changed. Pydantic schema declaration provides a compile-time and runtime guarantee.

## 3. Implementation Phases

### Phase 1: Cleansing `reporting.py` (Schema-First Templating)
- **Target:** `generate_report_hook`
- **Action:** Delete the scavenger hunting (`_get_agent_output`, `isinstance(overseer_out, dict)`).
- **Solution:** Introduce a `ReportSynthesisDTO` that requires strict typed classes for every supported specialist report (e.g. `PerformativityReport`, `LogicianReport`). The hook will do a single `ReportSynthesisDTO.model_validate(global_context_vars)` sweep. If successful, pass the DTO into Jinja2.

### Phase 2: Refactoring Scoring Key-Guessing
- **Target:** `enforce_passivity_penalty_hook` & `normalize_matrix_scores_hook` in `scoring.py`.
- **Action:** Replace `startswith("matrix_")` matching with strict Evaluation block fetching.
- **Solution:** Map the values through the explicit PromptBlock models directly (which already know what is a score and what is an evaluation) rather than doing string magic on the output keys.

### Phase 3: Formalizing Questionnaire Parsing
- **Target:** `input_processing.py`.
- **Action:** Remove the `isinstance(dict) and startswith("q")` markdown hack.
- **Solution:** Implement a `GuidedReflectionInputDTO(BaseModel)` with explicit `questions: list[QuestionAnswerPair]`. Let the model handle `.to_markdown()` serialization deterministically.

### Phase 4: Localization & Validation Metadata Sovereignty
- **Target:** `validation.py` & `translation_hook.py`.
- **Action:** Eradicate `.get("language")` and `.get("target_locale", "en")` fallbacks for state access.
- **Solution:** Define strict `HookStateMetadata` and `I18nStatePayload` Pydantic models. Both hooks must intercept `state.inputs` and `state.metadata` at the start of execution using `Model.model_validate()` and leverage `I18nText.resolve()` logic to achieve Fail-Fast parity with the hardened `synthesis.py` hook.

## 4. Testing & Verification Mandate (Synthesis.py Standard)

### Universal Synthesis.py Case Study Execution Standards
Every single code modification inside this Epic MUST strictly adhere to the exact same architectural rigor successfully pioneered in `backend_v2/hooks/synthesis.py`:
- **Eradicate God Blocks:** Destroy massive `try...except Exception:` blocks. If a function is wrapped in a catch-all that suppresses native `AppException` propagation or obscures the original HTTP status codes/`ErrorCodes`, blow it up immediately.
- **Pure Function Extraction:** Identify any deep dictionary mutation loops, arbitrary text compression, or O(N^2) search loops and aggressively rip them out into isolated, testable Pure Functions. Keep the main orchestrator as a simple, highly readable pipeline.
- **O(1) Map Pre-computation:** Nested iteration loops inside data pipelines must be replaced with O(1) pre-computed lookup dictionaries to resolve heavy schema references instantly.
- **Enum-Driven Configuration:** Replace arbitrary boolean toggles with strictly validated Pydantic Enums.
- **Zero-Compromise 100% Pytest Coverage:**
  - **Fail-Fast Safety Tests:** Write specific tests that feed missing or corrupted Pydantic metadata/locales to the orchestrator to verify that it immediately crashes with `400 Validation Error` or `404 Not Found` (Zero Graceful Degradation).
  - **Pure Function Isolation:** Every extracted helper function MUST have its own dedicated unit test validating corner cases without requiring Database or LLM mocks.
  - **Happy-Path Orchestrator Integration:** Use `MagicMock` and `PydanticModel.model_construct()` to bypass rigid instantiation overhead in the test suite, allowing the mock environment to simulate a flawless execution pipeline.
  - **Universal Quality Gate:** The refactored module MUST pass `ruff check`, `mypy`, and `pytest` with 0 warnings before being considered complete.

### Specific Epic 34 Testing Mandates
1. Use `uv run python scripts/backend_audit_loop.py backend_v2/hooks/reporting.py --test` specifically to verify missing specialists correctly trigger a null-value in the DTO instead of a silent `KeyError` or dictionary iteration failure.
2. Monitor the active Flutter Execution Trace UI. Ensure that refactoring the key logic in `scoring.py` does not break the XAI extension visibility for `_justification` and `_cited_source_id`.
3. Verify that `translation_hook.py` drops gracefully into `AppException` if the `target_locale` is absent, rather than defaulting to English without explicit architectural consent.
