from typing import List, Dict, Any, Optional
from datetime import datetime
import copy
import logging

from backend.models.view import ReportView, UiSection, SectionType

logger = logging.getLogger(__name__)

class ReportTransformer:
    def transform(self, raw_data: dict, valid_range: Optional[tuple[float, float]] = None) -> ReportView:
        """
        Transforms raw execution data (dict) into a clean ReportView model.
        Args:
            raw_data: The execution results.
            valid_range: (min, max) tuple for strict score validation. Defaults to Standard Matrix (1-4).
        """
        execution_id = raw_data.get("id") or raw_data.get("execution_id") or "unknown"
        results = raw_data.get("results", {})
        
        # We might have nested steps structure depending on how raw_data is passed
        # Sometimes results IS the dict of steps, sometimes results['step_results'] (ExecutionCompleted format)
        if "step_results" in results:
            steps = results["step_results"]
        else:
            steps = results
        
        sections = []

        # --- A. Score Cards (Support for Multiple Matrices) ---
        # We look for specific known judge steps. 
        # Future improvement: scan for any step with task_key="judge" via config, but keys are stable enough.
        judge_keys = ["step_judge", "step_judge_cognitive"]
        
        for key in judge_keys:
            step_data = steps.get(key)
            if step_data:
                try:
                    # Title based on Key
                    title = "Analyysin Tulos" if key == "step_judge" else "Kognitiivinen Arvio"
                    agent_name = "Tuomari" if key == "step_judge" else "Kognitiivinen Tuomari"

                    # Resolve matrix-specific range if possible (in future), currently sharing execution-wide valid_range
                    # or we could try to look up matrix_id per step here.
                    # For now, we apply the global strict range to ALL judges (assuming they share the scale or user explicitly passed wide range)
                    score_data = self._extract_score_data(step_data, agent_name=agent_name, valid_range=valid_range)
                    
                    sections.append(UiSection(
                        id=f"score-card-{key}", # Unique ID
                        type=SectionType.SCORE_CARD,
                        title=title,
                        data=score_data
                    ))
                except ValueError as e:
                    logger.error(f"Score validation failed for {key}: {e}")
                    raise e

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
        # Logic to support BOTH Sequential (Individual Steps) and Fused (Panel Step)
        # We prefer individual steps if present, otherwise look into Panel.
        
        panel = steps.get("step_panel", {})

        # 1. Logic / Logician
        logician_data = steps.get("step_logician") or panel.get("logiikka_auditointi")
        if logician_data:
            sections.append(UiSection(
                id="logic-analysis",
                type=SectionType.LOGIC_ANALYSIS,
                title="Logiikka-analyysi",
                data=logician_data if isinstance(logician_data, dict) else logician_data.dict()
            ))

        # 2. Falsification / Falsifier
        falsifier_data = steps.get("step_falsifier") or panel.get("falsifiointi_auditointi")
        if falsifier_data:
            sections.append(UiSection(
                id="stress-test",
                type=SectionType.STRESS_TEST,
                title="Falsifiointi & Stressitesti",
                data=falsifier_data if isinstance(falsifier_data, dict) else falsifier_data.dict()
            ))

        # 3. Causal / Causal Analyst
        causal_data = steps.get("step_causal") or panel.get("kausaalinen_auditointi")
        if causal_data:
            sections.append(UiSection(
                id="causal-analysis",
                type=SectionType.CAUSAL_ANALYSIS,
                title="Kausaalinen Auditointi",
                data=causal_data if isinstance(causal_data, dict) else causal_data.dict()
            ))

        # 4. Performativity / Detector
        detector_data = steps.get("step_detector") or panel.get("performatiivisuus_auditointi")
        if detector_data:
            sections.append(UiSection(
                id="performativity-check",
                type=SectionType.PERFORMATIVITY_CHECK,
                title="Performatiivisuustarkistus",
                data=detector_data if isinstance(detector_data, dict) else detector_data.dict()
            ))

        # 5. Facts & Ethics / Overseer
        overseer_data = steps.get("step_overseer") or panel.get("etiikka_ja_fakta")
        if overseer_data:
             sections.append(UiSection(
                id="fact-check",
                type=SectionType.FACT_CHECK,
                title="Fakta & Etiikka",
                data=overseer_data if isinstance(overseer_data, dict) else overseer_data.dict()
            ))

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
        sections.append(UiSection(
            id="unified-timeline",
            type=SectionType.TIMELINE_FEED,
            title="Prosessin Eteneminen",
            data={"entries": timeline_events}
        ))

        # --- D. Determine Theme ---
        theme = "success"
        # TODO: Dynamic theme based on score (e.g. < 2 = warning)

        return ReportView(
            view_id=execution_id,
            status_theme=theme, # TODO: Dynamic theme based on score (e.g. < 2 = warning)
            sections=sections
        )

    def _extract_score_data(self, judge_step: dict, agent_name: str, valid_range: Optional[tuple[float, float]]) -> dict:
        """
        Extracts score and verdict.
        STRICT: Raises ValueError if score is missing or out of range [min, max].
        """
        # Data might be in 'score_cards' list (new format) or flat fields (old format)
        score = None
        verdict = None
        dimensions = []

        # 1. Try 'score_cards' (New XAI format)
        if "score_cards" in judge_step and isinstance(judge_step["score_cards"], list) and judge_step["score_cards"]:
            card = judge_step["score_cards"][0]
            raw_score = card.get("total_score")
            verdict = card.get("verdict")
            dimensions = card.get("dimensions", [])
        
        # 2. Try 'pisteet' (Old format or fallback location)
        elif "pisteet" in judge_step:
            # Maybe 'pisteet' is a float? Or a dict?
            pisteet = judge_step["pisteet"]
            if isinstance(pisteet, (int, float)):
                raw_score = pisteet
            elif isinstance(pisteet, dict):
                 raw_score = judge_step.get("total_score")
            else:
                 raw_score = judge_step.get("total_score")
            
            # ATTEMPT TO EXTRACT LEGACY DIMENSIONS from 'perustelut' dict
            # Example: {"Relevanssi": "...", "Tarkkuus": "..."}
            # We don't have per-dimension scores in legacy data usually, just text.
            # BUT if we want to show *something* on the radar, we might need to fake it or check if 'pisteet' IS a dict of scores?
            # Looking at the raw data (from memory of typical legacy):
            # pisteet = 93.3
            # perustelut = {"Relevanssi": "...", "Tarkkuus": "..."}
            
            # If we strictly need numbers for Radar, and we only have text, we can't plot them.
            # But the user says "Matriisi ei näy" -> implies they expect the labels at least?
            # Flutter ScoreCardRadar requires 'score' for each dimension.
            
            # Let's check if 'perustelut' keys match the Matrix we restored.
            perustelut = judge_step.get("perustelut")
            
            if perustelut and isinstance(perustelut, dict):
                # DICT CASE: {"Relevanssi": "...", "Tarkkuus": "..."}
                for key, val in perustelut.items():
                    if len(str(key)) < 50:
                        dimensions.append({
                            "id": str(key).lower(),
                            "label": str(key),
                            "score": float(raw_score) if raw_score else 0.0,
                            "reasoning": str(val)
                        })
            
            elif perustelut and isinstance(perustelut, str):
                # STRING CASE: "Relevanssi: Oli hyvä. Tarkkuus: Tarkka."
                # We try to split by known standard keys to be safe
                known_keys = ["Relevanssi", "Tarkkuus", "Selkeys", "Johdonmukaisuus", "Perustelut"]
                
                # Simple strategy: Check if key exists in text, extract segment
                # Note: This is fuzzy but better than nothing for "No detailed dimension data".
                
                # Normalize text
                p_text = perustelut
                
                found_dims = []
                for key in known_keys:
                    if key in p_text or key + ":" in p_text:
                        # Find start index
                        try:
                            start_idx = p_text.find(key)
                            # Find next key to stop
                            end_idx = len(p_text)
                            for other in known_keys:
                                if other != key:
                                    other_idx = p_text.find(other, start_idx + len(key))
                                    if other_idx != -1 and other_idx < end_idx:
                                        end_idx = other_idx
                            
                            val = p_text[start_idx+len(key):end_idx].strip(" :.\n")
                            if val:
                                dimensions.append({
                                    "id": key.lower(),
                                    "label": key,
                                    "score": float(raw_score) if raw_score else 0.0,
                                    "reasoning": val
                                })
                        except Exception:
                            continue
                            
                # Fallback: If no dimensions found from string, add one generic "Perustelut" dimension
                if not dimensions and len(p_text) > 5:
                     dimensions.append({
                        "id": "general_reasoning",
                        "label": "Yleiset Perustelut",
                        "score": float(raw_score) if raw_score else 0.0,
                        "reasoning": p_text[:200] + "..." if len(p_text) > 200 else p_text
                    })
        
        else:
            raw_score = judge_step.get("total_score")

        # 3. Validation
        if raw_score is None:
            raise ValueError("Score is missing from Judge step.")
            
        try:
            score = float(raw_score)
        except (TypeError, ValueError):
            raise ValueError(f"Score '{raw_score}' is not a valid number.")

        # STRICT SCALE AUTHORITY CHECK (User Mandate: No defaults)
        if valid_range is None:
            # 1. Attempt to resolve from the step data itself (Self-Contained Authority)
            s_min = judge_step.get("scale_min")
            s_max = judge_step.get("scale_max")
            
            if s_min is not None and s_max is not None:
                valid_range = (float(s_min), float(s_max))
            else:
                 # 2. FAIL FAST. Do not assume 1-4.
                 raise ValueError(f"Score validation failed for {agent_name}: No scale definition found (valid_range=None and no in-step metadata). Fallback is forbidden.")

        scale_min, scale_max = valid_range
        if not (scale_min <= score <= scale_max):
            # STRICT MODE: No fallback.
            raise ValueError(f"Score {score} is out of valid range [{scale_min}, {scale_max}] from DB.")

        # Fallback: Check if 'dimensions' exists at root level (Intermediate Legacy Format)
        if not dimensions and "dimensions" in judge_step and isinstance(judge_step["dimensions"], list):
            dimensions = judge_step["dimensions"]

        # Extract Verdict if missing
        if not verdict:
            verdict = judge_step.get("tuomio") or judge_step.get("final_verdict") or "Arvioitu"

        return {
            "agent_name": agent_name,
            "total_score": score,
            "max_score": int(scale_max), # Cast to int for frontend model
            "verdict": verdict,
            "dimensions": dimensions
        }

    def _build_xai_section(self, steps: dict) -> Optional[UiSection]:
        if "step_xai" not in steps:
            return None
            
        xai = steps["step_xai"]
        content = xai.get("xai_report_formatted")
        
        # Fallback to direct verdict text if formatted report missing
        if not content:
            content = xai.get("final_verdict")

        if not content:
            return None

        return UiSection(
            id="xai-summary",
            type=SectionType.MARKDOWN_BLOCK,
            title="Tekoälyn Perustelut",
            data={"content": content}
        )

    def _build_timeline(self, steps: dict) -> List[dict]:
        events = []
        agent_names = {
            "step_guard": "🛡️ Vartija",
            "step_analyst": "🔎 Analyytikko",
            "step_interaction": "🤝 Vuorovaikutus",
            "step_profiler": "🧠 Profiloija",
            "step_logician": "📐 Loogikko",
            "step_falsifier": "🧪 Falsifioija",
            "step_causal": "🔗 Kausaalisuus",
            "step_detector": "🎭 Ilmaisunvalvoja",
            "step_judge": "⚖️ Tuomari",
            "step_judge_cognitive": "⚖️ Kognitiivinen Tuomari",
            "step_coach": "🎓 Valmentaja",
            "step_xai": "📝 Raportoija"
        }

        for step_key, step_data in steps.items():
            if not isinstance(step_data, dict):
                continue
                
            meta = step_data.get("metadata", {})
            timestamp = meta.get("luontiaika")
            agent_label = agent_names.get(step_key, step_key)
            
            # 1. Reasoning Trace (The thinking process)
            if "reasoning_trace" in step_data and step_data["reasoning_trace"]:
                events.append({
                    "timestamp": timestamp,
                    "actor": agent_label,
                    "type": "reasoning",
                    "message": str(step_data["reasoning_trace"])[:250] + "..." # Preview
                })

            # 2. Audit Logs (Filtered System Prompts)
            if "audit_logs" in meta and isinstance(meta["audit_logs"], list):
                for log in meta["audit_logs"]:
                    if log.get("role") == "system":
                        continue
                    
                    content = log.get("content", "")
                    # Hydrate references locally? Or keep as is?
                    # For now just format nicely.
                    clean_msg = content.replace("<<REFERENCE:", "[Viittaus:").replace(">>", "]")
                    
                    events.append({
                        "timestamp": timestamp,
                        "actor": agent_label,
                        "type": "log",
                        "message": clean_msg
                    })

        # Sort by timestamp (handling None)
        return sorted(events, key=lambda x: x.get("timestamp") or "")

    def _extract_analyst_table(self, steps: dict) -> Optional[UiSection]:
        step = steps.get("step_analyst")
        if not step or not isinstance(step, dict):
            return None
        
        hypotheses = step.get("hypoteesit", [])
        if not hypotheses:
            return None
            
        rows = []
        for h in hypotheses:
            # Handle Pydantic model dump or dict
            h_data = h if isinstance(h, dict) else h.dict()
            rows.append({
                "id": h_data.get("id"),
                "claim": h_data.get("vaite_teksti"),
                "proven": "✅" if h_data.get("loytyyko_todisteita") else "❌"
            })
            
        return UiSection(
            id="hypotheses-table",
            type=SectionType.DATA_TABLE,
            title="Analyytikon Hypoteesit",
            data={
                "columns": [
                    {"key": "id", "label": "ID"},
                    {"key": "claim", "label": "Väite"},
                    {"key": "proven", "label": "Vahvistettu"}
                ],
                "rows": rows
            }
        )

    def _extract_guard_grid(self, steps: dict) -> Optional[UiSection]:
        step = steps.get("step_guard")
        if not step or not isinstance(step, dict):
            return None
            
        sec = step.get("security_check", {})
        if not sec:
            return None
            
        return UiSection(
            id="security-grid",
            type=SectionType.KEY_VALUE_GRID,
            title="Turvatarkastus",
            data={
                "items": [
                    {"label": "Uhka Havaittu", "value": "Kyllä" if sec.get("uhka_havaittu") else "Ei", "highlight": sec.get("uhka_havaittu")},
                    {"label": "Riski Taso", "value": sec.get("riski_taso", "N/A")},
                    {"label": "Anonymisoitu", "value": "Kyllä" if sec.get("anonymisointi_tehty") else "Ei"}
                ]
            }
        )

    def _extract_profiler_section(self, steps: dict) -> Optional[UiSection]:
        step = steps.get("step_profiler")
        if not step or not isinstance(step, dict):
            return None
        
        # Use full data schema extraction for the Backbone
        return UiSection(
            id="profiler-analysis",
            type=SectionType.PROFILER_ANALYSIS,
            title="Profiloijan Analyysi",
            data=step # Pass full dict (contains metrics, biases, intent, etc.)
        )



    def _extract_interaction_section(self, steps: dict) -> Optional[UiSection]:
        step = steps.get("step_interaction")
        if not step or not isinstance(step, dict):
            return None
            
        role = step.get("driver_classification", "N/A")
        ratio = step.get("input_control_ratio")
        
        return UiSection(
            id="interaction-grid",
            type=SectionType.KEY_VALUE_GRID,
            title="Vuorovaikutus",
            data={
                "items": [
                    {"label": "Rooli", "value": role, "highlight": role == "Kuski"},
                    {"label": "Kontrollisuhde", "value": f"{ratio:.2f}" if ratio is not None else "N/A"}
                ]
            }
        )

    def _extract_coach_section(self, steps: dict) -> Optional[UiSection]:
        step = steps.get("step_coach")
        if not step or not isinstance(step, dict):
            return None
            
        # Prioritize V2 fields if available
        feedback = step.get("kannustava_palaute") or step.get("motivaatio")
        if not feedback:
            return None
            
        return UiSection(
            id="coach-markdown",
            type=SectionType.MARKDOWN_BLOCK,
            title="Valmentajan Palaute",
            data={"content": f"### Huomiot\n{feedback}"}
        )

    def _extract_archivist_section(self, steps: dict) -> Optional[UiSection]:
        step = steps.get("step_archivist")
        if not step or not isinstance(step, dict):
            return None
            
        return UiSection(
            id="archivist-check",
            type=SectionType.ARCHIVIST_CHECK,
            title="Arkistonhoitajan Tarkistus",
            data=step
        )

    def _extract_usage_section(self, raw_data: dict) -> Optional[UiSection]:
        # Usage might be at root 'usage' or aggregated from steps
        usage = raw_data.get("usage")
        
        # If no root usage, try to sum up? 
        # (Assuming root usage is populated by engine at end of run)
        if not usage:
            return None
            
        total_tokens = usage.get("total_tokens", 0)
        cost = usage.get("total_cost", 0.0)
        # Maybe model info?
        
        return UiSection(
            id="key-metrics",
            type=SectionType.KEY_VALUE_GRID,
            title="Suorituskyky & Kulutus",
            data={
                "items": [
                    {"label": "Tokenit", "value": f"{total_tokens:,}"},
                    {"label": "Kustannus", "value": f"${cost:.4f}"},
                    # We could add duration here if we had start/end times easily accessible
                ]
            }
        )
