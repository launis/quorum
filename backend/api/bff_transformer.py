import logging
from typing import Any

from backend.models.view import AssessmentView, ReportView, SectionType, UiSection, StepProgressItem
from backend.services.localization import LocalizationService

logger = logging.getLogger(__name__)


class ReportTransformer:
    def __init__(self, language: str = "en"):
        self.language = language
        self.loc = LocalizationService()

    def _t(self, key: str, default: str) -> str:
        return self.loc.get(key, self.language, default)

    def transform(self, raw_data: dict, valid_range: tuple[float, float] | None = None) -> ReportView:
        """Transforms raw execution data (dict) into a clean ReportView model.

        Args:
            raw_data: The execution results (WorkflowState dump).
            valid_range: (min, max) tuple for strict score validation. Defaults to Standard Matrix (1-4).
        """
        execution_id = raw_data.get("id") or raw_data.get("execution_id") or "unknown"

        # --- Event Sourcing Adaptation ---
        # 1. Try to get results from simplified key (legacy / persisted summary)
        results = raw_data.get("results", {})

        # 2. If results empty, check for 'step_results' directly (legacy)
        steps = {}
        if "step_results" in results:
            steps = results["step_results"]
        elif "step_results" in raw_data:
            steps = raw_data["step_results"]

        # 3. If still empty, reconstruct from strict Event Trace (New Architecture)
        if not steps and "execution_trace" in raw_data:
            steps = self._reconstruct_state_from_trace(raw_data["execution_trace"])
        elif not steps and "execution_trace" in results:
            steps = self._reconstruct_state_from_trace(results["execution_trace"])

        sections = []

        # --- A. Score Cards (Support for Multiple Matrices) ---
        judge_keys = ["step_judge", "step_judge_cognitive"]

        for key in judge_keys:
            step_data = steps.get(key)
            if step_data:
                # Determine base title and agent name
                base_title = (
                    self._t("Analysis Result", "Analyysin Tulos")
                    if key == "step_judge"
                    else self._t("Cognitive Assessment", "Kognitiivinen Arvio")
                )
                base_agent_name = (
                    self._t("Judge", "Tuomari")
                    if key == "step_judge"
                    else self._t("Cognitive Judge", "Kognitiivinen Tuomari")
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
                        # Use specific agent name from card if available
                        # This enables "Judge (matrix_v1)" vs "Judge (matrix_v2)" differentiation
                        card_agent_name = card.get("agent_name") or base_agent_name
                        
                        # Construct title
                        # If we have multiple cards or different name, append it
                        if len(cards) > 1 or card_agent_name != base_agent_name:
                             # E.g. "Analyysin Tulos (Judge (matrix_standard_v1))"
                             card_title = f"{base_title} ({card_agent_name})"
                        else:
                             card_title = base_title

                        # Extract score data using the CARD as the source
                        # valid_range is ignored if card has its own scale_min/max
                        score_data = self._extract_score_data(card, agent_name=card_agent_name, valid_range=valid_range)

                        # Create unique ID for the section
                        # If index > 0, append index to avoid collision
                        section_id = f"score-card-{key}"
                        if idx > 0:
                            section_id += f"-{idx}"

                        sections.append(
                            UiSection(id=section_id, type=SectionType.SCORE_CARD, title=card_title, data=score_data)
                        )
                    except ValueError as e:
                        logger.error(f"Score validation failed for {key} (card {idx}): {e}")
                        # Continue to next card

        # --- A2. Key Metrics (Usage & Cost) ---
        usage_section = self._extract_usage_section(raw_data)
        if usage_section:
            sections.append(usage_section)

        # --- B. XAI Report ---
        xai_section = self._build_xai_section(steps)
        if xai_section:
            sections.append(xai_section)

        # --- B2. Generic Data Sections (Versatile Reporting) ---
        guard_grid = self._extract_guard_grid(steps)
        if guard_grid:
            sections.append(guard_grid)

        analyst_table = self._extract_analyst_table(steps)
        if analyst_table:
            sections.append(analyst_table)

        profiler_section = self._extract_profiler_section(steps)
        if profiler_section:
            sections.append(profiler_section)

        # --- SPECIALIST BACKBONE (Courtroom 3.0) ---
        panel = steps.get("step_panel", {})

        # 1. Logic / Logician
        logician_data = steps.get("step_logician") or panel.get("logician_data") or panel.get("logiikka_auditointi")
        if logician_data:
            sections.append(
                UiSection(
                    id="logic-analysis",
                    type=SectionType.LOGIC_ANALYSIS,
                    title=self._t("Logic Analysis", "Logiikka-analyysi"),
                    data=self._transform_logician_data(logician_data if isinstance(logician_data, dict) else logician_data.dict()),
                )
            )

        # 2. Falsification / Falsifier
        falsifier_data = steps.get("step_falsifier") or panel.get("falsifier_data") or panel.get("falsifiointi_auditointi")
        if falsifier_data:
            sections.append(
                UiSection(
                    id="stress-test",
                    type=SectionType.STRESS_TEST,
                    title=self._t("Falsification & Stress Test", "Falsifiointi & Stressitesti"),
                    data=self._transform_falsifier_data(falsifier_data if isinstance(falsifier_data, dict) else falsifier_data.dict()),
                )
            )

        # 3. Causal / Causal Analyst
        causal_data = steps.get("step_causal") or panel.get("causal_analysis") or panel.get("kausaalinen_auditointi")
        if causal_data:
            sections.append(
                UiSection(
                    id="causal-analysis",
                    type=SectionType.CAUSAL_ANALYSIS,
                    title=self._t("Causal Audit", "Kausaalinen Auditointi"),
                    data=self._transform_causal_data(causal_data if isinstance(causal_data, dict) else causal_data.dict()),
                )
            )

        # 4. Performativity / Detector
        detector_data = steps.get("step_detector") or panel.get("performativity_analysis") or panel.get("performatiivisuus_auditointi")
        if detector_data:
            sections.append(
                UiSection(
                    id="performativity-check",
                    type=SectionType.PERFORMATIVITY_CHECK,
                    title=self._t("Performativity Check", "Performatiivisuustarkistus"),
                    data=self._transform_detector_data(detector_data if isinstance(detector_data, dict) else detector_data.dict()),
                )
            )

        # 5. Facts & Ethics / Overseer
        overseer_data = steps.get("step_overseer") or panel.get("overseer_data") or panel.get("etiikka_ja_fakta")
        if overseer_data:
            sections.append(
                UiSection(
                    id="fact-check",
                    type=SectionType.FACT_CHECK,
                    title=self._t("Facts & Ethics", "Fakta & Etiikka"),
                    data=self._transform_overseer_data(overseer_data if isinstance(overseer_data, dict) else overseer_data.dict()),
                )
            )

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
        # Pass trace directly if available for better fidelity?
        # For now, existing logic uses step timestamps, which we have in 'steps' (metadata).
        # We could enhance _build_timeline to check trace as well.
        timeline_events = self._build_timeline(steps)

        # Enhancement: If we have pure trace, maybe verify timeline against it?
        # But 'steps' is derived from trace, so it should be consistent.

        sections.append(
            UiSection(
                id="unified-timeline",
                type=SectionType.TIMELINE_FEED,
                title=self._t("Process Timeline", "Prosessin Eteneminen"),
                data={"events": timeline_events},
            )
        )

        theme = "success"

        return ReportView(view_id=execution_id, status_theme=theme, sections=sections)

    def _reconstruct_state_from_trace(self, trace: list[dict[str, Any]]) -> dict[str, Any]:
        """Reconstructs the 'step_results' map from an append-only linear trace."""
        reconstructed = {}

        for event in trace:
            # We are interested in OUTPUT events
            if event.get("event_type") == "output":
                step_name = event.get("step_name")
                if not step_name or not isinstance(step_name, str):
                    continue

                content = event.get("content", {})

                # Check for reasoning trace availability (optional optimization)
                # If the event has 'reasoning', we could inject it into content for UI visibility
                reasoning = event.get("reasoning")
                if reasoning:
                    if isinstance(reasoning, dict):
                        # Flatten relevant reasoning fields into content/metadata for UI
                        # e.g. "reasoning_trace" key used by timeline builder
                        content["reasoning_trace"] = reasoning.get("thought_process")

                # Timestamp to metadata
                timestamp = event.get("timestamp") or event.get("metadata", {}).get("timestamp")
                if timestamp:
                    if content.get("metadata") is None:
                        content["metadata"] = {}
                    content["metadata"]["luontiaika"] = timestamp

                reconstructed[step_name] = content

        return reconstructed

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
            title=self._t("AI Reasoning", "Tekoälyn Perustelut"),
            data={"content": content},
        )

    def _build_timeline(self, steps: dict) -> list[dict]:
        events = []
        agent_names = {
            "step_guard": f"🛡️ {self._t('Guard', 'Vartija')}",
            "step_analyst": f"🔎 {self._t('Analyst', 'Analyytikko')}",
            "step_interaction": f"🤝 {self._t('Interaction', 'Vuorovaikutus')}",
            "step_profiler": f"🧠 {self._t('Profiler', 'Profiloija')}",
            "step_logician": f"📐 {self._t('Logician', 'Loogikko')}",
            "step_falsifier": f"🧪 {self._t('Falsifier', 'Falsifioija')}",
            "step_causal": f"🔗 {self._t('Causal', 'Kausaalisuus')}",
            "step_detector": f"🎭 {self._t('Detector', 'Ilmaisunvalvoja')}",
            "step_judge": f"⚖️ {self._t('Judge', 'Tuomari')}",
            "step_judge_cognitive": f"⚖️ {self._t('Cognitive Judge', 'Kognitiivinen Tuomari')}",
            "step_coach": f"🎓 {self._t('Coach', 'Valmentaja')}",
            "step_xai": f"📝 {self._t('Reporter', 'Raportoija')}",
        }

        for step_key, step_data in steps.items():
            if not isinstance(step_data, dict):
                continue

            meta = step_data.get("metadata", {})
            timestamp = meta.get("luontiaika")
            agent_label = agent_names.get(step_key, step_key)

            # 1. Reasoning Trace (The thinking process)
            # Replaced "reasoning_trace" check with potential injected one from _reconstruct
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
            rows.append(
                {
                    "id": h_data.get("id"),
                    "claim": h_data.get("claim_text") or h_data.get("vaite_teksti"),
                    "proven": "✅" if (h_data.get("evidence_found") or h_data.get("loytyyko_todisteita")) else "❌",
                }
            )

        return UiSection(
            id="hypotheses-table",
            type=SectionType.DATA_TABLE,
            title=self._t("Analyst Hypotheses", "Analyytikon Hypoteesit"),
            data={
                "columns": [
                    {"key": "id", "label": self._t("ID", "ID")},
                    {"key": "claim", "label": self._t("Claim", "Väite")},
                    {"key": "proven", "label": self._t("Verified", "Vahvistettu")},
                ],
                "rows": rows,
            },
        )

    def _extract_guard_grid(self, steps: dict) -> UiSection | None:
        step = steps.get("step_guard")
        if not step or not isinstance(step, dict):
            return None

        sec = step.get("security_check", {})
        if not sec:
            return None

        return UiSection(
            id="security-grid",
            type=SectionType.KEY_VALUE_GRID,
            title=self._t("Security Check", "Turvatarkastus"),
            data={
                "items": [
                    {
                        "label": self._t("Threat Detected", "Uhka Havaittu"),
                        "value": self._t("Yes", "Kyllä") if (sec.get("threat_detected") or sec.get("uhka_havaittu")) else self._t("No", "Ei"),
                        "highlight": sec.get("threat_detected") or sec.get("uhka_havaittu"),
                    },
                    {"label": self._t("Risk Level", "Riski Taso"), "value": sec.get("risk_level") or sec.get("riski_taso", "N/A")},
                    {
                        "label": self._t("Anonymized", "Anonymisoitu"),
                        "value": self._t("Yes", "Kyllä") if (sec.get("anonymized") or sec.get("anonymisointi_tehty")) else self._t("No", "Ei"),
                    },
                ]
            },
        )

    def _extract_profiler_section(self, steps: dict) -> UiSection | None:
        step = steps.get("step_profiler")
        if not step or not isinstance(step, dict):
            return None

        return UiSection(
            id="profiler-analysis",
            type=SectionType.PROFILER_ANALYSIS,
            title=self._t("Profiler Analysis", "Profiloijan Analyysi"),
            data=self._transform_profiler_data(step),
        )

    def _transform_profiler_data(self, step: dict) -> dict:
        """Pass-through for Profiler Schema (Frontend now supports English)."""
        return step.copy()

    def _extract_interaction_section(self, steps: dict) -> UiSection | None:
        step = steps.get("step_interaction")
        if not step or not isinstance(step, dict):
            return None

        return UiSection(
            id="interaction-grid",
            type=SectionType.DRIVER_PROFILE,
            title=self._t("Interaction & Roles", "Vuorovaikutus & Roolitus"),
            data=self._transform_interaction_data(step),
        )

    def _transform_interaction_data(self, step: dict) -> dict:
        """Pass-through for Interaction Schema (Frontend now supports English)."""
        return step.copy()

    def _extract_coach_section(self, steps: dict) -> UiSection | None:
        step = steps.get("step_coach")
        if not step or not isinstance(step, dict):
            return None

        # 1. New English Schema (CoachingPlan)
        if "actionable_steps" in step or "focus_areas" in step:
            content = ""
            if "focus_areas" in step and step["focus_areas"]:
                content += f"### {self._t('Focus Areas', 'Painopisteet')}\n"
                content += "\n".join([f"- {item}" for item in step["focus_areas"]]) + "\n\n"
            
            if "actionable_steps" in step and step["actionable_steps"]:
                content += f"### {self._t('Actionable Steps', 'Toimenpiteet')}\n"
                content += "\n".join([f"- {item}" for item in step["actionable_steps"]]) + "\n\n"
            
            if "bibliography" in step and step["bibliography"]:
                content += f"### {self._t('References', 'Lähteet')}\n"
                # Handle bibliography (list of dicts or strings)
                for ref in step["bibliography"]:
                    if isinstance(ref, dict):
                        # Construct citation string
                        cit = f"{ref.get('author', '')} {ref.get('year', '')}. {ref.get('title', '')}."
                        content += f"- {cit}\n"
                    else:
                        content += f"- {ref}\n"

            return UiSection(
                id="coach-markdown",
                type=SectionType.MARKDOWN_BLOCK,
                title=self._t("Coach Feedback", "Valmentajan Palaute"),
                data={"content": content},
            )

        # 2. Legacy Finnish Schema
        feedback = step.get("kannustava_palaute") or step.get("motivaatio")
        if not feedback:
            return None

        return UiSection(
            id="coach-markdown",
            type=SectionType.MARKDOWN_BLOCK,
            title=self._t("Coach Feedback", "Valmentajan Palaute"),
            data={"content": f"### Huomiot\n{feedback}"},
        )

    def _extract_archivist_section(self, steps: dict) -> UiSection | None:
        step = steps.get("step_archivist")
        if not step or not isinstance(step, dict):
            return None

        return UiSection(
            id="archivist-check",
            type=SectionType.ARCHIVIST_CHECK,
            title=self._t("Archivist Check", "Arkistonhoitajan Tarkistus"),
            data=self._transform_archivist_data(step),
        )

    def _transform_archivist_data(self, step: dict) -> dict:
        """Pass-through for Archivist Schema (Frontend now supports English)."""
        return step.copy()

    def _extract_usage_section(self, raw_data: dict) -> UiSection | None:
        usage = raw_data.get("usage")

        if not usage:
            return None

        total_tokens = usage.get("total_tokens", 0)
    def _transform_logician_data(self, data: dict) -> dict:
        """Flattens LogicianOutput (removes 'logician_data' wrapper) for frontend."""
        # 1. Check for wrapper
        if "logician_data" in data and isinstance(data["logician_data"], dict):
            # Merge inner data with any top-level metadata if needed, 
            # but usually we just want the inner payload.
            return data["logician_data"].copy()
        
        # 2. Fallback (already flat or legacy)
        return data.copy()

    def _transform_falsifier_data(self, data: dict) -> dict:
        """Flattens FalsifierOutput (removes 'falsifier_data' wrapper) for frontend."""
        if "falsifier_data" in data and isinstance(data["falsifier_data"], dict):
            return data["falsifier_data"].copy()
        return data.copy()

    def _transform_causal_data(self, data: dict) -> dict:
        """Flattens CausalOutput (removes 'causal_analysis' wrapper) for frontend."""
        if "causal_analysis" in data and isinstance(data["causal_analysis"], dict):
            return data["causal_analysis"].copy()
        return data.copy()

    def _transform_detector_data(self, data: dict) -> dict:
        """Flattens PerformativityOutput (removes 'performativity_analysis' wrapper) for frontend."""
        if "performativity_analysis" in data and isinstance(data["performativity_analysis"], dict):
            return data["performativity_analysis"].copy()
        return data.copy()

    def _transform_overseer_data(self, data: dict) -> dict:
        """Flattens OverseerOutput (removes 'overseer_data' wrapper) for frontend."""
        if "overseer_data" in data and isinstance(data["overseer_data"], dict):
            return data["overseer_data"].copy()
        return data.copy()


class AssessmentTransformer:
    def __init__(self, language: str = "en"):
        self.language = language
        # Reuse localization specific to assessment if needed, or generic
        self.loc = LocalizationService()

    def _t(self, key: str, default: str) -> str:
        return self.loc.get(key, self.language, default)


    def _reconstruct_state_from_trace(self, trace: list[dict[str, Any]]) -> dict[str, Any]:
        """Reconstructs the 'step_results' map from an append-only linear trace."""
        reconstructed = {}
        for event in trace:
            if event.get("event_type") == "output":
                step_name = event.get("step_name")
                if not step_name or not isinstance(step_name, str):
                    continue
                content = event.get("content", {})
                
                # Basic content merge
                reconstructed[step_name] = content
        return reconstructed



    def _get_workflow_steps(self, workflow_id: str, current_data: dict, workflow_definition: Any | None = None) -> list[StepProgressItem]:
        """Determines the steps for the workflow and their status dynamically."""
        
        chain = []
        if workflow_definition:
             # Extract steps from definition
             # Assuming workflow_definition is a dict or Pydantic model with 'steps'
             steps = getattr(workflow_definition, "steps", [])
             if isinstance(steps, list):
                 for s in steps:
                     # Handle Pydantic model or dict
                     sid = getattr(s, "id", None) or s.get("id")
                     if sid:
                         chain.append(sid)
        
        if not chain:
            # Fallback for legacy/missing definition (though we want to be strict, 
            # safe fallback prevents immediate crash during transition)
            # But user asked for REMOVING hardcoded logic.
            # If I return empty, the UI might be empty.
            # Let's log a warning? 
            # For now I will return an empty list if not found, to enforce strictness as requested.
            pass

        # 3. Determine Status for each step
        progress_items = []
        for step_id in chain:
            step_status = "pending"
            step_res = current_data.get(step_id)
            
            if step_res:
                step_status = "completed"
                # Check for specific status flags if available
                if step_res.get("status") == "failed":
                    step_status = "failed"
            
            # Simple heuristic: if a later step is present, earlier ones are likely completed
            # (Refinement: rely on strict status from DB if available)
            
            label = self._t(f"STEP_{step_id.upper()}", step_id)
            progress_items.append(StepProgressItem(
                id=step_id,
                label=label,
                status=step_status
            ))
            
        return progress_items
        
        # Check actual results to see what's done
        # We look at 'results' (final) or 'execution_trace' (intermediate)
        # Note: current_data passed here should be the 'step_results' map we reconstructed
        
        # If the workflow is completed, all steps in chain are completed? Not necessarily (early exit).
        # But for UI purposes, if we have a result for 'step_x', it's completed.
        
        for step_key in chain:
            status = "pending"
            
            # If step result exists, it's completed
            if step_key in current_data:
                status = "completed"
                # Check specifics (e.g. failed step?)
                # If step has 'error', mark as failed
                if "error" in current_data[step_key]:
                    status = "failed"
            
            # If we are strictly sequential, and this step is pending, but the previous was completed...
            # The *next* one is likely "running".
            # However, we can't easily guess "running" without looking at the raw status or active step name.
            # For now, let's leave it simple: Completed or Pending.
            # "Running" is handled by the overall status label mostly.
            
            # To enable "Active Step" highlight:
            # If this is the FIRST pending step, and workflow is running, mark it running.
            
            progress_items.append(StepProgressItem(
                id=step_key,
                label=self._t(f"steps.{step_key}", step_key.replace("step_", "").capitalize()),
                status=status
            ))
            
        # Post-process for "Running" state
        # Find the first "pending" item
        first_pending_idx = next((i for i, item in enumerate(progress_items) if item.status == "pending"), -1)
        if first_pending_idx != -1:
             # If previous was completed (or it's the first one) AND generic status is running
             # Then this one is likely the active one.
             pass # Logic is tricky without explicit "current_step" from engine.
             # Improvement: Engine should emit 'current_step'.
             # Hack: use 'trace' last event? 
             pass

        # 4. Filter unused steps on completion
        # If the workflow is done, any step still "pending" was likely not part of the active path.
        status_raw = current_data.get("status") # This might be step status, not workflow.
        # We need workflow status. It's not passed to _get_workflow_steps directly, but we can infer or pass it.
        # Actually, let's filter in the caller or pass status to this method.
        
        return progress_items

    def transform(self, raw_data: dict, workflow_definition: Any | None = None, valid_range: tuple[float, float] | None = None) -> AssessmentView:
        """Transforms raw execution state into a live Monitoring View (AssessmentView)."""
        
        # 1. Basic Info
        execution_id = raw_data.get("id") or raw_data.get("execution_id") or "unknown"
        status = raw_data.get("status", "pending")
        workflow_id = raw_data.get("workflow_id") or raw_data.get("config", {}).get("workflow_id", "unknown")
        
        # 2. UI Variant & Label
        ui_variant = "default"
        status_label = self._t(f"status.{status}", status.title())
        
        if status in ("completed", "finished"):
            ui_variant = "success"
            status_label = self._t("status.completed", "Valmis")
        elif status in ("failed", "rejected", "error"):
            ui_variant = "error"
            status_label = self._t("status.failed", "Epäonnistui")
        elif status == "cancelled":
             ui_variant = "warning"
             status_label = self._t("status.cancelled", "Peruttu")
        elif status == "running":
             ui_variant = "default"
             status_label = self._t("status.running", "Käynnissä")

        # 3. Status Message & Steps
        status_message = ""
        
        # Extract steps from results OR trace
        steps_data = raw_data.get("results", {}).get("step_results", {})
        if not steps_data and "execution_trace" in raw_data:
             steps_data = self._reconstruct_state_from_trace(raw_data["execution_trace"])
        elif not steps_data and "results" in raw_data and "execution_trace" in raw_data["results"]:
             steps_data = self._reconstruct_state_from_trace(raw_data["results"]["execution_trace"])

        # GENERATE STEPS LIST
        steps_list = self._get_workflow_steps(workflow_id, steps_data, workflow_definition)
        
        # Filter out pending steps if the execution is completed or failed
        # This hides "phantom" steps like judge_cognitive that weren't part of the run
        if status in ("completed", "finished", "failed", "rejected"):
            steps_list = [s for s in steps_list if s.status != "pending"]

        if status == "failed":
            error_details = raw_data.get("error") or raw_data.get("result", {}).get("error")
            status_message = str(error_details) if error_details else self._t("Unknown error", "Tuntematon virhe")
        elif status == "running":
            status_message = self._t("Processing...", "Käsitellään...")
            if steps_data:
                count = len(steps_data)
                last_step = list(steps_data.keys())[-1].replace("step_", "").capitalize()
                status_message = f"{self._t('Processing', 'Käsitellään')}: {last_step} ({count})"
                
                # Mark the likely active step as running in the list
                # Logic: If last completed step is index N, then N+1 is running.
                # Actually, if we reconstructed from trace, the last item in trace MIGHT be the running one if it has no output?
                # No, trace usually logs output on completion.
                # So the one AFTER the last completed one is running.
                
                completed_ids = set(steps_data.keys())
                for i, item in enumerate(steps_list):
                    if item.id not in completed_ids: # First non-completed
                         # Start marking it as running
                         item.status = "running"
                         break
                    
        elif status == "completed":
             status_message = self._t("Assessment ready", "Arviointi valmis")
             # Ensure all are marked completed in UI if they are present in backend steps?
             # For now, rely on `steps_data` check.
        else:
             status_message = "" 

        # 4. Warnings
        show_warning = False
        guard = steps_data.get("step_guard", {})
        if guard.get("security_check", {}).get("uhka_havaittu"):
            show_warning = True
            
        # 5. Final Score
        final_score = None
        judge = steps_data.get("step_judge", {})
        if "score_cards" in judge and judge["score_cards"]:
             try:
                 final_score = int(float(judge["score_cards"][0].get("total_score", 0)))
             except:
                 pass
        elif "total_score" in judge:
             try:
                 final_score = int(float(judge["total_score"]))
             except:
                 pass

        return AssessmentView(
            sessionId=str(execution_id),
            statusLabel=str(status_label),
            uiVariant=str(ui_variant),
            statusMessage=str(status_message or ""),
            showWarningBanner=bool(show_warning),
            steps=steps_list,
            finalScore=final_score
        )
