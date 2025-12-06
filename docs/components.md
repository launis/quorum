# Workflow Components

Workflow Components are the fundamental building blocks of the Cognitive Quorum engine. They are divided into two main categories: **Workflow Hooks**, procedural Python functions for tasks like data retrieval and processing, and **Workflow Agents**, configurable, LLM-powered units that perform core reasoning and generation tasks.

---

## Workflow Hooks

Workflow Hooks are Python functions that extend a workflow's capabilities beyond standard LLM generation. Registered in the `HookRegistry`, they can be configured to execute at specific points in a workflow, such as before or after an Agent runs, to prepare data or process outputs.

### Data Retrieval

-   **`execute_google_search`**:
    -   **Description**: Queries the Google Custom Search JSON API to enrich the workflow context with real-time information.
    -   **Input**: `search_query` (string).
    -   **Output**: A list of search results, each containing a title, URL, and snippet.
    -   **Configuration**: Requires `GOOGLE_SEARCH_API_KEY` and `GOOGLE_SEARCH_CX` environment variables.

-   **`execute_rag_retrieval`**:
    -   **Description**: Retrieves relevant documents from a configured vector store to provide domain-specific context to an Agent.
    -   **Input**: A query string (e.g., `tainted_data`).
    -   **Output**: A string of concatenated documents (`rag_context`).

### Data Processing

-   **`sanitize_and_anonymize_input`**:
    -   **Description**: Sanitizes input text by removing Personally Identifiable Information (PII) using regular expressions to ensure data privacy and security.
    -   **Input**: `raw_input` (string).
    -   **Output**: `tainted_data` (sanitized string).

-   **`parse_json_output`**:
    -   **Description**: Parses a raw string from an LLM into a structured Pydantic model defined in the workflow configuration.
    -   **Feature**: Enforces strict schema compliance, ensuring that data passed between steps is valid and well-formed.

### Logic and Analysis

-   **`calculate_input_control_ratio`**:
    -   **Description**: Calculates the length ratio between an input text and a generated text. This metric serves as a heuristic for identifying potential hallucinations or overly verbose outputs.

-   **`detect_performative_patterns`**:
    -   **Description**: Scans text for keywords and phrases associated with performative or "fluff" language (e.g., "delve into," "tapestry").
    -   **Input**: Any text field from the workflow context (e.g., `history_text`).
    -   **Output**: A JSON list of detected patterns (`performative_patterns_detected`).

### Reporting

-   **`generate_jinja2_report`**:
    -   **Description**: Renders a final report by populating a Jinja2 template with data from the workflow context.
    -   **Feature**: Can dynamically fetch content, such as a disclaimer, from the static content database.

---

## Static Content

Static Content components provide a centralized repository for reusable text snippets like legal disclaimers, system prompts, or standardized instructions. This content is stored in a database and can be dynamically fetched by any hook or agent, ensuring consistency and ease of maintenance.

---

## Workflow Agents

Workflow Agents are the core reasoning and generation units of the engine. In Cognitive Quorum v2, an "Agent" is not a hardcoded class but a **configurable, data-driven step** within a workflow. This approach allows for the creation of complex, multi-step pipelines by defining a sequence of agent configurations in a data file, rather than writing new Python code.

### Agent Configuration

Each agent step in a workflow is defined by a configuration that specifies its behavior. Key parameters include:

-   **`agent_name`**: A unique identifier for the workflow step.
-   **`llm_config`**: Specifies the model to use (e.g., `gemini-1.5-pro-latest`) and its generation parameters (temperature, top-p, etc.).
-   **`prompt_template`**: The Jinja2 template used to generate the prompt sent to the LLM.
-   **`output_schema`**: The Pydantic model that the agent's response must conform to.

### The Agent Runner (`BaseAgent`)

The `BaseAgent` (`backend/agents/base.py`) is the underlying engine component responsible for executing these configured agent steps. It is not meant to be subclassed for each new task; instead, it provides a standardized, robust infrastructure for:

-   **LLM Interaction**: Manages connections to the configured LLM (e.g., Google Gemini, Mock LLM) and applies global or per-agent generation parameters.
-   **Error Handling**: Implements robust retry logic for transient API or network errors.
-   **Structured Output**: Provides a reliable `get_json_response` helper method to parse LLM string outputs into specified Pydantic models, ensuring data integrity between steps.

This data-driven architecture separates the logic of execution (the Agent Runner) from the definition of the task (the Agent Configuration). It empowers developers to rapidly build, modify, and chain together sophisticated reasoning steps—such as data extraction, analysis, critique, or synthesis—by simply editing a configuration file.