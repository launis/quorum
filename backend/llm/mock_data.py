"""Mock Data Store for AI Layer Testing (Zero-Token Cost)."""

from typing import Any

from backend.models.domain import (
    ArgumentaatioAnalyysi,
    ArchivistOutput,
    CoachingPlan,
    DimensionResultItem,
    EettinenHavainto,
    EtiikkaJaFakta,
    EvaluationResult,
    FaktantarkistusRFI,
    Hypoteesi,
    InteractionAnalysis,
    KausaalinenAuditointi,
    KausaalinenAuditointiData,
    KognitiivinenTaso,
    KontrafaktuaalinenTesti,
    LogiikkaAuditointi,
    Metadata,
    PaattelyketjunUskollisuus,
    PanelAudit,
    PerformatiivisuusAuditointi,
    PerformatiivisuusHeuristiikka,
    PreMortemAnalyysi,
    ProfilerAnalysis,
    RagTodiste,
    SafeDataContent,
    ScoreCardItem,
    SecurityCheck,
    TaintedData,
    TaintedDataContent,
    TodistusKartta,
    ToulminKomponentti,

    WaltonSkeema,
    WaltonStressitesti,
    XAIReport,
)


# --- Common Metadata ---
MOCK_METADATA = Metadata(
    luontiaika="2026-01-01T12:00:00Z", agentti="MOCK_AGENT", vaihe=1, versio="2.0", suoritus_ymparisto="Internal"
)

# --- Task Outputs ---

# 1. Guard (Usually logic-based, but if LLM used in future)
# Note: Switched to TaintedData (Jan 19)
# MOCK_GUARD_OUTPUT REMOVED - Use MOCK_TAINTED_DATA instead.

# 2. Analyst (TodistusKartta)
MOCK_ANALYST_OUTPUT = TodistusKartta(
    metadata=MOCK_METADATA.model_copy(update={"agentti": "Analyst", "vaihe": 3}),
    metodologinen_loki="Mock Analysis applied.",
    edellisen_vaiheen_validointi="Pass",
    semanttinen_tarkistussumma="hash_123",
    reasoning_trace="Mock reasoning trace...",
    hypoteesit=[
        Hypoteesi(
            id="H1",
            vaite_teksti="[KIRJOITA TÄHÄN HAVAINTO SYÖTTEESTÄ]",
            loytyyko_todisteita=True,
            hakusana_ehdotus="[HAKUTERMI]",
        )
    ],
    rag_todisteet=[
        RagTodiste(
            viittaa_hypoteesiin_id="H1",
            perusteet="[PERUSTELE HAVAINTO SYÖTTEELLÄ]",
            konteksti_segmentti="[SUORA SITAATTI SYÖTTEESTÄ TÄHÄN]",
            relevanssi_score=95,
        )
    ],
)

# 3. Panel (PanelAudit - Composite)
MOCK_PANEL_OUTPUT = PanelAudit(
    metadata=MOCK_METADATA.model_copy(update={"agentti": "Panel", "vaihe": 4}),
    metodologinen_loki="Mock Panel Review.",
    edellisen_vaiheen_validointi="Pass",
    semanttinen_tarkistussumma="hash_456",
    # Logician
    logiikka_auditointi=ArgumentaatioAnalyysi(
        metadata=MOCK_METADATA,
        metodologinen_loki="Logician",
        edellisen_vaiheen_validointi="OK",
        semanttinen_tarkistussumma="h1",
        toulmin_analyysi=[
            ToulminKomponentti(
                vaite_id="H1",
                claim="[VÄITE]",
                data="[TODISTE]",
                warrant="[PÄÄTTELYSILTA]",
                backing="[TUKI]",
            )
        ],
        kognitiivinen_taso=KognitiivinenTaso(bloom_taso="Analyysi", strateginen_syvyys="Keskinkertainen"),
        walton_skeema=WaltonSkeema(tunnistettu_skeema="Asiantuntijalausunto", kriittiset_kysymykset=["Onko lähde uskottava?"]),
    ),
    # Falsifier
    falsifiointi_auditointi=LogiikkaAuditointi(
        metadata=MOCK_METADATA,
        metodologinen_loki="Falsifier",
        edellisen_vaiheen_validointi="OK",
        semanttinen_tarkistussumma="h2",
        walton_stressitesti_loydokset=[
            WaltonStressitesti(kysymys="Bias?", kestiko_todistusaineisto=True, havainto="No bias")
        ],
        paattelyketjun_uskollisuus_auditointi=PaattelyketjunUskollisuus(
            onko_post_hoc_rationalisointia=False, perustelu="Clean deduction", uskollisuus_score="KORKEA"
        ),
    ),
    # Causal
    kausaalinen_auditointi=KausaalinenAuditointi(
        metadata=MOCK_METADATA,
        metodologinen_loki="Causal",
        edellisen_vaiheen_validointi="OK",
        semanttinen_tarkistussumma="h3",
        kausaalinen_auditointi=KausaalinenAuditointiData(aikajana_validi=True, havainnot="Linear"),
        kontrafaktuaalinen_testi=KontrafaktuaalinenTesti(
            skenaario_A_toteutunut="A", skenaario_B_simulaatio="B", uskottavuus_arvio="Plausible"
        ),
        abduktiivinen_paatelma="Aito Oivallus",
    ),
    # Detector
    performatiivisuus_auditointi=PerformatiivisuusAuditointi(
        metadata=MOCK_METADATA,
        metodologinen_loki="Detector",
        edellisen_vaiheen_validointi="OK",
        semanttinen_tarkistussumma="h4",
        performatiivisuus_heuristiikat=[
            PerformatiivisuusHeuristiikka(heuristiikka="Buzzwords", lippu_nostettu=False, kuvaus="Clean")
        ],
        pre_mortem_analyysi=PreMortemAnalyysi(suoritettu=True, hiljaiset_signaalit=["None"]),
        yleisarvio_aitoudesta="Orgaaninen",
    ),
    # Overseer
    etiikka_ja_fakta=EtiikkaJaFakta(
        metadata=MOCK_METADATA,
        metodologinen_loki="Overseer",
        edellisen_vaiheen_validointi="OK",
        semanttinen_tarkistussumma="h5",
        faktantarkistus_rfi=[
            FaktantarkistusRFI(
                vaite="[TARKASTETTAVA VÄITE]", verifiointi_tulos="Vahvistettu", lahde_tai_paattely="[LÄHDE]"
            )
        ],
        eettiset_havainnot=[EettinenHavainto(tyyppi="Ei havaittu", vakavuus="N/A", kuvaus="Ei eettisiä riskejä")],
    ),
)

# 4. Interaction Analysis
MOCK_INTERACTION_OUTPUT = InteractionAnalysis(
    metadata=MOCK_METADATA.model_copy(update={"agentti": "Interaction", "vaihe": 3}),
    metodologinen_loki="Mock Interaction Audit",
    edellisen_vaiheen_validointi="Pass",
    semanttinen_tarkistussumma="hash_int",
    tunnistetut_strategiat=["[STRATEGIA 1]", "[STRATEGIA 2]"],
    ohjausliikkeet=0,
    driver_classification="Matkustaja",
    input_control_ratio=0.0,
    total_turn_count=10,
    imperative_command_count=0,
)

# 5. Profiler Analysis
MOCK_PROFILER_OUTPUT = ProfilerAnalysis(
    metadata=MOCK_METADATA.model_copy(update={"agentti": "Profiler", "vaihe": 4}),
    metodologinen_loki="Mock Profiler",
    edellisen_vaiheen_validointi="Pass",
    semanttinen_tarkistussumma="hash_prof",
    intentio_analyysi="[ANALYSOI KIRJOITTAJAN TARKOITUS]",
    tunnetila_ja_savy="[ANALYSOI SÄVY]",
    tunnistetut_vinoumat=[],
    psykologinen_profiili="[PROFIILI]",
    manipulaatio_yritykset="Ei havaittu",
)

# 6. Archivist Output (ArchivistOutput)
MOCK_ARCHIVIST_OUTPUT = ArchivistOutput(
    metadata=MOCK_METADATA.model_copy(update={"agentti": "Archivist", "vaihe": 8}),
    metodologinen_loki="Mock Archivist",
    edellisen_vaiheen_validointi="Pass",
    semanttinen_tarkistussumma="hash_arch",
    analysis="Aligned with precedents.",
    compliance_score=100,
    recommendations=["Keep up good work"],
)

# 7. Judge Output
# 7. Judge Output (EvaluationResult)
MOCK_JUDGE_OUTPUT = EvaluationResult(
    metadata=MOCK_METADATA.model_copy(update={"agentti": "Judge", "vaihe": 9}),
    metodologinen_loki="Mock Judge",
    edellisen_vaiheen_validointi="Pass",
    semanttinen_tarkistussumma="hash_judge",
    matrix_id="mock_matrix",
    scale_min=1,
    scale_max=5,
    total_score=4.5,
    dimensions=[
        DimensionResultItem(dimension_id="dim1", score=5, reasoning="Excellent"),
        DimensionResultItem(dimension_id="dim2", score=4, reasoning="Good"),
    ],
    critical_findings=["[KRIITTINEN HAVAINTO]"],
)

# 8. Coach Output
MOCK_COACH_OUTPUT = CoachingPlan(
    metadata=MOCK_METADATA.model_copy(update={"agentti": "Coach", "vaihe": 12}),
    metodologinen_loki="Mock Coach",
    edellisen_vaiheen_validointi="Pass",
    semanttinen_tarkistussumma="hash_coach",
    kannustava_palaute="[POSITIIVINEN PALAUTE]",
    kehityskohteet_konkreettisesti=[],
    lopputuloksen_kehitysehdotukset=["[KONKREETTINEN EHDOTUS]"],
    lahdeluettelo=[],
)

# 9. XAI Report
MOCK_XAI_OUTPUT = XAIReport(
    metadata=MOCK_METADATA.model_copy(update={"agentti": "XAI", "vaihe": 13}),
    metodologinen_loki="Mock XAI",
    edellisen_vaiheen_validointi="Pass",
    semanttinen_tarkistussumma="hash_xai",
    executive_summary="[TIIVISTELMÄ]",
    analysis_strengths="[VAHVUUDET]",
    analysis_weaknesses="[HEIKKOUDET]",
    analysis_opportunities="[MAHDOLLISUUDET]",
    analysis_recommendations="[SUOSITUKSET]",
    final_verdict="[LOPPUTULOS]",
    confidence_score=0.95,
    comparison_data={"status": "Mock Comparison Data"},
    score_cards=[
        ScoreCardItem(
            agent_name="Standard Judge",
            total_score=4.5,
            max_score=5,
            verdict="High Fidelity",
            dimensions=[
                DimensionResultItem(dimension_id="logic", score=5, reasoning="Clear logic"),
                DimensionResultItem(dimension_id="ethics", score=4, reasoning="Good ethics"),
            ],
        )
    ],
)


# 10. Tainted Data (Guard Agent Model)
MOCK_TAINTED_DATA = TaintedData(
    metadata=MOCK_METADATA.model_copy(update={"agentti": "GuardAgent", "vaihe": 1}),
    metodologinen_loki="Mock Guard Scan",
    edellisen_vaiheen_validointi="N/A",
    semanttinen_tarkistussumma="hash_guard",
    data=TaintedDataContent(
        keskusteluhistoria="{{FILE: Keskusteluhistoria.pdf}}",
        lopputuote="{{FILE: Lopputuote.pdf}}",
        reflektiodokumentti="{{FILE: Reflektiodokumentti.pdf}}",
    ),
    security_check=SecurityCheck(
        uhka_havaittu=False,
        adversariaalinen_simulaatio_tulos="[SIMULAATION TULOS]",
        riski_taso="MATALA",
        anonymisointi_tehty=True,
        tietosuoja_raportti="Mock data redacted.",
    ),
    safe_data=SafeDataContent(
        keskusteluhistoria="Sanitized history",
        lopputuote="Sanitized product",
        reflektiodokumentti="Sanitized reflection",
    ),
)


# Registry Mapping
# Maps the Pydantic MODEL CLASS to the instance
MOCK_REGISTRY: dict[type[Any], Any] = {
    TodistusKartta: MOCK_ANALYST_OUTPUT,
    PanelAudit: MOCK_PANEL_OUTPUT,

    TaintedData: MOCK_TAINTED_DATA,
    InteractionAnalysis: MOCK_INTERACTION_OUTPUT,
    ProfilerAnalysis: MOCK_PROFILER_OUTPUT,
    ArchivistOutput: MOCK_ARCHIVIST_OUTPUT,
    EvaluationResult: MOCK_JUDGE_OUTPUT,
    CoachingPlan: MOCK_COACH_OUTPUT,
    XAIReport: MOCK_XAI_OUTPUT,
    # Expose Panel Components individually in case tasks are run in isolation
    ArgumentaatioAnalyysi: MOCK_PANEL_OUTPUT.logiikka_auditointi,
    LogiikkaAuditointi: MOCK_PANEL_OUTPUT.falsifiointi_auditointi,
    KausaalinenAuditointi: MOCK_PANEL_OUTPUT.kausaalinen_auditointi,
    PerformatiivisuusAuditointi: MOCK_PANEL_OUTPUT.performatiivisuus_auditointi,
    EtiikkaJaFakta: MOCK_PANEL_OUTPUT.etiikka_ja_fakta,
}

# --- Lookups & Helpers ---

AGENT_CLASS_TO_MOCK_KEY = {
    "GuardAgent": "guard_agent",
    "AnalystAgent": "analyst_agent",
    "InteractionAnalystAgent": "interaction_agent",
    "LogicianAgent": "logician_agent",
    "LogicalFalsifierAgent": "falsifier_agent",
    "CausalAnalystAgent": "causal_agent",
    "PerformativityDetectorAgent": "performativity_agent",
    "FactualOverseerAgent": "fact_checker_agent",
    "ProfilerAgent": "profiler_agent",
    "ArchivistAgent": "archivist_agent",
    "JudgeAgent": "judge_agent",
    "CoachAgent": "coach_agent",
    "XAIReporterAgent": "xai_agent",
    "PanelAgent": "panel_agent",
}


def get_fallback_data(key: str) -> dict[str, Any]:
    """Retrieves the default mock data for a given agent key."""
    if key == "guard_agent":
        return MOCK_TAINTED_DATA.model_dump()
    elif key == "analyst_agent":
        return MOCK_ANALYST_OUTPUT.model_dump()
    elif key == "interaction_agent":
        return MOCK_INTERACTION_OUTPUT.model_dump()
    elif key == "logician_agent":
        return MOCK_PANEL_OUTPUT.logiikka_auditointi.model_dump()
    elif key == "falsifier_agent":
        return MOCK_PANEL_OUTPUT.falsifiointi_auditointi.model_dump()
    elif key == "causal_agent":
        return MOCK_PANEL_OUTPUT.kausaalinen_auditointi.model_dump()
    elif key == "performativity_agent":
        return MOCK_PANEL_OUTPUT.performatiivisuus_auditointi.model_dump()
    elif key == "fact_checker_agent":
        return MOCK_PANEL_OUTPUT.etiikka_ja_fakta.model_dump()
    elif key == "profiler_agent":
        return MOCK_PROFILER_OUTPUT.model_dump()
    elif key == "archivist_agent":
        return MOCK_ARCHIVIST_OUTPUT.model_dump()
    elif key == "panel_agent":
        return MOCK_PANEL_OUTPUT.model_dump()
    elif key == "judge_agent":
        return MOCK_JUDGE_OUTPUT.model_dump()
    elif key == "coach_agent":
        return MOCK_COACH_OUTPUT.model_dump()
    elif key == "xai_agent":
        return MOCK_XAI_OUTPUT.model_dump()

    return {"message": "Mock data not found for key", "key": key}
