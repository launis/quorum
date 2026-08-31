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
            source = data
            try:
                raw_inputs = data.get("raw_inputs")
            except AttributeError, TypeError:
                raw_inputs = None

            if raw_inputs:
                try:
                    if (
                        "word_count" not in source
                        and "say_do_gap" not in source
                        and "automation_bias" not in source
                        and "performative_patterns" not in source
                        and "performative_phrases" not in source
                    ):
                        source = raw_inputs
                except TypeError, KeyError:
                    pass

            try:
                raw_wc = source.get("word_count")
                raw_sd = source.get("say_do_gap")
                raw_ab = source.get("automation_bias")
            except AttributeError, TypeError:
                raw_wc = raw_sd = raw_ab = None

            word_count = int(raw_wc) if isinstance(raw_wc, (int, float)) else 0
            say_do_gap = float(raw_sd) if isinstance(raw_sd, (int, float)) else 0.0
            automation_bias = float(raw_ab) if isinstance(raw_ab, (int, float)) else 0.0

            raw_patterns = None
            try:
                raw_patterns = source.get("performative_patterns") or source.get("performative_phrases")
            except AttributeError, TypeError:
                pass

            if raw_patterns is None and raw_inputs:
                try:
                    raw_patterns = raw_inputs.get("performative_patterns") or raw_inputs.get("performative_phrases")
                except AttributeError, TypeError:
                    pass

            patterns: list[PerformativePattern] = []
            if isinstance(raw_patterns, list):
                for item in raw_patterns:
                    match item:
                        case PerformativePattern():
                            patterns.append(item)
                        case str() if item.strip():
                            patterns.append(
                                PerformativePattern(
                                    pattern_id="pat_marker",
                                    detected_phrase=item.strip(),
                                    category="linguistic_marker",
                                )
                            )
                        case _:
                            try:
                                phrase = item.get("detected_phrase") or item.get("phrase")
                                if phrase and isinstance(phrase, str):
                                    pat_id = item.get("pattern_id") or item.get("pattern_name") or "pat_marker"
                                    cat = item.get("category") or "linguistic_marker"
                                    patterns.append(
                                        PerformativePattern(
                                            pattern_id=str(pat_id),
                                            detected_phrase=phrase,
                                            category=str(cat),
                                        )
                                    )
                            except AttributeError, TypeError:
                                pass

            return cls(
                word_count=max(0, word_count),
                say_do_gap=max(0.0, say_do_gap),
                automation_bias=max(0.0, automation_bias),
                performative_patterns=patterns,
            )
        except (ValueError, TypeError) as e:
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
