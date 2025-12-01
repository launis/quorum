# Hybrid Components

Hybrid Components are Python functions that extend a workflow's capabilities beyond standard text generation. They are registered in the `HookRegistry` and can be configured to execute at specific points in the process.

## Available Hooks

### 1. External Data Retrieval

- **`execute_google_search`**:
    - **Description**: Performs a Google Search using the official Custom Search JSON API.
    - **Input**: `hypothesis_argument` or `prompt_text`.
    - **Output**: A list of search results, each containing a title, URL, and snippet.
    - **Configuration**: Requires the `GOOGLE_SEARCH_API_KEY` and `GOOGLE_SEARCH_CX` environment variables to be set.

- **`execute_rag_retrieval`**:
    - **Description**: Retrieves relevant documents from a configured vector store to provide additional context.
    - **Input**: `tainted_data`.
    - **Output**: `rag_context`.

### 2. Data Processing and Parsing

- **`sanitize_and_anonymize_input`**:
    - **Description**: Removes Personally Identifiable Information (PII) and sanitizes input text using regular expressions.
    - **Input**: `raw_input`.
    - **Output**: `tainted_data` (sanitized text).

- **`parse_json_output`**:
    - **Description**: Parses raw LLM string output into a structured Pydantic model based on a predefined schema.
    - **Feature**: Enforces strict schema compliance (e.g., validating output against the `TuomioJaPisteet` model for a Judge Agent).

### 3. Logic and Control

- **`calculate_input_control_ratio`**:
    - **Description**: Calculates the ratio between the length of the original input and the generated text. This metric can help identify potential hallucinations or overly verbose outputs.

### 4. Reporting

- **`generate_jinja2_report`**:
    - **Description**: Renders the final report using a specified Jinja2 template.
    - **Feature**: Dynamically fetches content, such as a disclaimer, from the static content database via the `DISCLAIMER` component.

## Static Content

Static content components store reusable text, such as legal disclaimers or standardized instructions. This content is stored in a database and can be fetched dynamically by any hook during a workflow's execution.