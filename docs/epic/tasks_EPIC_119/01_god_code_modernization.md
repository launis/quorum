# Phase 1: Modernize God Code Decomposition

This plan implements Phase 1 of Epic 119: standardizing the Tier 3 God Code workflow to use the Hybrid XML Sandwich architecture and reinforcing context quarantine.

**Source**: Epic 119, Phase 1

### Target Files
- TARGET (Modify): `@[c:\src\quorum\.agents\workflows\tier3-god-code-decomposition.md]`

### Execution Instructions
```xml
<execution_protocol>
  <step id="1" name="VERIFY CODEBASE STATE">
    <action>Perform a Pre-Flight Codebase Scan. Use `grep_search` to check if `HYBRID_XML_SANDWICH_MANDATE` or similar rules have already been added to `tier3-god-code-decomposition.md`.</action>
    <action>If already implemented, skip to the next step or mark this plan complete.</action>
  </step>
  
  <step id="2" name="INJECT HYBRID XML SANDWICH MANDATE">
    <action>Modify `tier3-god-code-decomposition.md`. In `<step id="3" name="PHASE 2 (Micro-Chunking &amp; Lazy Plan Generation)">`, add a new `<constraint>` that enforces the HYBRID_XML_SANDWICH_MANDATE.</action>
    <action>The constraint must explicitly require that generated `phaseX_extraction.md` files wrap their step-by-step instructions in `<execution_protocol>` XML blocks inside fenced ```xml ``` codeblocks, exactly matching the format produced by `tier0-create-plan`.</action>
    <constraint invariant="surgical_precision_edits">You must use surgical edits to inject the constraint cleanly.</constraint>
  </step>
  
  <step id="3" name="REINFORCE SESSION HANDOVER">
    <action>Update `<step id="5" name="PHASE 4 (Embedded Handover Context)">` and `<step id="6" name="PHASE 5 (Stop &amp; Present)">`.</action>
    <action>Ensure the instructions strictly reinforce that the agent MUST stop and instruct the user to execute the plans in a fresh context window using the `/tier5-resume --workflow=/tier2-execute` command.</action>
  </step>
  
  <step id="4" name="TESTING & QUALITY GATE PLAN">
    <action>Run the `backend_audit_loop.py` script to verify no generic repository corruption occurred.</action>
    <action>Verify that `tier3-god-code-decomposition.md` parses cleanly as Markdown and the XML tags are well-formed.</action>
  </step>
</execution_protocol>
```
