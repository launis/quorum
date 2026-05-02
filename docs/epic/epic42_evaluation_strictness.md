# Epic 42: Arvioinnin tiukkuuden arkkitehtuuri (Evaluation Strictness)

Tässä dokumentissa kuvataan Quorum V2 -arkkitehtuurin asettama "Single Truth" -standardi tekoälyn True/False -päätösten tiukkuuden säätöön. Järjestelmä hylkää hallusinaatioalttiit numeeriset kynnysarvot (pseudomatiikka) ja nojaa sen sijaan vahvaan Pydantic Fail-Fast -skeemaan sekä portaittaiseen kielelliseen roolitukseen.

---

## Tavoitetila: Lopullinen Pydantic-skeema

Quorum-arkkitehtuurin erikoisuus on dynaamiset Pydantic-skeemat yhdistettynä "Zero-Trust" -promptaukseen. LLM:ää ei ohjata vain sanoilla, vaan sitä ohjataan ohjelmointikielen tietorakenteilla.

Jotta vältämme epävarmaa luonnollisen kielen tulkintaa ("kirjoittiko LLM sanan IMPLICIT HIT reasoning-kenttään?") ja hallitsemme laiskuusilmiötä, Atom-tason evaluaatiossa LLM pakotetaan vastaamaan ehdottoman matemaattisen tyyppiturvalliseen `AtomResponse`-skeemaan. (Huom: Kaikkien uusien mallien tulee käyttää modernia Python 3.14 union-syntaksia `| None`, ei legacy `Optional` -kirjastoa):

```python
class EvidenceType(str, Enum):
    EXPLICIT_QUOTE = "EXPLICIT_QUOTE"
    IMPLIED_INTENT = "IMPLIED_INTENT"
    NO_EVIDENCE = "NO_EVIDENCE"

class AtomResponse(BaseModel):
    # Aakkostushakkerointi (Zero-Trust) varmistaa Micro-CoT-järjestyksen
    step_1_evidence_type: EvidenceType = Field(
        ..., 
        description="CRITICAL: You MUST choose your strategy first."
    )
    step_2_quote: str | None = Field(
        default=None, 
        description="Required if evidence_type is EXPLICIT_QUOTE. The exact verbatim quote."
    )
    step_3_implicit_justification: str | None = Field(
        default=None, 
        description="Required ONLY if evidence_type is IMPLIED_INTENT. Provide an exhaustive 20+ word justification to prove the implied intent."
    )
    step_4_reasoning: str = Field(
        ..., 
        description="Final cognitive friction and evaluation reasoning."
    )
    step_5_boolean: bool = Field(
        ..., 
        description="The final True/False decision."
    )
```

1. **Ennakoiva kognitio (Forced Strategy Declaration):** `step_1_evidence_type: EvidenceType` on mallin **ensimmäinen** kenttä. Tämä pakottaa LLM:n lukitsemaan strategiansa (Enum-arvon valinta) ennen kuin se voi miettiä lainausta tai boolean-päätöstä.
2. **Deterministinen validointi (`@model_validator`):**
   Kirjoita `AtomResponse`-luokkaan Pydantic mallivalidaattori (`@model_validator(mode='after')`), joka valvoo seuraavia ehtoja:
   * Jos `step_1_evidence_type == EXPLICIT_QUOTE`, kentän `step_2_quote` on pakko sisältää tekstiä.
   * Jos `step_1_evidence_type == IMPLIED_INTENT`:
     * Kentän `step_3_implicit_justification` on pakko sisältää tekstiä.
     * **Aito tekninen valvonta (Hard Floor):** Validaattorin on tarkistettava sanamäärä fyysisesti (`len(step_3_implicit_justification.split()) >= 20`). Jos perustelu on liian lyhyt, heitä `ValueError("ANTI-LAZINESS MANDATE: Justification too short...")`. 20 sanaa luo asymmetrisen kynnyksen laiskuudelle, mutta ei romuta UX-latenssia.
     * Jos ajonaikainen `strictness_level >= 70` (luetaan `ValidationInfo.context` -objektista), heitä `ValueError` ("Strictness >= 70 ei salli implisiittistä logiikkaa").
   * Jos `step_1_evidence_type == NO_EVIDENCE`, `step_5_boolean`:in on oltava `False`.

### Haaste: "Benefit of the Doubt" ja LLM Laziness (Laiskuuden estoprotokolla)

Aiempi skeema salli lainauksen puuttumisen (`quote: str | None`) ilman lisävaatimuksia, mikä altisti järjestelmän "LLM Laziness" -ilmiölle (Path of Least Resistance). Jos LLM oppii, että se voi antaa `True`-tuloksia ilman fyysisen lainauksen etsimistä, se alkaa käyttää tätä porsaanreikää säästääkseen laskentatehoa (tokeneita).

Uudessa tavoitetilassa järjestelmään on sisäänrakennettu tiukka **Laiskuuden estoprotokolla (Anti-Laziness Mandate)**. Koska pelkkä kielellinen kielto ei riitä estämään LLM:n "Reward Hacking" -ilmiötä (oikoreittien etsimistä), nojaamme rakenteelliseen pelotteeseen:

1. **Epäsymmetrinen työtaakka (Asymmetric Token Cost) & Aito tekninen valvonta:** Pydantic-skeema sisältää pakollisen `implicit_justification` -kentän, jos malli valitsee pakoventtiilin (`EvidenceType.IMPLIED_INTENT`). Koska LLM:t ovat huonoja laskemaan sanoja pelkän kielellisen promptin perusteella ("150+ words"), Pydantic-validaattori asettaa ehdottoman teknisen lattian (esim. vähintään 50 sanaa). Tämä varmistaa fyysisesti asymmetrisen työtaakan: "tekosyyn" generoiminen vaatii aina mallilta enemmän token-laskentaa kuin suoran lainauksen poimiminen.
2. **Fail-Fast Rankaisu & Uudelleenyritysten elinkaari (Retry Lifecycle):** Kun Pydantic heittää `LLMSchemaValidationError`-poikkeuksen oikotien tai liian lyhyen selityksen käytöstä, malli pakotetaan yrittämään uudelleen.
   * **Retry Budget:** Säännön `infinite_retry_loops` mukaisesti `LLMTaskExecutor` nojaa globaaliin `SystemConcurrency.LLM_MAX_RETRIES` -vakioon (kiinteä 2 yritystä). Mielivaltaisia uusia limiittejä ei saa koodata.
   * **Terminaalinen kaatuminen (Zero "Silent False" -sääntö):** Jos maksimiyritykset ylitetään, järjestelmä **EI SAA** palauttaa automaattisesti arvoa `boolean: false`. Tämä vääristäisi arviointidataa. Sen sijaan suoritus kaatuu kyseisen Atomin kohdalla näkyvästi (esim. `EvaluationExecutionError`), jotta asiantuntija näkee arvioinnin epäonnistuneen rakenteellisesti eikä faktuaalisesti.
3. **Kielellinen pakkopaita:** Lempeisiin asennekategorioihin (esim. Lenient) lisätään lisäehto PromptCompileriin: *"You must NEVER use a Null quote simply to save effort. If a verbatim quote exists anywhere in the text, you are strictly mandated to extract it. Implicit hits require exhaustive justification."*

Tämä varmistaa, että "Benefit of the Doubt" ei tarkoita oikeutta olla laiska, ja Quorumin "Evidence-Based Reporting" -mandaatti säilyy murtumattomana myös matalammalla tiukkuusasetuksella.

### Haaste: Sycophantic Reasoning ja Hallusinaatiot (Micro-CoT Maadoitus)

Vaikka "Chain of Thought" (Micro-CoT) parantaa tekoälyn logiikkaa, se altistaa järjestelmän "Sycophantic Reasoning" -ilmiölle (mielistelevä perustelu). Jos LLM alitajuisesti kallistuu virheelliseen `True`-päätökseen, se on kielellisesti erittäin kyvykäs keksimään (hallusinoimaan) uskottavan kuuloisia mutta lähdetekstistä puuttuvia faktoja tukeakseen päätöstään `reasoning`-kentässä.

Quorum-arkkitehtuuri torjuu tämän kolmella tasolla, sillä pelkkä Pydantic-luokan määrittely ei automaattisesti takaa JSON-avainten generointijärjestystä API-tasolla:

1. **Zero-Trust Aakkostushakkerointi (Strict JSON Order):** Koska autoregressiivinen malli menettää "Chain of Thought" -edun täysin, jos se sattuu generoimaan päätöksen (`step_5_boolean`) ennen perusteluja, emme voi luottaa siihen, että API-tarjoajat (kuten OpenAI) kunnioittavat Pydantic-luokan määrittelyjärjestystä. Siksi avaimet on pakko nimetä aakkosjärjestykseen (`step_1_...`, `step_2_...`). Tämä varmistaa ehdottoman Micro-CoT-maadoituksen.
2. **Fail-Fast Pydantic Context (Ei 3rd Party Wrappereita):** Säännön `ai_bloatware_ban` mukaisesti Quorumissa koodin on oltava meidän natiivissa hallinnassa. Pydantic-validaattorille syötetään `strictness_level` suoraan `AtomResponse.model_validate_json(llm_output, context={'strictness_level': level})` -kutsussa natiivin `LLMTaskExecutorin` sisällä. Kolmannen osapuolen kirjastojen (kuten LangChain) aiheuttamaa abstraktiovuoto-riskiä ei siis ole.
3. **Explicit Negative Prompting & Order Mandate:** PromptCompileriin integroidaan hallusinaatiokiellon lisäksi ehdoton järjestysmääräys: *"CRITICAL: You MUST output the JSON keys in the exact strict order: step_1 to step_5. Your reasoning MUST ONLY synthesize facts explicitly stated in the source text."*

---

## Toteutettavat tehtävät (Technical Spec): Dynaaminen tiukkuuden säätö

Siirrä tiukkuuden säätö suoraan loppukäyttäjän hallintaan hyödyntäen nykyisiä suojamekanismeja. Toteuta alla olevat vaatimukset imperatiivisesti.

### 1. Backend: Hard Mandate, Zero Defaults & Fail-Fast Hydration

Quorum V2 -arkkitehtuurin Fail-Fast -periaatteen mukaisesti tiukkuusasetuksessa sovelletaan ehdotonta **Zero Defaults** -linjaa. Järjestelmässä ei sallita `null`-arvoja tai pehmeitä oletuksia, jotta vältytään piileviltä arkkitehtonisilta virheiltä.

*   **API ja Payloadit (Fail-Fast Hydration):** Lisää `strictness_level: int = Field(..., ge=0, le=100)` pakolliseksi kentäksi kaikkiin ajon luonnin DTO-malleihin. Tiukkuustaso ei saa matkustaa logiikkakerroksessa raakana sanakirjana (esim. `payload.get("strictness_level")`). Kaikki HTTP-data on hydratoitava välittömästi tyyppiturvalliseksi DTO-objektiksi (`.model_validate()`) heti rajapinnassa. Natiivi C/Rust-tason Field-validointi (`ge=0, le=100`) korvaa manuaaliset `@field_validator`-funktiot.
*   **Tietokantamallit & Zero Legacy Fallbacks:** Määrittele `strictness_level` pakolliseksi (non-nullable) kentäksi kaikissa historiatietokantamalleissa (esim. `ExecutionRecord`, `ReportDataDTO`). Älä koskaan käytä `@model_validator`-purkkakorjauksia vanhan datan hiljaiseksi hyväksymiseksi. Arkkitehtonisen driftaamisen estämiseksi vanhat tietueet on päivitettävä kerralla erillisellä tietokannan migraatioskriptillä.

### 2. Frontend-toteutus (Flutter UI & Työnkulkukohtaisuus)

Tiukkuusasetuksen on oltava ehdottomasti **työnkulkukohtainen (Workflow-specific)**, ei globaali järjestelmä- tai tenant-asetus. UX-illuusioiden estämiseksi ja "Evidence-Based Reporting" -mandaatin täyttämiseksi toteuta seuraavat toimenpiteet:

*   **Pakollinen Valintalista (Dropdown / Segmented Control):** Lisää Workflow Builderin "Yleiset & Tulosteet" -välilehdelle pakollinen tiukkuuden valinta. Koska tekoäly kykenee aidosti erottamaan vain 5 erilaista asennetta, liukusäätimen (Slider) käyttö on kielletty UX-illuusiona. Tarjoa tasan viisi kielellistä valintaa (esim. Absolute Leniency, Lenient, Balanced, Strict, Absolute Strictness).
*   **Taustamuunnos (Integer):** Mappaa käyttäjän tekemä semanttinen valinta taustalla standardiarvoksi (0, 15, 50, 85, 100). Lähetä tämä numeroarvo `POST`-kutsussa backendin `strictness_level`-kenttään. Tämä säilyttää tyyppiturvallisuuden (0-100) ilman UX-illuusioita.
*   **Auditoitavuus tulosnäkymässä (`execution_report_view.dart`):** Näytä raportin otsikossa selkeä Chip/Badge käytetystä tiukkuudesta. Näytä lisäksi jokaisen atomin tuloslaatikossa visuaalisesti LLM:n palauttama `EvidenceType` (esim. ikoni `EXPLICIT_QUOTE` tai varoittava ikoni `IMPLIED_INTENT`), jotta asiantuntija pystyy arvioimaan osuman faktuaalisen painoarvon yhdellä silmäyksellä.

### 3. Backend API ja Orkestrointi (DAGExecutor & LLMTaskExecutor)

*   **Sanakirjojen Täyskielto:** Konfiguroi `DAGExecutor` lukemaan tiukkuusarvo tyyppiturvallisesta DTO:sta työnkulun alkaessa. Arvoja ei poimita raaoista sanakirjoista.
*   **LLM-orkestroinnin Puhtaus:** Arvioinnin toteutuksessa ei saa tehdä suoria `LLMClient`-kutsuja tai manuaalista JSON-parsimista. Koko putki on pakotettava turvallisen pullonkaulan `LLMTaskExecutor.execute_structured_task(...)` läpi, joka takaa keskitetyn lokituksen ja FinOps-valvonnan.
*   **Pydantic Validation Context:** Koska alin Pydantic-malli (`AtomResponse`) on staattinen tietorakenne, välitä ajonaikainen tiukkuustaso Pydanticille injektoimalla se parserointivaiheessa kontekstina `execute_structured_task` -kutsun sisällä: `AtomResponse.model_validate_json(llm_output, context={'strictness_level': level})`. Tämän ansiosta luokan sisällä oleva `@model_validator` voi lukea arvon ja päättää dynaamisesti (esim. jos tiukkuus >= 70), sallitaanko laiskuuden oikoreitti (`IMPLIED_INTENT`) vai heitetäänkö Fail-Fast -rangaistus.

### 4. PromptCompiler ja Dynaaminen Injektio

*   **LLM-arkkitehtuurisääntöjen noudattaminen:** Syötä `DAGExecutorin` lukema arvo `prompt_compiler.py`:n `calibrate_strictness(level)` -funktiolle.
*   **Kriittinen Sijoittelu:** Sääntöjen `ephemeral_caching_topology` ja `high_fidelity_prompting_and_caching` mukaisesti: **Älä koskaan injektoi** palautettua ohjetta (Semantic Persona) System Promptiin, sillä se tuhoaa Prompt Caching -hyödyt. Injektoi dynaaminen tiukkuusohjeistus vain LLM-kutsun `user`-viestiin (**payloadin aivan loppuun**, kaiken staattisen datan jälkeen) ja eristä se tarkasti XML-tagien sisään: `<execution_parameters><STRICTNESS_CALIBRATION>...ohje...</STRICTNESS_CALIBRATION></execution_parameters>`.

### 5. Portaittainen asennekalibrointi (Semantic Categories)

Jotta vältämme tekoälyn "pseudomatiikan" hallusinaatiot, toteuta `calibrate_strictness`-funktio siten, että numeerinen skaala (0-100) koodataan viiteen kielelliseen asennekategoriaan. Käytä täsmälleen alla olevia ohjeistuksia asettaaksesi rajat sille, mitä `EvidenceType`-valintoja LLM saa käyttää:

*   **Taso 0 (Absolute Leniency):** "STRICTNESS CALIBRATION (0/100): Absolute Leniency. You must be extremely generous and forgiving. Assume the best possible intent. You are permitted to use `EvidenceType.IMPLIED_INTENT` if an explicit quote is missing but the context heavily implies the truth. However, you must provide a rigorous justification."
*   **Tasot 1–29 (Lenient):** "STRICTNESS CALIBRATION ({val}/100): Lenient. Be generally forgiving of minor errors and focus on the positive aspects of the input. You may use `EvidenceType.IMPLIED_INTENT` only if strongly supported by surrounding context."
*   **Tasot 30–69 (Balanced):** "STRICTNESS CALIBRATION ({val}/100): Balanced. Evaluate fairly and neutrally. `EvidenceType.IMPLIED_INTENT` should be used sparingly and only with exhaustive justification."
*   **Tasot 70–99 (Strict):** "STRICTNESS CALIBRATION ({val}/100): Strict. You must be highly critical and demanding. CRITICAL: At this strictness level, the use of `EvidenceType.IMPLIED_INTENT` is STRICTLY FORBIDDEN. If you cannot find a verbatim `EXPLICIT_QUOTE`, you must select `NO_EVIDENCE` and set boolean to false."
*   **Taso 100 (Absolute Strictness):** "STRICTNESS CALIBRATION (100/100): Absolute Strictness. You are an unforgiving auditor. Any deviation from perfection MUST be heavily penalized. `EvidenceType.IMPLIED_INTENT` is STRICTLY FORBIDDEN. If you cannot find a verbatim `EXPLICIT_QUOTE`, you must select `NO_EVIDENCE` and set boolean to false."

Tämä ratkaisu pitää UI:n matemaattisena (helppo säädin), pakkaa dynaamisen asenteen token-jonon loppuun välimuistin säästämiseksi (Prompt Caching), ohjaa mallin Enum-valintaa proaktiivisesti ja nojaa lopulta Pydanticin Fail-Fast -turvaverkkoihin.

---

### 6. Backend: Välimuistin invalidointi (Cache Key Hashing)

Päivitä tulosvälimuistin (`execution_cache`) logiikka vastaamaan dynaamista tiukkuutta:

*   **Tiivisteen muodostus (Hash Generation):** Koska sama lähdeteksti ja arvioitava väite (`Atom`) tuottavat täysin erilaisen tuloksen tiukkuudesta riippuen, sisällytä `strictness_level` pakollisena parametrinä välimuistiavaimen kryptografiseen tiivisteeseen (esim. SHA-256).
*   **Välimuistin vuotamisen esto (Cache Contamination):** Vältä vaaralliset "Cache Hit" -virheet (joissa tason 100 vaatimus palauttaisi vahingossa aiemman tason 10 tuloksen) rakentamalla välimuistiavain aina kaavalla: `hash(document_id + atom_id + prompt_version + strictness_level)`.

---

## Konkreettinen JSON-esimerkki: Kognitiivinen kitka käytännössä

Varmista, että toteutus tuottaa seuraavanlaisia tuloksia. Esimerkit havainnollistavat, miten asennekategoria ohjaa LLM:n Pydantic-tulostetta (`AtomResponse`).

* **Lähdeteksti:** *"Yhtiön tavoitteena on vähentää päästöjä seuraavan vuosikymmenen aikana. Olemme myös perustaneet komitean tutkimaan aurinkopaneelien asennusta."*
* **Arvioitava väite (Atom):** *"Yhtiö on siirtynyt täysin 100 % uusiutuvan energian käyttöön."*

### Tulos 1: Tiukka asetus (Strictness 100)
Malli omaksuu roolin *"unforgiving auditor"*. Se rankaisee hypettämisestä ja vaatii täydellistä loogista vastaavuutta.

```json
{
  "evidence_type": "EXPLICIT_QUOTE",
  "quote": "Yhtiön tavoitteena on vähentää päästöjä... perustaneet komitean tutkimaan",
  "implicit_justification": null,
  "reasoning": "Väite vaatii, että yhtiö on JO siirtynyt TÄYSIN (100 %) uusiutuvaan energiaan. Teksti mainitsee ainoastaan 'tavoitteen' ja 'tutkimisen'. Nämä ovat tulevaisuuden aikomuksia, eivät todisteita toteutuneesta 100 % siirtymästä. Looginen epäsuhta on massiivinen.",
  "boolean": false
}
```

### Tulos 2: Lempeä asetus (Strictness 10 - Lenient)
Malli omaksuu roolin *"Assume the best possible intent"*. Se käyttää "Laiskuuden estoprotokollan" suomaa `IMPLIED_INTENT` -pakoventtiiliä perusteelliseen tulkintaan, antaakseen väitteelle hyväksynnän ("Benefit of the Doubt").

```json
{
  "evidence_type": "IMPLIED_INTENT",
  "quote": null,
  "implicit_justification": "IMPLICIT HIT: Vaikka yhtiö ei ole vielä saavuttanut 100 % rajaa, teksti osoittaa erittäin vahvaa strategista tahtotilaa ja aktiivisia toimenpiteitä (komitea, aurinkopaneelit) uusiutuvan energian puolesta.",
  "reasoning": "Koska ohjeistuksena on antaa täysi 'benefit of the doubt', tulkitsen yhtiön olevan henkisesti siirtynyt uusiutuvan energian tielle.",
  "boolean": true
}
```

Näiden vertailu osoittaa kehittäjille, että tiukkuus ei ole vain laskennallinen backend-kynnys, vaan aito kognitiivinen muutos tekoälyn suorittamassa Micro-CoT -päättelyssä.

