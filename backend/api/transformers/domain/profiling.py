import logging

from backend.exceptions import AppException
from backend.models.domain import InteractionAnalysis, PerformativityOutput, ProfilerAnalysis
from backend.models.enums import LabelKey, TitleKey
# UVM Refactor: Use strict extensions
from backend.models.view import (
    DriverProfileDisplay,
    HeuristicDisplay,
    PerformativityDisplay,
    ProfilerDisplay,
    SectionType,
    UiSection
)
from backend.models.view_extensions import DriverDisplay as LegacyDriverDisplay # Deprecated

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

    def _extract_profiler_section(self, steps: dict) -> UiSection | None:
        step = steps.get("step_profiler")
        if not step:
            return None

        # STRICT VALIDATION
        try:
             # If step has "profiler_data" key, use that.
            if "profiler_data" in step:
                 model = ProfilerAnalysis(**self._adapt_legacy_trace(step["profiler_data"])) # If wrapped
            else:
                 model = ProfilerAnalysis(**self._adapt_legacy_trace(step)) # If flat
        except Exception as e:
            error_code = "PROFILER_VALIDATION_FAILED"
            logger.error(f"{error_code}: {e}", exc_info=True)
            raise AppException(
                message=str(e),
                status_code=500,
                details={"error_code": error_code}
            ) from e

        try:
            # UVM: Return strict model directly
            display_model = self._transform_profiler_data(model)

            return UiSection(
                id="profiler-analysis",
                type=SectionType.PROFILER_ANALYSIS,
                title=self._get_title(TitleKey.PROFILER),
                data=display_model
            )
        except Exception as e:
             raise AppException(f"Failed to transform Profiler display: {e}", 500) from e

    def _transform_profiler_data(self, model: ProfilerAnalysis) -> ProfilerDisplay:
        """Flattens ProfilerOutput and calculates SDUI properties (Strict UVM)."""
        metrics = model.metrics # dict[str, Any]

        # 1. Control Ratio (Special handling as it might be missing in strict schema?)
        control = metrics.get("control_ratio")
        cr_percent = None
        cr_label = "Unknown"

        if control is not None:
             val = control.get("driver") if isinstance(control, dict) else control
             if val is not None:
                cr_percent = float(val) * 100.0
                cr_label = "DRIVER_LABEL" # Placeholder logic

        # 2. Bias / Gap
        auto_bias = metrics.get("automation_bias", 0.0)
        say_do = metrics.get("say_do_gap", 0.0)

        ab_detected = auto_bias > 0.5
        sd_detected = say_do > 0.5




        # DISPLAY LABELS (Simulated localization or raw)
        ab_label_str = "Detected" if ab_detected else "None"
        sd_label_str = "Detected" if sd_detected else "None"

        # Raw Metrics
        word_count = int(metrics.get("word_count", 0))
        avg_sent = float(metrics.get("avg_sentence_length", 0.0))
        lex_div = float(metrics.get("lexical_diversity", 0.0))
        cap_ratio = float(metrics.get("capitalization_ratio", 0.0))

        # Mapping to UVM Strings
        # Mapping to UVM Strings
        return ProfilerDisplay(
            control_ratio_percent=cr_percent,
            control_label_key=None, # e.g. "CONTROL_DRIVER"
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

            psychological_profile=f"Tone: {model.emotional_tone}. Biases: {', '.join(model.cognitive_biases)}",
            intent_analysis=str(model.author_intent)
        )


    def _extract_interaction_section(self, steps: dict) -> UiSection | None:
        step = steps.get("step_interaction") or steps.get("step_driver")
        if not step:
            return None

        try:
             # Handle nested vs flat
            if "interaction_analysis" in step:
                 model = InteractionAnalysis(**self._adapt_legacy_trace(step["interaction_analysis"]))
            elif "driver_profile" in step:
                 model = InteractionAnalysis(**self._adapt_legacy_trace(step["driver_profile"]))
            else:
                 model = InteractionAnalysis(**self._adapt_legacy_trace(step))
        except Exception as e:
            error_code = "INTERACTION_VALIDATION_FAILED"
            logger.error(f"{error_code}: {e}", exc_info=True)
            raise AppException(
                message=str(e),
                status_code=500,
                details={"error_code": error_code}
            ) from e

        try:
             # UVM: Return strict DriverProfileDisplay
             display_model = self._transform_interaction_data(model)
             return UiSection(
                id="interaction-grid",
                type=SectionType.DRIVER_PROFILE,
                title=self._get_title(TitleKey.INTERACTION),
                data=display_model,
            )
        except Exception as e:
             raise AppException(f"Failed to transform Driver display: {e}", 500) from e

    def _transform_interaction_data(self, model: InteractionAnalysis) -> DriverProfileDisplay:
        """Flattens InteractionOutput to strict DriverProfileDisplay."""
        # STRICT MAPPING
        role_raw = model.role_classification # Literal
        # Ensure correct formatting for frontend ENUM
        role_key = f"ROLE_{role_raw.upper()}"

        strategies = model.improvement_suggestions
        input_quality = model.input_quality_score
        iq_label = str(input_quality)

        # Construct Strict View Model
        return DriverProfileDisplay(
            classification=role_key,
            input_quality_label=iq_label,
            strategies=strategies
        )

    def _extract_detector_section(self, steps: dict) -> UiSection | None:
        step = steps.get("step_detector")
        # Fallback to Panel if not in root steps (though usually root)
        if not step:
             panel = steps.get("step_panel", {})
             step = panel.get("performativity_analysis") or panel.get("performatiivisuus_auditointi")

        if not step:
            return None

        try:
              # PerformativityOutput
              # Strict Validation
             model = PerformativityOutput(**self._adapt_legacy_trace(step))
        except Exception as e:
            error_code = "PERFORMATIVITY_VALIDATION_FAILED"
            logger.error(f"{error_code}: {e}", exc_info=True)
            raise AppException(
                message=str(e),
                status_code=500,
                details={"error_code": error_code}
            ) from e

        try:
            display_model = self._transform_detector_data(model)
            return UiSection(
                id="performativity-check",
                type=SectionType.PERFORMATIVITY_CHECK,
                title=self._get_title(TitleKey.PERFORMATIVITY),
                data=display_model
            )
        except Exception as e:
             raise AppException(f"Failed to transform Performativity display: {e}", 500) from e

    def _transform_detector_data(self, model: PerformativityOutput) -> PerformativityDisplay:
        """Flattens DetectorOutput to strict PerformativityDisplay."""
        # Fix: access correct field 'performativity_analysis'
        check = model.performativity_analysis

        heuristics = []
        # Fix: iterate over 'performativity_heuristics'
        for h in check.performativity_heuristics:
            heuristics.append(HeuristicDisplay(
                name=h.heuristic_name,
                flag=h.flag_raised,
                color="red" if h.flag_raised else "green"
            ))

        return PerformativityDisplay(
            authenticity_score=check.authenticity_score,
            # Fix: Scale is 1-3, so divide by 3.0
            authenticity_percent=(check.authenticity_score / 3.0) * 100.0 if check.authenticity_score else 0.0,
            # Fix: access 'authenticity_assessment'
            authenticity_assessment=check.authenticity_assessment,
            authenticity_help=self._t("help.authenticity", "Autenttisuus arvioi tekstin aitoutta."),
            heuristics=heuristics
        )
