# BACKEND ARCHITECTURE CONSTRAINTS

*** UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS FOR PYTHON ***

<catastrophic_system_bans>
    <rule_block id="silent_failures">
        <banned_pattern>Swallowing exceptions silently using `try: ... except Exception: pass`.</banned_pattern>
        <mandatory_pattern>Exceptions must ALWAYS be logged natively (`logger.error`) and re-thrown or handled explicitly via `AppException` (RFC 7807).</mandatory_pattern>
        <catastrophic_reason>Silent failures mask root causes of memory leaks and DB corruption.</catastrophic_reason>
    </rule_block>
    
    <rule_block id="anemic_routers">
        <banned_pattern>Putting business logic, database CRUD, or RBAC checks in API routers (`backend_v2/api/`).</banned_pattern>
        <mandatory_pattern>Routers MUST ONLY handle HTTP parsing, assign an explicit `response_model`, and delegate to the Service layer (`backend_v2/services/`).</mandatory_pattern>
        <catastrophic_reason>Single Responsibility Principle violation. Business logic execution in routers breaks security isolation layers.</catastrophic_reason>
    </rule_block>

    <rule_block id="blocking_the_fastapi_thread">
        <banned_pattern>Executing long-running AI generation or heavy DAG execution synchronously within a FastAPI request cycle.</banned_pattern>
        <mandatory_pattern>MUST offload heavy processing to the Arq 2026 async worker queue. The API MUST return 202 Accepted with a TaskID immediately.</mandatory_pattern>
        <catastrophic_reason>Hangs the internal Node thread and fails remote user requests via timeout.</catastrophic_reason>
    </rule_block>

    <rule_block id="pydantic_namespace_collisions">
        <banned_pattern>Defining Pydantic schemas inline within `routers/` or duplicating class names.</banned_pattern>
        <mandatory_pattern>FastAPI schemas MUST be centralized in `models/` (SSOT). If a schema changes, you MUST instruct the user to run `generate_openapi.py`.</mandatory_pattern>
        <catastrophic_reason>Duplicate namespaces corrupt the OpenAPI generator and subsequently crash the Flutter Freezed parsers.</catastrophic_reason>
    </rule_block>

    <rule_block id="security_logging_ban">
        <banned_pattern>Logging raw HTTP payloads, user prompts (PII), API keys, or JWT tokens into logs or AppException messages.</banned_pattern>
        <mandatory_pattern>Log ONLY the mathematical/logical reason for the error and the Opaque System ID (e.g., req_abc123). All external API keys MUST be strictly read via pydantic-settings from environment variables, never hardcoded.</mandatory_pattern>
        <catastrophic_reason>Logging PII or secrets violates security compliance and exposes the system to catastrophic credential leaks. Furthermore, leaked secrets poison the LLM context if an agent reads `backend_debug.log` to troubleshoot.</catastrophic_reason>
    </rule_block>
</catastrophic_system_bans>

<architectural_invariants>
    <rule_block id="opaque_stripe_id_mandate">
        <banned_pattern>Using auto-incrementing integers (e.g., `id=1`), raw UUIDs leaking database context, or semantic strings like `slug` as primary keys, database references, or API route identifiers.</banned_pattern>
        <mandatory_pattern>Enforce the "Opaque Stripe ID" pattern (e.g., `wor_a1b2c3d4`, `usr_x9y8z7`) for ALL database identifiers, cross-model relations, and navigation endpoints. Slugs are for SEO/Display purposes only, NEVER for strict data relationships.</mandatory_pattern>
        <catastrophic_reason>Intelligible primary keys (slugs) lead to permanently broken foreign relations when a user edits the display name. Auto-increment IDs allow horizontal enumeration attacks (IDOR). Opaque prefix mapping ensures immediate visual typability during debugging and inherently secures the API.</catastrophic_reason>
    </rule_block>

    <rule_block id="strict_pydantic_v2_rust">
        <banned_pattern>Using legacy V1 instantiation (`MyModel(**data)`), Python standard JSON parsing (`json.loads()`), legacy V1 methods (`.dict()`, `@validator`), or using duck typing / arbitrary type checks like `hasattr(obj, 'key')` and `isinstance(data, dict)` to parse incoming LLM or DB state.</banned_pattern>
        <mandatory_pattern>Force the Fail-Fast pipeline by using `.model_validate()`, Rust-based `.model_validate_json()`, `.model_dump()`, and `@field_validator`. Use `model_config = ConfigDict(extra='forbid', strict=True)` to reject unstructured AI outputs instantly. Any structure not matching the strict model must CRASH immediately with a `ValidationError`.</mandatory_pattern>
    </rule_block>

    <rule_block id="zero_legacy_fallback_hacks">
        <banned_pattern>Adding `@model_validator(mode="before")` or optional union types (`| None`) to Pydantic models purely to silently scrub or appease old V1 legacy payload fields (e.g., `task_key`) from crashing `extra='forbid'`.</banned_pattern>
        <mandatory_pattern>NEVER bypass Pydantic `extra='forbid'` strictness to accommodate dirty databases. If historical data causes validation crashes, the root cause MUST be fixed at the source by instructing the user to wipe and re-seed the database (`run_seed.py`). Pydantic models must remain mathematically pure to the V2 spec.</mandatory_pattern>
        <catastrophic_reason>Writing fallback parsing logic pollutes the domain layer with historical technical debt, destroying the Fail-Fast architecture and silently allowing legacy structures to persist and mutate inside V2 pipelines.</catastrophic_reason>
    </rule_block>

    <rule_block id="no_naked_dicts_in_state">
        <banned_pattern>Pushing parsed LLM outputs directly into `state_delta` or intermediate caches as naked dictionaries simply to appease TinyDB/JSON serialization constraints.</banned_pattern>
        <mandatory_pattern>ALWAYS intercept raw datastreams with `.model_validate()` immediately at the boundary. If the storage engine requires raw dicts, chain it explicitly: `MyModel.model_validate(data).model_dump(mode='json')`.</mandatory_pattern>
        <catastrophic_reason>Passing naked dicts delays validation failures to the presentation layer, breaking traceability and defeating the 2026 Fail-Fast mandate.</catastrophic_reason>
    </rule_block>

    <rule_block id="structured_state_envelopes_mandate">
        <banned_pattern>Using naked dictionaries (`dict`) to represent the intermediate execution trace (e.g. `fold_trace` returning dicts) or parsing execution traces using string manipulation (`endswith()`, `split()`).</banned_pattern>
        <mandatory_pattern>All execution traces and state projections MUST use structured envelopes (`List[StepOutputDTO]`). Downstream consumers must strictly filter by `step_id` and `block_id` natively.</mandatory_pattern>
        <catastrophic_reason>Dictionary flatteners cause brittle "loose dictionary" traps, and string-parsing lineage leads to fatal reporting bugs.</catastrophic_reason>
    </rule_block>

    <rule_block id="pydantic_native_field_priority">
        <banned_pattern>Using `@field_validator` for simple bounds checking or regex.</banned_pattern>
        <mandatory_pattern>ALWAYS prefer native `Field(ge=0, pattern=...)`. Native Field is executed in Rust (pydantic-core) at lightning speed.</mandatory_pattern>
        <code_example>
            <anti_pattern>@field_validator('age') ... if v < 18: raise ValueError()</anti_pattern>
            <pro_pattern>age: int = Field(ge=18)</pro_pattern>
        </code_example>
    </rule_block>

    <rule_block id="frozen_state_mutability">
        <banned_pattern>Mutating domain objects in place (e.g., `event.status = 'done'`).</banned_pattern>
        <mandatory_pattern>All Event Sourcing models, DTOs, and DAG nodes MUST be immutable using `ConfigDict(frozen=True)`. Transition states strictly via `event.model_copy(update={'status': 'done'})`.</mandatory_pattern>
    </rule_block>

    <rule_block id="polymorphic_routing_o1">
        <banned_pattern>Using implicit Unions or Python structural type-checking `isinstance()` chains with polymorphic DAG nodes.</banned_pattern>
        <mandatory_pattern>Mandate Discriminated Unions (`Field(discriminator='type')`) for O(1) parsing. Use native Python 3.10+ match cases: `match event: case EventA():`.</mandatory_pattern>
    </rule_block>

    <rule_block id="python_314_modern_syntax">
        <banned_pattern>Using legacy wrapper typings (`TypeVar`, `Generic[T]`, `Optional[X]`) or `asyncio.gather()`.</banned_pattern>
        <mandatory_pattern>Mandate PEP 695 generics (`def process[T](data: T) -> T:`), the `@override` decorator, modern bitwise unions (`X | None`), and deterministically scoped threads (`async with asyncio.TaskGroup() as tg:`).</mandatory_pattern>
    </rule_block>

    <rule_block id="no_string_l10n">
        <banned_pattern>Hardcoding application vocabulary, UI display strings, or string comparisons inside the backend code.</banned_pattern>
        <mandatory_pattern>Backend APIs MUST resolve to Enum Keys (e.g. `AUTH_ORGANIC`). Raw UI rendering string resolution is deferred purely to Flutter `.arb` runtime evaluation.</mandatory_pattern>
    </rule_block>
    
    <rule_block id="data_leak_prevention_firewall">
        <banned_pattern>Returning raw DB models natively out of FastAPI endpoints, bypassing Pydantic filtering, or defining `exclude=True` locally in Routers for security fields.</banned_pattern>
        <mandatory_pattern>Every single FastAPI router MUST explicitly define `response_model=UserDTO` (which must inherit from a global `BaseResponseDTO`) to strip hidden database variables out of the HTTP response string globally, effectively preventing Cross-Tenant Trace Leaks.</mandatory_pattern>
    </rule_block>

    <rule_block id="llm_structured_execution_mandate">
        <banned_pattern>Directly calling OpenAI/VertexSDKs, relying on raw text outputs, parsing responses with Regex, or calling LLMClient methods directly for business logic.</banned_pattern>
        <mandatory_pattern>You MUST initialize the execution via `LLMClient.from_strategy("strategy_name", repo)` and pass it to an injected `LLMTaskExecutor`. For data retrieval, rely ONLY on the `executor.execute_structured_task()` methodology to force Fail-Fast Pydantic parsing and centralized healing. If doing open-text generation, use `executor.execute_chat_task()`.</mandatory_pattern>
    </rule_block>

    <rule_block id="ui_driven_synthesis_boundary">
        <banned_pattern>Hardcoding UI-defined data keys (e.g., `product_text`, `document_text`) in backend Python code, or blindly feeding the entire raw execution state (including Eager Extracted PDF dumps) to an LLM during the synthesis/reporting phase.</banned_pattern>
        <mandatory_pattern>Backend reporting and synthesis hooks MUST strictly filter data based on the UI-defined `target_blocks` (Output Profile Layouts). The raw `inputs` dictionary must be unpacked and evaluated strictly against this UI configuration to prevent massive token explosions (1.04M limits) from background data dumps.</mandatory_pattern>
        <catastrophic_reason>Backend coupling to dynamic UI nomenclature breaks workflow relations. Pushing unfiltered execution state into an LLM context invariably causes `Resource Exhausted` limit triggers due to heavy Eager Extraction blobs intentionally stored in the execution state.</catastrophic_reason>
    </rule_block>
    <rule_block id="strict_math_display_isolation">
        <banned_pattern>Using database configuration keys `scale_min` and `scale_max` to calculate backend mathematical scores, or using them as fallback bounds for the internal execution engine.</banned_pattern>
        <mandatory_pattern>The scoring math engine MUST derive internal mathematical boundaries exclusively from the strictly typed Pydantic `scales` array (`min(scales)` and `max(scales)` assigned to strictly named `math_min` and `math_max` variables). The Database config fields `scale_min` and `scale_max` MUST ONLY be used as UI projection boundary targets (`display_min` and `display_max`) for cosmetic school-grade scaling (e.g. 4-10) before sending to the frontend. If the Display bounds are missing in the DB, trigger a 500 Fail-Fast ConfigurationError rather than attempting to guess them.</mandatory_pattern>
        <catastrophic_reason>Conflating calculation bounds with UI display projections corrupts the empirical accuracy of the cognitive diagnostic model and fundamentally violates Single Source of Truth architecture. The LLM or the Backend must NEVER calculate "hunches" via cross-contamination.</catastrophic_reason>
    </rule_block>

    <rule_block id="zero_orm_bleed">
        <banned_pattern>Returning raw DB dictionaries directly from Repository to API routers.</banned_pattern>
        <mandatory_pattern>The Repository layer is an absolute firewall. Raw records MUST be mapped into strict Pydantic Domain Models (`ConfigDict(frozen=True)`).</mandatory_pattern>
        <code_example>
            <anti_pattern>return db.table('users').get(doc_id=1)</anti_pattern>
            <pro_pattern>return UserDTO.model_validate(raw[0])</pro_pattern>
        </code_example>
    </rule_block>

    <rule_block id="strict_dependency_injection">
        <banned_pattern>Instantiating services or databases directly inside FastAPI routers.</banned_pattern>
        <mandatory_pattern>Dependencies MUST be injected exclusively via FastAPI's `Depends()` + PEP 593 `Annotated`.</mandatory_pattern>
        <code_example>
            <anti_pattern>service = UserService()</anti_pattern>
            <pro_pattern>
                DatabaseSession = Annotated[Session, Depends(get_database)]
                async def route(db: DatabaseSession): ...
            </pro_pattern>
        </code_example>
    </rule_block>

    <rule_block id="global_settings_import">
        <banned_pattern>Importing `get_settings` locally inside a function (e.g., `from backend_v2.settings import get_settings` inside `def`).</banned_pattern>
        <mandatory_pattern>ALWAYS import `get_settings` globally at the top of the file. In unit tests, `monkeypatch` MUST target the module where it is used (e.g., `backend_v2.hooks.scoring.get_settings`), NOT `backend_v2.settings.get_settings`.</mandatory_pattern>
        <catastrophic_reason>Local imports create fragmented mutable references that silently bypass `pytest` monkeypatching, causing unit tests to execute against uncontrollable production configs.</catastrophic_reason>
    </rule_block>

    <rule_block id="no_inline_imports">
        <banned_pattern>Using inline imports (importing modules inside a function, method, or router) to resolve circular dependencies or lazy load modules.</banned_pattern>
        <mandatory_pattern>ALWAYS declare all imports globally at the top of the file. If you encounter a circular dependency, you MUST refactor the architectural flaw by extracting the shared domain logic into a separate utility or base module. Do NOT hide it with an inline import.</mandatory_pattern>
        <catastrophic_reason>Inline imports mask circular dependencies, indicating broken domain boundaries. They introduce runtime overhead, obscure module dependencies, and frequently break `pytest` monkeypatching and dependency injection.</catastrophic_reason>
    </rule_block>

    <rule_block id="cross_language_enum_parity">
        <banned_pattern>Encoding UI rendering logic in Pydantic `Literal` or `Enum` variables without enforcing parity on the Flutter client, leading to silent 'Contains' parsing failures in Dart UI.</banned_pattern>
        <mandatory_pattern>All cross-boundary Pydantic fields controlling UI lists or presets MUST map to a strict `@JsonEnum()` inside `client_app_v2/lib/core/models/enums.dart`. A corresponding Regex-based `test_enum_parity.py` MUST be enforced to crash Pytest immediately if Flutter fails to mirror a new Backend Literal/Enum.</mandatory_pattern>
        <catastrophic_reason>Without explicitly tested Enum parity, the UI dynamically collapses or drops missing fields when the backend introduces a new type, leading to severe dataloss (e.g., dropping 3D coordinates because the UI reverted to a 1D default).</catastrophic_reason>
    </rule_block>

    <rule_block id="schema_driven_routing">
        <banned_pattern>Using "Duck Typing" or blind `try...except` Pydantic validation (e.g. `if "raw_score" in dict`) to guess the type of a payload during orchestration or parsing.</banned_pattern>
        <mandatory_pattern>ALWAYS look at the Database (UI configuration) first. Types and processing routes MUST be explicitly dictated by a `schema_map` derived from the database (e.g., Workflow or V2Step definitions). If a payload needs to be processed as a MATRIX block, the orchestrator must know it is a MATRIX block *before* parsing, based purely on the database's map, never by guessing based on JSON keys.</mandatory_pattern>
        <catastrophic_reason>Duck typing breaks the "Single Source of Truth / De-Generator" architecture. If the UI defines an entity as a TEXT block, but it happens to coincidentally contain a `raw_score` key, duck typing will silently hijack it, bypassing the UI's explicit sovereignty and causing untraceable Fail-Fast violations down the line.</catastrophic_reason>
    </rule_block>

    <rule_block id="prompt_compiler_immutability">
        <banned_pattern>Modifying the `backend_v2/services/orchestrator/prompt_compiler.py` file.</banned_pattern>
        <mandatory_pattern>The Prompt Compiler is a frozen architectural cornerstone. Do NOT touch this file. If a change is absolutely necessary, you must explicitly flag it and seek USER CONFIRMATION before making any edits.</mandatory_pattern>
        <catastrophic_reason>Altering the Prompt Compiler risks breaking the deterministic synthesis pipeline, Schema V2 generation, and the core Fail-Fast architecture.</catastrophic_reason>
    </rule_block>

    <rule_block id="tripartite_rendering_boundary">
        <banned_pattern>Hardcoding UI components, layout structures, or Markdown tables directly within backend generation hooks (e.g., generating Matrix Summary tables via Python string concatenation).</banned_pattern>
        <mandatory_pattern>Backend services MUST return pure data payloads (Pydantic DTOs). Enforce the Tripartite Rendering Boundary: The Backend passes structured data, Flutter handles interactive UI rendering, and Jinja generates static PDFs. UI responsibilities MUST NOT bleed into the backend.</mandatory_pattern>
        <catastrophic_reason>Violating this boundary results in duplicate UI artifacts (e.g., Markdown tables rendered above native components), breaks cross-platform i18n capabilities, and pollutes synthesis contexts with redundant display logic.</catastrophic_reason>
    </rule_block>

    <rule_block id="zero_type_ignore_shortcuts">
        <banned_pattern>Using `# type: ignore` arbitrarily to silence MyPy without investigating the root cause or refactoring the underlying Pydantic/Domain types.</banned_pattern>
        <mandatory_pattern>ALWAYS investigate the root cause of a typing error. Fix the actual variable types, models, or function signatures. If an external library boundary forces a type violation that absolutely cannot be fixed natively, you MUST use a strictly scoped ignore marker with the exact error code (e.g., `# type: ignore[attr-defined]`) AND provide a comment explaining the external constraint. Blanket ignores are strictly forbidden.</mandatory_pattern>
        <catastrophic_reason>Overusing type ignores defeats the purpose of strict typing, allowing 'Any' or disjointed types to leak into the Fail-Fast domain logic, inevitably causing 500 Internals or UI rendering crashes downstream.</catastrophic_reason>
    </rule_block>
</architectural_invariants>

<testing_and_verification_mandate>
    <instruction>Executing Python tooling ALWAYS requires this explicit unified format calling the audit loop script:</instruction>
    <command>`uv run python scripts/backend_audit_loop.py backend_v2/[TARGET_FILES] --openapi`</command>
    
    <rule_block id="zero_deprecation">
        <banned_pattern>Calling code "Complete" while legacy APIs throw `DeprecationWarning` or typing reports an error.</banned_pattern>
        <mandatory_pattern>Proactively replace any deprecated members and clean all typing errors before signaling task finalization. Code MUST NOT be pushed if `Pytest` automated coverage is missing or failing.</mandatory_pattern>
    </rule_block>
</testing_and_verification_mandate>