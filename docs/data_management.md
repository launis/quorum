# Data Management & Databases

This document describes the data management architecture of the Cognitive Quorum system. The system is **data-driven**, meaning its business logic, prompts, and workflows are defined in the database rather than hardcoded in the application.

## Data Structure

All system data is located in the `data/` directory. This file-based approach simplifies backup and version control.

### 1. Initialization Data (`data/seed_data.json`)

This file contains the system's "factory settings" and defines its core logic. It includes:

*   **Components**: Definitions for agents, tools, and prompts.
*   **Steps**: Individual workflow steps, including their input/output schemas and execution hooks.
*   **Workflows**: The sequence and linkage of steps that form a complete process.

**Usage:**
On system initialization or database reset, `seed_data.json` is loaded into the runtime database. This design allows system behavior to be modified by changing the JSON file without altering application code.

### 2. Runtime Database (`data/db.json`)

The system uses **TinyDB**, a lightweight, document-oriented database stored in the `db.json` file.

It contains two primary categories of data:
1.  **Configuration**: A live copy of the content from `seed_data.json` (components, steps, workflows). This data can be modified at runtime to adjust system behavior dynamically.
2.  **Execution History**: A complete record of every analysis run is stored here, including:
    *   User inputs
    *   Intermediate results and responses from each agent
    *   The final generated report
    *   Timestamps and status information

> **Note:** The `db.json` file can grow significantly in size over time, as it stores a complete history of all execution runs.

### 3. Fragments (`data/fragments/`)

This directory contains reusable JSON-formatted text snippets used to construct prompts. Examples include:

*   `mandates.json`: High-level system goals (e.g., "Employ System 2 Thinking").
*   `rules.json`: Global operational rules (e.g., "Do not use external tools without permission").
*   `criteria.json`: Standardized evaluation criteria (e.g., a BARS matrix).
*   `protocols.json` & `methods.json`: Other methodological instructions.

This approach avoids content duplication. A rule or mandate can be referenced by multiple prompts; updating the fragment file ensures the change is propagated everywhere it is used.

### 4. Templates (`data/templates/`)

This directory contains **Jinja2** templates (`.j2`) that define the structure of agent prompts.

For example, `prompt_analyst.j2` might contain:
```jinja2
{{ MASTER_INSTRUCTIONS }}

PHASE 2: ANALYST AGENT
...
FOLLOW THESE RULES:
{% for rule in rules %}
- {{ rule }}
{% endfor %}
```

The system dynamically combines the following to construct a complete prompt for the Large Language Model (LLM):
1.  Configuration data from the runtime database (`db.json`).
2.  Text snippets from the `fragments/` directory.
3.  A structural template from the `templates/` directory.

### 5. Uploads (`data/uploads/`)

This directory serves as temporary storage for files uploaded by the user through the UI, such as PDF documents.

The process is as follows:
*   A file is uploaded to this directory.
*   The system processes the file (e.g., extracts text from a PDF).
*   The extracted content is used as an input for a workflow.
*   The folder can be cleaned periodically, either automatically or manually.

## Data Flow Summary

```mermaid
graph TD
    subgraph Initialization
        Seed[seed_data.json] -->|Load| DB[(db.json)]
    end

    subgraph "Prompt Engineering"
        Tpl[templates/*.j2] -->|Render| Prompt
        Frag[fragments/*.json] -->|Inject| Prompt
        DB -->|Config| Prompt
    end

    subgraph Execution
        User[User Input] --> Engine
        Uploads[data/uploads/*] -->|Process| Engine
        Prompt -->|Context| Engine
        Engine -->|Call| LLM[LLM API]
        LLM -->|Response| Engine
        Engine -->|Save History| DB
    end

    style DB fill:#f9f,stroke:#333,stroke-width:2px
    style LLM fill:#ff9,stroke:#333,stroke-width:2px
```