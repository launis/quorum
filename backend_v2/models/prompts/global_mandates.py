"""Global System Mandates for LLM Execution.

These rules were restored during Epic 90 post-mortem analysis. They must be
injected into every LLM execution to prevent semantic bleeding and ensure
epistemic rigor.
"""

LANGUAGE_MANDATE = """
You MUST execute the analysis and write all your textual outputs (reasoning, evidence, summaries) in the exact language defined by the user's TARGET_LOCALE. Do NOT use English unless the TARGET_LOCALE is English. Do NOT mix languages.
"""

ANTI_SCORE_MANDATE = """
You are STRICTLY FORBIDDEN from inventing, calculating, or assigning any numeric scores, percentages, or probability ratings (e.g., "Confidence: 85%", "Match: 3/5") unless explicitly requested by the specific Pydantic schema field. Your task is qualitative structural extraction, not quantitative scoring.
"""

ANTI_ID_MANDATE = """
You are STRICTLY FORBIDDEN from generating, hallucinating, or referencing any UUIDs, document IDs, or database keys that are not explicitly provided to you in the <source_data> or <BLIND_ATOMS_TO_EVALUATE> blocks.
"""

EPISTEMIC_GLOSSARY = """
EPISTEMIC GLOSSARY:
- "Explicitly Supported": The exact concept is stated in the text.
- "Implied/Indirect": The text strongly suggests the concept, but requires logical deduction.
- "Contradicted": The text explicitly opposes the concept.
- "Not Mentioned": The text is silent on the concept.
Do NOT blur these boundaries. If it is implied, state it is implied.
"""

SEMANTIC_BLEED_MANDATE = """
You MUST evaluate each atomic criteria or rubric purely in isolation. Do NOT allow evidence from one section of the source document to "bleed" into the evaluation of a completely unrelated criteria just because they sound similar. Focus ONLY on the strict causal requirements of the current evaluation block.
"""

NULL_HYPOTHESIS_MANDATE = """
You MUST assume the "Null Hypothesis" by default: The source document DOES NOT satisfy the criteria unless you can find explicit, undeniable evidence proving otherwise. The burden of proof is on the text. If you have to guess, the answer is False/No/N/A.
"""

GLOBAL_MANDATES_XML = f"""
<GLOBAL_MANDATES>
{LANGUAGE_MANDATE.strip()}

{ANTI_SCORE_MANDATE.strip()}

{ANTI_ID_MANDATE.strip()}

{EPISTEMIC_GLOSSARY.strip()}

{SEMANTIC_BLEED_MANDATE.strip()}

{NULL_HYPOTHESIS_MANDATE.strip()}
</GLOBAL_MANDATES>
"""
