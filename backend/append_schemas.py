
# --- Step 2.5: Profiler Agent ---

class ProfilerAnalysis(BaseJSON):
    intentio_analyysi: str
    tunnetila_ja_savy: str
    tunnistetut_vinoumat: list[str]
    psykologinen_profiili: str
    manipulaatio_yritykset: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "metadata": { "luontiaika": "2024-01-01T00:00:00Z", "agentti": "Profiloija", "vaihe": 2.5, "versio": "1.0" },
                    "metodologinen_loki": "Profiili luotu.",
                    "edellisen_vaiheen_validointi": "OK",
                    "semanttinen_tarkistussumma": "hash123",
                    "intentio_analyysi": "Vaikuttaminen tunteisiin.",
                    "tunnetila_ja_savy": "Ahdistunut.",
                    "tunnistetut_vinoumat": ["Vahvistusharha"],
                    "psykologinen_profiili": "Puolustuskannalla.",
                    "manipulaatio_yritykset": "Ei havaittu."
                }
            ]
        }
    )

# --- Step 8a: Archivist Agent ---

class CaseLawContext(BaseJSON):
    linjakkuus_analyysi: str
    poikkeamat_linjasta: str
    suositus_tuomarille: str
    viitatut_ennakkotapaukset: list[str]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "metadata": { "luontiaika": "2024-01-01T00:00:00Z", "agentti": "Arkistonhoitaja", "vaihe": 8.5, "versio": "1.0" },
                    "metodologinen_loki": "Arkisto tarkistettu.",
                    "edellisen_vaiheen_validointi": "OK",
                    "semanttinen_tarkistussumma": "hash123",
                    "linjakkuus_analyysi": "Linjassa.",
                    "poikkeamat_linjasta": "Ei.",
                    "suositus_tuomarille": "Neutraali.",
                    "viitatut_ennakkotapaukset": ["Case-1"]
                }
            ]
        }
    )

# --- Step 8c: Coach Agent ---

class Kehitysehdotus(BaseModel):
    kohde: Literal["Prosessi", "Lopputuote", "Argumentaatio"]
    ongelma: str
    ratkaisuehdotus: str
    hyoty: str

class CoachingPlan(BaseJSON):
    kannustava_palaute: str
    kehityskohteet_konkreettisesti: list[Kehitysehdotus]
    lopputuloksen_kehitysehdotukset: list[str] = Field(..., description="Konkreettiset ehdotukset lopputuotteen (esim. tekstin) parantamiseksi.")
    oppimispolku_viikko: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "metadata": { "luontiaika": "2024-01-01T00:00:00Z", "agentti": "Valmentaja", "vaihe": 8.5, "versio": "1.0" },
                    "metodologinen_loki": "Valmennus luotu.",
                    "edellisen_vaiheen_validointi": "OK",
                    "semanttinen_tarkistussumma": "hash123",
                    "kannustava_palaute": "Hyvä alku!",
                    "kehityskohteet_konkreettisesti": [
                        {
                            "kohde": "Argumentaatio",
                            "ongelma": "Perusteet puuttuvat.",
                            "ratkaisuehdotus": "Lisää lähteitä.",
                            "hyoty": "Uskottavuus kasvaa."
                        }
                    ],
                    "lopputuloksen_kehitysehdotukset": ["Tiivistä johdantoa.", "Lisää väliotsikoita."],
                    "oppimispolku_viikko": "Lue kirja X."
                }
            ]
        }
    )
