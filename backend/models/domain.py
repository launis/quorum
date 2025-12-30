from typing import Literal, Any, List, Dict, Optional, Union, Annotated
from pydantic import BaseModel, Field, field_validator, ConfigDict

# --- Base Schema ---

class Metadata(BaseModel):
    luontiaika: Annotated[str, Field(description="Timestamp of creation (ISO 8601).")]
    agentti: Annotated[str, Field(description="Name of the agent producing this result.")]
    vaihe: Annotated[Union[float, int], Field(description="Step number in the workflow.")]
    versio: Annotated[Literal["1.0", "2.0"], Field(description="Schema version.")] = "2.0"
    suoritus_ymparisto: Annotated[Optional[Literal["Kriitikkoryhma_External", "Internal"]], Field(description="Execution environment context.")] = None

class BaseJSON(BaseModel):
    metadata: Annotated[Metadata, Field(description="Execution metadata.")]
    reasoning_trace: Annotated[Optional[str], Field(description="Chain-of-Thought: Step-by-step reasoning BEFORE the final conclusion.")] = None
    metodologinen_loki: Annotated[str, Field(description="Log of methods applied during analysis.")]
    edellisen_vaiheen_validointi: Annotated[str, Field(description="Validation result of the previous step's output.")]
    semanttinen_tarkistussumma: Annotated[str, Field(description="Checksum or integrity hash of the content.")]

    model_config = ConfigDict(extra='allow')

# --- Step 1: Guard Agent ---

class SecurityCheck(BaseModel):
    uhka_havaittu: Annotated[bool, Field(description="True if a security threat was detected.")]
    adversariaalinen_simulaatio_tulos: Annotated[str, Field(description="Explanation of the threat simulation.")]
    riski_taso: Annotated[Literal["MATALA", "KESKITASO", "KORKEA"], Field(description="Assessed risk level.")]
    anonymisointi_tehty: Annotated[Optional[bool], Field(description="True if PII redaction was performed.")] = False
    tietosuoja_raportti: Annotated[Optional[str], Field(description="Report on what PII was removed.")] = None

    @field_validator('uhka_havaittu', mode='before')
    @classmethod
    def parse_uhka_havaittu(cls, v: Any) -> bool:
        if isinstance(v, str):
            if v.upper() in ['EI', 'NO', 'FALSE']:
                return False
            if v.upper() in ['KYLLÄ', 'YES', 'TRUE']:
                return True
        return v

class TaintedDataContent(BaseModel):
    keskusteluhistoria: Annotated[Optional[str], Field(description="ÄLÄ TULOSTA SISÄLTÖÄ! Käytä VAIN tätä tekstiä: '{{FILE: Keskusteluhistoria.pdf}}'")] = None
    lopputuote: Annotated[Optional[str], Field(description="ÄLÄ TULOSTA SISÄLTÖÄ! Käytä VAIN tätä tekstiä: '{{FILE: Lopputuote.pdf}}'")] = None
    reflektiodokumentti: Annotated[Optional[str], Field(description="ÄLÄ TULOSTA SISÄLTÖÄ! Käytä VAIN tätä tekstiä: '{{FILE: Reflektiodokumentti.pdf}}'")] = None

class SafeDataContent(BaseModel):
    keskusteluhistoria: Annotated[Optional[str], Field(description="Sanitized history.")] = None
    lopputuote: Annotated[Optional[str], Field(description="Sanitized product.")] = None
    reflektiodokumentti: Annotated[Optional[str], Field(description="Sanitized reflection.")] = None

class TaintedData(BaseJSON):
    data: Annotated[TaintedDataContent, Field(description="Pointer to source files.")]
    security_check: Annotated[SecurityCheck, Field(description="Results of security analysis.")]
    safe_data: Annotated[Optional[SafeDataContent], Field(description="Optional payload of sanitized text.")] = None

# --- Step 2: Analyst Agent ---

class Hypoteesi(BaseModel):
    id: Annotated[str, Field(description="Unique ID for the hypothesis.")]
    vaite_teksti: Annotated[str, Field(description="The hypothesis claim text.")]
    loytyyko_todisteita: Annotated[bool, Field(description="Whether evidence was found.")]
    hakusana_ehdotus: Annotated[Optional[str], Field(description="Suggested Google search query.")] = None

class RagTodiste(BaseModel):
    viittaa_hypoteesiin_id: Annotated[Union[str, List[str]], Field(description="ID(s) of the hypothesis this evidence supports.")]
    perusteet: Annotated[str, Field(description="Reasoning why this evidence is relevant.")]
    konteksti_segmentti: Annotated[str, Field(description="The concise text excerpt (quote).")]
    relevanssi_score: Annotated[int, Field(ge=1, le=100, description="Relevance score (1-100).")]

    @field_validator('viittaa_hypoteesiin_id', mode='before')
    @classmethod
    def parse_viittaa_hypoteesiin_id(cls, v: Any) -> Union[str, List[str]]:
        if isinstance(v, str):
            if v.startswith('[') and v.endswith(']'):
                import json
                try:
                    return json.loads(v.replace("'", '"'))
                except:
                    return v
        return v

    @field_validator('konteksti_segmentti', mode='before')
    @classmethod
    def parse_konteksti_segmentti(cls, v: Any) -> str:
        if isinstance(v, dict):
            for key in ['text', 'content', 'segment', 'history', 'lopputuote', 'reflektio']:
                if key in v and isinstance(v[key], str):
                    return v[key]
            import json
            return json.dumps(v, ensure_ascii=False)
        return v

    @field_validator('relevanssi_score', mode='before')
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
    hypoteesit: Annotated[List[Hypoteesi], Field(description="List of formulated hypotheses.")]
    rag_todisteet: Annotated[List[RagTodiste], Field(description="Evidence collected from RAG.")]

    @field_validator('hypoteesit', mode='before')
    @classmethod
    def parse_hypoteesit(cls, v: Any) -> List[Hypoteesi]:
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
                    parsed_list.append({
                        "id": "GENERATED_ID", 
                        "vaite_teksti": item, 
                        "loytyyko_todisteita": False
                    })
                else:
                    parsed_list.append(item)
            return parsed_list
        return v

# --- Step 3: Logician Agent ---

class ToulminKomponentti(BaseModel):
    vaite_id: Annotated[str, Field(description="Reference ID.")]
    claim: Annotated[str, Field(description="The conclusion.")]
    data: Annotated[str, Field(description="The evidence.")]
    warrant: Annotated[str, Field(description="The logical bridge.")]
    backing: Annotated[str, Field(description="Support for the warrant.")]

class KognitiivinenTaso(BaseModel):
    bloom_taso: Annotated[str, Field(description="Bloom's Taxonomy Level.")]
    strateginen_syvyys: Annotated[str, Field(description="Strategic depth analysis.")]

class WaltonSkeema(BaseModel):
    tunnistettu_skeema: Annotated[str, Field(description="Identified Argumentation Scheme.")]
    kriittiset_kysymykset: Annotated[List[str], Field(description="Critical Questions posed.")]

class ArgumentaatioAnalyysi(BaseJSON):
    toulmin_analyysi: Annotated[List[ToulminKomponentti], Field(description="Toulmin analysis breakdown.")]
    kognitiivinen_taso: Annotated[KognitiivinenTaso, Field(description="Cognitive level assessment.")]
    walton_skeema: Annotated[WaltonSkeema, Field(description="Argumentation scheme analysis.")]

# --- Step 4: Logical Falsifier ---

class WaltonStressitesti(BaseModel):
    kysymys: Annotated[str, Field(description="The critical question asked.")]
    kestiko_todistusaineisto: Annotated[bool, Field(description="Did the evidence hold up?")]
    havainto: Annotated[str, Field(description="Observation notes.")]

class PaattelyketjunUskollisuus(BaseModel):
    onko_post_hoc_rationalisointia: Annotated[bool, Field(description="True if post-hoc rationalization detected.")]
    perustelu: Annotated[str, Field(description="Reasoning.")]
    uskollisuus_score: Annotated[Literal["KORKEA", "EPÄVARMA", "HEIKKO"], Field(description="Fidelity score.")]

class LogiikkaAuditointi(BaseJSON):
    walton_stressitesti_loydokset: Annotated[List[WaltonStressitesti], Field(description="Stress test results.")]
    paattelyketjun_uskollisuus_auditointi: Annotated[PaattelyketjunUskollisuus, Field(description="Fidelity audit.")]

# --- Step 5: Factual & Ethical Overseer ---

class FaktantarkistusRFI(BaseModel):
    vaite: Annotated[str, Field(description="Claim to check.")]
    verifiointi_tulos: Annotated[Literal["Vahvistettu", "Kumottu", "Ei voitu vahvistaa"], Field(description="Result.")]
    lahde_tai_paattely: Annotated[str, Field(description="Source or reasoning.")]

class EettinenHavainto(BaseModel):
    tyyppi: Annotated[Literal["Syrjintä", "Haitallinen sisältö", "Plagiointi", "Ei havaittu"], Field(description="Type of issue.")]
    vakavuus: Annotated[Literal["Kriittinen", "Varoitus", "N/A"], Field(description="Severity.")]
    kuvaus: Annotated[str, Field(description="Description.")]

class EtiikkaJaFakta(BaseJSON):
    faktantarkistus_rfi: Annotated[List[FaktantarkistusRFI], Field(default_factory=list, description="Fact check report.")]
    eettiset_havainnot: Annotated[List[EettinenHavainto], Field(default_factory=list, description="Ethical audit report.")]

# --- Step 6: Causal Analyst ---

class KausaalinenAuditointiData(BaseModel):
    aikajana_validi: Annotated[bool, Field(description="Is the timeline valid?")]
    havainnot: Annotated[str, Field(description="General observations.")]

class KontrafaktuaalinenTesti(BaseModel):
    skenaario_A_toteutunut: Annotated[str, Field(description="Actual scenario.")]
    skenaario_B_simulaatio: Annotated[str, Field(description="Counterfactual simulation.")]
    uskottavuus_arvio: Annotated[str, Field(description="Plausibility assessment.")]

class KausaalinenAuditointi(BaseJSON):
    kausaalinen_auditointi: Annotated[KausaalinenAuditointiData, Field(description="Causal audit data.")]
    kontrafaktuaalinen_testi: Annotated[KontrafaktuaalinenTesti, Field(description="Counterfactual test.")]
    abduktiivinen_paatelma: Annotated[Literal["Aito Oivallus", "Post-Hoc Rationalisointi", "Epävarma"], Field(description="Abductive conclusion.")]

# --- Step 7: Performativity Detector ---

class PerformatiivisuusHeuristiikka(BaseModel):
    heuristiikka: Annotated[str, Field(description="Heuristic name.")]
    lippu_nostettu: Annotated[bool, Field(description="Flag raised?")]
    kuvaus: Annotated[str, Field(description="Description.")]

class PreMortemAnalyysi(BaseModel):
    suoritettu: Annotated[bool, Field(description="Was Pre-Mortem performed?")]
    hiljaiset_signaalit: Annotated[List[str], Field(description="Detected weak signals.")]

class PerformatiivisuusAuditointi(BaseJSON):
    performatiivisuus_heuristiikat: Annotated[List[PerformatiivisuusHeuristiikka], Field(description="Heuristics check.")]
    pre_mortem_analyysi: Annotated[PreMortemAnalyysi, Field(description="Pre-Mortem analysis.")]
    yleisarvio_aitoudesta: Annotated[Literal["Orgaaninen", "Performatiivinen", "Epäilyttävä"], Field(description="Overall authenticity assessment.")]

# --- Step 8: Judge Agent ---

class KonfliktinRatkaisu(BaseModel):
    konflikti: Annotated[str, Field(description="Description of conflict.")]
    ratkaisu_malli: Annotated[str, Field(description="Resolution model applied.")]
    perustelu: Annotated[str, Field(description="Justification.")]

class MestaruusPoikkeama(BaseModel):
    tunnistettu: Annotated[bool, Field(description="Is anomaly detected?")]
    perustelu: Annotated[str, Field(description="Reasoning.")]

class AitousEpaily(BaseModel):
    automaattinen_lippu: Annotated[bool, Field(description="Automatic flag?")]
    viesti_hitl_lle: Annotated[str, Field(alias="viesti_hitl:lle", description="Message for human reviewer.")]

class PisteetKriteeri(BaseModel):
    arvosana: Annotated[Union[int, float], Field(description="Grade (typically 1-4, but allows dynamic scales).")]
    perustelu: Annotated[str, Field(description="Justification.")]

class Pisteet(BaseModel):
    analyysi: Annotated[Optional[PisteetKriteeri], Field(description="Score for Analysis.")] = None
    arviointi: Annotated[Optional[PisteetKriteeri], Field(description="Score for Evaluation.")] = None
    synteesi: Annotated[Optional[PisteetKriteeri], Field(description="Score for Synthesis.")] = None

    model_config = ConfigDict(extra='allow')

class TuomioJaPisteet(BaseJSON):
    konfliktin_ratkaisut: Annotated[List[KonfliktinRatkaisu], Field(description="Conflict resolutions.")]
    mestaruus_poikkeama: Annotated[MestaruusPoikkeama, Field(description="Mastery deviation check.")]
    aitous_epaily: Annotated[AitousEpaily, Field(description="Authenticity suspicion.")]
    pisteet: Annotated[Pisteet, Field(description="Scoring breakdown.")]
    kriittiset_havainnot_yhteenveto: Annotated[List[str], Field(description="Critical observations summary.")]
    # Back-ported fields for Dynamic Matrix visibility in legacy views
    matrix_id: Annotated[Optional[str], Field(default=None, description="Matrix ID used (injected).")]
    scale_min: Annotated[Optional[int], Field(default=None, description="Minimum scale score.")]
    scale_max: Annotated[Optional[int], Field(default=None, description="Maximum scale score.")]

# --- DYNAMIC EVALUATION SYSTEM DOIMAIN MODELS ---

class EvaluationCriterion(BaseModel):
    """Defines a single dimension of evaluation (e.g., 'Analysis')."""
    id: Annotated[str, Field(description="Unique key for the criterion.")]
    label: Annotated[str, Field(description="Human readable label.")]
    instruction: Annotated[str, Field(description="Prompt instruction for the LLM.")]
    anchors: Annotated[Dict[str, str], Field(description="Scoring anchors (e.g., {'1': 'Bad', '4': 'Good'}).")]

class EvaluationMatrixConfig(BaseModel):
    """Configuration for a dynamic evaluation matrix."""
    name: Annotated[str, Field(description="Name of the matrix.")]
    description: Annotated[str, Field(description="Description of purpose.")]
    scale: Annotated[Dict[str, int], Field(description="Min and Max scale.")]
    role_description: Annotated[Optional[str], Field(description="Optional role persona.")] = None
    criteria: Annotated[List[EvaluationCriterion], Field(description="List of criteria.")]

class DimensionResultItem(BaseModel):
    """Result for a single dimension."""
    dimension_id: Annotated[str, Field(description="ID of the dimension (e.g., 'analysis').")]
    score: Annotated[Union[int, float], Field(description="Numerical score.")]
    reasoning: Annotated[str, Field(description="Justification for the score.")]
    
class EvaluationResult(BaseJSON):  # Inherits metadata from BaseJSON
    """Result of a dynamic evaluation."""
    matrix_id: Annotated[str, Field(description="ID of the matrix used.")]
    scale_min: Annotated[int, Field(default=1, description="Minimum score of the scale.")]
    scale_max: Annotated[int, Field(default=5, description="Maximum score of the scale.")]
    total_score: Annotated[Union[int, float], Field(description="Calculated total/average score.")]
    dimensions: Annotated[List[DimensionResultItem], Field(description="Breakdown by dimension.")]
    critical_findings: Annotated[List[str], Field(default_factory=list, description="Critical observations.")]

# --- Step 9: XAI Reporter ---

class XAIReport(BaseJSON):
    executive_summary: Annotated[str, Field(description="High-level summary.")]
    analysis_strengths: Annotated[str, Field(description="Strengths identified.")]
    analysis_weaknesses: Annotated[str, Field(description="Weaknesses identified.")]
    analysis_opportunities: Annotated[str, Field(description="Opportunities identified.")]
    analysis_recommendations: Annotated[str, Field(description="Recommendations.")]
    final_verdict: Annotated[str, Field(description="Final conclusion.")]
    confidence_score: Annotated[float, Field(description="Confidence score (0.0-1.0).")]
    xai_report_formatted: Annotated[Optional[str], Field(description="Markdown formatted report.")] = None

# --- Step 2.5: Profiler Agent ---

class StructuredBias(BaseModel):
    nimi: Annotated[str, Field(description="Name of the cognitive bias")]
    selitys: Annotated[str, Field(description="Explanation of how this bias appears in the text")]


class TextMetrics(BaseModel):
    word_count: Annotated[int, Field(description="Total number of words")]
    sentence_count: Annotated[int, Field(description="Total number of sentences")]
    avg_sentence_length: Annotated[float, Field(description="Average words per sentence")]
    lexical_diversity: Annotated[float, Field(description="Unique words divided by total words (0-1)")]
    capitalization_ratio: Annotated[float, Field(description="Ratio of uppercase letters to total letters")]

class ProfilerAnalysis(BaseJSON):
    intentio_analyysi: Annotated[str, Field(description="Analysis of intent.")]
    tunnetila_ja_savy: Annotated[str, Field(description="Tone and sentiment.")]
    tunnistetut_vinoumat: Annotated[List[StructuredBias], Field(description="List of biases.")]
    psykologinen_profiili: Annotated[str, Field(description="Psychological profile.")]
    manipulaatio_yritykset: Annotated[str, Field(description="Manipulation attempts.")]
    teksti_metriikka: Annotated[Optional[TextMetrics], Field(description="Objective metrics.")] = None

# --- Step 5 (Parallel): Panel Agent ---

class PanelAudit(BaseJSON):
    logiikka_auditointi: Annotated[ArgumentaatioAnalyysi, Field(description="Logic audit result.")]
    falsifiointi_auditointi: Annotated[LogiikkaAuditointi, Field(description="Falsification audit result.")]
    kausaalinen_auditointi: Annotated[KausaalinenAuditointi, Field(description="Causal audit result.")]
    performatiivisuus_auditointi: Annotated[PerformatiivisuusAuditointi, Field(description="Performativity audit result.")]
    etiikka_ja_fakta: Annotated[EtiikkaJaFakta, Field(description="Ethics audit result.")]

# --- Step 8a: Archivist Agent ---

class CaseLawContext(BaseJSON):
    linjakkuus_analyysi: Annotated[str, Field(description="Alignment analysis.")]
    poikkeamat_linjasta: Annotated[str, Field(description="Deviations.")]
    suositus_tuomarille: Annotated[str, Field(description="Recommendation to judge.")]
    viitatut_ennakkotapaukset: Annotated[List[str], Field(description="Referenced cases.")]

# --- Step 8c: Coach Agent ---

class ActionItem(BaseModel):
    otsikko: Annotated[str, Field(description="Action title.")]
    kuvaus: Annotated[str, Field(description="Description.")]
    resurssit: Annotated[List[str], Field(default_factory=list, description="URLs or Book refs")]

class ActionGroup(BaseModel):
    kategoria: Annotated[str, Field(description="Category header (e.g. 'Logic', 'Structure')")]
    kohdat: Annotated[List[ActionItem], Field(description="Items in this category")]

class CoachingPlan(BaseJSON):
    kannustava_palaute: Annotated[str, Field(description="Positive feedback.")]
    kehityskohteet_konkreettisesti: Annotated[List[ActionGroup], Field(description="Concrete steps grouped by category")]
    lopputuloksen_kehitysehdotukset: Annotated[List[str], Field(description="Concrete suggestions to improve the final product")]
    lahdeluettelo: Annotated[List[str], Field(default_factory=list, description="Bibliography references used in this plan")]

# --- Step 10: Interaction Analyst Agent ---

class InteractionAnalysis(BaseJSON):
    tunnistetut_strategiat: Annotated[List[str], Field(description="Identified strategies.")]
    ohjausliikkeet: Annotated[int, Field(description="Control moves count.")]
    driver_classification: Annotated[Literal["Matkustaja", "Kartanlukija", "Kuski", "Arkkitehti"], Field(description="Driver profile classification.")]
    input_control_ratio: Annotated[Optional[float], Field(description="Control ratio.")] = None
