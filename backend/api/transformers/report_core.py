import logging

from backend.models.enums import HelpTextKey, LabelKey, RiskLevel, TitleKey
from backend.models.view import (
    ReportView, SectionType, SystemNotification, UiSection,
    EvidenceList, EvidenceItem,
    LogicAnalysisDisplay, ToulminDisplay,
    StressTestDisplay, StressFindingDisplay,
    CausalDisplay,
    PerformativityDisplay, HeuristicDisplay
)
from backend.exceptions import AppException, status

from .base import BaseTransformer
from .domain.causal import CausalDomainTransformer
from .domain.compliance import ComplianceDomainTransformer
from .domain.falsification import FalsificationDomainTransformer
from .domain.logic import LogicDomainTransformer
from .domain.overseer import OverseerDomainTransformer
from .domain.profiling import ProfilingDomainTransformer
from .domain.retrieval import RetrievalDomainTransformer

logger = logging.getLogger(__name__)

# Mixin Pattern or Composition?
# Python supports multiple inheritance. Let's use it for the "Monolithic Facade" feel
# while keeping code separate.

class ReportTransformer(
    LogicDomainTransformer,
    ProfilingDomainTransformer,
    ComplianceDomainTransformer,
    FalsificationDomainTransformer,
    CausalDomainTransformer,
    OverseerDomainTransformer,
    RetrievalDomainTransformer,
    BaseTransformer
):
    def transform(self, raw_data: dict, valid_range: tuple[float, float] | None = None) -> ReportView:
        """Transforms raw execution data (dict) into a clean ReportView model.

        Args:
            raw_data: The execution results (WorkflowState dump).
            valid_range: (min, max) tuple for strict score validation. Defaults to Standard Matrix (1-4).
        """
        # STRICT: We prefer WorkflowState but support dict for legacy compatibility
        if not isinstance(raw_data, dict):
             # Future: Raise error if not Pydantic model
             pass
        execution_id = raw_data.get("id")
        if not execution_id:
             # Fail Fast: Strict Schema Requirement
             raise ValueError("Execution data missing mandatory 'id' field.")

        # --- Event Sourcing Adaptation ---
        results = raw_data.get("results", {})

        # Standard: ExecutionResponse.results or WorkflowState (no top-level results)
        # We prioritize the explicit 'results' dict if populated (snapshot).
        steps = {}
        if isinstance(results, dict) and "step_results" in results:
             steps = results["step_results"]
        
        # Fallback: Reconstruct from strict Event Trace (Source of Truth)
        # This covers cases where 'results' is empty/partial (e.g. in-flight execution).
        if not steps and "execution_trace" in raw_data:
             steps = self._reconstruct_state_from_trace(raw_data["execution_trace"])

        sections = []

        # --- A. Score Cards (Support for Multiple Matrices) ---
        judge_keys = ["step_judge", "step_judge_cognitive"]

        for key in judge_keys:
            step_data = steps.get(key)
            if step_data:
                # Determine base title and agent name
                base_title = (
                    self._get_label(LabelKey.ANALYSIS_RESULT)
                    if key == "step_judge"
                    else self._get_label(LabelKey.COGNITIVE_ASSESSMENT)
                )
                base_agent_name = (
                    self._get_label(LabelKey.AGENT_JUDGE)
                    if key == "step_judge"
                    else self._get_label(LabelKey.AGENT_COGNITIVE_JUDGE)
                )

                # Extract all cards (Legacy or V3 Array)
                cards = []
                if "score_cards" in step_data and isinstance(step_data["score_cards"], list):
                     cards = step_data["score_cards"]
                elif "score_card" in step_data:
                     cards = [step_data["score_card"]]
                else:
                     cards = [step_data] # Legacy fallback where step is the card

                for idx, card in enumerate(cards):
                    try:
                        # Fail Fast: Try/Except used for context logging, BUT we re-raise.

                        # Use specific agent name from card if available
                        card_agent_name = card.get("agent_name") or base_agent_name

                        # Construct title
                        if len(cards) > 1 or card_agent_name != base_agent_name:
                                card_title = f"{base_title} ({card_agent_name})"
                        else:
                                card_title = base_title

                        # Extract score data using the CARD as the source.
                        # STRICT: Card must self-contain scale info if valid_range is None.
                        score_data = self._extract_score_data(card, agent_name=card_agent_name, valid_range=valid_range)

                        # Create unique ID for the section
                        section_id = f"score-card-{key}"
                        if idx > 0:
                            section_id += f"-{idx}"

                        sections.append(
                            UiSection(id=section_id, type=SectionType.SCORE_CARD, title=card_title, data=score_data or {})
                        )
                    except ValueError as e:
                        logger.error(f"Score validation failed for {key} (card {idx}): {e}")
                        raise AppException(f"Score validation failed for {key}: {e}", 500) from e
                    except Exception as e:
                        raise AppException(f"Unexpected error in score card processing: {e}", 500) from e

        # --- A2. Key Metrics (Usage & Cost) ---
        usage_section = self._extract_usage_section(raw_data)
        if usage_section:
            sections.append(usage_section)

        # --- B. XAI Report ---
        xai_section = self._build_xai_section(steps)
        if xai_section:
            sections.append(xai_section)

        # --- B2. Generic Data Sections (Versatile Reporting) ---
        # Domain Mixins handle these
        guard_grid = self._extract_guard_grid(steps)
        if guard_grid:
            sections.append(guard_grid)

        analyst_table = self._extract_analyst_table(steps)
        if analyst_table:
            sections.append(analyst_table)

            # Helper: Extract Evidence separately if present
            evidence = self._extract_analyst_evidence(steps)
            if evidence:
                sections.append(evidence)

        profiler_section = self._extract_profiler_section(steps)
        if profiler_section:
            sections.append(profiler_section)


        # RetrievalDomainTransformer handles this
        context_section = self._extract_context_section(steps)
        if context_section:
            sections.append(context_section)

        # --- SPECIALIST BACKBONE (Courtroom 3.0) ---

        # 1. Logic / Logician
        logician = self._extract_logician_section(steps)
        if logician:
             sections.append(logician)

        # 2. Falsification / Falsifier
        falsifier = self._extract_falsifier_section(steps)
        if falsifier:
             sections.append(falsifier)

        # 3. Causal / Causal Analyst
        causal = self._extract_causal_section(steps)
        if causal:
             sections.append(causal)

        # 4. Performativity / Detector
        detector = self._extract_detector_section(steps)
        if detector:
             sections.append(detector)

        # 5. Facts & Ethics / Overseer
        overseer = self._extract_overseer_section(steps)
        if overseer:
             sections.append(overseer)

        interaction_grid = self._extract_interaction_section(steps)
        if interaction_grid:
            sections.append(interaction_grid)

        coach_section = self._extract_coach_section(steps)
        if coach_section:
            sections.append(coach_section)

        archivist_section = self._extract_archivist_section(steps)
        if archivist_section:
            sections.append(archivist_section)

        # --- C. Timeline ---
        timeline_events = self._build_timeline(steps)

        sections.append(
            UiSection(
                id="unified-timeline",
                type=SectionType.TIMELINE_FEED,
                title=self._get_title(TitleKey.TIMELINE),
                data={"events": timeline_events},
            )
        )

        theme = "success"

        # Extract Metrics from context_variables (if available)
        metrics = None
        context = raw_data.get("context_variables", {})
        if not context and "results" in raw_data:
             context = raw_data["results"].get("context_variables", {})

        if context:
            metrics = context.get("audit_metrics")

        # --- D. Dynamic Theming & Notifications ---
        status_theme, notification = self._determine_report_status(metrics, guard_grid)

        return ReportView(
            view_id=execution_id,
            status_theme=status_theme,
            sections=sections,
            metrics=metrics,
            system_notification=notification
        )




    def _determine_report_status(self, metrics: dict | None, guard_section: UiSection | None) -> tuple[str, SystemNotification | None]:
        """Calculates the Report Theme (Success/Warning/Danger) based on heuristics."""
        theme = "success"
        notification = None

        # 1. Security Check (Danger)
        if guard_section:
            # We need to peek into the data. UiSection.data is a dict.
            # SecurityDisplay was dumped into 'security_display' key.
            sec_data = guard_section.data.get("security_display", {})
            risk = sec_data.get("risk_level")

            if risk == RiskLevel.HIGH.value:
                theme = "danger"
                notification = SystemNotification(
                    title="TURVALLISUUSRISKI",
                    message="Raportissa on havaittu kriittisiä tietoturvariskejä. Tarkista 'Turvallisuus & Tietosuoja' -osio välittömästi.",
                    level="danger"
                )
                return theme, notification

        # 2. Activity Check (Warning)
        # Low Control Ratio (< 0.3) implies low user agency / high automation
        if metrics:
            cr = metrics.get("control_ratio", 0.5)
            # Handle float or dict (if nested) - simplify for now assuming float from hook
            if isinstance(cr, (float, int)) and cr < 0.3:
                theme = "warning"
                notification = SystemNotification(
                    title="ALHAINEN INTERAKTIO",
                    message="Käyttäjän osuus sisällöstä on alle 30%. Raportti saattaa sisältää merkittävästi tekoälyn hallusinoimaa sisältöä.",
                    level="warning"
                )
                return theme, notification

        return theme, notification

    def _extract_score_data(self, judge_step: dict, agent_name: str, valid_range: tuple[float, float] | None) -> dict:
        """Extracts score and verdict from V3 Schema."""
        score = None
        raw_score = None
        verdict = None
        dimensions = []

        # 1. Primary Source: 'score_cards' (V3 Standard)
        if "score_card" in judge_step:
            card = judge_step["score_card"]
            raw_score = card.get("total_score")
            verdict = card.get("final_verdict")
            dimensions = card.get("dimensions", [])
        elif "score_cards" in judge_step and isinstance(judge_step["score_cards"], list) and judge_step["score_cards"]:
            card = judge_step["score_cards"][0]
            raw_score = card.get("total_score")
            verdict = card.get("verdict")
            dimensions = card.get("dimensions", [])
        else:
            # V3 Fallback
            raw_score = judge_step.get("total_score")
            verdict = judge_step.get("final_verdict")
            dimensions = judge_step.get("dimensions", [])

        # 2. Validation
        if raw_score is None:
            raise ValueError(f"Score is missing from Judge step ({agent_name}). Expected 'total_score'.")

        try:
            score = float(raw_score)
        except (TypeError, ValueError):
            raise ValueError(f"Score '{raw_score}' is not a valid number.") from None

        # STRICT SCALE AUTHORITY CHECK
        if valid_range is None:
            s_min = judge_step.get("scale_min")
            s_max = judge_step.get("scale_max")

            if s_min is not None and s_max is not None:
                valid_range = (float(s_min), float(s_max))
            else:
                raise ValueError(f"Score validation failed for {agent_name}: No scale definition found.")

        scale_min, scale_max = valid_range
        if not (scale_min <= score <= scale_max):
            raise ValueError(f"Score {score} is out of valid range [{scale_min}, {scale_max}].")

        if not verdict:
            verdict = ""

        return {
            "agent_name": agent_name,
            "total_score": score,
            "min_score": int(scale_min),
            "max_score": int(scale_max),
            "verdict": verdict,
            "dimensions": dimensions,
        }

    def _build_xai_section(self, steps: dict) -> UiSection | None:
        if "step_xai" not in steps:
            return None

        xai = steps["step_xai"]
        content = xai.get("xai_report_formatted")

        if not content:
            content = xai.get("final_verdict")

        if not content:
            return None

        return UiSection(
            id="xai-summary",
            type=SectionType.MARKDOWN_BLOCK,
            title=self._get_label(LabelKey.AI_REASONING),
            data={"content": content},
        )

    def _build_timeline(self, steps: dict) -> list[dict]:
        events = []
        agent_names = {
            "step_guard": f"🛡️ {self._get_label(LabelKey.AGENT_GUARD)}",
            "step_analyst": f"🔎 {self._get_label(LabelKey.AGENT_ANALYST)}",
            "step_interaction": f"🤝 {self._get_label(LabelKey.AGENT_INTERACTION)}",
            "step_profiler": f"🧠 {self._get_label(LabelKey.AGENT_PROFILER)}",
            "step_logician": f"📐 {self._get_label(LabelKey.AGENT_LOGICIAN)}",
            "step_falsifier": f"🧪 {self._get_label(LabelKey.AGENT_FALSIFIER)}",
            "step_causal": f"🔗 {self._get_label(LabelKey.AGENT_CAUSAL)}",
            "step_detector": f"🎭 {self._get_label(LabelKey.AGENT_DETECTOR)}",
            "step_judge": f"⚖️ {self._get_label(LabelKey.AGENT_JUDGE)}",
            "step_judge_cognitive": f"⚖️ {self._get_label(LabelKey.AGENT_COGNITIVE_JUDGE)}",
            "step_coach": f"🎓 {self._get_label(LabelKey.AGENT_COACH)}",
            "step_xai": f"📝 {self._get_label(LabelKey.AGENT_REPORTER)}",
        }

        for step_key, step_data in steps.items():
            if not isinstance(step_data, dict):
                continue

            meta = step_data.get("metadata", {})
            timestamp = meta.get("luontiaika")
            agent_label = agent_names.get(step_key, step_key)

            # 1. Reasoning Trace (The thinking process)
            rt = step_data.get("reasoning_trace")
            if rt:
                events.append(
                    {
                        "timestamp": timestamp,
                        "actor": agent_label,
                        "label": agent_label,
                        "type": "reasoning",
                        "message": str(rt)[:250] + "...",
                        "content": str(rt)[:250] + "...",
                        "compliance_help": self._t(HelpTextKey.ARCHIVIST.value, default="Archivist Help"),
                        "bloom_help": self._t(HelpTextKey.BLOOM.value, default="Bloom Help"),
                        "strategic_help": self._t(HelpTextKey.STRATEGIC_DEPTH.value, default="Strategic Depth Help"),
                        "fidelity_help": self._t(HelpTextKey.FIDELITY.value, default="Fidelity Help"),
                        "help_abductive": self._t(HelpTextKey.ABDUCTIVE.value, default="Abductive Help"),
                        "authenticity_help": self._t(HelpTextKey.AUTHENTICITY.value, default="Authenticity Help"),
                    }
                )

            # 2. Audit Logs
            if "audit_logs" in meta and isinstance(meta["audit_logs"], list):
                for log in meta["audit_logs"]:
                    if log.get("role") == "system":
                        continue

                    content = log.get("content", "")
                    clean_msg = content.replace("<<REFERENCE:", "[Viittaus:").replace(">>", "]")

                    events.append(
                        {
                            "timestamp": timestamp,
                            "actor": agent_label,
                            "label": agent_label,
                            "type": "log",
                            "message": clean_msg,
                            "content": clean_msg,
                        }
                    )

        return sorted(events, key=lambda x: x.get("timestamp") or "")

    def _extract_analyst_table(self, steps: dict) -> UiSection | None:
        step = steps.get("step_analyst")
        if not step or not isinstance(step, dict):
            return None

        hypotheses = step.get("hypotheses") or step.get("hypoteesit", [])
        if not hypotheses:
            return None

        rows = []
        for h in hypotheses:
            h_data = h if isinstance(h, dict) else h.dict()
            rows.append({
                "id": h_data.get("id"),
                "claim": h_data.get("claim_text") or h_data.get("vaite_teksti"),
                # Explicit boolean conversion
                "proven": "✅" if (h_data.get("evidence_found") or h_data.get("loytyyko_todisteita")) else "❌",
            })

        # Enhancement: Include RAG Evidence if available
        rag_evidence = step.get("rag_evidence")
        evidence_content = ""
        if rag_evidence:
             evidence_content = f"### {self._get_label(LabelKey.EVIDENCE_FOUND)}\n"
             for item in rag_evidence:
                 evidence_content += f"- {item}\n"

        return UiSection(
            id="hypotheses-table",
            type=SectionType.DATA_TABLE,
            title=self._get_title(TitleKey.HYPOTHESES),
            data={
                "columns": [
                    {"key": "id", "label": self._get_label(LabelKey.ID)},
                    {"key": "claim", "label": self._get_label(LabelKey.CLAIM)},
                    {"key": "proven", "label": self._get_label(LabelKey.VERIFIED)},
                ],
                "rows": rows,
                # New field for Evidence (handled by frontend if present, or we create separate section)
                "rag_evidence": rag_evidence or [] 
            },
        )
        
    def _extract_analyst_evidence(self, steps: dict) -> UiSection | None:
        """Helper to extract RAG evidence as a separate section if needed."""
        step = steps.get("step_analyst")
        if not step:
            return None
        
        rag_evidence = step.get("rag_evidence")
        if not rag_evidence:
            return None
            
        items = []
        for i, item in enumerate(rag_evidence):
             items.append(
                 EvidenceItem(
                     id=f"evidence-{i}",
                     source="RAG Search",
                     content=item,
                     score=1.0, 
                     type="concept"
                 )
             )
            
        return UiSection(
            id="analyst-evidence",
            type=SectionType.EVIDENCE_LIST,
            title=self._get_label(LabelKey.EVIDENCE_FOUND),
            data=EvidenceList(items=items, total_count=len(items)),
        )

    def _extract_usage_section(self, raw_data: dict) -> UiSection | None:
        """Extracts usage and cost metrics from raw execution data."""
        # 1. Check for usage in top-level or result
        usage = raw_data.get("usage") or raw_data.get("result", {}).get("usage")

        if not usage:
            return None

        data = {
            "total_tokens": usage.get("total_tokens", 0),
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "cost_estimate": usage.get("cost", 0.0)
        }

        return UiSection(
            id="usage-stats",
            type=SectionType.USAGE_STATS,
            title=self._get_title(TitleKey.USAGE),
            data=data
        )
