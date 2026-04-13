# MEGA EPIC 23: Map-Reduce Orchestration & DINA Scoring Calibration

## Tausta (Background)
Järjestelmämme kohtaa parhaillaan kaksi rinnakkaista ydinongelmaa, jotka jarruttavat arviointien tuotantokehitystä:

1. **Infrastruktuurin Suorituskyky (Token Explosion):** Kun DAG Executor joutuu puskemaan jopa satoja kysymyksiä yhden Step-lohkon sisällä Vertex AI -malleille, koko massiivinen vastaus vaaditaan yhtenä strukturoituna JSON-taulukkona. Pydantic-validoinnin ja LLM-generoinnin raskaus johtaa usein tuotantoinfrastruktuurin aikakatkaisuihin (Timeout). Olemme joutuneet laastaroimaan tätä hylkäämällä osan kysymyksistä (esim. `STRATIFIED_3` sämpläys).
2. **Kognitiivinen Ylikriittisyys (Scoring Harshness):** Arviointi on toisinaan pikkutarkkaa eksakteista avainsanoista. Lisäksi nykyinen DINA-putouslaskenta rankaisee liian kovaa kertolaskuillaan, jolloin jopa perustellut ja taitavat analyysit valuvat kohti täyttä nollaa pienten puutteiden takia (Double Jeopardy & Cascading Doom).

## Tavoite (Objective)
Rakentaa täydellinen **Mega Epic**, joka yksinkertaistaa laskentamatematiikan takaisin täyteen O(1)-determinismiin ja ottaa käyttöön Map-Reduce arkkitehtuurin, jolla järjestelmä pystyy pureskelemaan rajattoman määrän tietoa tukehtumatta. 

Suorituskyvyn (Map-Reduce) ja Tarkkuuden (DINA Calibration) yhdistäminen luo arkkitehtuurin, jota ei tarvitse erikseen "suojella" raskaalta tiheydeltä.

## Arkkitehtuurivaatimukset ja Säännöt (`05_llm_architecture.md` Mukaisesti)

### A. DINA Scoring Calibration & Math Simplicity
1. **"Benefit of the Doubt" -mandaatti (Shift-Left)**: Arviointiin lisätään puhdas ohjeellinen rentous, joka pakottaa LLM:n tunnistamaan myös johdetun ja epäsuoran loogisen argumentoinnin ilman täydellisiä täsmäsanoja. Tämä parantaa `hit_rate`-osumia suoraan lähteellä ilman koodimuutoksia.
2. **DINA-virtakertoimen lattia (Floor)**: Puhdas matemaattinen turvaverkko natiivilla `max()` -toiminnolla. Kertovat rangaistukset eivät saa pudottaa suoritusta kohti nollaa ilman rajoja. Käytetään täysin uutta Enum-rakennetta (esim. `ScoringCalibrationThresholds.DINA_FLOOR = 0.30`).
3. **Double Jeopardy -Katto (Ceiling)**: Rangaistusten yhteisvaikutus lasketaan yhteen (esim. Post-Hoc + Passivity) ja niille asetetaan maksimikatto absoluuttisesti `min()` -funktiolla. Ohjataan uudella Enum-rakenteella (esim. `ScoringCalibrationThresholds.PENALTY_CAP = 0.25`). Ei ehtolausekkeitä, pelkkää suoraviivaista O(1)-matematiikkaa.

### B. Map-Reduce Orchestration
4. **Pirstalointi ja Kokoaminen (Map & Reduce)**: Kun kuorma ylittää rajan, arviointipuu halkaistaan osiin. Jokainen osa tuottaa EHDOTTOMASTI jähmetetyn Pydantic-mallin (ei ikinä raaka-dictejä / `no_naked_dicts_in_state`). Jokainen osanen tunnustaa yksilöllistä Opaque Stripe ID:tä (`chk_abc1a2...`). Valtoimenaan generoituva ChunkResponseSchema yhdistetään turvallisesti takaisin `state_delta` muotoon.
5. **SSOT Konkurrenssin ja Arkkitehtuurin Suojelu**: Mielivaltaisia erillisrajoittimia ei keksitä. Asyncio TaskGroup joutuu rajoittamaan rinnakkaiskutsunsa EHDOTTOMASTI ENUM-arvoon **`SystemConcurrency.MAX_CONCURRENT_LLM_STEPS`** API Rate Limitien (429) ehkäisyksi. Vertex SDK:ta (`litellm`) ei koskaan suorakääritä omilla semaphoreilla (Sääntö `direct_sdk_calls` ban).
6. **Fail-Fast Resilienssi**: Map-palasten osittaisyrityksiin (Partial Retry) sidotaan YKSINOMAAN tiukka **`SystemConcurrency.LLM_MAX_RETRIES`** Enum (joka on säädetty kakkoseen). Emme toteuta loputtomia itsensäparannussilmukoita ("Anti-Infinite Loop").

## Implementointivaiheet (Phases) Puhtaalta Pöydältä

- **Phase 1: Scoring Calibration & The Lenient Shift** 
  - Päivitetään uudet kynnysarvot (`DINA_FLOOR`, `PENALTY_CAP`) Enums-tiedostoon.
  - Viedään O(1) `min/max` -matematiikka rangaistuksiin `scoring.py` -tiedostossa. 
  - Lisätään `PromptCompilerin` System Injunctioniin "Constructive Leniency" ja Benefit of the Doubt -määräys.
- **Phase 2: The Eristetty Chunking Service (TDD)** 
  - Luodaan `ChunkingService` Pydantic-skeema ja yksikkötestit laboratoriomallissa. Se tuottaa palasta kohden puhtaita Map-paloja Opaque-tunnistein ilman kosketusta LLM:ään.
- **Phase 3: PromptCompilerin Dynaaminen Modulaarisuus** 
  - Päivitetään `PromptCompiler` rakentamaan täysin irrallinen V2 `ChunkResponseSchema` jokaiselle satunnaiselle Map-palaselle, säilyttäen `llm_structured_execution_mandate` -vaatimuksen, jottei LLM "vain renderöi epämääräistä JSONia". (Surgical Precision Exception Rule).
- **Phase 4: Async Orchestration ja Map-Reduce (Execution)** 
  - Laajennetaan `backend_v2/services/orchestrator/strategies/llm.py` hyväksymään modulaariseltä ChunkingServiceltä saatu taulukko. Ajo viedään turvallisen `TaskGroupin` läpi hyödyntäen ainoastaan `SystemConcurrency.MAX_CONCURRENT_LLM_STEPS` Enumia.
- **Phase 5: Release the Gates (Seeding & Validation)** 
  - `STRATIFIED` rajoittimen poistaminen järjestelmästä globaalisti ja vaihtaminen `ALL (0)` prosessointiin. Koko koodikannan validointi todistaaksemme Mega Epicin saavuttaneen kognitiivisen oikeellisuuden ja infrastruktuurin sietokyvyn rajattomille atomeille.
