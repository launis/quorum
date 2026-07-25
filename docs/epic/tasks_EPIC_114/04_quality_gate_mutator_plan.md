# Phase 4: SSOT Quality Gate Mutator

## User Review Required
No user review required.

## Open Questions
None.

## Proposed Changes

### c:\src\quorum\.agents\rules\

#### [MODIFY] [00-antigravity-core.md](file:///c:/src/quorum/.agents/rules/00-antigravity-core.md)
[ALREADY_IMPLEMENTED] - Skip execution. Verified at: @[c:\src\quorum\.agents\rules\00-antigravity-core.md#L216-L220]

### c:\src\quorum\.agents\workflows\

#### [MODIFY] [tier5-session-handover.md](file:///c:/src/quorum/.agents/workflows/tier5-session-handover.md)
[ALREADY_IMPLEMENTED] - Skip execution. Verified at: @[c:\src\quorum\.agents\workflows\tier5-session-handover.md#L28-L28]

#### [MODIFY] [tier6-execution-monitor.md](file:///c:/src/quorum/.agents/workflows/tier6-execution-monitor.md)
- **Source**: Epic Phase 4
- **TARGET (Modify)**: `@[c:\src\quorum\.agents\workflows\tier6-execution-monitor.md]`
- **Action**: Add explicit instruction to the `<execution_protocol>` or `architectural_invariants` indicating: "You MUST enforce ALL rule blocks in the `<universal_quality_gate>` section of `00-antigravity-core.md` — no rule block may be skipped." Specifically, update `<step id="1">` or `<rule_block id="core_rules_routing">` to ensure compliance routing is explicit, identical to the change made in tier5-session-handover.md.

## Verification Plan
### Automated Tests
- The rules files are markdown so unit tests don't apply.

### Testing & Quality Gate Plan
- Ensure that `tier6-execution-monitor.md` includes the exact required string.
