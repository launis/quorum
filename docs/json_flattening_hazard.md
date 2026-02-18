# Hazard: JSON Flattening & Post-Process Healing (V3.2)

**Severity:** Moderate (Validation Failure)
**Type:** Integration / Schema Mismatch
**Status:** Mitigated (via Strict DTOs & Post-Process Healing)

## The Hazard: "Level Skipping Hallucination"

When working with nested Pydantic models (e.g., `PerformativityOutput` containing `PerformativityAnalysis`), Large Language Models (LLMs) often exhibit a behavior known as **"Level Skipping"** or **"JSON Flattening"**.

### Symptoms
The LLM correctly identifies the *content* fields it needs to populate (the "leaf" nodes) but hallucinates that the *wrapper* object (the "branch" node) is unnecessary redundancy.

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

---

## The V3.2 Solution: Strict DTOs & Panel Fusion

In Phase 8 (V3.2), we introduced two architectural patterns that fundamentally alter the landscape of this hazard.

### 1. DTO Simplification (Prevention)
Instead of asking the LLM to fill complex Domain Models (with Metadata wrappers), we request **Data Transfer Objects (DTOs)**. These are often flatter by design.

*   **Old Way**: `AnalystOutput` (Domain) -> Requires nesting.
*   **New Way**: `AnalystOutputDTO` (Content) -> Flatter schema. Python code wraps it later.

### 2. Panel Fan-Out (Architectural Flattening)
The `PanelAgent` intentionally produces a massive nested object (`PanelOutputDTO`), which the Engine then **Fans Out** (flattens) into the `WorkflowState`.

*   **Input**: `PanelOutput.logician_analysis`
*   **Output State**: `step_logician` (Key) -> `LogicianOutput` (Value)

This implies that flattening is now a **First-Class Citizen** of the architecture when controlled by the Engine, but remains a **Hazard** when hallucinogenically performed by the LLM inside a DTO.

---

## Residual Mitation: Post-Process Healing

Despite DTOs, "Level Skipping" still occurs within the DTO structure itself. We apply **Postel's Law**: *"Be conservative in what you do, be liberal in what you accept."*

We implement `post_process` in Agent classes (`backend/agents/`) as a **Structure Healer**.

### Mechanism
1.  **Detection**: Check if expected wrapper key is missing.
2.  **Signature Matching**: Scan for "Signature Keys" unique to the inner object.
3.  **Healing**: If keys exist at root, wrap them.

### Code Example
```python
def post_process(self, response_data: Any) -> Any:
    # Heal Flattened Structure
    if "logician_data" not in response_data:
        inner_keys = ["toulmin_analysis", "cognitive_level"]
        if any(k in response_data for k in inner_keys):
            logger.warning(f"[{self.__class__.__name__}] Healing flattened response.")
            # ... wrapping logic ...
```

## ⚠️ CRITICAL WARNING: Implicit Coupling

This remedy introduces **Implicit Coupling** between Pydantic Models and Agent Code.

*   **The Risk:** `post_process` contains **Hardcoded String Literals**.
*   **The Danger:** Renaming a field in `backend/models/domain/*.py` will break the healer SILENTLY.
*   **Mitigation:**
    1.  **Audit:** When modifying Domain Models, ALWAYS grep for the field name in `backend/agents/`.
    2.  **DTO Isolation:** Since DTOs are less likely to change than Domain Models, binding healing logic to DTO schemas is safer.
