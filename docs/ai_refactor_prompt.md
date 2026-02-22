# The Atomic Refactoring Prompt Strategy

Below is a proven, step-by-step prompt sequence you can copy-paste into your AI chat (like ChatGPT, Claude, or Google AI). It forces the AI to check your code strictly against the `docs/flutterpromptohje.md` Manifesto without suffering from "Context Dilution" or hallucinated shortcuts.

**How to use:**
1. Replace `[YOUR_FILE.py]` with the actual file you want to audit (e.g., `backend/api/transformers/causal.py`).
2. Do not run Phase 2 before the AI has completely finished Phase 1. 

---

## 🛑 Phase 0: The Planning Phase (Do not let the AI code yet!)

Copy-paste this prompt first:

```markdown
Read the file `[YOUR_FILE.py]` and the system manifesto `docs/flutterpromptohje.md`.

Do NOT write or modify any code yet. Instead, write an `implementation_plan.md` that audits `[YOUR_FILE.py]` against the manifesto. Break the audit down into the following 6 phases:

1. **Phase 1: Generics & Architecture (Part 0 & 1)**: Dependencies, deprecated patterns (Check for `ChangeNotifier` vs `Riverpod 3.0`, raw Dicts).
2. **Phase 2: Core Frameworks (Part 2 & 4)**: Null-lists (Pydantic), `Annotated[Depends]`, async/sync drivers in Python, or `GoRouteData` and `Isolate` in Dart.
3. **Phase 3: The Error Handling Contract (Part 3)**: Verify EVERY try/except block. Look for the `AppException` pattern and RFC 7807 compliance.
4. **Phase 4: Localization & I18N (Part 10 & 16)**: Enforce the "No-String" API Policy, check for ICU pluralization, and ensure formatting happens in the frontend.
5. **Phase 5: Output Compositing (Part 15)**: Verify BFF boundaries. Missing data must degrade gracefully with `{}` instead of 500 errors.
6. **Phase 6: The Zero-Compromise Check (Part 18)**: Look for silent patches (`except pass`, `.get('field', default)`) or hardcoded magic strings.
7. **Phase 7: Documentation & Hygiene (Part 17)**: Eliminate "What" comments, enforce Contract-Driven comments, and verify strict Imperative Mood in docstrings.

Output the plan only. Wait for my permission before executing.
```

---

## ⚡ Execution Phases (Run these one by one)

Once the AI prints the plan, run these prompts sequentially. If the AI hallucinates, say "Stop. Re-read the manifesto rules for this phase."

### Prompt 1: Generics & Dependencies
```markdown
Execute Phase 1. Audit `[YOUR_FILE.py]` against Parts 0 and 1 of `flutterpromptohje.md`. Ensure modern standards are enforced and there are no BANNED legacy patterns (e.g., dict returns). Provide the refactored code block.
```

### Prompt 2: Core Framework Modernization
```markdown
Execute Phase 2. Audit `[YOUR_FILE.py]`/`[YOUR_FILE.dart]` against Parts 2 and 4 of `flutterpromptohje.md`. Focus purely on:
- **If Python**: Ensuring `Annotated[..., Depends()]` is used, checking Pydantic arrays use `Field(default_factory=list)`, and verifying the execution environment isolation (synchronous `TinyDB` routes MUST be `def`, `Firebase` routes `async def`).
- **If Dart**: Ensuring modern Riverpod 3.0 generation, `GoRouteData` usage, and replacing `compute` with `Isolate.run`.
Provide the refactored code block.
```

### Prompt 3: The Error Handling Contract
```markdown
Execute Phase 3. Audit `[YOUR_FILE.py]` STRICTLY against Part 3 of `flutterpromptohje.md`. 
- Upgrade every bare `ValueError` or generic `Exception` to the RFC 7807 `AppException` pattern.
- Ensure the Enum `ErrorCodes` are used.
- Ensure the `message` string does NOT contain leaked secrets. 
- Ensure Logger tags match the current component name.
- **Dual-Reporting Mandate**: Verify that EVERY error block contains an explicit `logger.error(...)` statement IN ADDITION to raising the exception.
Provide the refactored code block.
```

### Prompt 4: Localization & I18N
```markdown
Execute Phase 4. Audit `[YOUR_FILE.py]`/`[YOUR_FILE.dart]` against Parts 10 and 16 of `flutterpromptohje.md`.
- Enforce the "No-String" API Policy: Only Enum/Keys traverse the API, no translated UI texts or string formatting from the Backend.
- Ensure any string interpolation or pluralization uses ICU formats strictly in the frontend `.arb` files.
- Verify that UI styling (Semantic Markup) remains in `.arb` files and is not hardcoded.
Provide the refactored code block.
```

### Prompt 5: BFF Strict Typing & Resilience (If applicable)
```markdown
Execute Phase 5. Audit `[YOUR_FILE.py]` STRICTLY against Part 15 of `flutterpromptohje.md`.
- **Strict Nesting**: Ensure all Agent outputs are nested under their specialist key (e.g., `{"logician_data": {...}}`) and not flattened.
- **Graceful Degradation**: Verify that if specialist data is missing, the UiSection defaults to `{}` rather than crashing with `None`.
- **Developer Visibility**: Ensure that whenever fallback degradation occurs, the code emits a clear warning to alert developers. Use `logger.warning(...)` in Python or `debugPrint('🔴 UI GRACEFUL DEGRADATION: ...')` in Dart.
Provide the refactored code block.
```

### Prompt 6: The Zero-Compromise Integrity Check
```markdown
Execute Phase 6. Audit `[YOUR_FILE.py]`/`[YOUR_FILE.dart]` against Part 18 of `flutterpromptohje.md`. 
- Eradicate ALL defensive `except: pass` blocks.
- Remove hardcoded Magic Numbers and move them to Constants.
- Ensure all logic enforces Fail Fast on invalid data (e.g. out-of-bounds explicit scores).
Provide the final refactored code block.
```

### Prompt 7: Documentation & Code Hygiene
```markdown
Execute Phase 7. Audit `[YOUR_FILE.py]`/`[YOUR_FILE.dart]` against Part 17 of `flutterpromptohje.md`. 
- Enforce the Imperative Mood for all function descriptions.
- Eliminate narrative "What" inline comments entirely.
- Ensure architectural workarounds use bolded Contract-Driven Comments (e.g., `NOTE (Architecture):`).
- Delete any abandoned or orphaned `TODO` comments without owners.
- Wipe away all commented-out "zombie" code.
Provide the final refactored code block.
```

### Prompt 8: The Zero Error Linter Loop
```markdown
Execute Phase 8. After integrating the refactored code from the previous steps, you must now PROVE that the changes strictly comply with the typing and styling standards.
- Run `ruff check backend/` (Python) or `dart analyze` (Dart). Do NOT proceed until the response contains 0 errors. If errors exist, automatically write the fixes and re-run.
- Run `mypy backend/` (Python). Do NOT proceed until the response contains 0 errors (ignoring known global exclusions if any). If errors exist, automatically write the typing fixes and re-run.
You are not allowed to declare the refactoring finished until both static analyzers return completely clean output.
```

---
**Why this works:** Small, targeted prompts prevent the LLM from getting "lazy" or dropping context in the middle of a massive file refactor. You act as the conductor, ensuring standard compliance part by part, ending with an unarguable static analysis proof of correctness.
