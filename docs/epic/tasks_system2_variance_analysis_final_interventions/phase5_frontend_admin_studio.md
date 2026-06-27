# Implementation Plan: Phase 5 - Frontend Admin Studio

## Goal
Expose the `contrastive_example` metadata field directly in the Admin Studio matrix claim/assertion editing form to allow system administrators to calibrate negative boundaries.

## Proposed Changes

---

### Component: Admin Studio Scale Editor Modal

#### [MODIFY] [scale_editor_modal.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart)
- **Changes**:
  - Add a new `TextFormField` for editing `tda.contrastiveExample` right after the anti-patterns field (around line 556):
    ```dart
    const SizedBox(height: 8),
    TextFormField(
      initialValue: tda.contrastiveExample,
      decoration: const InputDecoration(
        labelText: 'Contrastive Example (Correct vs Incorrect)',
        helperText:
            'Calibration examples: ACCEPTABLE: X affects Y. UNACCEPTABLE: X is associated with Y.',
        border: OutlineInputBorder(),
        contentPadding: EdgeInsets.symmetric(
          horizontal: 10,
          vertical: 8,
        ),
      ),
      maxLines: 2,
      onChanged: (newVal) {
        setState(() {
          final newTdas = List<TDAAssertion>.from(
            claim.tdaAssertions,
          );
          newTdas[tdaIdx] = tda.copyWith(
            contrastiveExample: newVal.trim().isEmpty
                ? null
                : newVal.trim(),
          );
          final newClaims =
              List<MatrixClaim>.from(
                _editableScale.claims,
              );
          newClaims[index] = claim.copyWith(
            tdaAssertions: newTdas,
          );
          _editableScale = _editableScale
              .copyWith(claims: newClaims);
        });
      },
    ),
    ```
  - *(Source: Epic Section 2.1)*

## Hardening Constraints
- **Localization Standards**: Verify if new label and helper texts are static administrative labels or if they require inclusion in Arb files. (As administrative tool labels, inline texts matching other fields are acceptable, but maintain consistency with surrounding code).

## Verification Plan

### Manual Verification
1. Open the Flutter client.
2. Navigate to Admin Studio -> PromptBlock editor.
3. Open a Matrix claim and edit assertions.
4. Verify the new "Contrastive Example" field is rendered, correctly pre-populated, editable, and saved back successfully.

### Automated Tests
Run frontend audit script to ensure no syntax errors exist:
```powershell
uv run python scripts/flutter_audit_loop.py client_app_v2
```

### Documentation Update
Update [docs/architecture/model_registry/frontend_implementation.md](file:///c:/src/quorum/docs/architecture/model_registry/frontend_implementation.md) to record the addition of the calibration contrastive field to the TDA modal.

## Session Handover
To execute this plan in the next session:
```powershell
/tier2-execute --target docs/epic/tasks_system2_variance_analysis_final_interventions/phase5_frontend_admin_studio.md
```
