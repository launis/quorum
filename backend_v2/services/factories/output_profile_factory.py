"""OutputProfile Factory and Baseline Template SSOT.

Provides baseline default templates as plain English str constants used exclusively
for seeding and Studio UI 'New Profile' creation. Never invoked during runtime synthesis.
"""

from backend_v2.models.enums import PresetView, TargetBlockType
from backend_v2.models.v2_core import I18nText, MatrixSynthesisGroup, OutputProfile
from backend_v2.settings import get_settings

__all__ = [
    "DEFAULT_FACTORY_EXECUTIVE_SUMMARY_DIRECTIVE",
    "DEFAULT_FACTORY_MATRIX_1D_DIRECTIVE",
    "DEFAULT_FACTORY_MATRIX_2D_DIRECTIVE",
    "DEFAULT_FACTORY_MATRIX_3D_DIRECTIVE",
    "DEFAULT_FACTORY_MATRIX_TEXT_DIRECTIVE",
    "DEFAULT_FACTORY_ROW_EXPLANATION_DIRECTIVE",
    "DEFAULT_FACTORY_TONE_INSTRUCTION",
    "DEFAULT_FACTORY_VARIANCE_DIRECTIVE",
    "DEFAULT_FACTORY_XAI_DIRECTIVE",
    "build_draft_output_profile",
]

DEFAULT_FACTORY_TONE_INSTRUCTION: str = (
    "Act as a Senior Executive Coach. Provide deep, provocative, and strategic analysis rather than merely listing data."
)

DEFAULT_FACTORY_EXECUTIVE_SUMMARY_DIRECTIVE: str = (
    "EXECUTIVE SUMMARY SYNTHESIS MANDATE:\n"
    "- Synthesize the high-level findings, systemic implications, and strategic executive coaching advice.\n"
    "- Structure the narrative into clear, logical paragraphs.\n"
    "- Reference key strengths, vulnerabilities, and strategic focus areas from the evaluated data."
)

DEFAULT_FACTORY_MATRIX_1D_DIRECTIVE: str = (
    "1D METRICS SYNTHESIS MANDATE:\n"
    "- Focus on individual metric thresholds, isolated strengths, and isolated anomalies.\n"
    "- Provide clear, concise analytical takeaway for each evaluated dimension."
)

DEFAULT_FACTORY_MATRIX_2D_DIRECTIVE: str = (
    "2D COMPARISON SYNTHESIS MANDATE:\n"
    "- Analyze the cross-dimensional interactions, trade-offs, and tensions between the two evaluated axes.\n"
    "- Identify systemic correlations, divergence points, and strategic balance."
)

DEFAULT_FACTORY_MATRIX_3D_DIRECTIVE: str = (
    "3D RADAR SYNTHESIS MANDATE:\n"
    "- Provide a holistic multi-dimensional synthesis across all evaluated dimensions in the radar geometry.\n"
    "- Synthesize macro patterns, capability imbalances, and systemic maturity."
)

DEFAULT_FACTORY_MATRIX_TEXT_DIRECTIVE: str = (
    "TEXT SYNTHESIS MANDATE:\n"
    "- Formulate a narrative, qualitative deep-dive synthesis based on the textual evidence and qualitative observations.\n"
    "- Highlight nuances, contextual subtleties, and qualitative coaching takeaways."
)

DEFAULT_FACTORY_ROW_EXPLANATION_DIRECTIVE: str = (
    "ROW EXPLANATION SYNTHESIS MANDATE:\n"
    "- Formulate a clear, concise causal explanation for the score assigned to each evaluated matrix row.\n"
    "- Ground the explanation directly in the verified quotes and concrete textual evidence.\n"
    "- Explain why the score is justified based on the presence or absence of core criteria."
)

DEFAULT_FACTORY_XAI_DIRECTIVE: str = (
    "XAI EXTENSIONS SYNTHESIS MANDATE:\n"
    "- Synthesize explainable AI highlights, diagnostic extensions, and remediation recommendations.\n"
    "- Highlight actionable development points, key risks, and concrete next steps."
)

DEFAULT_FACTORY_VARIANCE_DIRECTIVE: str = (
    "VARIANCE EVALUATION SYNTHESIS MANDATE:\n"
    "- Evaluate the cognitive variance, performativity risk, and authenticity of the analyzed text.\n"
    "- Assess whether responses reflect authentic cognitive reasoning versus performative keyword compliance.\n"
    "- Provide an objective summary of linguistic signals and authenticity scores."
)


def build_draft_output_profile(
    profile_id: str,
    workflow_id: str,
    organization_id: str | None = None,
    initial_target_block: str | None = None,
) -> OutputProfile:
    """Build a fully populated, runnable OutputProfile draft for headless API and Studio creation."""
    settings = get_settings()

    target_block_order = [
        TargetBlockType.METADATA_BLOCK.value,
        TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value,
        TargetBlockType.SYNTHESIS_TEXT_BLOCK.value,
        TargetBlockType.GROUPED_EXTENSIONS_BLOCK.value,
        TargetBlockType.VARIANCE_VALIDATION_BLOCK.value,
    ]

    matrix_synthesis_groups: list[MatrixSynthesisGroup] = []
    if initial_target_block:
        target_block_order.insert(3, TargetBlockType.MATRIX_GRAPHS_BLOCK.value)
        matrix_synthesis_groups.append(
            MatrixSynthesisGroup(
                title=I18nText(translations={"en": "Executive Overview", "fi": "Johdon yleiskuva"}),
                target_blocks=[initial_target_block],
                view_type=PresetView.METRICS_1D,
            )
        )

    return OutputProfile(
        id=profile_id,
        slug="draft-profile",
        workflow_id=workflow_id,
        organization_id=organization_id,
        name=I18nText(translations={"en": "New Output Profile", "fi": "Uusi tulosprofiili"}),
        description=I18nText(
            translations={
                "en": "Standard executive reporting draft profile.",
                "fi": "Vakioitu johdon raportin luonnosprofiili.",
            }
        ),
        user_role_label=I18nText(translations={"en": "Target Audience:", "fi": "Kohdeyleisö:"}),
        target_block_order=target_block_order,
        matrix_synthesis_groups=matrix_synthesis_groups,
        tone_instruction=DEFAULT_FACTORY_TONE_INSTRUCTION,
        executive_summary_directive=DEFAULT_FACTORY_EXECUTIVE_SUMMARY_DIRECTIVE,
        matrix_1d_synthesis_directive=DEFAULT_FACTORY_MATRIX_1D_DIRECTIVE,
        matrix_2d_synthesis_directive=DEFAULT_FACTORY_MATRIX_2D_DIRECTIVE,
        matrix_3d_synthesis_directive=DEFAULT_FACTORY_MATRIX_3D_DIRECTIVE,
        matrix_text_synthesis_directive=DEFAULT_FACTORY_MATRIX_TEXT_DIRECTIVE,
        row_explanation_directive=DEFAULT_FACTORY_ROW_EXPLANATION_DIRECTIVE,
        xai_synthesis_directive=DEFAULT_FACTORY_XAI_DIRECTIVE,
        variance_synthesis_directive=DEFAULT_FACTORY_VARIANCE_DIRECTIVE,
        synthesis_length_constraint=settings.default_synthesis_length_constraint,
        row_explanation_length_constraint=settings.default_row_explanation_length_constraint,
        xai_length_constraint=settings.default_xai_length_constraint,
        variance_length_constraint=settings.default_variance_length_constraint,
    )
