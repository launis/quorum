# Phase 0: Seed Data & Database Prerequisite

## Overview
Ensure the database is cleanly re-seeded without legacy definitions causing test failures, and record baseline metrics before legacy purges begin.

## Target Files
- `@[c:\src\quorum\backend_v2\seed\run_seed.py]` (Context)
- `@[c:\src\quorum\backend_v2\seed\seed_data.json]` (Context)

```xml
<execution_protocol level="2_execute">
  <constraint invariant="seeding_command_mandate">If you instruct the execution agent or the user to run the database seed script, you MUST explicitly include the target environment argument.</constraint>
  <constraint invariant="zero_omission_for_existing_code">Every requirement from the Epic MUST appear in the plans.</constraint>
  
  <step id="1" name="RUN DATABASE SEEDING">
    <action>Execute the database seed script to establish a clean, pristine state before legacy purges.</action>
    <command>uv run python backend_v2/seed/run_seed.py local</command>
  </step>

  <step id="2" name="RECORD BACKEND BASELINE">
    <action>Run the backend audit loop to ensure the pristine state passes tests and record the baseline coverage.</action>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/ --test</command>
  </step>
  
  <step id="3" name="RECORD FRONTEND BASELINE">
    <action>Run the flutter test suite to establish a pristine frontend state baseline.</action>
    <command>dart run test</command>
  </step>

  <step id="4" name="TESTING STRATEGY & QUALITY GATE PLAN">
    <action>Verify that all baseline tests pass with a 100% success rate. The baseline must be established before moving to Phase 1.</action>
    <action>If baseline tests fail, DO NOT proceed. The environment must be fixed before structural refactoring begins.</action>
  </step>
</execution_protocol>
```
