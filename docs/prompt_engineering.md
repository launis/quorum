# Dynamic Prompt Construction

Prompts are assembled at runtime from `db.json` configurations + Jinja2 templates.

## Architecture

1.  **Template (`.j2`)**: The structural skeleton (e.g., `generic_task.j2`).
2.  **Fragments**: Reusable rules (e.g., `MANDATE_1`).
3.  **Context**: Data from previous steps (`WorkflowState`).

## Type-Safe Prompting (V2.0)

In V2.0, prompt engineering is tightly coupled with **Pydantic V2 Schemas**.

*   **No "JSON Hallucination"**: We do not ask the LLM to "try to make JSON".
*   **Explicit Schema**: We provide the JSON Schema of the target Pydantic model in the prompt or via Native Tool Calling.
*   **Validation Loop**: If the LLM output fails `model_validate()`, options are automatically retried.

## Workflow

1.  **Define Model**: Create `class MyResult(BaseJSON): ...` in `backend/models/`.
2.  **Create Template**: format instructions in `backend/templates/`.
3.  **Configure Step**: Link the step to the schema in `seed_data.json` (`output_schema: "MyResult"`).