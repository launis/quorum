# Phase 4: Extract Executive Summary Adapter

## Root Cause & Justification
**Root Cause:** The `blueprint.py` service violates the Single Responsibility Principle by manually constructing SDUI `ParagraphBlock` objects for the executive summary inline (lines 1072-1095). Additionally, the inline logic contains severe violations of Quorum's architectural invariants:
1. **The Duct-Tape Ban & Fail-Fast Violation:** It uses a blind `try...except Exception:` block to swallow `RoleClassification` validation failures and silently falls back to unvalidated strings.
2. **String L10N Ban Violation:** It hardcodes the English string `"User Role"` as a lazy fallback when `profile.user_role_label` is missing, which breaks the Finnish SDUI translation boundary.

**Justification:** Extracting this logic into a dedicated `ExecutiveSummaryAdapter` enforces the `Tripartite Rendering Boundary` and allows for rigorous, isolated unit testing. By replacing duct-tape fallbacks with strict `AppException` boundaries, we enforce the Fail-Fast architecture. 

## 1. Create ExecutiveSummaryAdapter
**Target File:** `@[c:\src\quorum\backend_v2\services\sdui\adapters\executive_summary_adapter.py]`

Create `ExecutiveSummaryAdapter` with a strictly typed static method:
```python
class ExecutiveSummaryAdapter:
    @staticmethod
    def hydrate(
        *,
        profile_cache: RenderedSynthesisCache,
        profile: OutputProfile,
        locale: str
    ) -> list[AnySduiBlock]:
```
- **Strict Role Validation:** Use `RoleClassification(profile_cache.user_role)`. If this throws a `ValueError`, you MUST catch it, log an error (`ErrorCodes.VALIDATION_FAILED`), and raise a strict `AppException`. NO `except Exception:` catch-alls.
- **Fail-Fast L10N Prefix:** When extracting the role prefix, use `profile.user_role_label.resolve(locale)`. If `profile.user_role_label` is missing, you MUST raise a Fail-Fast `AppException` rather than hardcoding `"User Role"`. The Database SSOT must explicitly provide the localized label.
- **Return Type:** Return a strictly typed `list[AnySduiBlock]` containing `ParagraphBlock` instances for the executive summary, user role, and user role justification.

## 2. Refactor Blueprint Transformer
**Target File:** `@[c:\src\quorum\backend_v2\services\blueprint.py#L1072-L1095]`
- Import `ExecutiveSummaryAdapter`.
- Delete the inline logic block that appends to `content_blocks` (lines 1072-1095).
- Replace it with a single, clean delegation call:
```python
summary_blocks = ExecutiveSummaryAdapter.hydrate(
    profile_cache=profile_cache, 
    profile=profile, 
    locale=locale
)
content_blocks.extend(summary_blocks)
```

## 3. Test Coverage & Migration
**Target Files:** 
- `@[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_executive_summary_adapter.py]`
- `@[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py]`

- **Mandatory Negative Test 1 (Role Coercion):** Write a strict negative test in `test_executive_summary_adapter.py` asserting that passing an invalid `user_role` string triggers an `AppException`.
- **Mandatory Negative Test 2 (Missing Label):** Write a strict negative test asserting that a missing `user_role_label` in the `OutputProfile` triggers an `AppException` instead of falling back to a hardcoded string.
- **Positive Test:** Verify that the three `ParagraphBlock` components are returned correctly when valid inputs are provided.
- Update `test_blueprint.py` to adapt to the new extraction strategy.
