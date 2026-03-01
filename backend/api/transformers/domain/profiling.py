import logging

from backend.models.domain import InteractionAnalysis, PerformativityOutput, ProfilerOutput
from backend.models.enums import TitleKey

# UVM Refactor: Use strict extensions
from backend.models.view import (
    DriverProfileDisplay,
    HeuristicDisplay,
    PerformativityDisplay,
    ProfilerDisplay,
    SectionType,
    UiSection,
)

from ..base import BaseTransformer

logger = logging.getLogger(__name__)


class ProfilingDomainTransformer(BaseTransformer):
    def _adapt_legacy_trace(self, data: dict) -> dict:
        """Helper to adapt legacy reasoning_trace string to strict ReasoningTraceDTO."""
        if "reasoning_trace" in data and "thought_process" not in data:
            data = data.copy()
            data["thought_process"] = data.pop("reasoning_trace")
            data["conclusion"] = "Implicit in Analysis"
            data["confidence_score"] = 1.0
        return data

    def _extract_profiler_section(self, state: WorkflowState) -> UiSection | None:
        model = state.step_profiler
        if not model:
            return None

        try:
            # UVM: Return strict model directly
            display_model = self._transform_profiler_data(model)

            return UiSection(
                id="profiler-analysis",
                type=SectionType.PROFILER_ANALYSIS,
                title=self._get_title(TitleKey.PROFILER),
                data=display_model,
            )
        except Exception as e:
            from backend.exceptions import AppException, ErrorCodes, status
            raise AppException(
                message=f"Failed to transform Profiler display: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.REPORT_GENERATION_FAILED, "original_error": str(e)},
            ) from e

    def _transform_profiler_data(self, model: ProfilerOutput) -> ProfilerDisplay:
        """Flattens ProfilerOutput and calculates SDUI properties (Strict UVM)."""
        metrics = model.metrics

        # 1. Control Ratio (Special handling as it might be missing in strict schema?)
        control = getattr(metrics, "control_ratio", None)
        cr_percent = None

        if control is not None:
            val = control.get("driver") if isinstance(control, dict) else control
            if val is not None:
                cr_percent = float(val) * 100.0

        # 2. Bias / Gap
        auto_bias = getattr(metrics, "automation_bias", 0.0)
        say_do = getattr(metrics, "say_do_gap", 0.0)

        ab_detected = auto_bias > 0.5
        sd_detected = say_do > 0.5

        # DISPLAY LABELS (Mapped to UI Enums logic)
        ab_label_str = "BIAS_DETECTED" if ab_detected else "BIAS_NONE"
        sd_label_str = "GAP_DETECTED" if sd_detected else "GAP_NONE"

        # Raw Metrics
        word_count = int(getattr(metrics, "word_count", 0))
        avg_sent = float(getattr(metrics, "avg_sentence_length", 0.0))
        lex_div = float(getattr(metrics, "lexical_diversity", 0.0))
        cap_ratio = float(getattr(metrics, "capitalization_ratio", 0.0))

        # Mapping to UVM Strings
        return ProfilerDisplay(
            control_ratio_percent=cr_percent,
            control_label_key=None,  # e.g. "CONTROL_DRIVER"
            control_help=self._t("help.control_ratio", "Kontrollisuhde mittaa kuljettajan osuutta vuorovaikutuksessa."),
            word_count=word_count,
            word_count_display=str(word_count),
            word_count_help=self._t("help.word_count", "Sanamäärä kertoo vastauksen pituuden."),
            avg_sentence_length=avg_sent,
            avg_sentence_length_display=f"{avg_sent:.1f}",
            lexical_diversity=lex_div,
            lexical_diversity_display=f"{lex_div:.2f}",
            capitalization_ratio_percent=int(cap_ratio * 100),
            capitalization_ratio_display=f"{(cap_ratio * 100):.1f}%",
            automation_bias_label=ab_label_str,
            automation_bias_color="red" if ab_detected else "green",
            say_do_gap_label=sd_label_str,
            say_do_gap_color="red" if sd_detected else "green",
            psychological_profile=f"{self._t('Tone', 'Tone')}: {model.emotional_tone}. {self._t('Biases', 'Biases')}: {', '.join(model.cognitive_biases)}",
            intent_analysis=str(model.author_intent),
        )

    def _extract_interaction_section(self, state: WorkflowState) -> UiSection | None:
        model = state.step_interaction
        if not model:
            # Try fallback to step_driver
            from backend.models.domain.interaction import InteractionAnalysis
            model = state.get_context("step_driver", InteractionAnalysis)

        if not model:
            return None

        try:
            # UVM: Return strict DriverProfileDisplay
            ratio = state.get_context("input_control_ratio")
            display_model = self._transform_interaction_data(model, ratio)
            return UiSection(
                id="interaction-grid",
                type=SectionType.DRIVER_PROFILE,
                title=self._get_title(TitleKey.INTERACTION),
                data=display_model,
            )
        except Exception as e:
            from backend.exceptions import AppException
            raise AppException(f"Failed to transform Driver display: {e}", 500) from e

    def _transform_interaction_data(self, model: InteractionAnalysis, input_control_ratio: float | None = None) -> DriverProfileDisplay:
        """Flattens InteractionOutput to strict DriverProfileDisplay."""
        # STRICT MAPPING
        role_raw = model.role_classification  # Literal
        # Ensure correct formatting for frontend ENUM
        role_key = f"ROLE_{role_raw.upper()}"

        high_dependency = model.high_dependency
        cmd_count = model.imperative_command_count
        strategy = model.strategy

        # Construct Strict View Model
        return DriverProfileDisplay(
            role_classification=role_key,
            high_dependency=high_dependency,
            imperative_command_count=cmd_count,
            strategy=strategy,
            input_control_ratio=input_control_ratio
        )

    def _extract_detector_section(self, state: WorkflowState) -> UiSection | None:
        model = state.step_detector

        # Fallback to Panel if not in root steps (though usually root)
        if not model:
            panel = state.step_panel
            if panel and getattr(panel, "performativity_analysis", None):
                model = PerformativityOutput(
                    performativity_analysis=panel.performativity_analysis,
                    thought_process="[Aggregated Panel Analysis]",
                    conclusion="N/A",
                    confidence_score=1.0,
                )

        if not model:
            return None

        try:
            display_model = self._transform_detector_data(model)
            return UiSection(
                id="performativity-check",
                type=SectionType.PERFORMATIVITY_CHECK,
                title=self._get_title(TitleKey.PERFORMATIVITY),
                data=display_model,
            )
        except Exception as e:
            from backend.exceptions import AppException
            raise AppException(f"Failed to transform Performativity display: {e}", 500) from e

    def _transform_detector_data(self, model: PerformativityOutput) -> PerformativityDisplay:
        """Flattens DetectorOutput to strict PerformativityDisplay."""
        # Fix: access correct field 'performativity_analysis'
        check = model.performativity_analysis

        heuristics = []
        # Fix: iterate over 'performativity_heuristics'
        for h in check.performativity_heuristics:
            heuristics.append(
                HeuristicDisplay(name=h.heuristic_name, flag=h.flag_raised, color="red" if h.flag_raised else "green")
            )

        return PerformativityDisplay(
            authenticity_score=check.authenticity_score,
            # Fix: Scale is 1-3, so divide by 3.0
            authenticity_percent=(check.authenticity_score / 3.0) * 100.0 if check.authenticity_score else 0.0,
            # Fix: access 'authenticity_assessment'
            authenticity_assessment=check.authenticity_assessment,
            authenticity_help=self._t("help.authenticity", "Autenttisuus arvioi tekstin aitoutta."),
            heuristics=heuristics,
        )
