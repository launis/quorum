# Phase 3: Context Quarantine for Bug Hunting

This plan implements Phase 3 of Epic 119: enforcing strict context quarantine for the Tier 4 Bug Hunting workflow, separating RCA from the bug fix execution.

**Source**: Epic 119, Phase 3

### Target Files
- TARGET (Modify): `@[c:\src\quorum\.agents\workflows\tier4-bug-hunting.md]`

### Execution Instructions
```xml
<execution_protocol>
  <step id="1" name="VERIFY CODEBASE STATE">
    <action>Perform a Pre-Flight Codebase Scan on `tier4-bug-hunting.md`. Check if `rca_quarantine_mandate` is already present.</action>
  </step>
  
  <step id="2" name="ADD RCA QUARANTINE MANDATE">
    <action>Modify `tier4-bug-hunting.md`. Add a new `<rule_block id="rca_quarantine_mandate">` to `<architectural_invariants>`.</action>
    <action>The mandate must state that the RCA session (Steps 1-3: identification, regression test writing, and proof of failure) stays in the current session. The actual fix MUST be deferred to a fresh session executing `tier2-execute`.</action>
    <constraint invariant="surgical_precision_edits">Use surgical edits.</constraint>
  </step>

  <step id="3" name="MODIFY BLAST RADIUS & GENERATE PLAN">
    <action>Modify `<step id="4">` (BLAST RADIUS ANALYSIS & THE 5 WHYS).</action>
    <action>Append an instruction: After the 5 Whys analysis and blast radius mapping, the agent MUST generate a `bug_fix_plan.md` Artifact using the XML Sandwich format, containing the precise fix instructions, `@-referenced` target files, and architectural constraints.</action>
  </step>
  
  <step id="4" name="IMPLEMENT QUARANTINE HANDOVER AND DELETE OLD STEPS">
    <action>EXPLICITLY DELETE the old Step 5 (`FIX & VERIFY (GREEN)`), Step 6 (`END-TO-END SMOKE TEST`), and Step 7 (`DOCUMENTATION & KI AUDIT`) from the workflow.</action>
    <action>Add a new `<step id="5" name="QUARANTINE HANDOVER">` that halts execution and provides a `/tier5-resume --workflow=/tier2-execute` command pointing to the generated plan artifact.</action>
    <action>Ensure the existing "ATOMIC INTERFACE EXCEPTION" in Step 2 is explicitly retained in the workflow text.</action>
  </step>
  
  <step id="5" name="TESTING & QUALITY GATE PLAN">
    <action>Run the Universal Quality Gate to ensure global repo health.</action>
    <action>Verify `tier4-bug-hunting.md` XML formatting is completely intact.</action>
  </step>
</execution_protocol>
```
