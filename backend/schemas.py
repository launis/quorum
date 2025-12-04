from typing import Literal, Any, List, Dict, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from backend.schemas_xai import XAIRaportti

# --- Base Schema ---

class Metadata(BaseModel):
    luontiaika: str = Field(..., description="ISO 8601 format timestamp")
    agentti: str
    vaihe: int
    versio: Literal["1.0", "2.0"] = "2.0"
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
    keskusteluhistoria: str | None = Field(default=None, description="ÄLÄ TULOSTA SISÄLTÖÄ! Käytä VAIN tätä tekstiä: '{{FILE: Keskusteluhistoria.pdf}}'")
    lopputuote: str | None = Field(default=None, description="ÄLÄ TULOSTA SISÄLTÖÄ! Käytä VAIN tätä tekstiä: '{{FILE: Lopputuote.pdf}}'")
    reflektiodokumentti: str | None = Field(default=None, description="ÄLÄ TULOSTA SISÄLTÖÄ! Käytä VAIN tätä tekstiä: '{{FILE: Reflektiodokumentti.pdf}}'")

class TaintedData(BaseJSON):
    data: TaintedDataContent
    security_check: SecurityCheck
    safe_data: dict[str, Any] | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "metadata": {
                        "luontiaika": "2024-07-30T12:00:00Z",
                        "agentti": "Vartija",
                        "vaihe": 1,
                        "versio": "1.0",
                        "suoritus_ymparisto": "Internal"
                    },
                    "metodologinen_loki": "Suoritettu syötteen puhdistus ja tarkistus.",
                    "edellisen_vaiheen_validointi": "Ei edellistä vaihetta.",
                    "semanttinen_tarkistussumma": "a1b2c3d4...",
                    "data": {
                        "keskusteluhistoria": "{{FILE: Keskusteluhistoria.pdf}}",
                        "lopputuote": "{{FILE: Lopputuote.pdf}}",
                        "reflektiodokumentti": "{{FILE: Reflektiodokumentti.pdf}}"
                    },
                    "security_check": {
                        "uhka_havaittu": False,
                        "adversariaalinen_simulaatio_tulos": "Ei uhkia.",
                        "riski_taso": "MATALA"
                    },
                    "safe_data": None
                }
            ]
        }
    )

# --- Step 2: Analyst Agent ---

class Hypoteesi(BaseModel):
    id: str
    vaite_teksti: str
    loytyyko_todisteita: bool

class RagTodiste(BaseModel):
    viittaa_hypoteesiin_id: str | list[str]
    perusteet: str
    konteksti_segmentti: str = Field(..., description="Lyhyt ote tekstistä. ÄLÄ kopioi koko dokumenttia.")
    relevanssi_score: int = Field(..., ge=1, le=10)

    @field_validator('viittaa_hypoteesiin_id', mode='before')
    @classmethod
    def parse_viittaa_hypoteesiin_id(cls, v: Any) -> str | list[str]:
        if isinstance(v, str):
            # If it looks like a list string "['ID1', 'ID2']", try to parse it
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
    hypoteesit: list[Hypoteesi]
    rag_todisteet: list[RagTodiste]

    @field_validator('hypoteesit', mode='before')
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
                    parsed_list.append({
                        "id": "GENERATED_ID", 
                        "vaite_teksti": item, 
                        "loytyyko_todisteita": False
                    })
                else:
                    parsed_list.append(item)
            return parsed_list
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "metadata": {
                        "luontiaika": "...",
                        "agentti": "Analyytikko",
                        "vaihe": 2,
                        "versio": "1.0",
                        "suoritus_ymparisto": "Internal"
                    },
                    "metodologinen_loki": "...",
                    "edellisen_vaiheen_validointi": "...",
                    "semanttinen_tarkistussumma": "...",
                    "hypoteesit": [
                        {
                            "id": "H1",
                            "vaite_teksti": "...",
                            "loytyyko_todisteita": True
                        }
                    ],
                    "rag_todisteet": [
                        {
                            "viittaa_hypoteesiin_id": "H1",
                            "perusteet": "...",
                            "konteksti_segmentti": "...",
                            "relevanssi_score": 10
                        }
                    ]
                }
            ]
        }
    )

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

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "metadata": { "luontiaika": "...", "agentti": "Loogikko", "vaihe": 3, "versio": "1.0" },
                    "metodologinen_loki": "...",
                    "edellisen_vaiheen_validointi": "...",
                    "semanttinen_tarkistussumma": "...",
                    "toulmin_analyysi": [
                        {
                            "vaite_id": "H1",
                            "claim": "...",
                            "data": "...",
                            "warrant": "...",
                            "backing": "..."
                        }
                    ],
                    "kognitiivinen_taso": {
                        "bloom_taso": "Analyze",
                        "strateginen_syvyys": "Korkea"
                    },
                    "walton_skeema": {
                        "tunnistettu_skeema": "Expert Opinion",
                        "kriittiset_kysymykset": ["..."]
                    }
                }
            ]
        }
    )

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

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "metadata": { "luontiaika": "...", "agentti": "Falsifioija", "vaihe": 4, "versio": "1.0" },
                    "metodologinen_loki": "...",
                    "edellisen_vaiheen_validointi": "...",
                    "semanttinen_tarkistussumma": "...",
                    "walton_stressitesti_loydokset": [
                        {
                            "kysymys": "...",
                            "kestiko_todistusaineisto": True,
                            "havainto": "..."
                        }
                    ],
                    "paattelyketjun_uskollisuus_auditointi": {
                        "onko_post_hoc_rationalisointia": False,
                        "perustelu": "...",
                        "uskollisuus_score": "KORKEA"
                    }
                }
            ]
        }
    )

# --- Step 5: Factual & Ethical Overseer ---

class FaktantarkistusRFI(BaseModel):
    vaite: str
    verifiointi_tulos: Literal["Vahvistettu", "Kumottu", "Ei voitu vahvistaa"]
    lahde_tai_paattely: str

class EettinenHavainto(BaseModel):
    tyyppi: Literal["Syrjintä", "Haitallinen sisältö", "Plagiointi", "Ei havaittu"]
    vakavuus: Literal["Kriittinen", "Varoitus", "N/A"]
    kuvaus: str

class EtiikkaJaFakta(BaseJSON):
    faktantarkistus_rfi: list[FaktantarkistusRFI] = Field(default_factory=list)
    eettiset_havainnot: list[EettinenHavainto] = Field(default_factory=list)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "metadata": { "luontiaika": "...", "agentti": "Valvoja", "vaihe": 5, "versio": "1.0" },
                    "metodologinen_loki": "...",
                    "edellisen_vaiheen_validointi": "...",
                    "semanttinen_tarkistussumma": "...",
                    "faktantarkistus_rfi": [
                        {
                            "vaite": "...",
                            "verifiointi_tulos": "Vahvistettu",
                            "lahde_tai_paattely": "..."
                        }
                    ],
                    "eettiset_havainnot": [
                        {
                            "tyyppi": "Ei havaittu",
                            "vakavuus": "N/A",
                            "kuvaus": "..."
                        }
                    ]
                }
            ]
        }
    )

# --- Step 6: Causal Analyst ---

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

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "metadata": { "luontiaika": "...", "agentti": "Kausaalinen", "vaihe": 6, "versio": "1.0" },
                    "metodologinen_loki": "...",
                    "edellisen_vaiheen_validointi": "...",
                    "semanttinen_tarkistussumma": "...",
                    "kausaalinen_auditointi": {
                        "aikajana_validi": True,
                        "havainnot": "..."
                    },
                    "kontrafaktuaalinen_testi": {
                        "skenaario_A_toteutunut": "...",
                        "skenaario_B_simulaatio": "...",
                        "uskottavuus_arvio": "..."
                    },
                    "abduktiivinen_paatelma": "Aito Oivallus"
                }
            ]
        }
    )

# --- Step 7: Performativity Detector ---

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

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "metadata": { "luontiaika": "...", "agentti": "Performatiivisuus", "vaihe": 7, "versio": "1.0" },
                    "metodologinen_loki": "...",
                    "edellisen_vaiheen_validointi": "...",
                    "semanttinen_tarkistussumma": "...",
                    "performatiivisuus_heuristiikat": [
                        {
                            "heuristiikka": "Keinotekoinen monimutkaisuus",
                            "lippu_nostettu": False,
                            "kuvaus": "..."
                        }
                    ],
                    "pre_mortem_analyysi": {
                        "suoritettu": True,
                        "hiljaiset_signaalit": ["..."]
                    },
                    "yleisarvio_aitoudesta": "Orgaaninen"
                }
            ]
        }
    )

# --- Step 8: Judge Agent ---

class KonfliktinRatkaisu(BaseModel):
    konflikti: str
    ratkaisu_malli: str # Relaxed from Literal to allow flexibility
    perustelu: str

class MestaruusPoikkeama(BaseModel):
    tunnistettu: bool
    perustelu: str

class AitousEpaily(BaseModel):
    automaattinen_lippu: bool
    viesti_hitl_lle: str = Field(..., alias="viesti_hitl:lle") 

class PisteetKriteeri(BaseModel):
    arvosana: int = Field(..., ge=1, le=4)
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

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "metadata": { "luontiaika": "...", "agentti": "Tuomari", "vaihe": 8, "versio": "1.0" },
                    "metodologinen_loki": "...",
                    "edellisen_vaiheen_validointi": "...",
                    "semanttinen_tarkistussumma": "...",
                    "konfliktin_ratkaisut": [],
                    "mestaruus_poikkeama": {
                        "tunnistettu": False,
                        "perustelu": "..."
                    },
                    "aitous_epaily": {
                        "automaattinen_lippu": False,
                        "viesti_hitl:lle": "..."
                    },
                    "pisteet": {
                        "analyysi_ja_prosessi": { "arvosana": 3, "perustelu": "..." },
                        "arviointi_ja_argumentaatio": { "arvosana": 3, "perustelu": "..." },
                        "synteesi_ja_luovuus": { "arvosana": 3, "perustelu": "..." }
                    },
                    "kriittiset_havainnot_yhteenveto": ["..."]
                }
            ]
        }
    )

# --- Step 9: XAI Reporter ---

class XAIReportSection(BaseModel):
    title: str
    content: str
    visualizations: list[str] | None = None

class XAIReport(BaseJSON):
    executive_summary: str
    detailed_analysis: list[XAIReportSection]
    final_verdict: str
    confidence_score: float

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "metadata": { "luontiaika": "...", "agentti": "XAI-Raportoija", "vaihe": 9, "versio": "1.0" },
                    "metodologinen_loki": "...",
                    "edellisen_vaiheen_validointi": "...",
                    "semanttinen_tarkistussumma": "...",
                    "executive_summary": "...",
                    "detailed_analysis": [
                        {
                            "title": "Analyysin Yhteenveto",
                            "content": "...",
                            "visualizations": []
                        }
                    ],
                    "final_verdict": "Hyväksytty",
                    "confidence_score": 0.95
                }
            ]
        }
    )

