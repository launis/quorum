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
3. REPORT: If ANY critical violation is discovered, refuse to pass the code. Fix them immediately using strict best practices.
```
