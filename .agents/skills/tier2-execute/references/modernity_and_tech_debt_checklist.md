# Quorum 2026 Modernity Replacements & Scoped Boy Scout Technical Debt Checklist

## 1. Quorum 2026 Modernity Replacement Matrix

Evaluate all proposed and inspected code against these mandatory Quorum 2026 replacements:

| Banned Legacy Anti-Pattern | Mandated Quorum 2026 Replacement |
| :--- | :--- |
| `asyncio.gather(...)` | `async with asyncio.TaskGroup() as tg:` (Python 3.14+ Fail-Fast cancellation) |
| `ConfigDict()` without `strict=True, extra="forbid"` | `ConfigDict(strict=True, extra="forbid", frozen=True)` |
| Raw `dict` state passing (`dict[str, Any]`, `list[dict]`, `TypedDict`, `cast(Any, ...)`, `match/case dict`, `isinstance(..., dict)`) | 100% Strict Pydantic V2 DTOs (`Model.model_validate()`) |
| `# noqa: QGR` inline suppressions | Structural architecture fixes (Zero Suppressions) |
| String concatenation for LLM prompts | `PromptBlock` assembly with Four-Layer Clean Stack isolation |
| Hardcoded model strings (`"gpt-4"`) | `await LLMClient.from_strategy("strategy_name", repo)` |
| Dynamic variables in system prompt prefix | 100% static `_SYSTEM_INSTRUCTION` prefix; dynamic variables isolated at the `user` message tail |
| `try ... except Exception:` catch-all or silent `pass` | Typed `AppException` preceded by structured `logger.error(..., exc_info=True)` (RFC 7807 Dual-Reporting) |
| `Optional[T] = None` or `.get("key", default)` for required config/state | PEP 593 `Annotated[T, Field(...)]` with immediate Fail-Fast crash on missing state |
| Regex or fuzzy matching (`RapidFuzz`, `Levenshtein`) for forensic evidence | Exact normalized `str.find()` lexical anchoring |
| Hardcoded thresholds, timeouts, or magic numbers in business logic | Centralized `settings.py` (`Settings`) SSOT |
| Frontend-side business logic or raw `Map<String, dynamic>` casting | Backend SDUI polymorphic blocks (`SduiBlockDTO`) with `AppErrorBoundary` and ICU `.arb` parity |
| `if/else` routing chains on string literals | Strategy + Registry Pattern or Pydantic V2 Discriminated Unions |
| Terminal commands (`cat`, `tail`, `grep`, `sed`) for reading files/logs | Native IDE tools (`read_file` / `view_file` with `StartLine`/`EndLine` bounds, `grep_search`) |

---

## 2. Scoped Boy Scout Technical Debt Checklist (Target Files & 1-Hop Callers)

Whenever researching, auditing, planning, or modifying codebase targets, run:
```powershell
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets <target_paths> --include-one-hop
```
Inspect the target files and their immediate 1-hop callers across these 3 domains:

1. **Python Backend (`backend_v2/`, `scripts/`):**
   - Eradicate `getattr`/`hasattr`, `.get(`, silent `except Exception:`, unvalidated `model_copy(update=...)`, anonymous 3+ element tuples, and hardcoded magic numbers/timeouts outside `settings.py`.
   - Enforce PEP 593 `Annotated` fields, PEP 695 generics, PEP 257 Google-style docstrings with explicit `Raises:` error codes, and `ConfigDict(strict=True, extra="forbid", frozen=True)`.
2. **Flutter Frontend (`client_app_v2/`):**
   - Eradicate hardcoded UI strings (enforce `.arb` localization), magic hex colors (`Color(0x...)`) and naked `TextStyle(...)` (enforce `Theme.of(context)` and `AppSemanticColors`), manual `substring()` clippings, and legacy `.when()`/`.maybeWhen()` chains (enforce Dart 3 `switch (state)` pattern matching).
   - Enforce `@freezed(equal: false)`, `@JsonSerializable(disallowUnrecognizedKeys: true)`, and `AppErrorBoundary` wrappers.
3. **ISTQB Testing (`backend_v2/tests/`, `client_app_v2/test/`):**
   - For every positive test case, ensure at least 2 negative/boundary test cases exist (missing/invalid required inputs raising `AppException`/`ValidationError`, and ISTQB Boundary Value Analysis `min-1`/`max+1`).
   - Use `polyfactory` (`ModelFactory[T]`) and stateful in-memory fakes (`InMemoryUnitOfWork`); ban manual raw dictionary fixtures and tautological mock-return assertions.

