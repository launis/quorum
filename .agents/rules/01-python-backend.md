# BACKEND ARCHITECTURE CONSTRAINTS

*** UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS FOR PYTHON ***

<domain_boundary>
    <role>RUNTIME & LOGIC ONLY</role>
    <instruction>These rules apply STRICTLY to Python (.py) execution logic, memory states, and Pydantic schemas. If you need to modify baseline JSON data or database configurations, you MUST halt and read `03_seed_vault.md` first.</instruction>
</domain_boundary>

<catastrophic_system_bans>
    <rule_block id="the_duct_tape_ban">
        <banned_pattern>"God Blocks" (`except Exception: pass`), returning empty dicts `{}` on failure, or using `.get("key", default)` to suppress missing data.</banned_pattern>
        <mandatory_pattern>All errors MUST be caught, logged, and re-raised via `AppException`. Rely strictly on Pydantic validation. The architectural mandate from `hardening.xml` strictly forbids "Duct-Tape" programming.</mandatory_pattern>
        <catastrophic_reason>Duct-tape fixes mask root causes, corrupt data flows, and violate the Zero-Compromise Pledge.</catastrophic_reason>
    </rule_block>
    
    <rule_block id="prompt_fragmentation_ban">
        <banned_pattern>Scattering LLM prompt instructions, structural JSON mandates, or logic constraints directly inside business methods or client wrappers (e.g., `client.py`).</banned_pattern>
        <mandatory_pattern>ALL global prompt instructions MUST be centralized in `directives.py` as explicit string constants. Treat `directives.py` as the absolute Single Source of Truth for LLM constraints.</mandatory_pattern>
        <catastrophic_reason>Fragmented prompt logic causes undetectable context degradation, violates DRY architecture, and prevents systemic oversight of LLM behavior.</catastrophic_reason>
    </rule_block>

    <rule_block id="docstring_fail_fast_ban">
        <banned_pattern>Documenting `Raises: None` in method docstrings, OR duplicating Python type hints (e.g. `type[BaseModel]:`) inside `Args:` or `Returns:` text.</banned_pattern>
        <mandatory_pattern>NEVER write `Raises: None`. You MUST explicitly list the exact `AppException` error codes the execution can trigger. Enforce strictly DRY typing (never repeat type hints in text).</mandatory_pattern>
        <catastrophic_reason>Claiming a function raises nothing creates false confidence in the Fail-Fast architecture, leading to unhandled downstream exceptions. DRY typing violations break doc generators and clutter the context.</catastrophic_reason>
    </rule_block>

    <rule_block id="inline_imports_ban">
        <banned_pattern>Using inline imports inside methods/functions to avoid circular dependencies.</banned_pattern>
        <mandatory_pattern>ALL standard imports MUST be declared globally at the top of the file. EXCEPTION: Heavy AI/ML libraries (e.g., `litellm`, `vertexai`, `spacy`) MUST be imported inside methods/functions (lazy loading) to prevent PyO3 failures and Zero Cold Starts.</mandatory_pattern>
        <catastrophic_reason>Inline imports mask severe circular architectural dependencies and silently crash asynchronous unit tests (`pytest`) when mocking paths.</catastrophic_reason>
    </rule_block>

    <rule_block id="slug_data_relation_ban">
        <banned_pattern>Using `slug`, UI labels, or other informational fields as JSON schema keys, Pydantic field names, or for strict data relations.</banned_pattern>
        <mandatory_pattern>ALWAYS use the object's `id` (e.g., the opaque Stripe-pattern ID `blk_123...`) for ALL data relations, schema generation, and dictionary key bindings.</mandatory_pattern>
        <catastrophic_reason>Slugs are highly mutable strings meant for SEO/Display. Binding system architecture or LLM JSON outputs to mutable slugs permanently breaks data extraction and causes undetected key-collisions.</catastrophic_reason>
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

    <rule_block id="de_generator_mandate_no_xml">
         <banned_pattern>Using XML tags like `<system_directive>`, `<role>`, or `<objective>` inside `seed_data.json` prompt fields (`ai_description`, `system_prompt`).</banned_pattern>
         <mandatory_pattern>Enforce the "De-Generator" mandate: write pure business logic using Markdown headings (e.g. `ROLE:`, `OBJECTIVE:`). The backend `prompt_factory.py` automatically handles all necessary XML wrappers for the LLM.</mandatory_pattern>
    </rule_block>
</catastrophic_system_bans>

<architectural_invariants>
    <rule_block id="pydantic_annotated_fields_mandate">
        <banned_pattern>Using bare type hints combined with a `Field(...)` assignment in Pydantic settings or models (e.g., `timeout: int = Field(...)`).</banned_pattern>
        <mandatory_pattern>ALWAYS use PEP 593 `Annotated` syntax to separate pure Python types from Pydantic runtime metadata (e.g., `timeout: Annotated[int, Field(description="...")] = 10`).</mandatory_pattern>
        <catastrophic_reason>Bare assignments violate strict type-checkers (like Mypy) because they assign a `FieldInfo` object to an `int` type. `Annotated` ensures 100% type purity and compatibility.</catastrophic_reason>
    </rule_block>

    <rule_block id="opaque_stripe_id_mandate">
        <banned_pattern>Using auto-incrementing integers (e.g., `id=1`), raw UUIDs leaking database context, or semantic strings like `slug` as primary keys, database references, or API route identifiers.</banned_pattern>
        <mandatory_pattern>Enforce the "Opaque Stripe ID" pattern (e.g., `wor_a1b2c3d4`, `usr_x9y8z7`) for ALL database identifiers, cross-model relations, and navigation endpoints. Slugs are for SEO/Display purposes only, NEVER for strict data relationships.</mandatory_pattern>
        <catastrophic_reason>Intelligible primary keys (slugs) lead to permanently broken foreign relations when a user edits the display name. Auto-increment IDs allow horizontal enumeration attacks (IDOR). Opaque prefix mapping ensures immediate visual typability during debugging and inherently secures the API.</catastrophic_reason>
    </rule_block>

    <rule_block id="alias_engine_llm_isolation_mandate">
        <banned_pattern>Passing raw database UUIDs or Opaque Stripe IDs (e.g., `tda_a1b2c3d4`) directly into LLM prompts, JSON schemas, or expecting the LLM to output them back.</banned_pattern>
        <mandatory_pattern>ALWAYS use the `AliasEngine` to generate short, semantic aliases (e.g., `a0`, `doc1`, `cond0`) before sending data to the LLM. When the LLM responds with these aliases (e.g., `depends_on: ["a0"]`), use `AliasEngine.hydrate_dict_list()` to deterministically map them back to the original Opaque UUIDs.</mandatory_pattern>
        <catastrophic_reason>LLMs are textual reasoners that hallucinate and lose context when forced to copy 32-character hex strings. Semantic aliases act as explicit "Attention Anchors", drastically reducing hallucination rates, cutting token bloat, and ensuring deterministic Pydantic validation via `AliasEngine.ALIAS_REGEX_PATTERN`.</catastrophic_reason>
    </rule_block>

    <rule_block id="strict_pydantic_v2_rust">
        <banned_pattern>Using legacy V1 instantiation (`MyModel(**data)`), Python standard JSON parsing (`json.loads()`), legacy V1 methods (`.dict()`, `@validator`), or using duck typing / arbitrary type checks like `hasattr(obj, 'key')` and `isinstance(data, dict)` to parse incoming LLM or DB state.</banned_pattern>
        <mandatory_pattern>Force the Fail-Fast pipeline by using `.model_validate()`, Rust-based `.model_validate_json()`, `.model_dump()`, and `@field_validator`. Use `model_config = ConfigDict(extra='forbid', strict=True)` to reject unstructured AI outputs instantly. Any structure not matching the strict model must CRASH immediately with a `ValidationError`.</mandatory_pattern>
    </rule_block>

    <rule_block id="zero_legacy_fallback_hacks">
        <banned_pattern>Adding `@model_validator(mode="before")` or optional union types (`| None`) to Pydantic models purely to silently scrub or appease old V1 legacy payload fields (e.g., `task_key`) from crashing `extra='forbid'`.</banned_pattern>
        <mandatory_pattern>NEVER bypass Pydantic `extra='forbid'` strictness to accommodate dirty databases. If historical data causes validation crashes, the root cause MUST be fixed at the source by wiping the seed data (via `uv run python backend_v2/seed/run_seed.py local`). Pydantic models must remain mathematically pure to the V2 spec.</mandatory_pattern>
        <catastrophic_reason>Writing fallback parsing logic pollutes the domain layer with historical technical debt, destroying the Fail-Fast architecture and silently allowing legacy structures to persist and mutate inside V2 pipelines.</catastrophic_reason>
    </rule_block>

    <rule_block id="pydantic_pure_hydration_boundary">
        <banned_pattern>Using `json.dumps(data, default=str)` hacks or temporarily stripping `strict=True` from the Pydantic model's `ConfigDict` just to parse raw database dictionaries containing mixed ISO strings and Python `datetime`/`UUID` objects.</banned_pattern>
        <mandatory_pattern>Models MUST maintain `model_config = ConfigDict(strict=True)` to strictly firewall the FastAPI incoming API boundary. When hydrating data FROM the trusted internal database (Repository Layer), you MUST use `MyModel.model_validate(data, strict=False)`. This is the pure Pydantic V2 Best Practice, allowing native Rust coercion of strings to datetimes at the database boundary without the massive CPU overhead of double-serialization or permanently polluting the model's strictness configuration.</mandatory_pattern>
        <catastrophic_reason>Using `json.dumps()` on fully-hydrated Python dicts causes `TypeError: Object of type datetime is not JSON serializable`. Stripping `strict=True` from the global model config breaks the Zero-Trust Fail-Fast architecture at the API layer, allowing malicious user payloads to bypass type safety.</catastrophic_reason>
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
        <banned_pattern>Using legacy wrapper typings (`TypeVar`, `Generic[T]`, `Optional[X]`), forward references with strings for class returns (e.g. `-> "MyClass"`), or `asyncio.gather()`.</banned_pattern>
        <mandatory_pattern>Mandate PEP 695 generics (e.g. `class Repository[T]:`), the `@override` decorator, modern bitwise unions (`X | None`), and deterministically scoped threads (`async with asyncio.TaskGroup() as tg:`). For classmethods returning the class itself, ALWAYS use PEP 673 `-> Self` (via `from typing import Self`) to ensure correct inheritance typing.</mandatory_pattern>
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
        <banned_pattern>Assuming that database config fields `scale_min` and `scale_max` dictate what scales are "in use" or using them to calculate backend mathematical scores. Using them as fallback bounds for the internal execution engine.</banned_pattern>
        <mandatory_pattern>The scoring math engine MUST derive internal mathematical boundaries exclusively from the strictly typed Pydantic `scales` array (`min(scales)` and `max(scales)` assigned to strictly named `math_min` and `math_max` variables). The Database config fields `scale_min` and `scale_max` do NOT represent the scales in use; they are ONLY for scoring scaling/stretching (UI projection boundary targets, mapped to `display_min` and `display_max` in Python) for cosmetic school-grade scaling (e.g. 4-10) before sending to the frontend. If the Display bounds are missing in the DB, trigger a 500 Fail-Fast ConfigurationError rather than attempting to guess them.</mandatory_pattern>
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

    <rule_block id="strict_configuration_segregation">
        <banned_pattern>Mixing global constraints, taxonomy values, and runtime instantiation into single files, or using magic numbers instead of global configurations.</banned_pattern>
        <mandatory_pattern>Enforce the Tripartite Configuration Architecture: 1) `enums.py` MUST contain ONLY finite string/int constants and taxonomy vocabulary (No logic, no environment variables). 2) `settings.py` MUST contain ALL global limits, bounds, and environment-dependent configuration. 3) DTOs (e.g., `models/llm.py`) MUST act as the blueprints that combine `enums.py` and `settings.py` during runtime execution. No "Magic Numbers" allowed in business logic.</mandatory_pattern>
        <catastrophic_reason>Violating this separation creates untraceable hidden dependencies (e.g., hardcoded chunk boundaries failing when global limits change) and destroys the Single Responsibility Principle for system limits.</catastrophic_reason>
    </rule_block>

    <rule_block id="global_settings_import">
        <banned_pattern>Importing `get_settings` locally inside a function (e.g., `from backend_v2.settings import get_settings` inside `def`).</banned_pattern>
        <mandatory_pattern>ALWAYS import `get_settings` globally at the top of the file. In unit tests, `monkeypatch` MUST target the module where it is used (e.g., `backend_v2.hooks.scoring.get_settings`), NOT `backend_v2.settings.get_settings`.</mandatory_pattern>
        <catastrophic_reason>Local imports create fragmented mutable references that silently bypass `pytest` monkeypatching, causing unit tests to execute against uncontrollable production configs.</catastrophic_reason>
    </rule_block>

    <!-- Rule elevated to CATASTROPHIC SYSTEM BANS (epic90_inline_imports_ban) -->

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

    <rule_block id="zero_db_hardcoding_mandate">
        <banned_pattern>Comparing logical conditions against hardcoded specific database IDs, strings, or names (e.g., `if node.id == "usr_123":` or `if block.slug == "main_matrix":`). Extracting elements from lists by assuming a hardcoded sort order (e.g., `first_block = db_result[0]`).</banned_pattern>
        <mandatory_pattern>Logic MUST always be based on the abstract attributes, schema types (via Pydantic Discriminators like `isinstance(block, MatrixBlockDTO)`), or dynamically injected configuration values. Database-driven entity processing must be purely polymorphic, without reliance on magic strings.</mandatory_pattern>
        <catastrophic_reason>Hardcoding database keys inside the backend architecture breaks isolation. When environments (e.g., Staging vs Production) drift or database schemas evolve, hardcoded keys result in immediate catastrophic logic failures and make tests impossible without massive data mocking.</catastrophic_reason>
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

    <rule_block id="execution_synthesis_tier_decoupling">
        <banned_pattern>Placing UI-formatting logic (e.g., "Output exactly ONE punchy sentence", 0-100 scales) in `PromptBlocks` or placing execution-tier directives (e.g., `ROLE: ANTAGONISTIC PROSECUTOR`, boolean hypothesis testing) in `OutputProfiles`.</banned_pattern>
        <mandatory_pattern>Strictly separate the Execution Phase from the Reporting Phase. `PromptBlocks` are EXCLUSIVELY for raw data evaluation (native scales like 1-5, ZERO-TRUST AUDITOR directives, atomic extraction) and MUST NOT contain UI formatting logic. `OutputProfiles` are EXCLUSIVELY for presentation and UI formatting (0-100 scales, brevity constraints, tone) and MUST NOT contain execution directives like hypothesis testing.</mandatory_pattern>
        <catastrophic_reason>Mixing these concerns causes LLM hallucinations, slows down generation, breaks the Single Source of Truth, and pollutes the execution trace with presentation details.</catastrophic_reason>
    <rule_block id="fail_fast_hydration_mandate">
        <banned_pattern>Fishing for dictionary values via `dict.get()`.</banned_pattern>
        <mandatory_pattern>All uncertain data flowing as dictionaries MUST be hydrated via `.model_validate()` IMMEDIATELY before processing.</mandatory_pattern>
        <catastrophic_reason>Delaying hydration allows invalid data structures to penetrate deep into execution logic, making root-cause stack traces impossible to decipher.</catastrophic_reason>
    </rule_block>
    <rule_block id="annotated_hydration_mandate">
        <banned_pattern>Converting enums manually using `if/else` checks or external dictionaries.</banned_pattern>
        <mandatory_pattern>External data enum conversions MUST be mapped exclusively using `Annotated[CustomEnum, Field(strict=False)]` aliases defined in `enums.py`.</mandatory_pattern>
        <catastrophic_reason>Manual enum parsing duplicates logic and bypasses Pydantic's Rust-based optimized C-core coercion.</catastrophic_reason>
    </rule_block>
    <rule_block id="vertex_serving_grammar_fix">
        <banned_pattern>Float type field constraints (e.g., ge, le) at the `Field()` level.</banned_pattern>
        <mandatory_pattern>Float constraints MUST NOT be applied at the `Field()` level to avoid Vertex AI 400 errors. Move them to local `@field_validator` methods.</mandatory_pattern>
        <catastrophic_reason>Vertex AI SDK strict JSON schema parser crashes natively with HTTP 400 when encountering float constraints nested inside object parameter definitions.</catastrophic_reason>
    </rule_block>
    <rule_block id="blind_extraction_null_hypothesis">
        <banned_pattern>Allowing the LLM to output both an `exact_quote` and flag `contextual_override == True` simultaneously.</banned_pattern>
        <mandatory_pattern>TDA extraction models MUST force the null hypothesis via `@model_validator`: If `contextual_override == True`, the `exact_quote` field MUST be forced to `None`.</mandatory_pattern>
        <catastrophic_reason>Failing to force this nullification allows hallucinated quotes to bypass the override logic, polluting the empirical audit reports.</catastrophic_reason>
    </rule_block>
    <rule_block id="zero_defaults_mandate">
        <banned_pattern>Using mutable types (e.g., list, dict) as default arguments (B006) or defaulting critical data.</banned_pattern>
        <mandatory_pattern>DTO models MUST NOT use default values if the missing data is critical. Always use `None` and initialize the mutable object inside the function block.</mandatory_pattern>
        <catastrophic_reason>Mutable defaults leak state across asynchronous requests, causing massive Cross-Tenant Data Leaks where User A sees User B's execution data.</catastrophic_reason>
    </rule_block>
    <rule_block id="duck_typing_token_shield_exception">
        <banned_pattern>The `extra="ignore"` configuration in Pydantic.</banned_pattern>
        <mandatory_pattern>STRICTLY PROHIBITED at all times, with the absolute exception of `SynthesisStepDataDTO`, Token Shield classes, and internal Data Projection Models.</mandatory_pattern>
        <catastrophic_reason>Ignoring extra payload data masks Prompt Injection attempts and suppresses critical validation warnings on outdated schemas.</catastrophic_reason>
    </rule_block>
    <rule_block id="python_314_root_model_ban">
        <banned_pattern>Using `RootModel` to enforce dynamic TypeAdapter patterns.</banned_pattern>
        <mandatory_pattern>Always wrap standard types dynamically using the `TypeAdapter` pattern instead. Example: `TypeAdapter(list[UserDTO]).validate_python(data)`.</mandatory_pattern>
        <catastrophic_reason>RootModel inherits heavy metaclasses which consume massive memory overhead during runtime array parsing in Python 3.14.</catastrophic_reason>
    </rule_block>
    <rule_block id="append_only_state_mutation">
        <banned_pattern>In-place mutation of `execution_trace` or `step_states`.</banned_pattern>
        <mandatory_pattern>Historical payload data MUST NEVER be overwritten via in-place mutation. Dynamic projections MUST be executed on-the-fly into newly instantiated DTO models.</mandatory_pattern>
        <catastrophic_reason>In-place mutation destroys the linear Forensic Audit Trail, invalidating the legal compliance of the cognitive execution.</catastrophic_reason>
    </rule_block>
    <rule_block id="base64_amnesia_protocol">
        <banned_pattern>Persisting raw base64 data or binaries within Pydantic states.</banned_pattern>
        <mandatory_pattern>They must be extracted into text representations via the Eager Extraction pattern at the boundary layer.</mandatory_pattern>
        <catastrophic_reason>Raw binaries bypass textual token tracking, inflate TinyDB filesizes beyond RAM capacity, and crash frontend JSON parsers instantly.</catastrophic_reason>
    </rule_block>
    <rule_block id="dlq_arq_fallback_routing">
        <banned_pattern>A Worker crashing the entire execution tree with a direct unhandled exception.</banned_pattern>
        <mandatory_pattern>TaskGroup or ChunkWorker errors MUST be routed to the Dead Letter Queue by yielding `{"_dlq_status": "FAILED/DLQ"}`.</mandatory_pattern>
        <catastrophic_reason>An unhandled exception within a single worker will immediately cancel the entire asyncio.TaskGroup, destroying hours of valid parallel LLM processing.</catastrophic_reason>
    </rule_block>
    <rule_block id="the_self_healing_ban">
        <banned_pattern>Attempting to dynamically patch AI-generated quotes or JSON formatting errors on-the-fly using Regex.</banned_pattern>
        <mandatory_pattern>Data validation belongs 100% to Pydantic.</mandatory_pattern>
        <catastrophic_reason>Regex patching creates recursive self-healing loops that mask severe Prompt Model degradation, ensuring the actual AI problem is never fixed.</catastrophic_reason>
    </rule_block>
    <rule_block id="md5_hashery_ban">
        <banned_pattern>`hashlib.md5` and `hashlib.sha1` for dynamic ID generation.</banned_pattern>
        <mandatory_pattern>Utilize `uuid.uuid4().hex[:8]`. For cryptographic operations, the standard `random` module is forbidden; always enforce `secrets`.</mandatory_pattern>
        <catastrophic_reason>MD5 is cryptographically broken and creates high collision probability in high-throughput chunking, causing silent data overwrite.</catastrophic_reason>
    </rule_block>
    <rule_block id="high_fidelity_prompting">
        <banned_pattern>Using f-strings for foundational core rules.</banned_pattern>
        <mandatory_pattern>Prompt core instructions MUST remain static. Dynamic execution variables MUST be isolated within an `<execution_parameters>` tag. Input data must be rigidly wrapped in `<source_data>`.</mandatory_pattern>
    </rule_block>
    <rule_block id="single_source_of_truth_mandate">
        <banned_pattern>V1 and V2 models coexisting.</banned_pattern>
        <mandatory_pattern>Ruthlessly purge deprecated V1-era fallback hacks, `.get()` coalescing chains, and `@model_validator` retrofits handling legacy data payloads.</mandatory_pattern>
        <catastrophic_reason>V1 data shapes cause infinite polymorphism crashes when the V2 parser attempts to resolve legacy nested loops.</catastrophic_reason>
    </rule_block>
    <rule_block id="native_english_generation">
        <banned_pattern>Prompting the Language Model to translate cognitive reasoning logic on-the-fly.</banned_pattern>
        <mandatory_pattern>Cognitive reasoning is formulated natively in English; UI localization is handled strictly in a downstream translation phase.</mandatory_pattern>
        <catastrophic_reason>Forcing translation simultaneously with logical evaluation degrades the LLM's IQ, resulting in severe reasoning errors.</catastrophic_reason>
    </rule_block>
    <rule_block id="hybrid_prompting_mandate">
        <banned_pattern>Constructing prompts using pure unstructured text.</banned_pattern>
        <mandatory_pattern>System prompts MUST use a hybrid of XML for structural control and Markdown for nested content formatting.</mandatory_pattern>
        <catastrophic_reason>Without XML, modern LLMs suffer from 'Attention Dilution' and bleed constraints across instruction boundaries.</catastrophic_reason>
    </rule_block>
    <rule_block id="role_segregation_and_fencing">
        <banned_pattern>Injecting raw user text directly into the system prompt.</banned_pattern>
        <mandatory_pattern>Always fence untrusted user payloads with clear XML tags (specifically `<user_payload>...</user_payload>`) as a firewall against prompt injection attacks.</mandatory_pattern>
        <catastrophic_reason>Unfenced data allows malicious payloads to hijack the role execution, bypassing the entire security layer.</catastrophic_reason>
    </rule_block>
    <rule_block id="infinite_retry_loops">
        <banned_pattern>Infinite retry loops on failed schema validations.</banned_pattern>
        <mandatory_pattern>Enforce an absolute max retry limit of 2 using `SystemConcurrency.LLM_MAX_RETRIES`; if it fails, trigger Fail-Fast.</mandatory_pattern>
    </rule_block>
    <rule_block id="system_concurrency_ssot">
        <mandatory_pattern>Parallel async LLM steps must use `asyncio.TaskGroup` constrained by `asyncio.Semaphore(SystemConcurrency.MAX_CONCURRENT_LLM_STEPS)`.</mandatory_pattern>
    </rule_block>
    <rule_block id="strict_physical_anchoring_mandate">
        <banned_pattern>Fuzzy string matching for evidence extraction.</banned_pattern>
        <mandatory_pattern>All evidence extractions must be validated using deterministic O(N) physical anchoring via `str.find` on normalized strings. If not found, raise `SemanticEvidenceError` immediately.</mandatory_pattern>
    </rule_block>
    <rule_block id="ensemble_parallel_evaluation_mandate">
        <mandatory_pattern>Execute high-entropy or negative validation steps using a single-pass 'Best-of-3' voting ensemble across parallel LLM calls wrapped in `asyncio.TaskGroup`.</mandatory_pattern>
    </rule_block>
    <rule_block id="pep257_google_style_docstrings">
        <mandatory_pattern>Every module, class, and function MUST possess a PEP 257 compliant Google-style docstring starting with a concise Summary line terminating with a period.</mandatory_pattern>
    </rule_block>
    <rule_block id="google_style_functions_args_returns">
        <mandatory_pattern>Function docstrings MUST EXPLICITLY specify `Args:`, `Returns:`, and/or `Yields:` blocks as applicable, immediately following the summary description.</mandatory_pattern>
    </rule_block>
    <rule_block id="google_style_classes_separation">
        <mandatory_pattern>Class-level docstrings contain ONLY the overarching description and public `Attributes:`. The `__init__` method MUST encapsulate `Args:` and `Raises:`.</mandatory_pattern>
    </rule_block>
    <!-- Rules elevated to CATASTROPHIC SYSTEM BANS (epic90_docstring_fail_fast_ban) -->
    <rule_block id="free_threading_concurrency">
        <banned_pattern>Utilizing the `multiprocessing` module.</banned_pattern>
        <mandatory_pattern>All routines MUST be demonstrably thread-safe (Free-threading architecture). Employ lightweight threads or `asyncio`.</mandatory_pattern>
    </rule_block>
    <rule_block id="modern_type_aliases_pep695">
        <mandatory_pattern>Implement the PEP 695 `type` keyword for type aliases (e.g., `type Point = tuple[float, float]`).</mandatory_pattern>
    </rule_block>
    <rule_block id="taskgroup_exceptiongroup_mandate">
        <banned_pattern>`asyncio.gather`.</banned_pattern>
        <mandatory_pattern>Background routines MUST ALWAYS be orchestrated utilizing the `asyncio.TaskGroup` context. When trapping parallel exceptions, use the `ExceptionGroup` class and native `except*` syntax.</mandatory_pattern>
        <catastrophic_reason>asyncio.gather silently orphans running tasks when one fails, causing zombie executions that leak memory and keep database locks open.</catastrophic_reason>
    </rule_block>
    <rule_block id="idiomatic_pattern_matching">
        <banned_pattern>Verbose `if-elif` cascades used for data destructuring or type validation.</banned_pattern>
        <mandatory_pattern>Utilize native `match` and `case` structures.</mandatory_pattern>
        <catastrophic_reason>Cascades scale poorly in polymorphic routing, reducing readability and increasing the likelihood of unhandled edge cases.</catastrophic_reason>
    </rule_block>
    <rule_block id="pathlib_over_ospath">
        <banned_pattern>Invoking the legacy `os.path` module.</banned_pattern>
        <mandatory_pattern>Exclusively leverage the object-oriented `pathlib.Path` standard library module.</mandatory_pattern>
    </rule_block>
    <rule_block id="pep750_t_strings_only">
        <banned_pattern>Standard f-strings within critical data ingestion pathways.</banned_pattern>
        <mandatory_pattern>Construct dynamic LLM prompts and SQL statements exclusively utilizing Python 3.14 t-strings (Template Strings - PEP 750).</mandatory_pattern>
    </rule_block>
    <rule_block id="pep734_subinterpreters_for_cpu">
        <mandatory_pattern>Heavyweight CPU-bound background processes MUST be dispatched via the standard library `interpreters` module (subinterpreters) instead of `multiprocessing`.</mandatory_pattern>
    </rule_block>
    <rule_block id="pep742_typeis_over_typeguard">
        <banned_pattern>Legacy `typing.TypeGuard` for Type Narrowing operations.</banned_pattern>
        <mandatory_pattern>Always enforce `typing.TypeIs` (PEP 742).</mandatory_pattern>
    </rule_block>
    <rule_block id="anti_hallucination_guardrail">
        <banned_pattern>Hallucinating or inventing new Pydantic models.</banned_pattern>
        <mandatory_pattern>NEVER delete existing classes or enums assuming they are unused, as they are likely imported by other files. DO NOT invent import paths.</mandatory_pattern>
    </rule_block>
    <rule_block id="polymorphic_parsing_mandate">
        <mandatory_pattern>All Data Access Layer (Repository) methods MUST return raw `dict[str, Any]` to embrace NoSQL polymorphism. DO NOT enforce strict Pydantic DTOs at the database boundary.</mandatory_pattern>
    </rule_block>
    <rule_block id="zero_truncation_pledge">
        <banned_pattern>Truncating existing methods, classes, or complex implementations into `pass` stubs.</banned_pattern>
        <mandatory_pattern>Code output MUST be a fully functional, complete drop-in replacement that perfectly preserves the original logic.</mandatory_pattern>
    </rule_block>
    <rule_block id="strict_attribute_integrity">
        <banned_pattern>Converting strict dot-notation attribute access into dynamic `getattr(model, "model", "")` fallbacks.</banned_pattern>
        <mandatory_pattern>Embracing the Fail-Fast protocol requires relying on Pydantic's static structure. EXCEPTIONS: Safe checks using `in` operator.</mandatory_pattern>
    </rule_block>
    <rule_block id="api_service_separation_mandate">
        <banned_pattern>ID generation for new or cloned entities at the API Router boundary.</banned_pattern>
        <mandatory_pattern>MUST occur exclusively within the Service layer (e.g., `StudioService`).</mandatory_pattern>
    </rule_block>
    <rule_block id="setdefault_hydration_mandate">
        <banned_pattern>Complex conditional logic for hydration (e.g., `if "key" not in kwargs: kwargs["key"] = value`).</banned_pattern>
        <mandatory_pattern>When safely injecting fallback or configuration values, you MUST utilize Python's native `dict.setdefault("key", value)` method.</mandatory_pattern>
    </rule_block>
    <rule_block id="pydantic_configuration_enforcement">
        <banned_pattern>Tolerating loose `extra="allow"` or `extra="ignore"` configurations in primary domain models, or simply logging a warning when encountering them.</banned_pattern>
        <mandatory_pattern>You MUST ruthlessly enforce `model_config = ConfigDict(extra="forbid", strict=True)` on ALL Domain DTOs unless explicitly defined as a Token Shield. Loose models must be fixed immediately.</mandatory_pattern>
        <catastrophic_reason>Tolerating loose Pydantic configurations creates silent parsing vulnerabilities that bypass the Zero-Trust execution boundaries.</catastrophic_reason>
    </rule_block>
    <rule_block id="pydantic_v2_computed_field_order">
        <banned_pattern>`@property` over `@computed_field`.</banned_pattern>
        <mandatory_pattern>The `@computed_field` decorator MUST strictly be placed ABOVE the `@property` decorator, appending `# type: ignore[prop-decorator]`.</mandatory_pattern>
        <catastrophic_reason>Inverting the decorators causes Pydantic Core schema generation to crash entirely, breaking the OpenAPI JSON spec.</catastrophic_reason>
    </rule_block>
    <rule_block id="srp_god_method_mandate">
        <banned_pattern>Writing monolithic controller or service methods exceeding 50 lines of core logic.</banned_pattern>
        <mandatory_pattern>You MUST break down methods exceeding 50 lines into isolated, pure, private helper methods to uphold the Single Responsibility Principle.</mandatory_pattern>
        <catastrophic_reason>God methods are untestable via isolated unit tests and cause cascading logical failures during refactoring.</catastrophic_reason>
    </rule_block>
    <rule_block id="fail_fast_payload_length_mandate">
        <mandatory_pattern>Always enforce a strict minimum character length on extracted user text payloads BEFORE passing them to an LLM context window.</mandatory_pattern>
    </rule_block>
    <rule_block id="async_io_lock_isolation_mandate">
        <banned_pattern>Executing slow asynchronous I/O operations (like database commits) inside an `asyncio.Lock()` block.</banned_pattern>
        <mandatory_pattern>Implement a Two-Lock Strategy: release the memory lock instantly, trigger event completion, and use a separate commit lock for eventual DB consistency.</mandatory_pattern>
    </rule_block>
    <rule_block id="pydantic_mutation_optimization_mandate">
        <banned_pattern>Mutating existing Pydantic objects by triggering a full serialization cycle (`model_dump()`) followed by full re-instantiation.</banned_pattern>
        <mandatory_pattern>ALWAYS use `.model_copy(update={...})` for shallow C-level updates.</mandatory_pattern>
    </rule_block>
    <rule_block id="primitive_obsession_evidence_quotes">
        <banned_pattern>Packing complex data structures (like text + source reference) into a single string using pipe characters (|||).</banned_pattern>
        <mandatory_pattern>Use structured Pydantic models directly from the LLM output boundary.</mandatory_pattern>
    </rule_block>
    <rule_block id="immutable_history_snapshot">
        <banned_pattern>Live queries to the database for display names during render time.</banned_pattern>
        <mandatory_pattern>The backend presentation layer (BFF / blueprint) MUST produce UI strings from runtime frozen metadata (inputs-snapshot).</mandatory_pattern>
    </rule_block>
    <rule_block id="graceful_degradation_over_fail_fast">
        <banned_pattern>Allowing the entire execution graph to crash because a single hallucinated string field (like an optional UI label) failed parsing.</banned_pattern>
        <mandatory_pattern>While core logic follows Fail-Fast, hallucinated *peripheral* fields from stochastic LLMs MUST be defensively scrubbed (cast to `None`) inside `@model_validator` so the expensive run does not crash entirely.</mandatory_pattern>
        <catastrophic_reason>Crashing a $0.05 LLM execution trace just because an optional metadata field contained a typo destroys system reliability and inflates API costs.</catastrophic_reason>
    </rule_block>
    <rule_block id="declarative_set_logic_mandate">
        <banned_pattern>Using imperative `if x not in lst: lst.append(x)` loops or multiple `list(set(x))` conversions for uniqueness filtering and list aggregation.</banned_pattern>
        <mandatory_pattern>ALWAYS use Python's declarative Set operations (e.g. `set(a) | set(b)` or `my_set.update({"x", "y"})`) for uniqueness and aggregation. Convert to a sorted list (`sorted(list(my_set))`) only at the final assignment.</mandatory_pattern>
        <catastrophic_reason>Imperative list-checking is O(N) leading to O(N^2) loops, and scattered type-casting is memory inefficient and unreadable. Set mathematics guarantees O(1) uniqueness natively.</catastrophic_reason>
    </rule_block>
    <rule_block id="pydantic_discriminator_hallucination_prevention">
        <banned_pattern>Using `Field(discriminator='...')` in Pydantic Union models without setting a strict JSON schema title for each child model.</banned_pattern>
        <mandatory_pattern>ALWAYS explicitly set `model_config = ConfigDict(title="<discriminator_value>")` on every polymorphic child model. This guarantees that `model_json_schema()` uses the exact literal value as the title instead of the Python Class Name, preventing LLMs from hallucinating the Python class name in structured JSON generation.</mandatory_pattern>
    </rule_block>
    <rule_block id="graceful_text_truncation_validator">
        <banned_pattern>Relying solely on `max_length=N` in `Field()` for text generation without providing a truncation mechanism.</banned_pattern>
        <mandatory_pattern>When setting `max_length` on LLM-generated strings, ALWAYS implement a `@field_validator(..., mode="before")` to silently truncate the string. You MUST round down to the nearest sentence (`.`).</mandatory_pattern>
        <catastrophic_reason>Without truncation validators, the system falls into infinite self-correction loops when the LLM generates a string that is 1 character too long.</catastrophic_reason>
    </rule_block>
</architectural_invariants>

<agentic_safety_guardrails>
    <rule_block id="architecture_lock_mandate">
        <banned_pattern>Refactoring, modifying control flow, or changing data traversal logic in code blocks protected by an `ARCHITECTURE LOCK` comment.</banned_pattern>
        <mandatory_pattern>You MUST strictly preserve these blocks as they contain verified logic. You MAY only add or update PEP 257 docstrings.</mandatory_pattern>
        <catastrophic_reason>Treating protected algorithmic blocks as "defensive programming" violations breaks human-verified TDD logic.</catastrophic_reason>
    </rule_block>

    <rule_block id="pydantic_schema_freeze_mandate">
        <banned_pattern>Autonomously tightening structural types, removing `Optional` (`| None`) bounds, or changing field signatures on existing Pydantic models.</banned_pattern>
        <mandatory_pattern>If a schema seems improperly typed, DO NOT fix it; instead log a Warning in the audit matrix. Schema mutability is strictly forbidden without explicit instruction.</mandatory_pattern>
        <catastrophic_reason>Modifying strictness autonomously breaks downstream validation of the SSOT database.</catastrophic_reason>
    </rule_block>

    <rule_block id="pydantic_validation_bypass_ban">
        <banned_pattern>Using `dict(model)`, list comprehensions casting to raw dicts, manually reconstructing an existing model field-by-field (e.g. `Model(field=[dict(x) for x in old.field])`), or mutating objects via full serialization cycles (`type(model)(**model_dump())`) to bypass validation constraints.</banned_pattern>
        <mandatory_pattern>ALWAYS use `model.model_copy(update={...})` or `model.model_copy(deep=True)` for shallow or deep instant updates when altering existing models.</mandatory_pattern>
        <catastrophic_reason>Manual reconstruction is verbose, prone to omissions, and bypassing validation causes runtime AttributeErrors, while full serialization forces recursive O(N) validation cycles.</catastrophic_reason>
    </rule_block>

    <rule_block id="data_and_file_preservation_mandate">
        <banned_pattern>Autonomously refactoring, truncating, or "simplifying" existing file I/O operations, data extraction loops, string concatenations, or dictionary traversals purely for aesthetics.</banned_pattern>
        <mandatory_pattern>Your mandate is strictly architectural (typing, docstrings, modern syntax), NOT algorithmic optimization. You MUST preserve functional I/O and parsing logic entirely.</mandatory_pattern>
        <catastrophic_reason>Deleting or altering working File I/O or parsing loops causes catastrophic Fail-Fast bypasses.</catastrophic_reason>
    </rule_block>

    <rule_block id="backend_quality_gate_delegation">
        <banned_pattern>Running naked `pytest`, `mypy`, or `ruff` commands manually.</banned_pattern>
        <mandatory_pattern>You MUST exclusively trigger the `<universal_quality_gates>` command mapped in `AGENTS.md` (e.g., `uv run python scripts/backend_audit_loop.py <target_path> --test`) to validate Python changes.</mandatory_pattern>
        <catastrophic_reason>Bypassing the unified audit loop allows type regressions and unformatted code to bypass the quality gates.</catastrophic_reason>
    </rule_block>
</agentic_safety_guardrails>