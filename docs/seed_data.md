# System Seeding & Data Lifecycle (V5.1 - Phase 9 Hardening)

In **Cognitive Quorum V5.1**, the system follows a strict **Unidirectional Data Flow**. The `backend/seed/seed_data.json` file is the **Immutable Source of Truth** (SSOT) for all configuration, logic, and structure.

> **Note**: Seeding requires **Python 3.14.2+** to ensure consistent hashing and Pydantic V2 validation behavior.

We do *not* sync runtime database changes back to the codebase. Instead, we edit the "DNA" of the system (`seed_data.json`) and re-seed the "Organism" (Database).

---

## 1. The Source of Truth (`seed_data.json`)

Located at `backend/seed/seed_data.json`. This version-controlled file contains the "Golden State" of the system.

### Schema Structure
The file defines six core domains:

1.  **`system_config`**: Global settings and **Model Registry**.
    *   Defines valid LLM models (e.g., `vertex_ai/gemini-2.5-pro`).
    *   **Agent Strategies**: Maps Agents (e.g., `PanelAgent`) to Models (`deep`) to avoid hardcoding.
2.  **`organizations`**: Multi-tenancy definitions.
    *   Includes `system` (Root) and tenant configs (Quotas, Tiers).
3.  **`users`**: Seeded identities.
    *   **Root User**: `root_master` (God Mode).
    *   **Tenant Admins**: `admin_1`, etc.
4.  **`components`**: Reusable Logic Blocks.
    *   **Prompts**: Mandates, Rules, Protocols.
    *   **Matrices (BARS)**: Evaluation criteria (automatically hydrates Ontology).
5.  **`workflows`**: Execution Blueprints.
    *   Defines the graph structure, steps, and default configuration.
6.  **`steps`**: The Step Registry. Reusable step definitions that workflows reference.
7.  **`agents`**: Explicitly separated autonomous agent configurations.
8.  **`concepts`, `references`, `claims`**: The Decoupled Knowledge Base. Stored as distinct strict DTO collections natively typed.

---

## 2. The Unified Seeder CLI (`run_seed.py`)

We use a single entry point for all seeding operations. This script wipes the target database and repopulates it from `seed_data.json`.

**Location**: `backend/seed/run_seed.py`

### Usage

```bash
# 1. Local Development (Standard)
# Resets 'data/db.json'. Use this for normal feature development.
python backend/seed/run_seed.py local

# 2. Mock Mode (Offline/Testing)
# Resets 'backend/database/db_mock.json'. Use for unit tests or UI work without LLM costs.
python backend/seed/run_seed.py mock

# 3. Production (Google Cloud Firestore)
# WARNING: Destructive operation. Overwrites the Cloud Database.
# Requires 'GOOGLE_APPLICATION_CREDENTIALS'.
python backend/seed/run_seed.py firestore
```

---

## 3. Data Lifecycle Models

### The "Blueprint Authority" Model
In V5.1, we moved strictly away from bi-directional syncing.

*   **OLD Way**: Edit in UI -> Sync to Code -> Commit. (Drift Prone).
*   **NEW Way**: Edit `seed_data.json` -> Seed to DB -> View in UI. (GitOps).

### Why?
1.  **Reviewability**: Configurations (Prompts, Matrices) are code. They should be reviewed in Pull Requests.
2.  **Predictability**: The database is always a pure derivation of the code.
3.  **Strict Pydantic Validation**: Seeder enforces strict schemas. You cannot seed invalid data. It fails fast.

### 3.1. Schema-Agnostic Seeder and Universal Registry
The seeder scripts (`run_seed.py` and `migrate_to_seed.py`) are strictly "Schema-Agnostic", powered by a centralized **Universal Seed Registry** (`backend/seed/seed_registry.py`). This means **you never need to modify the seeder scripts when adding new fields or collections to the database or models.**

*   **`seed_registry.py` (SSOT)**: Defines the mapping between database collections (e.g., `workflows`), their Pydantic Models (e.g., `WorkflowDefinition`), and their primary keys (e.g., `id` vs `uid`).
*   **Forward Seeding (`run_seed.py`)**: Uses a single programmatic loop over `STANDARD_REGISTRY`. It dynamically invokes Pydantic's `.model_validate()` and `.model_dump(mode='json')`. If a new collection or field is added, the seeder automatically processes it without needing explicit loops.
*   **Reverse Migration (`migrate_to_seed.py`)**: Iteratively extracts live data from either TinyDB (`local`) or Firestore (`firestore`) and merges it back into `seed_data.json` while meticulously preserving the original key order, again utilizing the Universal Registry to identify the correct ID fields.

### 3.2. "Round-Trip" Testausprotokolla
Käyttäjän asettama pakollinen testausprotokolla, jolla varmennetaan datan säilyminen bitti bitiltä integraattoria käytettäessä, suoritetaan aina tällä kaavalla:
1. **Turva:** Otetaan puhdas kopio alkuperäisestä `backend/seed/seed_data.json` (esim. `seed_data_test_roundtrip.json`). Tähän ei kosketa.
2. **Kantaan (Lataus):** Ajetaan `python backend/seed/run_seed.py local`. Tuhoaa kannan ja kirjoittaa erilliset taulut.
3. **Takaisin (Purku):** Ajetaan `python backend/seed/migrate_to_seed.py`. Lukee kannasta takaisin `seed_data.json`.
4. **Varmennus:** 
   - Verrataan kokonaisrivimäärää (`wc -l`).
   - Verrataan taulujen määrää (esim. 12 avainta).
   - Verrataan rivien määrää sisäisissä listoissa (esim. `len(agents) == 15`).
Jos eroja on `0` ja kaikki tiedostot näyttävät identtisiltä (paitsi puhtaat poistot kuolleelle koodille), rakenne-uudistus merkitään tuotantovalmiiksi.

### 3.3. Legacy Field Strip (Data Extraction) Protocol
Sometimes the data structure (`seed_data.json`) contains "Dead Code" fields (like `monitored_steps` or generic `metadata`) that are no longer supported by the Strict DTO Pydantic models. To safely amputate a field universally:

1. **Verify Expiration**: Use a grep search over the `backend/` directory. If the key is not defined, retrieved, or populated in ANY Python file, it is safe to erase.
2. **Back up**: Create a pre-strip backup (`cp seed_data.json seed_data.json.PRE_STRIP.bak`).
3. **Script the Purge**: Do NOT use regex to delete keys, as it risks corrupting JSON syntax or touching similarly named fields in the wrong context. Write a targeted Python script that traverses the defined components and executes `del item['config']['dead_key']`.
4. **Validate**: Perform the Data Integrity Roundtrip Protocol (Step 3.2) to ensure the newly "slimmed down" models correctly sync with databases. Run `pytest` and `ruff` to prove full systemic immunity.

---

## 4. Derived Data (Ontology)

The Seeder performs **Intelligent Extraction**. It does not just copy JSON; it transforms it.

*   **Example**: The `dimensions` table in the database is NOT in `seed_data.json`.
*   **Mechanism**: The Seeder scans all `evaluation_matrix` components in `seed_data.json`. It extracts every `criteria` and `scale` definition, ensuring that the **Ontology Store** (`dimensions` table) is populated with granular, queryable records.
*   **Purpose**: This allows the `MatrixFormatter` to look up individual criteria by ID if needed, though primarily it serves the **Cognitive Studio** for UI-based editing.

---

## 5. Development Workflow

To add a new feature (e.g., a new "Reviewer" Agent):

1.  **Define Agent Strategy**: Add `ReviewerAgent` to `system_config` in `seed_data.json` with `model_strategy="precise"`.
2.  **Add Prompts**: Add `instruction_review_guidelines` to `components`.
3.  **Create Step**: Define the step in `steps` list.
4.  **Update Workflow**: Reference the step ID in `workflows`.
5.  **Apply**: Run `python backend/seed/run_seed.py local`.
6.  **Verify**: Open the Studio (`localhost:8000`) and test the workflow.
