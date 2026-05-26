# Epic 61 Master Tracker: Evaluation Directives Hardening & Vice Rules Operationalization

This tracker monitors the phased implementation of Epic 61 to enforce syntactic anchoring, zero-trust null filtering, and deterministic prompt engine hardening.

## Active Sub-plans
- [OK] [phase1_tda_hardening.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_61/phase1_tda_hardening.md) - Rewrite the 5 unstable TDA assertions with explicit syntactic anchors, step-by-step logic, and ambiguity protocols. Run database seeding.
- [OK] [phase2_prompt_engine.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_61/phase2_prompt_engine.md) - Update global prompt directives in `system_directives.py` and the blind extraction prompt in `prompt_compiler.py` with zero-trust negative condition rules.
- [OK] [phase3_verification_loop.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_61/phase3_verification_loop.md) - Write unit/integration tests, run consistency audits, execute the backend audit loop, and update architecture documentation.

## Universal Hardening Loop Mandate
When all modified files are completed, the user must run:
```powershell
/tier2-hardening-backend
```
to audit PEP 257 standards and complete the Quality Gate verification.

---

## Handover Instructions
To start the execution loop:
1. Open a fresh context window.
2. Run command: `/tier5-resume --target docs/epic/EPIC_61_tracker.md`
