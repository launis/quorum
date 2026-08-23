# Arkkitehtuurin ja Tietomallien Parannuskohteet

Tähän dokumenttiin kerätään järjestelmän koodikannassa, tietomalleissa ja orkestraatiossa havaitut arkkitehtuuriset parannuskohteet, refaktorointitarpeet ja skeeman selkeytykset. Dokumentti on auditoitu Tier 8 System 2 First Principles -arvioinnilla ([`feature_audit_architecture_improvements.md`](file:///C:/Users/risto/.gemini/antigravity-ide/brain/c43af70a-f313-4b1a-ae3e-ceec08774a09/feature_audit_architecture_improvements.md) ja [`feature_audit_architecture_improvements_scope_hardening.md`](file:///C:/Users/risto/.gemini/antigravity-ide/brain/ea82cb8a-cbed-44ca-87bf-0108c08de960/feature_audit_architecture_improvements_scope_hardening.md)), ja se noudattaa ehdotonta *The e.g. Ban* -sääntöä, *No Hidden Scope* -periaatetta sekä Quorumin *Zero-Tolerance* -laatuvaatimusta ilman siirtymäajan purkkaratkaisuja.

---

## Luku 1: Matriisikohtainen vs. Workflow-tason skaalaus (`scale_min` / `scale_max`)

### 1.1 Nykytilanne ja havaittu ongelma
Tietokannassa ([`backend_v2/seed/seed_data.json`](file:///c:/src/quorum/backend_v2/seed/seed_data.json)) ja domain-mallissa ([`backend_v2/models/v2_core.py:PromptBlock`](file:///c:/src/quorum/backend_v2/models/v2_core.py#L376-L460)) matriiseille on määritelty staattiset kentät:
```json
"scale_min": 1,
"scale_max": 5
```

Samaan aikaan jokaisella matriisilla on `scales`-taulukko ([`MatrixScale`](file:///c:/src/quorum/backend_v2/models/v2_core.py#L354-L374)), joka sisältää kunkin kokonaislukuarvosanatason (nimenomaan ja tyhjentävästi: 1, 2, 3, 4, 5) kognitiiviset BARS-väitteet ja kriteerit. Järjestelmän invariantti `mathematical_extrema_anchoring` laskee automaattisesti näiden perusteella kentät `computed_min` ja `computed_max`.

Lisäksi esityskerroksen profiilissa ([`OutputProfile`](file:///c:/src/quorum/backend_v2/models/v2_core.py#L1290-L1360)) on kenttä `display_scale`, jonka vaihtoehdot ovat:
* `ORIGINAL` (käyttää kunkin matriisin omaa asteikkoa)
* `NORMALIZED_100` (normalisoi kaikki arvot välille 0–100 %)
* `CUSTOM` (käyttää workflow- ja profiilitason `custom_scale_min`/`custom_scale_max` -arvoja)

### 1.2 Miksi matriisikohtainen esitysskaalaus on ongelmallinen?

1. **Kognitiivinen pirstaleisuus loppuraportissa (Incommensurability):**
   * Jos yhdessä workflow'ssa Matriisi A on skaalattu välille $1–5$ ja Matriisi B välille $4–10$, loppukäyttäjä näkee samassa raportissa toisistaan poikkeavia pistearvoja, joita ei voi vertailla suoraan keskenään.
   * Arvosana $4.0$ on toisessa matriisissa erinomainen tulos (4/5) ja toisessa hylätty (4/10).

2. **Kokonaisarvosanan laskenta ja esittäminen:**
   * Workflow'n tuottama kokonaisarvosana (`total_score` / `workflow_score`) vaatii aina normalisoidun yhteisen asteikon. Jos matriisit skaalataan toisistaan riippumattomasti, workflow-tason kokonaispisteelle ei ole luontaista asteikkoa ilman erillistä määrittelyä.

3. **Kaavioiden ja visualisointien vääristymät:**
   * 2D-scatter-matriiseissa ([`static_charts.py`](file:///c:/src/quorum/backend_v2/utils/static_charts.py), [`logic_matrix_chart.dart`](file:///c:/src/quorum/client_app_v2/lib/shared/widgets/logic_matrix_chart.dart)) ja tutkakaavioissa eri akseleiden vertailu edellyttää, että akseleilla on yhtenevät tai normalisoidut ääripäät.

4. **Vastuualueiden sekoittuminen (Separation of Concerns):**
   * **Matriisi (Rubriikki / Sensori):** Matriisin ainoa tehtävä on arvioida sisältöä omien BARS-kriteeriensä perusteella (nimenomaan BARS-tasot 1–5). Matriisin ei tule tietää, missä asiakaskontekstissa tai millä loppuesitysasteikolla sen tulos halutaan raportoida.
   * **Workflow & OutputProfile (Esityskonteksti):** Raportti ja sen kohdeyleisö määrittelevät esitysasteikon (määrittäen kohdeasteikoksi `NORMALIZED_100` tai `CUSTOM` välille 4.0–10.0).

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
|        c) CUSTOM: Koko workflow'lle yhteinen kohdeväli                |
|           (määritelty kentissä custom_scale_min ja custom_scale_max)  |
|    - MatrixDomainParser projisoi sekä osamatriisit että kokonais-     |
|      arvosanan yhtenäisesti valitulle esitysasteikolle                |
+-----------------------------------------------------------------------+
```

### 1.4 Konkreettiset toimenpiteet toteutettaessa (Backlog)

1. **Domain- ja DTO-mallit ([`backend_v2/models/v2_core.py`](file:///c:/src/quorum/backend_v2/models/v2_core.py)):**
   * Siirretään `custom_scale_min` ja `custom_scale_max` eksplisiittisesti `OutputProfile`-malliin ([`v2_core.py#L1290-L1360`](file:///c:/src/quorum/backend_v2/models/v2_core.py#L1290-L1360)).
   * Poistetaan `PromptBlock`-mallista atomaarisesti staattiset `scale_min` ja `scale_max` Luvun 6 protokollan mukaisesti, jolloin luotetaan yksinomaan `computed_min`- ja `computed_max`-kenttiin ([`v2_core.py#L376-L460`](file:///c:/src/quorum/backend_v2/models/v2_core.py#L376-L460)).
2. **Domain-parseri ([`backend_v2/services/matrix_domain_parser.py`](file:///c:/src/quorum/backend_v2/services/matrix_domain_parser.py)):**
   * Kun `display_scale == DisplayScale.CUSTOM`, kohdeasteikon rajat luetaan `OutputProfile`-tasolta eikä yksittäiseltä `PromptBlockilta`.
3. **Frontend-mallit ja näkymät ([`client_app_v2`](file:///c:/src/quorum/client_app_v2)):**
   * Päivitetään vastaavat Dart/Freezed-mallit ([`client_app_v2/lib/features/studio/models/output_profile.dart`](file:///c:/src/quorum/client_app_v2/lib/features/studio/models/output_profile.dart), [`client_app_v2/lib/features/studio/models/prompt_block.dart`](file:///c:/src/quorum/client_app_v2/lib/features/studio/models/prompt_block.dart)) noudattamaan samaa logiikkaa (`OutputProfile` vs `PromptBlock`).
   * Päivitetään pisteytystabi ([`client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_scoring_tab.dart`](file:///c:/src/quorum/client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_scoring_tab.dart)) ja sen yksikkötestit ([`profile_scoring_tab_test.dart`](file:///c:/src/quorum/client_app_v2/test/features/studio/views/widgets/profile/tabs/profile_scoring_tab_test.dart)).
4. **Seed Vault ([`backend_v2/seed/seed_data.json`](file:///c:/src/quorum/backend_v2/seed/seed_data.json)):**
   * Siivotaan redundanssi matriisien määrittelyistä Luvun 6 atomaarisen siemenmigraation mukaisesti.
5. **Testifikstuurien skriptattu päivitys:**
   * Päivitetään yli 100 yksikkötestiviittausta ([`test_static_charts.py`](file:///c:/src/quorum/backend_v2/tests/unit/utils/test_static_charts.py), [`test_matrix_domain_parser.py`](file:///c:/src/quorum/backend_v2/tests/unit/services/test_matrix_domain_parser.py)) poistamaan `scale_min`/`scale_max` -parametrit `PromptBlock`-alustuksista.
   * Päivitetään Flutter-testit ([`output_profile_crud_view_test.dart`](file:///c:/src/quorum/client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart), [`block_card_registry_test.dart`](file:///c:/src/quorum/client_app_v2/test/features/studio/views/widgets/profile/blocks/block_card_registry_test.dart)).

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

### 2.3 Suositeltu tavoitearkkitehtuuri: Episteeminen eriyttämisparadigma (Epistemic Separation Paradigm)

```
+-----------------------------------------------------------------------------------+
| 1. TIETOMALLIN TYÖNJAON SELKEYTYS (seed_data.json)                                |
|    - ai_description: Sisältää VAIN tavoitteen ja arviointilogiikan (OBJECTIVE:)  |
|    - theory_grounding: Ainoa virallinen totuuden lähde lähdeviitteelle (SSOT)    |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 2. LLM-KEHOTTEIDEN KOKOOJA (Prompt Builder)                                       |
|    - Standardikehotteet (system_rule, agent_role, task_definition):              |
|      -> Syötetään VAIN ai_description (ei bibliografista kohinaa tai URL-linkkejä)|
|    - Matriisikehotteet (category_id: "matrix"):                                   |
|      -> Injektoidaan siisti semanttinen XML-tekstiviite ilman URL-tokenikuormaa: |
|         <theory_context>                                                          |
|           ARMA International. (2014). Generally Accepted Recordkeeping Principles.|
|         </theory_context>                                                         |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 3. ESITYSKERROS (Flutter UI & PDF-raportit)                                       |
|    - source_url & citation_reference luetaan TheoryGrounding-oliosta              |
|    - Tarjoaa klikattavat hyperlinkit selaimessa ja virallisen lähdeluettelon      |
+-----------------------------------------------------------------------------------+
```

### 2.4 Konkreettiset toimenpiteet toteutettaessa (Backlog)

1. **Prompt-kokoaja ([`backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py`](file:///c:/src/quorum/backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py)):**
   * Korvataan `theory_grounding.model_dump_json()` puhtaalla semanttisella tekstiviitemuotoilulla: `<theory_context>\n{citation_reference}\n</theory_context>`. URL-osoite (`source_url`) jätetään LLM-kehotteesta pois ja varataan esityskerrokselle.
2. **Seed Vault ([`backend_v2/seed/seed_data.json`](file:///c:/src/quorum/backend_v2/seed/seed_data.json)):**
   * Siivotaan `EPISTEMIC ANCHOR:` -tekstit pois kaikkien 13 matriisin `ai_description`-kentistä Luvun 6 atomaarisen skriptin avulla, jolloin `ai_description` sisältää vain `OBJECTIVE:`-osion ja `theory_grounding` toimii SSOT-viitteenä.
3. **Prompt- ja sensori-yksikkötestit:**
   * Päivitetään yksikkötestit ([`test_matrix_sensor_prompt_builder.py`](file:///c:/src/quorum/backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py)) assertoimaan puhdasta `<theory_context>` -XML-rakennetta raa'an JSON-merkkijonon tai URL-injektioiden sijasta.
4. **AST- ja skeema-guardrailit:**
   * Luodaan `test_ast_theory_grounding_guardrails.py` estämään `EPISTEMIC ANCHOR:` -duplikaattien synty ja varmistamaan, ettei `model_dump_json()` -kutsuja päädy kehotteisiin.

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
   * Kenttä toistuu 500 kertaa `seed_data.json`:ssa sekä yli 1300:ssa Flutter- ja Python-testifiktioissa (`defaultLocale: 'en'`), mikä kasvattaa turhaan tietomallien, API-DTO:iden ja tietokannan kokoa.

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
   * Poistetaan `default_locale` -kenttä `I18nText`-mallista.
   * Päivitetään `resolve(target_locale, fallback_locale="en")` käyttämään parametrina annettua varakieltä ilman mallitason kenttää.
2. **Flutter Client -mallit ([`client_app_v2/lib/shared/models/i18n_text.dart`](file:///c:/src/quorum/client_app_v2/lib/shared/models/i18n_text.dart)):**
   * Poistetaan `defaultLocale` Freezed-mallista ja päivitetään `get(langCode)` käyttämään sovelluksen oletuskieltä.
3. **Seed Vault ([`backend_v2/seed/seed_data.json`](file:///c:/src/quorum/backend_v2/seed/seed_data.json)):**
   * Siivotaan 500 kappaletta `"default_locale"` -rivejä pois Luvun 6 atomaarisen skriptin avulla.
4. **Yksikkötestifikstuurien AST/regex-migraatio ([`backend_v2/tests/`](file:///c:/src/quorum/backend_v2/tests)):**
   * Ajetaan Luvun 6 skripti B, joka siivoaa `default_locale`-avaimet pois kaikista yli 1300 testitapauksesta ([`test_worker.py`](file:///c:/src/quorum/backend_v2/tests/unit/test_worker.py), [`test_worker_synthesis.py`](file:///c:/src/quorum/backend_v2/tests/unit/test_worker_synthesis.py), [`test_workflows.py`](file:///c:/src/quorum/backend_v2/tests/unit/test_workflows.py)).

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
* **Studio-simulaatio ([`backend_v2/services/studio/simulation_service.py:181-182`](file:///c:/src/quorum/backend_v2/services/studio/simulation_service.py#L181-L182)):** Lukee `claim.ai_description` -kenttää duck-typingilla `getattr(claim, "ai_description", None)`.
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
   * Kopioidaan kaikissa 70:ssä tyhjässä tapauksessa `MatrixClaim.ai_description` suoraan kenttään `TDAAssertion.concept_description` ennen kentän poistamista.
   * Vahvistetaan ja yhdistetään 82 eriytynyttä tapausta `TDAAssertion`-tasolle.
2. **Koodikannan ja mallien harmonisointi:**
   * Poistetaan `MatrixClaim.ai_description` domain-malleista ([`backend_v2/models/v2_core.py#L320-L338`](file:///c:/src/quorum/backend_v2/models/v2_core.py#L320-L338)) ja Flutterin Freezed-malleista ([`client_app_v2/lib/features/studio/models/prompt_block.dart#L151-L180`](file:///c:/src/quorum/client_app_v2/lib/features/studio/models/prompt_block.dart#L151-L180)).
   * Korjataan [`simulation_service.py:181-182`](file:///c:/src/quorum/backend_v2/services/studio/simulation_service.py#L181-L182) poistamaan `getattr` ja lukemaan suoraan `tda.concept_description`, jotta simulaatio ja tuotanto käyttävät 100 % identtistä promptia.
3. **Testifikstuurien päivitys ([`test_blueprint.py`](file:///c:/src/quorum/backend_v2/tests/unit/services/test_blueprint.py)):**
   * Päivitetään yli 350 testitapausta, jotka alustavat `MatrixClaim.ai_description` -kenttää, käyttämään suoraan `TDAAssertion.concept_description` -kenttää.

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
2. **Profiilimallin ja adapterien selkeytys:**
   * Korvataan legacy-kenttiä sisältävä `layouts`-taulukko kevyellä `matrix_synthesis_groups` -rakenteella ([`backend_v2/models/v2_core.py#L1290-L1380`](file:///c:/src/quorum/backend_v2/models/v2_core.py#L1290-L1380)) ja poistetaan tarpeettomat V1-kentät (`preset_view`, `text_delivery_mode`, `steps: []`).
   * Päivitetään vastaava Flutter Freezed -malli ([`client_app_v2/lib/features/studio/models/output_profile.dart`](file:///c:/src/quorum/client_app_v2/lib/features/studio/models/output_profile.dart)), asettelutabi ([`client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart`](file:///c:/src/quorum/client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart)) ja sen testit ([`profile_layouts_tab_test.dart`](file:///c:/src/quorum/client_app_v2/test/features/studio/views/widgets/profile/tabs/profile_layouts_tab_test.dart)).
   * Päivitetään [`worker.py:906-930`](file:///c:/src/quorum/backend_v2/worker.py#L906-L930) ja adapterit ([`backend_v2/services/sdui/adapters/matrix_graphs_adapter.py`](file:///c:/src/quorum/backend_v2/services/sdui/adapters/matrix_graphs_adapter.py), [`backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py`](file:///c:/src/quorum/backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py)) käyttämään uutta puhdasta ryhmittelymallia.

---

## Luku 6: Atomaarinen Data-, Testifikstuuri- ja Mallimigraatio (Atomic Migration Protocol)

### 6.1 Arkkitehtuurinen riski: `extra='forbid'` ja testifikstuurien laajuus
Kaikki Quorumin Pydantic V2 -mallit ([`backend_v2/models/v2_core.py`](file:///c:/src/quorum/backend_v2/models/v2_core.py)) ajetaan tiukalla `ConfigDict(strict=True, extra='forbid')` -asetuksella. Samoin Flutterin Freezed-mallit vaativat 100 % vastaavuuden API-avainten kanssa ilman hiljaisia ohituksia.

Jos kenttiä (`scale_min`, `scale_max`, `default_locale`, `ai_description`, `metric_mappings`, `layouts`) poistetaan tietomalleista ennen kuin testidata ja siemendata on päivitetty:
1. **1339+ testifikstuuria** kaatuu välittömästi `ValidationError: Extra inputs are not permitted` -virheeseen.
2. Kehittäjä tai agentti ajautuu helposti rikkomaan sääntöjä lisäämällä purkkaratkaisuja (`extra='ignore'`, `@model_validator(mode="before")` tai `.get()` -fallbäkkejä).
3. Paikallinen ajotietokanta `db_v2.json` jää epäsynkroniin master-siemendatan `seed_data.json` kanssa, jolloin backend kaatuu käynnistyessään.

### 6.2 Pakollinen 5-vaiheinen migraatioprotokolla (Atomic Migration Protocol)

Jokainen parannuskohteiden toteutusaskel on suoritettava poikkeuksetta seuraavan protokollan mukaisesti:

```
+-----------------------------------------------------------------------------------+
| VAIHE 0: DETERMINISTISET MIGRAATIOSKRIPTIT (scratch/ tai scripts/migrations/)     |
|  1. Skripti A: seed_data.json -migraattori (kopioi tekstit, poistaa redundantit)  |
|  2. Skripti B: Testifikstuurien AST/regex-migraattori (siivoaa 1300+ testitapausta)|
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| VAIHE 1: SEED VAULT & TIETOKANNAN ATOMAARINEN PÄIVITYS                           |
|  1. Varmuuskopiointi: backend_v2/seed/backups/seed_data_<timestamp>.json          |
|  2. Aja Skripti A seed_data.json -tiedostolle                                     |
|  3. JSON Integrity & Syntax Check (tarkista ettei rikkinäisiä sulkuja synny)     |
|  4. Suorita uudelleensiemennys: uv run python backend_v2/seed/run_seed.py local   |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| VAIHE 2: PYTHON DOMAIN & FLUTTER FREEZED -MALLIEN YHTENÄISTÄMINEN                |
|  1. Poista poistettavat kentät: v2_core.py, models/dtos/                         |
|  2. Poista vastaavat kentät: client_app_v2 Freezed-mallit                         |
|  3. Generoi Flutter-koodit: dart run build_runner build --delete-conflicting-outputs|
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| VAIHE 3: YKSIKKÖTESTIEN JA PALVELUKERROKSEN KORJAUS                               |
|  1. Aja Skripti B päivittämään kaikki testifikstuurit backend_v2/tests/ -kansiossa|
|  2. Päivitä palvelut (matrix_domain_parser.py, simulation_service.py, adapterit)  |
|  3. Aja auditointiluuppi: uv run python scripts/backend_audit_loop.py backend_v2  |
|  4. Aja Flutter-auditointiluuppi: uv run python scripts/flutter_audit_loop.py     |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| VAIHE 4: AST GUARDRAIL & REGRESSION LOCK                                          |
|  1. Lisää AST-testit: test_seed_architectural_guardrails.py kieltämään poistetut   |
|     kentät (scale_min PromptBlockilla, default_locale I18nTextissä) pysyvästi     |
|  2. Atomaarinen git-commit ennen seuraavaa kokonaisuutta                          |
+-----------------------------------------------------------------------------------+
```

### 6.3 Purkkaratkaisujen nollatoleranssi (Zero-Tolerance Gates)
* **Kielto 1:** `extra='ignore'` -konfiguraation lisääminen malleihin teknisen velan ohittamiseksi on ehdottomasti kielletty ([`duck_typing_token_shield_exception`](file:///c:/src/quorum/.agents/rules/01-python-backend.md#L345-L349)).
* **Kielto 2:** `@model_validator(mode="before")` -metodien kirjoittaminen poistettujen avaimien siivoamiseksi ajonaikaisesti on kielletty ([`zero_legacy_fallback_hacks`](file:///c:/src/quorum/.agents/rules/01-python-backend.md#L133-L137)).
* **Kielto 3:** `.get("scale_min", 1.0)` tai vastaavien maagisten oletusarvojen lisääminen palvelukerrokseen on kielletty ([`zero_service_layer_fallbacks`](file:///c:/src/quorum/.agents/rules/00-antigravity-core.md#L132-L136)).
* **Kielto 4:** Failing-testien ohittaminen `@pytest.mark.skip` -merkinnällä on ehdottomasti kielletty ([`anti_test_skipping_mandate`](file:///c:/src/quorum/.agents/rules/00-antigravity-core.md#L222-L226)). Testit on aina korjattava vastaamaan uutta skeemaa.

---

### 6.4 Toteutusvaiheistus ja Etenemisjärjestys (Implementation Packages Roadmap)

Tier 8 -auditoinnin pohjalta kokonaisuus toteutetaan neljänä itsenäisenä ja hallittavana toteutuspakettina (Epicit / Tehtäväpaketit), joista jokainen suorittaa oman 5-vaiheisen atomaarisen migraationsa:

```
+-----------------------------------------------------------------------------------+
| PAKETTI 1: I18nText & TheoryGrounding Puhdistus (Luvut 3 & 2)                     |
|  - default_locale poisto I18nText-mallista (Python + Flutter)                     |
|  - theory_context XML-muotoilu ja ai_description tuplien poisto                  |
|  - Skriptit A & B: testifikstuurien ja seed_data.json:n siivous                   |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| PAKETTI 2: TDAAssertion & Kehotteiden Yhdistäminen (Luku 4)                       |
|  - 70 tyhjän <question>-bugin korjaus ja TDAAssertion SSOT -keskitys              |
|  - simulation_service.py duck-typingin poisto ja testien päivitys                 |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| PAKETTI 3: Matriisiskaalauksen Keskitys (Luku 1)                                  |
|  - scale_min / scale_max poisto PromptBlockilta (vain computed_min/max)           |
|  - custom_scale_min / custom_scale_max siirto OutputProfilelle                    |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| PAKETTI 4: Esitysprofiilin L10n & Ryhmittelyn Uudistus (Luku 5)                   |
|  - metric_mappings ym. sanakirjojen poisto seed_data.jsonista ja .arb-siirto      |
|  - layouts -> matrix_synthesis_groups refaktorointi (Python, Flutter Tab, worker) |
+-----------------------------------------------------------------------------------+
```
