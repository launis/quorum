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

# Core Agents

The system relies on a set of specialized AI agents, located in `backend/agents/`, each designed for a specific phase of the cognitive assessment process. All agents inherit from `BaseAgent`.

## Base Infrastructure

### `BaseAgent` (`backend/agents/base.py`)
- **What**: The abstract base class for all agents.
- **Why**: Standardizes LLM interactions, error handling, retries, and configuration.
- **How**:
    - Manages the connection to Google Gemini (or Mock LLM).
    - Applies global generation parameters (Temperature: 0.7, Top-P: 0.95, Top-K: 64).
    - Implements retry logic for network errors.
    - Provides `get_json_response` helper for robust JSON parsing.

## Operational Agents (By Phase)

### 1. `GuardAgent` (`backend/agents/guard.py`)
- **When**: **Phase 1 (Input Processing)**.
- **Why**: To ensure data safety, privacy, and compliance before deep analysis begins.
- **How**:
    - **Input**: Raw user submissions (chat history, product text, reflection).
    - **Action**: Sanitizes PII, checks for security threats, and structures the raw data.
    - **Output**: Cleaned and structured JSON data (`safe_data`).

### 2. `AnalystAgent` (`backend/agents/analyst.py`)
- **When**: **Phase 2 (Evidence Anchoring)**.
- **Why**: To create a factual foundation for the assessment.
- **How**:
    - **Input**: `safe_data` from the Guard Agent.
    - **Action**: Extracts verifiable facts and creates an "Evidence Map" (Todistuskartta).
    - **Output**: A structured map of evidence linking claims to specific parts of the input.

### 3. `LogicianAgent` (`backend/agents/logician.py`)
- **When**: **Phase 3 (Argument Construction)**.
- **Why**: To structure the evidence into a coherent logical argument.
- **How**:
    - **Input**: Evidence Map from the Analyst.
    - **Action**: Applies cognitive frameworks (Bloom's Taxonomy, Toulmin Argumentation) to build an argument.
    - **Output**: `argumentaatioanalyysi` (Argumentation Analysis).

### 4. `PanelAgent` (`backend/agents/panel.py`)
- **When**: **Phases 4-7 (Multi-Perspective Auditing)**.
- **Why**: To subject the argument to rigorous criticism from multiple angles without making multiple expensive API calls.
- **How**:
    - **Input**: Argumentation Analysis and Evidence Map.
    - **Action**: Simulates a panel of critics in a single execution:
        - **Logical Falsifier**: Checks for fallacies.
        - **Causal Analyst**: Verifies cause-and-effect claims.
        - **Performativity Detector**: Checks for AI-generated artifacts or lack of authenticity.
        - **Factual Overseer**: Verifies external facts (optionally using Google Search results).
    - **Output**: A combined JSON object containing audit reports from all perspectives.

### 5. `JudgeAgent` (`backend/agents/judge.py`)
- **When**: **Phase 8 (Final Verdict)**.
- **Why**: To synthesize all analyses and audits into a final score and verdict.
- **How**:
    - **Input**: All previous outputs (Audits, Argumentation, Evidence).
    - **Action**: Weighs the evidence and audits to determine the final grade.
    - **Output**: `TuomioJaPisteet` (Verdict and Points) - a strictly validated JSON object.

### 6. `XAIReporterAgent` (`backend/agents/judge.py`)
- **When**: **Phase 9 (Reporting)**.
- **Why**: To translate the structured data and scores into a human-readable, educational report.
- **How**:
    - **Input**: Final Verdict, Audits, and original context.
    - **Action**: Generates a natural language explanation of the results.
    - **Output**: Markdown-formatted text for the final report.