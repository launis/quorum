# API Models & Data Schemas (V2.9)

This document details the strict **Pydantic V2** data models used throughout the Cognitive Quorum system. All data exchange is strictly typed to ensure hallucination-free execution and proper integration with the "Zero-Magic" verification strategy.

---

## 🟢 Core State (`backend.models.state`)

### `WorkflowState`
The central "Blackboard" object passed between all agents.

| Field | Type | Description |
| :--- | :--- | :--- |
| `execution_id` | `str` | Unique UUID for this execution instance. |
| `workflow_id` | `str` | ID of the workflow definition. |
| `current_step_name` | `str` | Identifier of the active step. |
| `version` | `int` | Optimistic locking version. |
| `inputs` | `InputData` | Immutable user inputs. |
| `step_results` | `dict[str, Any]` | Dynamic container for agent outputs. |
| `audit_results` | `dict[str, EvaluationResult]` | Container for matrix-based evaluations. |
| `reasoning_context` | `dict` | "Thinking Tokens" (Gemini 1.5/DeepSeek) for continuity. |

### `InputData`
Raw inputs provided by the user.

| Field | Type | Description |
| :--- | :--- | :--- |
| `history_text` | `str` | Historical context (chat logs). |
| `product_text` | `str` | Primary artifact to analyze. |
| `reflection_text` | `str` | User self-reflection. |
| `bibliography_context` | `list[str]` | Optional reference citations. |

> **Note**: `InputData` is "Slot-Based" to prevent arbitrary file injection.

---

## 🛡️ Agent Schemas (`backend.models.domain`)

### 1. Guard Agent (`TaintedData` -> `SafeData`)
Security and PII redaction.

| Field | Type | Description |
| :--- | :--- | :--- |
| `security_check` | `SecurityCheck` | Threat analysis (`uhka_havaittu`, `riski_taso`). |
| `safe_data` | `SafeDataContent` | Sanitized text used by downstream agents. |

### 2. Analyst Agent (`TodistusKartta`)
Evidence extraction.

| Field | Type | Description |
| :--- | :--- | :--- |
| `hypoteesit` | `list[Hypoteesi]` | Formulated research hypotheses. |
| `rag_todisteet` | `list[RagTodiste]` | Evidence collected via RAG. |

### 3. Interaction Analyst (`InteractionAnalysis`)
User agency analysis.

| Field | Type | Description |
| :--- | :--- | :--- |
| `driver_classification` | `Literal` | "Kuski", "Matkustaja", etc. |
| `input_control_ratio` | `float` | Control ratio (Imperative / Total). |
| `imperative_command_count`| `int` | Count of direct commands. |
| `total_turn_count` | `int` | Total user turns analyzed. |

### 4. Profiler Agent (`ProfilerAnalysis`)
Cognitive bias profiling.

| Field | Type | Description |
| :--- | :--- | :--- |
| `tunnistetut_vinoumat` | `list[StructuredBias]` | Detected cognitive biases. |
| `teksti_metriikka` | `TextMetrics` | Word count, sentence length, etc. |

### 5. Logician Agent (`ArgumentaatioAnalyysi`)
Logic mapping.

| Field | Type | Description |
| :--- | :--- | :--- |
| `toulmin_analyysi` | `list[ToulminKomponentti]` | Assertions (Claim, Data, Warrant). |
| `kognitiivinen_taso` | `KognitiivinenTaso` | Bloom's Taxonomy level. |

### 6. Falsifier Agent (`LogiikkaAuditointi`)
Stress testing.

| Field | Type | Description |
| :--- | :--- | :--- |
| `walton_stressitesti_loydokset` | `list[WaltonStressitesti]` | Critical question results. |

### 7. Causal Agent (`KausaalinenAuditointi`)
Causal inference.

| Field | Type | Description |
| :--- | :--- | :--- |
| `kontrafaktuaalinen_testi` | `KontrafaktuaalinenTesti` | "What if" simulation. |
| `abduktiivinen_paatelma` | `Literal` | "Aito Oivallus" vs "Post-Hoc". |

### 8. Performativity Detector (`PerformatiivisuusAuditointi`)
Authenticity check.

| Field | Type | Description |
| :--- | :--- | :--- |
| `performatiivisuus_heuristiikat` | `list[PerformatiivisuusHeuristiikka]` | Heuristics flags. |
| `yleisarvio_aitoudesta` | `Literal` | "Orgaaninen" vs "Performatiivinen". |

### 9. Archivist Agent (`ArchivistOutput`)
Precedent compliance.

| Field | Type | Description |
| :--- | :--- | :--- |
| `compliance_score` | `int` | Alignment score (0-100). |
| `recommendations` | `list[str]` | Improvement suggestions. |

### 10. Coach Agent (`CoachingPlan`)
Pedagogical feedback.

| Field | Type | Description |
| :--- | :--- | :--- |
| `kehityskohteet_konkreettisesti` | `list[ActionGroup]` | Actionable steps. |
| `kannustava_palaute` | `str` | Positive reinforcement. |

---

## 🧠 Dynamic Evaluation (`EvaluationResult`)
Used by the **Judge Agent**.

| Field | Type | Description |
| :--- | :--- | :--- |
| `matrix_id` | `str` | ID of the matrix used (e.g., `matrix_standard_v1`). |
| `total_score` | `float` | Final calculated score. |
| `scaling_min` / `max` | `int` | Scale bounds (Strictly enforced). |
| `dimensions` | `list[DimensionResultItem]` | Score per dimension. |

`DimensionResultItem`:
*   `dimension_id` (`str`): ID from Ontology.
*   `score` (`float`): Numerical score.
*   `reasoning` (`str`): Justification.

---

## 📊 Reporting (`XAIReport`)
Final output schema.

| Field | Type | Description |
| :--- | :--- | :--- |
| `executive_summary` | `str` | High-level summary. |
| `final_verdict` | `str` | Conclusive judgment. |
| `score_cards` | `list[ScoreCardItem]` | Aggregated scores. |
| `xai_report_formatted` | `str` | **Markdown** report for the UI. |
