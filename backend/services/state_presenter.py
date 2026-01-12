"""Presenter layer for formatting WorkflowState into UI-ready structures."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from backend.models.state import WorkflowState


class StatePresenter:
    """Handles the presentation logic for WorkflowState.

    Separates the concern of data serialization/flattening from the state model itself.
    """

    @staticmethod
    def flatten_state(state: WorkflowState) -> dict[str, Any]:
        """Projects the complex state into a simplified, flat dictionary.

        This structured is optimized for frontend UI consumption (React/JSON).
        Does NOT rely on specific UI code but organizes data logically.

        Args:
            state: The WorkflowState instance to flatten.

        Returns:
            Dict[str, Any]: The flattened result object.

        """
        from backend.settings import get_settings

        settings = get_settings()

        # Determine DB Source Label
        # Use the single source of truth from Settings (SSO)
        # Returns: "FIRESTORE", "LOCAL", or "MOCK"
        db_source = settings.active_backend.value

        # DEBUG TRACE
        flat: dict[str, Any] = {}

        # 1. System Status & Safety
        flat["System_Status"] = {
            "execution_id": state.execution_id,
            "workflow_id": state.workflow_id,
            "workflow_name": state.workflow_name,
            "timestamp": state.start_time.isoformat() if state.start_time else None,
            "version": "2.0",
            # New Audit Metadata
            "reasoning_chain_active": bool(state.reasoning_context),
            "database_source": db_source,
            "environment": settings.environment,
            "uhka_havaittu": state.step_guard.security_check.uhka_havaittu
            if (state.step_guard and state.step_guard.security_check)
            else None,
            "riski_taso": state.step_guard.security_check.riski_taso
            if (state.step_guard and state.step_guard.security_check)
            else None,
            "logiikka_validi": not (
                state.step_falsifier.paattelyketjun_uskollisuus_auditointi.onko_post_hoc_rationalisointia
            )
            if (state.step_falsifier and state.step_falsifier.paattelyketjun_uskollisuus_auditointi)
            else None,
            # Identity Context
            "organization_id": state.organization_id,
            "user_id": state.user_id,
        }

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
        if state.step_reporter:
            report["final_verdict"] = state.step_reporter.final_verdict
            report["confidence"] = state.step_reporter.confidence_score
            if hasattr(state.step_reporter, "comparison_data") and state.step_reporter.comparison_data:
                # Direct check or field existence
                report["comparison_data"] = state.step_reporter.comparison_data

        # Dynamic Score Flattening
        # We iterate through all stored audit results (e.g., standard, cognitive, etc.)
        # and merge them into the flat 'scores' dictionary.

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

        # visited_keys = set() # unused

        for res_obj in sources_to_process:
            # Handle EvaluationResult (Dynamic)
            if hasattr(res_obj, "dimensions") and res_obj.dimensions:
                for dim in res_obj.dimensions:
                    key = dim.dimension_id
                    # Prevent overwriting if multiple matrices evaluate same thing (first wins? or merge?)
                    # For now, let's allow overwrite or use unique keys if possible.
                    # ideally keys are unique per matrix logic.
                    all_scores[key] = dim.score
                    all_scores[f"{key}_selitys"] = dim.reasoning

            # Handle TuomioJaPisteet (Legacy Adapter Object)
            elif hasattr(res_obj, "pisteet") and res_obj.pisteet:
                p = res_obj.pisteet
                # Map the legacy 3 fixed fields
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
                # Override or set if not present (Panel is newer info often)
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
            report["linjakkuus"] = state.step_archivist.linjakkuus_analyysi

        # Assign to root
        flat["Report"] = report

        # 6. Raw Data (Legacy/Debug Support)
        # Step 1 Cleanup: Excluding purely technical IDs and hashes.
        noise_fields = {
            "log_id",
            "execution_id",
            "input_text_hash",
            "semanttinen_tarkistussumma",
            "system_prompt_version",
        }

        # Build raw steps dict dynamically based on presence
        # This mirrors the original logic but uses state.step_X
        raw_steps_dict = {
            "step_guard": state.step_guard.model_dump(exclude=noise_fields, exclude_none=True)
            if state.step_guard
            else None,
            "step_analyst": state.step_analyst.model_dump(exclude=noise_fields, exclude_none=True)
            if state.step_analyst
            else None,
            "step_interaction": state.step_interaction.model_dump(exclude=noise_fields, exclude_none=True)
            if state.step_interaction
            else None,
            "step_profiler": state.step_profiler.model_dump(exclude=noise_fields, exclude_none=True)
            if state.step_profiler
            else None,
            "step_logician": state.step_logician.model_dump(exclude=noise_fields, exclude_none=True)
            if state.step_logician
            else None,
            "step_falsifier": state.step_falsifier.model_dump(exclude=noise_fields, exclude_none=True)
            if state.step_falsifier
            else None,
            "step_causal": state.step_causal.model_dump(exclude=noise_fields, exclude_none=True)
            if state.step_causal
            else None,
            "step_detector": state.step_detector.model_dump(exclude=noise_fields, exclude_none=True)
            if state.step_detector
            else None,
            "step_overseer": state.step_overseer.model_dump(exclude=noise_fields, exclude_none=True)
            if state.step_overseer
            else None,
            "step_archivist": state.step_archivist.model_dump(exclude=noise_fields, exclude_none=True)
            if state.step_archivist
            else None,
            "step_judge": state.step_judge.model_dump(exclude=noise_fields, exclude_none=True)
            if state.step_judge
            else None,
            "step_judge_cognitive": state.step_judge_cognitive.model_dump(exclude=noise_fields, exclude_none=True)
            if state.step_judge_cognitive
            else None,
            "step_coach": state.step_coach.model_dump(exclude=noise_fields, exclude_none=True)
            if state.step_coach
            else None,
            "step_panel": state.step_panel.model_dump(exclude=noise_fields, exclude_none=True)
            if state.step_panel
            else None,
            "step_reporter": state.step_reporter.model_dump(exclude=noise_fields, exclude_none=True)
            if state.step_reporter
            else None,
        }

        # Filter top-level Nones
        flat["Raw_Steps"] = {k: v for k, v in raw_steps_dict.items() if v is not None}

        return flat
