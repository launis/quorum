import logging
from typing import Any

from backend.exceptions import AppException
from backend.models.domain import ArchivistOutput
from backend.models.enums import LabelKey, RiskLevel, TitleKey
from backend.models.state import WorkflowState

# UVM: Use strict extensions
from backend.models.view.semantic_models import ArchivistDisplay, BlockType, SecurityDisplay, SemanticBlock

# Deprecated: Legacy imports removed
from ..base import BaseTransformer

logger = logging.getLogger(__name__)


class ComplianceDomainTransformer(BaseTransformer):
    def _adapt_legacy_trace(self, data: dict[str, Any]) -> dict[str, Any]:
        """Helper to adapt legacy reasoning_trace string to strict ReasoningTraceDTO."""
        if "reasoning_trace" in data and "thought_process" not in data:
            data = data.copy()
            data["thought_process"] = data.pop("reasoning_trace")
            data["conclusion"] = "Implicit in Analysis"
            data["confidence_score"] = 1.0
        return data

    def _extract_guard_grid(self, state: WorkflowState) -> SemanticBlock | None:
        model = state.step_guard
        if not model:
            return None

        # Check if empty (some steps might be skipped)
        if not getattr(model, "security_check", None):
             return None

        sec = model.security_check

        # Logic: Derived Presentation
        threat = sec.threat_detected
        risk = sec.risk_level  # Enum: RiskLevel.HIGH etc.
        risk_val = risk.value  # "RISK_HIGH"

        # Color Logic (BFF Decision)
        if risk == RiskLevel.HIGH:
            r_color = "red"
        elif risk == RiskLevel.MEDIUM:
            r_color = "orange"
        else:
            r_color = "green"

        anon = sec.anonymized

        # Findings (List of strings)
        findings = sec.pii_findings

        # UVM SecurityDisplay (Strict)
        try:
            s_display = SecurityDisplay(
                threat_detected=threat,
                threat_label="DETECTED" if threat else "CLEAN",
                threat_color="red" if threat else "green",
                risk_level=risk_val,
                risk_label=risk_val,
                risk_color=r_color,
                anonymized=anon,
                anonymized_label="ANONYMIZED" if anon else "RAW",
                anonymized_color="blue" if anon else "orange",
                findings=findings,
            )
        except Exception as e:
            raise AppException(f"Failed to create SecurityDisplay: {e}", 500) from e

        try:
            display_dict = s_display.model_dump()
            display_dict["findings_label"] = self._t("lblFindings", "Löydökset")
            display_dict["no_findings_label"] = self._t("lblNoSignificantFindings", "Ei merkittäviä löydöksiä.")
            
            return SemanticBlock(id="security-grid",
                type=BlockType.DATA_GRID,
                label=self._get_title(TitleKey.SECURITY),
                value={"security_display": display_dict},
            )
        except Exception as e:
            raise AppException(f"Failed to create SecurityGrid block: {e}", 500) from e

    def _extract_archivist_section(self, state: WorkflowState) -> SemanticBlock | None:
        model = state.step_archivist
        if not model:
            return None

        try:
            display_model = self._transform_archivist_data(model)
            return SemanticBlock(id="archivist-check",
                type=BlockType.CARD,
                label=self._get_title(TitleKey.ARCHIVIST),
                value=display_model,
            )
        except Exception as e:
            raise AppException(f"Failed to transform Archivist display: {e}", 500) from e

    def _transform_archivist_data(self, model: ArchivistOutput) -> ArchivistDisplay:
        """Flattens ArchivistOutput and calculates SDUI properties."""
        # Display Mapping
        comp_score = model.compliance_score
        comp_analysis = model.compliance_analysis
        comp_desc = model.description

        # Strict mapping: Convert relevant cases to strings for display list
        recs = [c.summary for c in model.relevant_cases]

        return ArchivistDisplay(
            compliance_score=comp_score,
            compliance_score_display=f"{comp_score:.1f}" if comp_score is not None else "N/A",
            compliance_analysis=comp_desc or comp_analysis,
            compliance_help=self._t("help.compliance", "Säädöstenmukaisuus arvioi tekstin lakiteknistä pätevyyttä."),
            recommendations=recs,
        )

    def _extract_coach_section(self, state: WorkflowState) -> SemanticBlock | None:
        model = state.step_coach
        if not model:
            return None

        # Content Construction (Markdown)
        content = ""
        if model.focus_areas:
            content += f"### {self._get_label(LabelKey.FOCUS_AREAS)}\n"
            content += "\n".join([f"- {item}" for item in model.focus_areas]) + "\n\n"

        if model.actionable_steps:
            content += f"### {self._get_label(LabelKey.ACTIONABLE_STEPS)}\n"
            content += "\n".join([f"- {item}" for item in model.actionable_steps]) + "\n\n"

        if model.bibliography:
            content += f"### {self._get_label(LabelKey.REFERENCES)}\n"
            for ref in model.bibliography:
                # ref is BibliographyItem
                author = getattr(ref, 'author', '') or ''
                year = getattr(ref, 'year', '') or ''
                title = getattr(ref, 'title', '') or ''
                cit = f"{author} {year}. {title}."
                content += f"- {cit}\n"

        return SemanticBlock(id="coach-markdown",
            type=BlockType.PARAGRAPH,
            label=self._get_title(TitleKey.COACH),
            value={"content": content},
        )


