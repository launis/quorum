# Backend Seed Directory

This directory contains the central logic and scripts for managing the application's database state. It handles **seeding** (populating databases from a source file) and **synchronization** (saving database state back to the source file).

## Core Files

- **`seed_data.json`**: The **Source of Truth**. This JSON file contains the "Golden State" of the system configuration (Agents, Workflows, Components, System Config). It is version-controlled and used to reset databases.
- **`seeder.py`**: The core Python module that implements the logic for reading `seed_data.json` and upserting it into the target database (TinyDB or Firestore).
- **`syncer.py`**: The core Python module that implements the logic for reading a target database and exporting its configuration back to `seed_data.json`.

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
  - **Usage:** Run when you want to deploy the seed configuration to the live cloud database. Requires Google Credentials.
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
