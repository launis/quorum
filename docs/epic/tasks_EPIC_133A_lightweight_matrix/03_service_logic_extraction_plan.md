# Phase 3: Service Logic Extraction & Duck-Typing Eradication

**Objective:** Strip `AnchorValidationService` and `AliasEngine` logic from DTO validators and move it entirely to the Service layer. Eradicate all `hasattr()`, `isinstance()`, and `.get()` duck-typing from DTOs.
**Source:** @[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix.md#L82-L107]

**Expected Target Files:**
- `@[c:\src\quorum\backend_v2\models\dtos\atom_evaluation.py]`
- `@[c:\src\quorum\backend_v2\services\orchestrator\anchor_validation_service.py]`
- `@[c:\src\quorum\backend_v2\models\enums.py]`
- Relevant test files.
