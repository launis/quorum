# Dynamic Prompt Construction

The workflow engine employs a data-driven **Dynamic Prompt Construction** system. This approach avoids hardcoding prompts in source code. Instead, prompts are assembled at runtime from modular, reusable components. This design provides superior flexibility, maintainability, and reusability across all workflows.

## The Architecture of a Prompt

A final prompt sent to an LLM is composed of three distinct layers:

1.  **Template (`.j2`)**: The structural skeleton of the prompt, containing logic and placeholders.
2.  **Content Fragments (`.json`)**: Reusable, modular blocks of content (e.g., rules, instructions, examples).
3.  **Runtime Context**: The specific input data and variables for a given task execution.

### 1. Jinja2 Templates

The engine uses the powerful **Jinja2** templating language. This allows for conditional logic, loops, and variable injection directly within the prompt's structure, enabling the creation of highly adaptive and context-aware prompts.

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

### 2. Content Fragments

Fragments are atomic, reusable pieces of text stored in a structured format like JSON. They are centrally managed and can be dynamically included in any template.

This design promotes the DRY (Don't Repeat Yourself) principle. For instance, a standard safety warning can be defined in a single fragment file. Any workflow needing this warning can include it. Updating the warning in the source fragment instantly propagates the change to all dependent prompts.

### 3. Runtime Context

This layer consists of the dynamic, real-time data provided to the workflow for a specific execution. It includes user inputs, data retrieved from other systems, and any other variables needed to complete the task. The Jinja2 template injects this context into the appropriate placeholders to create a complete, task-specific prompt.

## Structured Output and Schema Enforcement

To ensure reliable, machine-readable outputs, the engine enforces a strict schema on the LLM's response.

The workflow's configuration specifies a Pydantic model or a raw JSON Schema that defines the desired output structure. The engine automatically ensures the LLM's response conforms to this schema by using the most effective method available from the provider (e.g., Tool Calling, JSON Mode). This eliminates the need for fragile parsing logic and guarantees that the output is valid and predictable.

## Prompt Engineering Workflow

To create or modify a prompt for a workflow, follow these steps:

1.  **Define the Goal**: Clearly articulate the task the LLM needs to perform and the desired outcome.
2.  **Create Reusable Fragments**: Break down instructions, rules, or examples into modular JSON fragments for maximum reuse and maintainability.
3.  **Construct the Template**: Create a Jinja2 template (`.j2` file) that arranges the fragments and defines placeholders for runtime data.
4.  **Define the Output Schema**: Create a Pydantic model that defines the exact structure of the expected JSON output. This model is referenced in the workflow configuration, not in the prompt text itself.
5.  **Test and Iterate**: Use the engine's development tools to render and inspect the final prompt. Run the workflow with sample data to validate the LLM's output against the defined schema.