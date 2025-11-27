# Architecture: Cognitive Quorum v2

The **Cognitive Quorum v2** architecture is designed to be a fully **Generic Workflow Engine**. Unlike the previous version, which had hardcoded logic for specific agents, v2 is data-driven and modular.

## Core Concepts

### 1. Data-Driven Logic
All business logic is defined in the database (seeded from `seed_data.json`), not in code.
- **Rules**: Global constraints (e.g., "Chain of Trust").
- **Prompts**: Instructions for LLMs.
- **Steps**: Units of execution with defined Inputs, Outputs, and Hooks.
- **Workflows**: Ordered sequences of Steps.

### 2. Generic Engine
The `Orchestrator` and `Executor` classes (`src/engine/`) are agnostic to the specific content of the workflow. They simply execute the sequence defined in the database.

### 3. Registry Pattern
To bridge the gap between static data (JSON) and dynamic code (Python), we use a Registry Pattern:
- **`SchemaRegistry`**: Maps string names (e.g., "AnalysisSummary") to Pydantic models.
- **`HookRegistry`**: Maps string names (e.g., "execute_google_search") to Python functions.

## Directory Structure

```
src/
├── components/         # Hybrid Components (Hooks & Templates)
│   ├── hooks/          # Python functions (Search, RAG, Parsing)
│   └── templates/      # Jinja2 templates for reporting
├── database/           # Database Client & Initialization
├── engine/             # Orchestrator & Executor
└── models/             # Pydantic Schemas & Registry
```

## Execution Flow

1.  **Orchestrator** loads the Workflow definition from the DB.
2.  **Orchestrator** iterates through the `sequence` of Steps.
3.  **Executor** runs each Step:
    *   **Pre-Hooks**: Python functions run *before* the LLM (e.g., Search, RAG).
    *   **LLM Call**: Prompts + Context sent to the model (Gemini/GPT-4).
    *   **Post-Hooks**: Python functions run *after* the LLM (e.g., Parsing, Reporting).
4.  **State** is passed between steps via the `context` dictionary.
