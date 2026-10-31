"""Direct synthesis, section, and analytical prompt directives (Synthesis Layer).

Single Source of Truth (SSOT) for Layer 1 system identities and structural constants.
Substantive prompt directives are derived 100% dynamically from database OutputProfile.
"""

from backend_v2.models.enums import TargetBlockType

__all__ = [
    "CAUSAL_TDA_DIAGNOSIS_MANDATE",
    "CONTRASTIVE_FRONTIER_MANDATE",
    "EXECUTIVE_SUMMARY_SECTION_ID",
    "EXECUTIVE_SUMMARY_SECTION_RULES_PREFIX",
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

# Ground synthesis narratives in causal fault chains, Toulmin rebuttals, and contrastive deficits.
CAUSAL_TDA_DIAGNOSIS_MANDATE: str = (
    "<causal_tda_diagnosis_mandate>\n"
    "- CAUSAL & TOULMIN FALSIFICATION GROUNDING: When <causal_diagnosis> is provided in the dynamic context, "
    "you MUST ground executive summaries, matrix section narratives, XAI highlights, and row explanations in the "
    "resolved root-cause fault chains, Toulmin falsified claims (rebuttal -> invalidated warrant -> falsified claim), "
    "prescriptive remediations, and post-hoc fidelity penalties.\n"
    "- TRANSITIVE SHORT-CIRCUIT LINEAGE: When a criterion is marked N_A with `short_circuited_by_claims`, explicitly "
    "attribute the unreached tier to the upstream prerequisite failure rather than treating it as an independent omission.\n"
    "</causal_tda_diagnosis_mandate>"
)

CONTRASTIVE_FRONTIER_MANDATE: str = (
    "<contrastive_frontier_mandate>\n"
    "- CONTRASTIVE FRONTIER GROUNDING: When `unmet_deficits` are provided for a matrix, anchor your diagnostic "
    "explanation in the `evaluation_reasoning`, `anti_patterns`, `contrastive_rejected`, and `contrastive_acceptable` "
    "rubric exemplars to explain why the achieved score stopped at the current tier and what concrete shift is required "
    "to satisfy the next frontier tier.\n"
    "</contrastive_frontier_mandate>"
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
    "- LENGTH BUDGET MANDATE: Adhere strictly to the target character budget provided in <section_budget> if present. "
    "Provide a focused, evidence-grounded summary tailored to the section directive without exceeding the budget.\n"
    "- You MUST ALSO provide targeted synthesized summaries for the following distinct "
    "sections as an array in `section_syntheses`.\n\n"
)

EXECUTIVE_SUMMARY_SECTION_RULES_PREFIX: str = (
    "<section_rules>\n"
    "## Executive Summary Synthesis\n"
    "- LENGTH BUDGET MANDATE: Adhere strictly to the target character budget provided in <section_budget> if present. "
    "Structure the narrative into coherent, substantive paragraphs "
    "that fully address the strategic executive directive within the budgeted length.\n"
    "- You MUST provide structured SDUI content blocks representing the executive summary "
    "narrative in `executive_summary`.\n"
    "- Follow the specific directive below for the executive summary narrative:\n\n"
)
