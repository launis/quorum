# API Models & Data Schemas

This document details the strict **Pydantic V2** data models used throughout the Cognitive Quorum system. All agent outputs are validated against these schemas to ensure strictly typed, hallucination-free execution, with support for **Reasoning Token Extraction**.

---

## 🟢 Core State

### `WorkflowState` (Blackboard)
The central, persistent state object passed between all agents.

| Field | Type | Description |
| :--- | :--- | :--- |
| `execution_id` | `str` | Unique UUID for this execution instance. |
| `workflow_id` | `str` | ID of the workflow definition. |
| `current_step_name` | `str` | Identifier of the active step. |
| `version` | `int` | Optimistic locking version (prevents race conditions). |
| `organization_id` | `str` | Tenant ID. |
| `inputs` | `InputData` | Immutable user inputs. |
| `audit_results` | `dict[str, EvaluationResult]` | Dynamic container for matrix-based evaluations. |
| `reasoning_context` | `dict` | "Show Your Work" traces (Gemini "Thinking" tokens). |

### `InputData`
Raw inputs provided by the user.

| Field | Type | Description |
| :--- | :--- | :--- |
| `history_text` | `str` | Historical context (chat logs). |
| `product_text` | `str` | Primary artifact to analyze. |
| `reflection_text` | `str` | Student/User self-reflection. |
| `bibliography_context` | `list[str]` | Optional reference citations. |

> **⚠️ Architectural Constraint**: The current `InputData` model is "Slot-Based", enforcing specific fields (`history`, `product`). This prevents arbitrary file uploads without semantic mapping. A "Hyper-Dynamic" Artifact-based refactor is planned for Q1 2026.

---

## 🛡️ Agent Schemas (Step-by-Step)

### 1. Guard Agent (`TaintedData`)
Safety and PII analysis.

| Field | Type | Description |
| :--- | :--- | :--- |
| `data` | `TaintedDataContent` | Pointers to source files (content is hidden). |
| `security_check` | `SecurityCheck` | Threat analysis results. |
| `safe_data` | `SafeDataContent` | Sanitized (PII-free) text payload. |

### 2. Analyst Agent (`TodistusKartta`)
Research and evidentiary grounding.

| Field | Type | Description |
| :--- | :--- | :--- |
| `hypoteesit` | `list[Hypoteesi]` | Formulated research hypotheses. |
| `rag_todisteet` | `list[RagTodiste]` | Evidence retrieved from RAG/Vector DB. |

### 3. Logician Agent (`ArgumentaatioAnalyysi`)
Logical structure mapping.

| Field | Type | Description |
| :--- | :--- | :--- |
| `toulmin_analyysi` | `list[ToulminKomponentti]` | Breakdown into Claim, Data, Warrant. |
| `kognitiivinen_taso` | `KognitiivinenTaso` | Bloom's Taxonomy assessment. |
| `walton_skeema` | `WaltonSkeema` | Argumentation scheme identification. |

### 4. Falsifier Agent (`LogiikkaAuditointi`)
Devil's Advocate and Stress Testing.

| Field | Type | Description |
| :--- | :--- | :--- |
| `walton_stressitesti_loydokset` | `list[WaltonStressitesti]` | Results of critical questioning. |
| `paattelyketjun_uskollisuus_auditointi` | `PaattelyketjunUskollisuus` | Check for post-hoc rationalization. |

### 5. Overseer Agent (`EtiikkaJaFakta`)
Fact-checking and Ethical Audit.

| Field | Type | Description |
| :--- | :--- | :--- |
| `faktantarkistus_rfi` | `list[FaktantarkistusRFI]` | Verification of claims via Google Search. |
| `eettiset_havainnot` | `list[EettinenHavainto]` | Detection of bias, discrimination, or harm. |

### 6. Causal Agent (`KausaalinenAuditointi`)
Distinguishing correlation from causation.

| Field | Type | Description |
| :--- | :--- | :--- |
| `kausaalinen_auditointi` | `KausaalinenAuditointiData` | Timeline and causality analysis. |
| `kontrafaktuaalinen_testi` | `KontrafaktuaalinenTesti` | "What if?" simulation results. |
| `abduktiivinen_paatelma` | `Literal` | Final causal conclusion. |

### 7. Performativity Detector (`PerformatiivisuusAuditointi`)
Authenticity and psychological profiling.

| Field | Type | Description |
| :--- | :--- | :--- |
| `performatiivisuus_heuristiikat` | `list[PerformatiivisuusHeuristiikka]` | Checks for manipulative heuristics. |
| `pre_mortem_analyysi` | `PreMortemAnalyysi` | Weak signal detection. |
| `yleisarvio_aitoudesta` | `Literal` | Organic vs. Performative assessment. |

### 9. Judge Agent (`TuomioJaPisteet`)
Scoring and Final Verdict (Legacy/Static).

| Field | Type | Description |
| :--- | :--- | :--- |
| `pisteet` | `Pisteet` | Scoring breakdown (Analysis/Evaluation/Synthesis). |
| `konfliktin_ratkaisut` | `list[KonfliktinRatkaisu]` | How contradictions were resolved. |
| `mestaruus_poikkeama` | `MestaruusPoikkeama` | Detection of exceptional quality. |

---

## 🧠 Dynamic Evaluation

### `EvaluationResult` (New System)
Used by `JudgeAgent` (Cognitive) and other dynamic evaluators.

| Field | Type | Description |
| :--- | :--- | :--- |
| `matrix_id` | `str` | ID of the Evaluation Matrix used. |
| `total_score` | `float` | Calculated aggregate score. |
| `dimensions` | `list[DimensionResultItem]` | Score per dimension (e.g. "Agency", "Insight"). |
| `critical_findings` | `list[str]` | High-importance feedback. |

### `DimensionResultItem`

| Field | Type | Description |
| :--- | :--- | :--- |
| `dimension_id` | `str` | Validated ID from the Matrix. |
| `score` | `Union[int, float]` | Numerical score. |
| `reasoning` | `str` | Justification for the score. |

---

## 📊 Reporting

### `XAIReport` (Reporter Agent)
The final executive summary.

| Field | Type | Description |
| :--- | :--- | :--- |
| `executive_summary` | `str` | High-level overview. |
| `final_verdict` | `str` | Conclusive judgment. |
| `confidence_score` | `float` | AI confidence (0.0 - 1.0). |
| `xai_report_formatted` | `str` | Full Markdown report ready for rendering. |

---

## 🏢 Identity Models

### `Organization` (Tenant)
Represents a customer account or the system shell.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` | Unique Identifier (slug-friendly). |
| `name` | `str` | Display Name (e.g., "Acme Corp"). |
| `tier` | `enum` | `standard`, `premium`, `enterprise` |
| `contact_email` | `str` | Billing/Admin contact. |
| `created_at` | `str` | ISO 8601 Timestamp. |

---

## 🔩 Shared Components

### `APIError` (Standard Error)
Strict error contract for all HTTP 4xx/5xx responses.

| Field | Type | Description |
| :--- | :--- | :--- |
| `error_code` | `enum` | `VALIDATION_ERROR`, `RESOURCE_NOT_FOUND_ERROR`, `INTERNAL_SERVER_ERROR`, or custom (e.g., `ORG_HAS_USERS`). |
| `message` | `str` | Human-readable description (English, for debugging). |
| `details` | `list` | Optional context (Pydantic validation errors or stack traces). |

### `Metadata`
Included in every agent output.

| Field | Type | Description |
| :--- | :--- | :--- |
| `agentti` | `str` | Name of the producing agent. |
| `vaihe` | `float` | Workflow step number. |
| `luontiaika` | `str` | ISO 8601 Timestamp. |
| `thought` | `str` | **Reasoning Token** trace (Show Your Work). |
