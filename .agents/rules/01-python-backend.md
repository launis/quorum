---
trigger: always_on
description: Strict Pydantic V2 and FastAPI Rules
globs: backend_v2/**/*.py
---

# BACKEND ARCHITECTURE CONSTRAINTS

*** UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS FOR PYTHON ***

## 1. ARCHITECTURAL BANS & MANDATORY VERIFICATION

### 1.1 AI Verification Mandate
You (the AI assistant) MUST actively verify your compliance with the V2 Architecture on EVERY task. Before writing any code, you MUST explicitly state that the V2 Architecture has been taken into account.

### 1.2 Backend Bans (Non-Negotiable)
<architecture_bans>
  <rule>NO `try-except pass`.</rule>
  <rule>NO raw `dict` returns from Agents (Strict Pydantic V2 only).</rule>
  <rule>NO legacy `Depends` (Use `Annotated`).</rule>
  <rule>NO business logic in Routers.</rule>
  <rule>NO `HTTPException` (Use `AppException` & RFC 7807).</rule>
  <rule>No default values in domain models unless logically strictly necessary.</rule>
  <rule>NO duplicate Pydantic classes (The SSOT Mandate). FastAPI schemas must be centralized in `models/` and NEVER defined inline in `routers/` to prevent OpenAPI namespace collisions. If you modify ANY Pydantic model, you MUST instruct the user to run `uv run python backend_v2/scripts/generate_openapi.py` locally and commit the `docs/swagger/openapi.json` file to prevent CI/CD git diff crashes.</rule>
  <rule>Silent failures are BANNED. Exceptions must NEVER be swallowed silently.</rule>
</architecture_bans>

### 1.3 Background Workers (Arq 2026 Mandate)
Long-running AI generation or heavy DAG execution tasks MUST NEVER block the FastAPI HTTP request cycle. They MUST be offloaded to an asynchronous worker queue (Arq / Redis). The API router must return a 202 Accepted status with a TaskID immediately.

### 1.4 The Three Pydantic Boundaries & Single Responsibility Principle (SRP)
The system strictly enforces the Single Responsibility Principle across the "Three Pydantic Boundaries". Monolithic "God Functions" are strictly banned.
1. **API Routers (HTTP & Routing ONLY):** The API Routers (`backend_v2/api/`) are entirely *anemic*. They MUST ONLY handle HTTP parsing, assign an explicit `response_model`, and delegate to the Service layer. They MUST NOT contain database CRUD, RBAC checks, or complex business logic.
2. **Service Layer (Business Logic & Tenant Isolation):** The business logic (`backend_v2/services/`) ONLY accepts Pydantic models from the routers. It is exclusively responsible for RBAC, Tenant Isolation (vuokralaiseristys), and hydrating DB data into Pydantic models before logic. 
3. **Repository/Middleware (DB I/O & Event Sourcing ONLY):** Logic Nodes (Reducers) and Repositories are pure data handlers. They DO NOT mutate old dictionaries and DO NOT handle HTTP context or raw User access logic.

## 2. THE ZERO-COMPROMISE PLEDGE (Absolute Fail-Fast)

### 2.1 Strict Pydantic 2026 Mandate (Rust-Core & Anti-Hallucination)
1. **Instantiation:** NEVER use dictionary unpacking (`MyModel(**data)`). ALWAYS use `MyModel.model_validate(data)` to force the Fail-Fast validation pipeline.
2. **Rust-Speed JSON Parsing:** When parsing raw JSON strings (e.g., from Arq/Redis or LLM output), NEVER use Python's `json.loads()`. You MUST use `MyModel.model_validate_json(json_str)` to bypass Python and parse directly in Rust.
3. **Serialization Ban:** Legacy V1 methods `.dict()`, `.json()`, and `parse_obj()` are BANNED. Use `.model_dump()` and `.model_dump_json()`. Nested `class Config:` is banned; use `model_config = ConfigDict(...)`.
4. **V1 Validator Ban:** Legacy `@validator` and `@root_validator` are BANNED. Use V2 `@field_validator` and `@model_validator(mode='after')`.
5. **Anti-Hallucination:** All models parsing external or LLM payloads MUST use `model_config = ConfigDict(extra='forbid', strict=True)`. If an LLM hallucinates undocumented keys, the model MUST crash immediately (Fail-Fast). Silently dropping extra data is banned.
6. **Immutability (Frozen State):** All Event Sourcing models (`TraceEvent`), DTOs, and DAG nodes MUST be immutable using `model_config = ConfigDict(frozen=True)`. In-place mutation (`event.status = 'done'`) is BANNED. Spawn new states using `event.model_copy(update={'status': 'done'})`.
7. **Polymorphism (O(1) Routing):** When defining complex DAG nodes or TraceEvents, implicit Unions are BANNED. You MUST use Discriminated Unions (`Field(discriminator='type')`) to ensure O(1) parsing speed and prevent unsafe duck-typing.
8. **Annotated Validators (PEP 593):** NEVER mix validation with default values (e.g., `age: int = Field(gt=0)`). ALWAYS use `Annotated` to keep type hints pure for `mypy` (e.g., `age: Annotated[int, Field(gt=0)]`).

### 2.2 Execution & Silence Bans
- **FastAPI Async/Sync Rule:** If a router only reads from TinyDB (which is blocking), the route MUST be a synchronous `def`. If the route calls LLMs, Firebase, or Arq, it MUST be `async def`.
- **Silent Failures are BANNED:** NEVER use `try: ... except Exception: pass` in Python. Exceptions must NEVER be swallowed silently. They must be logged, properly handled, or re-thrown.
- **Service Boundary Fail-Fast (Fallback Ban):** If data is invalid or missing, crash immediately at the Service boundary. You are STRICTLY BANNED from returning default values, `None`, `{}`, or `[]` to silently bypass errors. Pydantic models must CRASH (Fail-Fast) if data does not match the strictest form. Fix the root cause.
- **Dual-Reporting Python:** Always log errors structurally (`logger.error`) BEFORE raising `AppException`.

### 2.3 Strictness & Hardcoding
- **DTO Parity Flexibility:** Backend Enums parsing from TinyDB are allowed practical `strict=False` flexibility.
- **NO HARDCODING:** NEVER hardcode dictionary keys, temporary IDs, or domain logic.

### 2.4 Data Leak Prevention (Zero Leaks Mandate)
- **Absolute Response Model Mandate:** EVERY FastAPI router MUST have an explicit `response_model` definition (e.g. `@router.get("/", response_model=UserDTO)`). 
- **No Raw Database Model Leaks:** You MUST NEVER leak internal database models directly to the UI. All returned models must be stripped down to safe Data Transfer Objects (DTOs) via Pydantic to prevent exposing password hashes, internal system parameters, or cross-tenant traces.

### 2.5 The 2026 Modern Python 3.14 Syntax Mandate
You MUST utilize the most advanced native syntax features of Python 3.14 and Pydantic V2. Legacy patterns are strictly BANNED:
1. **PEP 695 Generics:** Legacy `TypeVar` and `Generic[T]` usage is BANNED. Use native generic syntax: `def process[T](data: T) -> T:` and `class Repo[T]:`.
2. **PEP 698 Overrides:** When implementing abstract methods or subclassing Service interfaces, you MUST use the `@override` decorator to enforce compile-time certainty (`from typing import override`).
3. **Concurrency (TaskGroups):** `asyncio.gather()` is deprecated overhead. All parallel asynchronous execution MUST use `async with asyncio.TaskGroup() as tg:` to ensure deterministic cancellation (Fail-Fast behavior).
4. **Union & Optional:** Legacy `Optional[X]` and `Union[X, Y]` type hints are BANNED. You MUST use the native bitwise operator: `X | None` or `X | Y`.
5. **Structural Pattern Matching:** When consuming Polymorphic objects (Discriminated Unions from Pydantic models), `if-elif isinstance()` chains are BANNED. You MUST use native structural matching (O(1) routing): `match event: case EventA(): ... case EventB(): ...`.

## 3. DATA PARITY, DATABASE & CQRS

### 3.1 Firebase CQRS
ALL mutations MUST be sent to the Python FastAPI backend, which validates the payload via Pydantic and updates Firestore securely via the Admin SDK.

### 3.2 Backend Repo
Any database repository change MUST be implemented centrally in `UnifiedWorkflowRepository`.

### 3.3 Seed Data Protocol
Database modifications MUST NOT be done manually. Always follow the `03_seed_vault.md` rules.

## 4. L10N (No-String Policy)

### 4.1 Backend Resolution
Backend MUST return Enum Keys (e.g., `AUTH_ORGANIC`). Raw UI strings are BANNED in Python APIs. Backend resolves dynamic translations late in the pipeline via `BlueprintTransformer`.

## 5. QUALITY LOOP & TOOL USAGE

### 5.1 Python Linter & Typing
Commands MUST ALWAYS be given in this explicit format, listing the exact files (no wildcards) with `backend_v2/` path prefix from the project root, and using `;` instead of `&&`:
`uv run ruff check backend_v2/[TARGET_FILES] --fix ; uv run mypy backend_v2/[TARGET_FILES] --strict`

### 5.2 Zero-Deprecation Mandate
You MUST resolve ALL syntax errors, typing errors, AND deprecation warnings before declaring the step complete. Code with deprecated APIs is considered broken. Proactively replace deprecated members with their modern equivalents.

### 5.3 Testing Mandate
Whenever code is changed, refactored, or new features are added, you MUST ALWAYS write new automated tests OR fix existing old tests for the Python side. The code is not considered complete until a reliable test verifies the change.

## 6. OUTPUT FORMAT & DOCUMENTATION

### 6.1 Language Strategy
Prompts / Code Blocks MUST be in English. Explanations/Context MUST be in Finnish.

### 6.2 Google Docstrings
All Python functions, classes, and modules MUST use the standard Google Docstring format. Use the Imperative Mood for the short summary (e.g. "Calculate the...").

### 6.3 Internal Comments (The "Why" Mandate)
Only comment WHY business logic exists. Never explain WHAT the code mechanically does.

## 7. IDE FILE SCOPING & EDITING PROTOCOL

### 7.1 Read-Before-Write
NEVER guess the contents of a file. Use your tools to read the current context before proposing modifications.

### 7.2 Explicit Scope
Only modify `TARGET` files. Treat `CONTEXT` files as Read-Only.

### 7.3 Editing Safety (Anti-Duplication Protocol)
When modifying a file, explicitly DELETE or OVERWRITE the old version. NEVER append the new version to the end of the file while leaving the old one intact.