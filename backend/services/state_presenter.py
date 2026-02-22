"""Presenter layer for formatting WorkflowState into UI-ready structures."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from backend.exceptions import AppException, ErrorCodes
from backend.models.dtos.state_presentation import StatePresentation, SystemStatus

if TYPE_CHECKING:
    from backend.models.state import WorkflowState


class StatePresenter:
    """Handles the presentation logic for WorkflowState.

    Separates the concern of data serialization/flattening from the state model itself.
    Enforces strict typing and Fail Fast mechanics.
    """

    @staticmethod
    def flatten_state(state: WorkflowState) -> StatePresentation:
        """Projects the complex state into a simplified, strict DTO.

        Args:
            state: The WorkflowState instance to flatten.

        Returns:
            StatePresentation: The strict DTO result.

        Raises:
            AppException: If critical state data is missing (Fail Fast).
        """
        from backend.settings import get_settings

        settings = get_settings()

        # Fail Fast: Critical Integrity Check
        if not state.execution_id or not state.workflow_id:
            raise AppException(
                message="WorkflowState missing critical identity fields (execution_id/workflow_id).",
                status_code=500,
                details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR},
            )

        # Determine DB Source Label
        db_source = settings.active_backend.value

        # 1. System Status & Safety
        system_status = SystemStatus(
            execution_id=str(state.execution_id),
            workflow_id=state.workflow_id,
            workflow_name=state.workflow_name or "Unknown Workflow",
            timestamp=state.start_time.isoformat() if state.start_time else None,
            version="2.0",
            reasoning_chain_active=bool(state.reasoning_context),
            database_source=db_source,
            environment=settings.environment,
            uhka_havaittu=state.step_guard.security_check.uhka_havaittu
            if (state.step_guard and state.step_guard.security_check)
            else None,
            riski_taso=state.step_guard.security_check.riski_taso
            if (state.step_guard and state.step_guard.security_check)
            else None,
            logiikka_validi=not (
                state.step_falsifier.paattelyketjun_uskollisuus_auditointi.onko_post_hoc_rationalisointia
            )
            if (state.step_falsifier and state.step_falsifier.paattelyketjun_uskollisuus_auditointi)
            else None,
            organization_id=state.organization_id,
            user_id=state.user_id,
        )

        # MERGED REPORT (Max Simplicity)
        report: dict[str, Any] = {}

        # 2. Psychological & Behavioral Profile
        if state.step_profiler:
            report["psykologinen_profiili"] = {
                "profiili": state.step_profiler.psykologinen_profiili,
                "manipulaatio": state.step_profiler.manipulaatio_yritykset,
                "vinoumat": [b.model_dump() for b in state.step_profiler.tunnistetut_vinoumat]
                if state.step_profiler.tunnistetut_vinoumat
                else [],
                "intentio": state.step_profiler.intentio_analyysi,
            }

        # 3. Interaction Analysis
        if state.step_interaction:
            report["vuorovaikutus_analyysi"] = {
                "rooli": state.step_interaction.driver_classification,
                "ohjausliikkeet": state.step_interaction.ohjausliikkeet,
                "control_ratio": state.step_interaction.input_control_ratio,
                "strategiat": state.step_interaction.tunnistetut_strategiat,
            }

        # MERGED REPORT (Max Simplicity) - Continued

        # 1. High-Level Verdict
        if step_xai := getattr(state, "step_xai", None):
            report["final_verdict"] = step_xai.final_verdict
            report["confidence"] = step_xai.confidence_score
            if hasattr(step_xai, "comparison_data") and step_xai.comparison_data:
                # Direct check or field existence
                report["comparison_data"] = step_xai.comparison_data

        # Dynamic Score Flattening
        all_scores: dict[str, Any] = {}
        all_critique = []

        # Sources to check: 1. Dynamic Audit Results (New), 2. Legacy Fields (Old)
        sources_to_process: list[Any] = []

        # 1. Prefer Dynamic Storage
        if state.audit_results:
            for _step_id, res in state.audit_results.items():
                sources_to_process.append(res)

        # 2. Fallback to Legacy Fields if Dynamic Store is empty
        if not sources_to_process:
            if state.step_judge:
                sources_to_process.append(state.step_judge)
            if state.step_judge_cognitive:
                sources_to_process.append(state.step_judge_cognitive)

        for res_obj in sources_to_process:
            # Handle EvaluationResult (Dynamic)
            if hasattr(res_obj, "dimensions") and res_obj.dimensions:
                for dim in res_obj.dimensions:
                    key = dim.dimension_id
                    all_scores[key] = dim.score
                    all_scores[f"{key}_selitys"] = dim.reasoning

            # Handle TuomioJaPisteet (Legacy Adapter Object)
            elif hasattr(res_obj, "pisteet") and res_obj.pisteet:
                p = res_obj.pisteet
                if p.analyysi:
                    all_scores["analyysi"] = p.analyysi.arvosana
                    all_scores["analyysi_selitys"] = p.analyysi.perustelu
                if p.arviointi:
                    all_scores["arviointi"] = p.arviointi.arvosana
                    all_scores["arviointi_selitys"] = p.arviointi.perustelu
                if p.synteesi:
                    all_scores["synteesi"] = p.synteesi.arvosana
                    all_scores["synteesi_selitys"] = p.synteesi.perustelu

            # Collect Critiques
            if hasattr(res_obj, "critical_findings") and res_obj.critical_findings:
                all_critique.extend(res_obj.critical_findings)
            elif hasattr(res_obj, "kriittiset_havainnot_yhteenveto") and res_obj.kriittiset_havainnot_yhteenveto:
                all_critique.extend(res_obj.kriittiset_havainnot_yhteenveto)

        report["scores"] = all_scores
        report["kritiikki"] = list(set(all_critique))  # Dedupe

        # 2. Key Analysis Findings
        if state.step_analyst:
            if state.step_analyst.hypoteesit:
                report["analyysi_hypoteesit"] = [h.model_dump() for h in state.step_analyst.hypoteesit]
            if state.step_analyst.rag_todisteet:
                report["analyysi_todisteet"] = [r.model_dump() for r in state.step_analyst.rag_todisteet]

        if state.step_logician:
            if state.step_logician.toulmin_analyysi:
                report["logiikka_toulmin"] = [t.model_dump() for t in state.step_logician.toulmin_analyysi]
            if state.step_logician.walton_skeema:
                report["logiikka_skeema"] = state.step_logician.walton_skeema.tunnistettu_skeema

        if state.step_causal and state.step_causal.abduktiivinen_paatelma:
            report["kausaalisuus_paatelma"] = state.step_causal.abduktiivinen_paatelma

        if state.step_detector and state.step_detector.pre_mortem_analyysi:
            report["pre_mortem_analyysi"] = state.step_detector.pre_mortem_analyysi.model_dump()

        if state.step_falsifier and state.step_falsifier.paattelyketjun_uskollisuus_auditointi:
            report["logiikka_uskollisuus"] = (
                state.step_falsifier.paattelyketjun_uskollisuus_auditointi.uskollisuus_score
            )

        if state.step_overseer:
            if state.step_overseer.faktantarkistus_rfi:
                report["faktatarkistus"] = [f.model_dump() for f in state.step_overseer.faktantarkistus_rfi]
            if state.step_overseer.eettiset_havainnot:
                report["etiikka"] = [e.model_dump() for e in state.step_overseer.eettiset_havainnot]

        if state.step_panel:
            if (
                state.step_panel.performatiivisuus_auditointi
                and state.step_panel.performatiivisuus_auditointi.pre_mortem_analyysi
            ):
                report["pre_mortem_analyysi"] = (
                    state.step_panel.performatiivisuus_auditointi.pre_mortem_analyysi.model_dump()
                )

            if state.step_panel.logiikka_auditointi:
                if state.step_panel.logiikka_auditointi.toulmin_analyysi:
                    report["logiikka_toulmin"] = [
                        t.model_dump() for t in state.step_panel.logiikka_auditointi.toulmin_analyysi
                    ]
                if state.step_panel.logiikka_auditointi.walton_skeema:
                    report["logiikka_skeema"] = state.step_panel.logiikka_auditointi.walton_skeema.tunnistettu_skeema

            if (
                state.step_panel.kausaalinen_auditointi
                and state.step_panel.kausaalinen_auditointi.kausaalinen_auditointi
            ):
                report["kausaalisuus_paatelma"] = state.step_panel.kausaalinen_auditointi.abduktiivinen_paatelma

            if (
                state.step_panel.falsifiointi_auditointi
                and state.step_panel.falsifiointi_auditointi.paattelyketjun_uskollisuus_auditointi
            ):
                report["logiikka_uskollisuus"] = (
                    state.step_panel.falsifiointi_auditointi.paattelyketjun_uskollisuus_auditointi.uskollisuus_score
                )

            if state.step_panel.etiikka_ja_fakta:
                if state.step_panel.etiikka_ja_fakta.faktantarkistus_rfi:
                    report["faktatarkistus"] = [
                        f.model_dump() for f in state.step_panel.etiikka_ja_fakta.faktantarkistus_rfi
                    ]
                if state.step_panel.etiikka_ja_fakta.eettiset_havainnot:
                    report["etiikka"] = [e.model_dump() for e in state.step_panel.etiikka_ja_fakta.eettiset_havainnot]

        # 3. Actionable Feedback
        if state.step_coach:
            report["palaute_yhteenveto"] = state.step_coach.kannustava_palaute
            actions = []
            if state.step_coach.kehityskohteet_konkreettisesti:
                for group in state.step_coach.kehityskohteet_konkreettisesti:
                    for item in group.kohdat:
                        actions.append(f"[{group.kategoria}] {item.otsikko}: {item.kuvaus}")
            report["kehitystoimenpiteet"] = actions
            report["kehitysehdotukset"] = state.step_coach.lopputuloksen_kehitysehdotukset

            # Add Citations if available (Coach 2.0 feature)
            if hasattr(state.step_coach, "lahdeluettelo") and state.step_coach.lahdeluettelo:
                report["lahdet"] = state.step_coach.lahdeluettelo

        if state.step_archivist:
            report["linjakkuus"] = state.step_archivist.compliance_analysis

        # 6. Raw Data (Legacy/Debug Support)
        # Step 1 Cleanup: Excluding purely technical IDs and hashes.
        noise_fields = {
            "log_id",
            "execution_id",
            "input_text_hash",
            "semanttinen_tarkistussumma",
            "system_prompt_version",
        }

        # Helper for safe dumping
        def _safe_dump(obj: Any | None) -> dict[str, Any] | None:
            if obj and hasattr(obj, "model_dump"):
                return obj.model_dump(exclude=noise_fields, exclude_none=True)
            return None

        # Build raw steps dict dynamically
        raw_steps_dict = {
            "step_guard": _safe_dump(state.step_guard),
            "step_analyst": _safe_dump(state.step_analyst),
            "step_interaction": _safe_dump(state.step_interaction),
            "step_profiler": _safe_dump(state.step_profiler),
            "step_logician": _safe_dump(state.step_logician),
            "step_falsifier": _safe_dump(state.step_falsifier),
            "step_causal": _safe_dump(state.step_causal),
            "step_detector": _safe_dump(state.step_detector),
            "step_overseer": _safe_dump(state.step_overseer),
            "step_archivist": _safe_dump(state.step_archivist),
            "step_judge": _safe_dump(state.step_judge),
            "step_judge_cognitive": _safe_dump(state.step_judge_cognitive),
            "step_coach": _safe_dump(state.step_coach),
            "step_panel": _safe_dump(state.step_panel),
            "step_xai": _safe_dump(state.step_xai),
        }

        # Filter top-level Nones
        raw_steps = {k: v for k, v in raw_steps_dict.items() if v is not None}

        # Construct Final DTO
        return StatePresentation(System_Status=system_status, Report=report, Raw_Steps=raw_steps)
