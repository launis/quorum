# Phase 3: Backend Execution Alignment (DEFERRED)

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 3 "Backend Execution Alignment" (L512-L604)
**Status:** PLACEHOLDER — Detailed plan will be generated after Phase 2 is complete.

**Overview:** Align backend services with the new OutputProfile schema. Migrate `AUTHENTICITY_THRESHOLDS` from `authenticity_adapter.py` to `settings.py`, implement `MetadataAdapter` using bilingual `metric_mappings`, create `synthesis_directives.py` SSOT, purge dead-weight fields from `SynthesisConfigDTO`, and type `xai_highlights` from `list[Any]` to `list[XaiHighlightItem]`.

**Target Files:**
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/authenticity_adapter.py]`
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/synthesis_text_adapter.py]`
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/printable_sources_adapter.py]`
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]`
- `[MODIFY]` `@[backend_v2/services/sdui/adapters/executive_summary_adapter.py]`
- `[MODIFY]` `@[backend_v2/models/prompts/__init__.py]`
- `[MODIFY]` `@[backend_v2/models/v2_core.py]` — SynthesisConfigDTO purge, xai_highlights typing
- `[MODIFY]` `@[backend_v2/worker.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/sdui/adapters/test_metadata_adapter.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/sdui/adapters/test_authenticity_adapter.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/sdui/adapters/test_executive_summary_adapter.py]`
- `[NEW]` `@[backend_v2/models/prompts/synthesis_directives.py]`
- `[NEW]` `@[backend_v2/tests/unit/models/prompts/test_synthesis_directives.py]`

**Prerequisites:** Phase 2 (Plan 12) must be complete.

```xml
<execution_protocol>
  <step id="0" name="DEFERRED">
    <action>This plan is a placeholder. Detailed execution steps will be generated after Phase 2 completion.</action>
  </step>

  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\01-python-backend.md]</rule>
  </required_context_rules>

  <anti_targets>
    <file>client_app_v2/ — Do NOT touch Flutter files in this plan</file>
  </anti_targets>

  <dod_checklist>
    <item>DEFERRED — Will be populated during detailed planning.</item>
  </dod_checklist>

  <validation_gate>
    <check>DEFERRED — Will be populated during detailed planning.</check>
  </validation_gate>
</execution_protocol>
```
