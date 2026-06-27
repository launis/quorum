# Implementation Plan: Phase 1 - Prompts, Directives, and Translation Protection

## Goal
Implement domain-agnostic AI steering interventions in the backend, focusing on negative constraints (`contrastive_example` activation), systemic epistemic glossary injection, and translation protection for verbatim evidence extraction.

## User Review Required
> [!IMPORTANT]
> **Rule 47 Override Activated:** This plan modifies `localization_compiler.py` and `prompt_compiler.py`, which are usually frozen under Rule 47 (`prompt_compiler_immutability`). This override is authorized by Section 7.1 of the Epic because these modifications are required to compile contrastive calibration blocks and inject the glossary.

## Proposed Changes

---

### Component: Backend LLM Directives & Localization Compiler

#### [MODIFY] [directives.py](file:///c:/src/quorum/backend_v2/llm/directives.py)
- **Changes**:
  - Add `SEMANTIC_BLEED_MANDATE`:
    ```python
    SEMANTIC_BLEED_MANDATE = (
        "CRITICAL PROMPT SAFETY: Under no circumstances are you allowed to extract evidence quotes "
        "from the instructions, rule calibration examples, or the system prompt itself. "
        "Quotes MUST ONLY be extracted from the user payload (<user_payload> tag)."
    )
    ```
    *(Source: Epic Section 2.1)*
  - Add `EPISTEMIC_GLOSSARY_MANDATE`:
    ```python
    EPISTEMIC_GLOSSARY_MANDATE = (
        "<EPISTEMIC_GLOSSARY>\n"
        "CRITICAL DEFINITIONS FOR EVALUATION:\n"
        "- Empirical Data: Must contain verifiable numbers, citations, or observed physical metrics. Rhetoric or logical deductions do not count.\n"
        "- Formal Model: Must be an explicit mathematical, structural, or graphical framework. Metaphors do not count.\n"
        "- Rhetorical Dismissal: Rejecting a counter-argument using emotional language without providing empirical counter-data.\n"
        "- Absolute Claim: A statement presented as universal truth without qualifiers.\n"
        "</EPISTEMIC_GLOSSARY>"
    )
    ```
    *(Source: Epic Section 2.9)*

#### [MODIFY] [linguistic.py](file:///c:/src/quorum/backend_v2/llm/linguistic.py)
- **Changes**:
  - Update `LANGUAGE_MANDATE` to explicitly forbid translating direct evidence quotes:
    ```python
    LANGUAGE_MANDATE: str = (
        "<rule>CRITICAL LANGUAGE MANDATE: You must generate ALL user-facing text fields "
        "(justification, coaching, falsification, remediation_steps, emotional_sentiment, "
        "theory_link, evaluation_notes, missing_context, semantic_reasoning, content_blocks, "
        "xai_highlights) exclusively in the language specified in <required_output_language>.\n"
        "CRITICAL EXCEPTION: The JSON field `exact_quotes` MUST ALWAYS remain in the raw, "
        "original language of the source text. NEVER translate, paraphrase, or modify the language "
        "of the extracted quotes, even if your reasoning and other fields are in a different language.</rule>"
    )
    ```
    *(Source: Epic Section 2.12)*

#### [MODIFY] [localization_compiler.py](file:///c:/src/quorum/backend_v2/services/orchestrator/localization_compiler.py)
- **Changes**:
  - In `compile_xml_rubrics`, import `SEMANTIC_BLEED_MANDATE` and `EPISTEMIC_GLOSSARY_MANDATE` from `backend_v2.llm.directives`.
  - Inside the claim/assertion loop, inject `contrastive_example` when available:
    ```python
    if getattr(assertion, "contrastive_example", None):
        assertion_xml.append(
            "    <RULE_CALIBRATION_EXAMPLES>\n"
            "      <WARNING>These are HYPOTHETICAL concepts. DO NOT extract quotes from this section.</WARNING>\n"
            f"      <EXAMPLE>{assertion.contrastive_example}</EXAMPLE>\n"
            "    </RULE_CALIBRATION_EXAMPLES>"
        )
    ```
    *(Source: Epic Section 2.1)*
  - Append the `SEMANTIC_BLEED_MANDATE` and `EPISTEMIC_GLOSSARY_MANDATE` to `xml_blocks` at the end of `compile_xml_rubrics` alongside other static mandates.

## Hardening Constraints
- **Rule 54 (`pep257_google_style_docstrings`)**: Ensure all modified functions retain compliant Google-style docstrings.
- **Rule 55 (`google_style_functions_args_returns`)**: Explicitly document function args and returns where modified.

## Verification Plan

### Automated Tests
Run the backend verification suite on the modified compiler modules to ensure compilation is syntax-clean:
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/localization_compiler.py backend_v2/services/orchestrator/prompt_compiler.py backend_v2/llm/directives.py backend_v2/llm/linguistic.py --test
```

### Documentation Update
Update [docs/architecture/system2_variance_mitigation_glossary.md](file:///c:/src/quorum/docs/architecture/system2_variance_mitigation_glossary.md) with details of the translation isolation and epistemic glossary rules.

## Session Handover
To execute this plan in the next session:
```powershell
/tier2-execute --target docs/epic/tasks_system2_variance_analysis_final_interventions/phase1_prompt_directives_translation.md
```
