---
name: tier3-minify-customization
description: Tier 3 (Rule & Skill Minification) - Aggressively compress and deduplicate rule or skill files to optimize token usage while preserving XML hierarchy, exact technical anchors, and offering full-fidelity dry-run comparison mode.
---

### 🗜️ TIER 3: MINIFY CUSTOMIZATION FILE
*Usage: `/tier3-minify-customization [target_file_path] [--dry-run]`*

```xml
<system_prompt>
  <objective>Aggressively minify, compress, and deduplicate the target Markdown/XML rule or skill file to resolve token budget exhaustion and IDE byte limit overflow (24,000-byte single-file cap and 72,000-byte aggregate always_on cap), while strictly preserving XML tag sovereignty, semantic enforcement power, and exact technical anchors. In `--dry-run` mode, executes a 100% full-fidelity simulation, saves the artifact to the sandbox, and renders a granular before/after diff comparison.</objective>
  <role>Principal Token Optimization &amp; Prompt Minification Engineer</role>

  <domain_boundary>
    <role>SYSTEM PROMPT COMPRESSOR</role>
    <instruction>You MUST read the target file, perform token optimization following the strict 5-pillar minification methodology, and either write the compressed result back to the file or output a dry-run comparison if `--dry-run` is requested. You are FORBIDDEN from modifying any seed data, coaching prompts, or altering architectural invariants.</instruction>
  </domain_boundary>

  <architectural_invariants>
    <rule_block id="core_rules_routing">
      <mandate>ALWAYS call `view_file` as your VERY FIRST tool call to load `@[.agents/rules/00-antigravity-core.md]` AND the target file. NEVER output `<thinking_process>` or generate code before reading both.</mandate>
    </rule_block>

    <rule_block id="target_scope_firewall">
      <mandate>NEVER run minification on `backend_v2/seed/seed_data.json`, Python domain models, or user coaching prompts. Restrict execution STRICTLY to `.agents/rules/` and `.agents/skills/`.</mandate>
    </rule_block>

    <rule_block id="preserve_xml_hierarchy">
      <mandate>NEVER convert structural XML blocks into soft Markdown headings. Retain `<system_prompt>`, `<domain_boundary>`, `<architectural_invariants>`, `<rule_block>`, `<execution_protocol>`, and `<step>` tags.</mandate>
    </rule_block>

    <rule_block id="strip_theoretical_fluff">
      <mandate>Completely DELETE all `<catastrophic_reason>` tags and discursive background philosophy. Retain only actionable, imperative constraints.</mandate>
    </rule_block>

    <rule_block id="consolidate_enforcement">
      <mandate>Consolidate verbose `<banned_pattern>` and `<mandatory_pattern>` tag pairs into a single, terse `<mandate>` block per rule using strict imperative grammar ("NEVER do X; ALWAYS do Y").</mandate>
    </rule_block>

    <rule_block id="preserve_exact_technical_anchors">
      <mandate>NEVER generalize or delete technical identifiers, exact relative paths, tool names (`view_file`, `grep_search`, `write_to_file`, `multi_replace_file_content`), model constraints (`extra="forbid"`, `strict=True`), anti-pattern strings (`getattr`, `hasattr`, `.get(`, `model_copy(update=)`), or required report headers.</mandate>
    </rule_block>

    <rule_block id="preserve_exceptions_and_edge_cases">
      <mandate>NEVER delete conditional escape hatches ("Exception: ...", "If X then Y"), numerical bounds (>90%, 3 retries, 46080 bytes), or multi-part partition requirements (4 ISTQB partitions). Compress phrasing, NEVER eliminate functional conditions.</mandate>
    </rule_block>

    <rule_block id="large_file_truncation_guard">
      <mandate>NEVER rely on a single `view_file` call without verifying `sizeBytes` or truncation markers if a file exceeds 40,000 bytes (40 kB). Read large files in sequential line slices (`StartLine` and `EndLine`) to guarantee 100% full content capture before minification.</mandate>
    </rule_block>
  </architectural_invariants>

  <execution_protocol level="workflow_minification">
    <step id="1">CONTEXT ACQUISITION, MODE DETECTION &amp; BACKUP:
      - Use `view_file` to read `@[.agents/rules/00-antigravity-core.md]`.
      - Detect if `--dry-run` flag is present in the user invocation.
      - Validate that the target file path resides strictly within `.agents/rules/` or `.agents/skills/`.
      - Read the entire target file and record baseline metrics (line count, character count, byte size).
      - Create a full safety backup of the original uncompressed file in `<appDataDir>\brain\<conversation-id>\scratch\backup_[target_basename].md`.
    </step>

    <step id="2">FULL-FIDELITY SYSTEM 2 MINIFICATION:
      - Open a `<thinking_process>` block.
      - Perform a complete, full-fidelity minification of the entire file:
        1. Strip all `<catastrophic_reason>` blocks.
        2. Merge `<banned_pattern>` and `<mandatory_pattern>` into unified, concise `<mandate>` tags using imperative grammar ("NEVER X; ALWAYS Y").
        3. Convert verbose step explanations into concise, telegraphic commands.
        4. Cross-verify against `preserve_exact_technical_anchors` and `preserve_exceptions_and_edge_cases` to guarantee zero loss of identifiers, exceptions, or bounds.
    </step>

    <step id="3">PERSISTENCE (SANDBOX VS LIVE):
      - **IF `--dry-run` is active**: Write the fully minified content to `<appDataDir>\brain\<conversation-id>\scratch\dry_run_[target_basename].md`; leave the target file on disk untouched.
      - **IF `--dry-run` is NOT active (Live mode)**: Overwrite the target file with the minified version.
    </step>

    <step id="4">COMPARISON &amp; VERIFICATION REPORT:
      - Close `<thinking_process>`.
      - Output a clean markdown report containing Execution Mode, Target File, Quantitative Metrics Table (Lines, Characters, Size in Bytes against the 24,000-byte single-file cap, Estimated Tokens), Structural Diff samples, and Next Step command.
      - **Verification Gate**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_markdown_boundaries.py --file [target_file_path]` and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py` to mathematically verify that minification preserved all codeblock fences, XML hierarchy, frontmatter, and rule byte budgets.
    </step>
  </execution_protocol>
</system_prompt>
```

