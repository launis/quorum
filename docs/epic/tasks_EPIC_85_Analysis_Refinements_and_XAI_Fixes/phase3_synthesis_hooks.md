# Implementation Plan - Phase 3: Synthesis Hooks & XAI Highlight Curation

This implementation plan focuses on text consolidation, dynamic tone application, and curation of XAI highlight extensions inside the synthesis hook.

## User Review Required

> [!IMPORTANT]
> - Dynamic tone configuration overrides and removes the hardcoded "Human-Centric Focus" rule from both synthesis and row explanation prompts.
> - XAI highlights are curated and deduplicated by the LLM instead of blind python slicing (`items[:max_items]`). They are injected into the user message via `<raw_extensions>` XML block.
> - Dynamic curation constraints are passed inside the `<execution_parameters>` block.

## Proposed Changes

### Hooks Layer

#### [MODIFY] [synthesis.py](file:///c:/src/quorum/backend_v2/hooks/synthesis.py)
- **Source:** Epic §5, Fix 5 (Intelligent XAI Extension Curation) & Fix 6 (Unified Dynamic Tone & Language Maintenance)
- **Changes:**
  - **Tone Instruction Resolution (Fix 6):**
    - Resolve the dynamic tone configuration: `tone_text = synthesis_cfg.tone_instruction.resolve(language) if (synthesis_cfg and synthesis_cfg.tone_instruction) else ""`.
    - Remove the hardcoded "Human-Centric Focus" rules from global `sys_prompt` (lines 642-646) and row explanations `row_exp_prompt` (lines 825-834).
    - If `tone_text` is present, inject it dynamically into `sys_prompt` rules as:
      `sys_prompt += f"  <rule>TONE INSTRUCTION: {tone_text}</rule>\n"`
    - If `tone_text` is present, inject it dynamically into `row_exp_prompt` rules as well.
  - **XAI Highlights Extraction & LLM Curation (Fix 5):**
    - Move XAI highlights extraction logic (lines 797-814) to occur **before** the main `execute_tool_loop` call.
    - Format gathered raw highlights as an XML tag:
      ```python
      raw_ext_blocks = []
      for item in raw_highlights:
          ext_type = item["extension_type"]
          ext_content = item["content"]
          raw_ext_blocks.append(f'  <extension type="{ext_type}">{ext_content}</extension>')
      raw_ext_xml = ""
      if raw_ext_blocks:
          raw_ext_xml = "<raw_extensions>\n" + "\n".join(raw_ext_blocks) + "\n</raw_extensions>\n\n"
      ```
    - Append `raw_ext_xml` into the `user` message text `raw_input_text` (so it resides at the end of the user message and respects caching boundaries).
    - In `sys_prompt` rules, add a static rule:
      `"  <rule>XAI HIGHLIGHTS CURATION: Review the <raw_extensions> XML block in the source data. You must curate, deduplicate, and select the most critical, actionable insights and tips from the raw extensions, up to the maximum limit specified in <max_extension_items>. Format them as objects in the `xai_highlights` array, ensuring each has an `extension_type` and `content` (which must be at most 2 sentences).</rule>\n"`
    - Place `<max_extension_items>{max_items}</max_extension_items>` inside the `<execution_parameters>` block in the system prompt.
    - In the return block of `text_consolidation_hook`, remove the blind Python slicing (`raw_highlights.extend(items[:max_items])`), and instead map `result.xai_highlights` directly from the LLM output:
      ```python
      raw_highlights = [h.model_dump(mode="json") for h in result.xai_highlights] if result.xai_highlights else []
      ```

---

## Verification Plan

### Automated Tests
- Create unit tests in `backend_v2/tests/unit/hooks/test_synthesis.py` to verify:
  1. Dynamic tone injection in global synthesis system prompt and row explanation prompt.
  2. Integration of `<raw_extensions>` block in the LLM user input.
  3. Curation of `xai_highlights` through `SynthesisOutputDTO` output mapping instead of Python slice.
- Run the backend audit loop:
  ```powershell
  uv run python scripts/backend_audit_loop.py backend_v2/hooks/synthesis.py --test
  ```

---

## Session Handover

To execute this plan iteratively, start a NEW chat session and run:
```powershell
/tier2-execute --target docs/epic/tasks_EPIC_85_Analysis_Refinements_and_XAI_Fixes/phase3_synthesis_hooks.md
```
