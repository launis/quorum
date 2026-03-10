# Data Management & Databases (V2.5)

The engine is **data-driven**: logic definitions are stored in JSON (the "Mind"), but strict data contracts are enforced via Python/Dart code (the "Body").

> [!IMPORTANT]
> **Enterprise V2 Standard (Strict Pydantic V2 & Zero-Deploy)**
> All internal state management MUST use **Pydantic V2 Models**. Dictionary passing (`dict[str, Any]`) is strictly forbidden for inter-component communication. Järjestelmä siirtää kaiken kognitiivisen liiketoimintalogiikan, datareitityksen, arvioinnin kalibroinnin ja käyttöliittymän piirtosäännöt tietokantaan (Zero-Deploy).
> 
> *Tekoälyn säännöstöt ja Single Source of Truth (SSOT) on keskitetty ohjaustiedostoihin:* **`GEMINI.md`** *sekä* **`AGENTS.md`**.

---

## 1. The Blueprint Authority Pattern & Data as Logic

The engine is fundamentally **data-driven**. In Cognitive Quorum V2, the core "reasoning logic" is abstracted into data.

### Data as Software Logic
* **LLM Definitions are Data**: The instructions, matrices, and hooks that constrain the LLM's reasoning are stored entirely as database records in the `prompt_blocks` collection.
* **Dynamic Programming**: Changing a database record instantly alters how the system "thinks" and evaluates inputs. The database holds the AI's "Mind".
* **Single Source of Truth (SSOT)**: `data/seed_data.json` acts as the master blueprint for this logic.

### Database Data Flow
1. **Seeding (Blueprint to Database)**: `seed_data.json` is ingested into the Runtime Database (`db_v2.json` or Firestore). This step "compiles" the JSON blueprint into active database records.
2. **Execution Hydration (Database to Engine)**: When a workflow execution starts, the DAG Executor queries the database to fetch the necessary nodes and prompt blocks.
3. **State Persistence (Engine to Database)**: As the LLM processes the data, results (strictly validated via Pydantic) are written back to the database as `ExecutionRecords`.

---

## 2. The 3-Tier Data Model

The system utilizes a 3-tier hierarchy to differentiate between development environments.

### Tier 1: Local Testing (`data/db_v2.json` with Mocks)
*   **Purpose**: Rapid offline UI development.
*   **Inference**: Uses `USE_MOCK_LLM=true` (Zero-Cost).

### Tier 2: Local Production (`data/db_v2.json`)
*   **Purpose**: High-fidelity verification with **Live Cloud LLMs** but local storage.
*   **Seeding**: `uv run python backend_v2/seed/run_seed.py local`

### Tier 3: Cloud Production (Firestore)
*   **Purpose**: Multi-tenant SaaS operations in Google Cloud.
*   **Storage**: Google Cloud Firestore (Native).
*   **Seeding**: `uv run python backend_v2/seed/run_seed.py firestore`

---

## 3. Backend Data Layer (`backend_v2/`)

### 3.0. The "No-ORM" Pydantic Architecture
The backend is uniquely designed **without any traditional Object-Relational Mappers (ORMs)**. There is no SQLAlchemy or Prisma. 

**Pydantic V2 is the Absolute Single Source of Truth (SSOT).**
*   **Validation**: Pydantic validates incoming API requests.
*   **Datastore**: Pydantic defines the structure written to the database (Firestore).
*   **Documentation**: Pydantic generates the OpenAPI specifications.

### Strict Pydantic V2 (Phase 9 Hardening)
The system utilizes **Pydantic V2** for all internal state management.
1.  **Strict Models**: Data parsing strictly uses `ConfigDict(strict=True, extra="ignore")`.
2.  **Strict Enums Only**: Categorical data must match Enum values exactly.
3.  **Modular Domain**: Models are organized in `backend_v2/models/v2_core.py` to enforce strict separation of concerns.

### 3.1. Unified Workflow Executions
The core architecture for tracking a workflow in progress is built around the **`ExecutionRecord`** model.

*   **What it is:** The `ExecutionRecord` is an immutable, forward-only ledger. It contains the original inputs, a `frozen_context` guaranteeing auditability of the exact rules used, and the incremental `results` dictionary tracking each step's JSON outcome.
*   **The Air Gap:** The executor strictly separates generic HTTP inputs from internal Pydantic payloads. Inputs mapped to a specific node only become accessible to the LLM if they pass strict variable resolution logic (`$inputs.x`, `$steps.y`).

---

## 4. Client-Side Data Layer (Flutter)

The Flutter client mirrors the backend's strictness but uses a distinct architectural pattern tailored for UI resilience.

### DTOs and Serialization
*   **Strict Typing**: API responses are mapped to rigid Dart classes using `freezed` and `json_serializable`.
*   **Parity**: Dart models must exactly match the Pydantic schemas. A mismatch causes a localized UI ErrorBoundary capture, preventing whole-app crashes.

### Defensive Rendering (SafeCast)
When rendering SDUI rules from PromptBlocks (which may contain legacy bad data), the UI relies on defensive parsing methods (e.g., extracting `I18nText` safely) to guarantee rendering resilience.

---

## 5. Model Strategy Architecture (Model Registry)

The system employs an architectural pattern to decouple **Semantic Intent** from **Operational Constraints**. 
*   **Semantic Strategies**: `fast` (flash tasks) vs `deep` (pro tasks) vs `precise` (judge tasks).
*   **Global Registry**: The `system_config` table maps these semantic intents to physical cloud models (e.g., `gemini-2.5-pro`).
*   **Zero-Deploy Downgrades**: If an operational quota is hit, an administrator can edit the DB's `system_config` to route `deep` tasks temporarily to a `flash` model. The code does not change, only the data logic.

---

## 6. Database Schema & Firestore Deployment Strategy

The database architecture operates fundamentally under NoSQL best practices.

### 6.1. Polymorphic Collections (`prompt_blocks`)
In a relational model, UI Components, Rules, and Evaluation Matrices might live in distinct SQL tables. In our NoSQL architecture, these are purposefully **consolidated into a single `prompt_blocks` collection** leveraging a polymorphic `"type"` discriminator (`instruction`, `matrix`, `generator`, `hook`).

*   **The NoSQL Join Penalty:** Firestore does not support relational JOINs. Consolidating logic chunks allows for O(1) query patterns.
*   **Polymorphic Reconstruction:** The backend Pydantic tier seamlessly reconstructs these grouped objects back into their native strongly-typed classes (e.g., `PromptBlockMatrix`) upon reading from the database.

### 6.2. Isolated Entities (Users & Organizations)
Unlike polymorphic rule blocks, Core Entities (like `users` and `organizations`) are strictly isolated into their own dedicated collections.
*   **Security & Granular Permissions:** Keeping `users` and `organizations` separated allows the system to enforce explicit ACL boundary rules (e.g., Role-Based Access Control verified at the Domain Service Layer).