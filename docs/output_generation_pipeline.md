# End-to-End Output Generation Pipeline (V3.2 - Phase 8 Standards)

## Overview

This document details the complete lifecycle of an output artifact (PDF Report or UI Screen) in the Cognitive Quorum system. It traces the data flow from the initial user input, through the cognitive processing layers, database persistence, and finally to the rendering tier.

**Core Philosophy**: The system separates **Cognition** (Thinking) from **Presentation** (Rendering). The "Brain" produces strict data models; the "Renderer" translates them into human-readable formats.

**Architecture Hardening Mandate (Phase 8)**: All data exchange between layers (Service -> Agent -> Hook -> Presentation) **MUST** use strict Pydantic models. Raw dictionaries or unstructured strings are strictly forbidden in internal APIs.

---

## 1. The Foundation: Database & Software Roles

### The Database (TinyDB / Firestore)
*   **Role**: The **Immutable Ledger**.
*   **Function**: Persists the entire event log (`WorkflowState`) of the execution.
*   **Significance**: Every output is reproducible. We can regenerate a report from past executions exactly as it was.

### The Software (GraphEngine & Agents)
*   **Role**: The **Deterministic Processor**.
*   **Function**:
    1.  **Hydration (Relational Model)**: Loads workflow *skeletons* and hydrates Step Definitions from the **Step Registry** (`UnifiedWorkflowRepository`). **No embedded steps allowed.**
    2.  **Execution**: Runs Agents (LLM) and Hooks (Python).
    3.  **Standardization**: Converts fuzzy LLM text into strict **Pydantic Models** (e.g., `ScoringResult`, `TextMetrics`, `KnowledgeItem`).
*   **Significance**: The software ensures that the "raw material" for the report is strictly typed and validated before rendering begins.

---

## 2. Phase I: Data Production (The "Backstage")

### Step 1: Input & Metrics (Hook-Based)
*   **Action**: User submits text.
*   **Software**: `backend/hooks/metrics.py` (via `calculate_text_metrics` Hook).
*   **Strict Typing**: Uses `WorkflowInputs` object.
*   **Result**: `TextMetrics` model is created.
*   **Constraint**: Fail Fast on invalid input (AppException).

### Step 2: Cognitive Processing (The Panel Fusion)
*   **Action**: Agents analyze the input.
*   **Evolution (V3.2)**: We use the **Panel Pattern**.
    *   **Fused Execution**: The `PanelAgent` runs *once* but acts as multiple critics (Logician, Falsifier, Causal, Overseer).
    *   **Fan-Out**: The Agent produces a single `PanelOutput` (Domain Model) which the Engine then *fans out* to individual state keys (`step_logician`, `step_falsifier`).
    *   **Strict DTOs**: The LLM produces a `PanelOutputDTO` (Content Only). The Python Backend injects Authority (`metadata`, `timestamps`) to create the final Domain Object.

### Step 3: Retrieval & Grounding (Hybrid Strategy)
*   **Action**: `RetrievalAgent` fetches context.
*   **Software**: `backend/agents/retrieval.py` + `KnowledgeBaseService`.
*   **Lazy Inflation**: The Agent implementation safely handles legislative legacy data (dicts) while enforcing strict `KnowledgeItem` models for new executions.

### Step 4: Aggregation & Scoring (Safety Clamp)
*   **Action**: Consolidating multiple inputs into a final score (`backend/hooks/scoring.py`).
*   **Logic**: Aggregates scores from all judges and applies deterministic penalties.
*   **Safety Clamp**: Ensures `new_score = max(calculated_score, scale_min)`. This prevents scores from dropping below the schema minimum (e.g., 0.1), avoiding Pydantic validation crashes.
*   **Result**: `ScoringResult` (Total Score, Average, Penalties).

---

## 3. Phase II: The Bridge (Logic to Presentation)

### Software: `ReportingHook` (`backend/hooks/reporting.py`)

The `generate_report` hook acts as the **Director**.

1.  **Data Gathering**: Reads from `context_variables` (strictly typed).
2.  **Context Construction**: Instantiates the **`ReportContext`** Pydantic model.
    *   *New (V3.2)*: Extracts `knowledge_items` (List[KnowledgeItem]) from `step_retrieval` and passes them strictly to the report context.
3.  **Strict Validation**: The `ReportContext` constructor performs strict type checking. If any required field (e.g., `average_score`, `scores`, `knowledge_items`) is missing or invalid, the process **Fails Fast** (AppException).
4.  **Normalization**: Converts various data shapes into a unified structure.

---

## 4. Phase III: Rendering (The "Artist")

### The Golden Rule: JSON First (Single Source of Truth)
**Mandate**: The system MUST generate a complete, validated `ReportContext` (JSON/Pydantic) **BEFORE** any rendering takes place.

1.  **Creation**: The `ReportingHook` first aggregates all data into a `ReportContext` object.
2.  **Validation**: This object is strictly validated by Pydantic (fail fast if data is missing).
3.  **Persistence**: This JSON object is saved in `ReportResult.data` in the workflow state.
4.  **Rendering**:
    *   **PDF**: Jinja2 uses this EXACT JSON object to render Markdown/PDF.
    *   **Screen**: The Frontend uses this EXACT JSON object (`ReportResult.data`) to render the UI.

This guarantees that the PDF and the Dashboard **ALWAYS** show identical numbers, texts, and references.

> [!IMPORTANT]
> **Design Decision: Why we Persist Domain (ReportContext) and NOT View (ReportView)**
> We strictly persist the **Domain Model** (`ReportContext`) in the database, never the **View Model**.
> *   **Decoupling**: The UI changes frequently (widgets, colors, layout). The Data changes rarely. If we stored `ReportView`, every UI redesign would require a database migration or re-execution of historical records.
> *   **Multi-Channel**: The PDF engine needs raw data (fidelity), while the Mobile App needs simplified data (views). Storing the raw Domain Model allows us to derive multiple different views on-the-fly without data loss.
> *   **Historical Integrity**: `ReportContext` is the forensic record of *what the AI thought*. `ReportView` is just *how we chose to show it today*.

### Target A: PDF / Markdown Report
*   **Source**: `ReportContext` (The JSON).
*   **Engine**: **Jinja2**.
*   **Process**: `ReportingHook` -> `ReportContext` -> `Jinja2` -> Markdown -> PDF.
*   **Bibliography**: The `ReportContext.bibliography` field is the authoritative list. The Template iterates this list; it does NOT generate references itself.

### Target B: The Screen (Flutter UI / BFF)
*   **Pattern**: **BFF (Backend-for-Frontend)** via **Transformers**.
*   **Software**: `backend/api/transformers/`.
*   **Role**: Converts Domain Models (Python Pydantic) into UI ViewModels (JSON for Flutter).
*   **Example**: `AssessmentTransformer` converts `ContextData` into a `StepContext` view model.

#### Transformer Example (Retrieval)
When the Frontend polls `/monitor`, the `RetrievalTransformer` does this:
1.  Receives `ContextData` (Pydantic Domain Model) from the workflow state.
2.  Maps `knowledge_items` (List[KnowledgeItem]) to `KnowledgeCardViewModel` (Pydantic View Model).
    ```python
    # STRICT: Input must be a Pydantic Model (ExecutionRecord or ReportContext)
    def transform(self, execution: ExecutionRecord) -> ReportView:
        # 1. Extract Domain Data
        domain_data = execution.results # WorkflowState
        
        # 2. Transform to View Components (strictly typed UiSection)
        sections = []
        
        # ... logic ...

        # 3. Return View Model
        return ReportView(
            view_id=execution.id,
            sections=sections,
            # ...
        )
    ```
3.  The Frontend receives this strictly typed JSON structure.

### 4. Phase III: Rendering (BFF & P2P Pattern)
**Goal:** Transform the raw Domain Model into a strictly typed View Model for the Frontend.

The system uses a **Pydantic-to-Pydantic (P2P)** transformation pattern. We do **NOT** pass raw dictionaries or JSON objects to the Frontend.

#### The P2P Flow
1.  **Source (Domain)**: `ReportContext` (The validated "What Happened" data).
2.  **Transformation**: `ReportTransformer` (Backend Logic).
3.  **Destination (View)**: `ReportView` (The "How to Show It" UI contract).

#### Why P2P? (Zero-Magic)
-   **Build-Time Safety**: Renaming a field in the Domain Model immediately breaks the Transformer code, alerting developers at compile/lint time rather than causing runtime crashes.
-   **Valet Key Pattern**: `ReportView` exposes only what the UI needs, preventing accidental leakage of sensitive backend state.
-   **Autocomplete**: Developers get full IDE support (`.total_score`) instead of guessing magic strings (`['total_score']`).


### Implementation Strategy: Fail Fast & Strict Typing
To ensure zero-hallucination and architectural integrity, the pipeline adheres to the following strict implementation rules (Phase 8):

1.  **Removal of Graceful Fallbacks**:
    *   **Old Way**: If a field was missing, the system would silently skip it or use a default.
    *   **New Way (Fail Fast)**: Missing data raises `AppException` immediately. A broken report is better than a misleading one. Data corruption must be fixed at the source (Seeding/GraphEngine), not hidden in the view layer.

2.  **Domain-to-View Transformation**:
    *   Transformers (`backend/api/transformers/`) accept *only* **Domain Models** (`ExecutionRecord`). Passing raw `dicts` is prohibited.
    *   Transformers return *strictly typed* **View Models** (`UiSection`).
    *   **LogicDomainTransformer**, **CausalDomainTransformer**, etc., are "Mixins" that enforce specific schema requirements for their respective sections.

3.  **Template Fidelity**:
    *   The Jinja2 template (`report_template.jinja2`) operates *exclusively* on the `ReportView` object structure.
    *   No logic (loops, filters, checks) is allowed in the template that isn't directly supporting the View Model. "Smart Templates" are forbidden; logic belongs in the Transformer.

## 5. Summary Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant DB as Database
    participant E as GraphEngine
    participant S as KBService
    participant A as PanelAgent
    participant R as ReportingHook
    participant UI as Flutter

    U->>E: Submit Input
    E->>E: Metrics Hook (TextMetrics)
    
    rect rgb(240, 248, 255)
    note right of E: Strict Typing Zone
    E->>A: Execute PanelAgent (Fused)
    A->>E: Returns PanelOutput (Domain)
    E->>E: Fan-Out -> Step States
    end
    
    E->>R: Execute ReportingHook
    R->>R: Create ReportContext (Fail Fast)
    R->>DB: Persist ReportResult
    
    loop Polling (BFF)
        UI->>E: GET /monitor
        E->>E: Transformer(ReportResult) -> ViewModel
        E->>UI: JSON (ViewModel)
        UI->>UI: Render Widgets
    end
```
