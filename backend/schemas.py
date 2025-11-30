from typing import Literal, Any
from pydantic import BaseModel, Field, field_validator

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

# --- Step 1: Guard Agent ---

class SecurityCheck(BaseModel):
    uhka_havaittu: bool
    adversariaalinen_simulaatio_tulos: str
    riski_taso: Literal["MATALA", "KESKITASO", "KORKEA"]

class TaintedDataContent(BaseModel):
    keskusteluhistoria: str | None = None
    lopputuote: str | None = None
    reflektiodokumentti: str | None = None

class TaintedData(BaseJSON):
    data: TaintedDataContent
    security_check: SecurityCheck
    safe_data: dict[str, Any] | None = None

# --- Step 2: Analyst Agent ---

class Hypoteesi(BaseModel):
    id: str
    vaite_teksti: str
    loytyyko_todisteita: bool

class RagTodiste(BaseModel):
    viittaa_hypoteesiin_id: str
    perusteet: str
    konteksti_segmentti: str
    relevanssi_score: int = Field(..., ge=1, le=10)

    @field_validator('konteksti_segmentti', mode='before')
    @classmethod
    def parse_konteksti_segmentti(cls, v: Any) -> str:
        if isinstance(v, dict):
            # If it's a dict, try to find a likely content key or just dump it
            # Common keys might be 'text', 'content', 'history', 'segment'
            for key in ['text', 'content', 'segment', 'history', 'lopputuote', 'reflektio']:
                if key in v and isinstance(v[key], str):
                    return v[key]
            # Fallback: return JSON string
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
                return 1 # Default fallback
        return v

class TodistusKartta(BaseJSON):
    hypoteesit: list[Hypoteesi]
    rag_todisteet: list[RagTodiste]

    @field_validator('hypoteesit', mode='before')
    @classmethod
    def parse_hypoteesit(cls, v: Any) -> list[Hypoteesi]:
        if isinstance(v, list):
            parsed_list = []
            for item in v:
                if isinstance(item, str):
                    # Attempt to parse string as Hypoteesi object or create a dummy one
                    # If it's a JSON string, try to load it
                    import json
                    try:
                        loaded = json.loads(item)
                        if isinstance(loaded, dict):
                            parsed_list.append(loaded)
                            continue
                    except json.JSONDecodeError:
                        pass
                    
                    # If it's just a text string, wrap it in a dummy Hypoteesi
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
    toulmin_analyysi: list[ToulminKomponentti]
    kognitiivinen_taso: KognitiivinenTaso
    walton_skeema: WaltonSkeema

# --- Step 4: Logical Falsifier ---

class WaltonStressitesti(BaseModel):
    kysymys: str
    kestiko_todistusaineisto: bool
    havainto: str

class PaattelyketjunUskollisuus(BaseModel):
    onko_post_hoc_rationalisointia: bool
    perustelu: str
    uskollisuus_score: Literal["KORKEA", "EPÄVARMA", "HEIKKO"]

class LogiikkaAuditointi(BaseJSON):
    walton_stressitesti_loydokset: list[WaltonStressitesti]
    paattelyketjun_uskollisuus_auditointi: PaattelyketjunUskollisuus

# --- Step 5: Causal Analyst ---

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
    abduktiivinen_paatelma: Literal["Aito Oivallus", "Post-Hoc Rationalisointi", "Epävarma"]

# --- Step 6: Performativity Detector ---

class PerformatiivisuusHeuristiikka(BaseModel):
    heuristiikka: str
    lippu_nostettu: bool
    kuvaus: str

class PreMortemAnalyysi(BaseModel):
    suoritettu: bool
    hiljaiset_signaalit: list[str]

class PerformatiivisuusAuditointi(BaseJSON):
    performatiivisuus_heuristiikat: list[PerformatiivisuusHeuristiikka]
    pre_mortem_analyysi: PreMortemAnalyysi
    yleisarvio_aitoudesta: Literal["Orgaaninen", "Performatiivinen", "Epäilyttävä"]

# --- Step 7: Factual & Ethical Overseer ---

class FaktantarkistusRFI(BaseModel):
    vaite: str
    verifiointi_tulos: Literal["Vahvistettu", "Kumottu", "Ei voitu vahvistaa"]
    lahde_tai_paattely: str

class EettinenHavainto(BaseModel):
    tyyppi: Literal["Syrjintä", "Haitallinen sisältö", "Plagiointi", "Ei havaittu"]
    vakavuus: Literal["Kriittinen", "Varoitus", "N/A"]
    kuvaus: str

class EtiikkaJaFakta(BaseJSON):
    faktantarkistus_rfi: list[FaktantarkistusRFI]
    eettiset_havainnot: list[EettinenHavainto]

# --- Step 8: Judge Agent ---

class KonfliktinRatkaisu(BaseModel):
    konflikti: str
    ratkaisu_malli: Literal["POPPER", "DREYFUS"]
    perustelu: str

class MestaruusPoikkeama(BaseModel):
    tunnistettu: bool
    perustelu: str

class AitousEpaily(BaseModel):
    automaattinen_lippu: bool
    viesti_hitl_lle: str = Field(..., alias="viesti_hitl:lle") # Handle colon in key

class PisteetKriteeri(BaseModel):
    arvosana: Literal[1, 2, 3, 4]
    perustelu: str

class Pisteet(BaseModel):
    analyysi_ja_prosessi: PisteetKriteeri
    arviointi_ja_argumentaatio: PisteetKriteeri
    synteesi_ja_luovuus: PisteetKriteeri

class TuomioJaPisteet(BaseJSON):
    konfliktin_ratkaisut: list[KonfliktinRatkaisu]
    mestaruus_poikkeama: MestaruusPoikkeama
    aitous_epaily: AitousEpaily
    pisteet: Pisteet
    kriittiset_havainnot_yhteenveto: list[str]

# --- Step 9: XAI Reporter ---
# Note: Step 9 produces a text report, but we might want a schema for the intermediate XAI data if needed.
# The prompt says "VAIHE 9: XAI-Raportoija ... generoi lopullisen luettavan raportin ... hyödyntäen yllä olevia tietorakenteita."
# It doesn't explicitly define a JSON output schema for Step 9 in the latest prompt, unlike the previous version.
# However, the previous seed_data.json had an XAIReport schema. 
# Given the user's latest prompt says "Vaihe 9 ei tuota JSON-tiedostoa myöhemmille agenteille", we might not need a strict schema for it, 
# but having one for the internal generation is good practice. I will omit it for now to strictly follow the latest prompt which focuses on the report text.
