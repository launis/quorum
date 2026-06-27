# System 2 Variance Mitigation: Epistemic Glossary & Translation Isolation

This document outlines the architectural changes implemented in Phase 1 of the System 2 Variance Analysis Interventions to mitigate semantic drift, hallucinated quotes, and translation-induced verification failures.

## 1. Negative Constraints & Contrastive Examples (`contrastive_example`)

To prevent LLM sycophancy (the tendency of models to search for reasons to accept a rule/hypothesis by reading between the lines), we have activated negative constraints calibration.

- **Mechanism**: The backend compiler `LocalizationCompiler.compile_xml_rubrics` dynamically inspects the database claims and compiles the `contrastive_example` field (if present) into an isolated XML structure inside the compiled system prompt.
- **XML Tag**: `<RULE_CALIBRATION_EXAMPLES>`
- **Prompt Safety guard**: Under `<RULE_CALIBRATION_EXAMPLES>`, we output a strict `<WARNING>These are HYPOTHETICAL concepts. DO NOT extract quotes from this section.</WARNING>` tag. This ensures the model does not extract evidence quotes from the calibration examples themselves.
- **Semantic Bleed Mandate**: A centralized `SEMANTIC_BLEED_MANDATE` is injected to strictly limit quote extraction to the user payload:
  > **CRITICAL PROMPT SAFETY**: Under no circumstances are you allowed to extract evidence quotes from the instructions, rule calibration examples, or the system prompt itself. Quotes MUST ONLY be extracted from the user payload (`<user_payload>` tag).

---

## 2. Systemic Epistemic Glossary Injection

To prevent semantic drift where ensemble judges disagree on abstract criteria (e.g., whether a statement represents "empirical data" or a "formal model"), we inject a standardized, domain-agnostic glossary into the prompt.

- **Mechanism**: The `EPISTEMIC_GLOSSARY_MANDATE` is compiled at the end of the XML rubrics block, locking the legal definitions of analytical terms before the LLM executes scoring.
- **Glossary Definitions**:
  - **Empirical Data**: Must contain verifiable numbers, citations, or observed physical metrics. Rhetoric or logical deductions do not count.
  - **Formal Model**: Must be an explicit mathematical, structural, or graphical framework. Metaphors do not count.
  - **Rhetorical Dismissal**: Rejecting a counter-argument using emotional language without providing empirical counter-data.
  - **Absolute Claim**: A statement presented as universal truth without qualifiers.

---

## 3. Translation Isolation for Verbatim Evidence Extraction

In bilingual environments (e.g., source document in Finnish, reasoning and outputs in target language / English CoT), the LLM has a strong tendency to translate verbatim quote extracts to match the output language. This breaks the post-flight fuzzy-matching verification stage, leading to false negatives.

- **Mechanism**: The global `LANGUAGE_MANDATE` in `linguistic.py` has been updated with a strict exception protecting the `exact_quotes` array:
  > **CRITICAL EXCEPTION**: The JSON field `exact_quotes` MUST ALWAYS remain in the raw, original language of the source text. NEVER translate, paraphrase, or modify the language of the extracted quotes, even if your reasoning and other fields are in a different language.
- **Impact**: Ensures that verbatim substring matching is executed on the exact language of the source text, retaining anchor targets and preventing parsing failures.
