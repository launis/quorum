# Data Seeding & Ontology

## 1. Executive Summary
The **Data Seeding & Ontology** capability dictates that the Compound AI System is fundamentally **data-driven**, not code-driven. The entire behavior of the system—ranging from LLM instructions (PromptBlocks), allowed models, MCP tool gateways, to performative vocabularies—is defined externally in the `seed_data.json` repository. The backend's primary role is simply to parse, hydrate, and route this declarative ontology rather than hardcoding operational instructions.

## 2. Core Architectural Invariants (The Laws)

These absolute rules (Knowledge Items) govern the global context and must NEVER be violated:

### 2.1. Polymorphic Rule Routing
- **Law:** The system prohibits fractured rule models or hardcoded prompt logic inside Python files.
- **Enforcement:** All dynamic rules must be modeled as a unified `PromptBlock` entity within the database. The system utilizes Polymorphic Collection Parsing to automatically route different categories of data (e.g., `system_config`, `prompt_blocks`, `mcp_gateways`) into their respective Pydantic validation structures, simplifying the LLM DAG engine.

### 2.2. Single Source of Truth (SSOT) Immutability
- **Law:** The JSON structure of `seed_data.json` is the highest architectural authority for data shape.
- **Enforcement:** You MUST NEVER physically alter the root persistence arrays in the `seed_data.json` to match transient API shapes. While the backend API may expose nested, stitched structures (e.g., combining Workflows and Profiles), the underlying physical seed data must remain flat and relational to avoid cascading data corruption.

### 2.3. The Y-Funnel Pre-Hook Architecture
- **Law:** Data transformations during seeding must not pollute the pure domain objects.
- **Enforcement:** The system uses a Y-Funnel architecture where Pre-Hooks manage structural migrations (e.g., from V1 to V2 paradigms) *before* data enters the domain validation phase. This ensures backward compatibility for older JSON definitions without polluting the strict Pydantic V2 Domain Models with legacy parsing logic.

### 2.4. Semantic Localization (Performative Lexicons)
- **Law:** System personality and localization strings are data, not code.
- **Enforcement:** Attributes like specific vocabulary (e.g., forcing the AI to use "delve into" or "syventyä") are injected dynamically via `performative_lexicons` defined in the seed data. The LLM engine must apply these lexicons post-resolution, allowing multi-lingual operation without altering the core logic.

## 3. Logical Data Flow
```mermaid
flowchart TD
    A[seed_data.json] --> B[Seed Loader Utility]
    B --> C{Polymorphic Router}
    C -- Type: system_config --> D[System Config Models]
    C -- Type: prompt_blocks --> E[PromptBlock Models]
    C -- Type: mcp_gateways --> F[MCP Tool Registries]
    D & E & F --> G{Pydantic V2 Validation}
    G -- Invalid --> H[Fail-Fast & Crash]
    G -- Valid --> I[In-Memory / Database State]
    I --> J[LLM Execution Engine]
```

## 4. Physical Implementation Map (Auto-Generated)
> **Note:** This section is automatically maintained by the Tier 7 execution agent. Do not manually update physical file paths here.
- **Backend Entrypoints:** `backend_v2/seed/seed_data.json` (SSOT), `backend_v2/models/enums.py` & `backend_v2/models/v2_core.py` (Pydantic V2 Domain Models), `backend_v2/services/orchestrator/schema_factory.py` (Polymorphic Router), `backend_v2/services/localization.py` (Semantic Localization), `backend_v2/api/routers/studio/` (Ontology CRUD Endpoints), `backend_v2/services/studio/` (WorkflowService, SystemConfigService, SimulationService, PromptBlockService, OutputProfileService, LexiconService), `backend_v2/database/repositories/components/` (Domain-Specific Ontology Repositories: PromptBlocks, Matrices, Personas, Roles, Protocols), `backend_v2/database/` (Data Persistence & Wrappers).
- **Frontend Consumers:** `client_app_v2/lib/core/models/prompt_block_category.dart` (Enum Mapping).
