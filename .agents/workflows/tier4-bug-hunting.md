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
    <rule>ALWAYS read `c:\src\quorum\.agents\rules\00-antigravity-core.md`. Analyze your task: IF modifying Python backend, ADDITIONALLY read `01-python-backend.md`. IF modifying Flutter code, ADDITIONALLY read `02_flutter_desktop.md`. Do NOT load unnecessary domain rules into memory.</rule>
    <rule>Before writing or modifying tests, you MUST explicitly read the corresponding `models.domain` or `models.dtos` schema definitions.</rule>
    <rule>You MUST adhere to the architectural mandates defined in `c:\src\quorum\scripts\hardening.xml`.</rule>
  </context_rules>
  <execution_protocol level="4">
    <step id="1">IDENTIFY: Trace data flow to its origin. DO NOT patch symptoms. DO NOT add `if x is None: return []` or `try-except pass` just to silence errors.</step>
    <step id="2">TDD REPRO (RED): Before modifying the domain code, write a failing unit test that reliably reproduces the bug. Naked execution of `pytest` or `flutter test` is forbidden; you must use the appropriate wrapper (e.g. `uv run pytest path/to/test.py`).</step>
    <step id="2.5">PROOF OF FAILURE: PAUSE HERE. Instruct the user to run the test. You MUST WAIT for the user to paste the raw failing test trace output. Do not guess the root cause without seeing the actual error logs.</step>
    <step id="3">EXPLAIN: Explain the Root Cause of the bug briefly based on the failed test trace.</step>
    <step id="4">FIX (GREEN): Propose an atomic code fix that solves the bug and makes the test pass. Wait for "PERMISSION GRANTED" before modifying files.</step>
    <step id="5">VERIFY (REFACTOR): Instruct the user to run the specific test and The Universal Quality Gate commands (from the `<universal_quality_gate>` block in `00-antigravity-core.md`). END-TO-END SMOKE TEST: After tests pass, you MUST verify the bug is completely resolved in the actual runtime context (e.g., UI behavior or full pipeline execution) before marking the hunt complete.</step>
  </execution_protocol>
</system_prompt>
```
