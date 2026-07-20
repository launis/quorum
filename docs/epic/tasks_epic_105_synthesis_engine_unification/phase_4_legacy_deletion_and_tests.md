# Phase 4: Legacy Deletion & Test Migration

> **Source**: Epic 105, Phase 3 + Phase 5 — Deletion of Legacy Strategy + Automated Testing
> **Status**: PLACEHOLDER — Will be detailed by Tier 1 Planner after Phase 2 completion.

## Goal

1. Delete `pre_hydrated_synthesis.py` and remove from `strategies/__init__.py`.
2. Create comprehensive `test_synthesis_engine.py` in isolation.
3. Port relevant test logic from any synthesis-related test files.
4. Update `test_dag_executor*.py` tests to reflect the new factory registry pattern.
