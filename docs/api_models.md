# API Models & Data Schemas (V2.5)

This document details the strict **Pydantic V2** data models used throughout the Cognitive Quorum system. All data exchange is strictly typed (`ConfigDict(strict=True, extra="ignore")`) to ensure hallucination-free execution and proper integration with the Server-Driven UI (SDUI) architecture.

> [!NOTE] 
> This document provides specific schema details, but all architectural rules must still follow the Single Sources of Truth as defined in `GEMINI.md` and `AGENTS.md`.

---

## 🟢 Core Infrastructure Models (`backend_v2.models.v2_core`)

These models represent the canonical SSOT database entities for the dynamic V2 orchestration system.

### `Workflow`
The top-level execution blueprint.
- `id`: Unique slug identifier (e.g., `workflow_audit_v2`).
- `name` & `description`: Multilingual `I18nText` objects.
- `expected_inputs`: Dictionary mapping input keys to their UI types (e.g., `{"chat_log": "file"}`).
- `steps`: List of `RoutingNode` definitions defining the Directed Acyclic Graph (DAG) flow.

### `RoutingNode`
An individual step within a Workflow DAG.
- `id`: Node identifier (e.g., `step_node_1`).
- `task_blueprint`: Slug referencing a specific `TaskBlueprint`.
- `depends_on`: List of predecessor node IDs.
- `input_mappings`: Dictionary mapping step inputs to `$` variables (e.g., `{"context": "$inputs.chat_log"}`).
- `model_strategy`: LLM strategy slug defining intelligence tier (e.g., `fast`, `deep`).

### `PromptBlock` (formerly Matrix/Component)
The universal atomic unit of cognitive instruction, merging legacy text components and evaluation matrices into a single polymorphic concept.
- `id`: String identifier (e.g., `block_judge_criteria`).
- `type`: Enum `instruction`, `matrix`, `generator`, or `hook`.
- `instruction`: Multilingual `I18nText`.
- `theory_grounding`: `TheoryGrounding` object containing `source_url` and `citation_reference`.
- `scales` & `rows`: Definitions for matrix-style BARS evaluations.
- `output_format`: Expected JSON sub-schema definition.

### `SystemConfig` (Model Registry)
Configuration singleton for global LLM routing.
- `id`: `model_registry`.
- `models`: Nested dictionary mapping cloud providers (e.g., `google`) to their configured models (e.g., `fast`, `deep`) with rules like `tpm_limit` and `temperature`.

---

## 🔒 Domain Logic Models (`backend_v2.models.execution`)

Domain models represent the absolute "truth" of the AI's cognitive reasoning payload during an active execution run.

### `ExecutionRecord`
The immutable state of a workflow run.
- `id`: Execution UUID.
- `workflow_id`: Target workflow slug.
- `status`: Execution status enum.
- `raw_inputs`: Original uploaded files/text.
- `frozen_context`: A deep-copy snapshot of all `PromptBlocks` and `Workflows` as they existed at `created_at` to guarantee eternal auditability.
- `results`: The finalized JSON schema output per step.
- `cost_estimate`: Estimated USD cost of the execution block.
- `prompt_tokens`, `completion_tokens`, `total_tokens`: Core semantic token tracking.
- `cached_tokens`, `reasoning_tokens`: Global advanced provider metadata metrics for diagnostic tracing.

---

## 🎭 Frontend View Models (`client_app_v2.models`)

The Flutter client relies heavily on dynamic parsing of SDUI instructions rather than massive static DTOs.

- `I18nText` parsing: Handled by `SafeCast` to dynamically extract the translation matching the current UI locale, falling back to `default_locale`.
- `Compound Widgets`: The UI intrinsically understands how to render matrix blocks by parsing the `ui_hints_snapshot` combined with `require_justification` bools into localized Sliders and TextFields.

---

## 🚦 REST APIs (Strict Separation)

Each specific configuration entity has its own strictly typed API Router.

| Entity | REST URI | Description |
| :--- | :--- | :--- |
| **Model Registry** | `/api/v2/studio/model-registry/` | Direct CRUD for the global LLM routing configuration. |
| **Available Models** | `/api/v2/studio/model-registry/available-models` | Dynamic fetch of LLM configurations bypassing cached state. |
| **Workflows** | `/api/v2/studio/workflows/` | DAG Blueprint management. |
| **Prompt Blocks** | `/api/v2/studio/prompt-blocks/` | Universal cognitive instruction blocks. |
| **Steps** | `/api/v2/studio/steps/` | Reusable TaskBlueprints. |
| **Executions** | `/api/v2/execution/executions/` | Job submission and metadata persistence. |
| **Execution Streams** | `/api/v2/execution/executions/{id}/stream` | Server-Sent Events (SSE) log of the active DAG execution. |
| **Markdown Rendering** | `/api/v2/execution/executions/{id}/render?lang={locale}` | SDUI endpoint generating localized Markdown from structured data. |
| **PDF Rendering** | `/api/v2/execution/executions/{id}/render_pdf` | Asynchronous trigger to bake an execution into a local PDF. |

This API isolation ensures that a schema error instantly triggers an RFC 7807 `422 Unprocessable Entity` via Pydantic on the boundary, protecting downstream logic and the database.
