# Data Management & Databases (V2.5)

**Status:** Enterprise V2.5 Production Standard
**Core Philosophy:** The "Mind" (Logic) is Data; The "Spine" (Execution) is Deterministic Code.

The engine is fundamentally **data-driven**: cognitive business logic, evaluating matrices, and UI rules are stored natively as JSON documents (the "Mind"), while strict data contracts and validation are enforced via deterministic Python/Dart code (the "Body/Spine").

> [!IMPORTANT]
> **Enterprise V2 Standard: Strict Pydantic V2 & Zero-Deploy**
> All internal state and data transfer MUST use **Pydantic V2 Models** (`ConfigDict(strict=True)`). Dictionary passing or dynamic type coercion is strictly forbidden in the Service and API layers. Järjestelmä siirtää kaiken kognitiivisen liiketoimintalogiikan, datareitityksen, arvioinnin kalibroinnin ja käyttöliittymän piirtosäännöt tietokantaan (Zero-Deploy).
> 
> *Tekoälyn säännöstöt ja Single Source of Truth (SSOT) on keskitetty ohjaustiedostoihin:* **`GEMINI.md`** *sekä* **`AGENTS.md`**.

---

## 1. The Blueprint Authority Pattern & Data as Logic

In Cognitive Quorum V2, the core "reasoning logic" is abstracted into data. Database edits orchestrate the AI without requiring fresh deployments (Zero-Deploy).

### 1.1 Data as Software Logic
* **Cognitive Mandates are Data:** The instructions, scoring matrices, hook definitions, and penalty multipliers that constrain the LLM's reasoning are stored entirely as database records within the `prompt_blocks` collection.
* **Universal Orchestration:** The dynamic Directed Acyclic Graph (DAG) defines how nodes are chained (`workflows`), eliminating hardcoded agent sequences.
* **Single Source of Truth (SSOT):** `backend_v2/seed/seed_data.json` acts as the master blueprint for the AI's mind.

### 1.2 The Bidirectional Seeding System
The engine employs a bidirectional seeding mechanism to enforce the SSOT while allowing structural iteration.

1. **Seeding (Blueprint $\rightarrow$ Database via `run_seed.py`):** The engine ingests `seed_data.json` directly into the Runtime Database (`db_v2.json` or Firestore). This enforces mathematical Pydantic validation upon entry.
   - *🚨 Recovery Protocol (Data Integrity):* If programmatic patches or seeder scripts crash, developers must *never* blindly revert or overwrite `seed_data.json` with a backup. Script failures must be analyzed, and targeted fixes applied incrementally. Overwriting destroys active manual translation blocks and structural data changes.
   - *Safety Feature:* Automatically generates a timestamped backup in `backend_v2/seed/backups/` before clearing target tables. Do not manually edit `db_v2.json` to bypass this.
2. **Extraction (Database $\rightarrow$ Blueprint via `migrate_to_seed.py`):** Development modifications from the database can be extracted back into the SSOT blueprint, ensuring structural parity.

---

## 2. The 3-Tier Data Model

Data persists across a 3-tier operational lifecycle:

1. **Tier 1 (Local Testing - Mocks):** Rapid offline UI development via local `db_v2.json` and a `USE_MOCK_LLM=true` engine.
2. **Tier 2 (Local Production - Live):** High-fidelity local database testing utilizing Live Cloud LLMs (e.g., Gemini Vertex integration directly against the local `db_v2.json`).
3. **Tier 3 (Cloud Production):** Standard multi-tenant ecosystem running solely on Google Cloud Firestore natively.

Both Tiers 2 & 3 rely heavily on `system_configs` mappings. Operational strategies (`fast`, `deep` contexts) are entirely decoupled from rigid code, allowing operators to freely shift models in configuration depending on scale requirements without deploying any core code.

---

## 3. Backend Data Layer ("No-ORM")

### 3.1 The Gatekeeper (Service Layer)
The API Layer (`backend_v2/api/`) is strictly anemic. It parses HTTP text into Pydantic models, immediately delegating to the **Domain Service Layer** (`backend_v2/services/`). Only the Service Layer is authorized to compute business relations, isolate tenants, and command the database.

### 3.2 Dual Backend Parity
Object-Relational Mapping (ORM) tools structured for SQL (like SQLAlchemy) are banned. 
Pydantic V2 generates the schema natively. Any CRUD modification must be perfectly mirrored across:
1. `backend_v2/database/repository.py` (Local TinyDB logic).
2. `backend_v2/database/firestore_repo.py` (Cloud Firestore logic).

### 3.3 The Strict DTO Pattern (Air Gap)
To prevent the LLM from manufacturing or mutating relational data, execution relies on the Strict DTO Pattern:
- The LLM emits a purely substantive JSON object (e.g., scoring array via Structured Outputs).
- The executed Python Agent intercepts this payload into a Pydantic DTO inside the Hook Ecosystem.
- The Python layer acts as the absolute authority, injecting server metadata (Execution ID, Timestamp, Organization ID) via pre-hooks like `inject_step_metadata`, sealing the Domain Model before saving it against the `executions` ledger table as `frozen_context` and `results`.

---

## 4. NoSQL Design & Firestore Strategy

### 4.1 Polymorphic PromptBlocks
Because NoSQL architectures like Firestore punish relational JOIN queries, fragmented cognitive components (Instructions, Matrices, Hooks) are deliberately consolidated into a massive single **`prompt_blocks`** collection.
* The system utilizes a polymorphic `"type"` routing key on the documents.
* Pydantic instantly reconstructs these JSON payloads back into highly typed Python subclasses (e.g., `PromptBlockMatrix`) upon reading.

### 4.2 Explicit Isolation Limits
While configurations are grouped polymorphically, core transactional entities (`users`, `organizations`) exist in rigidly separated collections. This guarantees granular Role-Based Access Control (RBAC) validations at the Domain Service level.

---

## 5. Client-Side Data Integration (Flutter SDUI)

The Flutter UI matches backend rigidity, employing a **Server-Driven UI (SDUI)** approach.
* **Strict Typing:** API payloads are bound to generated Dart objects utilizing `freezed` and `json_serializable`.
* **Optimistic Updates:** The Riverpod (`@riverpod`) state engine prioritizes responsive local caching and optimistic UI writes over synchronous database blocking.
* **Defensive Rendering (Graceful Degradation):** Omni-channel SDUI objects utilize defensive Dart parsing known as `SafeCast`. If an incoming payload corrupts or fundamentally changes shape, the dynamic UI component wraps the failure in a logged RFC 7807 Error code and renders `SizedBox.shrink()`—isolating the crash from the user application.
* **The No-String Mandate:** Enumerated states from the database (e.g., `"AUTH_ORGANIC"`) are never hard-typed or concatenated. Formatting relies entirely on `.arb` file bindings utilizing standard ICU formatting.