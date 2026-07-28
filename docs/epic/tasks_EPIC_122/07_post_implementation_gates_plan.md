# Post-Implementation Gates

Source: @[c:\src\quorum\docs\epic\EPIC_122_legacy_parity_output_profile.md#L248-L254]

## Objective
Execute the mandatory Tier 2 Hardening tasks to finalize the Epic, ensure 100% test coverage for newly added logic, and perform a pre-merge audit.

## Target Files
- TARGET (Modify/Test): Codebase-wide

## Execution Protocol

```xml
<execution_protocol level="2_execute">
  <step id="6_1" name="Proxy Sunset &amp; Consumer Migration">
    <action>Ensure all downstream clients or testing suites use the `ReportDataDTO` V2 structure for the `holistic_audit` profile.</action>
    <action>Verify no tests are using the deprecated `matrix_visible_columns` from `ReportDataDTO` or `SynthesisConfigDTO`.</action>
  </step>

  <step id="6_2" name="Tier 2 Hardening &amp; Quality Gates">
    <action>Run `/tier2-hardening-backend` on modified `backend_v2` directories to enforce strict static typing and formatting.</action>
    <action>Run `/tier2-hardening-frontend` on modified `client_app_v2` directories to ensure Dart lints and Freezed generation are optimal.</action>
  </step>

  <step id="6_3" name="Pre-Delete Audit">
    <action>Verify no orphaned dependencies remain for any removed layouts (e.g., the interactive Human Override dialog from the matrix widget).</action>
  </step>

  <step id="6_4" name="Semantic Coverage &amp; Zero-Loss Audit">
    <action>Run the `backend_audit_loop.py` with test coverage explicitly enabled.</action>
    <action>Prove mathematically that line coverage >90% is achieved for the new blueprint logic (Hydrators) and context mappers added in Phase 2.</action>
  </step>
</execution_protocol>
```
