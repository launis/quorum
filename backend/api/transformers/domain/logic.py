import logging

# UVM: Use strict extensions
from pydantic import ValidationError

from backend.models.domain import LogicianData, LogicianOutput
from backend.models.enums import StrategicDepth, TitleKey
from backend.models.view import LogicAnalysisDisplay, SectionType, ToulminDisplay, UiSection

from ..base import BaseTransformer

logger = logging.getLogger(__name__)


class LogicDomainTransformer(BaseTransformer):
    def _extract_logician_section(self, state: 'WorkflowState') -> UiSection | None:
        model = state.step_logician
        # Fallback to Panel data (inner data only)
        if not model:
            panel = state.step_panel
            if panel and getattr(panel, "logician_data", None):
                model = LogicianOutput(
                    logician_data=panel.logician_data,
                    thought_process="[Aggregated Panel Analysis]",
                    conclusion="N/A",
                    confidence_score=1.0,
                )

        if not model:
            return None

        try:
            display_model = self._transform_logician_data(model)
            return UiSection(
                id="logic-analysis",
                type=SectionType.LOGIC_ANALYSIS,
                title=self._get_title(TitleKey.LOGICIAN),
                data=display_model,
            )
        except Exception as e:
            # Graceful fallback for transformation errors too
            logger.warning(f"Failed to transform Logic display: {e}")
            return None

    def _transform_logician_data(self, model: LogicianOutput) -> LogicAnalysisDisplay:
        """Flattens LogicianOutput and calculates Server-Driven UI properties (Strict UVM)."""
        # Access via Pydantic model
        data = model.logician_data
        cog = data.cognitive_level

        # --- STRATEGIC ---
        s_score = cog.strategic_score
        s_pct = (s_score / 4.0) * 100.0 if s_score else 0.0
        s_enum = cog.strategic_depth

        # Robust Enum Handling (matches original logic)
        s_label = "Unknown"
        if isinstance(s_enum, StrategicDepth):
            s_label = s_enum.value
        elif s_enum:
            s_label = str(s_enum)

        # --- BLOOM ---
        b_score = cog.bloom_score
        b_pct = (b_score / 6.0) * 100.0 if b_score else 0.0
        b_enum = cog.bloom_level
        b_label = str(b_enum.value) if hasattr(b_enum, "value") else str(b_enum)

        # --- TOULMIN ---
        t_score = data.toulmin_score
        t_pct = (t_score / 6.0) * 100.0 if t_score else 0.0

        # --- ARGUMENTS ---
        arguments = []
        for arg in data.toulmin_analysis:
            arguments.append(ToulminDisplay(
                claim=arg.claim, 
                data=arg.data,
                warrant=arg.warrant,
                backing=arg.backing,
                rebuttal=arg.rebuttal,
                qualifier=arg.qualifier
            ))

        # --- DISPLAY OBJECT ---
        return LogicAnalysisDisplay(
            # Bloom
            bloom_score=b_score,
            bloom_percent=b_pct,
            bloom_level_raw=b_label,
            bloom_label_key=None,  # e.g. "BLOOM_EVALUATION"
            bloom_help=self._t("help.bloom", "Bloomin taksonomia arvioi kognitiivista tasoa."),
            # Strategic
            strategic_score=s_score,
            strategic_score_display=f"{s_score:.1f}" if s_score is not None else "N/A",
            strategic_percent=s_pct,
            strategic_percent_display=f"{int(s_pct)}%",
            strategic_depth_raw=s_label,
            strategic_label_key=None,
            strategic_help=self._t("help.strategic", "Strateginen syvyys arvioi ajattelun kokonaisvaltaisuutta."),
            # Toulmin
            toulmin_score=t_score,
            toulmin_percent=t_pct,
            toulmin_help=self._t("help.toulmin", "Toulmin-argumentaatio arvioi perustelujen rakennetta."),
            # Layout
            quadrant_key=None,
            quadrant_label_key="QUADRANT_UNKNOWN",
            position_label=f"B{b_score:.1f} / S{s_score:.1f}" if b_score and s_score else "N/A",
            # Data
            arguments=arguments,
        )
