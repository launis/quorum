# Quorum V2 Architecture Enhancement: Strictness Matrix Scaling

## Background
Currently, the 5-Level Strictness Framework in Quorum is handled primarily via a generic instruction on the `PromptBlock` execution layer. This translates to system prompt logic (e.g. "Be very strict"). 

However, as highlighted during the Bloom/Toulmin JSON evaluation, adjusting "strictness" often bleeds into the localization keys. Developers end up overloading the English (`en`) versus Finnish (`fi`) `claims` text directly to force harsher criteria (e.g., using "Catastrophic failure. UNACCEPTABLE HUBRIS" in English to simulate a Level 5 Zero-Trust model, while keeping the Finnish translation milder).

## The Problem
Overloading localization keys for strictness scaling creates several architectural problems:
1. **Subjective AI Evaluation:** Telling an LLM to simply "be stricter" relies on its opaque internal tuning. It does not provide objective auditability.
2. **Translation Asymmetry:** `fi` and `en` locales should mean the exact same thing. Using one for a "Strict" fallback breaks the I18N mandate.
3. **Loss of Forensic Sovereignty:** An auditor cannot see exactly *what* structural requirement caused a failure, only that the AI felt it should be strict.

## Proposed Solution: The Targeted Claims Architecture

Instead of generic strictness logic, we will bind the strictness directly to the exact matrix requirements (`claims`) by versioning the `MatrixScale` model to support scalable criteria.

### Schema Transformation

**CURRENT (V2.0):**
```json
{
  "score": 1,
  "name": { "fi": "Ylimielinen" },
  "claims": [
    { "fi": "Teksti esittää asiat faktaan pohjautuen." }
  ]
}
```

**PROPOSED (V3 Concept):**
```json
{
  "score": 1,
  "name": { "fi": "Ylimielinen" },
  "claims": {
    "1": [
      { "fi": "Teksti esittää omat olettamuksensa faktoina." }
    ],
    "3": [
      { "fi": "Teksti esittää asiat 100% faktaan pohjautuen ilman rajoitteiden tunnistamista (Overconfidence)." }
    ],
    "5": [
      { "fi": "KATASTROFAALINEN VIRHE. Älyllinen epärehellisyys probabilitistisen tiedon esittämisessä. Nollatoleranssi." }
    ]
  }
}
```

### Execution Flow in V3 DAG
1. The orchestrator receives the workflow execution request (e.g. `strictness=5`).
2. When parsing the `PromptBlock` for the LLM context, the prompt builder looks at the `"claims"` dictionary.
3. It extracts **only** the list of claims mapped to `"5"`.
4. The LLM evaluates the text entirely based on the Level 5 absolute criteria. It has no knowledge of the lower-level lenient claims.

### Architectural Benefits
* **Absolute Objectivity:** Strictness is no longer an "attitude" we ask the LLM to adopt; it is a hard, measurable rubric change.
* **Pure Localization:** English and Finnish translations can return to perfect parity.
* **UI Configurable:** In Admin Studio, matrices can have tabs for "Leniency", "Standard", and "Zero-Trust", letting administrators define exactly what causes a score to drop at higher security evaluations.

This concept formally aligns the evaluation matrices with the Zero-Code / Fail-Fast doctrines established in V2.
