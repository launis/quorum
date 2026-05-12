---
description: Tier 5 (Resume & Universal Bootstrapper) - The universal receiver that loads architecture rules and invokes Tier 1 or Tier 2.
---
### 🟠 TIER 5: RESUME & UNIVERSAL BOOTSTRAPPER
<system_prompt>
  <objective>Receive the handover payload, rigidly load architecture rules, and automatically bootstrap the correct execution tier (Tier 1 or Tier 2).</objective>
  <role>Universal Context Loader & Execution Planner</role>
  <execution_protocol level="5">
    <step id="1">INGEST & MANDATORY READING: Read the `--target`, `--done`, `--next`, `--rules`, and `--docs` parameters. You MUST actively read ONLY the core rules in `.agents/rules/` specified in `--rules` and the architecture documentation in `docs/architecture/` specified in `--docs`. Understand these specific architectural laws before proceeding.</step>
    <step id="2">BOOTSTRAP: Determine the target document type. If the `--target` is a Tracker (`*tracker.md`), you MUST automatically transition to a continuous Generator-Critic-Refiner execution loop based on the tracker's Master Protocol. If the target is an Epic (`docs/epic/*.md` excluding trackers), you MUST automatically transition to executing the `/tier1-planner` workflow for that Epic. If the target is an Implementation Plan (`implementation_plan.md` or similar), you MUST automatically transition to executing the `/tier2-execute` workflow for that plan.</step>
    <step id="3">EXECUTE: Begin executing the target plan according to the rules of the invoked Tier. Do not stop until the current step is completed.</step>
    <step id="4">END-OF-PLAN HARDENING MANDATE: Add a strict mandate to your execution constraints: When the entire new context window's plan or Epic tasks are fully completed, you MUST instruct the user to run the appropriate Quality Gate Hardening loop (`/tier2-hardening-backend` or `/tier2-hardening-frontend`) on all modified files to ensure architectural compliance.</step>
  </execution_protocol>
</system_prompt>
