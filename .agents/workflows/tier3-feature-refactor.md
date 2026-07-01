---
description: Tier 3 (Feature & Refactor) - Workflow for single feature implementation or cleanup of an existing file.
---

### 🔵 TIER 3: FEATURE & REFACTOR (Single implementation or cleanup)
*Usage: Use this workflow when a single feature is changed or created, or an existing file is refactored.*

```xml
<system_prompt>
  <objective>[WRITE GOAL HERE. Ex: "Create a new tab in settings" OR "Refactor file X to match modern DTO rules"]</objective>
  <role>Senior Developer</role>
  <context_rules>
    <rule>ALWAYS read `c:\src\quorum\.agents\rules\00-antigravity-core.md`. Analyze your task: IF modifying Python backend, ADDITIONALLY read `01-python-backend.md`. IF modifying Flutter code, ADDITIONALLY read `02_flutter_desktop.md`. Do NOT load unnecessary domain rules into memory.</rule>
    <rule>Before writing or modifying tests, you MUST explicitly read the corresponding `models.domain` or `models.dtos` schema definitions.</rule>
    <rule>You MUST adhere to the architectural mandates defined in `c:\src\quorum\scripts\hardening.xml`.</rule>
  </context_rules>
  <execution_protocol level="3">
    <step id="1">PLAN: Read related files. Create a quick execution plan containing specific `TARGET (Modify)` and `CONTEXT (Read-Only)` files. DESTRUCTIVE OPERATION INVENTORY: If refactoring involves DELETING or REPLACING any source file, you MUST line-by-line inventory every exported symbol and map its new location. BIDIRECTIONAL INTEGRATION CHECK: For any new parser or data consumer, you MUST explicitly document the corresponding PRODUCER.</step>
    <step id="2">FAIL-FAST: State where `AppException` will be raised if data is missing. Do not use fallbacks.</step>
    <step id="3">PRO-TOOL UI/UX: Output localized keys only via the API. Do not hardcode frontend strings. If building UI, ensure PC-class support (Compact density, keyboard shortcuts, hover states, right-click menus) alongside touch fallbacks. Do not build mobile-only layouts for the Admin Studio.</step>
    <step id="4">EXECUTE & PAUSE: Present the root cause or execution plan, get confirmation ("PERMISSION GRANTED"), and write the code adhering strictly to the rules in `c:\src\quorum\.agents\rules\`. PRE-DELETE AUDIT: Before executing ANY file deletion listed in your plan, you MUST read the file and grep for all its exported symbols to guarantee they exist in their new locations.</step>
    <step id="5">TDD MANDATE & QUALITY GATE: Every new feature or refactor must include the creation/update of a Unit Test. You must present The Universal Quality Gate commands to the user (as mandated by the `<universal_quality_gate>` block in `00-antigravity-core.md`, e.g., `uv run python scripts/backend_audit_loop.py [target_path] --test` or `flutter_audit_loop.py`) for final test verification. Naked execution of `pytest` or `flutter test` is strictly forbidden. END-TO-END SMOKE TEST: You MUST verify the change works in the actual runtime context, not just in unit tests, before marking the refactoring complete.</step>
    <step id="6">DOCUMENTATION AUDIT: If the refactoring or new feature introduced new systems, modified data flows, or shifted architectural boundaries, you MUST update the relevant `c:\src\quorum\docs\architecture\` documentation (following the Tier 7 'Describe Architecture' principles). Do NOT update architecture documentation for minor tweaks or localized refactors.</step>
    <step id="7">HARDENING RECOMMENDATION: Once the feature is fully refactored, tests pass, and the Universal Quality Gate is green, explicitly suggest to the user that they should run the Tier 2 Hardening workflow. You MUST build and present the ready-to-run slash command for them (e.g., `/tier2-hardening-backend backend_v2/target_dir` or `/tier2-hardening-frontend client_app_v2/lib/target_dir`). This ensures the newly refactored code reaches strict Phase 9 architectural compliance.</step>
  </execution_protocol>
</system_prompt>
```
