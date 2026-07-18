# EPIC 102: Structured Provenance & Context Segregation - Tracker

## Instructions for the Execution Agent
- You MUST strictly follow the execution order.
- Before handing over the session, you MUST update the `/tier5-resume` command in the `# Session Handover Context` block at the bottom of this file.

## Execution Tracker
- [OK] Phase 1: Execute `docs\epic\tasks_EPIC_102_structured_provenance\01_intra_chat_segregation.md`
- [OK] Run `/tier0-research-plan` on Phase 2's plan in a fresh context window to Red-Team the architecture before execution.
- [OK] Phase 2: Execute `docs\epic\tasks_EPIC_102_structured_provenance\02_inter_source_segregation.md`
- [OK] Invoke the Tier 1 Planner again to generate detailed plans for the remaining phases based on the updated codebase state.
- [OK] Run `/tier0-research-plan` on Phase 3's plan to Red-Team and fix Pre-Flight Provenance fuzzy bypass.
- [OK] Phase 3: Execute `docs\epic\tasks_EPIC_102_structured_provenance\03_physical_anchoring.md`
- [NOK] Proxy Sunset & Consumer Migration
- [NOK] Tier 2 Hardening
- [NOK] Pre-Delete Audit
- [NOK] Semantic Coverage & Zero-Loss Audit

## Requirements Traceability Matrix
| Requirement | Addressed In |
|-------------|--------------|
| Intra-chat Role Segregation (AI vs User XML Tags) | Phase 1 (01_intra_chat_segregation.md) |
| Inter-source Segregation ($inputs vs $steps) | Phase 2 (02_inter_source_segregation.md) |
| Prevent Nested Provenance Trap for Chat Logs | Phase 2 (02_inter_source_segregation.md) |
| Global Directives XML Fencing and Prompt Injection | Phase 2 (02_inter_source_segregation.md) |
| Pre-Flight Provenance Check for Physical Anchoring | Phase 3 Placeholder (03_physical_anchoring.md) |

# Session Handover Context

### Achieved
- Broken down Epic 102 into micro-chunked execution plans focusing on structural separation of LLM context.
- Analyzed existing inputs processor and compiler mechanisms.
- Established Phase 1 and Phase 2 implementation plans.
- Executed Phase 1 (Intra-Chat Segregation) in `input_processing.py`.
- Executed Tier 0 (Research & Analysis) on Phase 2 plan to Red-Team architecture, removing SSOT violations and enforcing testing.
- Executed Phase 2 (Inter-Source Segregation & Global Directives) in `global_mandates.py` and `prompt_compiler.py`.
- Invoked Tier 1 Planner to generate the detailed plan for Phase 3 (Physical Anchoring).
- Executed Tier 0 (Research & Analysis) on Phase 3 plan, fixing critical Pre-Flight fuzzy matching bypass and SSOT duplication.
- Executed Phase 3 (Physical Anchoring) using Tier 2. Added Pre-Flight Provenance check to `AnchorValidationService` preventing quotes from escaping the `<user_payload>` tags.

### Learned
- `ChatHistoryDTO` is already stable and handles processing inside `input_processing.py`.
- Need to bypass NLP runs for pipeline chained JSON outputs in `input_processing.py`.
- `global_mandates.py` is injected globally via `prompt_compiler_adapter.py`. We must modify `GLOBAL_MANDATES_XML` directly to enforce SSOT, bypassing `localization_compiler.py`.
- CDATA encapsulation is done by `TemplateProcessor.encapsulate_payload(value)`. The structural tags `<user_payload>` must wrap this output, not sit inside it.
- `ExpectedInput` supports `is_chat_history`, allowing dynamic provenance segregation in the `prompt_compiler` `build_xml_context`.
- `AnchorValidationService.validate_evidence` requires a Pre-Flight Provenance check to preserve `index_map` offsets for exact physical highlighting on PDFs.
- Fuzzy matching allows skipping validation if strictness allows it. We moved fuzzy matching to a static helper to keep the provenance gate fully unified.

### Remaining
- Proxy Sunset & Consumer Migration
- Tier 2 Hardening
- Pre-Delete Audit
- Semantic Coverage & Zero-Loss Audit

To execute this Epic iteratively, start a NEW chat session and run the following command:

`/tier1-planner --target="docs\epic\EPIC_102_structured_provenance.md, docs\epic\EPIC_102_structured_provenance_tracker.md" --rules=".agents\rules\00-antigravity-core.md, .agents\rules\01-python-backend.md"`
