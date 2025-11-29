from typing import Literal, Any
from pydantic import BaseModel, Field

# --- Base Schema ---

class Metadata(BaseModel):
    luontiaika: str = Field(..., description="ISO 8601 format timestamp")
    agentti: str
    vaihe: int
    versio: Literal["1.0"] = "1.0"
    suoritus_ymparisto: Literal["Kriitikkoryhma_External", "Internal"] | None = None

class BaseJSON(BaseModel):
    metadata: Metadata
    metodologinen_loki: str
    edellisen_vaiheen_validointi: str
    semanttinen_tarkistussumma: str

class SecurityCheck(BaseModel):
    uhka_havaittu: bool
    adversariaalinen_simulaatio_tulos: str
    riski_taso: Literal["MATALA", "KESKITASO", "KORKEA"]

class TaintedDataContent(BaseModel):
    keskusteluhistoria: str
    lopputuote: str
    reflektiodokumentti: str

class TaintedData(BaseJSON):
    data: TaintedDataContent
    security_check: SecurityCheck
    safe_data: dict[str, Any] | None = None

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
    hypoteesit: list[Hypoteesi]
    rag_todisteet: list[RagTodiste]

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
    kriittiset_kysymykset: list[str]

class ArgumentaatioAnalyysi(BaseJSON):
    toulmin_analyysi: list[ToulminAnalyysi]
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
    walton_stressitesti_loydokset: list[WaltonStressitesti]
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
    hiljaiset_signaalit: list[str]

class PerformatiivisuusAuditointi(BaseJSON):
    performatiivisuus_heuristiikat: list[Heuristiikka]
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
    faktantarkistus_rfi: list[FaktantarkistusRFI]
    eettiset_havainnot: list[EettinenHavainto]

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
    konfliktin_ratkaisut: list[KonfliktinRatkaisu]
    mestaruus_poikkeama: MestaruusPoikkeama
    aitous_epaily: AitousEpaily
    pisteet: Pisteet
    kriittiset_havainnot_yhteenveto: list[str]
    lasketut_yhteispisteet: int | None = None
    lasketut_keskiarvo: float | None = None

# --- Step 9: XAI (Report) ---
# --- Step 9: XAI (Report) ---
class UncertaintyAnalysis(BaseModel):
    aleatoric: str
    systemic: list[str]
    epistemic: str

class XAIReport(BaseJSON):
    summary: str
    critical_findings: list[str]
    pre_mortem_signals: str | None = None
    hitl_required: bool
    ethical_issues: list[str]
    audit_questions: list[str]
    uncertainty: UncertaintyAnalysis
    report_content: str | None = None
