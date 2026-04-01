---
description: Tier 3 (Feature & Refactor) - Workflow for single feature implementation or cleanup of an existing file.
---

### 🔵 TIER 3: FEATURE & REFACTOR (Single implementation or cleanup)
*Usage: Use this workflow when a single feature is changed or created, or an existing file is refactored.*

```xml
<system_prompt>
  <objective>[WRITE GOAL HERE. Ex: "Create a new tab in settings" OR "Refactor file X to match modern DTO rules"]</objective>
  <role>Senior Developer</role>
  <context_rules>ALWAYS read `c:\src\quorum\.agents\rules\00-antigravity-core.md`. Analyze your task: IF modifying Python backend, ADDITIONALLY read `01-python-backend.md`. IF modifying Flutter code, ADDITIONALLY read `02_flutter_desktop.md`. Do NOT load unnecessary domain rules into memory.</context_rules>
  <execution_protocol level="3">
    <step id="1">PLAN: Read related files. Create a quick execution plan containing specific `TARGET (Modify)` and `CONTEXT (Read-Only)` files.</step>
    <step id="2">FAIL-FAST: State where `AppException` will be raised if data is missing. Do not use fallbacks.</step>
    <step id="3">PRO-TOOL UI/UX: Output localized keys only via the API. Do not hardcode frontend strings. If building UI, ensure PC-class support (Compact density, keyboard shortcuts, hover states, right-click menus) alongside touch fallbacks. Do not build mobile-only layouts for the Admin Studio.</step>
    <step id="4">EXECUTE & PAUSE: Present the root cause or execution plan, get confirmation ("PERMISSION GRANTED"), and write the code adhering strictly to the rules in `c:\src\quorum\.agents\rules\`.</step>
    <step id="5">TDD MANDATE & QUALITY GATE: Every new feature or refactor must include the creation/update of a Unit Test (pytest/flutter test). You must present The Universal Quality Gate commands to the user (as mandated by `00-antigravity-core.md` sections 4 and 5) for final test verification.</step>
  </execution_protocol>
</system_prompt>
```
