# Implementation Plan: Epic 1 - Phase B & C (Pydantic Models & Security)

**Source**: `epic_structured_prompting.md` (Phase B & C)
**Epic Phase**: Pydantic Prompt -mallien määrittely & PEP 750 t-strings & TemplateProcessor

## 1. Goal
Extract prompt structures into strict Pydantic models. Replace insecure f-strings with a `TemplateProcessor` that uses `<![CDATA[...]]>` encapsulation to prevent XML Prompt Injection while maintaining 100% Verbatim extraction compatibility.

## 2. Files
**TARGET (Modify):**
- `c:\src\quorum\backend_v2\models\prompts\validation_prompts.py` (New file)
- `c:\src\quorum\backend_v2\core\template_processor.py` (New file/Modify existing)

**CONTEXT (Read-Only):**
- `c:\src\quorum\.agents\rules\00-antigravity-core.md`
- `c:\src\quorum\.agents\rules\01-python-backend.md`

## 3. Implementation Steps

### 3.1. Prompt Pydantic Models (Phase B)
- Create strict Pydantic models for prompts (e.g., `TdaValidationPrompt`) in the `prompts/` directory.
- Use `exclude_none=True` to drop empty fields.

### 3.2. TemplateProcessor & CDATA Encapsulation (Phase C)
- Build `TemplateProcessor` class to process Python 3.14 `Template` objects / f-strings.
- **CDATA Encapsulation:** User input must be automatically wrapped in `<![CDATA[{user_text}]]>`. Do NOT use HTML escaping (`<` to `&lt;`) because it breaks Track A verbatim extraction.
- **Breakout Shield:** To prevent the user from escaping the CDATA block, `safe_interpolate` MUST find the string `]]>` in the user input and safely replace it (e.g. with `] ] >` or `]]]]><![CDATA[>`).
- Migrate legacy f-string constructions to route through this `TemplateProcessor`.

## 4. Testing & Quality Gate Plan
- **Unit Tests:** `tests/unit/test_template_processor.py`. Verify that injected `<rule>` tags remain untouched inside the CDATA, but `]]>` strings are safely neutralized.
- **Hardening:** Run the Universal Quality Gate on the modified files:
  `uv run python scripts/backend_audit_loop.py c:\src\quorum\backend_v2\models\prompts`
  `uv run python scripts/backend_audit_loop.py c:\src\quorum\backend_v2\core`

---
### Session Handover
To execute this phase iteratively, start a NEW chat session and run:
`/tier2-execute --target docs/epic/tasks_structured_prompting/phase_b_and_c_pydantic_and_security.md`
