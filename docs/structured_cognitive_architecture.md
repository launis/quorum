# Cognitive Quorum: Structured Cognitive Architecture (V5.1 - Phase 9 Hardening)

## Abstract

**Cognitive Quorum V2 (Enterprise Standard)** is a data-driven cognitive architecture designed to produce deterministic, high-fidelity reasoning from stochastic LLMs. It shifts the **Cognitive Strategy** (JSON-defined logic, UI rendering rules, and evaluation matrices) entirely into the database (Zero-Deploy philosophy), while the **Execution Spine** (Python) remains a "dumb" deterministic orchestrator.

The V2 iteration enforces a **Unidirectional Data Flow** where the "DNA" of the system (Evaluation Matrices, Prompts, System Config, and SDUI Hints) is immutable code, seeded into the database to drive execution.

---

## 1. The Core Architecture

### A. The "Spine" (Execution Layer)
* **Role**: Orchestration, State Management, and Type Enforcement.
* **Implementation**: `backend/core/engine.py`, `backend/models/state.py`.
* **Key Feature (Strict Object Mode)**: Data is passed between agents as strictly typed Pydantic V2 models (`EvaluationResult`, `XAIReport`), never as loose dictionaries.

### B. The "Mind" (Cognitive Layer)
* **Role**: Reasoning Strategy and Criteria.
* **Implementation**: `seed_data.json` -> Database -> Configuration Service.
* **The Role of the Database**: The database acts as the single source of truth (SSOT) for the system's cognitive configuration. Hardcoded Python logic is strictly avoided for cognitive parameters; instead, the Engine reads these values from the database at the start of each execution. This allows Administrators to tune the system's behavior (e.g., scoring strictness, penalized phrases) via the UI without requiring code deployments.
* **Components in DB**:
  * **System Config**: Defines Global Evaluation Penalties (e.g., `scoring_security_penalty`, `scoring_passivity_multiplier`) and Agent Strategies (e.g., `PanelAgent` -> `deep`).
  * **Matrices (BARS & Calibration)**: Behaviorally Anchored Rating Scales ("What is a score of 4 vs 1?"), defining the exact criteria the JudgeAgent must use. Now includes a mathematical **Strictness Level (0-100)** to dynamically calibrate AI attitude, and **Theory-Grounded URLs** to fetch external frameworks.
  * **Prompts**: Directives ("You are a ruthless prosecutor."), injected dynamically during prompt building.

### C. Strict DTO Pattern (The "Air Gap")
To prevent LLM hallucinations of system metadata (timestamps, IDs) and guarantee relational integrity, we use a strict DTO Pattern combined with Prefixed NewTypes:
1. **LLM Output**: The model generates a lean **PROPOSAL** (DTO), e.g., `PanelOutputDTO`. It contains *only* content (analysis, scores).
2. **Python Authority**: The Agent's Python code acts as the **AUTHORITY**. It receives the DTO, validates it, and injects system metadata (Run ID, Timestamp, Model Name) via `_apply_python_authority()`.
3. **Domain Promotion**: The enriched object is promoted to a full **Domain Model** (e.g., `PanelOutput`) before entering the `WorkflowState`.

---

## 2. Workflow Data Architecture (Courtroom 3.0)

The primary production workflow, **Courtroom 3.0 (Fused)**, utilizes a **Fused Panel** pattern to reduce latency and improve coherence. Instead of running specialized critics sequentially, a single deep LLM call assumes multiple personas simultaneously.

### High-Level Data Flow

```mermaid
graph TD
    %% Nodes
    UserInput[User Input Files & JSON]
    InputProcessor[Step 0: Input Processor]
    Guard[Step 1: Guard Agent (Safety)]
    Context[Step 1b: Context Retrieval]
    Analyst[Step 2: Analyst Agent]
    Interaction[Step 3: Interaction Agent]
    
    %% Fused Logic
    subgraph "Phase 2: The Panel (Courtroom 3.0)"
        Panel[Step 4: Panel Agent]
        note1[Wrapper: PanelOutputDTO]
        
        Logic[Logician Logic]
        False[Falsifier Logic]
        Causal[Causal Logic]
        Perform[Performativity Logic]
        Over[Overseer Logic]
        
        Panel --> note1
        note1 -.-> Logic
        note1 -.-> False
        note1 -.-> Causal
        note1 -.-> Perform
        note1 -.-> Over
    end
    
    %% Fan Out
    FanOut((Engine Fan-Out))
    note1 --> FanOut
    FanOut -->|step_logician| StateLogician[Logician State]
    FanOut -->|step_falsifier| StateFalsifier[Falsifier State]
    FanOut -->|step_causal| StateCausal[Causal State]
    FanOut -->|step_detector| StateDetector[Performativity State]
    FanOut -->|step_overseer| StateOverseer[Overseer State]
    
    JudgeStandard["Step 5: Judge (Standard Matrix)"]
    Coach[Step 6: Coach Agent]
    XAI[Step 7: XAI Reporter]
    
    %% Flows
    UserInput -->|Raw File JSON / Base64| InputProcessor
    InputProcessor -->|Processed Text| Guard
    Guard -->|SafeData| Context
    Context -.->|Sidebar Context| Panel
    Context -.->|Sidebar Context| JudgeStandard
    
    Guard -->|SafeData| Analyst
    Guard -->|SafeData| Interaction
    
    Analyst -->|TodistusKartta| Panel
    Interaction --> Panel
    
    StateLogician --> JudgeStandard
    StateFalsifier --> JudgeStandard
    StateCausal --> JudgeStandard
    StateDetector --> JudgeStandard
    StateOverseer --> JudgeStandard
    
    JudgeStandard -->|Verdict| Coach
    Coach -->|CoachingPlan| XAI
```

### Step-by-Step Data Contracts
All steps operate on the Hybrid State Architecture, reading inputs from the Blackboard (`WorkflowState.context_variables`) and writing outputs to the Event Log (`TraceEvent`) and projecting back to the Blackboard.

0. **Step 0: Input Processor (`step_input_processor`)**: Translates Raw `Base64FileDTO` payloads asynchronously into normalized strings (e.g., `history_text`). Outputs `InputProcessorOutput`.
1. **Step 1: Guard (`step_guard`)**: Input hygiene and PII redaction. Outputs `TaintedData` containing `safe_data` (Critical). Halts execution if `banned_phrases` detected.
2. **Step 1b: Context Retrieval (`step_context`)**: Fetches external knowledge (RAG). Outputs `RetrievalOutput`.
3. **Step 2: Analyst (`step_analyst`)**: Establishes ground truth. Outputs `AnalystOutput` with `provenance_map`.
4. **Step 3: Panel (`step_panel`)**: Parallel execution of specialized critics (Logician, Falsifier, Causal, Performativity, Overseer) wrapped in `PanelOutputDTO`. The Engine performs a **Fan-Out**, splitting this object into individual state keys (e.g., `step_logician`) to simulate independent agents.
5. **Step 4: Judge (`step_judge`)**: Authoritative scoring using a Matrix. The matrix injects dynamic strictness parameters and forces Theory-Grounded multilingual justifications. Outputs `EvaluationResult`.
6. **Step 5: XAI Reporter (`step_xai`)**: Synthesizes final output into `XAIFlatReportDTO` (for external BI) and `SemanticReport`. Output strictly follows **Late-Binding Omni-Channel** logic, resolving into interactive Riverpod SDUI (with Compound Widgets for UI hints), static Backend Jinja2 PDF, and Flat File / CSV exports without changing the underlying JSON logic.

---

## 3. Dynamic Prompt Engineering (Polymorphic Injection)

Prompt engineering is an architectural discipline in V5.1. The `PromptBuilder` (`backend/services/prompt_builder.py`) dynamically assembles prompts from database components, schemas, and runtime state.

### The "Sandwich" Composition Model
1. **Directives Layer**: System Mandates (e.g., "Mandaatti 1: Hidas ajattelu") and Agent Identity, fetched directly from the database's component library via slug names mapping to specific DB records.
2. **Context Layer**: Injected State (`{{HISTORY_TEXT}}`), Upstream Evidence (`{{PREVIOUS_STEP_OUTPUTS}}`), and External Data (`{{GOOGLE_SEARCH_RESULTS}}`).
3. **Cognitive Layer**: Evaluation Matrices retrieved from the DB, transformed by `MatrixFormatter` into formatted Markdown rubrics, plus task instructions.
4. **Output Layer**: Strict JSON Schema (`{{SCHEMA_EXAMPLE}}`) automatically generated from the agent's DTO models.

### Strict Type-Driven Prompting
To ensure zero hallucinations, Content is separated from Authority. The PromptBuilder injects the JSON Schema of the **DTO** (e.g., `PanelOutputDTO`), not the full Domain Object. The LLM is explicitly instructed *not* to invent timestamps or versions. Validation is handled by the `GraphEngine` downstream against this DTO.

---

## 4. Information Retrieval & 3-Tier Grounding Architecture

Information retrieval is explicitly segregated to prevent context collapse:

1. **PROACTIVE - Analyst Hypothesis Search (`backend/hooks/search.py`)**: *Generative Evidence Gathering*. An independent pre-hook searches the web to expand the Analyst's awareness *before* claims are formulated.
2. **REAL-TIME - Dynamic Vertex Grounding (`backend/llm/provider.py`)**: *In-line Fact-Checking*. Used for models supporting grounding. Cross-references generated tokens with Google Search in real-time, injecting citation URLs directly into metadata.
3. **POST-HOC - Internal Knowledge Base (`backend/hooks/references.py`)**: *Compliance Checking*. Executes asynchronously at the end of the workflow (`generate_bibliography_hook`). Aggregates generated text and cross-references against local domain policies (e.g., Brand Book). Since it runs exclusively in Python after all heavy LLM steps, it causes zero generation latency.

---

## 5. Data Integrity & Hazard Mitigation

The architecture resolves several common LLM orchestration hazards.

### Hazard 1: Database-to-Agent Schema Drift
**Solution: Static Resolution & Inflation (`_resolve_inputs`)**
Every step in `seed_data.json` defines an `inputs` mapping (a routing map).
1. **Introspection**: The Engine retrieves the Pydantic Input Schema (e.g., `JudgeInput`) and determines the required types (e.g., `AnalystOutput`).
2. **Hydration & Fail-Fast**: It fetches raw JSON from the Blackboard and attempts to inflate it into the expected model. If a key is missing or a type mismatches, the engine immediately crashes (`AGENT_SCHEMA_VALIDATION_FAILED`). 
3. **CI/CD Prevention**: A static audit test (`test_seed_schema_alignment.py`) verifies set-math alignment (`provided_keys - schema_keys`) to ensure JSON configs and Python definitions never drift.

### Hazard 2: "Level Skipping" (JSON Flattening)
**The Hazard**: When working with nested Pydantic models, LLMs often flatten the JSON, skipping the "wrapper" branch node and placing leaf nodes at the root.

**Architectural Solutions**:
1. **DTO Simplification**: Requesting flatter Data Transfer Objects (`AnalystOutputDTO`) instead of heavily nested Domain Models.
2. **Panel Fan-Out**: Accepting that flattening is best handled deterministically. The `PanelAgent` produces a massive object, and the Engine safely explicitly "Fans Out" the properties across the blackboard.
3. **Residual Mitigation (Post-Process Healing)**: We apply Postel's Law. The `post_process` method in Python acts as a Structure Healer. It scans for "Signature Keys". If they exist at the root, the Python wrapper deterministically rebuilds the expected nested wrapper. 
   * *Warning (Implicit Coupling)*: Healing logic contains hardcoded string literals. Modifying a field name in a Domain Model might silently break the healer. DTO isolation limits this risk.