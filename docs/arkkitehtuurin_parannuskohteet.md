# Arkkitehtuurin ja Tietomallien Parannuskohteet

Tähän dokumenttiin kerätään järjestelmän koodikannassa, tietomalleissa ja orkestraatiossa havaittuja pieniä ja keskisuuria parannuskohteita, refaktorointitarpeita sekä arkkitehtuurisia selkeytyksiä.

---

## Luku 1: Matriisikohtainen vs. Workflow-tason skaalaus (`scale_min` / `scale_max`)

### 1.1 Nykytilanne ja havaittu ongelma
Tietokannassa ([`backend_v2/seed/seed_data.json`](file:///c:/src/quorum/backend_v2/seed/seed_data.json)) ja domain-mallissa ([`backend_v2/models/v2_core.py:PromptBlock`](file:///c:/src/quorum/backend_v2/models/v2_core.py#L376-L460)) matriiseille on määritelty staattiset kentät:
```json
"scale_min": 1,
"scale_max": 5
```

Samaan aikaan jokaisella matriisilla on `scales`-taulukko ([`MatrixScale`](file:///c:/src/quorum/backend_v2/models/v2_core.py#L354-L374)), joka sisältää kunkin arvosanatason (esim. 1, 2, 3, 4, 5) kognitiiviset BARS-väitteet ja kriteerit. Järjestelmän invariantti `mathematical_extrema_anchoring` laskee automaattisesti näiden perusteella kentät `computed_min` ja `computed_max`.

Lisäksi esityskerroksen profiilissa ([`OutputProfile`](file:///c:/src/quorum/backend_v2/models/v2_core.py#L1290-L1360)) on kenttä `display_scale`, jonka vaihtoehdot ovat:
* `ORIGINAL` (käyttää kunkin matriisin omaa asteikkoa)
* `NORMALIZED_100` (normalisoi kaikki arvot välille 0–100 %)
* `CUSTOM` (käyttää matriisin `scale_min`/`scale_max` -arvoja)

### 1.2 Miksi matriisikohtainen esitysskaalaus on ongelmallinen?

1. **Kognitiivinen pirstaleisuus loppuraportissa (Incommensurability):**
   * Jos yhdessä workflow'ssa Matriisi A on skaalattu välille $1–5$ ja Matriisi B välille $4–10$, loppukäyttäjä näkee samassa raportissa toisistaan poikkeavia pistearvoja, joita ei voi vertailla suoraan keskenään.
   * Arvosana $4.0$ on toisessa matriisissa erinomainen tulos (4/5) ja toisessa hylätty (4/10).

2. **Kokonaisarvosanan laskenta ja esittäminen:**
   * Workflow'n tuottama kokonaisarvosana (`total_score` / `workflow_score`) vaatii aina normalisoidun yhteisen asteikon. Jos matriisit skaalataan toisistaan riippumattomasti, workflow-tason kokonaispisteelle ei ole luontaista asteikkoa ilman erillistä määrittelyä.

3. **Kaavioiden ja visualisointien vääristymät:**
   * 2D-scatter-matriiseissa ([`static_charts.py`](file:///c:/src/quorum/backend_v2/utils/static_charts.py), [`logic_matrix_chart.dart`](file:///c:/src/quorum/client_app_v2/lib/shared/widgets/logic_matrix_chart.dart)) ja tutkakaavioissa eri akseleiden vertailu edellyttää, että akseleilla on yhtenevät tai normalisoidut ääripäät.

4. **Vastuualueiden sekoittuminen (Separation of Concerns):**
   * **Matriisi (Rubriikki / Sensori):** Matriisin ainoa tehtävä on arvioida sisältöä omien BARS-kriteeriensä perusteella (esim. tasot 1–5). Matriisin ei tule tietää, missä asiakaskontekstissa tai millä loppuesitysasteikolla sen tulos halutaan raportoida.
   * **Workflow & OutputProfile (Esityskonteksti):** Raportti ja sen kohdeyleisö määrittelevät esitysasteikon (esim. *"Tämä johdon arviointiraportti esitetään 4–10 kouluarvosana-asteikolla"* tai *"0–100 % indeksinä"*).

5. **Datan redundanssi ja synkronointiriskit:**
   * Staattiset `scale_min` ja `scale_max` matriisitasolla toistavat vain `scales`-taulukon minimi- ja maksimiarvoja. Jos `scales`-kriteerejä muutetaan, staattiset arvot voivat jäädä epäsynkroniin.

---

### 1.3 Suositeltu tavoitearkkitehtuuri

```
+-----------------------------------------------------------------------+
| 1. MATRIISITASO (PromptBlock)                                         |
|    - Sisältää vain luontaiset BARS-tasot (scales: [1, 2, 3, 4, 5])     |
|    - computed_min / computed_max johdetaan dynaamisesti               |
|    - Poistetaan staattiset redundantit scale_min / scale_max          |
+-----------------------------------------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------+
| 2. MATEMAATTINEN AGGREGAATIO (Scoring Engines)                        |
|    - Kaikki matriisit normalisoidaan välille [0.0, 1.0] / [0-100]     |
|    - Lasketaan yhteismitalliset painotetut keskiarvot ja XAI-metriikat|
+-----------------------------------------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------+
| 3. ESITYS- JA RAPORTTITASO (Workflow / OutputProfile)                 |
|    - display_scale määrittää koko workflow'n esitystavan:             |
|        a) ORIGINAL: Kunkin matriisin oma BARS-asteikko                |
|        b) NORMALIZED_100: Kaikki tulokset 0-100 %                     |
|        c) CUSTOM: Koko workflow'lle yhteinen kohdeväli (esim. 4 - 10)  |
|    - MatrixDomainParser projisoi sekä osamatriisit että kokonais-     |
|      arvosanan yhtenäisesti valitulle esitysasteikolle                |
+-----------------------------------------------------------------------+
```

### 1.4 Konkreettiset toimenpiteet toteutettaessa (Backlog)

1. **Domain- ja DTO-mallit ([`backend_v2/models/v2_core.py`](file:///c:/src/quorum/backend_v2/models/v2_core.py)):**
   * Siirretään `custom_scale_min` ja `custom_scale_max` tarvittaessa `OutputProfile`-malliin (tai pidetään ne profiilitason asetuksena).
   * Poistetaan `PromptBlock`-mallista vähitellen staattiset `scale_min` ja `scale_max` tarpeettomina, jolloin luotetaan yksinomaan `computed_min`- ja `computed_max`-kenttiin.
2. **Domain-parseri ([`backend_v2/services/matrix_domain_parser.py`](file:///c:/src/quorum/backend_v2/services/matrix_domain_parser.py)):**
   * Kun `display_scale == DisplayScale.CUSTOM`, kohdeasteikon rajat luetaan `OutputProfile`-tasolta eikä yksittäiseltä `PromptBlockilta`.
3. **Frontend-mallit ([`client_app_v2`](file:///c:/src/quorum/client_app_v2)):**
   * Päivitetään vastaavat Dart/Freezed-mallit noudattamaan samaa logiikkaa (`OutputProfile` vs `PromptBlock`).
4. **Seed Vault ([`backend_v2/seed/seed_data.json`](file:///c:/src/quorum/backend_v2/seed/seed_data.json)):**
   * Siivotaan redundanssi matriisien määrittelyistä.

---

## Luku 2: Teoria-ankkurien kaksoissyöttö (`theory_grounding` vs. `ai_description`)

### 2.1 Nykytilanne ja havaittu ongelma
Tietokannassa ([`backend_v2/seed/seed_data.json`](file:///c:/src/quorum/backend_v2/seed/seed_data.json)) kaikille 13 matriisille on määritelty rinnakkain kaksi kenttää:
1. `theory_grounding`: Strukturoitu Pydantic-malli ([`TheoryGrounding`](file:///c:/src/quorum/backend_v2/models/v2_core.py#L190-L204)), joka sisältää `source_url`- ja `citation_reference`-kentät.
2. `ai_description`: Vapaamuotoinen tekstikenttä, joka sisältää sekä `OBJECTIVE:`- että `EPISTEMIC ANCHOR:` -osiot.

Esimerkki matriisista `matrix_archivist` ([`seed_data.json:L2654-2660`](file:///c:/src/quorum/backend_v2/seed/seed_data.json#L2654-L2660)):
```json
"theory_grounding": {
    "source_url": "https://www.arma.org/page/principles",
    "citation_reference": "ARMA International. (2014). Generally Accepted Recordkeeping Principles. ARMA International."
},
"ai_description": "OBJECTIVE:\nEvaluate strict adherence to operational guidelines, verifiable provenance, and structural integrity based on established archival frameworks.\nEPISTEMIC ANCHOR:\nARMA International. 'Generally Accepted Recordkeeping Principles (The Principles).' A framework ensuring organizational Accountability, Transparency, Integrity, Protection, Compliance, Availability, Retention, and Disposition."
```

Kun DAG-pohjainen sensoriekskutio ([`backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py`](file:///c:/src/quorum/backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L50-L76)) kokoaa staattista järjestelmäkehitetta, se lisää kummankin erillisinä `<STATIC_INSTRUCTION>` -lohkoina:
```xml
<!-- LOHKO 1: ai_description (sisältää vapaamuotoisen tekstin ja EPISTEMIC ANCHOR -osion) -->
<STATIC_INSTRUCTION label="blk_2222222222222222">
OBJECTIVE:
Evaluate strict adherence to operational guidelines, verifiable provenance, and structural integrity based on established archival frameworks.
EPISTEMIC ANCHOR:
ARMA International. 'Generally Accepted Recordkeeping Principles (The Principles).' A framework ensuring organizational Accountability, Transparency, Integrity, Protection, Compliance, Availability, Retention, and Disposition.
</STATIC_INSTRUCTION>

<!-- LOHKO 2: theory_grounding (raakana JSON-dumpina) -->
<STATIC_INSTRUCTION label="blk_3333333333333333">
{"source_url": "https://www.arma.org/page/principles", "citation_reference": "ARMA International. (2014). Generally Accepted Recordkeeping Principles. ARMA International."}
</STATIC_INSTRUCTION>
```

**Seuraus:** LLM saa täsmälleen saman kirjallisuusviitteen järjestelmäviestissään tuplana kahdessa eri muodossa.

### 2.2 Miksi tämä on ongelmallista?

1. **Huomion hajaantuminen (Attention Dilution) ja token-hukka:**
   * LLM käsittelee saman lähdeviitteen kahteen kertaan peräkkäisissä säännöissä, mikä kuluttaa turhaan kognitiivista kaistanleveyttä ja staattista token-tilaa.
2. **Raaka JSON järjestelmäohjeena:**
   * `theory_grounding.model_dump_json()` injektoi raakaa JSON-tekstiä suoraan sääntöjen sekaan ilman semanttista XML-kehystä. LLM voi tulkita raa'an JSONin mallivastaukseksi tai datalohkoksi pikemminkin kuin ohjesäännöksi.
3. **Single Source of Truth (SSOT) -rikkomus tietomallissa:**
   * Sama teoriaviite on tallennettu kahteen paikkaan samassa `PromptBlock`-oliossa. Jos kehittäjä päivittää `theory_grounding`-kentän, `ai_description`-teksti jää helposti vanhaan tilaan (tai päinvastoin), mikä aiheuttaa semanttisen ajautumisen (Semantic Drift) riskin.
4. **Strukturoitu vs. vapaamuotoinen data:**
   * Frontend (`client_app_v2`) ja XAI-laajennukset (`theory_link`, [`xai_highlights_adapter.py`](file:///c:/src/quorum/backend_v2/services/sdui/adapters/xai_highlights_adapter.py)) tarvitsevat nimenomaan strukturoitua `theory_grounding`-mallia näyttääkseen käyttäjälle klikattavan lähdelinkin ja kirjan kuvakkeen. `ai_description`-kentän sisällä oleva teksti on frontendille saavuttamatonta.

---

### 2.3 Suositeltu tavoitearkkitehtuuri

```
+-----------------------------------------------------------------------------------+
| 1. TIETOMALLIN TYÖNJAON SELKEYTYS (seed_data.json)                                |
|    - ai_description: Sisältää VAIN tavoitteen ja arviointilogiikan (OBJECTIVE:)  |
|    - theory_grounding: Ainoa virallinen totuuden lähde lähdeviitteelle           |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 2. PROMPT-KOKOAJAN SIISTIMINEN (matrix_sensor_prompt_builder.py)                 |
|    - Injektoidaan siisti semanttinen XML-lohko raa'an JSON-dumpin sijaan:         |
|      <theory_context source="https://...">                                        |
|        ARMA International. (2014). Generally Accepted Recordkeeping Principles.   |
|      </theory_context>                                                            |
+-----------------------------------------------------------------------------------+
```

### 2.4 Konkreettiset toimenpiteet toteutettaessa (Backlog)

1. **Prompt-kokoaja ([`backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py`](file:///c:/src/quorum/backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py)):**
   * Korvataan `theory_grounding.model_dump_json()` semanttisella muotoilulla (esim. `<theory_context source="...">...</theory_context>`).
2. **Seed Vault ([`backend_v2/seed/seed_data.json`](file:///c:/src/quorum/backend_v2/seed/seed_data.json)):**
   * Siivotaan `EPISTEMIC ANCHOR:` -tekstit pois kaikkien 13 matriisin `ai_description`-kentistä, jolloin `ai_description` sisältää vain `OBJECTIVE:`-osion ja `theory_grounding` hoitaa ankkuroinnin.

---

## Luku 3: `I18nText`-rakenteen `default_locale`-kentän redundanssi

### 3.1 Nykytilanne ja havaittu ongelma
Tietokannassa ([`backend_v2/seed/seed_data.json`](file:///c:/src/quorum/backend_v2/seed/seed_data.json)) on tasan **500 kappaletta** `I18nText`-rakenteita ([`backend_v2/models/v2_core.py:I18nText`](file:///c:/src/quorum/backend_v2/models/v2_core.py#L97-L146)), joissa jokaisessa toistetaan eksplisiittisesti `default_locale`:
```json
"name": {
    "default_locale": "fi",
    "translations": {
        "fi": "Käyttäjä:",
        "en": "User:"
    }
}
```

Samaan aikaan järjestelmän monikielisyysarkkitehtuurissa esityskieli määräytyy aina **ajonaikaisesta kontekstista**:
1. Käyttäjän käyttöliittymäkielestä (UI Locale / `Accept-Language`).
2. Raportin/profiilin kieliasetuksesta (`OutputProfile.language` / `Execution.target_locale`).
3. Järjestelmän globaalista varakielestä (`en`), jonka olemassaolon Pydantic-validaattori vaatii aina.

### 3.2 Miksi kenttäkohtainen `default_locale` on ongelmallinen ja turha?

1. **Vastuualueiden sekoittuminen (Separation of Concerns):**
   * Yksittäinen tekstipätkä tietomallissa on vain **käännössanakirja** (`translations: {"fi": "...", "en": "..."}`). Se ei tiedä kuka sitä lukee.
   * Oletuskieli tai varakieli (fallback) on sovellus-, profiili- tai käyttäjätason asetus, ei yksittäisen tekstin staattinen ominaisuus.
2. **Validaation sisäinen ristiriita:**
   * `I18nText.validate_i18n()` vaatii jo nyt, että englanninkielinen (`en`) käännös on aina pakollinen teknisenä varakielenä. Siten kenttäkohtainen `"default_locale": "fi"` on ristiriidassa järjestelmän globaalin fallback-käyttäytymisen kanssa.
3. **Datamassan kohina ja JSON-koko:**
   * Kenttä toistuu 500 kertaa `seed_data.json`:ssa sekä kymmenissä Flutter- ja Python-testifiktioissa (`defaultLocale: 'en'`), mikä kasvattaa turhaan tietomallien, API-DTO:iden ja tietokannan kokoa.

---

### 3.3 Suositeltu tavoitearkkitehtuuri

```
+-----------------------------------------------------------------------------------+
| 1. PUHDAS KÄÄNNÖSSÄILIÖ (I18nText)                                                |
|    - Sisältää vain kielikoodit ja käännöstekstit (translations: {"fi":.., "en":..})|
|    - Poistetaan redundantti default_locale -metatieto                             |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 2. KONTEKSTIPOHJAINEN RESOLVOINTI (I18nText.resolve)                             |
|    - resolve(target_locale: str | None = None, fallback_locale: str = "en")       |
|    - Kohdekieli luetaan käyttäjä-/profiilikontekstista                            |
|    - Jos käännös puuttuu, pudotaan globaaliin fallbackiin ("en")                 |
+-----------------------------------------------------------------------------------+
```

### 3.4 Konkreettiset toimenpiteet toteutettaessa (Backlog)

1. **Python Domain -mallit ([`backend_v2/models/v2_core.py`](file:///c:/src/quorum/backend_v2/models/v2_core.py)):**
   * Poistetaan `default_locale` -kenttä `I18nText`-mallista (tai tehdään siitä valinnainen defaulttina `"en"` siirtymävaiheessa).
   * Päivitetään `resolve(target_locale, fallback_locale="en")` käyttämään parametrina annettua varakieltä.
2. **Flutter Client -mallit ([`client_app_v2/lib/shared/models/i18n_text.dart`](file:///c:/src/quorum/client_app_v2/lib/shared/models/i18n_text.dart)):**
   * Poistetaan `defaultLocale` Freezed-mallista ja päivitetään `get(langCode)` käyttämään sovelluksen oletuskieltä.
3. **Seed Vault ([`backend_v2/seed/seed_data.json`](file:///c:/src/quorum/backend_v2/seed/seed_data.json)):**
   * Siivotaan 500 kappaletta `"default_locale"` -rivejä pois, jolloin tiedosto kevenee ja selkeytyy.

---

## Luku 4: Atomin kognitiivisen ohjeistuksen hajautuminen (`MatrixClaim.ai_description` vs. `TDAAssertion.concept_description`)

### 4.1 Nykytilanne ja havaittu ongelma
Tietokannassa ([`backend_v2/seed/seed_data.json`](file:///c:/src/quorum/backend_v2/seed/seed_data.json)) on 152 väitettä ([`MatrixClaim`](file:///c:/src/quorum/backend_v2/models/v2_core.py#L320-L338)) ja tasan 152 TDA-assertiota ([`TDAAssertion`](file:///c:/src/quorum/backend_v2/models/v2_core.py#L222-L290)). Jokainen väite sisältää 1:1 yhden TDA-assertion.

Tietomallissa ohjetekstit jakautuvat kuitenkin kahdelle eri tasolle:
```json
{
    "label": {
        "translations": { "fi": "Absoluuttinen varmuus...", "en": "Absolute certainty..." }
    },
    "ai_description": "EXTRACT a probabilistic or subjective statement presented as an absolute 100% fact without any Qualifiers.",
    "tda_assertions": [
        {
            "tda_id": "tda_d9cb646741ba4750ab561bf766c94f03",
            "concept_description": "",
            "anti_patterns": [
                {
                    "pattern": "it states a mathematical/historical fact",
                    "allows_contextual_excuse": false
                }
            ]
        }
    ]
}
```

Koko tietokannan auditointi osoittaa:
* **70 tapauksessa** `TDAAssertion.concept_description` on täysin tyhjä merkkijono `""`, ja poimintaohje sijaitsee vain vanhassa `MatrixClaim.ai_description` -kentässä.
* **82 tapauksessa** ohjeteksti on kirjattu *molemmille* tasoille, mutta ne ovat **eriytyneet toisistaan** (sisältävät toisistaan poikkeavia sääntöjä samalle atomille).

---

### 4.2 Kooditason vaikutusanalyysi ja löydetyt ristiriidat (Pipeline Forensics)

Kooditarkastelu paljasti, miten tämä hajautuminen aiheuttaa konkreettisia toiminnallisia vikoja ja kehoteristiriitoja:

#### A. Tuotantokehotteen rikkoutuminen (Tyhjä `<question>` -lohko)
1. **Litistyskoukku ([`backend_v2/hooks/atom_flattening.py:133`](file:///c:/src/quorum/backend_v2/hooks/atom_flattening.py#L133)):** Poimii atomin kysymykseksi vain `tda.concept_description.strip()`.
2. Koska 70 atomilla `concept_description` on tyhjä `""`, DTO:n [`FlattenedAtom.question`](file:///c:/src/quorum/backend_v2/models/dtos/engine.py#L21) saa arvoksi tyhjän merkkijonon.
3. **Prompt-kokoaja ([`backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py:141-143`](file:///c:/src/quorum/backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L141-L143)):** Generoi LLM:lle menevään XML-kehotteeseen:
   ```xml
   <claim alias="a0">
     <question>
     <![CDATA[]]>   <!-- TÄYSIN TYHJÄ! -->
     </question>
     <extraction_rule>
     <![CDATA[no empirical data or external reference exists in the same paragraph.]]>
     </extraction_rule>
   </claim>
   ```
   **Seuraus:** LLM ei koskaan saa `MatrixClaim.ai_description` -kentässä olevaa kysymystä/direktiiviä, vaan joutuu arvailemaan poimintakohdetta pelkän `<extraction_rule>` -lisäsäännön perusteella.

#### B. "Split-Brain" Studio-simulaation ja tuotannon välillä
* **Tuotantoajo ([`atom_flattening.py`](file:///c:/src/quorum/backend_v2/hooks/atom_flattening.py)):** Lukee `tda.concept_description` -kenttää.
* **Studio-simulaatio ([`backend_v2/services/studio/simulation_service.py:181-182`](file:///c:/src/quorum/backend_v2/services/studio/simulation_service.py#L181-L182)):** Lukee `claim.ai_description` -kenttää (`rendered += f"  Rule: {claim.ai_description.strip()}\n"`).
* **Seuraus:** Kun käyttäjä testaa matriisia Studiossa, simulaatio testaa eri kehotetta kuin mitä oikea tuotantomoottori suorittaa!

#### C. Kontekstin spatiaalinen leikkaus ([`backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py:153`](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L153))
* `ContextBuilder._collect_rule_descriptions()` etsii vaiheohjeita (`before phase X`) vain `tda.concept_description` -kentästä. Koska kenttä on 70 atomilla tyhjä, spatiaalinen leikkaus ei aktivoidu, vaikka `claim.ai_description` sisältäisi vaihemäärityksiä.

---

### 4.3 Suositeltu tavoitearkkitehtuuri

```
+-----------------------------------------------------------------------------------+
| 1. IHMISLUETTAVA VÄITE (MatrixClaim)                                              |
|    - label: I18nText (Käyttöliittymässä näkyvä BARS-väite)                        |
|    - tda_assertions: list[TDAAssertion] (Kytkentä testattaviin sääntöihin)        |
|    - Poistetaan redundantti ja virheitä aiheuttava ai_description                 |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 2. TEKOÄLYN TESTATTAVA SÄÄNTÖ (TDAAssertion - Ainoa SSOT)                         |
|    - concept_description: Konseptin määritelmä ja päädirektiivi                   |
|    - extraction_rule: Varsinainen poimintasääntö                                  |
|    - acceptance_criteria & anti_patterns: Strukturoidut kriteerit                 |
+-----------------------------------------------------------------------------------+
```

### 4.4 Konkreettiset toimenpiteet toteutettaessa (Backlog)

1. **Seed Vault -migraatio ([`backend_v2/seed/seed_data.json`](file:///c:/src/quorum/backend_v2/seed/seed_data.json)):**
   * Kopioidaan kaikissa 70:ssä tyhjässä tapauksessa `MatrixClaim.ai_description` suoraan kenttään `TDAAssertion.concept_description`.
   * Vahvistetaan ja yhdistetään 82 eriytynyttä tapausta `TDAAssertion`-tasolle.
2. **Koodikannan harmonisointi:**
   * Poistetaan `MatrixClaim.ai_description` domain-malleista ([`backend_v2/models/v2_core.py`](file:///c:/src/quorum/backend_v2/models/v2_core.py)) ja Flutter-malleista.
   * Korjataan [`simulation_service.py`](file:///c:/src/quorum/backend_v2/services/studio/simulation_service.py) lukemaan `tda.concept_description`, jotta simulaatio ja tuotanto käyttävät 100 % identtistä promptia.


---

## Luku 5: Esitysprofiilin jäänteet ja Dual-Axis Localization -päällekkäisyydet

### 5.1 Nykytilanne ja havaittu ongelma
Tietokannan raporttiprofiilissa ([`OutputProfile: prof_5d6e7f8091a2b3c4`](file:///c:/src/quorum/backend_v2/seed/seed_data.json#L9180-L9570)) esiintyy kaksi merkittävää arkkitehtuurista päällekkäisyyttä ja jännitettä:

1. **Staattiset UI-käännökset backend-tietokannassa (Kaksoiskäännökset):**
   * Profiili säilöö tietokannassa satoja rivejä staattisia käyttöliittymäotsikoita **neljässä eri sanakirjassa**:
     - `metric_mappings`: `"metadata_user": "Käyttäjä:"`, `"metadata_organization": "Organisaatio:"`, `"variance_mechanical": "Mekaaninen"`, `"variance_cognitive": "Kognitiivinen"`
     - `matrix_column_labels`: `"label": "Ulottuvuus"`, `"quotes": "Lainaukset"`, `"atomic_breakdown": "Tasojakauma"`, `"score": "Pisteet"`
     - `user_role_mappings`: `"ROLE_COACH": "Valmentaja"`, `"ROLE_EXECUTIVE": "Johtaja"`
     - `extension_labels`: `"variance_validation": "Variaation validointi"`
2. **Vanha `layouts`-taulukko vs. uusi `target_block_order`:**
   * Profiilissa on yhä 4 kpl vanhoja V1-aikaisia `layouts`-lohkoja tyhjine kenttineen (`steps: []`, `text_delivery_mode: "none"`), vaikka raportin lohkojärjestys määräytyy V2:ssa puhtaasti `target_block_order` -listasta.

---

### 5.2 Kooditason vaikutusanalyysi ja löydetyt ristiriidat

#### A. "Dumb Painter" -periaatteen rikkoutuminen ja L10n Drift ([`metadata_adapter.py:76-80`](file:///c:/src/quorum/backend_v2/services/sdui/adapters/metadata_adapter.py#L76-L80))
* Backendin adapteri muodostaa merkkijonoja liittämällä käännöksen ja arvon yhteen:
  ```python
  lbl = get_metadata_label("metadata_user")   # Hakee profiilin metric_mappings["metadata_user"]
  metadata_lines.append(f"{lbl}: {context.user_name}")  # Tulostaa: "Käyttäjä: Matti Meikäläinen"
  ```
* **Ristiriita Dual-Axis Localization -arkkitehtuurin kanssa:**
  * Quorumin perusperiaatteen mukaan backend hallinnoi vain dataa ja frontend (.arb) kaikkia staattisia UI-tekstejä.
  * Samat sanat (`"Käyttäjä"`, `"Organisaatio"`, `"Tasojakauma"`) on määritelty Flutterin [`app_fi.arb`](file:///c:/src/quorum/client_app_v2/lib/l10n/app_fi.arb) -tiedostossa.
  * Jos kääntäjä korjaa termin Flutterin `.arb`-tiedostoon, backendin tuottama raportti käyttää yhä vanhaa tietokannan `seed_data.json` -käännöstä.

#### B. `layouts`-käsitteen semanttinen harha ([`worker.py:906-930`](file:///c:/src/quorum/backend_v2/worker.py#L906-L930) ja [`matrix_graphs_adapter.py:67`](file:///c:/src/quorum/backend_v2/services/sdui/adapters/matrix_graphs_adapter.py#L67))
* Kooditarkastelu osoittaa, että `layouts` **ei toimi todellisena sivuasetteluna** (koska sivun rakenteen määrää `target_block_order`), vaan sitä käytetään kahteen erikoistarkoitukseen:
  1. **Synteesipyyntöjen laukaisu:** `worker.py` silmukoi `profile.layouts`-listaa ja lähettää LLM:lle synteesipyyntöjä (`MATRIX_2D_SYNTHESIS_DIRECTIVE`).
  2. **Matriisien ryhmittely:** `MatrixGraphsAdapter` ja `MatrixSummaryTableAdapter` lukevat `layout.target_blocks` -kenttää tietääkseen, mitkä matriisit ryhmitellään yhteen 2D-kaavioon tai taulukkoon.
* Nimi `layouts` ja sen sisällä olevat V1-kentät (`preset_view`, `text_delivery_mode`, `matrix_column_labels`, `steps: []`) ovat harhaanjohtavaa legacy-painolastia.

---

### 5.3 Suositeltu tavoitearkkitehtuuri

```
+-----------------------------------------------------------------------------------+
| 1. STRUKTUROIDUT METADATALOHKOT (Zero-Math Dumb Painter)                          |
|    - Backend lähettää data-avaimet: { key: "user", value: "Matti Meikäläinen" }   |
|    - Flutter ja PDF kääntävät otsikot suoraan omista .arb-tiedostoistaan          |
|    - Poistetaan metric_mappings, matrix_column_labels ja user_role_mappings kannasta|
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 2. PUHDAS MATRIISIRYHMITTELY (matrix_synthesis_groups)                            |
|    - target_block_order: määrää raportin lohkojärjestyksen (TargetBlockType)      |
|    - layouts korvataan puhtaalla mallilla (matrix_synthesis_groups), joka         |
|      sisältää vain ryhmän nimen (title) ja kohdematriisit (target_blocks)        |
+-----------------------------------------------------------------------------------+
```

### 5.4 Konkreettiset toimenpiteet toteutettaessa (Backlog)

1. **Lokalisaation SSOT-siivous:**
   * Poistetaan staattiset UI-sanakirjat (`metric_mappings`, `matrix_column_labels`, `user_role_mappings`, `extension_labels`) `OutputProfile`-tietokantarakenteesta ([`backend_v2/seed/seed_data.json`](file:///c:/src/quorum/backend_v2/seed/seed_data.json)).
   * Muutetaan [`MetadataAdapter`](file:///c:/src/quorum/backend_v2/services/sdui/adapters/metadata_adapter.py) lähettämään avain-arvo -pareja merkkijonoketjutuksen sijaan.
2. **Profiilimallin selkeytys ([`backend_v2/models/v2_core.py`](file:///c:/src/quorum/backend_v2/models/v2_core.py)):**
   * Korvataan legacy-kenttiä sisältävä `layouts`-taulukko kevyellä `matrix_synthesis_groups` -rakenteella ja poistetaan tarpeettomat V1-kentät (`preset_view`, `text_delivery_mode`, `steps: []`).
   * Päivitetään [`worker.py`](file:///c:/src/quorum/backend_v2/worker.py) ja adapterit käyttämään uutta puhdasta ryhmittelymallia.




