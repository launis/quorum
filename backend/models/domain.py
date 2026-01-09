"""Domain Entities and Agent Output Schemas.

This module contains the core domain models representing the output of various
AI agents (Analyzer, Profiler, Logician, etc.) and the structure of the
audit report components.
"""

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# --- Base Schema ---


class Metadata(BaseModel):
    """Metadata for execution tracking.

    Attributes:
        luontiaika (str): Timestamp of creation (ISO 8601).
        agentti (str): Name of the agent producing this result.
        vaihe (Union[float, int]): Step number in the workflow.
        versio (Literal["1.0", "2.0"]): Schema version.
        suoritus_ymparisto (Optional[Literal]): Execution environment context.
    """

    luontiaika: Annotated[str, Field(description="Timestamp of creation (ISO 8601).")]
    agentti: Annotated[str, Field(description="Name of the agent producing this result.")]
    vaihe: Annotated[float | int, Field(description="Step number in the workflow.")]
    versio: Annotated[Literal["1.0", "2.0"], Field(description="Schema version.")] = "2.0"
    suoritus_ymparisto: Annotated[
        Literal["Kriitikkoryhma_External", "Internal"] | None, Field(description="Execution environment context.")
    ] = None

    model_config = ConfigDict(validate_assignment=True)


class BaseJSON(BaseModel):
    """Base class for all JSON output schemas.

    Attributes:
        metadata (Metadata): Execution metadata.
        reasoning_trace (Optional[str]): Chain-of-Thought reasoning.
        metodologinen_loki (str): Log of methods applied.
        edellisen_vaiheen_validointi (str): Previous step validation.
        semanttinen_tarkistussumma (str): Integrity hash.
    """

    metadata: Annotated[Metadata, Field(description="Execution metadata.")]
    reasoning_trace: Annotated[
        str | None, Field(description="Chain-of-Thought: Step-by-step reasoning BEFORE the final conclusion.")
    ] = None
    metodologinen_loki: Annotated[str, Field(description="Log of methods applied during analysis.")]
    edellisen_vaiheen_validointi: Annotated[str, Field(description="Validation result of the previous step's output.")]
    semanttinen_tarkistussumma: Annotated[str, Field(description="Checksum or integrity hash of the content.")]

    model_config = ConfigDict(extra="allow", validate_assignment=True)


# --- Step 1: Guard Agent ---


class SecurityCheck(BaseModel):
    """Result of the safety and PII analysis.

    Attributes:
        uhka_havaittu (bool): True if a security threat was detected.
        adversariaalinen_simulaatio_tulos (str): Explanation of the threat simulation.
        riski_taso (Literal): Assessed risk level.
        anonymisointi_tehty (Optional[bool]): True if PII redaction was performed.
        tietosuoja_raportti (Optional[str]): Report on what PII was removed.
    """

    uhka_havaittu: Annotated[bool, Field(description="True if a security threat was detected.")]
    adversariaalinen_simulaatio_tulos: Annotated[str, Field(description="Explanation of the threat simulation.")]
    riski_taso: Annotated[Literal["MATALA", "KESKITASO", "KORKEA"], Field(description="Assessed risk level.")]
    anonymisointi_tehty: Annotated[bool | None, Field(description="True if PII redaction was performed.")] = False
    tietosuoja_raportti: Annotated[str | None, Field(description="Report on what PII was removed.")] = None

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("uhka_havaittu", mode="before")
    @classmethod
    def parse_uhka_havaittu(cls, v: Any) -> bool:
        if isinstance(v, str):
            if v.upper() in ["EI", "NO", "FALSE"]:
                return False
            if v.upper() in ["KYLLÄ", "YES", "TRUE"]:
                return True
        return v


class TaintedDataContent(BaseModel):
    """Wrapper for file pointers to potential PII-laden content.

    Attributes:
        keskusteluhistoria (Optional[str]): Pointer to history file.
        lopputuote (Optional[str]): Pointer to product file.
        reflektiodokumentti (Optional[str]): Pointer to reflection file.
    """

    keskusteluhistoria: Annotated[
        str | None,
        Field(description="ÄLÄ TULOSTA SISÄLTÖÄ! Käytä VAIN tätä tekstiä: '{{FILE: Keskusteluhistoria.pdf}}'"),
    ] = None
    lopputuote: Annotated[
        str | None, Field(description="ÄLÄ TULOSTA SISÄLTÖÄ! Käytä VAIN tätä tekstiä: '{{FILE: Lopputuote.pdf}}'")
    ] = None
    reflektiodokumentti: Annotated[
        str | None,
        Field(description="ÄLÄ TULOSTA SISÄLTÖÄ! Käytä VAIN tätä tekstiä: '{{FILE: Reflektiodokumentti.pdf}}'"),
    ] = None

    model_config = ConfigDict(validate_assignment=True)


class SafeDataContent(BaseModel):
    keskusteluhistoria: Annotated[str | None, Field(description="Sanitized history.")] = None
    lopputuote: Annotated[str | None, Field(description="Sanitized product.")] = None
    reflektiodokumentti: Annotated[str | None, Field(description="Sanitized reflection.")] = None

    model_config = ConfigDict(validate_assignment=True)


class TaintedData(BaseJSON):
    """Full output schema for the Guard Agent.

    Attributes:
        data (TaintedDataContent): Pointer to source files.
        security_check (SecurityCheck): Results of security analysis.
        safe_data (Optional[SafeDataContent]): Optional payload of sanitized text.
    """

    data: Annotated[TaintedDataContent, Field(description="Pointer to source files.")]
    security_check: Annotated[SecurityCheck, Field(description="Results of security analysis.")]
    safe_data: Annotated[SafeDataContent | None, Field(description="Optional payload of sanitized text.")] = None


# --- Step 2: Analyst Agent ---


class Hypoteesi(BaseModel):
    """A research hypothesis formulated by the Analyst.

    Attributes:
        id (str): Unique ID for the hypothesis.
        vaite_teksti (str): The hypothesis claim text.
        loytyyko_todisteita (bool): Whether evidence was found.
        hakusana_ehdotus (Optional[str]): Suggested Google search query.
    """

    id: Annotated[str, Field(description="Unique ID for the hypothesis.")]
    vaite_teksti: Annotated[str, Field(description="The hypothesis claim text.")]
    loytyyko_todisteita: Annotated[bool, Field(description="Whether evidence was found.")]
    hakusana_ehdotus: Annotated[str | None, Field(description="Suggested Google search query.")] = None

    model_config = ConfigDict(validate_assignment=True)


class RagTodiste(BaseModel):
    viittaa_hypoteesiin_id: Annotated[
        str | list[str], Field(description="ID(s) of the hypothesis this evidence supports.")
    ]
    perusteet: Annotated[str, Field(description="Reasoning why this evidence is relevant.")]
    konteksti_segmentti: Annotated[str, Field(description="The concise text excerpt (quote).")]
    relevanssi_score: Annotated[int, Field(ge=1, le=100, description="Relevance score (1-100).")]

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("viittaa_hypoteesiin_id", mode="before")
    @classmethod
    def parse_viittaa_hypoteesiin_id(cls, v: Any) -> str | list[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json

                try:
                    return json.loads(v.replace("'", '"'))
                except Exception:
                    return v
        return v

    @field_validator("konteksti_segmentti", mode="before")
    @classmethod
    def parse_konteksti_segmentti(cls, v: Any) -> str:
        if isinstance(v, dict):
            for key in ["text", "content", "segment", "history", "lopputuote", "reflektio"]:
                if key in v and isinstance(v[key], str):
                    return v[key]
            import json

            return json.dumps(v, ensure_ascii=False)
        return v

    @field_validator("relevanssi_score", mode="before")
    @classmethod
    def parse_relevanssi_score(cls, v: Any) -> int:
        if isinstance(v, float):
            return int(round(v))
        if isinstance(v, str):
            try:
                return int(float(v))
            except ValueError:
                return 1
        return v


class TodistusKartta(BaseJSON):
    """Output schema for the Analyst Agent.

    Attributes:
        hypoteesit (list[Hypoteesi]): List of formulated hypotheses.
        rag_todisteet (list[RagTodiste]): Evidence collected from RAG.
    """

    hypoteesit: Annotated[list[Hypoteesi], Field(description="List of formulated hypotheses.")]
    rag_todisteet: Annotated[list[RagTodiste], Field(description="Evidence collected from RAG.")]

    @field_validator("hypoteesit", mode="before")
    @classmethod
    def parse_hypoteesit(cls, v: Any) -> list[Hypoteesi]:
        if isinstance(v, list):
            parsed_list = []
            for item in v:
                if isinstance(item, str):
                    import json

                    try:
                        loaded = json.loads(item)
                        if isinstance(loaded, dict):
                            parsed_list.append(loaded)
                            continue
                    except json.JSONDecodeError:
                        pass
                    parsed_list.append({"id": "GENERATED_ID", "vaite_teksti": item, "loytyyko_todisteita": False})
                else:
                    parsed_list.append(item)
            return parsed_list
        return v


# --- Step 2.5: Profiler Agent ---


class StructuredBias(BaseModel):
    nimi: Annotated[str, Field(description="Name of the cognitive bias")]
    selitys: Annotated[str, Field(description="Explanation of how this bias appears in the text")]

    model_config = ConfigDict(validate_assignment=True)


class TextMetrics(BaseModel):
    word_count: Annotated[int, Field(description="Total number of words")]
    sentence_count: Annotated[int, Field(description="Total number of sentences")]
    avg_sentence_length: Annotated[float, Field(description="Average words per sentence")]
    lexical_diversity: Annotated[float, Field(description="Unique words divided by total words (0-1)")]
    capitalization_ratio: Annotated[float, Field(description="Ratio of uppercase letters to total letters")]

    model_config = ConfigDict(validate_assignment=True)


class ProfilerAnalysis(BaseJSON):
    """Output schema for the Profiler Agent.

    Attributes:
        intentio_analyysi (str): Analysis of intent.
        tunnetila_ja_savy (str): Tone and sentiment.
        tunnistetut_vinoumat (list[StructuredBias]): List of biases.
        psykologinen_profiili (str): Psychological profile.
        manipulaatio_yritykset (str): Manipulation attempts.
        teksti_metriikka (Optional[TextMetrics]): Objective metrics.
    """

    intentio_analyysi: Annotated[str, Field(description="Analysis of intent.")]
    tunnetila_ja_savy: Annotated[str, Field(description="Tone and sentiment.")]
    tunnistetut_vinoumat: Annotated[list[StructuredBias], Field(description="List of biases.")]
    psykologinen_profiili: Annotated[str, Field(description="Psychological profile.")]
    manipulaatio_yritykset: Annotated[str, Field(description="Manipulation attempts.")]
    teksti_metriikka: Annotated[TextMetrics | None, Field(description="Objective metrics.")] = None


# --- Step 3: Logician Agent ---


class ToulminKomponentti(BaseModel):
    """Component of the Toulmin Argumentation Model.

    Attributes:
        vaite_id (str): Reference ID.
        claim (str): The conclusion.
        data (str): The evidence.
        warrant (str): The logical bridge.
        backing (str): Support for the warrant.
    """

    vaite_id: Annotated[str, Field(description="Reference ID.")]
    claim: Annotated[str, Field(description="The conclusion.")]
    data: Annotated[str, Field(description="The evidence.")]
    warrant: Annotated[str, Field(description="The logical bridge.")]
    backing: Annotated[str, Field(description="Support for the warrant.")]

    model_config = ConfigDict(validate_assignment=True)


class KognitiivinenTaso(BaseModel):
    bloom_taso: Annotated[str, Field(description="Bloom's Taxonomy Level.")]
    strateginen_syvyys: Annotated[str, Field(description="Strategic depth analysis.")]

    model_config = ConfigDict(validate_assignment=True)


class WaltonSkeema(BaseModel):
    tunnistettu_skeema: Annotated[str, Field(description="Identified Argumentation Scheme.")]
    kriittiset_kysymykset: Annotated[list[str], Field(description="Critical Questions posed.")]

    model_config = ConfigDict(validate_assignment=True)


class ArgumentaatioAnalyysi(BaseJSON):
    """Output schema for the Logician Agent.

    Attributes:
        toulmin_analyysi (list[ToulminKomponentti]): Toulmin analysis breakdown.
        kognitiivinen_taso (KognitiivinenTaso): Cognitive level assessment.
        walton_skeema (WaltonSkeema): Argumentation scheme analysis.
    """

    toulmin_analyysi: Annotated[list[ToulminKomponentti], Field(description="Toulmin analysis breakdown.")]
    kognitiivinen_taso: Annotated[KognitiivinenTaso, Field(description="Cognitive level assessment.")]
    walton_skeema: Annotated[WaltonSkeema, Field(description="Argumentation scheme analysis.")]


# --- Step 4: Logical Falsifier ---


class WaltonStressitesti(BaseModel):
    kysymys: Annotated[str, Field(description="The critical question asked.")]
    kestiko_todistusaineisto: Annotated[bool, Field(description="Did the evidence hold up?")]
    havainto: Annotated[str, Field(description="Observation notes.")]

    model_config = ConfigDict(validate_assignment=True)


class PaattelyketjunUskollisuus(BaseModel):
    onko_post_hoc_rationalisointia: Annotated[bool, Field(description="True if post-hoc rationalization detected.")]
    perustelu: Annotated[str, Field(description="Reasoning.")]
    uskollisuus_score: Annotated[Literal["KORKEA", "EPÄVARMA", "HEIKKO"], Field(description="Fidelity score.")]

    model_config = ConfigDict(validate_assignment=True)


class LogiikkaAuditointi(BaseJSON):
    """Output schema for the Falsifier Agent.

    Attributes:
        walton_stressitesti_loydokset (list[WaltonStressitesti]): Stress test results.
        paattelyketjun_uskollisuus_auditointi (PaattelyketjunUskollisuus): Fidelity audit.
    """

    walton_stressitesti_loydokset: Annotated[list[WaltonStressitesti], Field(description="Stress test results.")]
    paattelyketjun_uskollisuus_auditointi: Annotated[PaattelyketjunUskollisuus, Field(description="Fidelity audit.")]


# --- Step 5: Factual & Ethical Overseer ---


class FaktantarkistusRFI(BaseModel):
    vaite: Annotated[str, Field(description="Claim to check.")]
    verifiointi_tulos: Annotated[Literal["Vahvistettu", "Kumottu", "Ei voitu vahvistaa"], Field(description="Result.")]
    lahde_tai_paattely: Annotated[str, Field(description="Source or reasoning.")]

    model_config = ConfigDict(validate_assignment=True)


class EettinenHavainto(BaseModel):
    tyyppi: Annotated[
        Literal["Syrjintä", "Haitallinen sisältö", "Plagiointi", "Ei havaittu"], Field(description="Type of issue.")
    ]
    vakavuus: Annotated[Literal["Kriittinen", "Varoitus", "N/A"], Field(description="Severity.")]
    kuvaus: Annotated[str, Field(description="Description.")]

    model_config = ConfigDict(validate_assignment=True)


class EtiikkaJaFakta(BaseJSON):
    """Output schema for the Overseer Agent.

    Attributes:
        faktantarkistus_rfi (list[FaktantarkistusRFI]): Fact check report.
        eettiset_havainnot (list[EettinenHavainto]): Ethical audit report.
    """

    faktantarkistus_rfi: Annotated[
        list[FaktantarkistusRFI], Field(default_factory=list, description="Fact check report.")
    ]
    eettiset_havainnot: Annotated[
        list[EettinenHavainto], Field(default_factory=list, description="Ethical audit report.")
    ]


# --- Step 6: Causal Analyst ---


class KausaalinenAuditointiData(BaseModel):
    aikajana_validi: Annotated[bool, Field(description="Is the timeline valid?")]
    havainnot: Annotated[str, Field(description="General observations.")]

    model_config = ConfigDict(validate_assignment=True)


class KontrafaktuaalinenTesti(BaseModel):
    skenaario_A_toteutunut: Annotated[str, Field(description="Actual scenario.")]
    skenaario_B_simulaatio: Annotated[str, Field(description="Counterfactual simulation.")]
    uskottavuus_arvio: Annotated[str, Field(description="Plausibility assessment.")]

    model_config = ConfigDict(validate_assignment=True)


class KausaalinenAuditointi(BaseJSON):
    """Output schema for the Causal Agent.

    Attributes:
        kausaalinen_auditointi (KausaalinenAuditointiData): Causal audit data.
        kontrafaktuaalinen_testi (KontrafaktuaalinenTesti): Counterfactual test.
        abduktiivinen_paatelma (Literal): Abductive conclusion.
    """

    kausaalinen_auditointi: Annotated[KausaalinenAuditointiData, Field(description="Causal audit data.")]
    kontrafaktuaalinen_testi: Annotated[KontrafaktuaalinenTesti, Field(description="Counterfactual test.")]
    abduktiivinen_paatelma: Annotated[
        Literal["Aito Oivallus", "Post-Hoc Rationalisointi", "Epävarma"], Field(description="Abductive conclusion.")
    ]


# --- Step 7: Performativity Detector ---


class PerformatiivisuusHeuristiikka(BaseModel):
    heuristiikka: Annotated[str, Field(description="Heuristic name.")]
    lippu_nostettu: Annotated[bool, Field(description="Flag raised?")]
    kuvaus: Annotated[str, Field(description="Description.")]

    model_config = ConfigDict(validate_assignment=True)


class PreMortemAnalyysi(BaseModel):
    suoritettu: Annotated[bool, Field(description="Was Pre-Mortem performed?")]
    hiljaiset_signaalit: Annotated[list[str], Field(description="Detected weak signals.")]

    model_config = ConfigDict(validate_assignment=True)


class PerformatiivisuusAuditointi(BaseJSON):
    """Output schema for the Performativity Detector.

    Attributes:
        performatiivisuus_heuristiikat (list[PerformatiivisuusHeuristiikka]): Heuristics check.
        pre_mortem_analyysi (PreMortemAnalyysi): Pre-Mortem analysis.
        yleisarvio_aitoudesta (Literal): Overall authenticity assessment.
    """

    performatiivisuus_heuristiikat: Annotated[
        list[PerformatiivisuusHeuristiikka], Field(description="Heuristics check.")
    ]
    pre_mortem_analyysi: Annotated[PreMortemAnalyysi, Field(description="Pre-Mortem analysis.")]
    yleisarvio_aitoudesta: Annotated[
        Literal["Orgaaninen", "Performatiivinen", "Epäilyttävä"], Field(description="Overall authenticity assessment.")
    ]


# --- Step 8: Judge Agent ---


class KonfliktinRatkaisu(BaseModel):
    konflikti: Annotated[str, Field(description="Description of conflict.")]
    ratkaisu_malli: Annotated[str, Field(description="Resolution model applied.")]
    perustelu: Annotated[str, Field(description="Justification.")]

    model_config = ConfigDict(validate_assignment=True)


class MestaruusPoikkeama(BaseModel):
    tunnistettu: Annotated[bool, Field(description="Is anomaly detected?")]
    perustelu: Annotated[str, Field(description="Reasoning.")]

    model_config = ConfigDict(validate_assignment=True)


class AitousEpaily(BaseModel):
    automaattinen_lippu: Annotated[bool, Field(description="Automatic flag?")]
    viesti_hitl_lle: Annotated[str, Field(alias="viesti_hitl:lle", description="Message for human reviewer.")]

    model_config = ConfigDict(validate_assignment=True)


class PisteetKriteeri(BaseModel):
    arvosana: Annotated[int | float, Field(description="Grade (typically 1-4, but allows dynamic scales).")]
    perustelu: Annotated[str, Field(description="Justification.")]

    model_config = ConfigDict(validate_assignment=True)


class Pisteet(BaseModel):
    analyysi: Annotated[PisteetKriteeri | None, Field(description="Score for Analysis.")] = None
    arviointi: Annotated[PisteetKriteeri | None, Field(description="Score for Evaluation.")] = None
    synteesi: Annotated[PisteetKriteeri | None, Field(description="Score for Synthesis.")] = None

    model_config = ConfigDict(extra="allow", validate_assignment=True)


class TuomioJaPisteet(BaseJSON):
    """Output schema for the Judge Agent (Standard & Cognitive).

    Attributes:
        konfliktin_ratkaisut (list[KonfliktinRatkaisu]): Conflict resolutions.
        mestaruus_poikkeama (MestaruusPoikkeama): Mastery deviation check.
        aitous_epaily (AitousEpaily): Authenticity suspicion.
        pisteet (Pisteet): Scoring breakdown.
        kriittiset_havainnot_yhteenveto (list[str]): Critical observations summary.
        matrix_id (Optional[str]): Matrix ID used (injected).
        scale_min (Optional[int]): Minimum scale score.
        scale_max (Optional[int]): Maximum scale score.
    """

    konfliktin_ratkaisut: Annotated[list[KonfliktinRatkaisu], Field(description="Conflict resolutions.")]
    mestaruus_poikkeama: Annotated[MestaruusPoikkeama, Field(description="Mastery deviation check.")]
    aitous_epaily: Annotated[AitousEpaily, Field(description="Authenticity suspicion.")]
    pisteet: Annotated[Pisteet, Field(description="Scoring breakdown.")]
    kriittiset_havainnot_yhteenveto: Annotated[list[str], Field(description="Critical observations summary.")]
    # Back-ported fields for Dynamic Matrix visibility in legacy views
    matrix_id: Annotated[str | None, Field(default=None, description="Matrix ID used (injected).")]
    scale_min: Annotated[int | None, Field(default=None, description="Minimum scale score.")]
    scale_max: Annotated[int | None, Field(default=None, description="Maximum scale score.")]


# --- Step 8a: Archivist Agent ---


class CaseLawContext(BaseJSON):
    """Output schema for the Archivist Agent (Step 8a).

    Attributes:
        linjakkuus_analyysi (str): Alignment analysis.
        poikkeamat_linjasta (str): Deviations.
        suositus_tuomarille (str): Recommendation to judge.
        viitatut_ennakkotapaukset (list[str]): Referenced cases.
    """

    linjakkuus_analyysi: Annotated[str, Field(description="Alignment analysis.")]
    poikkeamat_linjasta: Annotated[str, Field(description="Deviations.")]
    suositus_tuomarille: Annotated[str, Field(description="Recommendation to judge.")]
    viitatut_ennakkotapaukset: Annotated[list[str], Field(description="Referenced cases.")]


# --- Step 8c: Coach Agent ---


class ActionItem(BaseModel):
    otsikko: Annotated[str, Field(description="Action title.")]
    kuvaus: Annotated[str, Field(description="Description.")]
    resurssit: Annotated[list[str], Field(default_factory=list, description="URLs or Book refs")]

    model_config = ConfigDict(validate_assignment=True)


class ActionGroup(BaseModel):
    kategoria: Annotated[str, Field(description="Category header (e.g. 'Logic', 'Structure')")]
    kohdat: Annotated[list[ActionItem], Field(description="Items in this category")]

    model_config = ConfigDict(validate_assignment=True)


class CoachingPlan(BaseJSON):
    """Output schema for the Coach Agent (Step 8c).

    Attributes:
        kannustava_palaute (str): Positive feedback.
        kehityskohteet_konkreettisesti (list[ActionGroup]): Concrete steps grouped by category.
        lopputuloksen_kehitysehdotukset (list[str]): Concrete suggestions to improve the final product.
        lahdeluettelo (list[str]): Bibliography references used in this plan.
    """

    kannustava_palaute: Annotated[str, Field(description="Positive feedback.")]
    kehityskohteet_konkreettisesti: Annotated[
        list[ActionGroup], Field(description="Concrete steps grouped by category")
    ]
    lopputuloksen_kehitysehdotukset: Annotated[
        list[str], Field(description="Concrete suggestions to improve the final product")
    ]
    lahdeluettelo: Annotated[
        list[str], Field(default_factory=list, description="Bibliography references used in this plan")
    ]


# --- Step 9: XAI Reporter ---


class XAIReport(BaseJSON):
    """Output schema for the XAI Reporter Agent (Step 9).

    Attributes:
        executive_summary (str): High-level summary.
        analysis_strengths (str): Strengths identified.
        analysis_weaknesses (str): Weaknesses identified.
        analysis_opportunities (str): Opportunities identified.
        analysis_recommendations (str): Recommendations.
        final_verdict (str): Final conclusion.
        confidence_score (float): Confidence score (0.0-1.0).
        xai_report_formatted (Optional[str]): Markdown formatted report.
    """

    executive_summary: Annotated[str, Field(description="High-level summary.")]
    analysis_strengths: Annotated[str, Field(description="Strengths identified.")]
    analysis_weaknesses: Annotated[str, Field(description="Weaknesses identified.")]
    analysis_opportunities: Annotated[str, Field(description="Opportunities identified.")]
    analysis_recommendations: Annotated[str, Field(description="Recommendations.")]
    final_verdict: Annotated[str, Field(description="Final conclusion.")]
    confidence_score: Annotated[float, Field(description="Confidence score (0.0-1.0).")]
    xai_report_formatted: Annotated[str | None, Field(description="Markdown formatted report.")] = None
    # comparison_data removed from schema to avoid LLM validation errors (handled dynamically)

    model_config = ConfigDict(extra="allow", validate_assignment=True)


# --- Step 10: Interaction Analyst Agent ---


class InteractionAnalysis(BaseJSON):
    """Output schema for the Interaction Analyst (Step 10).

    Attributes:
        tunnistetut_strategiat (list[str]): Identified strategies.
        ohjausliikkeet (int): Control moves count.
        driver_classification (Literal): Driver profile classification.
        input_control_ratio (Optional[float]): Control ratio.
    """

    tunnistetut_strategiat: Annotated[list[str], Field(description="Identified strategies.")]
    ohjausliikkeet: Annotated[int, Field(description="Control moves count.")]
    driver_classification: Annotated[
        Literal["Matkustaja", "Kartanlukija", "Kuski", "Arkkitehti"],
        Field(description="Driver profile classification."),
    ]
    input_control_ratio: Annotated[float | None, Field(description="Control ratio.")] = None


# --- Step 5 (Parallel): Panel Agent ---
# Defined last because it depends on almost everything else


class PanelAudit(BaseJSON):
    """Consolidated Output schema for the Panel Agent (Parallel Step 5).

    Attributes:
        logiikka_auditointi (ArgumentaatioAnalyysi): Logic audit result.
        falsifiointi_auditointi (LogiikkaAuditointi): Falsification audit result.
        kausaalinen_auditointi (KausaalinenAuditointi): Causal audit result.
        performatiivisuus_auditointi (PerformatiivisuusAuditointi): Performativity audit result.
        etiikka_ja_fakta (EtiikkaJaFakta): Ethics audit result.
    """

    logiikka_auditointi: Annotated[ArgumentaatioAnalyysi, Field(description="Logic audit result.")]
    falsifiointi_auditointi: Annotated[LogiikkaAuditointi, Field(description="Falsification audit result.")]
    kausaalinen_auditointi: Annotated[KausaalinenAuditointi, Field(description="Causal audit result.")]
    performatiivisuus_auditointi: Annotated[
        PerformatiivisuusAuditointi, Field(description="Performativity audit result.")
    ]
    etiikka_ja_fakta: Annotated[EtiikkaJaFakta, Field(description="Ethics audit result.")]


# --- DYNAMIC EVALUATION SYSTEM DOIMAIN MODELS ---


class EvaluationCriterion(BaseModel):
    """Defines a single dimension of evaluation (e.g., 'Analysis')."""

    id: Annotated[str, Field(description="Unique key for the criterion.")]
    label: Annotated[str, Field(description="Human readable label.")]
    instruction: Annotated[str, Field(description="Prompt instruction for the LLM.")]
    anchors: Annotated[dict[str, str], Field(description="Scoring anchors (e.g., {'1': 'Bad', '4': 'Good'}).")]

    model_config = ConfigDict(validate_assignment=True)


class EvaluationMatrixConfig(BaseModel):
    """Configuration for a dynamic evaluation matrix."""

    name: Annotated[str, Field(description="Name of the matrix.")]
    description: Annotated[str, Field(description="Description of purpose.")]
    scale: Annotated[dict[str, int], Field(description="Min and Max scale.")]
    role_description: Annotated[str | None, Field(description="Optional role persona.")] = None
    criteria: Annotated[list[EvaluationCriterion], Field(description="List of criteria.")]

    model_config = ConfigDict(validate_assignment=True)


class DimensionResultItem(BaseModel):
    """Result for a single dimension."""

    dimension_id: Annotated[str, Field(description="ID of the dimension (e.g., 'analysis').")]
    score: Annotated[int | float, Field(description="Numerical score.")]
    reasoning: Annotated[str, Field(description="Justification for the score.")]

    model_config = ConfigDict(validate_assignment=True)


class EvaluationResult(BaseJSON):  # Inherits metadata from BaseJSON
    """Result of a dynamic evaluation.

    Attributes:
        matrix_id (str): ID of the matrix used.
        scale_min (int): Minimum score of the scale (default 1).
        scale_max (int): Maximum score of the scale (default 5).
        total_score (Union[int, float]): Calculated total/average score.
        dimensions (list[DimensionResultItem]): Breakdown by dimension.
        critical_findings (list[str]): Critical observations.
    """

    matrix_id: Annotated[str, Field(description="ID of the matrix used.")]
    scale_min: Annotated[int, Field(default=1, description="Minimum score of the scale.")]
    scale_max: Annotated[int, Field(default=5, description="Maximum score of the scale.")]
    total_score: Annotated[int | float, Field(description="Calculated total/average score.")]
    dimensions: Annotated[list[DimensionResultItem], Field(description="Breakdown by dimension.")]
    critical_findings: Annotated[list[str], Field(default_factory=list, description="Critical observations.")]


# --- USAGE TRACKING ---


class UsageRecord(BaseModel):
    """Immutable record of LLM token consumption and cost.

    Aligned with LiteLLM response metadata.
    """

    id: Annotated[str, Field(description="Unique UUID for the usage record.")]
    org_id: Annotated[str, Field(description="Organization ID context.")]
    user_id: Annotated[str, Field(description="User ID who initiated the request.")]
    model: Annotated[str, Field(description="Model name used (e.g. 'gemini-1.5-pro').")]
    input_tokens: Annotated[int, Field(description="Number of input tokens.")]
    output_tokens: Annotated[int, Field(description="Number of generated tokens.")]
    cost_usd: Annotated[float, Field(description="Calculated cost in USD (from LiteLLM).")]
    timestamp: Annotated[str, Field(description="ISO 8601 timestamp of the event.")]

    model_config = ConfigDict(frozen=True, validate_assignment=True)
