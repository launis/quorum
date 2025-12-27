from typing import Optional, List, Dict, Any, Literal, Union
from pydantic import BaseModel, Field
from datetime import datetime
from backend.models.domain import (
    TaintedData, 
    TodistusKartta, 
    ArgumentaatioAnalyysi,
    LogiikkaAuditointi, 
    KausaalinenAuditointi,
    PerformatiivisuusAuditointi, 
    EtiikkaJaFakta,
    TuomioJaPisteet, 
    XAIReport,
    ProfilerAnalysis,
    CaseLawContext,
    CoachingPlan,
    InteractionAnalysis,
    PanelAudit
)

class InputData(BaseModel):
    """Raakadata, joka tulee käyttäjältä."""
    history_text: str
    product_text: str
    reflection_text: str
    # Optional bibliography context
    bibliography_context: Optional[List[str]] = None

class WorkflowState(BaseModel):
    """
    Tämä on "Blackboard". Se elää muistissa koko ajon ajan.
    Kaikki agentit lukevat tästä ja kirjoittavat tähän.
    """
    # Metadata
    execution_id: str
    start_time: datetime = Field(default_factory=datetime.now)
    current_step_name: str = "init"
    
    # Syötteet (Read-only agenteille)
    inputs: InputData
    
    # Agenttien tulosteet (Alussa None, täyttyvät matkan varrella)
    step_guard: Optional[TaintedData] = None
    step_analyst: Optional[TodistusKartta] = None
    step_profiler: Optional[ProfilerAnalysis] = None # Step 2.5
    step_logician: Optional[ArgumentaatioAnalyysi] = None
    step_falsifier: Optional[LogiikkaAuditointi] = None
    step_overseer: Optional[EtiikkaJaFakta] = None
    step_causal: Optional[KausaalinenAuditointi] = None
    step_detector: Optional[PerformatiivisuusAuditointi] = None
    step_judge: Optional[TuomioJaPisteet] = None
    step_archivist: Optional[CaseLawContext] = None # Step 8.5/8a
    step_coach: Optional[CoachingPlan] = None # Step 8.5/8c
    step_interaction: Optional[InteractionAnalysis] = None # Step 2.2
    step_panel: Optional[PanelAudit] = None
    step_reporter: Optional[XAIReport] = None

    # Formatted output
    xai_report_formatted: Optional[str] = None

    # Apumuuttujat
    aux_data: Dict[str, Any] = Field(default_factory=dict)

    def get_previous_outputs_summary(self) -> str:
        """
        Kerää yhteenvedon aiempien vaiheiden tuloksista.
        """
        summary = []
        steps = [
            ("Vartija", self.step_guard),
            ("Analyytikko", self.step_analyst),
            ("Profiloija", self.step_profiler),
            ("Loogikko", self.step_logician),
            ("Falsifioija", self.step_falsifier),
            ("Valvoja", self.step_overseer),
            ("Kausaalinen", self.step_causal),
            ("Tunnistaja", self.step_detector),
            ("Tuomari", self.step_judge),
            ("Arkistonhoitaja", self.step_archivist),
            ("Valmentaja", self.step_coach),
            ("Vuorovaikutusanalysaattori", self.step_interaction),
            ("Paneeli", self.step_panel)
        ]
        
        for name, data in steps:
            if data:
                # Use model_dump_json() for Pydantic v2 or json() for v1
                # formatting for readability
                try:
                    content = data.model_dump_json(indent=2)
                except AttributeError:
                    content = str(data)
                summary.append(f"--- {name} ---\n{content}\n")
        
        if not summary:
            return "(Ei aiempia tuloksia)"
            
        return "\n".join(summary)

    def to_flat_dict(self) -> Dict[str, Any]:
        """
        Flattens the state into a smart 2-layer structure for UI consumption.
        Groups data by logical domain rather than agent identity.
        """
        # DEBUG TRACE
        flat = {}
        
        # 1. System Status & Safety
        flat["System_Status"] = {
            "execution_id": self.execution_id,
            "timestamp": self.start_time.isoformat() if self.start_time else None,
            "version": "2.0",
            "uhka_havaittu": self.step_guard.security_check.uhka_havaittu if (self.step_guard and self.step_guard.security_check) else None,
            "riski_taso": self.step_guard.security_check.riski_taso if (self.step_guard and self.step_guard.security_check) else None,
            "logiikka_validi": not (self.step_falsifier.paattelyketjun_uskollisuus_auditointi.onko_post_hoc_rationalisointia) if (self.step_falsifier and self.step_falsifier.paattelyketjun_uskollisuus_auditointi) else None
        }

        # MERGED REPORT (Max Simplicity)
        report = {}

        # 2. Psychological & Behavioral Profile
        if self.step_profiler:
            report["psykologinen_profiili"] = {
                "profiili": self.step_profiler.psykologinen_profiili,
                "manipulaatio": self.step_profiler.manipulaatio_yritykset,
                "vinoumat": [b.model_dump() for b in self.step_profiler.tunnistetut_vinoumat] if self.step_profiler.tunnistetut_vinoumat else [],
                "intentio": self.step_profiler.intentio_analyysi
            }

        # 3. Interaction Analysis
        if self.step_interaction:
            report["vuorovaikutus_analyysi"] = {
                "rooli": self.step_interaction.driver_classification,
                "ohjausliikkeet": self.step_interaction.ohjausliikkeet,
                "control_ratio": self.step_interaction.input_control_ratio,
                "strategiat": self.step_interaction.tunnistetut_strategiat
            }

        # MERGED REPORT (Max Simplicity) - Continued
        
        # 1. High-Level Verdict
        if self.step_reporter:
            report["final_verdict"] = self.step_reporter.final_verdict
            report["confidence"] = self.step_reporter.confidence_score
        
        if self.step_judge and self.step_judge.pisteet:
            p = self.step_judge.pisteet
            report["scores"] = {
                "analyysi": p.analyysi.arvosana if p.analyysi else 0,
                "analyysi_selitys": p.analyysi.perustelu if p.analyysi else "",
                "arviointi": p.arviointi.arvosana if p.arviointi else 0,
                "arviointi_selitys": p.arviointi.perustelu if p.arviointi else "",
                "synteesi": p.synteesi.arvosana if p.synteesi else 0,
                "synteesi_selitys": p.synteesi.perustelu if p.synteesi else ""
            }
            report["kritiikki"] = self.step_judge.kriittiset_havainnot_yhteenveto

        # 2. Key Analysis Findings
        if self.step_analyst:
             if self.step_analyst.hypoteesit: report['analyysi_hypoteesit'] = [h.model_dump() for h in self.step_analyst.hypoteesit]
             if self.step_analyst.rag_todisteet: report['analyysi_todisteet'] = [r.model_dump() for r in self.step_analyst.rag_todisteet]

        if self.step_logician:
             if self.step_logician.toulmin_analyysi: report['logiikka_toulmin'] = [t.model_dump() for t in self.step_logician.toulmin_analyysi]
             if self.step_logician.walton_skeema: report['logiikka_skeema'] = self.step_logician.walton_skeema.tunnistettu_skeema

        if self.step_causal and self.step_causal.abduktiivinen_paatelma:
             report['kausaalisuus_paatelma'] = self.step_causal.abduktiivinen_paatelma

        if self.step_detector and self.step_detector.pre_mortem_analyysi:
             report['pre_mortem_analyysi'] = self.step_detector.pre_mortem_analyysi.model_dump()

        if self.step_falsifier and self.step_falsifier.paattelyketjun_uskollisuus_auditointi:
             report['logiikka_uskollisuus'] = self.step_falsifier.paattelyketjun_uskollisuus_auditointi.uskollisuus_score

        if self.step_overseer:
             if self.step_overseer.faktantarkistus_rfi:
                 report['faktatarkistus'] = [f.model_dump() for f in self.step_overseer.faktantarkistus_rfi]
             if self.step_overseer.eettiset_havainnot:
                 report['etiikka'] = [e.model_dump() for e in self.step_overseer.eettiset_havainnot]

        if self.step_panel:
            if self.step_panel.performatiivisuus_auditointi and self.step_panel.performatiivisuus_auditointi.pre_mortem_analyysi:
                 # Override or set if not present (Panel is newer info often)
                 report['pre_mortem_analyysi'] = self.step_panel.performatiivisuus_auditointi.pre_mortem_analyysi.model_dump()

            if self.step_panel.logiikka_auditointi:
                 if self.step_panel.logiikka_auditointi.toulmin_analyysi: report['logiikka_toulmin'] = [t.model_dump() for t in self.step_panel.logiikka_auditointi.toulmin_analyysi]
                 if self.step_panel.logiikka_auditointi.walton_skeema: report['logiikka_skeema'] = self.step_panel.logiikka_auditointi.walton_skeema.tunnistettu_skeema
            
            if self.step_panel.kausaalinen_auditointi and self.step_panel.kausaalinen_auditointi.kausaalinen_auditointi:
                 report['kausaalisuus_paatelma'] = self.step_panel.kausaalinen_auditointi.abduktiivinen_paatelma

            if self.step_panel.falsifiointi_auditointi and self.step_panel.falsifiointi_auditointi.paattelyketjun_uskollisuus_auditointi:
                 report['logiikka_uskollisuus'] = self.step_panel.falsifiointi_auditointi.paattelyketjun_uskollisuus_auditointi.uskollisuus_score

            if self.step_panel.etiikka_ja_fakta:
                 if self.step_panel.etiikka_ja_fakta.faktantarkistus_rfi:
                     report['faktatarkistus'] = [f.model_dump() for f in self.step_panel.etiikka_ja_fakta.faktantarkistus_rfi]
                 if self.step_panel.etiikka_ja_fakta.eettiset_havainnot:
                     report['etiikka'] = [e.model_dump() for e in self.step_panel.etiikka_ja_fakta.eettiset_havainnot]

        # 3. Actionable Feedback
        if self.step_coach:
            report["palaute_yhteenveto"] = self.step_coach.kannustava_palaute
            actions = []
            if self.step_coach.kehityskohteet_konkreettisesti:
                for group in self.step_coach.kehityskohteet_konkreettisesti:
                    for item in group.kohdat:
                        actions.append(f"[{group.kategoria}] {item.otsikko}: {item.kuvaus}")
            report["kehitystoimenpiteet"] = actions
            report["kehitysehdotukset"] = self.step_coach.lopputuloksen_kehitysehdotukset
            
            # Add Citations if available (Coach 2.0 feature)
            if hasattr(self.step_coach, 'lahdeluettelo') and self.step_coach.lahdeluettelo:
                report["lahdet"] = self.step_coach.lahdeluettelo

        if self.step_archivist:
             report["linjakkuus"] = self.step_archivist.linjakkuus_analyysi

        # Assign to root
        flat["Report"] = report
        
        # 6. Raw Data (Legacy/Debug Support)
        # We include the raw dumps of steps for components that rely on specific internal structures
        # or for "View Raw JSON" debugging.
        # 6. Raw Data (Legacy/Debug Support)
        # Step 1 Cleanup: Excluding purely technical IDs and hashes.
        noise_fields = {
            'log_id', 'execution_id', 'input_text_hash', 
            'semanttinen_tarkistussumma', 'system_prompt_version'
        }

        raw_steps_dict = {
            "step_guard": self.step_guard.model_dump(exclude=noise_fields, exclude_none=True) if self.step_guard else None,
            "step_analyst": self.step_analyst.model_dump(exclude=noise_fields, exclude_none=True) if self.step_analyst else None,
            "step_interaction": self.step_interaction.model_dump(exclude=noise_fields, exclude_none=True) if self.step_interaction else None,
            "step_profiler": self.step_profiler.model_dump(exclude=noise_fields, exclude_none=True) if self.step_profiler else None,
            "step_logician": self.step_logician.model_dump(exclude=noise_fields, exclude_none=True) if self.step_logician else None,
            "step_falsifier": self.step_falsifier.model_dump(exclude=noise_fields, exclude_none=True) if self.step_falsifier else None,
            "step_causal": self.step_causal.model_dump(exclude=noise_fields, exclude_none=True) if self.step_causal else None,
            "step_detector": self.step_detector.model_dump(exclude=noise_fields, exclude_none=True) if self.step_detector else None,
            "step_overseer": self.step_overseer.model_dump(exclude=noise_fields, exclude_none=True) if self.step_overseer else None,
            "step_archivist": self.step_archivist.model_dump(exclude=noise_fields, exclude_none=True) if self.step_archivist else None,
            "step_judge": self.step_judge.model_dump(exclude=noise_fields, exclude_none=True) if self.step_judge else None,
            "step_coach": self.step_coach.model_dump(exclude=noise_fields, exclude_none=True) if self.step_coach else None,
            "step_panel": self.step_panel.model_dump(exclude=noise_fields, exclude_none=True) if self.step_panel else None,
            "step_reporter": self.step_reporter.model_dump(exclude=noise_fields, exclude_none=True) if self.step_reporter else None,
        }
        
        # Filter top-level Nones
        flat["Raw_Steps"] = {k: v for k, v in raw_steps_dict.items() if v is not None}
        
        return flat
