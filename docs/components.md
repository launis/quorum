# Hybrid Components & Hooks

Hybrid Components allow the workflow to perform actions beyond text generation. They are implemented as Python functions and registered in the `HookRegistry`.

## Available Hooks

### 1. External Data Retrieval
- **`execute_google_search`**:
    - **Description**: Performs a Google Search using the official Custom Search JSON API.
    - **Input**: `hypothesis_argument` or `prompt_text`.
    - **Output**: List of search results (Title, URL, Snippet).
    - **Configuration**: Requires `GOOGLE_SEARCH_API_KEY` and `GOOGLE_SEARCH_CX`.

- **`execute_rag_retrieval`**:
    - **Description**: (Stub) Retrieves relevant documents from a vector store.
    - **Input**: `tainted_data`.
    - **Output**: `rag_context`.

### 2. Data Processing & Parsing
- **`sanitize_and_anonymize_input`**:
    - **Description**: Removes PII and sanitizes input text using RegEx.
    - **Input**: `raw_input`.
    - **Output**: `tainted_data` (sanitized).

- **`parse_analyst_output`**, **`parse_logician_output`**, **`parse_judge_output`**:
    - **Description**: Parses raw LLM output (Markdown/JSON) into structured Pydantic models.
    - **Feature**: Extracts **Citations** (`source`, `explanation`) from the text.

### 3. Reporting
- **`generate_jinja2_report`**:
    - **Description**: Renders the final XAI Report using a Jinja2 template.
    - **Feature**: Dynamically fetches the **Disclaimer** from the database (`DISCLAIMER` component).

### 4. Logic & Control
- **`calculate_input_control_ratio`**:
    - **Description**: Calculates the ratio of original input vs. generated text to detect hallucinations.

## Static Content
Static text, such as disclaimers, is stored as a `static_text` component in the database and fetched dynamically by hooks.
