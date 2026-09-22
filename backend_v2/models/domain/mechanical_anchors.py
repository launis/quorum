"""Mechanical Anchors domain models.

Defines structured text metrics and performative phrase detection anchors
for grounded LLM prompt compilation.
"""

import logging
from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.performativity import PerformativePattern
from backend_v2.models.dtos.prompt import LLMContextDataDTO

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
    def from_context(cls, data: LLMContextDataDTO | None = None) -> MechanicalAnchorsPayload:
        """Extracts mechanical anchors deterministically from LLM context map.

        Args:
            data: LLM context data DTO or mapping containing state data or text metrics.

        Returns:
            A strictly validated MechanicalAnchorsPayload instance.
        """
        if not data:
            return cls(performative_patterns=[])

        if isinstance(data, LLMContextDataDTO):
            source = data.inputs if data.inputs is not None else data.raw_inputs
            raw_inputs = data.raw_inputs
        else:
            source = data
            raw_inputs = data["raw_inputs"] if (data is not None and "raw_inputs" in data) else None
            if (
                raw_inputs
                and "word_count" not in source
                and "say_do_gap" not in source
                and "automation_bias" not in source
                and "performative_patterns" not in source
                and "performative_phrases" not in source
            ):
                source = raw_inputs

        raw_wc = source["word_count"] if (source is not None and "word_count" in source) else None
        raw_sd = source["say_do_gap"] if (source is not None and "say_do_gap" in source) else None
        raw_ab = source["automation_bias"] if (source is not None and "automation_bias" in source) else None

        word_count = int(raw_wc) if isinstance(raw_wc, (int, float)) else 0
        say_do_gap = float(raw_sd) if isinstance(raw_sd, (int, float)) else 0.0
        automation_bias = float(raw_ab) if isinstance(raw_ab, (int, float)) else 0.0

        raw_patterns = None
        if source is not None and "performative_patterns" in source:
            raw_patterns = source["performative_patterns"]
        elif source is not None and "performative_phrases" in source:
            raw_patterns = source["performative_phrases"]
        elif raw_inputs is not None and "performative_patterns" in raw_inputs:
            raw_patterns = raw_inputs["performative_patterns"]
        elif raw_inputs is not None and "performative_phrases" in raw_inputs:
            raw_patterns = raw_inputs["performative_phrases"]

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
                        patterns.append(PerformativePattern.model_validate(item))

        return cls(
            word_count=max(0, word_count),
            say_do_gap=max(0.0, say_do_gap),
            automation_bias=max(0.0, automation_bias),
            performative_patterns=patterns,
        )

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
