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
    <rule_block id="core_rules_routing">
      <mandatory_pattern>Your VERY FIRST tool call in a new task MUST be `view_file` to load the appropriate rule file. You MUST NOT output any `<thinking_process>` or generate code until you have physically read the rules. ALWAYS read `.agents\rules\00-antigravity-core.md`. Analyze your task dynamically: IF modifying the Python backend, ADDITIONALLY read `01-python-backend.md`. IF modifying Flutter code, ADDITIONALLY read `02_flutter_desktop.md`. NEVER load legacy `hardening.xml`. You MUST synchronize your understanding with the system's Knowledge Item (KI) guidelines to prevent architectural regressions.</mandatory_pattern>
      <catastrophic_reason>Loading deprecated XML rules or ignoring KI guidelines causes the agent to re-introduce V1 legacy patterns, destroying the Phase 9 architecture.</catastrophic_reason>
    </rule_block>
    <rule_block id="schema_first_mandate">
      <mandatory_pattern>Before writing or modifying tests, you MUST explicitly read the corresponding `models.domain` or `models.dtos` schema definitions.</mandatory_pattern>
      <catastrophic_reason>Guessing the schema shapes causes strict Pydantic V2 validations to fail instantly.</catastrophic_reason>
    </rule_block>
  </context_rules>
  <execution_protocol level="3">
    <step id="1">DYNAMIC CONTEXT ACQUISITION &amp; EXHAUSTIVE PLAN: Do NOT attempt to read the entire codebase blindly. Instead, actively use your search tools (`grep_search`, `view_file`) to precisely target related files. Create an exhaustive, detailed execution plan containing specific `TARGET (Modify)` and `CONTEXT (Read-Only)` files. DESTRUCTIVE OPERATION INVENTORY: If refactoring involves DELETING or REPLACING any source file, you MUST line-by-line inventory every exported symbol and map its new location. BIDIRECTIONAL INTEGRATION CHECK: For any new parser or data consumer, you MUST explicitly document the corresponding PRODUCER.</step>
    
    <step id="2">FAIL-FAST DATA CONTRACTS: State exactly where `AppException` will be raised if data is missing. Do not use silent fallbacks.</step>
    
    <step id="3">PRO-TOOL UI/UX: Output localized keys only via the API. Do not hardcode frontend strings. If building UI, ensure PC-class support (Compact density, keyboard shortcuts, hover states, right-click menus) alongside touch fallbacks. Do not build mobile-only layouts for the Admin Studio.</step>
    
    <step id="4">EXECUTE &amp; PAUSE: Present the root cause or execution plan, get confirmation ("PERMISSION GRANTED") from the user, and write the code adhering strictly to the `rules` directory. PRE-DELETE AUDIT: Before executing ANY file deletion listed in your plan, you MUST read the file and grep for all its exported symbols to guarantee they exist in their new locations.</step>
    
    <step id="5">RED-GREEN-REFACTOR MANDATE: Every new feature or refactor must begin with writing a failing Unit Test. You MUST run the tests YOURSELF using the `run_command` tool via the Universal Quality Gate as defined in `AGENTS.md`. Do NOT tell the user to run the tests. END-TO-END SMOKE TEST: You MUST verify the change works in the actual runtime context before marking the refactoring complete.</step>
    
    <step id="6">DOCUMENTATION AUDIT MANDATE: If the refactoring introduced new systems, modified data flows, shifted architectural boundaries, or created directories, you MUST physically modify the documents in `docs\architecture\` AND `.agents\rules\04_directory_reference.md`, strictly maintaining their existing table structures. Do NOT update architecture documentation for minor tweaks.</step>
    
    <step id="7">HARDENING RECOMMENDATION: Once the feature is fully refactored, tests pass, and the Universal Quality Gate is green, explicitly suggest to the user that they should run the Tier 2 Hardening workflow. You MUST build and present the ready-to-run slash command for them (e.g., `/tier2-hardening-backend backend_v2/target_dir`).</step>
  </execution_protocol>
</system_prompt>
```
