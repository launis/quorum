# EPIC 115 Phase 1.3: Workflow Pillar Count Fix

Source: Epic Phase 1, Task 1.3

## TARGET Files (Modify)
- @[c:\src\quorum\.agents\workflows\tier7-describe-architecture.md]

## CONTEXT Files (Read-Only)
- @[c:\src\quorum\.agents\rules\04_directory_reference.md]
- @[c:\src\quorum\docs\epic\EPIC_115_timeless_architecture_documentation.md]

## Proposed Changes

### .agents/workflows/tier7-describe-architecture.md
- [ ] Update all instances of "5 pillar" / "5 core capabilities" to "6 pillar" / "6 core capabilities". (There are 7+ occurrences scattered across `<architectural_invariants>` and `<execution_protocol>`).
- [ ] Use `multi_replace_file_content` to surgically replace them.

### .agents/rules/04_directory_reference.md
- [ALREADY_IMPLEMENTED] - Skip execution. Verified at: @[c:\src\quorum\.agents\rules\04_directory_reference.md#L111-L114]

## Testing & Quality Gate Plan
- Verify `tier7-describe-architecture.md` no longer contains "5 pillar" or "5 core capabilities" using `grep_search`.
