# Phase 4: AST Hardening & Governance Lockdown

> **STATUS: DEFERRED** — This is a placeholder. Run `/tier0-create-plan @[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md] @[docs/epic/EPIC_150_tracker.md]` to generate the full implementation plan for this phase.

## Scope Summary

Harden the AST guardrail engine to `FATAL` severity for all non-test, non-exempt files. Create `ki_zero_permissive_typing.md` Knowledge Item. Synchronize architectural rules. Run full-stack verification.

## Target Files (~5 files)

- `@[scripts/_ast_guardrails.py]`
- `@[scripts/backend_audit_loop.py]`
- `@[.agents/rules/01-python-backend.md]`
- Knowledge Item: `ki_zero_permissive_typing.md` (NEW)
- Knowledge Item: `@[ki_ast_guardrail_engine.md]` (UPDATE)
