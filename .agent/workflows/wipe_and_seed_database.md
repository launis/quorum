---
description: Completely wipes the local DB and reconstructs it from the Safe Seed file.
---
# Database Wipe & Seed Workflow
Use this workflow when the user requests to reset the system, clear out trash, or seed a fresh local environment.

1. **Verify Context:** Ensure you are operating in the local TinyDB context (`data/db_v2.json`), NOT Firestore.
2. **Execute Wipe Utility:** 
// turbo
   Run `python c:\src\quorum\backend_v2\seed\wipe_user_data.py`.
3. **Execute Seed Utility:**
// turbo
   Run `python c:\src\quorum\backend_v2\seed\run_seed.py local`.
4. **Report:** Notify the user that the database is pure and aligned with `seed_data.json`.
