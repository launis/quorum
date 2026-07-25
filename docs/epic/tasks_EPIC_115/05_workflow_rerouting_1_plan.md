# EPIC 115 Phase 2: Workflow Re-Routing (Part 1)

Source: Epic Phase 2, Task 2.4

## TARGET Files (Modify)
- @[c:\src\quorum\.agents\workflows\tier2-execute.md]
- @[c:\src\quorum\.agents\workflows\tier3-feature-refactor.md]
- @[c:\src\quorum\.agents\workflows\tier2-hardening-backend.md]

## CONTEXT Files (Read-Only)
- @[c:\src\quorum\docs\epic\EPIC_115_timeless_architecture_documentation.md]

## Proposed Changes

- [ ] Ensure edits use `multi_replace_file_content`.
- [ ] Use the Standard Replacement Text for DOCUMENTATION & KI AUDIT as defined in Task 2.4 of the Epic.

### .agents/workflows/tier2-execute.md
- [ ] [MODIFY] Update `<step id="7">` (DOCUMENTATION AUDIT MANDATE). Replace `docs\architecture\` modification mandate with KI creation + Tier 7 delegation.

### .agents/workflows/tier3-feature-refactor.md
- [ ] [MODIFY] Update `<step id="6">` (DOCUMENTATION AUDIT MANDATE). Replace `docs\architecture\` modification mandate with KI creation + Tier 7 delegation.

### .agents/workflows/tier2-hardening-backend.md
- [ ] [MODIFY] Update `<constraint name="DOCUMENTATION AUDIT MANDATE">`. Replace `docs\architecture\` modification mandate with KI creation + Tier 7 delegation.

## Testing & Quality Gate Plan
- Verify no execution workflow contains instructions to manually edit `docs\architecture\` pillar files.
