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

## 2. THE ABSOLUTE ZERO-COMPROMISE PLEDGE (NO DUCT-TAPE, NO LEGACY)
<architecture_bans>
### 2.1 The Duct-Tape Ban
<rule>You MUST NEVER write "duct-tape" code (purkkakoodi), shortcuts, or hasty fixes that merely patch symptoms. Returning empty arrays `[]`, default dicts `{}`, or hiding UI elements `SizedBox.shrink()` when real data goes missing is STRICTLY BANNED. Fix the root cause instead.</rule>

### 2.2 The No-Legacy Mandate
<rule>The system is a modern V2 Architecture. You MUST NEVER write code that maintains "backwards compatibility" with old V1 structures, deprecated APIs, or legacy databases. Obsolete code must be ruthlessly deleted and replaced.</rule>

### 2.3 Universal Explicit Fail-Fast
<rule>You MUST enforce the "Fail-Fast" paradigm at every boundary. If data does not precisely match the Pydantic V2 or Dart 3 Freezed schema, the system MUST crash audibly and visibly (`AppException` or `AppErrorBoundary`). Silent fallbacks are categorically banned.</rule>
</architecture_bans>

## 3. EDITING SAFETY

### 3.1 Anti-Duplication Protocol
When modifying a file, explicitly DELETE or OVERWRITE the old version. NEVER append the new version to the end of the file while leaving the old one intact.

## 4. OUTPUT FORMAT REQUIREMENTS

### 4.1 Language Strategy
Antigravity Prompts / Code Blocks MUST be in English. Explanations/Context MUST be in Finnish.

### 4.2 Internal Comments (The "Why" Mandate)
Only comment WHY business logic exists. Never explain WHAT the code mechanically does. Use Imperative Mood for docstrings.

## 5. QUALITY LOOP & TOOL USAGE (THE UNIVERSAL QUALITY GATE)

### 5.1 Backend Quality Gate (Python)
Commands MUST ALWAYS be given in this explicit format, listing the exact files (no wildcards) with `backend_v2/` path prefix from the project root, and using `;` instead of `&&`:
`uv run ruff check backend_v2/[tiedostot] --fix ; uv run mypy backend_v2/[tiedostot] --strict`
If modifying Pydantic models or Router schemas, you MUST also instruct the user to sync the API documentation:
`uv run python backend_v2/scripts/generate_openapi.py`

### 5.2 Frontend Quality Gate (Flutter/Dart)
The frontend verification follows a strict order of native tools:
1. **Clean & Analyze (Always):** `dart format . ; dart analyze`
2. **Generators (If `@riverpod` or `@freezed` models changed):** `dart run build_runner build --delete-conflicting-outputs`
3. **Localization (If `.arb` files or No-Strings constants were changed):** `flutter gen-l10n`

### 5.3 Zero-Deprecation Mandate
You MUST resolve ALL syntax errors, typing errors, AND deprecation warnings (e.g., `deprecated_member_use`) before declaring the step complete. Code with deprecated APIs is considered broken. Proactively replace deprecated members with their modern equivalents.

## 6. TESTING MANDATE

### 6.1 Universal Testing & TDD
Whenever code is changed, refactored, or new features are added, you MUST ALWAYS write new automated tests OR fix existing old tests for both the Flutter and Python sides. 
- **Backend Test Command:** `uv run pytest backend_v2/tests/ -v`
- **Frontend Test Command:** `flutter test`
Test-Driven Development (TDD) applies: When fixing bugs, you MUST write a failing test that reproduces the bug BEFORE fixing the domain code. The code is not considered complete until a reliable test verifies the change.