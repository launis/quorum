# Backend Seed Directory

This document explains the central logic for managing the application's database state. It handles **seeding** (populating databases from a source file) and **synchronization** (saving database state back to the source file).

## Core Files

- **`backend/seed/seed_data.json`**: The **Source of Truth**. This JSON file contains the "Golden State" of the system configuration (Agents, Workflows, Components, System Config). It is version-controlled and used to reset databases.
- **`backend/seed/seeder.py`**: The core Python module that implements the logic for reading `seed_data.json` and upserting it into the target database (TinyDB or Firestore).
- **`backend/seed/syncer.py`**: The core Python module that implements the logic for reading a target database and exporting its configuration back to `seed_data.json`.

## Operation Scripts (Run these)

These scripts are wrappers that configure the environment variables correctly before calling the core modules. **Always use these scripts instead of calling modules directly.**

### Database Resets (Destructive)

These scripts **wipe and re-populate** the target database using the data from `seed_data.json`.

- **`seed_mock.py`**
  - **Target:** Mock Database (`backend/database/db_mock.json`)
  - **Usage:** Run when you want to reset your local development (mock) environment.
  - **Command:** `python backend/seed/seed_mock.py`

- **`seed_prod.py`**
  - **Target:** Production Database (`data/db.json`)
  - **Usage:** Run when you want to reset your local production environment to the clean state. **WARNING: Deletes all local production data.**
  - **Command:** `python backend/seed/seed_prod.py`

- **`seed_firestore.py`**
  - **Target:** Google Cloud Firestore (Live Production)
  - **Usage:** Run when you want to reset the live cloud database. Requires Google Credentials.
  - **Command:** `python backend/seed/seed_firestore.py`

### Synchronization (Saving Work)

These scripts update `seed_data.json` from a database source.

- **`sync_db_to_seed.py`**
  - **Source:** Production Database (`data/db.json`)
  - **Action:** Reads the current configuration from Prod DB and saves it to `seed_data.json`.
  - **Usage:** Run this after making changes in the Admin UI that you want to save to the repository.
  - **Command:** `python backend/seed/sync_db_to_seed.py`

- **`deploy_mock_to_prod.py`**
  - **Source:** Mock Database (`backend/database/db_mock.json`)
  - **Action:** 
    1. Syncs Mock DB -> `seed_data.json`.
    2. Seeds `seed_data.json` -> Production DB.
  - **Usage:** Run this to promote changes tested in Mock mode directly to local Production mode.
  - **Command:** `python backend/seed/deploy_mock_to_prod.py`

### Verification (Checking Sync Status)

These scripts **read** the databases and compare them to `seed_data.json` to verify everything is in sync. They are **read-only** and safe to run at any time.

- **`verify_sync.py`**
  - **Action:** Compares `seed_data.json` against:
    1. Local Production DB (`data/db.json`)
    2. Mock DB (`backend/database/db_mock.json`)
    3. Firestore DB (if `service-account.json` is present)
  - **Goal:** Output should read **"ALL SYSTEMS SYNCED"**.
  - **Command:** `python backend/seed/verify_sync.py`


## Database Hierarchy & Roles

Understanding the specific role of each data location is critical for the "Source of Truth" workflow.

### 1. The Source of Truth (`backend/seed/seed_data.json`)
*   **Role:** The **Golden Master**. This Git-committed file contains the definitive initial state for the system (Agents, Models, Prompts, Configs).
*   **Workflow:** All databases are seeded *from* this file. When you make stable changes in the UI that should be permanent, you sync them back *to* this file.

### 2. The Mock Database (`backend/database/db_mock.json`)
*   **Role:** **Transient / Experimental**. Used when running the backend in `MOCK_DB=true` mode.
*   **Purpose:** Allows rapid iteration and testing without affecting your main local database. You can trash this database freely and re-seed it in seconds.
*   **Zero-Cost Mocking:** When running in this mode, **NO real LLM calls are made**. The system is completely disconnected from Vertex AI / OpenAI.

### 3. The Local Production Database (`data/db.json`)
*   **Role:** **Local Persistence**. Used when running the backend in standard mode.
*   **Purpose:** Represents the "real" state of your local application. This is where your actual work and history live when running locally. It isolates your persistent local data from the experimental mock data.

### 4. Firestore DB (Google Cloud)
*   **Role:** **Live Production**. The actual cloud database used by the deployed application.
*   **Purpose:** Serves real users. It is updated only via the `seed_firestore.py` script (for config) or by actual user usage.
