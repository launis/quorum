# Protocol: Executing Implementation Plans (V1.0)

## Overview

This protocol defines the standard procedure for converting a planned `implementation_plan.md` into executed code using the strict mandates of `docs/Execute ohje.md`.

## The Goal

To execute a plan **atomically**, **safely**, and **strictly**, ensuring that every step adheres to the project's zero-compromise architecture (no fallbacks, strict types, full parity).

---

## 1. Prerequisites

Before starting execution, ensure you have:
1.  **Approved Plan**: A finalized `implementation_plan.md` in the artifacts folder.
2.  **The Instructor**: The file `docs/Execute ohje.md` (The "Ohje").

---

## 2. The Execution Command

To trigger this process efficiently, provide the AI with the following instruction:

> "Execute the approved **Implementation Plan** step-by-step. For each step, strictly follow the architectural mandates defined in `docs/Execute ohje.md`. Treat each plan item as a 'Feature Request' under that protocol. Do not ask for confirmation between steps unless a critical issue arises. Confirm after each step that you have used `docs/Execute ohje.md` and explain after each step how was the guideline followed."

---

## 3. The Process (for the AI)

The AI will perform the following loop for each item in the Implementation Plan:

1.  **Read Context**:
    -   Read the specific item from `implementation_plan.md`.
    -   Re-read `docs/Execute ohje.md` (mentally or explicitly) to refresh constraints.

2.  **Apply Constraints**:
    -   **Strict Typing**: Ensure no `dict` outputs, only Pydantic models.
    -   **No Fallbacks**: If data is missing, raise an error (Fail Fast).
    -   **Dual Impl**: If touching DB, update both TinyDB and Firestore repositories.

3.  **Execute**:
    -   Writes the code.
    -   Runs the verification (Lint/Test).

4.  **Mark Complete**:
    -   Updates `task.md` (and `implementation_plan.md` checklists).

---

## 4. Why this works?

-   **Separation of Concerns**: The *Plan* defines **WHAT** to do. The *Ohje* defines **HOW** to do it (Quality Standards).
-   **Reproducibility**: By referencing `Execute ohje.md` every time, we ensure that code written on Day 1 and Day 100 follows the same strict standards.
