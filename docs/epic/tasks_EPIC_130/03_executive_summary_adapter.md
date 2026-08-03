# Phase 4: Extract Executive Summary Adapter

**Overview:** Extract the inline executive summary role-mapping logic from `blueprint.py`'s `build_report_dto` into a self-contained `ExecutiveSummaryAdapter`. Replace the bare `except Exception:` catch-all and `.get()` fallback with strict typing.

**Target Files:**
- @[c:\src\quorum\backend_v2\services\sdui\adapters\executive_summary_adapter.py] [NEW]
- @[c:\src\quorum\backend_v2\services\blueprint.py] [MODIFY]
- @[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_executive_summary_adapter.py] [NEW]
- @[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py] [MODIFY]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by the previous phase. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <dod_checklist>
    <item>blueprint.py contains ZERO direct ParagraphBlock instantiation for the executive summary prefix.</item>
    <item>executive_summary_adapter.py is self-contained: it has its own module-level rules dictionary and strictly uses explicit Key-Access (`RULES[key]`) rather than `.get()`.</item>
    <item>Atomic Test Migration: Any tests previously asserting on private methods are updated in the exact same phase. No test suite breakage between phases.</item>
    <item>MyPy strict passes with zero new `# type: ignore` annotations.</item>
    <item>Zero bare `except Exception:` catch-alls in any adapter file. All exception handlers MUST use typed exceptions and explicitly state them in the `Raises:` section of the Google-style docstring.</item>
    <item>The word "Epic" (or "EPIC") does NOT appear in any added code, docstrings, or comments.</item>
    <item>Zero inline imports in any adapter file. All imports MUST be at the top of the file.</item>
  </dod_checklist>

  <anti_targets>
    <target>backend_v2/models/view/sdui.py</target>
    <target>backend_v2/models/v2_core.py</target>
    <target>synthesis_md resolution, content_blocks aggregation, and section_syntheses mapping in blueprint.py (these remain in blueprint.py's orchestration flow at #L1060-L1077).</target>
  </anti_targets>

  <step id="1" name="CREATE EXECUTIVE SUMMARY ADAPTER">
    <constraint invariant="knowledge_item_preflight">You MUST read KI `sdui_adapter_decomposition` (specifically `ki_sdui_adapter_pattern.md`) BEFORE creating the adapter file. The file MUST be structurally identical to the canonical reference template (use an empty RULES dictionary for Section 1 if no hardcoded aesthetics exist).</constraint>
    <action>Create `@[c:\src\quorum\backend_v2\services\sdui\adapters\executive_summary_adapter.py]` [NEW].</action>
    <action>Define class `ExecutiveSummaryAdapter` with `@staticmethod build(context: AdapterContext) -> list[AnySduiBlock]`.</action>
    <action>Implement strict role validation: Enforce `RoleClassification(context.profile_cache.user_role)`. Catch `ValueError` and raise `AppException` (ErrorCodes.VALIDATION_FAILED). Do NOT use `except Exception:`.</action>
    <action>Implement Fail-Fast L10N Prefix: Enforce `context.profile.user_role_label.resolve(context.locale)`. If `user_role_label` is missing (None), raise a Fail-Fast `AppException` (ErrorCodes.VALIDATION_FAILED) rather than hardcoding English "User Role".</action>
    <action>Implement strict mapping lookup: Use `context.profile.user_role_mappings[context.profile_cache.user_role]` instead of `.get()`. Catch `KeyError` and raise `AppException` (ErrorCodes.VALIDATION_FAILED).</action>
    <action>If `context.profile_cache.user_role` is None or empty, return an empty list `[]`.</action>
    <action>Return `[ParagraphBlock(text=f"**{prefix}:** {role_val}", exact_quotes=[], citations=[])]` on success.</action>
  </step>

  <step id="2" name="MODIFY BLUEPRINT.PY">
    <action>Open `@[c:\src\quorum\backend_v2\services\blueprint.py]`.</action>
    <action>Import `ExecutiveSummaryAdapter` at the module level (top of file).</action>
    <action>In `__init__`, add `ExecutiveSummaryAdapter` to `_target_block_hydrators` dispatch table, wrapped in a lambda: `lambda ctx: ExecutiveSummaryAdapter.build(ctx)`.</action>
    <demolish>
      REMOVE: inline executive summary role-mapping logic inside `build_report_dto` at @[c:\src\quorum\backend_v2\services\blueprint.py] lines 1051-1063 (the `if profile_cache.user_role:` block containing `try...except Exception`, `.get()`, and `content_blocks.append(ParagraphBlock(...))`).
      REPLACE WITH: Nothing inline. The logic is now handled by the adapter through the dispatch loop. `synthesis_md` resolution remains untouched.
    </demolish>
  </step>

  <step id="3" name="TESTING & QUALITY GATE">
    <action>Create `@[c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_executive_summary_adapter.py]` [NEW].</action>
    <action>Move any existing executive summary tests from `test_blueprint.py` (if any exist) to the new test file.</action>
    <action>Implement the test contracts specified below.</action>
    
    <test_contracts>
      <test name="test_build_valid_role_returns_paragraph_block" category="positive">
        <input>AdapterContext with profile_cache.user_role="valid_role", valid profile.user_role_mappings, valid profile.user_role_label</input>
        <expected>returns list containing one ParagraphBlock with formatted text</expected>
      </test>
      <test name="test_build_missing_user_role_returns_empty_list" category="boundary">
        <input>AdapterContext with profile_cache.user_role=None</input>
        <expected>returns []</expected>
      </test>
      <test name="test_build_invalid_role_classification_raises_app_exception" category="negative">
        <input>AdapterContext with profile_cache.user_role="invalid_role" that fails RoleClassification enum parsing</input>
        <expected>raises AppException with ErrorCodes.VALIDATION_FAILED</expected>
      </test>
      <test name="test_build_missing_user_role_label_raises_app_exception" category="negative">
        <input>AdapterContext with profile.user_role_label=None</input>
        <expected>raises AppException with ErrorCodes.VALIDATION_FAILED</expected>
      </test>
      <test name="test_build_missing_role_mapping_raises_app_exception" category="error_path">
        <input>AdapterContext with valid user_role but missing key in profile.user_role_mappings</input>
        <expected>raises AppException with ErrorCodes.VALIDATION_FAILED</expected>
      </test>
    </test_contracts>
  </step>

  <validation_gate>
    <command>uv run python scripts/backend_audit_loop.py backend_v2 --test</command>
  </validation_gate>
</execution_protocol>
```
