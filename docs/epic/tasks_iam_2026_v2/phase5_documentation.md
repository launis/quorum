# Phase 5: Architecture Documentation Update

**Source:** Tier 1 Mandate (Documentation Update)
**Objective:** Update the global architecture documentation with the new 2026 IAM patterns.

## 🛑 Architectural Invariants (From .agents/rules)
* **Rule 1:** Keep documentation accurate and reflective of the strict Pydantic V2 mandates.

## 🎯 Target Scope
* **TARGET (Modify):** `docs/architecture/unified_backend_architecture_and_standards.md` (or equivalent IAM doc)

## 🛠️ Implementation Steps

### 1. Update IAM Documentation
* Add sections detailing the Token Exchange flow (Firebase -> Local JWT).
* Add documentation on the CacheService abstraction (Local Dict vs Prod Redis) and Kill-Switch.
* Document the TinyDB Python-level isolation vs PostgreSQL RLS strategy.

## 🧪 Testing & Quality Gate Plan
* No code tests required. Manual review of markdown output.

---
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/iam_2026_v2_tracker.md`
