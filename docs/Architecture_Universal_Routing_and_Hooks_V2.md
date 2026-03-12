# System Architecture Specification: Universal Routing & Hooks (V2)
**Date:** March 2026
**Status:** Deployed (Stable)
**Scope:** Core Backend Execution Pipeline (`backend_v2/hooks/` and `seed_data.json` DAGs)

---

## 1. Executive Summary

This document serves as the definitive scientific and technical specification for the "Heart" of the Quorum V2 Architecture: The Universal Routing pipeline, the deterministic Hook Ecosystem, and the Structured Cognitive Architecture.

The primary objective of the V2 migration was to systematically eliminate the volatility and inherent hallucination risks of V1, which relied heavily on heuristic LLM instructions ("Ghost Matrices" and narrative descriptions) and opaque logic processing. 

V2 fundamentally reconstructs the pipeline around two core principles:
1.  **Strict Pydantic Enforcement (Fail-Fast):** All data state validation, filtering, math, and constraint verification have been forcefully migrated out of the LLM context into deterministic Python CPU logic. If data does not strictly match the expected semantic structure, the system terminates execution via an RFC 7807 error.
2.  **Universal Data Routing (DAG):** Information flows exclusively across explicit paths mapped in the system configuration database (`depends_on` and `input_mappings`), ensuring downstream nodes receive unbroken, raw intelligence from upstream expert systems.

---

## 2. The Core Architecture: Spine vs. Mind

V2 strictly enforces a **Unidirectional Data Flow** where the "DNA" of the system is isolated from the executing machinery.

### A. The "Spine" (Execution Layer)
* **Role**: Orchestration, State Management, and Type Enforcement.
* **Feature (Strict Object Mode)**: Data is passed between agents as strictly typed Pydantic V2 models, never as loose dictionaries. The GraphEngine (Python) provides deterministic execution but contains zero "hardcoded" intelligence.

### B. The "Mind" (Cognitive Layer)
* **Role**: Reasoning Strategy and Criteria.
* **Location**: The database acts as the single source of truth (SSOT). The Engine reads these values to construct prompts, allowing Administrators to tune the system without code deployments.
* **Components in DB**:
  * **System Config**: Defines Global Evaluation Penalties and Model Strategies (e.g., `fast`, `deep`).
  * **Polymorphic PromptBlocks**: Fuses directives and evaluation matrices. Includes mathematical **Strictness Levels (0-100)** to dynamically calibrate AI attitude, and **Theory-Grounded URLs** to fetch external frameworks.

### C. Strict DTO Pattern (The "Air Gap")
To prevent LLM hallucinations of system metadata (timestamps, IDs) and guarantee relational integrity:
1. **LLM Output**: The model generates a lean **PROPOSAL** (DTO) comprising only raw data (e.g., scoring arrays).
2. **Python Authority**: The Agent's Python code acts as the **AUTHORITY**, catching the DTO, validating boundaries, and injecting system metadata (Run ID, Timestamp).
3. **Domain Promotion**: The enriched object is promoted to a full Domain Model before persisting to the database.

---

## 3. Universal Data Routing & Courtroom 3.0

The execution engine in V2 interprets a dynamic Directed Acyclic Graph (DAG), resolving variables (`$inputs`, `$step_node_X.output`) at runtime. The premier example of this architecture in production is the `workflow_courtroom_20_full_audit` pipeline.

### 3.1 The Eradication of "Ghost Matrices"
All legacy plain-text "Role Matrices" were programmatically destroyed to eliminate token bloat and LLM confusion. Agents now rely exclusively on concise PromptBlocks paired with a strict `{{SCHEMA_EXAMPLE}}` JSON blueprint injection.

### 3.2 Dynamic Input Ingestion
Raw inputs (PDFs, chat logs) are intercepted by the orchestration engine. Instead of hardcoding instructions for specific filenames into prompts, the system uses **Universal Routing**: a pre-hook injects an `ai_description` header dynamically determined by the workflow configuration directly into the document string. Any generalized AI agent can thus process any input natively without workflow-specific prompt hacks.

### 3.3 The Fan-Out & Upstream Experts
The initial tier of execution processes the context:
-   **Step 1-3 (Ingestion):** Process raw text strings, authenticate security perimeters, and retrieve external domain contexts.
-   **Step 4-12 (The Fused Analysts):** Independent experts execute highly specialized cognitive functions. 
    *   `step_analyst` processes Vertex Search data into rigorous, sequenced hypotheses (`HYP-N`).
    *   `step_profiler` evaluates cognitive biases.
    *   `step_logician` builds Toulmin Argument schemas out of the primary input text.
    *   `step_falsifier` attempts to actively destroy the analyst's hypotheses by locating Popperian failures.
    *   `step_causal_analyst` constructs counterfactuals.

### 3.4 The Grand Unifier (The Judge) & Late Reporting
At node 13 (`step_judge`), the architecture reaches its first convergence point. The `JudgeInput` Pydantic model absorbs this 360-degree data panorama and derives a unified categorical scoring matrix.

Nodes 14 (`step_coach`) and 15 (`step_xai_reporter`) act as the final rendering systems. *Note: While the theoretical cognitive framework describes 15 logical maturity steps, the V2 DAG engine physically executes this across 13 optimized nodes (`step_node_1` to `step_node_13`). The references to nodes 13-15 reflect the conceptual architecture.* By explicitly routing the Upstream Experts directly into to the downstream output generators (`$steps.step_analyst.output`), V2 ensures PDF reports and SDUI dashboards contain exact structured fallacies and raw search quotes uncovered deep inside the DAG runtime.

---

## 4. Dynamic Prompt Engineering (Polymorphic Injection)

Prompt engineering is an architectural discipline in V2. The `PromptBuilder` dynamically assembles prompts from database components, schemas, and runtime state.

### The "Sandwich" Composition Model
1. **Directives Layer**: System Mandates and Agent Identity, fetched directly from the database's component library.
2. **Context Layer**: Injected State (`{{HISTORY_TEXT}}`), Upstream Evidence (`{{PREVIOUS_STEP_OUTPUTS}}`), and External Data (`{{GOOGLE_SEARCH_RESULTS}}`).
3. **Cognitive Layer**: Evaluation Matrices retrieved from the DB, transformed into formatted Markdown rubrics, combined with strictness vectors.
4. **Output Layer**: Strict JSON Schema (`{{SCHEMA_EXAMPLE}}`) automatically generated from the agent's Pydantic DTO models.

---

## 5. The Hook Ecosystem: CPU-Bound Determinism

To minimize expensive LLM token ingestion and enforce absolute mathematical and security certainty, the V2 framework executes modular Python routines (`Hooks`) across the workflow Lifecycle. All hooks exist within `backend_v2/hooks/` and strictly adhere to the `AppException` Fail-Fast standard.

### 5.1 Front-Door Validation and Security
Before any AI model is activated, the context data undergoes vicious mathematical processing:
-   **`check_banned_phrases`**: Dynamically queries the NoSQL DB for "Banned Phrases". If a hit occurs, throws a `SecurityViolationError` HTTP 400.
-   **`sanitize_text`**: Standard regex-based PII redaction layer. 
-   **`verify_structure`**: Character array counting. Rejects payloads under 100 characters.
-   **`input_processing`**: Normalizes modalities. Converts Base64 PDFs using `PyMuPDF`. Parses legacy questionnaires. Injects universal `ai_description` headers. Can trigger the V2 `ChatParserService`.

### 5.2 Heuristics and Quantitative Measurement
In V1, LLMs were instructed to "calculate" bias or word lengths. This is moved to CPU math.
-   **`metrics`**: Employs classical NLP math to parse `inputs` for Total Word Counts, Average Sentence Lengths, and calculates the absolute mathematical "Input Control Ratio" between Human and AI strings.
-   **`linguistics`**: Executes raw string matching arrays against user input (e.g. locating "synergy"), cataloging performative buzzwords.

### 5.3 Governance: Zero-Hallucination & Penalty Execution
The crown jewel of the V2 mechanism protects the output from LLM distortion:
-   **`verify_citation_integrity`**: The ultimate anti-hallucination safeguard. Forces the Analyst and Falsifier to supply exact `quotes`. The hook scans originating inputs; if quoted text does not exist precisely in the raw data, the internal `integrity_score` drops. If this score falls beneath the system threshold, the API crashes via `AppException`. Enforces sequential IDs (`HYP-1`) on hypotheses.
-   **`score_penalties`**: Evaluates boolean flags generated across the expert pipeline (e.g. `post_hoc_rationalization` applied by the Falsifier) and multiplies the Judge's ultimate grade by administrative penalty scalars entirely outside the LLM purview.

---

## 6. Information Retrieval & 3-Tier Grounding Architecture

Information retrieval is explicitly segregated to prevent context collapse:

1. **PROACTIVE - Analyst Hypothesis Search (`search.py` Hook)**: *Generative Evidence Gathering*. An independent pre-hook intercepts Analyst hypotheses, extracting strings > 3 chars, and searches the web via a dedicated Vertex AI LLM (handling 429 Quotas via Backoff). Snippets are typed into `search_result` Pydantic models.
2. **REAL-TIME - Dynamic Vertex Grounding (`provider.py`)**: *In-line Fact-Checking*. Placed directly inside the final LLM provider call (`tools=[{"googleSearch": {}}]`) for deep models. Cross-references generated tokens with Google Search in real-time, pulling `grounding_metadata`.
3. **POST-HOC - Internal Knowledge Base (`references.py` Hook)**: *Compliance Checking*. Executes asynchronously at the end of the workflow to aggregate generated text and cross-reference against local organizational policies (e.g., Brand Book).

---

## 7. Data Integrity & Hazard Mitigation

The architecture revolves around eliminating data drift.

### Hazard: Database-to-Agent Schema Drift
**Solution: Static Resolution & Hydration**
Every step defines an `inputs` mapping (routing map). The Engine retrieves the Pydantic Input Schema and inflates raw JSON into it. If a key is missing or a type mismatches, the engine immediately crashes (`AGENT_SCHEMA_VALIDATION_FAILED`). A static audit block verifies set-math alignment (`provided_keys - schema_keys`) to ensure JSON configs and Python definitions never drift.

### Hazard: "Level Skipping" (JSON Flattening)
**Solution: DTO Simplification and Post-Process Healing**
LLMs often flatten heavily nested JSON. In V2, we request much flatter Data Transfer Objects (`AnalystOutputDTO`). Additionally, the `post_process` method acts as a string-matching Structure Healer to deterministically rebuild nested structures if the LLM attempted to dump them to the root scope.

---

## 8. Conclusion

The Quorum V2 Architecture constitutes a massive paradigm leap from "Instructed" GenAI to "Deterministic, Schema-Driven, DAG-Routed" Software Engineering.

By forcing the extraction of all counting, validation, API querying, scoring penalties, and document generation responsibilities into the pure Python Hook ecosystem, and linking the expert reasoning models through the Universal Router map directly to the final coaching outputs, the system guarantees 100% computational integrity while maximizing the LLMs' actual intended utility: qualitative semantic analysis.
