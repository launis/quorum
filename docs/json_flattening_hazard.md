# Hazard: JSON Flattening & Post-Process Healing

**Severity:** Moderate (Validation Failure)
**Type:** Integration / Schema Mismatch
**Status:** Mitigated (via Post-Process Healing)

## The Hazard: "Level Skipping Hallucination"

When working with nested Pydantic models (e.g., `PerformativityOutput` containing `PerformativityAnalysis`), Large Language Models (LLMs) often exhibit a behavior known as **"Level Skipping"** or **"JSON Flattening"**.

### Symptoms
The LLM correctly identifies the *content* fields it needs to populate (the "leaf" nodes of the schema) but hallucinates that the *wrapper* object (the "branch" node) is unnecessary redundancy.

**Expected Schema (Nested):**
```json
{
  "reasoning_trace": "...",
  "performativity_analysis": {  // <-- The Wrapper
    "performativity_heuristics": "...",
    "authenticity_score": "..."
  }
}
```

**Actual LLM Output (Flattened):**
```json
{
  "reasoning_trace": "...",
  "performativity_heuristics": "...", // <-- Flattened to root
  "authenticity_score": "..."
}
```

### Root Cause
1.  **Schema Complexity:** Injected JSON schemas (`{{SCHEMA_EXAMPLE}}`) show definitions separate from the main object, leading the model to "optimize" the structure under high token load context.
2.  **Instruction Drift:** Prompts focusing heavily on "Fill these fields" cause the model to lose focus on the structural hierarchy.

## The Remedy: Post-Process Healing (Postel's Law)

To ensure system resilience, we apply **Postel's Law**: *"Be conservative in what you do, be liberal in what you accept from others."*

We implement a `post_process` method in the Agent class (`backend/agents/critics.py`, `backend/agents/logician.py`) that acts as a **Structure Healer**.

### Mechanism
1.  **Detection:** The method checks if the expected wrapper key (e.g., `performativity_analysis`) is missing.
2.  **Signature Matching:** It scans the top-level keys for "Signature Keys" unique to the inner object (e.g., `performativity_heuristics`).
3.  **Healing:** If signature keys are found at the root, it creates the missing wrapper object and moves the data inside it.
4.  **Logging:** It logs a warning (`Schema Mismatch Detected`) to allow monitoring of the issue's frequency.

### Code Example
```python
def post_process(self, response_data: Any) -> Any:
    # 2. Heal Flattened Structure (Missing 'logician_data' wrapper)
    if "logician_data" not in response_data:
        inner_keys_signature = ["toulmin_analysis", "cognitive_level", "walton_scheme"]
        
        # If signature keys exist at root, wrap them
        if any(k in response_data for k in inner_keys_signature):
            logger.warning(f"[{self.__class__.__name__}] Healing flattened response structure (Schema Mismatch Detected).")
            # ... wrapping logic ...
```

## ⚠️ CRITICAL WARNING: Implicit Coupling

This remedy introduces **Implicit Coupling** (Hidden Dependency) between the Pydantic Model and the Agent Code.

*   **The Risk:** The `post_process` logic contains **Hardcoded String Literals** (e.g., `"toulmin_analysis"`, `"logician_data"`).
*   **The Danger:** If you rename a field in `backend/models/domain/*.py` (Refactoring), the Pydantic model updates, but this `post_process` logic **WILL BREAK SILENTLY** (or rather, fail to heal).
*   **Mitigation:**
    1.  **Audit:** When modifying Domain Models, ALWAYS grep for the field name in `backend/agents/`.
    2.  **Tests:** Ensure `backend/scripts/generate_preview_report.py` is run after any schema change.

> **Rule of Thumb:** Use `post_process` healing only when necessary for LLM stability. Do not rely on it for internal API communication.
