from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

# --- Base Schema ---
class BaseJSON(BaseModel):
    metadata: Dict[str, Any] = Field(..., description="Metadata including timestamp, agent, phase, version")
    metodologinen_loki: str = Field(..., description="Methodological log of constraints and limitations")
    semanttinen_tarkistussumma: str = Field(..., description="Short summary of content")

# --- Step 1: Guard ---
class SecurityCheck(BaseModel):
    uhka_havaittu: bool
    adversariaalinen_simulaatio_tulos: str
    riski_taso: str # "MATALA" | "KESKITASO" | "KORKEA"

class TaintedData(BaseJSON):
    data: Dict[str, str] # keskusteluhistoria, lopputuote, reflektiodokumentti
    security_check: SecurityCheck

# --- Step 2: Analyst ---
class Hypoteesi(BaseModel):
    id: str
    vaite_teksti: str
    loytyyko_todisteita: bool

class RagTodiste(BaseModel):
    viittaa_hypoteesiin_id: str
    perusteet: str
    konteksti_segmentti: str
    relevanssi_score: int

class TodistusKartta(BaseJSON):
    hypoteesit: List[Hypoteesi]
    rag_todisteet: List[RagTodiste]

# --- Step 3: Logician ---
class ToulminAnalyysi(BaseModel):
    vaite_id: str
    claim: str
    data: str
    warrant: str
    backing: str

class KognitiivinenTaso(BaseModel):
    bloom_taso: str
    strateginen_syvyys: str

class WaltonSkeema(BaseModel):
    tunnistettu_skeema: str
    kriittiset_kysymykset: List[str]

class ArgumentaatioAnalyysi(BaseJSON):
    toulmin_analyysi: List[ToulminAnalyysi]
    kognitiivinen_taso: KognitiivinenTaso
    walton_skeema: WaltonSkeema

# --- Step 4: Falsifier ---
class WaltonStressitesti(BaseModel):
    kysymys: str
    kestiko_todistusaineisto: bool
    havainto: str

class UskollisuusAuditointi(BaseModel):
    onko_post_hoc_rationalisointia: bool
    perustelu: str
    uskollisuus_score: str # "KORKEA" | "EPÄVARMA" | "HEIKKO"

class LogiikkaAuditointi(BaseJSON):
    walton_stressitesti_loydokset: List[WaltonStressitesti]
    paattelyketjun_uskollisuus_auditointi: UskollisuusAuditointi

# --- Step 5: Causal ---
class KausaalinenAuditointiData(BaseModel):
    aikajana_validi: bool
    havainnot: str

class KontrafaktuaalinenTesti(BaseModel):
    skenaario_A_toteutunut: str
    skenaario_B_simulaatio: str
    uskottavuus_arvio: str

class KausaalinenAuditointi(BaseJSON):
    kausaalinen_auditointi: KausaalinenAuditointiData
    kontrafaktuaalinen_testi: KontrafaktuaalinenTesti
    abduktiivinen_paatelma: str # "Aito Oivallus" | "Post-Hoc Rationalisointi" | "Epävarma"

# --- Step 6: Performativity ---
class Heuristiikka(BaseModel):
    heuristiikka: str
    lippu_nostettu: bool
    kuvaus: str

class PreMortem(BaseModel):
    suoritettu: bool
    hiljaiset_signaalit: List[str]

class PerformatiivisuusAuditointi(BaseJSON):
    performatiivisuus_heuristiikat: List[Heuristiikka]
    pre_mortem_analyysi: PreMortem
    yleisarvio_aitoudesta: str # "Orgaaninen" | "Performatiivinen" | "Epäilyttävä"

# --- Step 7: Fact & Ethics ---
class FaktantarkistusRFI(BaseModel):
    vaite: str
    verifiointi_tulos: str # "Vahvistettu" | "Kumottu" | "Ei voitu vahvistaa"
    lahde_tai_paattely: str

class EettinenHavainto(BaseModel):
    tyyppi: str # "Syrjintä" | "Haitallinen sisältö" | "Plagiointi" | "Ei havaittu"
    vakavuus: str # "Kriittinen" | "Varoitus" | "N/A"
    kuvaus: str

class EtiikkaJaFakta(BaseJSON):
    faktantarkistus_rfi: List[FaktantarkistusRFI]
    eettiset_havainnot: List[EettinenHavainto]

# --- Step 8: Judge ---
class KonfliktinRatkaisu(BaseModel):
    konflikti: str
    ratkaisu_malli: str # "POPPER" | "DREYFUS"
    perustelu: str

class MestaruusPoikkeama(BaseModel):
    tunnistettu: bool
    perustelu: str

class AitousEpaily(BaseModel):
    automaattinen_lippu: bool
    viesti_hitl_lle: str

class Arvosana(BaseModel):
    arvosana: int
    perustelu: str

class Pisteet(BaseModel):
    analyysi_ja_prosessi: Arvosana
    arviointi_ja_argumentaatio: Arvosana
    synteesi_ja_luovuus: Arvosana

class TuomioJaPisteet(BaseJSON):
    konfliktin_ratkaisut: List[KonfliktinRatkaisu]
    mestaruus_poikkeama: MestaruusPoikkeama
    aitous_epaily: AitousEpaily
    pisteet: Pisteet
    kriittiset_havainnot_yhteenveto: List[str]
    lasketut_yhteispisteet: Optional[int] = None
    lasketut_keskiarvo: Optional[float] = None

# --- Step 9: XAI (Report) ---
# --- Step 9: XAI (Report) ---
class UncertaintyAnalysis(BaseModel):
    aleatoric: str
    systemic: List[str]
    epistemic: str

class XAIReport(BaseJSON):
    summary: str
    critical_findings: List[str]
    pre_mortem_signals: Optional[str] = None
    hitl_required: bool
    ethical_issues: List[str]
    audit_questions: List[str]
    uncertainty: UncertaintyAnalysis
    report_content: Optional[str] = None
