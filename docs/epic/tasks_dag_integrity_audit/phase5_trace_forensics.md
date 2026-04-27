# Phase 5: Empiirinen Jäljitettävyys (Execution Trace)

## Tavoite
Rakentaa tai hyödyntää diagnostinen Python-skripti, joka auditoi pytjon kutsussa annettavan `execution_trace.json` -tiedoston vahvistaen, että `prompt_tokens` korreloi kaikkien askelten syötteiden kanssa, ja data virtaa ehjänä alusta loppuun.

## Arkkitehtuurin Invariantit
- Rule 1: **Temporary Workspace Sandbox**: All temporary debug scripts must be written to `c:\src\quorum\tmp\`. NEVER inside core architectural directories.
- Rule 2: **Data Leak Prevention**: Scripts must not output PII directly into logs.

## Tiedostot (Scoping)
- **TARGET**: `tmp/audit_execution_trace.py` (New diagnostic script)
- **CONTEXT**: `data/files/executions/*`

## Työkalut & Verify Plan
- `python tmp/audit_execution_trace.py`

## Tilanne
- [x] COMPLETE: Diagnostinen skripti luotu osoitteeseen `tmp/audit_execution_trace.py`.

