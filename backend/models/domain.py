"""Domain Entities and Agent Output Schemas.

This module contains the core domain models representing the output of various
AI agents (Analyzer, Profiler, Logician, etc.) and the structure of the
audit report components.
"""

from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)

from backend.hooks.security import check_banned_phrases

# --- Base Schema ---


class Metadata(BaseModel):
    """Metadata for execution tracking.

    Attributes:
        luontiaika (datetime): Timestamp of creation (ISO 8601).
        agentti (str): Name of the agent producing this result.
        vaihe (Union[float, int]): Step number in the workflow.
        versio (Literal["1.0", "2.0"]): Schema version.
        suoritus_ymparisto (Optional[Literal]): Execution environment context.
    """

    luontiaika: Annotated[datetime, Field(description="Timestamp of creation (ISO 8601).")]
    agentti: Annotated[str, Field(description="Name of the agent producing this result.")]
    vaihe: Annotated[float | int, Field(description="Step number in the workflow.")]
    versio: Annotated[Literal["1.0", "2.0"], Field(description="Schema version.")] = "2.0"
    suoritus_ymparisto: Annotated[
        Literal["Kriitikkoryhma_External", "Internal", "VIRTUAL_ENCLAVE"] | None,
        Field(description="Execution environment context."),
    ] = None

    model_config = ConfigDict(extra="allow", validate_assignment=True)


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


def validate_guard_input(v: str, info: ValidationInfo) -> str:
    """Validator to check for banned phrases using context."""
    if not v:
        return v

    # Context is passed from the Agent via model_validate(..., context={...})
    if info.context and "banned_phrases" in info.context:
        banned = info.context["banned_phrases"]
        detected = check_banned_phrases(v, banned)
        if detected:
            # We use a specific Error Code prefix for handling upstream
            raise ValueError(f"SECURITY_BANNED_PHRASE_DETECTED: {detected}")
    return v


class GuardInput(BaseModel):
    """Input schema for Guard Agent Validation."""

    history_text: Annotated[str, AfterValidator(validate_guard_input)]
    product_text: Annotated[str, AfterValidator(validate_guard_input)]
    reflection_text: Annotated[str | None, AfterValidator(validate_guard_input)] = None

    model_config = ConfigDict(extra="ignore")


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
        """Validate uhka_havaittu boolean."""
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
        str | None,
        Field(description="ÄLÄ TULOSTA SISÄLTÖÄ! Käytä VAIN tätä tekstiä: '{{FILE: Lopputuote.pdf}}'"),
    ] = None
    reflektiodokumentti: Annotated[
        str | None,
        Field(description="ÄLÄ TULOSTA SISÄLTÖÄ! Käytä VAIN tätä tekstiä: '{{FILE: Reflektiodokumentti.pdf}}'"),
    ] = None

    model_config = ConfigDict(validate_assignment=True)


class SafeDataContent(BaseModel):
    """Sanitized data content (PII removed)."""

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
    """Evidence retrieved via RAG."""

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
        """Validate hypothesis ID reference."""
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
        """Validate context segment."""
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
        """Validate relevance score."""
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
        """Validate list of hypotheses."""
        if isinstance(v, list):
            parsed_list = []
            for item in v:
                if isinstance(item, str):
                    import json

                    try:
                        loaded = json.loads(item)
                        if isinstance(loaded, dict):
                            parsed_list.append(Hypoteesi(**loaded))
                            continue
                    except (json.JSONDecodeError, ValueError, TypeError):
                        pass
                    parsed_list.append(Hypoteesi(id="GENERATED_ID", vaite_teksti=item, loytyyko_todisteita=False))
                elif isinstance(item, dict):
                    parsed_list.append(Hypoteesi(**item))
                else:
                    parsed_list.append(item)
            return parsed_list
        return v


# --- Step 2.5: Profiler Agent ---


class StructuredBias(BaseModel):
    """Structured representation of a cognitive bias."""

    nimi: Annotated[str, Field(description="Name of the cognitive bias")]
    selitys: Annotated[str, Field(description="Explanation of how this bias appears in the text")]

    model_config = ConfigDict(validate_assignment=True)


class TextMetrics(BaseModel):
    """Objective text metrics."""

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
    """Assessment of cognitive depth."""

    bloom_taso: Annotated[str, Field(description="Bloom's Taxonomy Level.")]
    strateginen_syvyys: Annotated[str, Field(description="Strategic depth analysis.")]

    model_config = ConfigDict(validate_assignment=True)


class WaltonSkeema(BaseModel):
    """Walton's Argumentation Scheme."""

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
    """Stress test using Walton's critical questions."""

    kysymys: Annotated[str, Field(description="The critical question asked.")]
    kestiko_todistusaineisto: Annotated[bool, Field(description="Did the evidence hold up?")]
    havainto: Annotated[str, Field(description="Observation notes.")]

    model_config = ConfigDict(validate_assignment=True)


class PaattelyketjunUskollisuus(BaseModel):
    """Audit of the chain of reasoning fidelity."""

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
    """Request for Information (Fact Check)."""

    vaite: Annotated[str, Field(description="Claim to check.")]
    verifiointi_tulos: Annotated[Literal["Vahvistettu", "Kumottu", "Ei voitu vahvistaa"], Field(description="Result.")]
    lahde_tai_paattely: Annotated[str, Field(description="Source or reasoning.")]

    model_config = ConfigDict(validate_assignment=True)


class EettinenHavainto(BaseModel):
    """Ethical Observation."""

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
    """Data from Causal Audit."""

    aikajana_validi: Annotated[bool, Field(description="Is the timeline valid?")]
    havainnot: Annotated[str, Field(description="General observations.")]

    model_config = ConfigDict(validate_assignment=True)


class KontrafaktuaalinenTesti(BaseModel):
    """Counterfactual Simulation Test."""

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
    """Heuristic check for performativity."""

    heuristiikka: Annotated[str, Field(description="Heuristic name.")]
    lippu_nostettu: Annotated[bool, Field(description="Flag raised?")]
    kuvaus: Annotated[str, Field(description="Description.")]

    model_config = ConfigDict(validate_assignment=True)


class PreMortemAnalyysi(BaseModel):
    """Pre-Mortem Analysis results."""

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


# --- Step 8a: Archivist Agent ---


class ArchivistOutput(BaseJSON):
    """Output schema for the Archivist Agent (Step 8a) - Standardized.

    Attributes:
        analysis (str): Analysis of alignment.
        compliance_score (int): Compliance score (0-100).
        recommendations (list[str]): List of recommendations.
    """

    analysis: Annotated[str, Field(description="Analysis of alignment.")]
    compliance_score: Annotated[int, Field(description="Compliance score (0-100).")]
    recommendations: Annotated[list[str], Field(description="List of recommendations.")]


# --- Step 8c: Coach Agent ---


class ActionItem(BaseModel):
    """Concrete action item for improvement."""

    otsikko: Annotated[str, Field(description="Action title.")]
    kuvaus: Annotated[str, Field(description="Description.")]
    resurssit: Annotated[list[str], Field(default_factory=list, description="URLs or Book refs")]

    model_config = ConfigDict(validate_assignment=True)


class ActionGroup(BaseModel):
    """Group of action items categories."""

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
    # V2 Support (Cognitive Quorum 2.0)
    analyysi_haasteista: Annotated[str | None, Field(description="Analysis of challenges (V2).")] = None
    toimenpiteet: Annotated[list[str] | None, Field(description="List of actions (V2).")] = None
    motivaatio: Annotated[str | None, Field(description="Motivation for improvement (V2).")] = None


# --- Step 9: XAI Reporter ---


class DimensionResultItem(BaseModel):
    """Result for a single dimension."""

    dimension_id: Annotated[str, Field(description="ID of the dimension (e.g., 'analysis').")]
    score: Annotated[int | float, Field(description="Numerical score.")]
    reasoning: Annotated[str, Field(description="Justification for the score.")]

    # STRICT: Do not allow extra fields like 'label' or 'name'.
    # Force LLM to map correctly to 'dimension_id'.
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class ScoreCardItem(BaseModel):
    """Summary of a single judgment step."""

    agent_name: Annotated[str, Field(description="Name of the judge (e.g. 'Standard Judge').")]
    total_score: Annotated[float, Field(description="Total score (0-5).")]
    max_score: Annotated[int, Field(description="Max scale.")]
    verdict: Annotated[str, Field(description="Short verdict or summary.")]
    dimensions: Annotated[list[DimensionResultItem], Field(default_factory=list, description="Radar chart data.")]


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
    comparison_data: Annotated[dict[str, Any] | None, Field(description="Structured comparison data.")] = None
    score_cards: Annotated[
        list[ScoreCardItem], Field(default_factory=list, description="Aggregated scores from all judges.")
    ]

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
    input_control_ratio: Annotated[
        float | None, Field(description="Control ratio (Calculated from imperative_count / total_turn_count).")
    ] = None
    imperative_command_count: Annotated[
        int, Field(default=0, description="Count of imperative commands (e.g. 'Tee', 'Korjaa').")
    ]
    total_turn_count: Annotated[int, Field(default=1, description="Total number of user turns analysed.")]

    @field_validator("input_control_ratio", mode="before")
    @classmethod
    def compute_ratio(cls, v: Any, info: ValidationInfo) -> float | None:
        """Compute ratio if not provided, based on counts.

        Refines 0.0 defaults to None if the classification implies activity,
        avoiding the 'Architect 0%' visual bug.
        """
        values = info.data
        cmd = values.get("imperative_command_count", 0)

        if v is not None and not (v == 0.0 and cmd > 0):
            return v
        total = values.get("total_turn_count", 1)
        role = values.get("driver_classification", "Matkustaja")

        # If no commands detected (0) but Role is high-level, the heuristic failed.
        # Check against active roles (Navigator, Driver, Architect)
        active_roles = ["kartanlukija", "navigator", "kuski", "driver", "arkkitehti", "architect"]
        is_active_role = any(r in role.lower() for r in active_roles)

        if total == 0:
            return None

        ratio = round(cmd / total, 2)

        # If Active Role (Driver) but 0% commands, metric is likely invalid/missing.
        # Return None to show "N/A" instead of misleading "0%".
        if ratio == 0.0 and is_active_role:
            return None

        return ratio


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

    model_config = ConfigDict(
        validate_assignment=True,
        json_schema_extra={
            "properties": {
                "id": {"x-ui-label": "ID"},
                "label": {"x-ui-label": "Label"},
                "instruction": {"x-ui-label": "Instruction", "x-ui-widget": "textarea"},
                "anchors": {"x-ui-label": "Scoring Anchors"},
            }
        },
    )


class EvaluationMatrixConfig(BaseModel):
    """Configuration for a dynamic evaluation matrix."""

    name: Annotated[str, Field(description="Name of the matrix.")]
    description: Annotated[str, Field(description="Description of purpose.")]
    scale: Annotated[dict[str, int], Field(description="Min and Max scale.")]
    role_description: Annotated[str | None, Field(description="Optional role persona.")] = None
    criteria: Annotated[list[EvaluationCriterion], Field(description="List of criteria.")]

    model_config = ConfigDict(
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "Standard Analysis",
                    "description": "Basic analysis matrix.",
                    "scale": {"min": 1, "max": 5},
                    "criteria": [],
                }
            ],
            "properties": {
                "name": {"x-ui-label": "Matrix Name"},
                "description": {"x-ui-label": "Description"},
                "scale": {"x-ui-label": "Scoring Scale"},
                "role_description": {"x-ui-label": "Role Persona"},
                "criteria": {"x-ui-group": "Evaluation Criteria"},
            },
        },
    )


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

    @model_validator(mode="after")
    def validate_scores(self) -> EvaluationResult:
        if self.scale_min >= self.scale_max:
            raise ValueError(f"Invalid scale: min ({self.scale_min}) must be less than max ({self.scale_max})")

        # 1. Validate Total Score
        if not (self.scale_min <= self.total_score <= self.scale_max):
            # Try to fix rounding errors if very close, otherwise raise
            if abs(self.total_score - self.scale_max) < 0.01:
                self.total_score = float(self.scale_max)
            elif abs(self.total_score - self.scale_min) < 0.01:
                self.total_score = float(self.scale_min)
            else:
                raise ValueError(f"Total score {self.total_score} out of bounds [{self.scale_min}, {self.scale_max}]")

        # 2. Validate Dimension Scores
        for dim in self.dimensions:
            if not (self.scale_min <= dim.score <= self.scale_max):
                # Try soft fix
                if abs(dim.score - self.scale_max) < 0.01:
                    dim.score = float(self.scale_max)
                elif abs(dim.score - self.scale_min) < 0.01:
                    dim.score = float(self.scale_min)
                else:
                    raise ValueError(
                        f"Dimension '{dim.dimension_id}' score {dim.score} "
                        f"out of bounds [{self.scale_min}, {self.scale_max}]"
                    )

        return self


# --- Reporting Context Models (Internal) ---


class ReportScore(BaseModel):
    """Normalized score structure for the report context."""

    score: Annotated[int | float | str | None, Field(description="Numerical or text score.")] = None
    reasoning: Annotated[str, Field(description="Explanation.")] = ""

    # V2 Finnish Keys (Standard)
    arvosana: Annotated[int | float | str | None, Field(description="Grade (Finnish key).")] = None
    perustelu: Annotated[str, Field(description="Reasoning (Finnish key).")] = ""

    model_config = ConfigDict(validate_assignment=True, extra="allow")


class ReportContext(BaseModel):
    """The 'Flat File' structure for Jinja2 rendering.

    Replacing the loose dictionary in `hooks/reporting.py`.
    """

    summary: Annotated[str, Field(description="Executive Summary.")]
    critical_findings: Annotated[list[str | dict[str, Any]], Field(default_factory=list)]
    pre_mortem_signals: Annotated[list[str], Field(default_factory=list)]
    hitl_required: Annotated[bool, Field(default=False)]
    ethical_issues: Annotated[list[dict[str, Any]], Field(default_factory=list)]
    audit_questions: Annotated[list[dict[str, Any]], Field(default_factory=list)]
    uncertainty: Annotated[dict[str, Any], Field(default_factory=dict)]
    scores: Annotated[dict[str, ReportScore], Field(default_factory=dict)]
    average_score: Annotated[float, Field(default=0.0, description="Calculated average score.")]
    timestamp: Annotated[str, Field(description="Generation timestamp.")]
    coaching_plan: Annotated[dict[str, Any] | None, Field(default=None)] = None

    # New fields from hooks (Jan 2026)
    penalties_applied: Annotated[
        list[str], Field(default_factory=list, description="List of penalties applied by scoring hook.")
    ]
    score_summary: Annotated[str | None, Field(default=None, description="Full score summary from scoring hook.")]
    input_control_ratio: Annotated[float | None, Field(default=None, description="Human/AI control ratio (0.0-1.0).")]

    # Hook outputs (Jan 2026 - Expanded)
    structural_warnings: Annotated[
        list[str], Field(default_factory=list, description="Validation warnings for short/missing inputs.")
    ]
    archivist_precedents: Annotated[
        str | None, Field(default=None, description="Historical context from past executions.")
    ]
    google_search_results: Annotated[
        list[dict[str, Any]], Field(default_factory=list, description="Fact-checking sources from Google Search.")
    ]

    model_config = ConfigDict(validate_assignment=True)


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
    timestamp: Annotated[datetime, Field(description="ISO 8601 timestamp of the event.")]

    model_config = ConfigDict(frozen=True, validate_assignment=True)


# --- Retrieval & Context ---


class Precedent(BaseModel):
    """Represents a single historical execution precedent."""

    id: str
    date: str
    scores: str
    verdict: str


class ContextData(BaseJSON):
    """Output schema for RetrievalAgent (Simulated or Real)."""

    precedents: Annotated[str, Field(description="Summary text of precedents.")]
    precedent_list: Annotated[
        list[Precedent],
        Field(default_factory=list, description="Structured list of precedents."),
    ]
