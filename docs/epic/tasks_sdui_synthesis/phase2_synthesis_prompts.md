# Epic SDUI Synthesis - Phase 2: Synthesis Prompts & Migration
Source: Epic Phase 2

Siirtymästrukturoituihin `content_blocks`-vastauksiin vaatii tiukan hybrid-promptingin sekä Graceful Degradation -logiikan listan purussa.

## Proposed Changes
### Backend V2 Orchestrator
#### [MODIFY] [synthesis.py](file:///c:/src/quorum/backend_v2/hooks/synthesis.py) (tai muu vastaava synteesikutsuja koordinoiva tiedosto)
- Rip-and-replace all usages of `synthesized_markdown` with `content_blocks`.
- Update the `run_structured_task` call to return the updated `SynthesisOutputDTO`.
- Add an explicit `<rule>` to the `_SYSTEM_INSTRUCTION`:
  - List allowed `block_type`s exclusively.
  - Ban recursion and nested blocks.
  - Ban markdown syntax inside texts.
  - Mandate `citations: list[int]` arrays instead of inline string brackets `[1]`.
- Enforce Hybrid Prompting logic: Keep all system instructions static. Dynamic variables go into the `<execution_parameters>` tag at the end to ensure 100% Context Caching efficiency.
- Graceful Degradation (DLQ Crash Protection): When unpacking `content_blocks`, use `try-except` on individual blocks to silently drop invalid blocks or replace them with a dummy AppErrorBoundary warning block, instead of crashing the whole report.

## Architectural Rules Implemented
- **Hardening Rule 29 & 51 (High Fidelity & Hybrid Prompting)**: Prompt core instructions MUST remain static, wrap dynamic params in `<execution_parameters>`.
- **Hardening Rule 17 (The Duct Tape Ban)**: Use proper `try...except` and re-raise or handle strictly, but do not hide errors.
- **Epic Constraint (Drop Bad Blocks)**: Fallback iteratively inside the list to protect the main process.

## Testing & Quality Gate Plan
### Integration Tests
- Run `uv run python scripts/backend_audit_loop.py backend_v2/hooks/synthesis.py --test`.

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_sdui_synthesis_tracker.md`
