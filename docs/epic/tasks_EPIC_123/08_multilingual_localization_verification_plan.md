# Phase 8: Multilingual & Localization (i18n) Verification Plan

**Objective:** Verify strict adherence to SDUI Dumb Painter mandate for multilingual content and confirm localized dynamic enums.

Source: @[c:\src\quorum\docs\epic\EPIC_123_legacy_matrix_synthesis_and_pure_sdui_parity.md#L148-L159] Phase 8: Multilingual & Localization (i18n) Verification

## Target Files (Read-Only Context)
- @[c:\src\quorum\backend_v2\services\blueprint.py#L686-L726]
- @[c:\src\quorum\backend_v2\models\prompts\linguistic_directives.py]
- @[c:\src\quorum\backend_v2\models\prompts\global_mandates.py]

```xml
<execution_protocol level="1_epic_planner">
  <constraint invariant="cross_language_mapping_mandate">The backend MUST ALWAYS provide the fully resolved string — the frontend NEVER performs translation lookups on SDUI block content.</constraint>
  <step id="1" name="Database Source Verification">
    <action>Verify in `@[c:\src\quorum\backend_v2\services\blueprint.py#L686-L726]` that the `I18nText` object from `extension_labels` is resolved using the Execution's `target_language` before injecting it into the SDUI `AlertBlock.text`. Furthermore, you MUST explicitly identify and remove any string manipulation fallback (specifically `ext_key.replace("_", " ").title()`) which violates the `strict_enum_l10n_mapping` rule. If `label_obj` is missing, you MUST raise an explicit `ConfigurationError` and CRASH. Zero Tolerance for silent bypasses.</action>
  </step>
  <step id="2" name="Prompt Directives Verification">
    <action>Verify that `@[c:\src\quorum\backend_v2\models\prompts\linguistic_directives.py]` properly injects `<linguistic_context>` XML pattern without hardcoded natural language instructions. Specifically: Delete the redundant `<critical_warning>` natural language block from `build_linguistic_context()` because it duplicates the `LANGUAGE_MANDATE`. Ensure only the XML tags for languages are present.</action>
  </step>
  <step id="3" name="Dynamic Enums Verification">
    <action>Verify that user roles (specifically "Käyttäjän Rooli") are mapped and retrieved dynamically through Enum definitions and their exact translation property mapping (specifically `@property def l10n_key(self) -> str`), explicitly forbidding hardcoding of localized strings in Python code or Prompt configurations.</action>
  </step>
  <step id="4" name="Extension Anchoring Mandate">
    <action>Verify that `EXTENSION_ANCHORING_MANDATE` in `@[c:\src\quorum\backend_v2\models\prompts\global_mandates.py]` explicitly requires anchoring to the user's raw input or extracted evidence quote without relying on generic theoretical advice.</action>
  </step>
  <step id="5" name="Testing &amp; Quality Gate Plan">
    <action>Write at least two explicit negative test cases verifying that a missing `label_obj` raises `ConfigurationError`. Execute the backend Universal Quality Gate (`uv run python scripts/backend_audit_loop.py backend_v2/ --test`), verifying that test coverage for the verified features has not decreased and all assertions pass correctly.</action>
  </step>
</execution_protocol>
```


