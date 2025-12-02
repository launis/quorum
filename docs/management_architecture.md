# Management Architecture

The Management Architecture of Cognitive Quorum allows administrators to modify the system's "brain" (prompts, rules, and logic) without touching the source code. This is achieved through the **Management UI** in Streamlit.

## The "Configuration as Code" Philosophy

While the system is running, its behavior is governed by the data in `db.json`. However, the "Source of Truth" is the `seed_data.json` file and the `fragments/` directory.

### Management Workflow

1.  **Edit**: The user modifies a Rule or Prompt in the Streamlit UI.
2.  **Runtime Update**: The change is immediately saved to `db.json` (or `db_mock.json`), affecting all *subsequent* workflow runs.
3.  **Persistence**: To make the change permanent (surviving a database reset), the user must click **"Deploy to Seed"** (or "Deploy Mock to Prod").

## UI Components (`pages/management.py`)

The Management Dashboard is divided into several tabs:

### 1. Prompts & Rules
*   **Editor**: A rich text editor for modifying prompt templates.
*   **Fragment Manager**: Allows editing specific `rules.json` or `mandates.json` entries.
*   **Preview**: Shows how a prompt will look after Jinja2 rendering.

### 2. System Maintenance
*   **Database Reset**: Wipes the current `db.json` and reloads from `seed_data.json`.
*   **Migration**: Tools to move data between Mock and Production environments.
    *   *Deploy Mock to Prod*: Promotes tested configurations to the live system.
    *   *Deploy Prod to Mock*: Copies live data to the sandbox for debugging.

### 3. Workflow Editor
*   **Visualizer**: Displays the current workflow steps and their connections.
*   **Configuration**: Allows changing the model (e.g., Flash vs Pro) for specific steps.

## Data Synchronization

The system maintains two parallel environments:

| Environment | Database File | Purpose |
| :--- | :--- | :--- |
| **MOCK** | `data/db_mock.json` | Sandbox for testing new prompts and rules safely. |
| **PROD** | `data/db.json` | The live environment used for actual assessments. |

The **Management UI** automatically detects which environment is active (based on `.env` or backend config) and operates on the corresponding database.