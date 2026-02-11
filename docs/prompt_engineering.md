# Dynamic Prompt Engineering (V2.9)

In Cognitive Quorum V2026, prompt engineering is an **architectural discipline**, not just text editing. The system uses a **Polymorphic Injection** strategy to dynamically assemble prompts from database components, strict Pydantic schemas, and runtime state.

Instead of static text files, prompts are constructed at runtime by the `PromptBuilder` service (`backend/services/prompt_builder.py`), ensuring that every agent receives exactly the context it needs—and nothing else.

---

## 1. The Composition Architecture

The prompt generation pipeline follows a strict **Builder Pattern**:

1.  **Resolution**: The system fetches the Step Configuration from `seed_data.json` (or DB).
2.  **Component Fetch**: It retrieves all referenced components listed in `execution_config.llm_prompts` (e.g., `["mandate_slow_thinking", "matrix_cognitive_v2"]`).
3.  **Formatting**:
    *   **Text Components**: Appended directly.
    *   **Matrix Components**: Transformed by `MatrixFormatter` into Markdown-formatted **Behaviorally Anchored Rating Scales (BARS)**. This ensures high-fidelity instruction for the LLM.
4.  **Injection**: The `PromptBuilder` scans the assembled text for Handlebars-style placeholders (`{{VARIABLE}}`) and injects runtime data.

### The "Sandwich" Model

A typical prompt is constructed in layers:

1.  **Directives Layer (The Bun)**:
    *   **System Mandates**: Irrevocable constraints (e.g., "Mandaatti 1: Hidas ajattelu").
    *   **Agent Identity**: "You are the Judge."
2.  **Context Layer (The Lettuce)**:
    *   **Injected State**: `{{HISTORY_TEXT}}`, `{{PRODUCT_TEXT}}`.
    *   **Upstream Evidence**: `{{PREVIOUS_STEP_OUTPUTS}}` (The "Baton").
    *   **External Data**: `{{GOOGLE_SEARCH_RESULTS}}`, `{{PROFILER_METRICS}}`.
3.  **Cognitive Layer (The Meat)**:
    *   **Evaluation Matrix (BARS)**: Matrices are expanded into full rubrics (Criteria, Anchors, Scale Instructions).
    *   **Task Instructions**: Specific rules for the current step.
4.  **Output Layer (The Plate)**:
    *   **Strict JSON Schema**: `{{SCHEMA_EXAMPLE}}` (Auto-generated from Pydantic V2 models).
    *   **Formatting Rules**: "You MUST output valid JSON..."

---

## 2. Dynamic Injection Variables

The `PromptBuilder` supports a specific set of injection keys. These are **Case-Sensitive**.

### Core Workflow State
| Placeholder | Description | Source |
| :--- | :--- | :--- |
| `{{HISTORY_TEXT}}` | The raw chat log or input text being analyzed. | `state.inputs.history_text` |
| `{{PRODUCT_TEXT}}` | The target product/service description. | `state.inputs.product_text` |
| `{{REFLECTION_TEXT}}` | Strategic reflection or self-analysis input. | `state.inputs.reflection_text` |
| `{{CURRENT_STEP_NAME}}` | The ID of the currently executing step. | `state.current_step_name` |

### Context & Evidence (The Baton)
| Placeholder | Description | Source |
| :--- | :--- | :--- |
| `{{PREVIOUS_STEP_OUTPUTS}}` | A summary of findings from all previous agents. | `state.step_results` (Filtered) |
| `{{GOOGLE_SEARCH_RESULTS}}` | Results from the *Analyst* agent's web searches. | `state.aux_data.google_search_results` |
| `{{PROFILER_METRICS}}` | Quantitative metrics (token counts, etc.). | `state.aux_data.profiler_metrics` |

### System & Environment
| Placeholder | Description | Source | Implementation |
| :--- | :--- | :--- | :--- |
| `{{CURRENT_DATE}}` | Server date (DD.MM.YYYY). | `datetime.now()` | Standard |
| `{{DYNAMIC_TIME}}` | Server time (HH:MM). | `datetime.now()` | Standard |
| `{{DYNAMIC_LOCATION}}` | Server location (City, Country). | `ipapi.co` | Timeout-protected HTTP request |
| `{{BANNED_PHRASES}}` | Comma-separated list of prohibited terms. | `db.json` | Repository Fetch |

### Structural Enforcement
| Placeholder | Description | Source |
| :--- | :--- | :--- |
| `{{SCHEMA_EXAMPLE}}` | **CRITICAL**. The JSON structure the agent *must* output. | `model.model_json_schema()` |

---

## 3. Behaviorally Anchored Rating Scales (BARS)

V2.9 rejects generic "Rate 1-5" instructions. We use **BARS** matrices defined as JSON components. The `MatrixFormatter` transforms these into human-readable instructions.

**JSON Source (`db.json`):**
```json
{
  "id": "matrix_agency",
  "type": "evaluation_matrix",
  "content": {
    "scale": {"min": 1, "max": 4},
    "criteria": [
      {
        "id": "agency",
        "label": "Strateginen Ohjaus",
        "anchors": {
          "1": "Matkustaja: Ulkoistaa ajattelun.",
          "4": "Arkkitehti: Purkaa ongelman osiin."
        }
      }
    ]
  }
}
```

**Formatted Prompt Output (Markdown BARS):**
```markdown
### EVALUATION MATRIX: Kognitiivinen Quorum Unified Matrix
Scale: 1-4

### CRITERIA FOR EVALUATION:
#### Dimension: Strateginen Ohjaus (ID: agency)
**JSON Requirement**: You MUST use the exact ID 'agency' as the value for 'dimension_id'...
Proficiency Levels (Anchors):
  - Level 1: Matkustaja: Ulkoistaa ajattelun.
  - Level 4: Arkkitehti: Purkaa ongelman osiin.
  [SCORING INSTRUCTION]: Map the Anchor Levels (1-4) to the required Scale (1-4).
```

---

## 4. Strict Type-Driven Prompting

To ensure system stability, we allow **no hallucinations** in the output structure.

1.  **Schema Definition**: Every Agent (e.g., `JudgeAgent`) defines a Pydantic V2 `OUTPUT_SCHEMA` (e.g., `EvaluationResult`).
2.  **Auto-Generation**: `PromptBuilder` calls `_generate_schema_json()` on the agent instance.
3.  **Validation**: The `GraphEngine` validates the LLM's response against this schema. If it fails, the step fails (Fail-Fast).

**Example Instruction:**
> "Return the result purely as size-optimized JSON. Use this schema:
> `{{SCHEMA_EXAMPLE}}`"

---

## 5. Development Workflow

To add a new prompt or matrix:

1.  **Create Component**: Add a new entry to `seed_data.json` under `components`.
    *   Type: `prompt` (for text) or `evaluation_matrix` (for BARS).
2.  **Reference in Step**: Update the `step_definition` in `seed_data.json`:
    ```json
    "execution_config": {
      "llm_prompts": ["mandate_system_1", "my_new_prompt", "matrix_custom"]
    }
    ```
3.  **Run Seeder**: `python backend/seed/run_seed.py local` to apply changes.
4.  **No Code Required**: The `PromptBuilder` handles the rest dynamically.