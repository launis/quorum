---
description: Tier 5 (Zero-Shortcut Audit) - Workflow for ruthless code review against the V5.2 Phase 9 Hardening constraints.
---

### 🟠 TIER 5: ZERO-SHORTCUT AUDIT (Judging and code quality assurance)
*Usage: Use this workflow to aggressively audit newly written code against the IDE Protocol constraints.*

```text
Goal: Audit the newly written files: [WRITE FILES HERE, e.g., backend_v2/api/router.py]

ROLE: Ruthless Code Reviewer.
REFERENCE: read `c:\src\quorum\.agents\rules\` (00, 01, 02, 03).

INSTRUCTIONS (LEVEL 5):
1. Review the provided targets aggressively against the Single Source of Truth architecture rules in `c:\src\quorum\.agents\rules\`.
2. Look strictly for: `try-except pass` blocks, silent `{}` returns masking data errors, naked `ValueError` raises, implicit domain defaults (like `score = 0.0`), Main Thread Jank risks (missing `Isolate.run` on heavy JSON), and hardcoded localization strings.
3. TESTING MANDATE CHECK: Verify if the presented code logic includes an updated Unit Test. If new core logic is created without tests, it's an immediate fail.
4. QUALITY GATE CHECK: Check if the submitter explicitly provided The Universal Quality Gate (Ruff/Mypy/Flutter toolchain) commands for the step.
5. REPORT: If ANY critical violation is discovered, including missing tests (Step 3) or unlinted code (Step 4), immediately declare the audit REFUSED. Fix them immediately using strict best practices and provide The Universal Quality Gate commands to the user to re-verify.
```
