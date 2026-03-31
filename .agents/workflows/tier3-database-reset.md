---
description: Tier 3 (Database Reset) - A single-operation workflow to safely instruct the user to wipe and re-seed the local TinyDB development database.
---

### 🔴 TIER 3: DATABASE RESET (Single Operation)
*Usage: Use this workflow when the user requests to reset the system, clear out trash, or seed a fresh local environment.*

```text
Goal: Reset the Local Data Environment.
ROLE: Database Administrator.
REFERENCE: `c:\src\quorum\.agents\rules\03_seed_vault.md`

INSTRUCTIONS (LEVEL 3):
1. VERIFY CONTEXT: Ensure you are operating in the local TinyDB context (`data/db_v2.json`), NOT Firestore.
2. DATABASE WIPE: Generate a PowerShell block containing the command to wipe the database. Do NOT auto-execute.
   Command format: `uv run python backend_v2\seed\wipe_user_data.py`
3. DATABASE SEED: Generate a PowerShell block containing the command to re-seed the database. Do NOT auto-execute.
   Command format: `uv run python backend_v2\seed\run_seed.py local`
4. INSTRUCT THE USER: Output the commands and explicitly ask the user to run them in their PowerShell instance, fulfilling the CRITICAL WIN11 CONSTRAINTS.
5. REPORT: Once the user confirms execution, verify the success programmatically (check JSON size/content).
```
