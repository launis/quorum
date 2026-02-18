# API Models & Data Schemas (V2.9)

This document details the strict **Pydantic V2** data models used throughout the Cognitive Quorum system. All data exchange is strictly typed to ensure hallucination-free execution and proper integration with the "Zero-Magic" verification strategy.

---

## 🟢 Core State (`backend.models.state`)

### `WorkflowState` (Event Sourcing)
The system uses an **Event Sourcing** pattern. The state is an immutable log of events, not a mutable blackboard.

| Field | Type | Description |
| :--- | :--- | :--- |
| `execution_id` | `UUID` | Unique identifier for this execution instance. |
| `workflow_id` | `str` | ID of the workflow definition. |
| `status` | `Literal` | `pending`, `running`, `completed`, `failed`. |
| `execution_trace` | `list[TraceEvent]` | **Immutable log** of all steps, inputs, reasoning, and outputs. |
| `context_variables` | `dict[str, Any]` | Current snapshots of context variables (the "Folded State"). |

### `TraceEvent`
An atomic unit of history.

| Field | Type | Description |
| :--- | :--- | :--- |
| `event_id` | `UUID` | Unique event ID. |
| `timestamp` | `datetime` | UTC timestamp. |
| `step_name` | `str` | Name of the step that generated this event. |
| `event_type` | `Literal` | `input`, `reasoning`, `decision`, `error`, `output`. |
| `content` | `dict` | Structured content payload (polymorphic). |
| `reasoning` | `ReasoningTrace` | **Hidden Chain-of-Thought** (separate from content). |

### `ReasoningTrace`
Captures the "Thinking Tokens" (e.g., Gemini 1.5 Thinking) that are NOT shown to the user but are crucial for the next agent.

| Field | Type | Description |
| :--- | :--- | :--- |
| `thought_process` | `str` | Raw chain-of-thought. |
| `conclusion` | `str` | Synthesized conclusion. |
| `confidence_score` | `float` | Self-assessed confidence (0.0 - 1.0). |

| `confidence_score` | `float` | Self-assessed confidence (0.0 - 1.0). |

---

## 🔒 Agent Input Schemas (`backend.models.domain`)

Strict input contracts enforced by `BaseAgent`.

| Agent | Input Model | Description |
| :--- | :--- | :--- |
| **Retrieval** | `RetrievalInput` | Query & Org ID. |
| **Interaction** | `InteractionInput` | History Text. |
| **Coach** | `CoachInput` | Judge Verdict (`step_judge`). |
| **XAI** | `XAIReporterInput` | Judge Verdict(s) (`step_judge*`). |
| **Guard** | `GuardInput` | Raw Text (History, Product, Reflection). |
| **Analyst** | `AnalystInput` | Research Claims. |
| **Logician** | `LogicianInput` | Argument Analysis. |
| **Protector** | `OverseerInput` | Fact Checking. |
| **Profiler** | `ProfilerInput` | Text Analysis. |

---


## 🛡️ Agent Schemas (`backend.models.domain`)

### 1. Guard Agent (`GuardOutput`)
Security and PII redaction.

| Field | Type | Description |
| :--- | :--- | :--- |
| `security_check` | `SecurityCheck` | Threat analysis (`RiskLevel`, `SimulationType`). |
| `tainted_data` | `TaintedDataContent` | Original input wrapper. |

### 2. Analyst Agent (`AnalystOutput`)
Grounding & Evidence Extraction.

| Field | Type | Description |
| :--- | :--- | :--- |
| `hypotheses` | `list[Hypothesis]` | Formulated research claims. |
| `rag_evidence` | `list[str]` | Evidence collected via RAG. |

### 3. Retrieval Agent (`ContextData`)
Organizational Knowledge Retrieval (RAG).

| Field | Type | Description |
| :--- | :--- | :--- |
| `precedents` | `str` | Summary text of retrieved precedents. |
| `precedent_list` | `list[Precedent]` | Structured list of past cases. |

### 4. Interaction Agent (`InteractionAnalysis`)
User Agency Analysis.

| Field | Type | Description |
| :--- | :--- | :--- |
| `role_classification` | `Literal` | `Passenger`, `Navigator`, `Driver`, `Architect`. |
| `input_quality_score` | `float` | Quality of user prompting. |
| `improvement_suggestions` | `list[str]` | Tips for the user. |

### 5. Profiler Agent (`ProfilerAnalysis`)
Cognitive Bias & Tone Profiling.

| Field | Type | Description |
| :--- | :--- | :--- |
| `author_intent` | `str` | Assessed intent. |
| `cognitive_biases` | `list[str]` | Detected biases (e.g., "Confirmation Bias"). |
| `emotional_tone` | `str` | Tone analysis. |

### 6. Logician Agent (`LogicianOutput`)
Argumentation Structure Analysis.

| Field | Type | Description |
| :--- | :--- | :--- |
| `logician_data` | `LogicianData` | Container for results. |
| -> `toulmin_analysis` | `list[ToulminComponent]` | Claim, Data, Warrant structure. |
| -> `walton_scheme` | `WaltonScheme` | Identified argumentation scheme. |
| -> `toulmin_score` | `float` | Logic strength score (0-6). |

### 7. Panel Agent (`PanelOutput`)
**Consolidated Audit** (Runs Falsifier, Overseer, Causal, and Detector in parallel/sequence).

| Field | Type | Description |
| :--- | :--- | :--- |
| `falsifier_data` | `FalsifierData` | Stress test findings (`stress_test_findings`). |
| `overseer_data` | `OverseerData` | Fact checks & ethical audit. |
| `causal_analysis` | `CausalAnalysis` | Counterfactuals & abductive reasoning. |
| `performativity_analysis` | `PerformativityAnalysis` | `AuthenticityLevel` assessment. |

### 8. Archivist Agent (`ArchivistOutput`)
Precedent & Compliance Audit.

| Field | Type | Description |
| :--- | :--- | :--- |
| `compliance_score` | `float` | Alignment score (1-5). |
| `compliance_analysis` | `Literal` | e.g., `Aligned`, `Misaligned`. |
| `relevant_cases` | `list[ArchiveCase]` | Similar past cases. |

### 9. Judge Agent (`JudgeOutput`)
**BARS Scoring** & Final Verdict.

| Field | Type | Description |
| :--- | :--- | :--- |
| `score_card` | `JudgeScoreCard` | The final score. |
| -> `total_score` | `float` | Aggregated score. |
| -> `verdict` | `str` | Final decision (Derived from `EvaluationMatrix` Enums). |
| -> `dimensions` | `list[DimensionResultItem]` | Score per dimension (Radar Chart). |

### 10. Coach Agent (`CoachingPlan`)
Pedagogical Feedback.

| Field | Type | Description |
| :--- | :--- | :--- |
| `actionable_steps` | `list[str]` | Concrete improvement steps. |
| `focus_areas` | `list[str]` | Areas needing attention. |
| `bibliography` | `list[dict]` | Recommended reading. |

### 11. Reporter Agent (`XAIOutput`)
Final Report Generation.

| Field | Type | Description |
| :--- | :--- | :--- |
| `executive_summary` | `str` | High-level summary. |
| `final_verdict` | `str` | Conclusive judgment. |
| `confidence_score` | `float` | System confidence. |
| `xai_report_formatted` | `str` | **Markdown** report for the UI. |

---

## 🔄 Dynamic Evaluation Models (`backend.models.workflow`)

### `EvaluationMatrixConfig`
Defines *how* things are scored.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` | Matrix ID (e.g., `matrix_standard_v1`). |
| `criteria` | `list[EvaluationCriterion]` | The rubric dimensions. |

### `WorkflowDefinition`
Defines the graph.

| Field | Type | Description |
| :--- | :--- | :--- |
| `steps` | `list[WorkflowStep]` | Sequence of steps. |
| `scoring_logic` | `list[ScoringLogic]` | How component scores are weighted. |
