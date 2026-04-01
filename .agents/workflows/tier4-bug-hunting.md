---
description: Tier 4 (Bug Hunting & RCA) - Workflow for deep root cause analysis and resolution of a specific bug.
---

### 🟣 TIER 4: BUG HUNTING & ROOT CAUSE ANALYSIS (Bug resolution)
*Usage: Use this workflow for systematic bug tracking and resolution without patching symptoms.*

```text
Goal: [WRITE BUG HERE. Ex: "API throws a 500 error on the /profile route"]

ROLE: Lead Security & Quality Auditor.
REFERENCE: read `c:\src\quorum\.agents\rules\` (00, 01, 02, 03).

INSTRUCTIONS (LEVEL 4):
1. IDENTIFY: Trace data flow to its origin. DO NOT patch symptoms. DO NOT add `if x is None: return []` or `try-except pass` just to silence errors.
2. TDD REPRO (RED): Before modifying the domain code, write a failing `pytest` or `flutter test` that reliably reproduces the bug.
3. EXPLAIN: Explain the Root Cause of the bug briefly based on the failed test trace.
4. FIX (GREEN): Propose an atomic code fix that solves the bug and makes the test pass. Wait for "PERMISSION GRANTED" before modifying files.
5. VERIFY (REFACTOR): Instruct the user to run the specific test and The Universal Quality Gate commands (from `00-antigravity-core.md` section 4).
```
