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
- NO `try-except pass`. 
- NO raw `dict` returns from Agents (Strict Pydantic V2 only). 
- NO legacy `Depends` (Use `Annotated`). 
- NO business logic in Routers. 
- NO `HTTPException` (Use `AppException` & RFC 7807). 
- No default values in domain models unless logically strictly necessary.
- NO duplicate Pydantic classes (The SSOT Mandate). FastAPI schemas must be centralized in `models/` and NEVER defined inline in `routers/` to prevent OpenAPI namespace collisions causing git diff 'Ping-Pong' loops.

### 1.3 Background Workers (Arq 2026 Mandate)
Long-running AI generation or heavy DAG execution tasks MUST NEVER block the FastAPI HTTP request cycle. They MUST be offloaded to an asynchronous worker queue (Arq / Redis). The API router must return a 202 Accepted status with a TaskID immediately.

### 1.4 The Three Pydantic Boundaries (API, Service, Middleware)
1. **API Ingestion (Generic IN -> Strict OUT):** The API Routers (`backend_v2/api/`) MUST take raw JSON/Dict from the web and immediately force it into a strict Pydantic DTO.
2. **Service Layer (Strict IN -> Strict OUT):** The business logic (`backend_v2/services/`) ONLY accepts Pydantic models from the routers and instantly hydrates DB data into Pydantic models before logic. 
3. **DAG/Middleware (V3 EVENT SOURCING ACTIVE):** Logic Nodes (Reducers) are pure functions emitting new `TraceEvent` objects. They DO NOT mutate old dictionaries and DO NOT perform batch database I/O.

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
- **Service Boundary Fail-Fast:** If data is invalid or missing, crash immediately at the Service boundary. Do not return `None`, `{}`, or `[]` to silently bypass errors. Fix the root cause.
- **Dual-Reporting Python:** Always log errors structurally (`logger.error`) BEFORE raising `AppException`.

### 2.3 Strictness & Hardcoding
- **DTO Parity Flexibility:** Backend Enums parsing from TinyDB are allowed practical `strict=False` flexibility.
- **NO HARDCODING:** NEVER hardcode dictionary keys, temporary IDs, or domain logic.

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