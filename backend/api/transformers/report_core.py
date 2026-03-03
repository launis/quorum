import logging
from typing import Any

from backend.exceptions import AppException
from backend.models.domain.execution import ExecutionRecord
from backend.models.enums import HelpTextKey, LabelKey, RiskLevel, TitleKey
from backend.models.state import WorkflowState
from backend.models.view.semantic_models import (
    BlockType,
    DimensionDisplay,
    EvidenceItem,
    EvidenceList,
    ReferenceIntent,
    ReferenceItem,
    ScoreCardDisplay,
    SemanticBlock,
    SemanticIntent,
    SemanticReport,
    SystemNotification,
)

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
    BaseTransformer,
):
    def transform(
        self,
        raw_data: ExecutionRecord,
        valid_range: tuple[float, float] | None = None,
        step_names: dict[str, str] | None = None,
        workflow_name: str | None = None,
    ) -> SemanticReport:
        """Transforms execution data (Pydantic Model) into a clean ReportView model.

        Args:
            raw_data: The execution results (ExecutionRecord or WorkflowState).
            valid_range: (min, max) tuple for strict score validation. Defaults to Standard Matrix (1-4).
            step_names: Optional dictionary mapping step IDs to their UI display names.
        """
        # 1. Normalize Input to Dict (Internal Processing) OR handle Object attributes directly?
        # Mandate says: "Pass Pydantic Models". So we should use attribute access.
        # However, for transition, we might support both or normalize first.
        # "If it has a shape, it must be a Model."

        execution_id = ""
        state = None

        if isinstance(raw_data, ExecutionRecord):
            execution_id = raw_data.id
            if isinstance(raw_data.results, WorkflowState):
                state = raw_data.results
            elif isinstance(raw_data.results, dict):
                # We attempt to reconstruct State
                raw_res = raw_data.results
                ctx_vars: dict[str, Any] = raw_res.get("context_variables", raw_res.get("step_results", raw_res)) or {}
                state = WorkflowState(workflow_id=raw_data.workflow_id or "legacy_fallback", context_variables=ctx_vars)
            else:
                logger.warning(
                    f"Unrecognized results type {type(raw_data.results)}, defaulting to empty WorkflowState."
                )
                state = WorkflowState(workflow_id="unknown")
        else:
            # FAIL FAST: Strict Schema Requirement
            raise TypeError(f"ReportTransformer requires ExecutionRecord. Got: {type(raw_data)}")

        if not execution_id:
            raise ValueError("Execution data missing mandatory 'id' field.")

        sections = []

        # --- A. Score Cards (Support for Multiple Matrices) ---
        judge_keys = ["step_judge", "step_judge_cognitive"]

        for key in judge_keys:
            # Use type-safe property dynamically from WorkflowState
            # Returns JudgeOutput or None
            step_output = getattr(state, key) if hasattr(state, key) else None

            if step_output:
                # Determine base title and agent name
                base_title = (
                    self._get_label(LabelKey.ANALYSIS_RESULT)
                    if key == "step_judge"
                    else self._get_label(LabelKey.COGNITIVE_ASSESSMENT)
                )

                # Use step name if provided, else fallback to hardcoded
                base_agent_name = ""
                if step_names and key in step_names:
                    base_agent_name = step_names[key]
                else:
                    base_agent_name = (
                        self._get_label(LabelKey.AGENT_JUDGE)
                        if key == "step_judge"
                        else self._get_label(LabelKey.AGENT_COGNITIVE_JUDGE)
                    )

                cards = []
                if hasattr(step_output, "score_cards") and step_output.score_cards:
                    cards = step_output.score_cards
                elif hasattr(step_output, "score_card") and step_output.score_card:
                    cards = [step_output.score_card]
                else:
                    cards = [step_output]  # Just in case JudgeOutput itself is the card payload

                for idx, card in enumerate(cards):
                    try:
                        # Fail Fast: Try/Except used for context logging, BUT we re-raise.

                        # Attribute access. If missing, it crashes (Fail Fast)
                        card_agent_name = getattr(card, "agent_name", base_agent_name)

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
                            SemanticBlock(id=section_id, type=BlockType.CARD, label=card_title, value=score_data)
                        )
                    except ValueError as e:
                        logger.error(f"Score validation failed for {key} (card {idx}): {e}")
                        raise AppException(
                            status_code=400,
                            message=f"Score validation failed for {key} (card {idx}): {e}",
                            details={"error_code": "SCORE_VALIDATION_FAILED"},
                        ) from e
                    except Exception as e:
                        raise AppException(f"Unexpected error in score card processing: {e}", 500) from e
            else:
                logger.warning(f"Missing data for {key} in Score Cards layout")

        # --- A2. Key Metrics (Usage & Cost) ---
        usage_section = self._extract_usage_section(raw_data)
        if usage_section:
            sections.append(usage_section)

        # --- B. XAI Report ---
        xai_section = self._build_xai_section(state)
        if xai_section:
            sections.append(xai_section)

        # --- B2. Generic Data Sections (Versatile Reporting) ---
        # Domain Mixins handle these
        guard_grid = self._extract_guard_grid(state)
        if guard_grid:
            sections.append(guard_grid)

        # --- Truth Protocol Findings (Critical Findings) ---
        # User Request: "Näytetään löydökset kirjallisena lopputulosteessa"
        # We extract 'critical_findings' from Judge step and show them prominently.
        truth_section = self._extract_critical_findings(state)
        if truth_section:
            sections.append(truth_section)

        analyst_table = self._extract_analyst_table(state)
        if analyst_table:
            sections.append(analyst_table)

            # Helper: Extract Evidence separately if present
            evidence = self._extract_analyst_evidence(state)
            if evidence:
                sections.append(evidence)

        profiler_section = self._extract_profiler_section(state)
        if profiler_section:
            sections.append(profiler_section)

        # RetrievalDomainTransformer handles this
        context_section = self._extract_context_section(state)
        if context_section:
            sections.append(context_section)

        # --- SPECIALIST BACKBONE (Courtroom 3.0) ---

        # 1. Logic / Logician
        logician = self._extract_logician_section(state)
        if logician:
            sections.append(logician)

        # 2. Falsification / Falsifier
        falsifier = self._extract_falsifier_section(state)
        if falsifier:
            sections.append(falsifier)

        # 3. Causal / Causal Analyst
        causal = self._extract_causal_section(state)
        if causal:
            sections.append(causal)

        # 4. Performativity / Detector
        detector = self._extract_detector_section(state)
        if detector:
            sections.append(detector)

        # 5. Facts & Ethics / Overseer
        overseer = self._extract_overseer_section(state)
        if overseer:
            sections.append(overseer)

        interaction_grid = self._extract_interaction_section(state)
        if interaction_grid:
            sections.append(interaction_grid)

        coach_section = self._extract_coach_section(state)
        if coach_section:
            sections.append(coach_section)

        archivist_section = self._extract_archivist_section(state)
        if archivist_section:
            sections.append(archivist_section)

        # --- C. Timeline ---
        timeline_events = self._build_timeline(state, step_names)

        sections.append(
            SemanticBlock(id="unified-timeline",
                type=BlockType.LIST,
                label=self._get_title(TitleKey.TIMELINE),
                value={"events": timeline_events},
            )
        )

        # --- D. Global References ---
        references_list = self._compile_references(state)

        # Extract Metrics from context_variables (if available)
        metrics = state.context_variables.get("audit_metrics") if state else None

        # --- E. Dynamic Theming & Notifications ---
        status_theme, notification = self._determine_report_status(metrics, guard_grid)

        # --- F. Dynamic Title with Timestamp ---
        base_title = self._t("lblTitleReport", "Raportti")
        created_str = ""
        
        if isinstance(raw_data, ExecutionRecord):
            ts = raw_data.started_at or raw_data.created_at
            if ts:
                created_str = self._format_date(str(ts))
            
            # Use injected workflow_name if provided, else fallback to formatted workflow_id
            if not workflow_name and raw_data.workflow_id:
                # e.g 'xai_audit' -> 'Xai Audit'
                workflow_name = raw_data.workflow_id.replace("_", " ").title()

        # Combine: "Xai Audit - 03.10.2023 15:30"
        final_title = base_title
        if workflow_name:
            final_title = workflow_name
        if created_str:
            final_title = f"{final_title} - {created_str}"

        return SemanticReport(
            report_id=execution_id,
            title=final_title,
            intent=SemanticIntent.SUCCESS
            if status_theme == "success"
            else (SemanticIntent.WARNING if status_theme == "warning" else SemanticIntent.DANGER),
            blocks=sections,
            metrics=metrics,
            system_notification=notification,
            references=references_list,
        )

    def _compile_references(self, state: WorkflowState | None) -> list[ReferenceItem]:
        """Kokoaa yhteen kaikki kontekstuaaliset lähdeviitteet."""
        if not state:
            return []

        references = []
        counters = {"SEARCH": 1, "GROUNDING": 1, "INTERNAL_KB": 1}

        # 1. Analyst Search (Web / Snippets) -> [H-X]
        # Haetaan sekä rag_evidencestä että hakutuloksista, koska arkitehtuuri oli siirtymävaiheessa
        search_items: list[Any] = []
        if getattr(state, "step_analyst", None):
            rag = getattr(state.step_analyst, "rag_evidence", [])
            if rag:
                search_items.extend(rag)

        # Oletetaan SearchHook palauttaa context_variables["search_result"]
        sr_obj = state.context_variables.get("search_result")
        if sr_obj:
            results = (
                getattr(sr_obj, "results", [])
                if hasattr(sr_obj, "results")
                else (sr_obj.get("results", []) if isinstance(sr_obj, dict) else sr_obj)
            )
            if isinstance(results, list):
                search_items.extend(results)

        for item in search_items:
            # Map object or dict
            title = "Verkkohaku"
            snippet = ""
            url = None
            if isinstance(item, dict):
                title = item.get("title", title)
                snippet = item.get("snippet", str(item))
                url = item.get("link")
            elif hasattr(item, "snippet"):
                title = getattr(item, "title", title)
                snippet = getattr(item, "snippet", str(item))
                url = getattr(item, "link", None)
            else:
                snippet = str(item)

            if snippet and snippet.strip():
                references.append(
                    ReferenceItem(
                        id=f"[H-{counters['SEARCH']}]",
                        intent=ReferenceIntent.SEARCH,
                        title=title,
                        snippet=snippet,
                        url=url,
                    )
                )
                counters["SEARCH"] += 1

        # 2. Vertex Grounding (Fact-checking/Web URIs) -> [F-X]
        # Grounding data is usually intercepted into LLMResponse model_extra.
        # Safest way without schema coupling is finding grounding metadata across steps' LLM traces if they exist
        for key, val in state.context_variables.items():
            if "grounding" in key.lower() and isinstance(val, (list, dict)):
                # Very simplified generic mapper, actual integration requires provider-specific schema
                pass

        # Note: If Judge provides critical_findings, we could also map them as [F-X] here in the future.
        # Until then, we extract from provider metadata directly if we see it.
        # Fallback to searching step_metadata:
        for step_key in [k for k in dir(state) if k.startswith("step_")]:
            model = getattr(state, step_key, None)
            if model:
                p_meta = getattr(model, "metadata", None)
                p_prov = getattr(p_meta, "provider_metadata", {}) if p_meta else {}
                g_urls: list[str] = p_prov.get("grounding_urls", []) if isinstance(p_prov, dict) else []
                for url in g_urls:
                    references.append(
                        ReferenceItem(
                            id=f"[F-{counters['GROUNDING']}]",
                            intent=ReferenceIntent.GROUNDING,
                            title="Faktantarkistus (Google)",
                            snippet=f"Vertex AI Grounding lähde: {url}",
                            url=url,
                        )
                    )
                    counters["GROUNDING"] += 1

        # 3. Internal KB (ReferencesHook) -> [O-X]
        # ReferenceHook tallentaa 'bibliography_result' tilaobjektiin
        bib_obj = state.context_variables.get("bibliography_result")
        if bib_obj:
            items: list[Any] = []
            if isinstance(bib_obj, dict):
                items = bib_obj.get("references", bib_obj.get("items", [])) or []
            else:
                items = getattr(bib_obj, "references", getattr(bib_obj, "items", [])) or []
            if isinstance(items, list):
                for item in items:
                    title = "Organisaation Linjaus"
                    snippet = ""
                    url = None
                    if isinstance(item, dict):
                        title = item.get("title", title)
                        snippet = item.get("snippet", str(item))
                        url = item.get("url") or item.get("source_id")
                    elif hasattr(item, "snippet"):
                        title = getattr(item, "title", title)
                        snippet = getattr(item, "snippet", str(item))
                        url = getattr(item, "url", getattr(item, "source_id", None))
                    else:
                        snippet = str(item)

                    if snippet and snippet.strip():
                        references.append(
                            ReferenceItem(
                                id=f"[O-{counters['INTERNAL_KB']}]",
                                intent=ReferenceIntent.INTERNAL_KB,
                                title=title,
                                snippet=snippet,
                                url=url,
                            )
                        )
                        counters["INTERNAL_KB"] += 1

        return references

    def _determine_report_status(
        self, metrics: dict[str, Any] | None, guard_section: SemanticBlock | None
    ) -> tuple[str, SystemNotification | None]:
        """Calculates the Report Theme (Success/Warning/Danger) based on heuristics."""
        theme = "success"
        notification = None

        # 1. Security Check (Danger)
        if guard_section:
            # We need to peek into the data. SemanticBlock.value is a dict or Object.
            # SecurityDisplay was dumped into 'security_display' key.
            sec_val: dict[str, Any] = (
                guard_section.value
                if isinstance(guard_section.value, dict)
                else getattr(guard_section.value, "security_display", {})
            )
            sec_data: dict[str, Any] = sec_val.get("security_display", {}) if "security_display" in sec_val else sec_val
            risk = sec_data.get("risk_level")

            if risk == RiskLevel.HIGH.value:
                theme = "danger"
                notification = SystemNotification(
                    title=self._t("lblSecurityRisk", "TURVALLISUUSRISKI"),
                    message=self._t("lblSecurityRiskText", "Raportissa on havaittu kriittisiä tietoturvariskejä. Tarkista 'Turvallisuus & Tietosuoja' -osio välittömästi."),
                    level="danger",
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
                    title=self._t("lblLowInteraction", "ALHAINEN INTERAKTIO"),
                    message=self._t("lblLowInteractionText", "Käyttäjän osuus sisällöstä on alle 30%. Raportti saattaa sisältää merkittävästi tekoälyn hallusinoimaa sisältöä."),
                    level="warning",
                )
                return theme, notification

        return theme, notification

    def _extract_score_data(
        self, judge_step: object, agent_name: str, valid_range: tuple[float, float] | None
    ) -> ScoreCardDisplay:
        """Extracts score and verdict from V3 Schema."""
        if hasattr(judge_step, "model_dump"):
            judge_step = judge_step.model_dump()
        elif hasattr(judge_step, "dict"):
            judge_step = judge_step.dict()

        score = None
        raw_score = None
        verdict = None
        judge_step_dict: dict[str, Any] = (
            getattr(judge_step, "model_dump", lambda: {})()
            if hasattr(judge_step, "model_dump")
            else (judge_step if isinstance(judge_step, dict) else {})
        )
        if not judge_step_dict and hasattr(judge_step, "dict"):
            judge_step_dict = getattr(judge_step, "dict", lambda: {})()

        # 1. Primary Source: 'score_cards' (V3 Standard)
        if (
            "score_cards" in judge_step_dict
            and isinstance(judge_step_dict["score_cards"], list)
            and judge_step_dict["score_cards"]
        ):
            card = judge_step_dict["score_cards"][0]
            score = card.get("total_score") if isinstance(card, dict) else getattr(card, "total_score", None)
            verdict = card.get("verdict") if isinstance(card, dict) else getattr(card, "verdict", None)
            dimensions_list = card.get("dimensions", []) if isinstance(card, dict) else getattr(card, "dimensions", [])

            raw_score = (
                card.get("total_score_raw") if isinstance(card, dict) else getattr(card, "total_score_raw", None)
            )
            if raw_score is None:
                raw_score = score

            if raw_score is not None and score is None:
                score = raw_score

        # 2. Legacy 'judge' struct fallbacks
        elif judge_step_dict:  # If judge_step_dict is not empty, try legacy keys
            if "score_card" in judge_step_dict:  # Legacy/Fallback if card inside 'score_card' key
                card2: dict[str, Any] = (
                    getattr(judge_step_dict["score_card"], "model_dump", lambda: {})()
                    if hasattr(judge_step_dict["score_card"], "model_dump")
                    else (
                        judge_step_dict["score_card"]
                        if isinstance(judge_step_dict["score_card"], dict)
                        else getattr(judge_step_dict["score_card"], "__dict__", {})
                    )
                )
                score = card2.get("total_score")
                raw_score = score
                verdict = card2.get("final_verdict")
                dimensions_list = card2.get("dimensions", [])
            else:  # V3 Fallback (direct attributes)
                score = judge_step_dict.get("total_score")
                raw_score = score
                verdict = judge_step_dict.get("final_verdict")
                dimensions_list = judge_step_dict.get("dimensions", [])

        # 2. Validation
        if raw_score is None:
            raise AppException(
                status_code=400,
                message=f"Score is missing from Judge step ({agent_name}). Expected 'total_score'.",
                details={"error_code": "MISSING_SCORE"},
            )

        try:
            score = float(raw_score)
        except (TypeError, ValueError):
            raise AppException(
                status_code=400, message=f"Score '{raw_score}' is not a valid number.", details={"error_code": "INVALID_SCORE"}
            ) from None

        # STRICT SCALE AUTHORITY CHECK
        if valid_range is None:
            s_min = judge_step_dict.get("scale_min")
            s_max = judge_step_dict.get("scale_max")

            if s_min is not None and s_max is not None:
                valid_range = (float(s_min), float(s_max))
            else:
                # If no scale found, default to 1-4 (Legacy Standard) but WARN or FAIL?
                # For migration safety, we should stick to Fail Fast if unknown.
                # However, let's look for known scales in dimensions if absent.
                raise AppException(
                    status_code=400,
                    message=f"Score validation failed for {agent_name}: No scale definition found.",
                    details={"error_code": "MISSING_SCALE"},
                )

        scale_min, scale_max = valid_range
        if not (scale_min <= score <= scale_max):
            raise AppException(
                status_code=400,
                message=f"Score {score} is out of valid range [{scale_min}, {scale_max}].",
                details={"error_code": "OUT_OF_RANGE"},
            )

        if not verdict:
            verdict = ""

        # Map dimensions to proper model
        mapped_dimensions: list[DimensionDisplay] = []
        for d in dimensions_list:
            # Handle potential dict vs object
            d_data = d if isinstance(d, dict) else d.model_dump()
            mapped_dimensions.append(
                DimensionDisplay(
                    dimension_id=d_data.get("dimension_id", "dim_unknown"),
                    dimension_label=d_data.get("dimension_label") or d_data.get("dimension_id", "dim_unknown"),
                    score=float(d_data.get("score", 0.0)),
                    max_score=float(d_data.get("max_score", scale_max)),
                    weight=float(d_data.get("weight", 1.0)),
                    reasoning=d_data.get("reasoning", ""),
                )
            )

        return ScoreCardDisplay(
            agent_name=agent_name,
            total_score=score,
            min_score=int(scale_min),
            max_score=int(scale_max),
            verdict=verdict,
            dimensions=mapped_dimensions,
        )

    def _build_xai_section(self, state: WorkflowState) -> SemanticBlock | None:
        xai = state.step_xai
        if not xai:
            logger.warning("Missing data for step_xai in XAI Report layout")
            return None

        content = getattr(xai, "xai_report_formatted", None)

        if not content:
            content = getattr(xai, "final_verdict", None)

        if not content:
            logger.warning("step_xai exists but missing both 'xai_report_formatted' and 'final_verdict'")
            return None

        return SemanticBlock(id="xai-summary",
            type=BlockType.PARAGRAPH,
            label=self._get_label(LabelKey.AI_REASONING),
            value={"content": content},
        )

    def _build_timeline(self, state: WorkflowState, step_names: dict[str, str] | None = None) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        agent_names: dict[str, str] = {
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

        # Iterate context_variables to find all step keys
        for step_key in state.context_variables.keys():
            if not step_key.startswith("step_"):
                continue

            # Load typed Pydantic model using WorkflowState's intelligent accessor properties
            model = getattr(state, step_key, None)
            if not model:
                logger.warning(
                    f"Timeline extraction: no typed property found in WorkflowState for {step_key}, skipping."
                )
                continue

            meta = getattr(model, "metadata", None)
            if not meta:
                continue

            timestamp = getattr(meta, "luontiaika", None)
            if timestamp:
                timestamp = timestamp.isoformat()

            # Determine agent label from hardcoded defaults or dynamic step_names
            if step_key in agent_names:
                agent_label = agent_names[step_key]
            elif step_names and step_key in step_names:
                agent_label = step_names[step_key]
            else:
                agent_label = step_key

            # 1. Reasoning Trace (The thinking process)
            rt = getattr(model, "reasoning_trace", None)
            if rt:
                thought = getattr(rt, "thought_process", str(rt))
                events.append(
                    {
                        "timestamp": timestamp,
                        "actor": agent_label,
                        "label": agent_label,
                        "type": "reasoning",
                        "message": thought[:250] + "...",
                        "content": thought[:250] + "...",
                        "compliance_help": self._t(HelpTextKey.ARCHIVIST.value, default="Archivist Help"),
                        "bloom_help": self._t(HelpTextKey.BLOOM.value, default="Bloom Help"),
                        "strategic_help": self._t(HelpTextKey.STRATEGIC_DEPTH.value, default="Strategic Depth Help"),
                        "fidelity_help": self._t(HelpTextKey.FIDELITY.value, default="Fidelity Help"),
                        "help_abductive": self._t(HelpTextKey.ABDUCTIVE.value, default="Abductive Help"),
                        "authenticity_help": self._t(HelpTextKey.AUTHENTICITY.value, default="Authenticity Help"),
                    }
                )

            # 2. Audit Logs
            audit_logs = getattr(meta, "audit_logs", None)
            if audit_logs and isinstance(audit_logs, list):
                for log in audit_logs:
                    # 'log' is an AuditLogEntry pydantic model
                    # But it could be a dict if Pydantic conversion failed
                    role = getattr(log, "level", None) or getattr(log, "role", None)
                    if role == "system":
                        continue

                    content = getattr(log, "message", None) or getattr(log, "content", "")
                    clean_msg = str(content).replace("<<REFERENCE:", "[Viittaus:").replace(">>", "]")

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

    def _extract_analyst_table(self, state: WorkflowState) -> SemanticBlock | None:
        step = state.step_analyst
        if not step:
            logger.warning("Missing data for step_analyst in Analyst Table layout")
            return None

        hypotheses: list[Any] = getattr(step, "hypotheses", None) or getattr(step, "hypoteesit", [])
        if not hypotheses:
            logger.warning("step_analyst exists but 'hypotheses' data is missing or empty")
            return None

        rows: list[dict[str, Any]] = []
        for h in hypotheses:
            h_data = h if isinstance(h, dict) else h.model_dump()
            rows.append(
                {
                    "id": h_data.get("id"),
                    "claim": h_data.get("claim_text") or h_data.get("vaite_teksti"),
                    # Explicit boolean conversion
                    "proven": "✅" if (h_data.get("evidence_found") or h_data.get("loytyyko_todisteita")) else "❌",
                }
            )

        # Enhancement: Include RAG Evidence if available
        rag_evidence = getattr(step, "rag_evidence", None)
        evidence_content = ""
        if rag_evidence:
            evidence_content = f"### {self._get_label(LabelKey.EVIDENCE_FOUND)}\n"
            for item in rag_evidence:
                evidence_content += f"- {item}\n"

        return SemanticBlock(id="hypotheses-table",
            type=BlockType.DATA_GRID,
            label=self._get_title(TitleKey.HYPOTHESES),
            value={
                "columns": [
                    {"key": "id", "label": self._get_label(LabelKey.ID)},
                    {"key": "claim", "label": self._get_label(LabelKey.CLAIM)},
                    {"key": "proven", "label": self._get_label(LabelKey.VERIFIED)},
                ],
                "rows": rows,
                # New field for Evidence (handled by frontend if present, or we create separate section)
                "rag_evidence": rag_evidence or [],
            },
        )

    def _extract_analyst_evidence(self, state: WorkflowState) -> SemanticBlock | None:
        """Helper to extract RAG evidence as a separate section if needed."""
        step = state.step_analyst
        if not step:
            logger.warning("Missing data for step_analyst in Analyst Evidence layout")
            return None

        rag_evidence = getattr(step, "rag_evidence", None)
        if not rag_evidence:
            logger.warning("step_analyst exists but 'rag_evidence' data is missing or empty")
            return None

        items: list[EvidenceItem] = []
        for i, item in enumerate(rag_evidence):
            items.append(
                EvidenceItem(id=f"evidence-{i}", source="RAG Search", content=str(item), score=1.0, type="concept")
            )

        if not items:
            return None

        return SemanticBlock(id="analyst-evidence",
            type=BlockType.LIST,
            label=self._get_label(LabelKey.EVIDENCE_FOUND),
            value={"evidence": EvidenceList(items=items, total_count=len(items))},
        )

    def _extract_usage_section(self, record: ExecutionRecord) -> SemanticBlock | None:
        """Extracts usage and cost metrics from strictly typed ExecutionRecord."""
        # Cost is top-level in ExecutionRecord
        cost = record.cost_estimate or 0.0

        # Token usage is usually inside 'results' -> 'usage' or 'metadata' -> 'usage'
        # Since ExecutionRecord doesn't strictly define usage breakdown, we look in results.
        total_tokens = 0
        prompt_tokens = 0
        completion_tokens = 0

        # Access results safely
        usage: dict[str, Any] | None = None
        if isinstance(record.results, WorkflowState):
            usage = record.results.context_variables.get("usage")
            if not usage:
                # Fallback to total audit_metrics if usage object is absent
                metrics = (record.results.context_variables or {}).get("audit_metrics", {})
                usage = metrics.get("usage")
        elif isinstance(record.results, dict):
            res_data: dict[str, Any] = record.results
            usage = res_data.get("usage")
            if not usage and "result" in res_data:
                usage = res_data["result"].get("usage")
            if not usage and "context_variables" in res_data:
                usage = res_data["context_variables"].get("usage")
        else:
            usage = None

        if usage:
            total_tokens = usage.get("total_tokens", 0)
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            # Prefer top-level cost, but fallback if needed? No, top level is authoritive.
        else:
            logger.warning("Missing usage stats in ExecutionRecord results")

        items: list[dict[str, Any]] = [
            {"label": self._t("lblTotalTokens", "Kokonaistokenit"), "value": str(total_tokens)},
            {"label": self._t("lblPromptTokens", "Syötetokenit"), "value": str(prompt_tokens)},
            {"label": self._t("lblCompletionTokens", "Vastaustokenit"), "value": str(completion_tokens)},
            {
                "label": self._t("lblCostEstimate", "Kustannusarvio ($)"),
                "value": f"${cost:.4f}" if cost > 0 else "N/A",
                "highlight": True,
            },
        ]

        data: dict[str, Any] = {"items": items}

        return SemanticBlock(id="usage-stats", type=BlockType.METRIC, label=self._get_title(TitleKey.USAGE), value=data)

    def _extract_critical_findings(self, state: WorkflowState) -> SemanticBlock | None:
        """Extracts Truth Protocol findings (Critical Findings) from Judge step."""
        findings: list[str] = []

        # Check both judges
        for key in ["step_judge", "step_judge_cognitive"]:
            # Returns typed JudgeOutput
            step = getattr(state, key, None)
            if not step:
                logger.warning(f"Missing data for {key} in Critical Findings layout")
                continue

            f_list = getattr(step, "critical_findings", [])

            # Legacy/Fallback: Check inside score_card if not at top level
            if not f_list and hasattr(step, "score_card") and step.score_card:
                f_list = getattr(step.score_card, "critical_findings", [])
            elif not f_list and hasattr(step, "score_cards") and step.score_cards:
                for card in step.score_cards:
                    card_findings = getattr(card, "critical_findings", [])
                    if card_findings:
                        f_list.extend(card_findings)

            if f_list:
                findings.extend(f_list)

        if not findings:
            return None

        # Remove duplicates preserving order
        unique_findings = []
        seen = set()
        for f in findings:
            if f not in seen:
                unique_findings.append(f)
                seen.add(f)

        title = self._t("lblTruthProtocolFindings", "TOTUUSPROTOKOLLAN LÖYDÖKSET")
        disclaimer = self._t("lblFindingsDisclaimer", "Nämä löydökset perustuvat Tietopankin (Laki), Hakutulosten (Faktat) ja Lokien (Teot) vertailuun.")
        
        # Format as Markdown List for high visibility
        content = f"### \u26a0\ufe0f {title.upper()}\n\n"
        for item in unique_findings:
            content += f"- {item}\n"

        content += f"\n*{disclaimer}*"

        return SemanticBlock(id="critical-findings",
            type=BlockType.PARAGRAPH,
            intent=SemanticIntent.WARNING,
            label="TOTUUSPROTOKOLLA",  # Hardcoded or use TitleKey if exists
            value={"content": content},
        )
