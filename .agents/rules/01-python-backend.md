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
    <rule_block id="strict_pydantic_v2_rust">
        <banned_pattern>Using legacy V1 instantiation (`MyModel(**data)`), Python standard JSON parsing (`json.loads()`), or legacy V1 methods (`.dict()`, `@validator`).</banned_pattern>
        <mandatory_pattern>Force the Fail-Fast pipeline by using `.model_validate()`, Rust-based `.model_validate_json()`, `.model_dump()`, and `@field_validator`. Use `model_config = ConfigDict(extra='forbid', strict=True)` to reject unstructured AI outputs.</mandatory_pattern>
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
        <banned_pattern>Returning raw DB models natively out of FastAPI endpoints, bypassing Pydantic filtering.</banned_pattern>
        <mandatory_pattern>Every single FastAPI router MUST explicitly define `response_model=UserDTO` to strip hidden database variables out of the HTTP response string, effectively preventing Cross-Tenant Trace Leaks.</mandatory_pattern>
    </rule_block>

    <rule_block id="llm_structured_execution_mandate">
        <banned_pattern>Directly calling OpenAI/VertexSDKs, relying on raw text outputs, or parsing responses with Regex.</banned_pattern>
        <mandatory_pattern>You MUST initialize the execution via `LLMClient.from_strategy("strategy_name", repo)`. For data retrieval, rely ONLY on the `run_structured_task()` methodology to force Socratic Self-Healing JSON parsing through a dedicated Pydantic model. If doing open-text generation, use `run_chat()`.</mandatory_pattern>
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