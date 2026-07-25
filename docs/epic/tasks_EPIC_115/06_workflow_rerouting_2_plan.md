# EPIC 115 Phase 2: Workflow Re-Routing (Part 2)

Source: Epic Phase 2, Task 2.4

## TARGET Files (Modify)
- @[c:\src\quorum\.agents\workflows\tier2-hardening-frontend.md]
- @[c:\src\quorum\.agents\workflows\tier4-bug-hunting.md]
- @[c:\src\quorum\.agents\workflows\tier5-session-handover.md]

## CONTEXT Files (Read-Only)
- @[c:\src\quorum\docs\epic\EPIC_115_timeless_architecture_documentation.md]

## Proposed Changes

- [ ] Ensure edits use `multi_replace_file_content`.
- [ ] Use the Standard Replacement Text for DOCUMENTATION & KI AUDIT as defined in Task 2.4 of the Epic.

### .agents/workflows/tier2-hardening-frontend.md
- [ ] [MODIFY] Update `<rule_block id="documentation_audit_mandate">` in `<context_rules>`. Replace `docs\architecture\` modification mandate with KI creation + Tier 7 delegation.

### .agents/workflows/tier4-bug-hunting.md
- [ ] [MODIFY] Update `<step id="7">` (DOCUMENTATION & KI AUDIT). Replace modification mandate with KI creation + Tier 7 delegation.

### .agents/workflows/tier5-session-handover.md
- [ ] [MODIFY] Update Step 2. Replace `docs\architecture\` verification with KI audit check.

## Testing & Quality Gate Plan
- Verify no execution workflow contains instructions to manually edit `docs\architecture\` pillar files.
