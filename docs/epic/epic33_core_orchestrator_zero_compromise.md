# Epic 33: Core Orchestrator Zero-Compromise Hardening

## 1. Description and Motivation
A comprehensive audit of the core orchestrator suite (`atomizer.py`, `chunking_service.py`, `dag_compiler.py`, `dag_executor.py`, and `prompt_compiler.py`) reveals a mixed state of architectural compliance. 

**The Good:**
- `chunking_service.py` is perfectly pure and generic (`T` generics).
- `dag_compiler.py` performs strict topological sorting using Pydantic models.
- `atomizer.py` explicitly utilizes strongly typed `.run_structured_task(response_model=AtomizationSchema)`.

**The Violations:**
Significant architectural drift (duck typing and "graceful fallback" behavior) is found deeply embedded in the variable parsing mechanisms of the `PromptCompiler`. It bypasses the **Strict Pydantic V2** mandates to manually parse naked dictionaries.

- The `PromptCompiler._extract_value_from_state` logic acts as a "scavenger", manually checking `hasattr`, `callable()`, and heavily branching on `isinstance(current, dict)`. It attempts to duct-tape generic dictionaries into Markdown recursively rather than relying on explicit Pydantic formatters.

**Objective:** Cleanse `PromptCompiler` of runtime type guessing. Enforce a rigorous boundary where only known, typed schemas are parsed into XML context nodes, strictly satisfying **The Zero-Compromise Pledge**.

## 2. Architectural Mandates Enforced (Rules Reference)
- **`the_zero_compromise_pledge` (`00-antigravity-core`):** Eradicate "Try A, then B" chains. `PromptCompiler` currently utilizes: `if hasattr(model_dump), else if isinstance(dict), else str()`. This guessing must be replaced with strict interface contracts (`TracePayload` objects).
- **`the_duct_tape_ban` (`00-antigravity-core`):** The recursive string un-nesting loop inside `PromptCompiler` (line ~197) is raw duct-tape applied to fix the Attention Dilution token crisis (Epic 12). It must be extracted into a formal Pydantic `.to_xml()` context renderer natively attached to the model.

## 3. Implementation Phase

### Eliminating PromptCompiler Semantic Duck Typing
- **Target:** `_extract_value_from_state` in `PromptCompiler`.
- **Action:** Remove the `isinstance(dict)` recursion tree, `hasattr` checks, and hardcoded string replacements (e.g., `replace("step_1_", "")`).
- **Reasoning:** Dynamically generating `<prior_step_context>` tags by stripping prefixes from arbitrary keys is a brittle, untestable hack that couples parsing logic tightly to old V1 nomenclature. While Epic 38 mitigated the prompt length token crisis, the parsing logic remains severely flawed and violates the Duct Tape Ban.
- **Solution:** Enforce that variables fetched from the state are typed models. Build explicit Pydantic `.to_xml()` formatters rendering XML context natively instead of magically guessing keys.

## 4. Testing & Verification Mandate (Synthesis.py Standard)

### Universal Synthesis.py Case Study Execution Standards
Every single code modification inside this Epic MUST strictly adhere to the exact same architectural rigor successfully pioneered in `backend_v2/hooks/synthesis.py`:
- **Eradicate God Blocks:** Destroy massive `try...except Exception:` blocks. If a function is wrapped in a catch-all that suppresses native `AppException` propagation or obscures the original HTTP status codes/`ErrorCodes`, blow it up immediately.
- **Pure Function Extraction:** Identify any deep dictionary mutation loops, arbitrary text compression, or O(N^2) search loops and aggressively rip them out into isolated, testable Pure Functions. Keep the main orchestrator as a simple, highly readable pipeline.
- **O(1) Map Pre-computation:** Nested iteration loops inside data pipelines must be replaced with O(1) pre-computed lookup dictionaries to resolve heavy schema references instantly.
- **Enum-Driven Configuration:** Replace arbitrary boolean toggles with strictly validated Pydantic Enums.
- **Zero-Compromise 100% Pytest Coverage:**
  - **Fail-Fast Safety Tests:** Write specific tests that feed missing or corrupted Pydantic metadata/locales to the orchestrator to verify that it immediately crashes with `400 Validation Error` or `404 Not Found` (Zero Graceful Degradation).
  - **Pure Function Isolation:** Every extracted helper function MUST have its own dedicated unit test validating corner cases without requiring Database or LLM mocks.
  - **Happy-Path Orchestrator Integration:** Use `MagicMock` and `PydanticModel.model_construct()` to bypass rigid instantiation overhead in the test suite, allowing the mock environment to simulate a flawless execution pipeline.
  - **Universal Quality Gate:** The refactored module MUST pass `ruff check`, `mypy`, and `pytest` with 0 warnings before being considered complete.

### Specific Epic 33 Testing Mandates
1. Use `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompt_compiler.py --test` specifically to verify no loss of XML nesting functionality during schema conversion.
