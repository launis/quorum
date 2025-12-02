# Prompt Engineering & Dynamic Construction

Cognitive Quorum uses a sophisticated **Dynamic Prompt Construction** system. Instead of hardcoding prompts in Python strings, we assemble them at runtime from modular components.

## The Architecture of a Prompt

A final prompt sent to the LLM is composed of three layers:

1.  **Template (`.j2`)**: The structural skeleton.
2.  **Fragments (`.json`)**: Reusable content blocks (Rules, Mandates).
3.  **Context (Runtime Data)**: The specific input data for the task.

### 1. Jinja2 Templates

We use **Jinja2** for templating. This allows for logic within the prompt itself.

**Example (`templates/prompt_analyst.j2`):**
```jinja2
You are the ANALYST AGENT.

{{ MANDATES.SYSTEM_2_THINKING }}

YOUR TASK:
Analyze the following input data:
{{ input_data }}

CRITERIA:
{% for criterion in criteria.BARS_MATRIX %}
- {{ criterion.name }}: {{ criterion.description }}
{% endfor %}
```

### 2. Fragments

Fragments are small, atomic pieces of text stored in `data/fragments/`.

*   **Why?** If we want to update the definition of "Critical Thinking," we change it in `fragments/mandates.json` once, and it automatically updates every agent that uses that mandate.

### 3. Schema Injection

To ensure the LLM outputs valid JSON, we inject the JSON Schema directly into the prompt.

*   **Syntax**: `[Ks. schemas.py / ModelName]`
*   **Mechanism**: The `WorkflowEngine` parses this tag, looks up the Pydantic model in `backend/schemas.py`, and inserts the corresponding JSON Schema definition.

## Prompt Engineering Workflow

To create or modify a prompt:

1.  **Identify the Goal**: What should this agent do?
2.  **Select Fragments**: Which existing Rules or Mandates apply?
3.  **Draft the Template**: Create a new `.j2` file (or edit via UI) combining instructions and fragments.
4.  **Define Output Schema**: Create a Pydantic model in `backend/schemas.py` and reference it in the template.
5.  **Test**: Run the workflow in Mock mode to verify the LLM understands the instructions and adheres to the schema.