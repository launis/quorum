# Epic Tracker: component.py Decomposition

This tracker orchestrates the Strangler Fig extraction of `backend_v2/database/repositories/component.py` into the `components/` subdirectory, following the Tier 3 Zero-Loss Parity protocol.

## Execution Checklist

- [x] `[BASELINE]` **Pre-Flight Parity Metric**: 20 tests passed, 32.06% coverage.
- [x] `[NOK]` **Phase 1: PromptBlock Extraction**: Move/Merge PromptBlock logic from God Code into `components/prompt_block.py`. Implement Import Proxies if needed.
- [x] `[NOK]` **Phase 2: Agent Extraction**: Move/Merge Agent logic into `components/agent.py`.
- [x] `[NOK]` **Phase 3: TaskBlueprint Extraction**: Move/Merge Blueprint logic into `components/task_blueprint.py`.
- [x] `[NOK]` **Phase 4: OutputProfile Extraction**: Move/Merge OutputProfile logic into `components/output_profile.py`.
- [x] `[NOK]` **Dependency Rewiring & Cleanup**: Perform codebase-wide search and replace for old import paths. Once all DI paths are updated, remove the proxy methods from the original God Code.
- [x] `[NOK]` **Pre-Delete Audit**: Verify no orphaned dependencies or legacy fixtures remain.
- [x] `[NOK]` **Hardening Audit**: Run `/tier2-hardening-backend` on the `backend_v2/database/repositories/` directory.
- [x] `[NOK]` **Baseline Parity Verification**: Re-run the full backend test suite to confirm zero loss of functionality. verify that the final test count and coverage match or exceed the `[BASELINE]` metric recorded above.

## Instructions for the Execution Agent
- You MUST update the `--achieved` parameter of the `/tier5-resume` command below after completing any phase.
- Do NOT delete the old files until the "Dependency Rewiring & Cleanup" task is explicitly executed.
- Enforce the Zero Behavioral Change Mandate.

---

## Session Handover

To execute this Epic iteratively, start a NEW chat session and run the following command:

```text
/tier5-resume --workflow=/tier2-execute --target="docs\epic\component_decomposition_tracker.md, c:\src\quorum\backend_v2\database\repositories\component.py" --achieved="Generated Tier 3 Tracker and baseline planning." --learned="Need to use Import Proxy Pattern to avoid DI breakages. Logic is fragmented between God Code and standalone files." --remaining="[Execute Baseline, Phase 1 to 4, Rewiring, Parity Audit]" --rules=".agents/rules/00-antigravity-core.md, .agents/rules/01-python-backend.md"
```
