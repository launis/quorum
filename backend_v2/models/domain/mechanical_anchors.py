"""Mechanical Anchors domain models.

Defines structured text metrics and performative phrase detection anchors
for grounded LLM prompt compilation.
"""

import logging
from typing import Annotated, Any

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.performativity import PerformativePattern

logger = logging.getLogger(__name__)

__all__ = ["MechanicalAnchorsPayload"]


class MechanicalAnchorsPayload(V2CoreBase):
    """Encapsulates mechanical text metrics and detected patterns for LLM context."""

    model_config = ConfigDict(strict=True, extra="forbid")

    word_count: Annotated[int, Field(ge=0, description="Total word count of source text")] = 0
    say_do_gap: Annotated[float, Field(ge=0.0, description="Calculated say-do gap metric")] = 0.0
    automation_bias: Annotated[float, Field(ge=0.0, description="Automation bias risk score")] = 0.0
    performative_patterns: Annotated[
        list[PerformativePattern],
        Field(
            description="List of detected performative linguistic patterns",
        ),
    ] = Field(default_factory=list)

    @classmethod
    def from_context(cls, data: dict[str, Any] | None) -> MechanicalAnchorsPayload:
        """Extracts mechanical anchors deterministically from LLM context map.

        Args:
            data: Raw context map containing state data or text metrics.

        Returns:
            A strictly validated MechanicalAnchorsPayload instance.
        """
        if not data:
            return cls(performative_patterns=[])

        try:
            from pydantic import BaseModel, ConfigDict

            class _RawContextDTO(BaseModel):
                model_config = ConfigDict(strict=False, extra="ignore")
                word_count: int | float | None = None
                say_do_gap: float | None = None
                automation_bias: float | None = None
                performative_patterns: list[PerformativePattern | dict[str, Any] | str] | None = None
                performative_phrases: list[PerformativePattern | dict[str, Any] | str] | None = None
                raw_inputs: dict[str, Any] | None = None

            ctx = _RawContextDTO.model_validate(data)
            word_count = ctx.word_count
            say_do_gap = ctx.say_do_gap
            automation_bias = ctx.automation_bias
            patterns_raw = ctx.performative_patterns or ctx.performative_phrases

            if ctx.raw_inputs:
                raw_ctx = _RawContextDTO.model_validate(ctx.raw_inputs)
                if word_count is None:
                    word_count = raw_ctx.word_count
                if say_do_gap is None:
                    say_do_gap = raw_ctx.say_do_gap
                if automation_bias is None:
                    automation_bias = raw_ctx.automation_bias
                if patterns_raw is None:
                    patterns_raw = raw_ctx.performative_patterns or raw_ctx.performative_phrases

            patterns: list[PerformativePattern] = []
            if patterns_raw:
                for pat in patterns_raw:
                    if isinstance(pat, PerformativePattern):
                        patterns.append(pat)
                    elif isinstance(pat, str) and pat.strip():
                        patterns.append(
                            PerformativePattern(
                                pattern_id="pat_marker",
                                detected_phrase=pat.strip(),
                                category="linguistic_marker",
                            )
                        )
                    elif isinstance(pat, dict):
                        phrase = pat.get("detected_phrase") or pat.get("phrase")
                        if phrase:
                            pattern_id = pat.get("pattern_id") or pat.get("pattern_name") or "pat_marker"
                            category = pat.get("category") or "linguistic_marker"
                            patterns.append(
                                PerformativePattern(
                                    pattern_id=str(pattern_id),
                                    detected_phrase=str(phrase),
                                    category=str(category),
                                )
                            )

            return cls(
                word_count=int(word_count) if word_count is not None else 0,
                say_do_gap=float(say_do_gap) if say_do_gap is not None else 0.0,
                automation_bias=float(automation_bias) if automation_bias is not None else 0.0,
                performative_patterns=patterns,
            )
        except Exception as e:
            logger.warning("[MechanicalAnchors] Could not parse context: %s", e)
            return cls(performative_patterns=[])

    def to_xml(self) -> str:
        """Generates <mechanical_anchors> XML string for prompt injection.

        Returns:
            Formatted XML representation of mechanical anchors.
        """
        phrase_list = [p.detected_phrase for p in self.performative_patterns if p.detected_phrase]
        phrase_count = len(phrase_list)

        items_xml = "".join(f"      <phrase>{p}</phrase>\n" for p in phrase_list)

        anchors_xml = "<mechanical_anchors>\n"
        anchors_xml += "  <text_metrics>\n"
        anchors_xml += f"    <word_count>{self.word_count}</word_count>\n"
        anchors_xml += f"    <say_do_gap>{self.say_do_gap}</say_do_gap>\n"
        anchors_xml += f"    <automation_bias>{self.automation_bias}</automation_bias>\n"
        anchors_xml += "  </text_metrics>\n"
        anchors_xml += "  <detected_performative_phrases>\n"
        anchors_xml += f"    <phrase_count>{phrase_count}</phrase_count>\n"
        anchors_xml += f"    <items>\n{items_xml}    </items>\n"
        anchors_xml += "  </detected_performative_phrases>\n"
        anchors_xml += "</mechanical_anchors>"
        return anchors_xml
