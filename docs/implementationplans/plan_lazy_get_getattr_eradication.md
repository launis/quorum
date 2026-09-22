# Implementation Plan: Eradication of Lazy `.get()` and `getattr()` Calls

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

<anti_targets>
- Do NOT use regex, substring searches, or heuristic string matching for AST validation.
- Do NOT swallow exceptions or return empty default dictionaries `{}` or fallback values `or ""` (`the_duct_tape_ban`).
- Do NOT use dynamic reflection (`getattr`, `hasattr`, `setattr`, `vars`, `.__dict__`, `operator.attrgetter`) in domain services or tests (`the_zero_compromise_pledge`).
- Do NOT use naked dictionary `.get()` calls or fallback chains in domain models, DTOs, or service pipelines (`zero_service_layer_fallbacks`).
- Do NOT suppress AST guardrail violations with `# noqa: QGR` in domain code.
- Do NOT allow CLI options (e.g. `--strict`) to be parsed as target paths in audit scripts.
- Do NOT use `write_to_file` to overwrite existing files when `multi_replace_file_content` is available.
- Do NOT hardcode provider models or reflection lookups in LLM adapters.
</anti_targets>

## Goal Description
Eradicate all lazy dictionary `.get("key", default)` lookups and dynamic reflection `getattr(obj, "field", None)` calls across `backend_v2` domain code, replacing them with explicit Pydantic V2 field access (`model.field`), positive membership guards (`key in dict`), or Fail-Fast `AppException` validation. Establish a strict Anti-Corruption Layer (ACL) for external untyped structures (specifically and exhaustively: PyMuPDF `fitz` page drawings and LiteLLM model info), eliminate reflective assertions in test suites, and update the AST Guardrail Engine (`_ast_guardrails.py` and `audit_dict_eradication.py`) so that `QGR001` and `QGR002` violations are permanently certified at zero across all domain modules.

---

## User Review Required

> [!IMPORTANT]
> **External Library Boundaries (PyMuPDF & LiteLLM):**  
> External libraries (specifically and exhaustively: PyMuPDF `fitz` page drawings and LiteLLM `get_model_info`) return raw C-extension or untyped dictionary structures. We establish explicit positive key guards (`key in dict`) and direct subscription (`dict[key]`) rather than allowing naked dictionary `.get()` calls or dynamic reflection to proliferate in domain logic.

> [!WARNING]
> **Fail-Fast Behavior Shift in Validators & Services:**  
> Specifically, if a required key (`source_id` in `quote_evidence.py` or `tda_id` in `matrix_sensor_prompt_builder.py`) is missing or malformed, `.get()` previously returned silent `None` or an empty dictionary fallback. With this change, missing required fields immediately raise an explicit `ValidationError` or `AppException(ErrorCodes.VALIDATION_FAILED, status_code=422)`.

---

## Touched Scope Technical Debt & Anti-Pattern Sweep

An exhaustive AST and ripgrep scan of `backend_v2` identified 47 fatal `QGR002` violations in domain code across 15 files, 134 `QGR001` reflection occurrences (specifically and exhaustively: 72 test `getattr()` reflection calls in test assertions and 62 AST guardrail inspection lines), and multiple CLI and visitor gaps in audit scripts.

### Discovered Technical Debt & 1-Hop Caller Blast Radius:
1. **`models/dtos/quote_evidence.py#L57-L106`, `#L129-L202`**: 7 `.get()` calls in `@model_validator(mode="before")` methods (`resolve_source_id` and `resolve_and_verify_aliases`), including lazy fallback dictionary parsing `info.context.get("alias_map") or {}` and `registry.get(alias)`.
   - *1-Hop Callers:* `services/orchestrator/services/extractive_sensor_service.py`, `services/orchestrator/services/anchor_validation_service.py`, `backend_v2/tests/unit/models/dtos/test_quote_evidence.py`.
2. **`models/domain/mechanical_anchors.py#L35-L130`**: 13 `.get()` calls in `from_context` with chained lazy fallbacks (`source.get("performative_patterns") or source.get("performative_phrases")`) and redundant fallback chains between `source` and `raw_inputs`.
   - *1-Hop Callers:* `services/orchestrator/strategies/llm_execution/prompt_factory.py`, `backend_v2/tests/unit/models/domain/test_mechanical_anchors.py`.
3. **`models/dtos/evaluation_steps.py#L32-L75`**: 2 `.get()` calls in `_sanitize_source_aliases` checking `d.get(list_field)` and `cls.model_fields.get(list_field)`.
   - *1-Hop Callers:* `services/orchestrator/prompts/matrix_sensor_prompt_builder.py`, `backend_v2/tests/unit/models/dtos/test_evaluation_steps.py`.
4. **`services/ingress/pdf_chat_extractor.py#L56-L103`, `#L179-L194`, `#L328-L358`**: 5 `.get()` calls on raw PyMuPDF drawing dictionaries (`d.get("rect")`, `d.get("fill")`, `d.get("color")`).
   - *1-Hop Callers:* `services/ingress/multi_channel_ingress_service.py`, `backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py`.
5. **`services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L84-L275` (specifically `#L140-L165`)**: 1 `.get()` call on `matrix_assertions_map.get(tda_id)` returning silent `None` instead of raising Fail-Fast `AppException`.
   - *1-Hop Callers:* `services/orchestrator/services/enriched_dag_executor.py`, `backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py`.
6. **`llm/adapters/openai_adapter.py#L107-L149`, `#L189-L220`**: 3 `.get()` calls on LiteLLM model info dictionary and JSON schema nodes.
   - *1-Hop Callers:* `llm/provider.py`, `backend_v2/tests/unit/llm/adapters/test_openai_adapter.py`.
7. **`llm/adapters/anthropic_adapter.py#L177-L212`**: 1 `.get()` call on `call_kwargs.get("model")`.
   - *1-Hop Callers:* `llm/provider.py`, `backend_v2/tests/unit/llm/adapters/test_anthropic_adapter.py`.
8. **`llm/adapters/base_adapter.py#L354-L371`**: 1 `.get()` call on `node["discriminator"].get("propertyName")`.
   - *1-Hop Callers:* `llm/adapters/openai_adapter.py`, `llm/adapters/anthropic_adapter.py`, `llm/adapters/vertex_adapter.py`, `llm/adapters/ai_studio_adapter.py`.
9. **`llm/ingress_pipeline.py#L95-L214`**: 3 `.get()` calls on candidate models and discriminator tags.
   - *1-Hop Callers:* `llm/client.py`, `backend_v2/tests/unit/llm/test_ingress_pipeline.py`.
10. **`llm/client.py#L261-L593` (specifically `#L530-L555`)**: 1 `.get()` call on `schema_err.details.get("error_code")`.
    - *1-Hop Callers:* `services/llm_task_executor.py`, `backend_v2/tests/unit/llm/test_client.py`.
11. **`llm/mock.py#L53-L85` (specifically `#L68-L75`)**: 1 `.get()` call on raw schema dictionary title in mock service.
    - *1-Hop Callers:* `backend_v2/tests/conftest.py`, unit test suites utilizing mock LLM.
12. **`services/auth.py#L268-L373` (specifically `#L280-L345`)**: 2 `.get()` calls on JWT claims and Firebase decoded token.
    - *1-Hop Callers:* `api/deps.py`, `backend_v2/tests/unit/test_auth.py`.
13. **`main.py#L61-L115`**: 2 `.get()` calls in `_audit_storage_and_database_sync` on TinyDB records.
    - *1-Hop Callers:* FastAPI application lifespan context in `main.py`.
14. **`api/routers/execution/reports.py#L194-L212`, `#L466-L508`**: 2 false-positive QGR002 detections on FastAPI APIRouter subrouter `.get()` decorators (`@execution_reports_subrouter.get`, `@external_router.get`).
15. **`database/wrapper.py#L264-L275`, `#L541-L544`**: 2 `.get()` calls in database driver wrapper (`res = self._get_table(db).get(query)`, `self.get(query)`).
16. **`services/cache/typed_cache.py#L30-L60` (specifically `#L43`)**: 1 `.get()` call on async Redis client (`await self.redis.get(key)`); false-positive detection in AST visitor.
17. **`backend_v2/tests/` (Test Suite Reflection)**: 72 test `getattr()` and `hasattr()` reflection calls in test assertions (specifically and exhaustively in `test_worker_models_used.py#L90`, `test_epic_chain_e2e.py#L204`, `#L253`, `test_caching_schema_scrub_bug.py#L54`, `test_structured_retry.py#L96`, `test_llm_task_executor.py#L151`, `test_litellm_redis_timeout.py#L54`, `#L56`, `test_epic66_multi_provider.py#L157`, `#L166`, `test_prompt_compiler.py#L233`).
18. **`scripts/_ast_guardrails.py#L83-L91`, `#L337-L672`**: Update AST guardrail visitor logic to recognize FastAPI router decorators, Redis client calls, and database wrapper methods.
19. **`scripts/audit_dict_eradication.py#L35-L40`, `#L119-L135`, `#L205-L218`, `#L389-L496`, `#L603-L734`**: Fix CLI argument parsing where `--strict` is treated as a target file path, synchronize receiver exclusion logic with `_ast_guardrails.py`, and expand domain scanning scope to include `llm/` and root `main.py`.

---

## Red-Team Falsification & Blast Radius Analysis

### Concrete Failure Points & Mitigations:

1. **Failure Point 1: CLI Argument Parsing Bug in `audit_dict_eradication.py` (False-Positive Clean Audit)**
   - *Attack Vector:* Running `uv run python scripts/audit_dict_eradication.py --strict` treats `--strict` as a target file path. Because `Path('--strict').exists()` evaluates to `False`, the script processes 0 files and exits with code 0 (`[PASSED] 100% Mathematical Zero Violations across all metrics.`), allowing regressions to evade CI quality gates.
   - *Mitigation:* Explicitly filter CLI option flags (`flags = {"--strict", "--ast-strict"}`) from target arguments; default to `backend_v2` if target list is empty; fail-fast with `FileNotFoundError` or exit code 1 if a requested path does not exist on disk.

2. **Failure Point 2: Missing Validation Context in Pydantic V2 `@model_validator(mode="before")`**
   - *Attack Vector:* Replacing `info.context.get("alias_map") or {}` with direct subscript `info.context["alias_map"]` will raise `TypeError: 'NoneType' object is not subscriptable` when models are instantiated in unit tests or CLI utilities without context injection.
   - *Mitigation:* Enforce positive context guard: `alias_map = info.context["alias_map"] if (info.context is not None and "alias_map" in info.context) else {}`. Guard against empty context deterministically without using `.get()` or naked duck-typing (`isinstance(info.context, dict)`).

3. **Failure Point 3: Silent Atom Omission in `matrix_sensor_prompt_builder.py`**
   - *Attack Vector:* Previously, `matrix_assertions_map.get(tda_id)` returned `None`, which then silently bypassed validation inside `if assertion:`. If a DAG node referenced an unmapped atom, the prompt compiler generated an empty assertion block, causing prompt leakage and model hallucination.
   - *Mitigation:* Enforce Fail-Fast validation:
     ```python
     if tda_id not in matrix_assertions_map:
         raise AppException(
             message=f"Missing matrix assertion for atom '{tda_id}'",
             status_code=400,
             details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "tda_id": tda_id},
         )
     assertion = matrix_assertions_map[tda_id]
     ```

4. **Failure Point 4: Outdated SDUI Architecture Assertions in `test_epic_chain_e2e.py`**
   - *Attack Vector:* In `test_epic_95_na_cascade_e2e`, the assertion previously checked `s for s in view.sections if getattr(s.type, "value", s.type) == "MARKDOWN_BLOCK"`. However, in the Dumb Painter SDUI architecture (EPIC 110/111), `ReportView` no longer contains `sections`; it contains a flat polymorphic `inner_sdui_blocks: list[AnySduiBlock]`, and `SduiNACard` is appended directly to `inner_sdui_blocks`.
   - *Mitigation:* Modernize the test assertion to directly inspect `view.inner_sdui_blocks`:
     ```python
     na_card = next(
         (b for b in view.inner_sdui_blocks if isinstance(b, SduiNACard)),
         None,
     )
     assert na_card is not None, "N/A outcomes block missing from inner_sdui_blocks"
     assert tda_id in na_card.short_circuit_reason_tda_ids
     assert "Ohitettu säännön perusteella: This is the NA reason claim" in na_card.message
     ```

5. **Failure Point 5: Scope Blindness & Missing AST Checks in `audit_dict_eradication.py` (Unchecked Domain Files)**
   - *Attack Vector:* `audit_dict_eradication.py` defined `is_domain_or_service` using a hardcoded 7-part tuple `("services", "models", "hooks", "orchestrator", "api", "database", "workers")`. This completely bypassed `backend_v2/llm/` (including `client.py`, `ingress_pipeline.py`, `mock.py`, and `adapters/`), `backend_v2/core/`, `backend_v2/utils/`, `backend_v2/seed/`, and `backend_v2/main.py`. As a result, banned `.get()` calls (such as `rec.get("id")` and `rec.get("execution_trace_storage_path")` in `main.py#L81`, `#L86`, or `schema_err.details.get("error_code")` in `llm/client.py#L545`) were never checked by `audit_dict_eradication.py`. Furthermore, tests were completely skipped (`not self.is_test`), omitting all 72 test `getattr()` reflection calls, and dynamic `.__dict__`, `attrgetter`, and `object.__setattr__` AST nodes were completely unmonitored.
   - *Mitigation:* Redefine `is_domain_or_service` universally as all files under `backend_v2` excluding `tests` and files starting with `test_`. Track reflection calls across test suites under `--strict`. Add `visit_Attribute` checking `.__dict__`, `operator.attrgetter`, and `object.__setattr__` to `DictEradicationVisitor`. Synchronize `LOCKED_PHYSICAL_DRIVERS` and receiver exclusions for `*_router`, `*_subrouter`, `redis`, and `_get_table`.

---

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`models/dtos/quote_evidence.py#L57-L106`, `#L129-L202`** | Banned `d.get("source_id")`, `info.context.get("alias_map") or {}`, and `registry.get(alias)`. | Enforce positive membership `if "source_id" in d:`, positive key lookup on `info.context`, and `alias in registry`. | Direct dictionary subscription after positive guard without reflection. | `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/quote_evidence.py --test` |
| **`models/domain/mechanical_anchors.py#L35-L130`** | Banned 13 loose `.get()` calls and `dict[str, Any]` naked dict signature in `from_context`. | Enforce positive dictionary checks: `key in source`, direct subscription `source[key]`, typed `PerformativePattern` construction, and accept `LLMContextDataDTO`. | Prune chained `or` fallbacks (`performative_patterns or performative_phrases`); prioritize authoritative field. | `uv run pytest backend_v2/tests/unit/models/domain/test_mechanical_anchors.py` |
| **`services/orchestrator/strategies/llm_execution/prompt_factory.py#L120-L135`** | Banned `llm_context_data.model_dump(mode="json")` intermediate double-serialization. | Pass `llm_context_data: LLMContextDataDTO` directly into `MechanicalAnchorsPayload.from_context`. | Eliminate temporary dictionary conversion before domain anchor compilation. | Prompt factory unit tests in `test_prompt_factory.py`. |
| **`models/dtos/evaluation_steps.py#L32-L75`** | Banned `d.get(list_field)` and `cls.model_fields.get(list_field)`. | Enforce positive membership checks: `if list_field in d:` and `if list_field in cls.model_fields:`. | Direct dictionary subscripting `cls.model_fields[list_field]`. | `uv run pytest backend_v2/tests/unit/models/dtos/test_evaluation_steps.py` |
| **`services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L84-L275` (specifically `#L140-L165`)** | Banned `matrix_assertions_map.get(tda_id)` returning silent `None`. | Enforce positive membership check: `if tda_id not in matrix_assertions_map: raise AppException(...)` and direct indexing. | Direct key lookup `matrix_assertions_map[tda_id]` without intermediate fallback variables. | ISTQB test verifying `AppException(ErrorCodes.VALIDATION_FAILED)` on missing atom. |
| **`services/ingress/pdf_chat_extractor.py#L56-L103`, `#L179-L194`, `#L328-L358`** | Banned raw dictionary `.get()` on PyMuPDF drawing dictionaries (`d.get("rect")`, `d.get("fill")`, `d.get("color")`). | Enforce positive key membership `if "rect" in d:` and direct indexing `d["rect"]`. | Avoid creating complex wrapper DTOs for simple C-extension dictionary checks. | `uv run pytest backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py` |
| **`llm/adapters/*.py` (OpenAI `#L107-L149`, `#L189-L220`; Anthropic `#L177-L212`; Base `#L354-L371`)** | Banned `info.get(...)`, `call_kwargs.get("model")`, and `node["discriminator"].get(...)`. | Enforce positive membership checks: `"supported_openai_params" in info`, `"model" in call_kwargs`, `"propertyName" in node["discriminator"]`. | Direct dictionary subscripting after positive guard without reflection. | Unit tests in `backend_v2/tests/unit/llm/adapters/`. |
| **`llm/ingress_pipeline.py#L95-L214`** | Banned `item.get(discriminator_field)` and `model.model_fields.get(...)`. | Explicit positive key check: `if discriminator_field in item: current_tag = item[discriminator_field]`. | Direct dictionary subscripting after positive guard. | `uv run pytest backend_v2/tests/unit/llm/test_ingress_pipeline.py` |
| **`llm/client.py#L261-L593` (specifically `#L530-L555`)** | Banned `schema_err.details.get("error_code")` on `AppException`. | Explicit key check: `schema_err.details and "error_code" in schema_err.details and schema_err.details["error_code"] == ...`. | Direct subscript `schema_err.details["error_code"]`. | `uv run pytest backend_v2/tests/unit/llm/test_client.py` |
| **`llm/mock.py#L53-L85` (specifically `#L68-L75`)** | Banned `response_schema.get("title")` on schema dictionary. | Positive membership check `if "title" in response_schema: title = response_schema["title"]`. | Direct subscription without redundant `.get()`. | `uv run pytest backend_v2/tests/unit/test_mock_llm.py` |
| **`services/auth.py#L268-L373` (specifically `#L280-L345`)** | Banned `payload.get("sub")` and `decoded_token.get("email")`. | Enforce `if "sub" not in payload: raise ...` and direct subscription `payload["sub"]`. | Direct subscription on verified JWT payload. | `uv run pytest backend_v2/tests/unit/test_auth.py` |
| **`backend_v2/main.py#L61-L115`** | Banned `rec.get("id")` and `rec.get("execution_trace_storage_path")` on TinyDB records. | Positive key membership `if "id" in rec:` and direct subscription `rec["id"]`. | Direct subscription without redundant `.get()`. | Startup self-audit test in `backend_v2/tests/unit/test_main.py`. |
| **`backend_v2/tests/` (Test Suite Reflection: `worker_models_used#L85-L97`, `epic_chain_e2e#L200-L265`, `caching_schema_scrub#L50-L60`, `structured_retry#L95-L100`, `llm_task_executor#L145-L155`, `litellm_redis_timeout#L54-L57`, `epic66_multi_provider#L155-L167`, `prompt_compiler#L230-L236`)** | Banned defensive `getattr(obj, "field", default)` calls across test assertions. | Direct dot-notation attribute access: `assert obj.field == expected` and `typing.get_args()`. | Prune defensive reflection; let tests fail fast with `AttributeError` if schema changes. | `uv run pytest backend_v2/tests/` running with strict AST guardrails. |
| **`scripts/_ast_guardrails.py#L83-L91`, `#L337-L672`** | False positive QGR002 triggers on FastAPI subrouters, Redis cache calls, and database wrapper. | Add `wrapper.py` to boundary exemptions; add `execution_reports_subrouter`, `external_router`, `redis`, `redis_client`, and suffix patterns (`*_router`, `*_subrouter`, `*_client`) to receiver exemptions. | Pure AST matching without dynamic reflection or string regex parsing. | `uv run python scripts/_ast_guardrails.py backend_v2`. |
| **`scripts/audit_dict_eradication.py#L35-L40`, `#L119-L135`, `#L205-L218`, `#L389-L496`, `#L603-L734`** | CLI argument bug treating `--strict` as a non-existent path; scope blindness excluding `llm/`, `core/`, `utils/`, `main.py`; missing `.__dict__`, `attrgetter`, and `object.__setattr__` checks. | Filter CLI flags from target arguments; validate target existence fail-fast; expand `is_domain_or_service` to all non-test `backend_v2` files; add `visit_Attribute` and full reflection visitors. | Clean standard sys.argv filtering and complete AST coverage without custom bloat. | `uv run python scripts/audit_dict_eradication.py --strict` executes scan on `backend_v2` and reflects real violation counts. |
| **`@[ki_zero_permissive_typing.md]`** | Banned stale 4-file boundary contract, missing QGR002 FastAPI/Redis receiver exemptions, undocumented external C-extension raw dict handling, duplicate rule blocks, and missing canonical patterns for ValidationInfo context, model_fields, falsy `or` guards, and test mock typing. | Update SSOT to 8 locked driver files, codify router/Redis exemptions, formalize positive ACL subscription (`key in dict`), consolidate duplicate blocks, and codify 4 canonical patterns (ValidationInfo context extraction, `cls.model_fields` membership, explicit `is not None` vs falsy `or` corruption, and test mock typing). | Zero speculative additions; purely synchronize with physical as-built contracts. | Verification against as-built codebase asserting zero rule conflicts. |

---

## Proposed Changes

Grouped by component layer:

---

### Phase 1: Knowledge Item SSOT Synchronization, Pre-Implementation Cleanups & AST Guardrail Calibration

#### [MODIFY] [ki_zero_permissive_typing.md](file:///c:/Users/risto/.gemini/antigravity-ide/knowledge/zero_permissive_typing/artifacts/ki_zero_permissive_typing.md)
- Modernize and clean `ki_zero_permissive_typing.md` to establish universal authority across the entire codebase from day one:
  - In `<rule_block id="zero_naked_dicts_and_permissive_typing">`: Remove historical changelog anecdotes (such as *"As proven by WorkflowSchemaResponseDTO which eradicated legacy..."*); formulate the mandate as a 100% universal invariant applying to all domain, service, orchestrator, controller, and hook layers.
  - In `<rule_block id="ast_guardrail_fatal_severity_mandate">`:
    - Update `BOUNDARY_EXEMPTION_FILES` contract from 4 to 8 locked physical driver files:
      `{"tinydb_driver.py", "firestore_driver.py", "provider.py", "logging_config.py", "vertex_adapter.py", "ai_studio_adapter.py", "handler.py", "wrapper.py"}`.
    - Formalize QGR002 receiver exemptions for FastAPI routers and subrouters (`*_router`, `*_subrouter` such as `@execution_reports_subrouter.get`, `@external_router.get`), Redis clients (`redis`, `redis_client`, `*_client`), and database table pointer resolvers (`_get_table`).
  - In `<rule_block id="pure_dot_notation_and_anti_reflection">`:
    - Codify the Anti-Corruption Layer (ACL) standard for untyped external structures (PyMuPDF `fitz` page drawings, LiteLLM `get_model_info`): positive key verification (`key in raw_dict`) followed by direct subscription (`raw_dict[key]`) without `.get()` fallback chains.
    - Mandate direct attribute access in test assertions (`assert obj.field == expected`), eradicating defensive `getattr()` reflection from test suites.
    - **Codify 4 Canonical Replacement Patterns:**
      1. **ValidationInfo Context Extraction Pattern**: In Pydantic validators (`@model_validator`, `@field_validator`), extracting values from `info.context` must never use `info.context.get(...)` (violates QGR002) or `info.context.get(...) or {}` (violates duct-tape ban). Mandate:
         ```python
         context_val = info.context["key"] if (info.context is not None and "key" in info.context) else default
         ```
         or Fail-Fast if required:
         ```python
         if info.context is None or "key" not in info.context:
             raise ValueError("Missing required validation context: 'key'")
         context_val = info.context["key"]
         ```
      2. **Pydantic `cls.model_fields` Membership Pattern**: When inspecting model fields on Pydantic classes, never use `cls.model_fields.get(name)`. Mandate positive membership guard:
         ```python
         field_info = cls.model_fields[name] if name in cls.model_fields else None
         ```
      3. **Explicit `is not None` Guard vs. Falsy `or` Corruption**: Strictly ban replacing `.get(key, default)` with `d[key] or default` or `(d[key] if key in d else None) or default`, because valid falsy domain values (`0`, `0.0`, `""`, `False`) are corruptively clobbered by the default. Mandate:
         ```python
         val = d[key] if (key in d and d[key] is not None) else default
         ```
      4. **Test Mock Typing & Direct Attribute Assertions**: In unit and integration test fixtures, require mock return values to be typed Pydantic DTO instances or explicitly configured objects. Ban `getattr(mock_obj, "field", None)` in test assertions; mandate `assert obj.field == expected` so that schema deviations fail fast with `AttributeError` rather than silently passing.
  - In `<rule_block id="ban_anonymous_state_tuples">`: Remove file-specific historical commentary (`atom_flattening.py` lines); frame the ban as an immutable SSOT law across all pipeline intermediate payloads.
  - In `<rule_block id="primitive_obsession_and_nested_collection_eradication">`:
    - Consolidate duplicate blocks into a single authoritative SSOT definition.
    - Document `audit_dict_eradication.py` CLI `--strict` protocol scanning all non-test `backend_v2` modules (including `llm/`, `core/`, `utils/`, and root `main.py`).

#### [MODIFY] [scripts/_ast_guardrails.py#L83-L91](file:///c:/src/quorum/scripts/_ast_guardrails.py#L83-L91)
- Synchronize `BOUNDARY_EXEMPTION_FILES` to keep low-level physical I/O drivers cleanly quarantined by appending `"wrapper.py"`:
  ```python
  BOUNDARY_EXEMPTION_FILES: set[str] = {
      "tinydb_driver.py",
      "firestore_driver.py",
      "provider.py",
      "logging_config.py",
      "vertex_adapter.py",
      "ai_studio_adapter.py",
      "handler.py",
      "wrapper.py",
  }
  ```

#### [MODIFY] [scripts/_ast_guardrails.py#L337-L672](file:///c:/src/quorum/scripts/_ast_guardrails.py#L337-L672)
- In `visit_Call`, update QGR002 receiver exclusion to exempt FastAPI APIRouters and subrouters (`execution_reports_subrouter`, `external_router`), Redis clients (`self.redis`, `redis_client`), and database wrapper methods (`_get_table(db)`):
  ```python
  # Match receiver AST nodes
  match receiver:
      case ast.Attribute(value=ast.Name(id="os"), attr="environ") | ast.Name(id="environ"):
          exempt = True
      case ast.Attribute(attr="headers") | ast.Name(id="headers"):
          exempt = True
      case ast.Name(id=name) if (
          name in {
              "client", "http", "requests", "session", "httpx", "driver", "router", "app",
              "redis", "redis_client", "_LABEL_MAP", "LABEL_MAP", "_VALUE_MAP", "_NAME_MAP",
              "_L10N_MAP", "L10N_MAP",
          }
          or name.endswith(("_router", "_subrouter", "_client"))
      ):
          exempt = True
      case ast.Attribute(attr=attr_name) if (
          attr_name in {
              "client", "http", "requests", "session", "httpx", "driver", "router", "app",
              "redis", "redis_client", "_LABEL_MAP", "LABEL_MAP", "_VALUE_MAP", "_NAME_MAP",
              "_L10N_MAP", "L10N_MAP",
          }
          or attr_name.endswith(("_router", "_subrouter", "_client"))
      ):
          exempt = True
      case ast.Call(func=ast.Name(id="_get_table")):
          exempt = True
      case _:
          exempt = False
  ```

#### [MODIFY] [scripts/audit_dict_eradication.py#L35-L40](file:///c:/src/quorum/scripts/audit_dict_eradication.py#L35-L40)
- Synchronize `LOCKED_PHYSICAL_DRIVERS` constants with `_ast_guardrails.py` by adding `"vertex_adapter.py"`, `"ai_studio_adapter.py"`, `"handler.py"`, and `"wrapper.py"`:
  ```python
  LOCKED_PHYSICAL_DRIVERS: set[str] = {
      "tinydb_driver.py",
      "firestore_driver.py",
      "provider.py",
      "logging_config.py",
      "vertex_adapter.py",
      "ai_studio_adapter.py",
      "handler.py",
      "wrapper.py",
  }
  ```

#### [MODIFY] [scripts/audit_dict_eradication.py#L119-L135](file:///c:/src/quorum/scripts/audit_dict_eradication.py#L119-L135)
- In `DictEradicationVisitor.__init__`, eliminate domain scope blindness by replacing the 7-part tuple check with universal non-test `backend_v2` path inclusion:
  ```python
  path_parts = set(Path(filepath).parts)
  self.is_test = "tests" in path_parts or Path(filepath).name.startswith("test_")
  self.is_domain_or_service = not self.is_test and not (
      "scripts" in path_parts or "migrations" in path_parts
  )
  ```

#### [MODIFY] [scripts/audit_dict_eradication.py#L205-L218](file:///c:/src/quorum/scripts/audit_dict_eradication.py#L205-L218)
- Add `visit_Attribute` method to `DictEradicationVisitor` to detect `.__dict__` access:
  ```python
  def visit_Attribute(self, node: ast.Attribute) -> None:
      """Inspects dynamic reflection attribute access like .__dict__."""
      if not self.is_exempt and self.is_domain_or_service:
          if node.attr == "__dict__":
              self.violations.append(
                  AuditViolation(
                      filepath=self.filepath,
                      line=node.lineno,
                      metric="reflection_calls",
                      message=f"Banned dynamic `.__dict__` access: `{ast.unparse(node)}`",
                  )
              )
      self.generic_visit(node)
  ```

#### [MODIFY] [scripts/audit_dict_eradication.py#L389-L496](file:///c:/src/quorum/scripts/audit_dict_eradication.py#L389-L496)
- In `visit_Call`, expand dynamic reflection detection to catch `operator.attrgetter` and `object.__setattr__`:
  ```python
  # Dynamic reflection checks
  match node.func:
      case ast.Name(id="getattr" | "hasattr" | "setattr" | "vars"):
          self.violations.append(
              AuditViolation(
                  filepath=self.filepath,
                  line=node.lineno,
                  metric="reflection_calls",
                  message=f"Banned dynamic reflection call `{node.func.id}`: `{ast.unparse(node)}`",
              )
          )
      case ast.Name(id="attrgetter") | ast.Attribute(value=ast.Name(id="operator"), attr="attrgetter"):
          self.violations.append(
              AuditViolation(
                  filepath=self.filepath,
                  line=node.lineno,
                  metric="reflection_calls",
                  message=f"Banned dynamic `operator.attrgetter` reflection call: `{ast.unparse(node)}`",
              )
          )
      case ast.Attribute(value=ast.Name(id="object"), attr="__setattr__"):
          self.violations.append(
              AuditViolation(
                  filepath=self.filepath,
                  line=node.lineno,
                  metric="reflection_calls",
                  message=f"Banned dynamic `object.__setattr__` reflection call: `{ast.unparse(node)}`",
              )
          )
      case _:
          pass
  ```
- Track reflection calls across test files: when `self.is_test` is True, append discovered `getattr/hasattr/setattr` calls to `reflection_calls` when run with strict audit mode.
- Synchronize receiver exclusion logic in `DictEradicationVisitor.visit_Call` with `_ast_guardrails.py` for `*_router`, `*_subrouter`, `*_client`, `redis`, `redis_client`, `app`, and `_get_table`.

#### [MODIFY] [scripts/audit_dict_eradication.py#L603-L734](file:///c:/src/quorum/scripts/audit_dict_eradication.py#L603-L734)
- Fix CLI argument parsing in `audit_dict_eradication` and `main`:
  ```python
  flags = {"--strict", "--ast-strict"}
  raw_args = argv if argv is not None else sys.argv[1:]
  filtered_args = [a for a in raw_args if a not in flags]
  target = filtered_args if filtered_args else ["backend_v2"]
  ```
- If a specified target path does not exist on disk, raise `FileNotFoundError` or exit with code 1 instead of returning an empty passing report:
  ```python
  for t in (targets if not isinstance(targets, (str, Path)) else [targets]):
      p = Path(t)
      if not p.exists():
          raise FileNotFoundError(f"Target path does not exist on disk: {p}")
  ```

---

### Phase 2: Models & DTO Validation Layer

#### [MODIFY] [backend_v2/models/dtos/quote_evidence.py#L57-L106](file:///c:/src/quorum/backend_v2/models/dtos/quote_evidence.py#L57-L106)
- In `resolve_source_id`:
  - Replace `d.get("source_id")` with `source_id = d["source_id"] if "source_id" in d else None`.
  - Replace `info.context.get(...)` with positive key membership checks:
    ```python
    alias_map = info.context["alias_map"] if (info.context is not None and "alias_map" in info.context) else {}
    allowed_dynamic_keys = info.context["allowed_dynamic_keys"] if (info.context is not None and "allowed_dynamic_keys" in info.context) else []
    allowed_mcp_prefixes = info.context["allowed_mcp_prefixes"] if (info.context is not None and "allowed_mcp_prefixes" in info.context) else []
    ```

#### [MODIFY] [backend_v2/models/dtos/quote_evidence.py#L129-L202](file:///c:/src/quorum/backend_v2/models/dtos/quote_evidence.py#L129-L202)
- In `resolve_and_verify_aliases`:
  - Replace `info.context.get("alias_registry")` with `info.context["alias_registry"] if (info.context is not None and "alias_registry" in info.context) else {}`.
  - Replace `d.get("source_alias")` with `d["source_alias"] if "source_alias" in d else None`.
  - Replace `registry.get(alias)` with `registry[alias] if (registry is not None and alias in registry) else None`.

#### [MODIFY] [backend_v2/models/domain/mechanical_anchors.py#L35-L130](file:///c:/src/quorum/backend_v2/models/domain/mechanical_anchors.py#L35-L130)
- In `from_context`:
  - Eliminate `dict[str, Any]` naked dict signature; accept `data: LLMContextDataDTO | None = None` (supporting typed extraction from `data.inputs` or `data.raw_inputs` directly).
  - Replace `data.get("raw_inputs")` with positive check: `raw_inputs = data["raw_inputs"] if (data is not None and "raw_inputs" in data) else None` (or typed attribute access `data.raw_inputs`).
  - Replace `.get()` calls for `word_count`, `say_do_gap`, `automation_bias`:
    ```python
    raw_wc = source["word_count"] if (source is not None and "word_count" in source) else None
    raw_sd = source["say_do_gap"] if (source is not None and "say_do_gap" in source) else None
    raw_ab = source["automation_bias"] if (source is not None and "automation_bias" in source) else None
    ```
  - Normalize performative patterns extraction without chained `or`:
    ```python
    raw_patterns = None
    if source is not None and "performative_patterns" in source:
        raw_patterns = source["performative_patterns"]
    elif source is not None and "performative_phrases" in source:
        raw_patterns = source["performative_phrases"]
    ```
  - In pattern parsing loop, replace `item.get("phrase")` and `item.get("pattern_id")` with positive key checks.

#### [MODIFY] [backend_v2/tests/unit/models/domain/test_mechanical_anchors.py#L1-L105](file:///c:/src/quorum/backend_v2/tests/unit/models/domain/test_mechanical_anchors.py#L1-L105)
- Modernize unit test fixtures in `test_mechanical_anchors.py`:
  - Update `test_mechanical_anchors_from_context_direct_keys` and `test_mechanical_anchors_from_context_nested_raw_inputs` to instantiate `MechanicalAnchorsPayload` and test `from_context` using `LLMContextDataDTO`, adhering to modern Pydantic V2 typed testing contracts.

#### [MODIFY] [backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L120-L135](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L120-L135)
- In `PromptFactory.build_prompt_payload`:
  - Eliminate intermediate double-serialization `llm_context_data.model_dump(mode="json")` before passing to `MechanicalAnchorsPayload.from_context`.
  - Pass `llm_context_data` directly:
    ```python
    if is_grounded_step:
        anchors_payload = MechanicalAnchorsPayload.from_context(llm_context_data)
        anchors_xml = anchors_payload.to_xml()
    ```

#### [MODIFY] [backend_v2/models/dtos/evaluation_steps.py#L32-L75](file:///c:/src/quorum/backend_v2/models/dtos/evaluation_steps.py#L32-L75)
- In `_sanitize_source_aliases`:
  - Replace `d.get(list_field)` with `raw_list = d[list_field] if list_field in d else None`.
  - Replace `cls.model_fields.get(list_field)` with `field_info = cls.model_fields[list_field] if list_field in cls.model_fields else None`.

---

### Phase 3: Orchestration & Prompt Compilation Layer

#### [MODIFY] [backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L84-L275](file:///c:/src/quorum/backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L84-L275)
- In `build_compiled_prompt` (lines 140-165):
  - Replace `matrix_assertions_map.get(tda_id)` with Fail-Fast positive verification:
    ```python
    if tda_id not in matrix_assertions_map:
        raise AppException(
            message=f"Missing matrix assertion for atom '{tda_id}'",
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "tda_id": tda_id},
        )
    assertion = matrix_assertions_map[tda_id]
    ```

---

### Phase 4: External Ingress & LLM Adapters Layer

#### [MODIFY] [backend_v2/services/ingress/pdf_chat_extractor.py#L56-L103](file:///c:/src/quorum/backend_v2/services/ingress/pdf_chat_extractor.py#L56-L103)
- In `_is_user_bubble_drawing`:
  - Replace `d.get("rect")` with `rect_obj = d["rect"] if "rect" in d else None`.
  - Replace `d.get("fill") is None and d.get("color") is None` with `("fill" not in d or d["fill"] is None) and ("color" not in d or d["color"] is None)`.

#### [MODIFY] [backend_v2/services/ingress/pdf_chat_extractor.py#L179-L194](file:///c:/src/quorum/backend_v2/services/ingress/pdf_chat_extractor.py#L179-L194)
- In `_extract_page_user_bubbles`:
  - Replace `d.get("rect")` with `r_obj = d["rect"] if "rect" in d else None`.

#### [MODIFY] [backend_v2/services/ingress/pdf_chat_extractor.py#L328-L358](file:///c:/src/quorum/backend_v2/services/ingress/pdf_chat_extractor.py#L328-L358)
- In `_detect_attachment_cards`:
  - Replace `d.get("rect")` with `rect_obj = d["rect"] if "rect" in d else None`.

#### [MODIFY] [backend_v2/llm/adapters/openai_adapter.py#L107-L149](file:///c:/src/quorum/backend_v2/llm/adapters/openai_adapter.py#L107-L149)
- In `prepare_kwargs`:
  - Replace `info.get("supported_openai_params")` with `raw_params = info["supported_openai_params"] if "supported_openai_params" in info else None`.
  - Replace `info.get("supports_reasoning")` with `supports_reasoning = bool(info["supports_reasoning"]) if "supports_reasoning" in info else False`.

#### [MODIFY] [backend_v2/llm/adapters/openai_adapter.py#L189-L220](file:///c:/src/quorum/backend_v2/llm/adapters/openai_adapter.py#L189-L220)
- In `_apply_strict_schema_invariants`:
  - Replace `node.get("type") == "object"` with `("type" in node and node["type"] == "object") or "properties" in node`.

#### [MODIFY] [backend_v2/llm/adapters/anthropic_adapter.py#L177-L212](file:///c:/src/quorum/backend_v2/llm/adapters/anthropic_adapter.py#L177-L212)
- In `prepare_kwargs`:
  - Replace `call_kwargs.get("model")` with `call_model = call_kwargs["model"] if "model" in call_kwargs else (config.model_name if isinstance(config, ModelProfile) else "")`.

#### [MODIFY] [backend_v2/llm/adapters/base_adapter.py#L354-L371](file:///c:/src/quorum/backend_v2/llm/adapters/base_adapter.py#L354-L371)
- In `_collect_discriminator_names`:
  - Replace `node["discriminator"].get("propertyName")` with:
    ```python
    prop_name = (
        node["discriminator"]["propertyName"]
        if "propertyName" in node["discriminator"]
        else None
    )
    ```

#### [MODIFY] [backend_v2/llm/ingress_pipeline.py#L95-L214](file:///c:/src/quorum/backend_v2/llm/ingress_pipeline.py#L95-L214)
- In `_infer_and_heal_discriminator`:
  - Replace `item.get(discriminator_field)` with `current_tag = item[discriminator_field] if discriminator_field in item else None`.
  - Replace `model.model_fields.get(discriminator_field)` with `f_info = model.model_fields[discriminator_field] if discriminator_field in model.model_fields else None`.
  - Replace `isinstance(item.get("items"), list)` with `isinstance(item["items"], list)`.

#### [MODIFY] [backend_v2/llm/client.py#L261-L593](file:///c:/src/quorum/backend_v2/llm/client.py#L261-L593)
- In `run_structured_task` (lines 530-555):
  - Replace `schema_err.details.get("error_code")` with:
    ```python
    (
        schema_err.details is not None
        and "error_code" in schema_err.details
        and schema_err.details["error_code"] == ErrorCodes.UPSTREAM_TIMEOUT.value
    )
    ```

#### [MODIFY] [backend_v2/llm/mock.py#L53-L85](file:///c:/src/quorum/backend_v2/llm/mock.py#L53-L85)
- In `generate` (lines 68-75):
  - Replace `response_schema.get("title")` with `title = response_schema["title"] if "title" in response_schema else None`.

---

### Phase 5: Core Services & Infrastructure

#### [MODIFY] [backend_v2/services/auth.py#L268-L373](file:///c:/src/quorum/backend_v2/services/auth.py#L268-L373)
- In `verify_token` (lines 280-345):
  - Replace `payload.get("sub")` with:
    ```python
    if "sub" not in payload or not payload["sub"]:
        raise AuthenticationError(
            message="Invalid internal token: missing 'sub'.", details={"error_code": "INVALID_TOKEN"}
        )
    id = payload["sub"]
    ```
  - Replace `decoded_token.get("email")` with `email = decoded_token["email"] if "email" in decoded_token else None`.

#### [MODIFY] [backend_v2/main.py#L61-L115](file:///c:/src/quorum/backend_v2/main.py#L61-L115)
- In `_audit_storage_and_database_sync`:
  - Replace `rec.get("id")` with `rec_id = rec["id"] if "id" in rec else None`.
  - Replace `rec.get("execution_trace_storage_path")` with `trace_path_raw = rec["execution_trace_storage_path"] if "execution_trace_storage_path" in rec else None`.

---

### Phase 6: Test Suite Modernization (Eradicating `getattr()` Reflection)

#### [MODIFY] [backend_v2/tests/test_worker_models_used.py#L10-L97](file:///c:/src/quorum/backend_v2/tests/test_worker_models_used.py#L10-L97)
- In `test_worker_preserves_models_used`:
  - Replace `getattr(update_payload, "models_used", None) or (update_payload.get("models_used") ...)` with direct attribute access:
    ```python
    models_used = update_payload.models_used
    ```

#### [MODIFY] [backend_v2/tests/integration/test_epic_chain_e2e.py#L20-L210](file:///c:/src/quorum/backend_v2/tests/integration/test_epic_chain_e2e.py#L20-L210)
- In `test_epic_93_e2e_golden_master`:
  - Replace `getattr(b, "block_type", "")` with `b.block_type`.

#### [MODIFY] [backend_v2/tests/integration/test_epic_chain_e2e.py#L211-L265](file:///c:/src/quorum/backend_v2/tests/integration/test_epic_chain_e2e.py#L211-L265)
- In `test_epic_95_na_cascade_e2e`:
  - Replace outdated `view.sections` and `getattr(s.type, "value", s.type)` with direct `view.inner_sdui_blocks` inspection matching Dumb Painter SDUI architecture:
    ```python
    na_card = next(
        (b for b in view.inner_sdui_blocks if isinstance(b, SduiNACard)),
        None,
    )
    assert na_card is not None, "N/A outcomes block missing from inner_sdui_blocks"
    assert tda_id in na_card.short_circuit_reason_tda_ids
    assert "Ohitettu säännön perusteella: This is the NA reason claim" in na_card.message
    ```

#### [MODIFY] [backend_v2/tests/test_caching_schema_scrub_bug.py#L14-L64](file:///c:/src/quorum/backend_v2/tests/test_caching_schema_scrub_bug.py#L14-L64)
- In `test_caching_schema_scrub_bug`:
  - Replace `getattr(msg, "role", None)` with direct property access `msg.role == "system"`.

#### [MODIFY] [backend_v2/tests/unit/llm/test_structured_retry.py#L53-L101](file:///c:/src/quorum/backend_v2/tests/unit/llm/test_structured_retry.py#L53-L101)
- In `test_run_structured_task_self_healing_success`:
  - Replace `assert getattr(result, "name", "") == "Fixed"` with `assert result.name == "Fixed"`.

#### [MODIFY] [backend_v2/tests/unit/test_llm_task_executor.py#L140-L175](file:///c:/src/quorum/backend_v2/tests/unit/test_llm_task_executor.py#L140-L175)
- In `test_execute_structured_task_logical_error_retry`:
  - Replace `if getattr(model, "value", None) == "bad logic":` with direct attribute check `if model.value == "bad logic":`.

#### [MODIFY] [backend_v2/tests/unit/services/test_llm_task_executor.py#L180-L215](file:///c:/src/quorum/backend_v2/tests/unit/services/test_llm_task_executor.py#L180-L215)
- In `test_execute_structured_task_logical_error_retry`:
  - Replace `if getattr(model, "value", None) == "bad logic":` with direct attribute check `if model.value == "bad logic":`.

#### [MODIFY] [backend_v2/tests/unit/test_litellm_redis_timeout.py#L50-L65](file:///c:/src/quorum/backend_v2/tests/unit/test_litellm_redis_timeout.py#L50-L65)
- In `test_litellm_redis_timeout`:
  - Replace defensive reflection `assert hasattr(provider.router, "cache")` and `assert getattr(provider.router.cache, "redis_cache", None) is None` with direct attribute assertions:
    ```python
    assert provider.router.cache.redis_cache is None
    ```

#### [MODIFY] [backend_v2/tests/unit/test_epic66_multi_provider.py#L150-L167](file:///c:/src/quorum/backend_v2/tests/unit/test_epic66_multi_provider.py#L150-L167)
- In `test_multi_provider_api_key_override`:
  - Replace `assert getattr(provider, "api_key", None) == "anthropic-key"` and `assert getattr(provider_litellm, "api_key", None) == "anthropic-key"` with direct attribute assertions:
    ```python
    assert provider.api_key == "anthropic-key"
    assert provider_litellm.api_key == "anthropic-key"
    ```

#### [MODIFY] [backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py#L225-L245](file:///c:/src/quorum/backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py#L225-L245)
- In `test_build_chunk_schema`:
  - Replace `getattr(records_field.annotation, "__args__", None)` with standard Python `typing.get_args`:
    ```python
    records_annotation_args = get_args(records_field.annotation)
    ```

---

### Phase 7: Codebase-Wide Verification & Quality Gates

1. Verify `scripts/_ast_guardrails.py backend_v2` emits 0 FATAL violations for QGR001 and QGR002.
2. Verify `scripts/audit_dict_eradication.py backend_v2` and `scripts/audit_dict_eradication.py --strict` pass with 100% mathematical zero violations across all 8 metrics.
3. Run targeted unit test suite and `backend_audit_loop.py`.

---

<dod_checklist>
- [ ] Phase 1: Synchronize `ki_zero_permissive_typing.md` to establish universal authority, remove historical file changelog anecdotes, lock 8 boundary files, codify QGR002 receiver exemptions, formalize external ACL positive key subscription standard, and codify 4 canonical patterns (ValidationInfo context extraction, `cls.model_fields` membership, explicit `is not None` vs falsy `or` corruption, test mock typing).
- [ ] Phase 1: `scripts/_ast_guardrails.py` exempts `wrapper.py`, subrouters, Redis clients, and database tables.
- [ ] Phase 1: `scripts/audit_dict_eradication.py` CLI handles `--strict` without error, includes all `backend_v2` domain files, and inspects reflection calls.
- [ ] Phase 2: All `.get()` calls in `quote_evidence.py`, `mechanical_anchors.py`, and `evaluation_steps.py` replaced with positive key membership guards and typed subscripting.
- [ ] Phase 3: `matrix_sensor_prompt_builder.py` raises `AppException` with `ErrorCodes.VALIDATION_FAILED` on missing atoms.
- [ ] Phase 4: `pdf_chat_extractor.py` and LLM adapters (`openai_adapter.py`, `anthropic_adapter.py`, `base_adapter.py`, `ingress_pipeline.py`, `client.py`, `mock.py`) eliminate naked `.get()`.
- [ ] Phase 5: `auth.py` and `main.py` eliminate `.get()` calls and enforce positive token and record verification.
- [ ] Phase 6: All `getattr()` reflection calls in targeted unit/integration tests replaced with direct typed property access.
- [ ] Phase 7: `uv run python scripts/_ast_guardrails.py backend_v2` emits 0 FATAL violations for QGR001 and QGR002.
- [ ] Phase 7: `uv run python scripts/audit_dict_eradication.py --strict` exits cleanly with 0 violations across all 8 metrics.
- [ ] Phase 7: Full `backend_audit_loop.py backend_v2 --test` passes 100%.
</dod_checklist>

<validation_gate>
  <action>Execute Knowledge Item Verification: Assert physical contracts and universal scope in `ki_zero_permissive_typing.md` match codebase reality.</action>
  <action>Execute Guardrails Audit: `uv run python scripts/_ast_guardrails.py backend_v2`</action>
  <action>Execute Dict Eradication Audit: `uv run python scripts/audit_dict_eradication.py --strict`</action>
  <action>Execute Targeted Unit Tests: `uv run pytest backend_v2/tests/unit/test_mechanical_anchors.py backend_v2/tests/unit/models/dtos/ backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py backend_v2/tests/unit/llm/adapters/ backend_v2/tests/unit/test_auth.py`</action>
  <action>Execute Full Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</action>
</validation_gate>

---

## Verification Plan

### Automated Tests
1. **Targeted Unit Tests:**
   ```powershell
   uv run pytest backend_v2/tests/unit/models/domain/test_mechanical_anchors.py
   uv run pytest backend_v2/tests/unit/models/dtos/
   uv run pytest backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py
   uv run pytest backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py
   uv run pytest backend_v2/tests/unit/llm/adapters/
   uv run pytest backend_v2/tests/unit/test_auth.py
   uv run pytest backend_v2/tests/unit/test_llm_task_executor.py
   uv run pytest backend_v2/tests/unit/services/test_llm_task_executor.py
   uv run pytest backend_v2/tests/unit/test_litellm_redis_timeout.py
   uv run pytest backend_v2/tests/unit/test_epic66_multi_provider.py
   uv run pytest backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py
   uv run pytest backend_v2/tests/test_worker_models_used.py
   uv run pytest backend_v2/tests/test_caching_schema_scrub_bug.py
   uv run pytest backend_v2/tests/integration/test_epic_chain_e2e.py
   ```
2. **AST Guardrail & Dict Eradication Audit:**
   ```powershell
   uv run python scripts/_ast_guardrails.py backend_v2
   uv run python scripts/audit_dict_eradication.py backend_v2
   uv run python scripts/audit_dict_eradication.py --strict
   ```
   *Expected Output: `--strict` scans `backend_v2` and exits cleanly with 0 violations once all phases are executed.*
3. **Comprehensive Backend Audit Loop:**
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2 --test
   ```
   *Enforces Ruff, MyPy Strict, and complete Pytest suite.*

### Manual Verification
- Verify that intentionally omitting a required field triggers an immediate HTTP 422 `VALIDATION_FAILED` rather than downstream silent `None` processing.
- Verify that running `uv run python scripts/audit_dict_eradication.py non_existent_path` exits with a non-zero error and does not output `[PASSED]`.
