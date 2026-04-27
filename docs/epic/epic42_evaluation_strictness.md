# Epic 42: Arvioinnin tiukkuuden toteutusmallit (Evaluation Strictness)

Tässä dokumentissa on avattu yksityiskohtaisesti kolme eri arkkitehtonista tapaa toteuttaa tekoälyn True/False -päätösten tiukkuuden säätö (Strictness). Jokaisessa mallissa käydään läpi sen filosofinen merkitys, tarkka kooditason toteutustapa Quorum-arkkitehtuurissa, sekä lopputulokset järjestelmän ja loppukäyttäjän kannalta.

---

## Malli 1: Prompt-ohjattu tiukkuus (Kielitieteellinen)

**Merkitys:**  
Tämä on perinteinen "ChatGPT-tyyppinen" ratkaisu. Luotamme siihen, että kun sanomme tekoälylle "ole lempeämpi", se ymmärtää mitä tarkoitamme ja muuttaa käytöstään. Ohjelmistoarkkitehtuuri pysyy täysin ennallaan, ainoastaan tekoälylle menevä tekstimuotoinen ohjeistus muuttuu.

**Toteutustapa koodissa:**
1. Otamme käyttöön `prompt_compiler.py` -tiedostossa jo uinuvan `calibrate_strictness(level)` -funktion.
2. Kun `DAGExecutor` rakentaa työnkulkua, se lukee asetuksista (esim. 0-100) tiukkuuden ja lisää LLM:n järjestelmäpromptin alkuun lauseen:
   - *Lempeä (esim. 25):* "STRICTNESS CALIBRATION (25/100): Lenient. Be generally forgiving of minor errors..."
   - *Tiukka (esim. 100):* "STRICTNESS CALIBRATION (100/100): Absolute Strictness. You are an unforgiving auditor..."

**Lopputulokset ja vaikutus:**
- **Käyttäjälle:** Tulokset muuttuvat todennäköisesti hieman pehmeämmiksi lempeällä asetuksella (enemmän True-arvoja).
- **Järjestelmälle:** Erittäin arvaamaton. Pitkissä teksteissä tekoäly saattaa unohtaa promptin alun ("Attention Dilution") ja palata oletustiukkuuteen. Tulos on musta laatikko: emme koskaan voi ohjelmallisesti todistaa, *miksi* LLM päätti antaa True-arvon jossain satunnaisessa matriisissa.

---

## Malli 2: Skeema-ohjattu tiukkuus (Pydantic Fail-Fast)

**Merkitys:**  
Quorum-arkkitehtuurin erikoisuus on dynaamiset Pydantic-skeemat. LLM:ää ei ohjata vain sanoilla, vaan sitä ohjataan ohjelmointikielen tietorakenteilla. Tässä mallissa muutamme tiukkuutta muuttamalla niitä fyysisiä ehtoja, jotka LLM:n palauttaman vastauksen on täytettävä, jotta järjestelmä ei kaadu.

**Toteutustapa koodissa:**
Muutetaan `prompt_compiler.py`:n `build_dynamic_schema()` -metodia (jossa `AtomResponse` luodaan lennosta).
1. **Lempeä ajo (Lenient):**
   ```python
   quote: str | None = Field(default=None, description="Vapaaehtoinen lainaus. Anna Null jos osuma on vain implisiittinen.")
   boolean: bool = Field(..., description="True, jos teksti edes sivuaa aihetta. Oleta hyvä tarkoitus.")
   ```
2. **Tiukka ajo (Strict Auditor):**
   ```python
   quote: str = Field(..., description="PAKOLLINEN, täydellinen verbatim-lainaus lähdetekstistä.")
   boolean: bool = Field(..., description="True VAIN JOS pakollinen lainaus todistaa asian absoluuttisesti.")
   ```

**Lopputulokset ja vaikutus:**
- **Järjestelmälle:** 100% "Fail-Fast" suoja. Jos olemme "Tiukassa" tilassa, ja LLM yrittää antaa `True` mutta ei löydä sananmukaista lainausta (`quote`), Pydantic-skeema heittää välittömästi `ValidationError`. LLM pakotetaan korjaamaan virheensä ja vaihtamaan arvo `False`:ksi.
- **Käyttäjälle:** Luotettava kokemus. Lempeä-asetus antaa reilusti "helpotusta", koska LLM uskaltaa antaa True-arvoja silloinkin, kun se päättelee asioita rivien välistä ilman suoria todisteita.

---

## Malli 3: Hybridi (Numeerinen arvo + Pydantic Fail-Fast Maadoitus)

**Merkitys:**  
Tämä on Quorumin asiantuntija-arkkitehtuurin todellinen kulmakivi, joka ottaa huomioon sekä "Code is Truth" -periaatteen että Googlen infrastruktuurin kovat reunaehdot (esim. 5 RPM maksimiraja). Pelkkä numeerinen arvio altistaisi tekoälyn hallusinoimaan kalibrointiharhan vuoksi ("pseudomatiikkaa"). Tässä mallissa tekoäly tuottaa numeerisen luottamusarvion, mutta se pakotetaan "maadoittamaan" se fyysisellä lainauksella Pydanticin nollahypoteesi-säännön kautta.

**Toteutustapa koodissa:**
1. **Skeeman muutos (`AtomResponse` tai matriisikohtainen laajennus):**
   Lisätään float-arvon rinnalle lainaus, ja validoidaan se armottomasti `@model_validator` -koristeella.
   ```python
   confidence_score: float = Field(..., ge=0.0, le=100.0, description="Numeerinen arvio (0-100).")
   quote: str | None = Field(default=None, description="Verbatim-lainaus lähteestä.")

   @model_validator(mode="after")
   def enforce_quote_for_high_confidence(self):
       # FAIL-FAST ARKKITEHTUURI (Nollahypoteesi-mandaatti)
       strictness_baseline = 50.0 
       if self.confidence_score >= strictness_baseline and not self.quote:
           raise ValueError(
               "Fail-Fast Error: Confidence is high, but explicit verbatim quote is missing."
           )
       return self
   ```
2. **Backendin laskentalogiikka (esim. BlueprintTransformer / DINA-malli):**
   ```python
   # Kynnys voidaan määritellä dynaamisesti (esim. 30.0 = Lempeä, 85.0 = Tiukka)
   threshold = execution.metadata.get("strictness_threshold", 50.0)
   atom.is_hit = atom.confidence_score >= threshold
   ```

**Lopputulokset ja vaikutus:**
- **Arkkitehtuurille ja Infrastruktuurille:** Täydellinen tasapaino luotettavuuden ja API-kustannusten/nopeuden välillä. Koska emme aja satoja erillisiä boolean-atomeja ristiinkuulusteluineen, emme törmää Googlen 5 RPM -rajoitteisiin. Saamme kerralla koko matriisin tai ryhmän arviot, minimoimalla erillisten LLM-kutsujen määrän (vrt. Karkaistu Malli 2).
- **Hallusinaatioiden tappaminen (Grounding):** Pydantic-validaattori varmistaa lennosta, että "mututuntumalla" annettu korkea pistemäärä ei mene läpi ilman konkreettista näyttöä (lainaus).
- **Mullistava etu (Jälkikäteen säätäminen DINA-mallilla!):** Koska LLM palautti "raakadatan" (numeerinen analyysi + lainaus), loppukäyttäjä voi säätää tiukkuutta käyttöliittymästä jälkikäteen ilman ainoatakaan uutta Vertex AI -kutsua. Raportti päivittyy lennosta näyttämään, mitkä kohdat putoavat punaiseksi ja mitkä pysyvät vihreinä.

---

### Loppupäätelmä
- Jos etsimme tieteisutooppista "Titanium Standardia" (Karkaistu Malli 2), jossa jokainen fakta tarkistetaan erikseen Pydantic Substring Matchilla ja Falsifier-agentilla, tuhoaisimme suorituskyvyn (kymmeniä minuutteja per raportti) ja törmäisimme jatkuvasti Googlen API-rajoihin (esim. 5 RPM).
- Siksi **Hybridi Malli 3** on ainoa oikea, tuotantovalmis tie. Se sitoo yhteen Pydanticin Fail-Fast -luotettavuuden (maadoitus lainauksilla) ja dynaamisen matemaattisen raja-arvon (Zero-Math UI / DINA), tarjoten sekä turvallisuutta että äärimmäisen joustavan loppukäyttäjäkokemuksen kustannustehokkaasti.

Malli 1 tulisi hylätä liian epävarmana "mustana laatikkona".
