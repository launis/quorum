import logging

# UVM: Use strict extensions
from backend.models.domain import LogicianOutput
from backend.models.enums import StrategicDepth, TitleKey
from backend.models.state import WorkflowState
from backend.models.view.semantic_models import BlockType, LogicAnalysisDisplay, SemanticBlock, ToulminDisplay

from ..base import BaseTransformer

logger = logging.getLogger(__name__)


class LogicDomainTransformer(BaseTransformer):
    def _extract_logician_section(self, state: WorkflowState) -> SemanticBlock | None:
        model = state.step_logician
        # Fallback to Panel data (inner data only)
        if not model:
            panel = state.step_panel
            if panel and getattr(panel, "logician_data", None):
                model = LogicianOutput(
                    logician_data=panel.logician_data,
                    thought_process=panel.thought_process,
                    conclusion=panel.conclusion,
                    confidence_score=panel.confidence_score,
                )

        if not model:
            return None

        try:
            display_model = self._transform_logician_data(model)
            return SemanticBlock(id="logic-analysis",
                type=BlockType.CARD,
                label=self._get_title(TitleKey.LOGICIAN),
                value=display_model,
            )
        except Exception as e:
            from fastapi import status
            from backend.exceptions import AppException, ErrorCodes
            import logging
            logger = logging.getLogger(__name__)

            logger.error(f"[LogicDomainTransformer] {ErrorCodes.REPORT_GENERATION_FAILED.name}: Error: {e}", exc_info=True)
            raise AppException(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.REPORT_GENERATION_FAILED.name},
            ) from e

    def _transform_logician_data(self, model: LogicianOutput) -> LogicAnalysisDisplay:
        """Flattens LogicianOutput and calculates Server-Driven UI properties (Strict UVM)."""
        # Access via Pydantic model
        data = model.logician_data
        cog = data.cognitive_level

        # --- STRATEGIC ---
        s_score = cog.strategic_score
        s_pct: float | None = (s_score / 4.0) * 100.0 if s_score is not None else None
        s_enum = cog.strategic_depth

        # Robust Enum Handling (matches original logic)
        s_label: str | None = None
        if isinstance(s_enum, StrategicDepth):
            s_label = s_enum.value
        elif s_enum:
            s_label = str(s_enum)

        # --- BLOOM ---
        b_score = cog.bloom_score
        b_pct: float | None = (b_score / 6.0) * 100.0 if b_score is not None else None
        b_enum = cog.bloom_level
        b_label = str(b_enum.value) if hasattr(b_enum, "value") else (str(b_enum) if b_enum else None)

        # --- TOULMIN ---
        t_score = data.toulmin_score
        t_pct: float | None = (t_score / 6.0) * 100.0 if t_score is not None else None

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

        # --- DISPLAY HINTS ---
        # No defaults. If score is missing, bubble properties are skipped.
        b_size: float | None = None
        b_style: str | None = None
        if s_score is not None and b_pct is not None and t_pct is not None:
            b_size = 20.0 + (s_score * 5.0)
            b_style = f"position: absolute; border-radius: 50%; background-color: rgba(63, 81, 181, 0.6); border: 1px solid #3F51B5; transform: translate(-50%, 50%); left: {b_pct:.1f}%; bottom: {t_pct:.1f}%; width: {int(b_size)}px; height: {int(b_size)}px;"
        
        # --- DISPLAY OBJECT ---
        return LogicAnalysisDisplay(
            # Bloom
            bloom_score=b_score,
            bloom_percent=b_pct,
            bloom_percent_display=f"{b_pct:.1f}" if b_pct is not None else None,
            bloom_level_raw=b_label,
            bloom_label_key=None,  # e.g. "BLOOM_EVALUATION"
            bloom_help=self._t("help.bloom", "Bloomin taksonomia arvioi kognitiivista tasoa."),
            # Strategic
            strategic_score=s_score,
            strategic_score_display=f"{s_score:.1f}" if s_score is not None else None,
            strategic_percent=s_pct,
            strategic_percent_display=f"{s_pct:.1f}%" if s_pct is not None else None,
            strategic_depth_raw=s_label,
            strategic_label_key=None,
            strategic_help=self._t("help.strategic", "Strateginen syvyys arvioi ajattelun kokonaisvaltaisuutta."),
            # Toulmin
            toulmin_score=t_score,
            toulmin_percent=t_pct,
            toulmin_percent_display=f"{t_pct:.1f}" if t_pct is not None else None,
            toulmin_help=self._t("help.toulmin", "Toulmin-argumentaatio arvioi perustelujen rakennetta."),
            # Layout
            quadrant_key=None,
            quadrant_label_key="QUADRANT_UNKNOWN",
            position_label=f"B{b_score:.1f} / S{s_score:.1f}" if b_score and s_score else "N/A",
            bubble_size=b_size,
            bubble_style=b_style,
            # Data
            arguments=arguments,
        )


