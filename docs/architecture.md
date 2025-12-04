# System Architecture

Cognitive Quorum v2 is built on a modern, modular architecture designed for flexibility, scalability, and rigorous process control. The system is a generic, data-driven engine capable of executing complex workflows defined entirely through configuration.

## High-Level Diagram

```mermaid
graph TD
    User[User / Client] -->|HTTP| Streamlit[Streamlit Frontend]
    Streamlit -->|REST API| FastAPI[FastAPI Backend]
    
    subgraph "Backend Core"
        FastAPI --> Engine[Generic Workflow Engine]
        Engine -->|Executes Step| Agent[Agent (as defined in DB)]
        Engine -->|Reads/Writes State| Context[(Workflow Context)]
        
        Agent -->|Uses| LLM["LLM Service (Gemini)"]
        Agent -->|Uses| Hooks[Hybrid Hooks]
    end
    
    subgraph "Data & Configuration (TinyDB)"
        Engine -- Reads --> WorkflowDef[Workflow Definition]
        Context -- Stored in --> DB[(Database)]
        Hooks <-->|Search| Google[Google Search API]
    end
```

## Core Components

### 1. Frontend (Streamlit)
*   **Role**: Provides a dynamic user interface for interacting with the backend engine. It acts as the primary client for initiating workflows and managing system configurations.
*   **Features**:
    *   **Workflow UI**: A user-friendly interface for selecting a workflow, providing initial inputs (e.g., file uploads), and monitoring its execution in real-time.
    *   **Management UI**: Configuration editors for creating and modifying Workflows, Steps (Agents), Prompts, and Schemas.
    *   **Data Inspection**: Tools for viewing the final and intermediate JSON context of any workflow run.

### 2. Backend (FastAPI)
*   **Role**: The system's central API layer. It exposes REST endpoints that allow the frontend (or any other client) to interact with the workflow engine and manage its configuration.
*   **Key Endpoints**:
    *   `/workflows/{workflow_id}/start`: Initiates a new run of a specific workflow.
    *   `/workflows/`, `/steps/`, `/prompts/`: CRUD operations for all system configuration objects stored in the database.
    *   `/status/{run_id}`: Retrieves the current state and context of a running or completed workflow.

### 3. Generic Workflow Engine
*   **Role**: The heart of the system. It orchestrates the execution of workflows based on definitions loaded from the database. It is entirely agnostic to the specific logic of the steps it is running.
*   **Mechanism**:
    1.  Receives a request to start a specific **Workflow**.
    2.  Loads the corresponding **Workflow Definition** from the database. This definition is a list of **Steps** to be executed in sequence.
    3.  Initializes a **Workflow Context**, a JSON object that holds the state for the entire run.
    4.  Iterates through each **Step (Agent)** in the definition.
    5.  For each step, it:
        *   Constructs a **Prompt** by rendering a Jinja2 template with data from the current **Context**.
        *   Executes the designated **Tool** (e.g., an LLM call or a custom Python hook).
        *   Validates the tool's output against the step's defined Pydantic **Schema**.
        *   Merges the validated result back into the **Workflow Context**.
    6.  Persists the final context to the database upon completion.

### 4. Database (TinyDB)
*   **Role**: The single source of truth for all configuration and runtime data. Its file-based, schema-less nature provides flexibility for rapid development.
*   **Data Stored**:
    *   **Configuration**: All definitions for Workflows, Steps, Prompts, and Schemas.
    *   **Runtime Data**: The execution history and final JSON context for every workflow run.

## Data-Driven Workflow Execution

The core principle of v2 is that **logic is data**. Instead of a hardcoded process, the system executes workflows that are defined as documents within the database. This makes the system extremely flexible, allowing operators to create, modify, or combine cognitive processes without changing any code.

A **Workflow** is simply a named, ordered list of **Steps**.

A **Step** (or "Agent") is a document that defines a single unit of work, containing:
*   A reference to a **Prompt** template.
*   The name of the **Tool** to execute (e.g., `llm:gemini-pro` or `hook:google_search`).
*   A reference to a Pydantic **Schema** used to validate the tool's output.

This data-driven design transforms the system from a specific application into a general-purpose platform for creating and running structured, multi-step AI processes.

## Technology Stack

*   **Language**: Python 3.10+
*   **Web Framework**: FastAPI
*   **UI Framework**: Streamlit
*   **Database**: TinyDB (JSON-based, file-backed)
*   **LLM**: Google Gemini (via `google-generativeai`)
*   **Validation**: Pydantic
*   **Templating**: Jinja2