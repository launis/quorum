# Dynamic Prompt Construction

The workflow engine utilizes a **Dynamic Prompt Construction** system. This approach avoids hardcoding prompts in source code, instead assembling them at runtime from modular, data-driven components. This provides greater flexibility, reusability, and maintainability.

## The Architecture of a Prompt

A final prompt sent to an LLM is composed of three distinct layers:

1.  **Template (`.j2`)**: The structural skeleton of the prompt, containing logic and placeholders.
2.  **Fragments (`.json`)**: Reusable, modular blocks of content (e.g., rules, instructions, examples).
3.  **Runtime Context**: The specific input data and variables for a given task execution.

### 1. Jinja2 Templates

We use the powerful **Jinja2** templating engine. This allows for conditional logic, loops, and variable injection directly within the prompt's structure, enabling highly adaptive prompts.

**Example (`templates/generic_task.j2`):**
```jinja2
You are a {{ role }}. Your primary directive is to act as a helpful assistant.

**INSTRUCTIONS**
{{ fragments.instructions.core_directive }}

**TASK**
Analyze the following user input and perform the requested action.
User Input:
---
{{ user_input }}
---

**FORMATTING REQUIREMENTS**
{% for requirement in formatting_rules %}
- {{ requirement.name }}: {{ requirement.description }}
{% endfor %}

Your output must be a JSON object that adheres to the provided schema.
```

### 2. Fragments

Fragments are atomic, reusable pieces of text stored as structured data (e.g., JSON). They are centrally managed and can be included in any template.

*   **Benefit**: This design promotes the DRY (Don't Repeat Yourself) principle. For example, a standard safety warning can be defined in a single fragment file. Any workflow needing this warning can include it. Updating the warning in the one source file propagates the change to all dependent prompts instantly.

### 3. Structured Output (Schema Enforcement)

To ensure reliable, machine-readable outputs, the engine enforces a JSON Schema on the LLM's response.

*   **Mechanism**: The workflow's configuration specifies a Pydantic model or a direct JSON Schema for the desired output. The engine automatically handles enforcement by using the LLM provider's most effective method (e.g., Tool Calling, JSON Mode). This guarantees that the output conforms to the defined structure, eliminating the need for fragile parsing logic.

## Prompt Engineering Workflow

To create or modify a prompt for a workflow:

1.  **Define the Goal**: Clearly articulate the task the LLM needs to perform.
2.  **Author Reusable Fragments**: Break down instructions, rules, or examples into modular JSON fragments for maximum reuse.
3.  **Construct the Template**: Create a Jinja2 template (`.j2` file) that arranges the fragments and placeholders for runtime data.
4.  **Define the Output Schema**: Create a Pydantic model that defines the exact structure of the expected JSON output. This model is linked in the workflow configuration, not referenced in the template text.
5.  **Test and Iterate**: Use the engine's testing tools to build and inspect the final prompt, then run the workflow to validate the LLM's output against the schema.