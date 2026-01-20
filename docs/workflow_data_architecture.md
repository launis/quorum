# Workflow Data Architecture: Courtroom 3.0 (Fused Dual)

**Workflow ID:** `fused_audit_chain_dual`  
**Description:** This document details the data lineage, input/output contracts, and information flow within the system's primary audit chain. It serves as the architectural source of truth for how agents communicate.

---

## 1. High-Level Data Flow (Mermaid)

The following diagram illustrates how data transforms from raw user input into a finalized XAI report.

```mermaid
graph TD
    %% Nodes
    UserInput[User Input Files]
    Guard[Step 1: Guard Agent]
    Analyst[Step 2: Analyst Agent]
    Interaction[Step 3: Interaction Agent]
    Profiler[Step 4: Profiler Agent]
    
    subgraph "Parallel Critics (Panel)"
        Panel[Step 5: Panel Agent]
    end
    
    Archivist[Step 6: Archivist Agent]
    JudgeStandard[Step 7: Judge (Standard Matrix)]
    JudgeCognitive[Step 8: Judge (Cognitive Matrix)]
    Coach[Step 9: Coach Agent]
    Context[Step 10: RAG Context]
    XAI[Step 11: XAI Reporter]
    
    %% Flows
    UserInput -->|Raw Strings| Guard
    Guard -->|SafeData (Sanitized)| Analyst
    Guard -->|SafeData| Interaction
    Guard -->|SafeData| Profiler
    Guard -->|SafeData| Archivist
    
    Analyst -->|TodistusKartta (Grounding)| Panel
    Analyst -->|TodistusKartta| JudgeStandard
    Analyst -->|TodistusKartta| JudgeCognitive
    
    Interaction -->|DriverMetrics| JudgeStandard
    Profiler -->|CognitiveProfile| JudgeStandard
    
    Panel -->|PanelAudit (Consolidated Logic/Falsification/Facts)| JudgeStandard
    Panel -->|PanelAudit| JudgeCognitive
    
    Archivist -->|Precedents| JudgeStandard
    
    JudgeStandard -->|Verdict (Standard)| Coach
    JudgeStandard -->|Verdict (Standard)| XAI
    JudgeCognitive -->|Verdict (Cognitive)| XAI
    
    Coach -->|CoachingPlan| XAI
    Context -->|RelatedCases| XAI
    
    XAI -->|Final JSON| Dashboard[Frontend UI]
```

---

## 2. Step-by-Step Data Contracts

### Step 1: Guard (`step_guard`)
**Objective:** Input hygiene, PII redaction, and security scanning.
- **Input:** Raw strings (`history_text`, `product_text`, `reflection_text`).
- **Process:** Regex scanning, PII detection logic.
- **Output:** `TaintedData` schema.
    - `security_check`: Risk level assessment.
    - `safe_data`: **CRITICAL.** This object contains the sanitized text versions used by ALL subsequent agents. If this is missing/empty, the chain should halt.

### Step 2: Analyst (`step_analyst`)
**Objective:** Establish the "Ground Truth".
- **Input:** `safe_data` (from Guard).
- **Process:** Extraction of claims and mapping them to evidence.
- **Output:** `TodistusKartta` schema.
    - `hypoteesit`: List of claims made by the user.
    - `rag_todisteet`: Direct quotes from the input supporting/refuting claims. **This is the binding contract for the Judge.** If a claim isn't here, it doesn't exist.

### Step 5: Panel (`step_panel`) - *Fused Execution*
**Objective:** Parallel execution of specialized critics to form a holistic view.
- **Input:** `TodistusKartta` (proven claims), `safe_data`.
- **Process:** Runs `Logician`, `Falsifier`, `Causal`, `Performativity`, and `Overseer` prompts in parallel (or sequential internal blocks).
- **Output:** `PanelAudit` schema (Consolidated).
    - `logiikka_auditointi`: Toulmin analysis of arguments.
    - `falsifiointi_auditointi`: Results of stress tests on claims.
    - `etiikka_ja_fakta`: Hallucination checks (comparison against Google Search results if enabled).

### Step 7 & 8: Judge (`step_judge` / `step_judge_cognitive`)
**Objective:** Authoritative scoring based on the Matrix.
- **Input:**
    - `TodistusKartta` (The Truth)
    - `PanelAudit` ( The Critiques)
    - `InteractionAnalysis` (User agency)
- **Process:**
    1.  Resolves conflicts (e.g., if Falsifier says "False" but Analyst says "True").
    2.  Applies the **Matrix Scale** (fetched from DB).
    3.  Calculates the final score.
- **Output:** `TuomioJaPisteet` schema.
    - `total_score`: Final numeric grade.
    - `dimensions`: Breakdown per matrix dimension (e.g., "Agency", "Synthesis").
    - `matrix_id`: Traceability to the exact criteria used.

### Step 9: Coach (`step_coach`)
**Objective:** Constructive remediation.
- **Input:** `TuomioJaPisteet` (Verdict).
- **Process:** Maps score gaps to actionable advice.
- **Output:** `CoachingPlan` schema.
    - `toimenpiteet`: Concrete list of "Do this next".
    - `motivaatio`: Psychological/Pedagogical reasoning.

### Step 11: XAI Reporter (`step_xai`)
**Objective:** Final user-facing artifact.
- **Input:** All previous outputs.
- **Process:** Synthesizes technical logs into a readable narrative.
- **Output:** `XAIReport` schema.
    - `executive_summary`: High-level "what happened".
    - `score_cards`: Visualizable data for the UI Radar Charts.
    - `xai_report_formatted`: Full Markdown report.

---

## 3. Strict Enforcements & Invariants

1.  **Truth Propagation:** The `Judge` acts as the final arbiter. It MUST NOT hallucinate scores. It acts strictly on the evidence provided in `TodistusKartta` and `PanelAudit`.
2.  **Scale Fidelity:** The `Judge` retrieves its scale (`min`/`max`) from the database at runtime. Hardcoded scales are strictly forbidden.
3.  **Sanitization:** No agent other than `Guard` accesses the raw, potentially PII-laden input. All others operate on `safe_data`.
4.  **Schema Compliance:** All outputs effectively guarantee adherence to the Pydantic models defined in `backend/models/domain.py`. Failure to validate results in a step failure.
