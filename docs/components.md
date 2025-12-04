# Workflow Components

Workflow Components are the building blocks of the Cognitive Quorum engine. They are divided into two main categories: **Workflow Hooks**, which are procedural Python functions for tasks like data retrieval and processing, and **Workflow Agents**, which are configurable, LLM-powered units for core reasoning and generation tasks.

---

## Workflow Hooks

Workflow Hooks are Python functions that extend a workflow's capabilities beyond standard text generation. Registered in the `HookRegistry`, they can be configured to execute at specific points in a workflow, such as before or after an Agent runs.

### 1. External Data Retrieval

- **`execute_google_search`**:
    - **Description**: Performs a Google Search using the official Custom Search JSON API to enrich the workflow context with real-time information.
    - **Input**: `search_query` (typically derived from a prompt or a previous step's output).
    - **Output**: A list of search results, each containing a title, URL, and snippet.
    - **Configuration**: Requires the `GOOGLE_SEARCH_API_KEY` and `GOOGLE_SEARCH_CX` environment variables.

- **`execute_rag_retrieval`**:
    - **Description**: Retrieves relevant documents from a configured vector store to provide additional, domain-specific context to an Agent.
    - **Input**: A query string (e.g., `tainted_data`).
    - **Output**: A string of concatenated documents (`rag_context`).

### 2. Data Processing and Parsing

- **`sanitize_and_anonymize_input`**:
    - **Description**: Removes Personally Identifiable Information (PII) and sanitizes input text using regular expressions to ensure data privacy and security.
    - **Input**: `raw_input`.
    - **Output**: `tainted_data` (sanitized text).

- **`parse_json_output`**:
    - **Description**: Parses a raw LLM string output into a structured Pydantic model defined in the workflow configuration.
    - **Feature**: Enforces strict schema compliance, ensuring the data passed between steps is valid and well-formed.

### 3. Logic and Control

- **`calculate_input_control_ratio`**:
    - **Description**: Calculates the ratio between the length of an input text and a generated text. This metric can be used as a heuristic to help identify potential hallucinations or overly verbose outputs.

### 4. Reporting

- **`generate_jinja2_report`**:
    - **Description**: Renders a final report by populating a specified Jinja2 template with data from the workflow context.
    - **Feature**: Can dynamically fetch content, such as a disclaimer, from the static content database via a `DISCLAIMER` component.

### 5. Analysis Hooks

- **`detect_performative_patterns`**:
    - **Description**: Scans text for specific keywords and phrases associated with performative or "fluff" language (e.g., "delve into", "tapestry").
    - **Input**: Any text field from the workflow context (e.g., `history_text`, `product_text`).
    - **Output**: A JSON list of detected patterns (`performative_patterns_detected`).

---

## Static Content

Static content components store reusable text snippets, such as legal disclaimers, standardized instructions, or system prompts. This content is stored in a database and can be dynamically fetched and injected into the workflow context by any hook or agent.

---

## Workflow Agents

Agents are the core reasoning units of the workflow engine. Located in `backend/agents/`, they are designed to be generic and configurable. Instead of a fixed sequence of hardcoded agents, a workflow is now defined by a series of agent configurations, allowing for flexible and adaptable data processing pipelines.

### Base Infrastructure

#### `BaseAgent` (`backend/agents/base.py`)
- **What**: The abstract base class for all dynamically configured agents.
- **Why**: It standardizes LLM interactions, error handling, retries, and configuration management, ensuring consistent behavior across all workflow steps.
- **How**:
    - Manages the connection to the configured LLM (e.g., Google Gemini, Mock LLM).
    - Applies global and per-agent generation parameters (e.g., Temperature, Top-P, Top-K).
    - Implements robust retry logic for transient network or API errors.
    - Provides a `get_json_response` helper method for reliable parsing of LLM outputs into Pydantic models.

### Agent Configuration

An "Agent" is not a static class but an *instance* configured within a workflow definition. Each agent in a sequence is defined by its specific configuration, which typically includes:

- **`agent_name`**: A unique identifier for the workflow step.
- **`llm_config`**: Specifies the model to use (e.g., `gemini-1.5-pro-latest`) and its generation parameters.
- **`prompt_template`**: The Jinja2 template used to generate the prompt sent to the LLM.
- **`output_schema`**: The Pydantic model that the agent's response is expected to conform to.

This data-driven approach allows developers to construct complex workflows by defining a sequence of specialized agents, each performing a discrete task—such as data extraction, analysis, critique, synthesis, or formatting—without writing new Python code for each step.