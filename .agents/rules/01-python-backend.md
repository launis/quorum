# BACKEND ARCHITECTURE CONSTRAINTS

*** UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS FOR PYTHON ***

<domain_boundary>
    <role>RUNTIME & LOGIC ONLY</role>
    <instruction>These rules apply STRICTLY to Python (.py) execution logic, memory states, and Pydantic schemas. If you need to modify baseline JSON data or database configurations, you MUST halt and read `03_seed_vault.md` first.</instruction>
</domain_boundary>

<catastrophic_system_bans>
    <rule_block id="the_duct_tape_ban">
        <mandate>NEVER catch-all with `except Exception: pass`, return empty dicts `{}`, use `.get("key", default)`, or use lazy fallback operators (`or "en"`, `or {}`, `or []`). ALL errors MUST be caught, logged, and re-raised via `AppException`. Rely strictly on Pydantic validation (schema-level defaults) and Fail-Fast on missing required values.</mandate>
    </rule_block>
    
    <rule_block id="partial_mocking_srp_ban">
        <mandate>NEVER use "Partial Mocking" in unit tests by stuffing heavy orchestration or AI logic into private methods (e.g., `_execute_rag_preflight`) inside parent classes like `DAGExecutor`. ALWAYS follow Single Responsibility Principle (SRP): extract heavy sub-processes into isolated service classes (e.g., `RAGPreflightService`), inject via Dependency Injection, and mock the injected service class in tests.</mandate>
    </rule_block>

    <rule_block id="engine_override_ban">
        <mandate>NEVER rely on workflow-level override flags (e.g., `engine_override`) or hardcoded strategy aliases. ALWAYS enforce Eager Fetching and Dynamic Inference by reading the SSOT directly from the blueprint definition (e.g., `step_def.model_strategy`) to infer execution paths dynamically.</mandate>
    </rule_block>
    
    <rule_block id="prompt_fragmentation_ban">
        <mandate>NEVER scatter LLM prompt instructions, structural JSON mandates, or logic constraints in business methods or client wrappers (`client.py`). ALL global prompt instructions MUST be centralized in `directives.py` as explicit string constants (SSOT).</mandate>
    </rule_block>

    <rule_block id="docstring_fail_fast_ban">
        <mandate>NEVER write `Raises: None` in method docstrings or duplicate Python type hints (e.g. `type[BaseModel]:`) in `Args:`/`Returns:` text. ALWAYS explicitly list the exact `AppException` error codes the execution can trigger and enforce strictly DRY typing.</mandate>
    </rule_block>

    <rule_block id="inline_imports_ban">
        <mandate>NEVER use inline imports inside methods/functions to avoid circular dependencies. ALL standard imports MUST be declared globally at the top of the file. EXCEPTION: Heavy AI/ML libraries (`litellm`, `vertexai`, `spacy`) MUST be lazily imported inside methods/functions to prevent PyO3 initialization crashes and ensure Zero Cold Starts.</mandate>
    </rule_block>

    <rule_block id="slug_data_relation_ban">
        <mandate>NEVER use `slug`, UI labels, or informational fields as JSON schema keys, Pydantic field names, strict data relations, inside loggers (`logger.info/warning/error`), in exception messages, or for business logic conditionals (`if b.slug == ...`). ALWAYS use canonical Opaque Stripe IDs (e.g., `blk_...`, `stp_...`, `wor_...`) for all data relations, schema generation, dict key bindings, logger outputs, error traces, and runtime branching.</mandate>
    </rule_block>

    <rule_block id="id_backend_generation_authority_mandate">
        <mandate>NEVER accept client-defined primary IDs on resource creation endpoints, use sequential/semantic counters, or rely on frontend timestamps. All primary and relational entity IDs MUST be generated exclusively on the backend via randomized cryptographic generators (`f"{prefix}_{uuid.uuid4().hex[:16]}"`). Resources in draft endpoints MUST have their canonical Opaque Stripe ID pre-assigned by the backend. All models MUST enforce strict regex `pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$"` on `id` fields.</mandate>
    </rule_block>

    <rule_block id="anemic_routers">
        <mandate>NEVER place business logic, database CRUD, or RBAC checks in API routers (`backend_v2/api/`). Routers MUST ONLY handle HTTP parsing, assign an explicit `response_model`, and delegate to the Service layer (`backend_v2/services/`).</mandate>
    </rule_block>

    <rule_block id="blocking_the_fastapi_thread">
        <mandate>NEVER execute long-running AI generation or heavy DAG execution synchronously within a FastAPI request cycle. ALWAYS offload heavy processing to the Arq 2026 async worker queue and return 202 Accepted with TaskID immediately.</mandate>
    </rule_block>

    <rule_block id="anti_fragility_boundaries">
        <mandate>NEVER make unbounded external requests or rely solely on Fail-Fast without circuit breaking during 429/502/503 storms. ALL heavy I/O operations and external API integrations MUST use Circuit Breaker and Bulkhead architectures (`asyncio.Semaphore` for concurrency limits + Circuit Breaker to reject new requests with transient errors when endpoints fail repeatedly). Retries MUST be subordinated to the Circuit Breaker.</mandate>
    </rule_block>

    <rule_block id="pydantic_namespace_collisions">
        <mandate>NEVER define Pydantic schemas inline within `routers/` or duplicate class names. ALWAYS centralize FastAPI schemas in `models/` (SSOT) and run `generate_openapi.py` upon changes.</mandate>
    </rule_block>

    <rule_block id="security_logging_ban">
        <mandate>NEVER log raw HTTP payloads, user prompts (PII), API keys, or JWT tokens into logs or `AppException` messages. ALWAYS log only mathematical/logical reasons and Opaque System IDs (e.g., `req_abc123`). Read external API keys exclusively via `pydantic-settings` from environment variables, never hardcoded.</mandate>
    </rule_block>

    <rule_block id="de_generator_mandate_no_xml">
        <mandate>NEVER use XML tags (`<system_directive>`, `<role>`, `<objective>`) inside `seed_data.json` prompt fields (`ai_description`, `system_prompt`). ALWAYS write pure business logic using Markdown headings (`ROLE:`, `OBJECTIVE:`); `prompt_factory.py` automatically injects required XML wrappers.</mandate>
    </rule_block>

    <rule_block id="internal_language_and_epic_ban">
        <mandate>NEVER use the term "Epic" (or "EPIC") in any `description`, docstring, or comment, and NEVER use Finnish or non-English in comments, variable names, or internal descriptions. ALL internal codebase documentation, comments, and Pydantic descriptions MUST be written exclusively in English.</mandate>
    </rule_block>

    <rule_block id="anti_surface_level_remodeling">
        <mandate>NEVER propose [NEW] DTOs, Enums, Exceptions, or Data Models based purely on generic type hints (`dict`, `Any`, `str`, `**kwargs`) or loose boundaries in existing code. ALWAYS execute a two-step verification: 1. TRACE UPSTREAM (Origin Check) to verify runtime data types; 2. TRACE SSOT (Reuse Check) via `grep_search` across `models/v2_core.py`, `models/enums.py`, `models/dtos/` before creating models. If data is structured, surgically correct type hints without inventing parallel models.</mandate>
    </rule_block>

    <rule_block id="pydantic_discriminated_union_mandate">
        <mandate>NEVER create "Chameleon/Pseudo-Classes" inheriting from BaseModel that hijack `__new__`, override `model_construct`/`model_validate` with `# type: ignore[override]`, use `if-elif` chains with raw string literals, or fall back to default subclasses. ALWAYS implement polymorphic schemas strictly as Pydantic V2 Discriminated Unions: 1) Pure Type Alias (`AnyPromptBlock = Annotated[SubA | SubB, Field(discriminator="category_id")]`), 2) Centralized `TypeAdapter(AnyPromptBlock)`, 3) Strict Enum Registry (`PROMPT_BLOCK_REGISTRY: dict[PromptBlockCategory, type[PromptBlockBase]]`), 4) Absolute Fail-Fast with zero silent fallbacks, 5) Concrete instantiation in business logic and fixtures.</mandate>
    </rule_block>
</catastrophic_system_bans>

<architectural_invariants>
    <rule_block id="context_envelope_ssot_predicates">
        <mandate>NEVER add `@property` or computed methods to API DTOs, database persistence models, or OpenAPI schemas (`models/dtos/`, `models/api/`); NEVER execute I/O, DB queries, or state mutations in `@property`; NEVER define derived state as writable `Field` attributes; and NEVER write repeated multi-level null checks across consumers. ALWAYS enforce the "Context Envelope Predicate SSOT" pattern exclusively on in-memory context envelopes (`AdapterContext`, `ExecutionContext`) as pure, side-effect-free, O(1) properties returning `bool` (`is_*`, `has_*`) or typed `Enum` derived from immutable fields.</mandate>
    </rule_block>

    <rule_block id="pydantic_annotated_fields_mandate">
        <mandate>NEVER use bare type hints combined with `Field(...)` assignments in Pydantic settings or models (e.g., `timeout: int = Field(...)`). ALWAYS use PEP 593 `Annotated` syntax (e.g., `timeout: Annotated[int, Field(description="...")] = 10`).</mandate>
    </rule_block>

    <rule_block id="opaque_stripe_id_mandate">
        <mandate>NEVER use auto-incrementing integers (`id=1`), raw UUIDs leaking database context, or semantic strings like `slug` as primary keys, database references, or API route identifiers. ALWAYS enforce the "Opaque Stripe ID" pattern (e.g., `wor_a1b2c3d4`, `usr_x9y8z7`) for all database identifiers, cross-model relations, and navigation endpoints.</mandate>
    </rule_block>

    <rule_block id="alias_engine_llm_isolation_mandate">
        <mandate>NEVER pass raw database UUIDs or Opaque Stripe IDs (`tda_...`) directly into LLM prompts/schemas or expect them back. ALWAYS use `AliasEngine` to generate short, semantic aliases (`a0`, `doc1`, `cond0`) before sending data to LLM, and use `AliasEngine.hydrate_dict_list()` to map them back to original Opaque UUIDs.</mandate>
    </rule_block>

    <rule_block id="strict_pydantic_v2_rust">
        <mandate>NEVER use legacy V1 instantiation (`MyModel(**data)`), Python standard JSON parsing (`json.loads()`), legacy methods (`.dict()`, `@validator`), or duck typing/arbitrary checks (`hasattr(obj, 'key')`, `isinstance(data, dict)`). ALWAYS use `.model_validate()`, Rust-based `.model_validate_json()`, `.model_dump()`, and `@field_validator`. Enforce `model_config = ConfigDict(extra='forbid', strict=True)` to Fail-Fast on invalid structures with `ValidationError`.</mandate>
    </rule_block>

    <rule_block id="strict_enum_hydration_and_validation">
        <mandate>NEVER use `.value` when updating or instantiating Pydantic models (e.g. `model_copy(update={"status": Status.PASSED.value})`) or wrap hydration in `isinstance(data, dict)`. ALWAYS pass native Enum objects to Pydantic models for Rust coercion. `.value` is permitted ONLY for primitive assignments, stdlib logging (`extra={"error_code": ...}`), and raw `AppException` dicts.</mandate>
    </rule_block>

    <rule_block id="zero_legacy_fallback_hacks">
        <mandate>NEVER add `@model_validator(mode="before")` or optional union types (`| None`) purely to silently scrub or appease old V1 legacy payload fields (e.g., `task_key`) from crashing `extra='forbid'`. ALWAYS maintain Pydantic `extra='forbid'` strictness; fix dirty historical databases at the source via `uv run python backend_v2/seed/run_seed.py local`.</mandate>
    </rule_block>

    <rule_block id="pydantic_pure_hydration_boundary">
        <mandate>NEVER use `json.dumps(data, default=str)` hacks or strip `strict=True` from model `ConfigDict` to parse raw database dictionaries containing mixed ISO strings and datetimes/UUIDs. ALWAYS keep `model_config = ConfigDict(strict=True)` on models for API boundaries, and use `MyModel.model_validate(data, strict=False)` when hydrating data from the trusted internal Repository layer.</mandate>
    </rule_block>

    <rule_block id="no_naked_dicts_in_state">
        <mandate>NEVER push parsed LLM outputs directly into `state_delta` or intermediate caches as naked dictionaries. ALWAYS intercept raw datastreams with `.model_validate()` at the boundary. If storage requires dicts, chain explicitly: `MyModel.model_validate(data).model_dump(mode='json')`.</mandate>
    </rule_block>

    <rule_block id="schema_convergence_mandate">
        <mandate>NEVER create parallel schemas representing the same logical domain concept, add compatibility properties to bridge schemas, or maintain parallel if/else branches based on mode flags. ALWAYS enforce "One Concept = One Schema": 1) Extract shared Protocol/ABC, 2) Implement Protocol in both models, 3) Consumers accept ONLY the Protocol type, 4) Set explicit SUNSET DEADLINE to delete old models within the same or next Epic, 5) Absolute Fail-Fast with zero fallback chains.</mandate>
    </rule_block>

    <rule_block id="structured_state_envelopes_mandate">
        <mandate>NEVER use naked dictionaries (`dict`) for intermediate execution traces (e.g. `fold_trace` returning dicts) or string manipulation (`endswith()`, `split()`) to parse traces. ALWAYS use structured envelopes (`list[StepOutputDTO]`) and filter by `step_id` and `block_id` natively.</mandate>
    </rule_block>

    <rule_block id="polymorphic_dag_payload_handling">
        <mandate>NEVER assume `StepOutputDTO.payload` is always a `dict` or write consumers that crash on strings/Markdown, scalars, or empty payloads. Downstream consumers (`SynthesisPayloadCompressor`, `synthesis_distiller_hook`, reporting hooks) MUST polymorphically handle all 4 valid partitions (`dict`, `list`, `str`, `int`/`float`/`bool`), filter metadata (`_`) and empty payloads gracefully, and test all 4 partitions in unit tests.</mandate>
    </rule_block>

    <rule_block id="pydantic_native_field_priority">
        <mandate>NEVER use `@field_validator` for simple bounds checking or regex. ALWAYS prefer native Rust-executed `Field(ge=0, pattern=...)`.</mandate>
    </rule_block>

    <rule_block id="frozen_state_mutability">
        <mandate>NEVER mutate domain objects in-place (`event.status = 'done'`), use `setattr(...)`, `object.__setattr__(...)`, or `__setattr__()`, perform unsynchronized mutations across coroutines, or run `model.model_validate(model.model_dump() | updates)` on large object graphs (`ExecutionRecord`) during high-frequency DAG loops. ALL Event Sourcing models, DTOs, and DAG nodes MUST use `ConfigDict(frozen=True)`. State transitions in `DAGExecutor` MUST execute inside `async with _update_lock:` using `.model_copy(update=...)` with typed instances.</mandate>
    </rule_block>

    <rule_block id="polymorphic_routing_o1">
        <mandate>NEVER use implicit Unions or structural `isinstance()` chains with polymorphic DAG nodes. ALWAYS mandate Discriminated Unions (`Field(discriminator='type')`) and Python 3.10+ `match...case` structures.</mandate>
    </rule_block>

    <rule_block id="dynamic_vs_static_localization_ssot_mandate">
        <mandate>NEVER create ad-hoc translation keys in `fi.json` / `en.json` (e.g. `input_key_*`) or hardcode localized dictionaries in Python code for dynamic entities configured by users or seeded in the database. ALWAYS enforce Dynamic vs Static Localization SSOT:
        1. **Static UI & Structural Labels**: Fixed layout labels, column headers, and system statuses MUST be defined in `backend_v2/l10n/` and Flutter `.arb` files (e.g. `col_label`, `matrix_col_score`).
        2. **Dynamic User-Configurable Entities**: Workflows, steps, input names (`ExpectedInput.label`), and prompt blocks MUST be stored as `I18nText` directly in the database (`seed_data.json` / `Workflow`).
        Backend services and SDUI transformers MUST resolve dynamic entity labels directly from their database model instances (`input_def.label`) without intermediate fallback dictionaries.</mandate>
    </rule_block>

    <rule_block id="python_314_modern_syntax">
        <mandate>NEVER use legacy wrapper typings (`TypeVar`, `Generic[T]`, `Optional[X]`), forward string return annotations (`-> "MyClass"`), or `asyncio.gather()`. ALWAYS use PEP 695 generics (`class Repository[T]:`), `@override`, bitwise unions (`X | None`), `async with asyncio.TaskGroup() as tg:`, and PEP 673 `-> Self` for classmethods returning the class itself.</mandate>
    </rule_block>

    <rule_block id="no_string_l10n">
        <mandate>NEVER hardcode application vocabulary, UI display strings, or string comparisons in backend code. ALWAYS resolve Backend APIs to Enum Keys (e.g., `AUTH_ORGANIC`) and defer raw string resolution to Flutter `.arb`.</mandate>
    </rule_block>

    <rule_block id="strict_enum_l10n_mapping">
        <mandate>NEVER use string manipulation (`role.value.split('_')` or `.lower()`) to guess Flutter ARB keys from Enums. When backend formats text (SDUI Localization), ALWAYS define the mapping explicitly inside the Enum class via `@property def l10n_key(self) -> str:` method.</mandate>
    </rule_block>
    
    <rule_block id="data_leak_prevention_firewall">
        <mandate>NEVER return raw DB models natively out of FastAPI endpoints, bypass Pydantic filtering, or define `exclude=True` locally in Routers. EVERY FastAPI router MUST explicitly define `response_model=UserDTO` (inheriting from `BaseResponseDTO`) to strip hidden variables globally.</mandate>
    </rule_block>

    <rule_block id="llm_structured_execution_mandate">
        <mandate>NEVER directly call OpenAI/Vertex SDKs, rely on raw text outputs, parse responses with Regex, or call `LLMClient` methods directly for business logic. ALWAYS initialize via `LLMClient.from_strategy("strategy_name", repo)` and pass to injected `LLMTaskExecutor`: use `executor.execute_structured_task()` for structured data and `executor.execute_chat_task()` for open-text generation.</mandate>
    </rule_block>

    <rule_block id="ui_driven_synthesis_boundary">
        <mandate>NEVER hardcode UI-defined data keys (e.g., `product_text`, `document_text`) in backend Python code or feed raw execution state (including Eager Extracted PDF dumps) to LLM during synthesis/reporting. Backend reporting and synthesis hooks MUST strictly filter data based on UI-defined `target_blocks` (Output Profile Layouts) and unpack `inputs` against this UI config to prevent token explosions.</mandate>
    </rule_block>

    <rule_block id="strict_math_display_isolation">
        <mandate>NEVER assume database config fields `scale_min` and `scale_max` dictate scales in use or use them to calculate backend mathematical scores. Scoring math engine MUST derive internal mathematical boundaries exclusively from typed Pydantic `scales` array (`min(scales)` -> `math_min`, `max(scales)` -> `math_max`). `scale_min`/`scale_max` in DB are ONLY cosmetic UI projection targets (`display_min`, `display_max`); if missing, trigger Fail-Fast `ConfigurationError`.</mandate>
    </rule_block>

    <rule_block id="service_layer_hydration_firewall">
        <mandate>NEVER return raw DB dictionaries from the Data Access Layer (Repository) or Service layer. The Repository layer acts as the reconstitution firewall: internal database drivers return raw dictionaries, and Repository methods map them into strictly typed Pydantic Domain Models (`ConfigDict(frozen=True)`) before returning to the Service layer or callers.</mandate>
    </rule_block>

    <rule_block id="strict_dependency_injection">
        <mandate>NEVER instantiate services or databases directly inside FastAPI routers. Dependencies MUST be injected exclusively via FastAPI's `Depends()` + PEP 593 `Annotated`. EXCEPTION: Arq workers, CLI scripts, and cron tasks run outside HTTP request lifecycle; instantiate services manually at the top-level entrypoint and pass them explicitly.</mandate>
    </rule_block>

    <rule_block id="typed_dependency_container_mandate">
        <mandate>NEVER pass long parameter lists (5+ dependencies) across constructors, use `**kwargs` dictionary unpacking, or copy-paste constructor parameter lists. ALWAYS encapsulate multi-dependency groupings into strictly typed, immutable `@dataclass(frozen=True)` containers (e.g., `StrategyDependencies`, `HookDependencies`) and pass `deps: StrategyDependencies` to constructors.</mandate>
    </rule_block>

    <rule_block id="strict_configuration_segregation">
        <mandate>NEVER mix global constraints, taxonomy values, and runtime instantiation into single files or use magic numbers. Enforce Tripartite Configuration Architecture: 1) `enums.py` contains finite constants/taxonomy (no logic/env vars), 2) `settings.py` contains all global limits/bounds/env config, 3) DTOs combine them during runtime. No magic numbers in business logic.</mandate>
    </rule_block>

    <rule_block id="global_settings_import">
        <mandate>NEVER import `get_settings` locally inside a function (`from backend_v2.settings import get_settings` inside `def`). ALWAYS import `get_settings` globally at the top of the file. In unit tests, `monkeypatch` the module where it is used (e.g. `backend_v2.hooks.scoring.get_settings`).</mandate>
    </rule_block>

    <rule_block id="cross_language_enum_parity">
        <mandate>NEVER encode UI rendering logic in Pydantic `Literal` or `Enum` without enforcing parity on Flutter client. All cross-boundary Pydantic fields controlling UI lists/presets MUST map to strict `@JsonEnum()` in `client_app_v2/lib/core/models/enums.dart`, verified by `test_enum_parity.py` in Pytest.</mandate>
    </rule_block>

    <rule_block id="schema_driven_routing">
        <mandate>NEVER use duck typing or blind `try...except` Pydantic validation (e.g., `if "raw_score" in dict`) to guess payload types during orchestration. ALWAYS derive types and processing routes from database UI configuration (`schema_map` from Workflow/V2Step definitions).</mandate>
    </rule_block>

    <rule_block id="zero_db_hardcoding_mandate">
        <mandate>NEVER compare logical conditions against hardcoded database IDs, strings, or names (`if node.id == "usr_123"` or `if block.slug == "main_matrix"`), or assume sort orders (`db_result[0]`). Logic MUST be based on abstract attributes, schema types (via Pydantic Discriminators like `isinstance(block, MatrixBlockDTO)`), or dynamically injected configuration values.</mandate>
    </rule_block>

    <rule_block id="orchestrator_god_object_fragility">
        <mandate>NEVER modify individual files in DAG Engine core (`backend_v2/services/orchestrator/`, e.g., `atomizer.py`, `dag_executor.py`, `topological_evaluator.py`, `matrix_reducer.py`) without full blast-radius analysis. You MUST STOP and request "PERMISSION GRANTED to mutate DAG Orchestrator ecosystem", run the FULL backend audit loop, and evaluate the entire topological flow.</mandate>
    </rule_block>

    <rule_block id="tripartite_rendering_boundary">
        <mandate>NEVER hardcode UI components, layout structures, or Markdown tables in backend generation hooks. Backend services MUST return pure data payloads (Pydantic DTOs). Tripartite Rendering: Backend passes structured data, Flutter renders interactive UI, Jinja generates static PDFs. All SDUI adapters and PDF generation changes MUST be verified using `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.</mandate>
    </rule_block>

    <rule_block id="zero_type_ignore_shortcuts">
        <mandate>NEVER use `# type: ignore` arbitrarily to silence MyPy without investigating the root cause. Fix variable types, models, or signatures. If an external library forces an unavoidable violation, use strictly scoped ignore markers with exact error codes (e.g. `# type: ignore[attr-defined]`) and an explanatory comment. Blanket ignores are strictly forbidden.</mandate>
    </rule_block>

    <rule_block id="explicit_reexport_mandate">
        <mandate>NEVER perform implicit re-exports (`from module import Symbol`) in `__init__.py` or Strangler Fig proxy/facade files. Re-exported symbols MUST be explicitly declared via `__all__ = ["Symbol", ...]` OR redundant import aliases (`from module import Symbol as Symbol`) to satisfy PEP 484 and `mypy --strict`.</mandate>
    </rule_block>

    <rule_block id="execution_synthesis_tier_decoupling">
        <mandate>NEVER place UI-formatting logic (e.g., "Output ONE punchy sentence", 0-100 scales) in `PromptBlocks`, and NEVER place execution-tier directives (e.g., `ROLE: ANTAGONISTIC PROSECUTOR`, boolean hypothesis testing) in `OutputProfiles`. `PromptBlocks` are EXCLUSIVELY for raw data evaluation (1-5 scales, ZERO-TRUST AUDITOR, atomic extraction); `OutputProfiles` are EXCLUSIVELY for presentation formatting (0-100 scales, brevity, tone).</mandate>
    </rule_block>

    <rule_block id="fail_fast_hydration_mandate">
        <mandate>NEVER fish for dictionary values via `dict.get()`. ALL uncertain data flowing as dictionaries MUST be hydrated via `.model_validate()` IMMEDIATELY before processing.</mandate>
    </rule_block>

    <rule_block id="annotated_hydration_mandate">
        <mandate>NEVER convert enums manually using `if/else` checks or external dictionaries. External data enum conversions MUST be mapped exclusively using `Annotated[CustomEnum, Field(strict=False)]` aliases in `enums.py`.</mandate>
    </rule_block>

    <rule_block id="vertex_serving_grammar_fix">
        <mandate>NEVER apply float type field constraints (`ge`, `le`) at the `Field()` level (causes Vertex AI 400 errors). ALWAYS move float constraints to local `@field_validator` methods.</mandate>
    </rule_block>

    <rule_block id="blind_extraction_null_hypothesis">
        <mandate>NEVER allow LLM to output both an `exact_quote` and `contextual_override == True` simultaneously. TDA extraction models MUST force null hypothesis via `@model_validator`: if `contextual_override == True`, force `exact_quote` to `None`.</mandate>
    </rule_block>

    <rule_block id="zero_defaults_mandate">
        <mandate>NEVER use mutable types (list, dict) as default arguments (B006) or default critical data. DTO models MUST NOT use default values for critical data; use `None` and initialize inside the function block.</mandate>
    </rule_block>

    <rule_block id="duck_typing_token_shield_exception">
        <mandate>NEVER use `extra="ignore"` in Pydantic models. ABSOLUTE EXCEPTION: `SynthesisStepDataDTO`. You MUST NOT invent or classify arbitrary models as "Token Shields" without explicit USER pre-approval.</mandate>
    </rule_block>

    <rule_block id="python_314_root_model_ban">
        <mandate>NEVER use `RootModel` to enforce dynamic TypeAdapter patterns. ALWAYS wrap standard types dynamically using `TypeAdapter` (e.g. `TypeAdapter(list[UserDTO]).validate_python(data)`).</mandate>
    </rule_block>

    <rule_block id="append_only_state_mutation">
        <mandate>NEVER perform in-place mutation of `execution_trace` or `step_states`. Historical payload data MUST NEVER be overwritten; dynamic projections MUST be executed on-the-fly into newly instantiated DTO models.</mandate>
    </rule_block>

    <rule_block id="base64_amnesia_protocol">
        <mandate>NEVER persist raw base64 data or binaries within Pydantic states. ALWAYS extract them into text representations via Eager Extraction at the boundary layer.</mandate>
    </rule_block>

    <rule_block id="dlq_arq_fallback_routing">
        <mandate>NEVER let a worker crash the entire execution tree with an unhandled exception. Route TaskGroup or ChunkWorker errors to Dead Letter Queue by yielding `{"_dlq_status": "FAILED/DLQ"}`.</mandate>
    </rule_block>

    <rule_block id="the_self_healing_ban">
        <mandate>NEVER attempt to dynamically patch AI-generated quotes or JSON formatting errors on-the-fly using Regex. Data validation belongs 100% to Pydantic.</mandate>
    </rule_block>

    <rule_block id="md5_hashery_ban">
        <mandate>NEVER use `hashlib.md5` or `hashlib.sha1` for dynamic ID generation. ALWAYS use `uuid.uuid4().hex[:8]`. For cryptographic operations, `random` is forbidden; always enforce `secrets`.</mandate>
    </rule_block>

    <rule_block id="high_fidelity_prompting">
        <mandate>NEVER use f-strings for foundational core rules. Prompt core instructions MUST remain static. Dynamic variables MUST be isolated within `<execution_parameters>` and input data in `<source_data>`.</mandate>
    </rule_block>

    <rule_block id="single_source_of_truth_mandate">
        <mandate>NEVER allow V1 and V2 models to coexist. Ruthlessly purge deprecated V1-era fallback hacks, `.get()` coalescing chains, and `@model_validator` retrofits handling legacy data payloads.</mandate>
    </rule_block>

    <rule_block id="native_english_generation">
        <mandate>NEVER prompt LLMs to translate cognitive reasoning logic on-the-fly. Cognitive reasoning MUST be formulated natively in English; UI localization is handled strictly in a downstream translation pass.</mandate>
    </rule_block>

    <rule_block id="hybrid_prompting_mandate">
        <mandate>NEVER construct prompts using pure unstructured text. ALWAYS use hybrid XML for structural control and Markdown for nested content formatting.</mandate>
    </rule_block>

    <rule_block id="role_segregation_and_fencing">
        <mandate>NEVER inject raw user text directly into system prompts. ALWAYS fence untrusted user payloads with clear XML tags (`<user_payload>...</user_payload>`).</mandate>
    </rule_block>

    <rule_block id="infinite_retry_loops">
        <mandate>NEVER run infinite retry loops on failed schema validations. ALWAYS enforce an absolute max retry limit of 2 using `SystemConcurrency.LLM_MAX_RETRIES` before triggering Fail-Fast.</mandate>
    </rule_block>

    <rule_block id="system_concurrency_ssot">
        <mandate>Parallel async LLM steps MUST use `asyncio.TaskGroup` constrained by `asyncio.Semaphore(SystemConcurrency.MAX_CONCURRENT_LLM_STEPS)`.</mandate>
    </rule_block>

    <rule_block id="strict_physical_anchoring_mandate">
        <mandate>NEVER use fuzzy string matching as PRIMARY validation gate for evidence extraction, apply fuzzy matching to quotes under 10 chars, or skip mandatory `str.find`. ALWAYS enforce Tiered Lexical Validation: 1) Primary Gate: `str.find` on normalized strings, 2) Entropy Gate: quotes < 10 chars require 100% exact match, 3) Fuzzy Fallback: RapidFuzz permitted only when Primary Gate fails, quote > 10 chars, and strictness < 100, 4) RapidFuzz unrestricted for non-forensic optimization.</mandate>
    </rule_block>

    <rule_block id="ensemble_parallel_evaluation_mandate">
        <mandate>ALWAYS execute high-entropy or negative validation steps using a single-pass "Best-of-3" voting ensemble across parallel LLM calls wrapped in `asyncio.TaskGroup`.</mandate>
    </rule_block>

    <rule_block id="pep257_google_style_docstrings">
        <mandate>Every module, class, and function MUST possess a PEP 257 compliant Google-style docstring starting with a concise Summary line terminating with a period.</mandate>
    </rule_block>

    <rule_block id="google_style_functions_args_returns">
        <mandate>Function docstrings MUST explicitly specify `Args:`, `Returns:`, and/or `Yields:` blocks immediately following the summary description.</mandate>
    </rule_block>

    <rule_block id="google_style_classes_separation">
        <mandate>Class-level docstrings contain ONLY description and public `Attributes:`. The `__init__` method MUST encapsulate `Args:` and `Raises:`.</mandate>
    </rule_block>

    <rule_block id="free_threading_concurrency">
        <mandate>NEVER use `multiprocessing`. ALL routines MUST be thread-safe (Free-threading architecture) using lightweight threads or `asyncio`.</mandate>
    </rule_block>

    <rule_block id="modern_type_aliases_pep695">
        <mandate>ALWAYS use PEP 695 `type` keyword for type aliases (`type Point = tuple[float, float]`).</mandate>
    </rule_block>

    <rule_block id="taskgroup_exceptiongroup_mandate">
        <mandate>NEVER use `asyncio.gather`. ALWAYS orchestrate background routines via `asyncio.TaskGroup` and trap parallel exceptions with `ExceptionGroup` and native `except*` syntax.</mandate>
    </rule_block>

    <rule_block id="idiomatic_pattern_matching">
        <mandate>NEVER use verbose `if-elif` cascades for data destructuring or type validation. ALWAYS use native Python `match` and `case` structures.</mandate>
    </rule_block>

    <rule_block id="pathlib_over_ospath">
        <mandate>NEVER invoke legacy `os.path`. ALWAYS exclusively use `pathlib.Path`.</mandate>
    </rule_block>

    <rule_block id="pep750_t_strings_only">
        <mandate>NEVER use standard f-strings in critical data ingestion pathways. Construct dynamic LLM prompts and SQL statements using Python 3.14 t-strings (Template Strings - PEP 750).</mandate>
    </rule_block>

    <rule_block id="pep734_subinterpreters_for_cpu">
        <mandate>Heavyweight CPU-bound background processes MUST be dispatched via standard library `interpreters` module (subinterpreters) instead of `multiprocessing`.</mandate>
    </rule_block>

    <rule_block id="pep742_typeis_over_typeguard">
        <mandate>NEVER use legacy `typing.TypeGuard` for Type Narrowing. ALWAYS enforce `typing.TypeIs` (PEP 742).</mandate>
    </rule_block>

    <rule_block id="anti_hallucination_guardrail">
        <mandate>NEVER delete existing classes or enums assuming they are unused; DO NOT invent import paths or hallucinate new Pydantic models.</mandate>
    </rule_block>

    <rule_block id="repository_reconstitution_mandate">
        <mandate>All Data Access Layer (Repository) methods MUST return strictly typed Pydantic Domain models (`ConfigDict(frozen=True)`). Raw database dictionaries (`dict[str, Any]`) are strictly isolated within internal database driver layers. Service and Hook layers MUST NEVER use `getattr()`, `hasattr()`, or `isinstance(..., dict)` for reflection or duck-typing.</mandate>
    </rule_block>

    <rule_block id="zero_truncation_pledge">
        <mandate>NEVER truncate existing methods, classes, or implementations into `pass` stubs. Code output MUST be fully functional drop-in replacements.</mandate>
    </rule_block>

    <rule_block id="strict_attribute_integrity">
        <mandate>NEVER convert strict dot-notation attribute access into dynamic `getattr(model, "model", "")` fallbacks. ALWAYS rely on Pydantic's static structure (EXCEPTIONS: Safe checks using `in` operator).</mandate>
    </rule_block>

    <rule_block id="api_service_separation_mandate">
        <mandate>ID generation for new or cloned entities MUST occur exclusively within the Service layer (`StudioService`), NEVER at the API Router boundary.</mandate>
    </rule_block>

    <rule_block id="setdefault_hydration_mandate">
        <mandate>NEVER use complex conditional logic for hydration (`if "key" not in kwargs:`). ALWAYS use Python's native `dict.setdefault("key", value)`.</mandate>
    </rule_block>

    <rule_block id="pydantic_configuration_enforcement">
        <mandate>NEVER tolerate loose `extra="allow"` or `extra="ignore"` in primary domain models. ALWAYS enforce `model_config = ConfigDict(extra="forbid", strict=True)` on all Domain DTOs unless explicitly defined as a Token Shield.</mandate>
    </rule_block>

    <rule_block id="pydantic_v2_computed_field_order">
        <mandate>NEVER place `@property` above `@computed_field`. The `@computed_field` decorator MUST strictly be placed ABOVE `@property`, appending `# type: ignore[prop-decorator]`.</mandate>
    </rule_block>

    <rule_block id="srp_god_method_mandate">
        <mandate>NEVER write monolithic controller or service methods exceeding 50 lines of core logic. ALWAYS break down methods >50 lines into isolated private helper methods to uphold Single Responsibility Principle.</mandate>
    </rule_block>

    <rule_block id="fail_fast_payload_length_mandate">
        <mandate>ALWAYS enforce strict minimum character length on extracted user text payloads BEFORE passing them to an LLM context window.</mandate>
    </rule_block>

    <rule_block id="async_io_lock_isolation_mandate">
        <mandate>NEVER execute slow async I/O (like DB commits) inside an `asyncio.Lock()` block. ALWAYS implement a Two-Lock Strategy: release memory lock instantly, trigger event completion, and use a separate commit lock for eventual DB consistency.</mandate>
    </rule_block>

    <rule_block id="pydantic_mutation_optimization_mandate">
        <mandate>NEVER mutate Pydantic objects via full serialization (`model_dump()`) followed by full re-instantiation. ALWAYS use `.model_copy(update={...})` for shallow C-level updates.</mandate>
    </rule_block>

    <rule_block id="primitive_obsession_evidence_quotes">
        <mandate>NEVER pack complex data structures (text + source reference) into a single string using pipe characters (`|||`). ALWAYS use structured Pydantic models directly from the LLM output boundary.</mandate>
    </rule_block>

    <rule_block id="immutable_history_snapshot">
        <mandate>NEVER execute live queries to the database for display names during render time. Backend presentation layer (BFF / blueprint) MUST produce UI strings from runtime frozen metadata (inputs-snapshot).</mandate>
    </rule_block>

    <rule_block id="graceful_degradation_over_fail_fast">
        <mandate>NEVER allow the entire execution graph to crash because a single hallucinated peripheral string field (like an optional UI label) failed parsing. Defensively scrub peripheral fields (cast to `None`) inside `@model_validator` while strictly enforcing Fail-Fast on core business logic.</mandate>
    </rule_block>

    <rule_block id="declarative_set_logic_mandate">
        <mandate>NEVER use imperative `if x not in lst: lst.append(x)` loops or multiple `list(set(x))` conversions. ALWAYS use Python declarative Set operations (`set(a) | set(b)`, `my_set.update(...)`) and convert to `sorted(list(my_set))` only at final assignment.</mandate>
    </rule_block>

    <rule_block id="pydantic_discriminator_hallucination_prevention">
        <mandate>NEVER use `Field(discriminator='...')` in Pydantic Union models without setting a strict schema title for each child model. ALWAYS set `model_config = ConfigDict(title="<discriminator_value>")` on every polymorphic child model.</mandate>
    </rule_block>

    <rule_block id="graceful_text_truncation_validator">
        <mandate>NEVER rely solely on `max_length=N` in `Field()` for LLM text generation without a truncation mechanism. ALWAYS implement `@field_validator(..., mode="before")` to truncate strings rounding down to the nearest sentence (`.`).</mandate>
    </rule_block>
</architectural_invariants>

<agentic_safety_guardrails>
    <rule_block id="architecture_lock_mandate">
        <mandate>NEVER refactor, modify control flow, or change data traversal logic in code blocks protected by an `ARCHITECTURE LOCK` comment. ALWAYS strictly preserve these blocks (you MAY only add/update PEP 257 docstrings).</mandate>
    </rule_block>

    <rule_block id="pydantic_schema_freeze_mandate">
        <mandate>NEVER autonomously tighten structural types, remove `Optional` (`| None`) bounds, or change field signatures on existing Pydantic models. Log warnings in audit matrix instead; schema mutability is strictly forbidden without explicit instruction.</mandate>
    </rule_block>

    <rule_block id="pydantic_validation_bypass_ban">
        <mandate>NEVER use `dict(model)`, list comprehensions casting to raw dicts, manual field-by-field reconstruction (`Model(field=[dict(x) for x in old.field])`), or full serialization cycles (`type(model)(**model_dump())`) to bypass validation constraints. NEVER use unsynchronized `model_copy(update={...})` across concurrent coroutines. For mutating frozen models: 1) Hydrate untrusted inputs via `Model.model_validate(raw_data)`, 2) Internal high-throughput DAG state uses `model.model_copy(update=...)` with typed instances inside `async with _update_lock:`.</mandate>
    </rule_block>

    <rule_block id="data_and_file_preservation_mandate">
        <mandate>NEVER autonomously refactor, truncate, or "simplify" existing file I/O operations, data extraction loops, string concatenations, or dictionary traversals purely for aesthetics. Architectural mandate is strictly typing, docstrings, and modern syntax; ALWAYS preserve functional I/O and parsing logic entirely.</mandate>
    </rule_block>

    <rule_block id="backend_quality_gate_delegation">
        <mandate>NEVER run generic pytest without the global audit script. If you modify `.py` files, you MUST run: `uv run python scripts/backend_audit_loop.py <target_path> --test` after every single code mutation.</mandate>
    </rule_block>
</agentic_safety_guardrails>