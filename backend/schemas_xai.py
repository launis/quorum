from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict

# --- XAI Report Schema ---

class ArviointiKriteeri(BaseModel):
    kriteeri: str = Field(description="Arviointikriteerin nimi (esim. 'Analyysi ja prosessi')")
    arvosana: int = Field(description="Arvosana asteikolla 1-4", ge=1, le=4)
    perustelu: str = Field(description="Lyhyt perustelu arvosanalle")

class YhteenvetoJaHavainnot(BaseModel):
    tiivistelma: str = Field(description="Lyhyt tiivistelmä arvioinnista")
    kriittinen_havainto: str = Field(description="Tärkein kriittinen havainto tai varoitus")

class KognitiivinenArviointiraportti(BaseModel):
    analyyttinen_arviointimatriisi_JEM_A: List[ArviointiKriteeri]
    yhteenveto_ja_keskeiset_havainnot: YhteenvetoJaHavainnot

class XAIRaportti(BaseModel):
    kognitiivinen_arviointiraportti: KognitiivinenArviointiraportti
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kognitiivinen_arviointiraportti": {
                        "analyyttinen_arviointimatriisi_JEM_A": [
                            { "kriteeri": "Analyysi ja prosessi", "arvosana": 4, "perustelu": "Erinomainen strateginen ote." },
                            { "kriteeri": "Arviointi ja argumentaatio", "arvosana": 3, "perustelu": "Hyvä argumentaatio." },
                            { "kriteeri": "Synteesi ja luovuus", "arvosana": 3, "perustelu": "Selkeä synteesi." }
                        ],
                        "yhteenveto_ja_keskeiset_havainnot": {
                            "tiivistelma": "Käyttäjä suoriutui hyvin.",
                            "kriittinen_havainto": "Ei merkittäviä poikkeamia."
                        }
                    }
                }
            ]
        }
    )
