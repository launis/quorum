---
trigger: always_on
description: Global Antigravity Protocol and Agent Behavior
globs: *
---

# 🚀 ANTIGRAVITY COMMAND CENTER

> [!IMPORTANT]
> ANTIGRAVITY IDE PROTOCOL (STRICT ORCHESTRATION):
> 1. You are operating natively in the Antigravity IDE under a strict PERMISSION GRANTED workflow.
> 2. AI Agents inherently want to auto-execute and rush tasks. YOU MUST RESIST THIS. When instructed to PLAN, or after completing a SINGLE STEP in a plan, you MUST STOP. 
> 3. DO NOT auto-generate or modify the next files until the user explicitly says "PERMISSION GRANTED" or "PROCEED".
> 4. ANTI-APOLOGY PROTOCOL: If you violate a rule, DO NOT apologize. Acknowledge the error briefly and output the fixed code immediately.

## 1. ANTI-HALLUCINATION & FILE SCOPING PROTOCOL

### 1.1 Read-Before-Write
NEVER guess the contents of a file. Use your tools to read the current context before proposing modifications.

### 1.2 Explicit Scope
Only modify `TARGET` files. Treat `CONTEXT` files as Read-Only.

## 2. EDITING SAFETY

### 2.1 Anti-Duplication Protocol
When modifying a file, explicitly DELETE or OVERWRITE the old version. NEVER append the new version to the end of the file while leaving the old one intact.

## 3. OUTPUT FORMAT REQUIREMENTS

### 3.1 Language Strategy
Antigravity Prompts / Code Blocks MUST be in English. Explanations/Context MUST be in Finnish.

### 3.2 Internal Comments (The "Why" Mandate)
Only comment WHY business logic exists. Never explain WHAT the code mechanically does. Use Imperative Mood for docstrings.

## 4. QUALITY LOOP & TOOL USAGE

### 4.1 Python Linting
Commands MUST ALWAYS be given in this explicit format, listing the exact files (no wildcards) with `backend_v2/` path prefix from the project root, and using `;` instead of `&&`:
`uv run ruff check backend_v2/__init__.py backend_v2/worker.py backend_v2/settings.py backend_v2/main.py backend_v2/logging_config.py backend_v2/run_worker.py backend_v2/exceptions.py backend_v2/context.py --fix ; uv run mypy backend_v2/__init__.py backend_v2/worker.py backend_v2/settings.py backend_v2/main.py backend_v2/logging_config.py backend_v2/run_worker.py backend_v2/exceptions.py backend_v2/context.py --strict`

### 4.2 Flutter Linting
Run `dart format` -> `dart analyze` -> `flutter test`.

### 4.3 Zero-Deprecation Mandate
You MUST resolve ALL syntax errors, typing errors, AND deprecation warnings (e.g., `deprecated_member_use`) before declaring the step complete. Code with deprecated APIs is considered broken. Proactively replace deprecated members with their modern equivalents.

## 5. TESTING MANDATE

### 5.1 Universal Testing
Whenever code is changed, refactored, or new features are added, you MUST ALWAYS write new automated tests OR fix existing old tests for both the Flutter and Python sides. The code is not considered complete until a reliable test verifies the change.