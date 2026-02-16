# Antigravity Gemini 3 Pro - Documentation Best Practices

This document outlines the hierarchy of project documentation and how to utilize it effectively with Gemini 3 Pro (Antigravity).

## 1. The Hierarchy

Documentation is organized into four distinct levels:

### Level 1: The Constitution
*   **File**: `docs/flutterpromptohje.md`
*   **Role**: **Single Source of Truth (SSOT)**.
*   **Content**: All architectural rules, banned patterns, coding styles, and strict mandates (e.g., Strict Nesting, English Only).
*   **Usage**: The AI (and human developer) MUST read this *always* before beginning work.

### Level 2: Context Injection (Gatekeepers)
*   **Files**: 
    *   `.cursorrules` (Cursor IDE)
    *   `.antigravity/rules.md` (Gemini Antigravity)
*   **Role**: "Gatekeeper".
*   **Content**: A high-level summary of critical rules and a **direct pointer** to Level 1.
*   **Usage**: These files are automatically loaded into the AI's context to enforce compliance with the Constitution.

### Level 3: Bootstrap Protocol
*   **File**: `docs/alku.md`
*   **Role**: "Session Initializer".
*   **Content**: Instructions for the AI on how to *start a new session* (which files to read, which modes to activate).
*   **Usage**: Instruct the AI to read this file at the start of every session ("Read docs/alku.md") to ensure correct context loading.

### Level 4: Execution & Pipeline Protocols
*   **Execution Protocol**: `docs/execution_protocol.md` (The "How-To").
    *   **Role**: Explicit instructions for the AI on converting an `implementation_plan.md` into strict code.
*   **Pipeline Reference**: `docs/output_generation_pipeline.md`.
    *   **Role**: Defines the data flow for specific subsystems (e.g., Report Generation).
*   **Template**: `docs/Execute ohje.md`.
    *   **Role**: "Feature Request Template" for the user to copy-paste.
*   **Usage**: The AI follows `execution_protocol.md` to execute the request defined in `Execute ohje.md`.

---

## 2. Best Practice Workflow (Gemini 3 Pro)

When initiating a new task ("Feature Request"):

1.  **Ensure Context**:
    *   Gemini 3 Pro automatically reads `.antigravity/rules.md`.
    *   Verify that it is also aware of `docs/flutterpromptohje.md` (request it to read the file if in doubt).

2.  **Define the Task (Prompting)**:
    *   Open `docs/Execute ohje.md`.
    *   Copy the preamble ("FEATURE REQUEST" block).
    *   Fill in the details of your request.
    *   Paste this structured prompt to Gemini.

3.  **Execution**:
    *   Gemini will follow the "UNIVERSAL MANDATE" in `Execute ohje.md` (which incorporates the latest strict rules).
    *   If Gemini suggests "flat data" or code that violates `flutterpromptohje.md`, the Gatekeepers (`.cursorrules` and `.antigravity/rules.md`) will flag the violation ("STRICT NESTING", "FAIL FAST").

## 3. Maintenance

*   **Update One Source**: If architecture changes, update `docs/flutterpromptohje.md` FIRST.
*   **Sync**: Ensure `.cursorrules` and `Execute ohje.md` reflect (or point to) these changes. (Synchronized as of Feb 13, 2026).
