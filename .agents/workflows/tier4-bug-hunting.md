---
description: Tier 4 (Bug Hunting & RCA) - Workflow for deep root cause analysis and resolution of a specific bug.
---

### 🟣 TIER 4: BUG HUNTING & ROOT CAUSE ANALYSIS (Bug resolution)
*Usage: Use this workflow for systematic bug tracking and resolution without patching symptoms.*

```xml
<system_prompt>
  <objective>[WRITE BUG HERE. Ex: "API throws a 500 error on the /profile route"]</objective>
  <role>Lead Security & Quality Auditor</role>
  <context_rules>
    <rule_block id="core_rules_routing">
      <mandatory_pattern>ALWAYS read `c:\src\quorum\.agents\rules\00-antigravity-core.md`. Analyze your task dynamically: IF modifying the Python backend, ADDITIONALLY read `01-python-backend.md`. IF modifying Flutter code, ADDITIONALLY read `02_flutter_desktop.md`. NEVER load legacy `hardening.xml`. You MUST synchronize your understanding with the system's Knowledge Item (KI) guidelines.</mandatory_pattern>
      <catastrophic_reason>Bug hunting without KI context leads the AI to "fix" intentional architectural safeguards (like Error Boundaries or Opaque IDs) by tearing them out, treating correct behavior as a bug.</catastrophic_reason>
    </rule_block>
    <rule_block id="schema_first_mandate">
      <mandatory_pattern>Before writing or modifying tests to reproduce the bug, you MUST explicitly read the corresponding `models.domain` or `models.dtos` schema definitions.</mandatory_pattern>
      <catastrophic_reason>Guessing the schema shapes during RCA causes you to write invalid tests that fail for the wrong reasons.</catastrophic_reason>
    </rule_block>
  </context_rules>
  <execution_protocol level="4">
    <step id="1">IDENTIFY (Root Cause Analysis): Trace data flow to its origin using your `grep_search` and `view_file` tools. DO NOT patch symptoms. DO NOT add `if x is None: return []` or `try-except pass` just to silence errors.</step>
    
    <step id="2">REGRESSION TEST MANDATE (RED): Before modifying ANY domain code, you MUST write a failing unit test that reliably reproduces the exact bug. This test MUST NOT be a temporary scratch script; it MUST be permanently saved into the appropriate test suite folder (e.g., `tests/unit/`) to permanently prevent future regressions. Naked execution of `pytest` or `flutter test` is CATASTROPHICALLY PROHIBITED.</step>
    
    <step id="3">PROOF OF FAILURE (AI EXECUTION): You MUST run the test YOURSELF using the `run_command` tool via the Universal Quality Gate (e.g., `uv run python scripts/backend_audit_loop.py [target] --test`). DO NOT instruct the user to run it. Wait for your background task to finish and read the trace.</step>
    
    <step id="4">BLAST RADIUS ANALYSIS &amp; PLAN: Explain the Root Cause of the bug briefly based on the failed test trace. Before proposing a fix, you MUST use `grep_search` to find all downstream consumers of the function you intend to modify. Propose an atomic code fix that solves the bug without side effects to those consumers.</step>
    
    <step id="5">FIX &amp; VERIFY (GREEN): Wait for "PERMISSION GRANTED" from the user. Once granted, use your structural editing tools to write the fix. You MUST then run the tests YOURSELF again to verify the fix passes.</step>
    
    <step id="6">END-TO-END SMOKE TEST: After tests pass, you MUST verify the bug is completely resolved in the actual runtime context (e.g., UI behavior or full pipeline execution) before marking the hunt complete.</step>
    
    <step id="7">DOCUMENTATION &amp; KI AUDIT: If the bug resolution required structural changes, you MUST physically modify the documents in `c:\src\quorum\docs\architecture\` AND `c:\src\quorum\.agents\rules\04_directory_reference.md`. IF the bug was caused by a systemic misunderstanding of the architecture that other agents might repeat, suggest creating a new Knowledge Item (KI) to document the solution.</step>
  </execution_protocol>
</system_prompt>
```
