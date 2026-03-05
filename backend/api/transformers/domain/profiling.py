import logging
from typing import Any

from backend.models.domain import InteractionAnalysis, PerformativityOutput, ProfilerOutput
from backend.models.enums import TitleKey
from backend.models.state import WorkflowState

# UVM Refactor: Use strict extensions
from backend.models.view.semantic_models import (
    BlockType,
    DriverProfileDisplay,
    HeuristicDisplay,
    PerformativityDisplay,
    ProfilerDisplay,
    SemanticBlock,
)

from ..base import BaseTransformer

logger = logging.getLogger(__name__)


class ProfilingDomainTransformer(BaseTransformer):
    def _adapt_legacy_trace(self, data: dict[str, Any]) -> dict[str, Any]:
        """Helper to adapt legacy reasoning_trace string to strict ReasoningTraceDTO."""
        if "reasoning_trace" in data and "thought_process" not in data:
            data = data.copy()
            data["thought_process"] = data.pop("reasoning_trace")
            data["conclusion"] = "Implicit in Analysis"
            data["confidence_score"] = 1.0
        return data

    def _extract_profiler_section(self, state: WorkflowState) -> SemanticBlock | None:
        model = state.step_profiler
        if not model:
            return None

        try:
            # UVM: Return strict model directly
            display_model = self._transform_profiler_data(model)

            return SemanticBlock(id="profiler-analysis",
                type=BlockType.CARD,
                label=self._get_title(TitleKey.PROFILER),
                value=display_model,
            )
        except Exception as e:
            logger.warning(f"BFF Graceful degradation [ProfilerDomainTransformer]: {e}", exc_info=True)
            return SemanticBlock(
                id="profiler-analysis",
                type=BlockType.CARD,
                label=self._get_title(TitleKey.PROFILER),
                value={},
            )

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
            imperative_command_count=getattr(metrics, "imperative_command_count", None),
            role_classification=str(metrics.role_classification.value) if getattr(metrics, "role_classification", None) else None,
            psychological_profile=f"{self._t('Tone', 'Tone')}: {model.emotional_tone}. {self._t('Biases', 'Biases')}: {', '.join(model.cognitive_biases)}",
            intent_analysis=str(model.author_intent),
        )

    def _extract_interaction_section(self, state: WorkflowState) -> SemanticBlock | None:
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
            return SemanticBlock(id="interaction-grid",
                type=BlockType.CARD,
                label=self._get_title(TitleKey.INTERACTION),
                value=display_model,
            )
        except Exception as e:
            logger.warning(f"BFF Graceful degradation [ProfilerDomainTransformer - Interaction]: {e}", exc_info=True)
            return SemanticBlock(
                id="interaction-grid",
                type=BlockType.CARD,
                label=self._get_title(TitleKey.INTERACTION),
                value={},
            )

    def _transform_interaction_data(self, model: InteractionAnalysis, input_control_ratio: float | None = None) -> DriverProfileDisplay:
        """Flattens InteractionOutput to strict DriverProfileDisplay."""
        # STRICT MAPPING
        role_raw = model.role_classification  # Literal
        # Ensure correct formatting for frontend ENUM
        role_key = f"ROLE_{role_raw.upper()}"

        high_dependency = model.high_dependency
        cmd_count = model.imperative_command_count
        strategy = model.strategy

        # Calculate visual hints
        control_pct = input_control_ratio * 100.0 if input_control_ratio is not None else None
        control_pct_display = f"{control_pct:.1f}" if control_pct is not None else None
        input_control_display = f"{int(round(control_pct))}%" if control_pct is not None else None

        # Construct Strict View Model
        return DriverProfileDisplay(
            role_classification=role_key,
            high_dependency=high_dependency,
            imperative_command_count=cmd_count,
            strategy=strategy,
            input_control_ratio=input_control_ratio,
            input_control_ratio_display=input_control_display,
            control_ratio_percent=control_pct,
            control_ratio_display=control_pct_display,
            control_label=self._t("help.control_ratio", "Ohjausaste")
        )

    def _extract_detector_section(self, state: WorkflowState) -> SemanticBlock | None:
        model = state.step_detector

        # Fallback to Panel if not in root steps (though usually root)
        if not model:
            panel = state.step_panel
            if panel and getattr(panel, "performativity_analysis", None):
                model = PerformativityOutput(
                    performativity_analysis=panel.performativity_analysis,
                    thought_process=panel.thought_process,
                    conclusion=panel.conclusion,
                    confidence_score=panel.confidence_score,
                )

        if not model:
            return None

        try:
            display_model = self._transform_detector_data(model)
            return SemanticBlock(id="performativity-check",
                type=BlockType.CARD,
                label=self._get_title(TitleKey.PERFORMATIVITY),
                value=display_model,
            )
        except Exception as e:
            logger.warning(f"BFF Graceful degradation [ProfilerDomainTransformer - Detector]: {e}", exc_info=True)
            return SemanticBlock(
                id="performativity-check",
                type=BlockType.CARD,
                label=self._get_title(TitleKey.PERFORMATIVITY),
                value={},
            )

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

        score = check.authenticity_score
        pct = (score / 3.0) * 100.0 if score is not None else None

        return PerformativityDisplay(
            authenticity_score=score,
            authenticity_score_display=f"{score:.1f}" if score is not None else None,
            authenticity_percent=pct,
            authenticity_percent_display=f"{pct:.1f}" if pct is not None else None,
            authenticity_assessment=check.authenticity_assessment.value,
            authenticity_help=self._t("help.authenticity", "Autenttisuus arvioi onko sisältö aitoa vai tekoälymalleille ominaista performatiivista roolipeliä."),
            heuristics=heuristics,
        )
