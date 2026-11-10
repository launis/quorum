# Quorum 2026 Modernity Replacements & Scoped Boy Scout Technical Debt Checklist

## 1. Quorum 2026 Modernity Replacement Matrix

Evaluate all proposed and inspected code against these mandatory Quorum 2026 replacements:

| Banned Legacy Anti-Pattern | Mandated Quorum 2026 Replacement |
| :--- | :--- |
| `asyncio.gather(...)` or `await asyncio.wait_for(coro, timeout)` | `async with asyncio.TaskGroup() as tg:` and `async with asyncio.timeout(delay):` (Python 3.14+ Fail-Fast cancellation) |
| `from typing import Sequence, Mapping, Callable, Iterable, AsyncIterator, Awaitable` or `timezone.utc` | `from collections.abc import ...` (PEP 585 / `UP035`) and `from datetime import UTC` (`UP017`) |
| `json.dumps(model.model_dump(...))` | Direct Pydantic V2 Rust `.model_dump_json()` or `TypeAdapter(...).dump_json()` |
| SQL `DEFAULT gen_random_uuid()`, physical `created_at DEFAULT NOW()`, or N+1 `for x in items: await conn.execute(...)` | PostgreSQL 19 `DEFAULT uuidv7()`, `GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL`, and bulk `executemany` / `UNNEST` |
| `ConfigDict()` without `strict=True, extra="forbid"` | `ConfigDict(strict=True, extra="forbid", frozen=True)` |
| Raw `dict` state passing (`dict[str, Any]`, `list[dict]`, `TypedDict`, `cast(Any, ...)`, `match/case dict`, `isinstance(..., dict)`) | 100% Strict Pydantic V2 DTOs (`Model.model_validate()`) |
| `# noqa: QGR` inline suppressions | Structural architecture fixes (Zero Suppressions) |
| String concatenation for LLM prompts | `PromptBlock` assembly with Four-Layer Clean Stack isolation |
| Hardcoded model strings (`"gpt-4"`) or raw tier strings (`LLMClient.from_strategy("fast", repo)`) | `await LLMClient.from_tier(CognitiveTier.<TIER>, repository=repo)` (`CognitiveTier.FAST`, `BALANCED`, `DEEP`, `REASONING`) |
| Dynamic variables in system prompt prefix | 100% static `_SYSTEM_INSTRUCTION` prefix; dynamic variables isolated at the `user` message tail |
| `try ... except Exception:` catch-all or silent `pass` | Typed `AppException` preceded by structured `logger.error(..., exc_info=True)` (RFC 7807 Dual-Reporting) |
| `Optional[T] = None` or `.get("key", default)` for required config/state | PEP 593 `Annotated[T, Field(...)]` with immediate Fail-Fast crash on missing state |
| Regex or fuzzy matching (`RapidFuzz`, `Levenshtein`) for forensic evidence | Exact normalized `str.find()` lexical anchoring |
| Hardcoded thresholds, timeouts, or magic numbers in business logic | Centralized `settings.py` (`Settings`) SSOT |
| Frontend-side business logic or raw `Map<String, dynamic>` casting | Backend SDUI polymorphic blocks (`SduiBlockDTO`) with `AppErrorBoundary` and ICU `.arb` parity |
| Freezed 2 bare `class Foo with _$Foo`, Riverpod 2 `*Ref` types, `Color.withOpacity(...)`, `MediaQuery.of(context).size`, or `colorScheme.surfaceVariant`/`background` | Freezed 3.2 `abstract class` / `sealed class`, Riverpod 3.0 unified `Ref ref`, `.withValues(alpha: ...)`, `MediaQuery.sizeOf(context)`, and Material 3 `surfaceContainerHighest`/`surface` |
| `if/else` routing chains on string literals | Strategy + Registry Pattern or Pydantic V2 Discriminated Unions |
| Terminal commands (`cat`, `tail`, `grep`, `sed`) for reading files/logs | Native IDE tools (`read_file` / `view_file` with `StartLine`/`EndLine` bounds, `grep_search`) |
| `uuid.uuid4()`, `Uuid().v4()`, or 8/16-hex ID truncations (`.hex[:8]`, `.hex[:16]`, `.substring(0, 16)`, `.take(16)`) | 32-hex RFC 9562 UUIDv7 via `generate_opaque_id(EntityPrefix.<TYPE>)`, `generate_uuid7()`, and `generateOpaqueUuid7(prefix)` (`QGR030`, `DGR008`) |
| Direct `DomainModel(...)` or `DTO(...)` constructor calls in unit tests | `ModelFactory.build(...)` from `@[backend_v2/tests/factories/model_factories.py]` or `.model_validate()` boundary hydration (`schema_blast_radius_and_factory_mandate`) |
| Synchronous CPU/disk blocking (`pd.ExcelWriter`, `.to_excel()`, `openpyxl`, `fitz.open`, `PdfReader`, `zipfile.ZipFile`) inside `async def` or unbounded `.get_all_*()` on hot execution/export paths | `await asyncio.to_thread(...)` offload and targeted $O(1)$ ID / scoped batch lookups (`TD_ASYNC_EVENT_LOOP_BLOCKING`, `TD_UNBOUNDED_HOT_PATH_QUERY`) |
| Unchecked entity ID access, split multi-step writes outside a single `async with uow:`, or unversioned lifecycle state overwrites | Strict tenant/RBAC verification (`initiator.organization_id` / `is_resource_accessible`), atomic `async with uow:` transactions, and `expected_state_version` optimistic concurrency (`CONFLICT`) |

---

## 2. Scoped Boy Scout Technical Debt Checklist (Target Files & 1-Hop Callers)

Whenever researching, auditing, planning, or modifying codebase targets, run:
```powershell
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets <target_paths> --include-one-hop
```
Inspect the target files and their immediate 1-hop callers across these 3 domains:

1. **Python Backend (`backend_v2/`, `scripts/`):**
   - Eradicate `getattr`/`hasattr`, `.get(`, silent `except Exception:`, unvalidated `model_copy(update=...)`, anonymous 3+ element tuples, legacy `uuid.uuid4()` / 8-16 hex ID truncations (enforce `generate_opaque_id` / `generate_uuid7`), and hardcoded magic numbers/timeouts outside `settings.py`.
   - Enforce Multi-Tenant & RBAC ownership (`initiator.organization_id` / `is_resource_accessible`) on all ID-based service reads/mutations, atomic `async with uow:` transactions for coupled multi-step writes, `expected_state_version` optimistic concurrency on lifecycle transitions, `await asyncio.to_thread(...)` for synchronous CPU/disk work inside `async def`, zero `.get_all_*()` scans on hot execution/export paths, and 1-hop caller-callee `AppException`/return contract parity.
   - Enforce PEP 593 `Annotated` fields, PEP 695 generics, PEP 257 Google-style docstrings with explicit `Raises:` error codes, and `ConfigDict(strict=True, extra="forbid", frozen=True)`.
   - Whenever adding or modifying any `<rule_block>` or static AST guardrail (`QGR*`, `DGR*`, `ZORM*`, `SKL*`, `TD_*`, `DictEradicationVisitor`), run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` to verify pairwise rule-vs-rule and static-checker orthogonality (`pairwise_rule_and_guardrail_orthogonality_mandate`).
2. **Flutter Frontend (`client_app_v2/`):**
   - Eradicate hardcoded UI strings (enforce `.arb` localization), magic hex colors (`Color(0x...)`) and naked `TextStyle(...)` (enforce `Theme.of(context)` and `AppSemanticColors`), manual `substring()` clippings, legacy `Uuid().v4()` / `.take(16)` ID truncations (enforce `generateOpaqueUuid7(prefix)`), and legacy `.when()`/`.maybeWhen()` chains (enforce Dart 3 `switch (state)` pattern matching).
   - Enforce `@freezed(equal: false)`, `@JsonSerializable(disallowUnrecognizedKeys: true)`, and `AppErrorBoundary` wrappers.
3. **ISTQB Testing (`backend_v2/tests/`, `client_app_v2/test/`):**
   - For every positive test case, ensure at least 2 negative/boundary test cases exist (missing/invalid required inputs raising `AppException`/`ValidationError`, and ISTQB Boundary Value Analysis `min-1`/`max+1`).
   - Use `polyfactory` (`ModelFactory.build(...)` from `@[backend_v2/tests/factories/model_factories.py]`) and stateful in-memory fakes (`InMemoryUnitOfWork`, `@[backend_v2/tests/fakes/in_memory_repositories.py]`); ban direct `DomainModel(...)` / `DTO(...)` constructors in unit tests, manual raw dictionary fixtures, and tautological mock-return assertions, and pass modified test/fake file paths explicitly to `scripts/backend_audit_loop.py` (`schema_blast_radius_and_factory_mandate`).

