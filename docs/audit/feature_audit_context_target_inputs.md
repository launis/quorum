# Feature & Architectural Audit: Context Target Input Routing & "Lopputuote" Badge Hardcoding

## Context & Executive Summary

In response to user inquiry:
> *"Miksi kaikki perusteet on muka haettu 'Lopputuote' syötteestä. Eri atomien arvothan pitäisi hakea kaikista eri syötteistä."*

This audit conducts a First Principles System 2 deconstruction and a Panel of Experts investigation into how evaluation inputs (`product_text`, `chat_log`, `reflection_text`) flow from the workflow DAG to the extractive sensor LLM, and why every single scorecard row in the Flutter client UI currently displays the `"Lopputuote"` badge.

---

## 1. Root Cause & First Principles Analysis

### 1.1 The Visual Bug: Naive Dictionary Iteration in `matrix_domain_parser.py`

When the backend builds `MatrixScorecardRowDTO` instances for SDUI presentation, it assigns `context_target` and `context_target_label` in @[backend_v2/services/matrix_domain_parser.py#L470-L491].

The current legacy implementation in `matrix_domain_parser.py` executes an unindexed loop across the dictionary values of `input_mappings`:
1. It iterates over `mapped_val` in `input_mappings.values()`.
2. As soon as it encounters a string prefix matching `$inputs.`, it strips the prefix and executes `break`.
3. It resolves the resulting key against `expected_inputs_map`.

In @[backend_v2/seed/seed_data.json], workflow `wf_9d68c573802341db` configures `input_mappings` for all 13 evaluation step rules with dictionary key-value order:
```json
"input_mappings": {
  "product_text": "$inputs.product_text",
  "chat_log": "$inputs.chat_log",
  "reflection_text": "$inputs.reflection_text"
}
```

Because Python 3.7+ preserves dictionary insertion order:
1. The loop starts at `"product_text": "$inputs.product_text"`.
2. It encounters `$inputs.product_text`.
3. It immediately executes `break`.
4. It resolves `"product_text"` to label `"Lopputuote"`.
5. **Result**: Every matrix (specifically: *Aktiivinen ohjaus / Goodhart*, *Prosessiomistajuus / Ylituomari*, *Päättelyn rehellisyys*, *Harkintakyky*) is unconditionally labeled with the grey chip `"Lopputuote"` in Flutter, completely ignoring the fact that `chat_log` and `reflection_text` were also mapped into that step.

---

### 1.2 The Execution Reality: What Did the LLM Actually Evaluate?

Did the LLM actually evaluate `"Lopputuote"` only, or did it see all inputs?

In @[backend_v2/services/orchestrator/strategies/llm.py#L127-L143], the workflow execution engine unpacks step inputs:
It extracts all string values from `inputs_unwrapped` and joins them into a single string:
`global_source_text = "\n\n".join(texts)`

Because all three inputs (`product_text`, `chat_log`, `reflection_text`) are strings in `inputs_unwrapped`, `llm.py` concatenated **all three inputs together** into a single `global_source_text` separated by `\n\n`.

In @[backend_v2/services/orchestrator/engines/tda_engine.py#L136-L163] and @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L68], this entire concatenated text was wrapped inside `<context>\n...\n</context>`:

```xml
<context>
[B0] ... Lopputuote text ...
[B1] ...
[B12] ... Keskusteluhistoria (User: ..., AI: ...) ...
[B25] ... Reflektiodokumentti (Itsearviointi ...) ...
</context>
```

#### Forensic Proof from `execution_trace.json`:
Looking at the actual reasoning emitted by the LLM in run `exe_88267cb7b3cf4718ae76b7dbce04a92e`:
- **`matrix_goodhart` (Atom `tda_09d6056ea44a7315473d0abe737d7a85`)**:
  > *"In your user payloads, you explicitly request a balanced dialogue across three distinct perspectives (Talous, HR, Strategia)..."* $\rightarrow$ **Evaluated `chat_log`**!
- **`matrix_judge` (Atom `tda_b4e82bca48654f9ab948d4b3004abf81`)**:
  > *"You structured the problem into sequential iterative stages (multi-perspective dialogue, initial draft, source verification)..."* $\rightarrow$ **Evaluated `chat_log` and process structure**!
- **`matrix_taskguard` (Atom `tda_76df73280fc943cc9434d44efc8116e8`)**:
  > *"The text documents self-reflection and iterative critique of workplace policies..."* $\rightarrow$ **Evaluated `reflection_text`**!
- **`matrix_causal_abductive` (Atom `tda_1361cf5ec5b5420c905cd2a1f80893a7`)**:
  > *"The self-reflection acknowledges general post-hoc evaluation but does not actively claim unstated preceding intent parameters."* $\rightarrow$ **Evaluated `reflection_text`**!

**Conclusion**: The sensor **did** search across all inputs, but:
1. The inputs were sent as an unpartitioned text block without input-source delimitations.
2. The UI stamped `"Lopputuote"` on every row because of the naive dictionary break in `matrix_domain_parser.py`.

---

## 2. Panel of Experts Audit

### Expert 1: Backend & Seed Vault Architect
- **Defect in SSOT Schema**: Neither `PromptBlock` (matrix) nor `TDAAssertion` currently specifies which input key it targets. In `seed_data.json`, `PromptBlock` has `theory_grounding`, `scales`, `ai_description`, but lacks an explicit `target_input_key: str | None` (specifically: `"chat_log"`, `"reflection_text"`, `"product_text"`, or `"all"`).
- **Hardcoded Fallback in Parser**: `matrix_domain_parser.py#L477` contains a classic anti-pattern: iterating through dictionary values and breaking on the first match. If multiple inputs are mapped, arbitrarily selecting the first one violates the Zero-Compromise rule.

### Expert 2: LLM Prompt & Attention Topology Architect
- **Context Pollution**: Concatenating `product_text`, `chat_log`, and `reflection_text` into a single monolithic string creates ambiguous epistemic grounds. When an atom in *Goodhart* asks whether the human steered the prompt, the model must scan through the *entire* student memo, the reflection essay, and the chat transcript.
- **Section Fencing Mandate**: Per `05_llm_architecture.md#role_segregation_and_fencing`, multiple user inputs must be explicitly tagged and fenced in XML:
  ```xml
  <input_payloads>
    <input name="product_text" label="Lopputuote">...</input>
    <input name="chat_log" label="Keskusteluhistoria">...</input>
    <input name="reflection_text" label="Reflektiodokumentti">...</input>
  </input_payloads>
  ```
  This allows atoms to target specific inputs without cross-contamination.

### Expert 3: SDUI & Frontend Architect
- **Deceptive Labeling**: The Flutter widget @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart#L53-L90] faithfully displays `axis.contextTargetLabel`. Because the backend returned `"Lopputuote"` for every row, the user logically concluded that Quorum only evaluated the final deliverable and completely ignored the chat log and reflection.
- **Visual Asterisks**: The frontend in `sdui_matrix_table_widget.dart#L62-L63` appends raw `*` and `**` strings to the title for evaluative / override flags, which clashes with modern typography and creates visual clutter.

---

## 3. Falsification & Anti-Happy-Path Scenarios

1. **Scenario 1: Missing or Optional Input**
   - If a workflow run provides only `product_text` and leaves `chat_log` empty, atoms that strictly evaluate operator dialogue must not pass based on content in `product_text`, nor should they crash. They must evaluate to `FAILED` or `N_A` (Data Starvation).
2. **Scenario 2: Matrix with Dedicated Target vs Cross-Cutting Target**
   - Specific matrices have single-target focus:
     - *Goodhart / Aktiivinen ohjaus*: Evaluates human steering in `chat_log`.
     - *Epistemic Humility / Oman tiedon rajat*: Evaluates meta-cognition in `reflection_text` and caveats in `product_text`.
     - *Toulmin / Väitteiden perustelu*: Evaluates argumentation in `product_text`.
   - If `context_target` is hardcoded to a single input string on the row, how does the UI represent a matrix that evaluates all inputs or multiple inputs?
   - **Resolution**: `context_target` can either be a specific input key (specifically: `"chat_log"`) with label `"Keskusteluhistoria"`, or `"all"` with label `"Kaikki syötteet"` (All inputs).

---

## 4. Five-Axis Deconstruction & Directives Table

| Axis | Current As-Is | Target To-Be (Architectural Law) | Invariant Guardrail | Actionable Directive |
| :--- | :--- | :--- | :--- | :--- |
| **Scope Boundary** | Naive loop selects first `$inputs.` key from step rule (`product_text`). | `PromptBlock` or `StepRule` explicitly declares `target_input_key` (`product_text`, `chat_log`, `reflection_text`, or `all`). | SSOT Schema Integrity | Add `target_input_key: str | None` to `MatrixPromptBlock` and resolve `context_target_label` from it. |
| **Duct-Tape Prevention** | `matrix_domain_parser.py` breaks on first dict item with `# noqa: QGR012`. | Explicit deterministic mapping: if matrix has `target_input_key`, use it; if step has multiple inputs and matrix has none, label as `"Kaikki syötteet"` (`all`). | Zero Permissive Typing / No Duck-Tape | Eliminate first-match break loop. Replace with explicit SSOT attribute check. |
| **Best Practice** | All inputs concatenated into raw unlabelled text string. | Inputs compiled with explicit XML boundaries (`<input name="chat_log">...</input>`). | Context Segregation (`05_llm_architecture.md`) | In `MatrixSensorPromptBuilder`, fence each input with its designated tag. |
| **Over-Engineering Guard** | Attempting to route atoms individually to different LLM sub-calls per atom. | Keep batch sensor execution intact, but inform LLM via prompt which section to evaluate or provide fenced sections. | Concurrency & Cost Sovereignty | Do not fragment DAG execution into dozens of micro-calls. Keep Bo3 chunk batching. |
| **Proof Anchor** | Visual inspection of grey pill badge in Flutter app. | SDUI integration tests asserting exact `context_target` and `context_target_label` on each matrix scorecard row. | Two-Stage Audit Loop | Test asserting `matrix_goodhart` has `chat_log` target and `matrix_toulmin` has `product_text` target. |

---

## 5. Architectural Recommendation & Two-Phase Solution

### Phase A: Remedial Display & Resolution Fix (Immediate)
1. **Fix `matrix_domain_parser.py`**:
   - Check if the `MatrixPromptBlock` has a declared `target_input_key`.
   - If the StepRule has multiple `$inputs.*` mappings (specifically: `product_text`, `chat_log`, `reflection_text`), and the matrix does not restrict itself to a single input, label it as `"Kaikki syötteet"` (`"all"`) instead of falsely labeling it `"Lopputuote"`.
   - Map known matrices to their intended target inputs:
     - `matrix_goodhart`: `chat_log` ("Keskusteluhistoria")
     - `matrix_judge`: `chat_log` ("Keskusteluhistoria")
     - `matrix_toulmin`: `product_text` ("Lopputuote")
     - `matrix_bloom`: `product_text` ("Lopputuote")
     - `matrix_causal_analyst`: `product_text` ("Lopputuote")
     - `matrix_kahneman`: `all` ("Kaikki syötteet")
     - `matrix_falsifier`: `all` ("Kaikki syötteet")
     - `matrix_epistemic_humility`: `all` ("Kaikki syötteet")
     - `matrix_taskguard`: `all` ("Kaikki syötteet")
     - `matrix_causal_abductive`: `all` ("Kaikki syötteet")
     - `matrix_taskxai_clarity`: `all` ("Kaikki syötteet")
     - `matrix_archivist`: `all` ("Kaikki syötteet")
     - `matrix_xai_reporter`: `all` ("Kaikki syötteet")
2. **Clean UI Titles**:
   - Remove the `*` and `**` string suffixes in `sdui_matrix_table_widget.dart` and `matrix_row_item_widget.dart`.

### Phase B: SSOT Schema & Fenced Context Pipeline (Implementation Plan Update)
1. Add `target_input_key: str | None = None` to `MatrixPromptBlock` in `backend_v2/models/domain/prompt_block.py`.
2. Update `seed_data.json` so each matrix explicitly declares its target input (`"chat_log"`, `"product_text"`, or `"all"`).
3. Update `MatrixSensorPromptBuilder` to format the inputs with explicit XML delimiters so the LLM knows precisely where the chat transcript ends and the product text begins.
