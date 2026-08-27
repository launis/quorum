# Data Seeding & Ontology

## 1. Executive Summary
The **Data Seeding & Ontology** capability dictates that the Compound AI System is fundamentally **data-driven**, not code-driven. The entire behavior of the system—ranging from LLM instructions (PromptBlocks), allowed models, MCP tool gateways, to performative vocabularies—is defined externally in the central static data vault. The backend's primary role is simply to parse, hydrate, and route this declarative ontology rather than hardcoding operational instructions.

## 2. Core Architectural Invariants (The Laws)

These absolute rules (Knowledge Items) govern the global context and must NEVER be violated:

### 2.1. Polymorphic Rule Routing
- **Law:** The system prohibits fractured rule models or hardcoded prompt logic inside Python files.
- **Enforcement:** All dynamic rules must be modeled as a unified `PromptBlock` entity within the database. The system utilizes Polymorphic Collection Parsing to automatically route different categories of data (e.g., `system_config`, `prompt_blocks`, `mcp_gateways`) into their respective Pydantic validation structures, simplifying the LLM DAG engine.

### 2.2. Single Source of Truth (SSOT) Immutability
- **Law:** The JSON structure of the central static data vault is the highest architectural authority for data shape.
- **Enforcement:** You MUST NEVER physically alter the root persistence arrays in the central static data vault to match transient API shapes. While the backend API may expose nested, stitched structures (e.g., combining Workflows and Profiles), the underlying physical seed data must remain flat and relational to avoid cascading data corruption.

### 2.3. The Y-Funnel Pre-Hook Architecture
- **Law:** Data transformations during seeding must not pollute the pure domain objects.
- **Enforcement:** The system uses a Y-Funnel architecture where Pre-Hooks perform structural data normalization *before* data enters the domain validation phase. This ensures heterogeneous JSON definitions are canonicalized into strict Pydantic V2 Domain Models without polluting the domain layer with transformation logic.

### 2.4. Semantic Localization (Performative Lexicons)
- **Law:** System personality and localization strings are data, not code.
- **Enforcement:** Attributes like specific vocabulary (e.g., forcing the AI to use "delve into" or "syventyä") are injected dynamically via `performative_lexicons` defined in the seed data. The LLM engine must apply these lexicons post-resolution, allowing multi-lingual operation without altering the core logic.

### 2.5. Universal I18n Domain Model (I18nText)
- **Law:** Dynamic localized strings must never be flattened into dictionary maps, legacy default locale properties, or separate schema fields (e.g., `title_en`).
- **Enforcement:** Any user-facing string that exists within the ontology (like profile titles, layout descriptions, and preambles) MUST use the strictly typed `I18nText` object in Python and Flutter. The schema mandates a required `translations` mapping containing non-empty baseline `'en'` and target language keys with 100% bilingual parity. This ensures Fail-Fast translation fallback resolution logic (`target -> fallback -> en`), structural parity across boundaries, and prevents UI crashes due to missing translation keys.

### 2.6. Workflow Context Governance & System Core Protections
- **Law:** Foundational pipeline steps and synthesis context boundaries must be declaratively governed within the ontology rather than assumed by ad-hoc runtime code.
- **Enforcement:** Foundational pipeline step definitions (such as raw document ingestion, scoring, holistic synthesis, and forensic XAI reporting) declare explicit system core protections (`is_system_core: true`). The system enforces immutable protection against deletion or unauthorized schema mutations on protected core resources. Furthermore, step rules declare explicit synthesis source flags (`is_synthesis_source`), enabling deterministic context boundary governance between upstream document extraction and downstream synthesis distillation.

### 2.7. The Epistemic Separation Paradigm (TheoryGrounding SSOT)
- **Law:** Bibliographic references and provenance metadata must be strictly decoupled from operational prompting instructions.
- **Enforcement:** `PromptBlock.theory_grounding` (`TheoryGrounding`) is the sole Single Source of Truth for citation references (`citation_reference`) and target URLs (`source_url`). `PromptBlock.ai_description` is strictly reserved for operational prompts (`OBJECTIVE:`, `ROLE:`, `MANDATE:`). Standardizing this structure eliminates semantic drift, prevents duplicate persistence of academic citations, and ensures that presentation layers and PDF reports consume clean, structured metadata without brittle string scraping.

## 3. Logical Data Flow
```mermaid
flowchart TD
    A[Central Static Data Vault] --> B[Seed Loader Utility]
    B --> C{Polymorphic Router}
    C -- Type: system_config --> D[System Config Models]
    C -- Type: prompt_blocks --> E[PromptBlock Models]
    C -- Type: mcp_gateways --> F[MCP Tool Registries]
    D & E & F --> G{Pydantic V2 Validation}
    G -- Invalid --> H[Fail-Fast & Crash]
    G -- Valid --> I[In-Memory / Database State]
    I --> J[LLM Execution Engine]
```
