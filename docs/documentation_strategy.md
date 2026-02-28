# Documentation Strategy (V5.1 / Phase 9 Hardening)

This document outlines the hierarchy of project documentation and the "Living Documentation" strategy for Gemini 3 Pro (Antigravity).

> [!IMPORTANT]
> **Living Documentation Mandate**
> Documentation is NOT a static artifact. It must be updated **simultaneously** with code changes. If you refactor a component, you MUST update its documentation (`components.md`, `data_management.md`, etc.) in the same session.

---

## 1. The Hierarchy

Documentation is organized into four distinct levels:

### Level 1: The Constitution
*   **File**: `docs/flutterpromptohje.md`
*   **Role**: **Single Source of Truth (SSOT)**.
*   **Content**: All architectural rules, banned patterns, coding styles (Fail Fast, English Only, Strict Pydantic).
*   **Usage**: The AI (and human developer) MUST read this *always* before beginning work.

### Level 2: Strategic Context
*   **File**: `docs/product_roadmap.md`
*   **Role**: **Feature Authority**.
*   **Content**: Defines *what* we are building and *why*. Contains the "Immediate Execution Priority".
*   **Usage**: Use this to align technical implementation with business goals.

### Level 3: Architectural Reference
*   **Files**:
    *   `docs/components.md`: Detailed breakdown of Agents, Hooks, and Services (Registry, Engine).
    *   `docs/data_management.md`: Data flow, persistence, seeding, and strict typing rules (Phase 9).
    *   `docs/output_generation_pipeline.md`: The rendering pipeline (Agent -> BFF -> Report).
    *   `docs/api_models.md`: The strict Pydantic definitions and DTO contracts.
*   **Role**: "System Maps".
*   **Usage**: Consult these when modifying system components to ensure you don't break existing contracts.

### Level 4: Execution Protocols
*   **File**: `docs/execution_protocol.md`
*   **Role**: "The How-To".
*   **Content**: Step-by-step instructions for converting requirements into code.

---

## 2. The Artifact-First Workflow

Gemini 3 Pro operates on an "Artifact-First" basis to ensure transparency and recoverability.

### 1. The `task.md` (The Checklist)
*   **Location**: `<appDataDir>/brain/<conversation-id>/task.md`
*   **Role**: Tracks granular progress.
*   **Rule**: Every major step must be checked off (`[x]`) as it is completed.

### 2. The `implementation_plan.md` (The Design Doc)
*   **Location**: `<appDataDir>/brain/<conversation-id>/implementation_plan.md`
*   **Role**: Defines the technical approach BEFORE code is written.
*   **Rule**: Must be approved (or implicitly accepted) by the user before `EXECUTION` mode begins.

### 3. The `walkthrough.md` (The Proof)
*   **Location**: `<appDataDir>/brain/<conversation-id>/walkthrough.md`
*   **Role**: Demonstrates verification.
*   **Rule**: Must include evidence (logs, screenshots, test results) that the changes work.

---

## 3. Best Practice Workflow (Gemini 3 Pro)

When initiating a new task:

1.  **Plan**:
    *   Read `docs/product_roadmap.md` and `docs/components.md`.
    *   Create `implementation_plan.md`.
    *   Create `task.md`.

2.  **Execute**:
    *   Follow the plan.
    *   **Fail Fast**: If a strict rule is violated (e.g., dictionary passing), stop and fix it immediately.
    *   **Refactor Documents**: As you code, update the relevant `docs/*.md` files. This is not optional.

3.  **Verify**:
    *   Run tests/scripts.
    *   **Seeding Validation**: If enhancing data, run `verifier.py` or `run_seed.py` to prove SSOT integrity.
    *   Create `walkthrough.md`.

---

## 4. Specific Documentation Protocols (Phase 9)

### 4.1. Error Documentation (RFC 7807)
*   **Location**: `docs/flutterpromptohje.md` (Contract) and `backend/exceptions.py` (Implementation).
*   **Rule**: All new error conditions must map to a specific `ErrorCode`. Generic `500` errors are forbidden for known states.

### 4.2. Component Registry
*   **Location**: `docs/data_management.md`.
*   **Context**: Code (`Agent`) is separate from Content (`Component`).
*   **Rule**: Documentation must clarify whether a change is Logic (Code) or Configuration (DB/Seed).

### 4.3. Type Safety
*   **Location**: `docs/data_management.md`.
*   **Rule**: All Agent inputs/outputs are strictly typed Pydantic models. Documentation examples must reflect this `BaseAgent[InputT, OutputT]` pattern.

---

## 5. Maintenance

*   **Update One Source**: If architecture changes, update `docs/flutterpromptohje.md` FIRST.
*   **Sync**: Ensure `.cursorrules` and `Rules.md` reflect (or point to) these changes.
