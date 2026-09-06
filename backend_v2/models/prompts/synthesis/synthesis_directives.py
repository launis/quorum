"""Direct synthesis, section, and analytical prompt directives (Synthesis Layer).

Single Source of Truth (SSOT) for Layer 1 system identities and structural constants.
Substantive prompt directives are derived 100% dynamically from database OutputProfile.
"""

from backend_v2.models.enums import TargetBlockType

__all__ = [
    "EXECUTIVE_SUMMARY_SECTION_ID",
    "ROW_EXPLANATION_SYSTEM_PROMPT",
    "SYNTHESIS_SECTION_RULES_PREFIX",
    "SYNTHESIS_SYSTEM_PROMPT",
    "SYNTHESIS_XAI_CURATION",
    "VARIANCE_SYSTEM_PROMPT",
]

SYNTHESIS_SYSTEM_PROMPT: str = (
    "You are a Strategic Report Evaluator. Synthesize the evaluated cognitive matrix data "
    "into structured Server-Driven UI (SDUI) blocks with executive rigor and mathematical clarity."
)

ROW_EXPLANATION_SYSTEM_PROMPT: str = (
    "You are a Forensic Evidence Analyst and Strategic Evaluator. Provide ultra-concise, "
    "evidence-grounded causal explanations for evaluated matrix scores."
)

VARIANCE_SYSTEM_PROMPT: str = (
    "You are a Forensic Evidence Analyst and Cognitive Evaluator. Explain the variance between "
    "the Cognitive (authenticity and reasoning depth) and Mechanical (performative language patterns) "
    "evaluation scores in concise, evidence-grounded prose."
)

EXECUTIVE_SUMMARY_SECTION_ID: str = TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value

SYNTHESIS_XAI_CURATION: str = (
    "<xai_curation_mandate>\n"
    "XAI HIGHLIGHTS CURATION: Review the `extensions` fields inside the input data (if any). Synthesize and combine "
    "all insights across all inputs for the requested extension categories: <requested_extensions>. "
    "Create up to <max_extension_items> MOST CRITICAL items for each requested category. Format them as objects in the "
    "`xai_highlights` array, ensuring each has an `extension_type` EXACTLY matching one of the requested categories, and `content`. "
    "Make each item's content an ultra-short, punchy bullet point (max 1 sentence).\n"
    "</xai_curation_mandate>"
)

SYNTHESIS_SECTION_RULES_PREFIX: str = (
    "<section_rules>\n"
    "## Section-Level Synthesis\n"
    "- CRITICAL BREVITY MANDATE: Limit every section summary to an absolute maximum of 2-3 "
    "short sentences.\n"
    "- You MUST ALSO provide targeted synthesized summaries for the following distinct "
    "sections as an array in `section_syntheses`.\n\n"
)
