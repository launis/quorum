"""Direct synthesis, section, and analytical prompt directives.

Single Source of Truth (SSOT) for direct content generation, including Executive Summary,
1D Metrics, 2D Comparison, 3D Radar, Text-Only matrix syntheses, Row Explanations,
XAI Highlights, and Variance Explanations.
"""

from backend_v2.models.enums import TargetBlockType

__all__ = [
    "DEFAULT_SYNTHESIS_SYSTEM_PROMPT",
    "EXECUTIVE_SUMMARY_DIRECTIVE",
    "EXECUTIVE_SUMMARY_SECTION_ID",
    "MATRIX_1D_SYNTHESIS_DIRECTIVE",
    "MATRIX_2D_SYNTHESIS_DIRECTIVE",
    "MATRIX_3D_SYNTHESIS_DIRECTIVE",
    "MATRIX_TEXT_SYNTHESIS_DIRECTIVE",
    "ROW_EXPLANATION_DIRECTIVE",
    "VARIANCE_EXPLANATION_DIRECTIVE",
    "XAI_EXPLANATIONS_DIRECTIVE",
]

DEFAULT_SYNTHESIS_SYSTEM_PROMPT: str = (
    "You are a Senior Executive Coach and Strategic Evaluator. Synthesize the evaluated "
    "cognitive matrix data into structured Server-Driven UI (SDUI) blocks with executive rigor, "
    "mathematical clarity, and actionable developmental feedback."
)

EXECUTIVE_SUMMARY_SECTION_ID: str = TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value

EXECUTIVE_SUMMARY_DIRECTIVE: str = (
    "<executive_summary_directive>\n"
    "EXECUTIVE SUMMARY SYNTHESIS MANDATE:\n"
    "- Synthesize the high-level findings, systemic implications, and strategic executive coaching advice.\n"
    "- Structure the narrative into clear, logical paragraphs using SDUI ParagraphBlocks.\n"
    "- Reference key strengths, vulnerabilities, and strategic focus areas from the evaluated data.\n"
    "</executive_summary_directive>"
)

MATRIX_1D_SYNTHESIS_DIRECTIVE: str = (
    "<matrix_1d_directive>\n"
    "1D METRICS SYNTHESIS MANDATE:\n"
    "- Focus on individual metric thresholds, isolated strengths, and isolated anomalies.\n"
    "- Provide clear, concise analytical takeaway for each evaluated dimension.\n"
    "- Structure your findings directly as SDUI blocks.\n"
    "</matrix_1d_directive>"
)

MATRIX_2D_SYNTHESIS_DIRECTIVE: str = (
    "<matrix_2d_directive>\n"
    "2D COMPARISON SYNTHESIS MANDATE:\n"
    "- Compare and contrast the primary dimension against the secondary dimension.\n"
    "- Identify quadrants, balance, trade-offs, and tensions between the two dimensions.\n"
    "- Structure your findings directly as SDUI blocks.\n"
    "</matrix_2d_directive>"
)

MATRIX_3D_SYNTHESIS_DIRECTIVE: str = (
    "<matrix_3d_directive>\n"
    "3D RADAR SYNTHESIS MANDATE:\n"
    "- Synthesize the holistic systemic profile across all evaluated radar axes.\n"
    "- Identify overall balance, center of gravity, systemic strengths, and critical vulnerabilities.\n"
    "- Structure your findings directly as SDUI blocks.\n"
    "</matrix_3d_directive>"
)

MATRIX_TEXT_SYNTHESIS_DIRECTIVE: str = (
    "<matrix_text_directive>\n"
    "TEXT-ONLY MATRIX SYNTHESIS MANDATE:\n"
    "- Synthesize the evaluated matrix dimensions into a cohesive analytical narrative.\n"
    "- Provide actionable takeaways and contextual explanations for each evaluated topic.\n"
    "- Structure your findings directly as SDUI ParagraphBlocks.\n"
    "</matrix_text_directive>"
)

ROW_EXPLANATION_DIRECTIVE: str = (
    "<row_explanation_directive>\n"
    "MATRIX ROW CAUSAL EXPLANATION MANDATE:\n"
    "- Provide a concise causal explanation in the <required_output_language> for why this specific matrix score level was reached based on the source text evidence.\n"
    "- Ground the explanation in the specific level achieved (e.g. why 2/5 was achieved based on passed criteria and observed evidence).\n"
    "- Strict brevity constraint: maximum 30 words per row.\n"
    "- Return plain text only; no markdown formatting.\n"
    "- NEVER output English or mixed languages when <required_output_language> specifies another language.\n"
    "</row_explanation_directive>"
)

XAI_EXPLANATIONS_DIRECTIVE: str = (
    "<xai_explanations_directive>\n"
    "XAI HIGHLIGHTS & EXTENSIONS SYNTHESIS MANDATE:\n"
    "- Review evaluated XAI extensions across matrices and distill critical developmental insights.\n"
    "- Highlight key risk flags, coaching challenges, and remediation pathways.\n"
    "- Structure findings into compact, high-impact bullet items.\n"
    "</xai_explanations_directive>"
)

VARIANCE_EXPLANATION_DIRECTIVE: str = (
    "<variance_explanation_directive>\n"
    "VARIANCE & AUTHENTICITY EVALUATION MANDATE:\n"
    "- Explain the mechanical versus cognitive alignment score and interpret any detected variance.\n"
    "- Provide actionable coaching context regarding authenticity and rhetorical consistency.\n"
    "- Keep explanations objective, constructive, and evidence-grounded.\n"
    "</variance_explanation_directive>"
)
