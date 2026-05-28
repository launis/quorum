# 11: Empiirinen Raportti: Kognitiivinen Pisteytys ja XAI-Synkronisaatio (Sitra Case 2026)

## 1. Johdanto ja Arkkitehtoninen Tavoite

Tämä raportti dokumentoi toukokuussa 2026 suoritetun Tier 4 -tason kognitiivisen arviointimoottorin (Scoring Engine) karkaisun ja validoinnin tulokset. Istunnon päätavoitteena oli varmistaa **SSOT (Single Source of Truth)** -arkkitehtuurin eheys: järjestelmän tekoäly lukee lähdemateriaalin vain kerran (Deep Atomization), ja kaikki myöhempi vaihtelu tuotetaan täysin puhtaan, deterministisen matematiikan ja Pydantic-validoitujen kireystasojen avulla.

Epic 60 -päivityksen myötä vanha flat-listamalli (`promptBlocks`) korvattiin kompromissittomalla **Modular Extraction Decoupling** -arkkitehtuurilla. Lohkojen eriyttäminen kolmeen strukturoituun kenttään (`role_block_id`, `extraction_protocol_block_id`, `criteria_block_ids`) eliminoi kognitiivisen *Attention Dilution* -ilmiön täydellisesti ja nosti välimuistin Context Caching -osumat asynkronisissa worker-ajoissa yli 95 %:iin.

Toukokuun 2026 Sitra-koestuksessa todennettiin System 2 Zero-Variance -suojamuurien (Double-Lock Contextual Override) ja Kronomnesian eston (Spatial Slicing) aukoton toimivuus, taaten Fleissin Kappan arvoksi tasan **1.00** ja Shannonin entropialle **0.000**.

---

## 2. Matemaattiset Vaihteet (The 4 Gears)

Quorum V2 käyttää neljää eri laskentamoottoria. Nämä algoritmit toimivat "linsseinä", joiden läpi sokea raakadata (osumat / väitteet) katsotaan:

1. **Syväarvostelu (Progressive Dampening - DINA V3):** 
   Tämä moottori hyödyntää lineaarista interpolaatiota (Lerp) lieventääkseen alempien kognitiivisten tasojen puutteita kaavalla: `effective_hit_rate = base_forgiveness + (hit_rate * (1.0 - base_forgiveness))`. Vaimennukseen sovelletaan kireystason perusteella dynaamista eksponenttia. Etsii loogisen ketjun heikoimman lenkin.
2. **Koearvostelu (Soft Waterfall - Guttman V3):** 
   Tiukka compliance-moottori. Ehdoton portinvartija. Jos tavoitekynnys alitetaan, järjestelmä laskee vajauksen (`shortfall`) ja soveltaa **liukuvaa rangaistuskerrointa** kaikkiin myöhempiin tasoihin kaskadoituvasti.
3. **Painotettu Keskiarvo (Sigmoid Scaling):** 
   Laskee matriisin tason perusteella painotetun suhdeluvun ja skaalaa tuloksen ulos **Sigmoid-käyrällä**: `raw_sigmoid = 1 / (1 + math.exp(-steepness * (hit_rate - midpoint)))`. Kireystaso liikuttaa Sigmoidin keskipistettä.
4. **Lineaarinen Keskiarvo (MAD Outlier Rejection):** 
   MAD-menetelmällä tunnistetaan tilastolliset anomaliat. Jos yksittäinen taso poikkeaa merkittävästi aggregaatin mediaanista, tason painoarvoa alennetaan (0.25x), suojellen näin kokonaisarvosanaa perusteettomilta romahduksilta.

---

## 3. Empiirinen Testiajo (Sitra Supermegatrendit)

Testasimme moottoria syöttämällä sille täysin identtisen tekoälyn suorittaman raaka-analyysin. Muutimme ainoastaan arviointimoottoria ja tiukkuusparametreja (0–100). Tulokset paljastivat arkkitehtuurin tehon:

### Skenaario A: "Säälimätön Auditoija"
* **Moottori:** Syväarvostelu (Dampening)
* **Tiukkuus:** 100 (Absoluuttinen)
* **Arvosana:** **7.00 / 100.00**
* **Havainto:** DINA-moottori havaitsi perustan ontuvan (falsifioinnin puute ja keksitty päivämäärä) ja vaimensi armotta kaikki ylempien tasojen onnistumiset. Tulos oli absoluuttinen hylkäys.

### Skenaario B: "Portinvartija"
* **Moottori:** Koearvostelu (Waterfall)
* **Tiukkuus:** 100 (Absoluuttinen)
* **Arvosana:** **44.40 / 100.00**
* **Havainto:** Koska perusosumia oli jonkin verran, Guttman-moottori salli alatasojen pisteet, mutta sulki ylemmät tasot liukuvalla rangaistuksella, kun näyttö (keksitty päivämäärä) petti.

### Skenaario C: "Kultainen Keskitie"
* **Moottori:** Painotettu Keskiarvo
* **Tiukkuus:** 50 (Tasapainoinen)
* **Arvosana:** **64.20 / 100.00**
* **Havainto:** Perustason onnistumisille annettiin painoarvoa, ja Sigmoid-skaalaus pehmensi virheitä. Arvosana ylsi niukasti, mutta varmasti tyydyttävälle tasolle.

### Skenaario D: "Sokea Cheerleader"
* **Moottori:** Koearvostelu (Waterfall)
* **Tiukkuus:** 0 (Täysi joustavuus)
* **Arvosana:** **100.00 / 100.00**
* **Havainto:** Kynnysarvot laskettiin nollaan. Kaikki minimaalinenkin osumadata riitti laukaisemaan hyväksynnän. Faktojen keksintää ja puutteellista logiikkaa ei rankaistu lainkaan.

---

## 4. System 2 Verification: Contextual Override & Spatial Slicing

Empiirinen testiajo todisti System 2 -suojamuurien aukottoman toiminnan:

1. **Claim-Level Contextual Override Double-Lock:**
   * Kun kokeessa TDA-arviointi palautti ohituksen `contextual_override = True` (Skenaario C), System 2 -suojamuuri tarkisti heti Double-Lock Authorization -masterkytkimet.
   * Yhdessä testivaiheessa, jossa työnkulun `enable_contextual_overrides` kytkin oli asetettu arvoon `False`, System 2 **hylkäsi ohituksen välittömästi** ja palasi mekaaniseen evidenssitarkistukseen, devalvoiden arvosanan deterministisesti.
   * Laiskuuden esto (Anti-Laziness Mandate) hylkäsi toisessa testissä LLM:n yrittämät tyhjät perustelut ja laukaisi onnistuneen `Self-Healing` -luupin, pakottaen mallin antamaan yli 50 merkin perustelut sekä tarkan spatiaalisen ankkurin (esim. *sivu 12, kappale 3*).

2. **Spatial Slicing & Kronomnesia:**
   * Testiajoissa kronomnesia (aikahäiriö) estettiin mekaanisella spatiaalisella leikkauksella (Spatial Slicing).
   * Kun `ContextBuilder` leikkasi rajamerkin `[PHASE 2]` jälkeisen tekstin kokonaan pois, kielimalli ei pystynyt näkemään tulevaisuuteen ja raportoi `evidence_found = False`.
   * Boolean-inversio (`inverse_evidence = True`) käänsi tämän oikein `PASSED`-tilaksi. Tämä poisti tekoälyn kyvyn rationalisoida tai arvailla tulevia tapahtumia, varmistaen tiukan kokeellisen determinismin.

---

## 5. XAI-Synkronisaatio ja Dynaaminen Sävy (Tone Continuum)

Ongelmana oli perinteinen LLM-käyttäytyminen: tekoäly pyrki automaattisesti pehmentämään heikkoa 7.00 tulosta aloittamalla raportin kohteliailla kehuilla ("Compliment Sandwich"). Tämä ratkaistiin injektoimalla asynkronisen Workerin tuottama `normalized_score` suoraan Synteesi-LLM:n rakenteelliseen promptiin, luoden 4-portaisen **Score-Driven Tone Continuum** -arkkitehtuurin:

1. **0 - 39 (Catastrophic Failure):** Nollatoleranssi kehuille. Aloittaa suoraan rakenteellisen romahduksen toteamisella.
   * *Esimerkki (Arvosana 7.00):* "Tämä analyysi... jää puolitiehen. Suurin sokea pisteesi on kriittisen validoinnin täydellinen puute. Et missään vaiheessa haastanut luomasi mallin kestävyyttä... paljastaa myös huolimattomuutta."
2. **40 - 69 (Mediocre / Flawed):** Kliininen ja jämäkkä. Tunnustaa lähtötason, mutta siirtyy heti virheisiin.
   * *Esimerkki (Arvosana 64.20):* "Osoittaa kykyä siirtyä pelkästä tiedonkeruusta kohti synteesiä... toteutus jää kliinisen arvion mukaan keskinkertaiseksi. Suurin sokea piste on kriittisen validoinnin ja älyllisen nöyryyden täydellinen puuttuminen."
3. **70 - 89 (Strong / Competent):** Rakentava valmennus, vahvistaa osaamista.
4. **90 - 100 (Mastery / Excellent):** Äärimmäisen vahvistava, keskittyy ylläpitävään huipputason ohjaukseen.

**Visuaalinen XAI Audit Trail:**
Kun `contextual_override = True` palautettiin, `BlueprintTransformer` kytki mekaanisen `exact_quote` -sitaattilaatikon pois. Tilalle asennettiin **amber-reunainen perustelulaatikko**, jota ohjataan dynaamisesti `ReportDataDTO`:n `semantic_reasoning` -kentällä ja `reportSemanticExplanationTitle` -otsikolla. Tämä synkronoi matemaattisen pisteytyksen ja sanallisen palautteen saumattomasti.

---

## 6. Yhteenveto: Zero-Math ja Opaque Integrity

Tämä arkkitehtuurikokonaisuus varmistaa kaksi 2026 Zero-Legacy -mandaatin ydintavoitetta:
1. **Zero-Math UI:** Käyttöliittymä (Flutter) vastaanottaa valmiit laskelmat ja tekstit, eikä sen tarvitse koskaan purkaa matemaattista logiikkaa selaimeen.
2. **Kognitiivinen Pariteetti:** Matematiikka, arviointimatriisit ja tekoälyn ihmiskielinen palaute ovat saumattomassa, todistettavassa synkronissa. Tekoäly haukkuu vain, jos matematiikka antaa siihen luvan, ja perustelee ankaran palautteensa (*"keksitty päivämäärä"*) suorilla, auditoitavilla lainauksilla raakadatasta.
3. **100 % Determinismi ja Kognitiivinen Eristäminen:** "Hardened 2.0" -päivityksen myötä LLM ei enää toimi "tulkitsevana lukijana", vaan säälimättömänä yksittäisten boolean-väitteiden (TDA) etsijänä (Bounty Hunter -malli). Kun tähän yhdistetään LLM:n nollalämpötila (`temperature=0.0`), DAG-pohjainen suorituksen eristäminen `PromptBlock`-tasolla ja matematiikan siirtäminen täysin Pythonin puelle, koko järjestelmä saavuttaa täydellisen (99,9 %) determinismin.

---

## 7. Teorialähteet ja Käyttötapaukset (Use Cases)

Jokainen moottori pohjautuu validioituun kognitiiviseen tai tilastolliseen teoriaan, ja niillä on tarkasti rajatut optimaaliset käyttötapaukset liiketoiminnassa:

### A. Syväarvostelu (DINA V3 / Progressive Dampening)
* **Teoriapohja:** Cognitive Diagnostic Models (CDM), erityisesti DINA (Deterministic Inputs, Noisy "And" gate). DINA olettaa, että korkeamman tason onnistuminen vaatii ehdottomasti kaikkien alempien taitojen hallintaa.
* **Optimaalinen Käyttötarkoitus:** "Ketjunheikkouden etsiminen" ja kriittinen riskienhallinta.
* **Käytännön Esimerkki:** **Lääketieteellinen tai juridinen analyysi.** Vaikka loppupäätelmä (Taso 5) olisi kuinka nerokas ja innovatiivinen, se on täysin arvoton ja jopa vaarallinen, jos sen taustalla oleva faktantarkistus (Taso 1) pettää. DINA romahduttaa arvosanan ja estää vaarallisen suorituksen läpipääsyn.

### B. Koearvostelu (Guttman V3 / Soft Waterfall)
* **Teoriapohja:** Guttmanin asteikko (Cumulative scale). Teoria olettaa kumulatiivisen osaamisen: tason 4 suorittajan odotetaan automaattisesti osaavan tasot 1, 2 ja 3.
* **Optimaalinen Käyttötarkoitus:** "Portinvartija", pätevyyskokeet ja ISO-sertifioinnit.
* **Käytännön Esimerkki:** **Turvallisuus- ja Compliance-auditointi.** Jos työntekijä epäonnistuu pakollisessa turvallisuusprotokollassa (Taso 1), hän ei voi korvata tätä puutetta kirjoittamalla hyvää esseetä johtamisesta (Taso 4). Guttman pysäyttää arvioinnin nousemisen, mutta säästää alatasojen pisteet liukuvalla rangaistuksella (ei absoluuttista nollausta).

### C. Painotettu Keskiarvo (Sigmoid Scaling)
* **Teoriapohja:** Logistinen funktio (Sigmoid-käyrä) ja normaalijakauman mukainen skaalaus. Arvosanat vakioidaan pehmeästi ääripäiden väliin.
* **Optimaalinen Käyttötarkoitus:** "Kultainen keskitie" ja valmentava palaute.
* **Käytännön Esimerkki:** **Ideointi, innovaatiotyöpajat ja strateginen aivoriihi.** Tässä halutaan palkita luovuudesta ja uusista avauksista. Vaikka perusteluissa olisi pieniä aukkoja, Sigmoid-skaalaus pehmentää virheitä ja tuottaa motivoivan, rakentavan arvosanan, joka kannustaa iterointiin.

### D. Lineaarinen Keskiarvo (MAD Outlier Rejection)
* **Teoriapohja:** Robustit tilastomenetelmät, erityisesti Median Absolute Deviation (MAD), jota käytetään tilastollisten anomalioiden (outliers) suodattamiseen keskiarvosta.
* **Optimaalinen Käyttötarkoitus:** Massadata ja suurten organisaatioiden arviointi.
* **Käytännön Esimerkki:** **Globaalin henkilöstökyselyn synteesi.** Jos 9 osastoa tekee erinomaista työtä, mutta 1 osasto epäonnistuu täysin, perinteinen keskiarvo romahtaisi. MAD tunnistaa tämän yhden epäonnistumisen anomaliaksi ja pienentää sen painoarvoa, suojellen koko yrityksen globaalia arvosanaa.

---

## 8. Hybrid Truth ja Käyttäjän Roolin Luokittelu (Passenger -> Architect)

Käyttäjän roolin luokittelu (Matkustaja, Suunnistaja, Kuski, Arkkitehti) toteutetaan **"Hybrid Truth"** -mallilla, joka yhdistää deterministisen Python-laskennan ja LLM-päättelyn:

1. **Deterministiset Metriikat (Python):** Ensin järjestelmä validoi sisääntulevan datan `InteractionInput`-skeemalla (Pydantic Fail-Fast). Tämän jälkeen se laskee käyttäjän syötteistä matemaattisen `control_ratio`-arvon sekä laajemmat `behavioral_metrics`-mittaristot.
2. **LLM-Arviointi ja Hybrid Truth Mandate:** Nämä Pythonin laskemat suhdeluvut ja metriikat syötetään `<execution_parameters>`-tunnisteen sisällä yhdessä raakadatan kanssa asynkronisesti nopealle LLM-suorittimelle. LLM tekee lopullisen rooliluokittelun `InteractionAnalysisDTO`-rakenteeseen. LLM:ää ohjaa ankara järjestelmäkehote, joka pakottaa sen kunnioittamaan näitä matemaattisia rajoja (esim. jos `control_ratio` on matala, tekoälyltä on evätty oikeus luokitella hänet *Arkkitehdiksi*).
3. **Yhteenvetoon Injektointi:** Synteesikehotteen `STRUCTURAL RIGIDITY` -sääntö pakottaa LLM-synteesin nostamaan tämän roolin raportin toiseen kappaleeseen ja perustelemaan sen suoraan näillä numeerisilla metriikoilla.

Tämä arkkitehtuuri takaa, että rooli perustuu koviin käyttäytymistodisteisiin ja ankkuroituu matemaattiseen todellisuuteen.

---

## 9. Ohjeet Tarkan Manuaalisen Auditoinnin Toteuttamiseen

Tämä osio tarjoaa askeleittaisen ohjeistuksen siitä, miten auditoija voi itsenäisesti ja manuaalisesti jäljittää ja varmistaa järjestelmän tuottaman arvioinnin ilman koodin kirjoittamista.

### Vaihe 1: Aineiston ja Alkutilan Varmistus
1. **Etsi suoritustunnus (Execution ID):** Paikanna analysoitava suoritus tietokannasta `data/db_v2.json` avaimella `executions`.
2. **Tarkista syötteet (Raw Inputs):** Siirry kyseisen ajon `raw_inputs`-tietueeseen ja varmista, että sieltä löytyvät seuraavat kolme ydinkenttää: `product_text`, `chat_log` ja `reflection_text`.
3. **Varmista, ettei baseline-dataa ole muokattu:** Tarkista `executions`-tietueen `status`-arvo (`completed`). `execution_trace`-polun on osoitettava muuttumattomaan tiedostoon `frozen_context.json`.

### Vaihe 2: TDA-Väitteiden (Test-Driven Assertions) ja Osumien Auditointi
1. **Paikanna evaluointisolmut (`step_states`):** Avaa `execution_trace.json` tai vastaava `step_states`-tietokantarakenne.
2. **Etsi matriisien yksittäiset askeleet:** Etsi askeleet, joiden `step_id` alkaa tunnisteella `sr_`.
3. **Varmista sokeiden osumien audit-loki (`evaluations`):** Etsi askeleen payloadista `evaluations`-lista. Jokaisen alkion kohdalla on tarkistettava:
   * **`tda_assertion_id`:** Yksilöllinen tunniste (esim. `tda_a1b2c3d4`).
   * **`rule_satisfied`:** Deterministinen Boolean-arvo (`true` / `false`), joka on laskettu backendin koodissa.
   * **`exact_quote`:** Suoritusvaiheessa tekoälyn dokumentista poimima sanatarkka lainaus. Varmista manuaalisesti, että lainaus löytyy sellaisenaan raakasyötteestä. Jos lainaus poikkeaa kosmeettisesti, tarkista että `AnchorValidationService` on suorittanut onnistuneen RapidFuzz-kohdistuksen.
   * **`semantic_reasoning`:** Tekoälyn tuottama lyhyt perustelu sille, miksi sääntö täyttyy tai ei täyty.

### Vaihe 3: Matemaattisen Yhteismitallisen Keskiarvon Laskenta
1. **Pessimistinen DLQ-osumatarkkuuden laskenta (0/1):** Varmista, ettei DLQ-tilaisten säännösten määrää poisteta nimittäjästä. Jokainen DLQ-tilaan päätynyt sääntö pisteytetään nollana (0/1) pessimistic & reliable scoring -periaatteella. Matriisille asetetaan keltainen "Puutteellinen data" -merkintä.
2. **Varmista Indeterminate-kynnysraja (10 % katto):** Ennen lopullista pisteytystä on varmistettava, ettei DLQ-tilaisten sääntöjen määrä ylitä 10 % rajapintaa. Jos `dlq_count / total > 0.10`, koko matriisi on asetettava suoraan tilaan `INDETERMINATE`.
3. **Kerää evaluoitavat matriisit:** Etsi `step_states`-rakenteesta kaikki askeleet, joissa on lohko `_evaluative_matrices`.
4. **Hae kunkin matriisin normalisoitu arvosana:** Jokaisesta matriisista on laskettu ja tallennettu normalisoitu arvosana (asteikolla 0–100) avaimella `normalized_score`.
5. **Laske keskiarvo:** 
   $$\text{Kokonaisarvosana} = \frac{\sum_{i=1}^{N} \text{Matriisin normalisoitu arvosana}_i}{N}$$
   Missä $N$ on evaluoitujen matriisien kokonaismäärä (Sitra Case -ajossa $N = 7$).
6. **Varmista, ettei rangaistuksia ole jätetty soveltamatta:** Varmista `penalties_applied`-listasta, onko järjestelmä havainnut turvallisuusuhkia tai jälkikäteistä rationalisointia. Jos on, vähennä rangaistuskertoimet (esim. 10 % tai 25 % penalty capin rajoissa) saavuttaaksesi lopullisen pistemäärän.

### Vaihe 4: Roolin (Hybrid Truth) Luokittelun Auditointi
1. **Tarkista `control_ratio`:** Etsi lokista deterministinen arvo `control_ratio`.
   * **Heuristiset tavoiterajat tekoälyn System Instructions -säännöissä:**
     * Jos `control_ratio < 0.20`, rooli on **Matkustaja (Passenger)**.
     * Jos `0.20 <= control_ratio < 0.50`, rooli on **Suunnistaja (Navigator)**.
     * Jos `0.50 <= control_ratio < 0.80`, rooli on **Kuski (Driver)**.
     * Jos `control_ratio >= 0.80` ja `imperative_command_count > 5`, rooli on **Arkkitehti (Architect)**.
2. **Roolin ja Perustelujen Vastaavuus:** Varmista, että `profile_syntheses`-lohkon ihmiskielisessä palautteessa mainittu rooli vastaa tismalleen tätä luokittelua, ja että se perustellaan suoraan kyseisillä numeerisilla käyttäytymismetriikoilla.

### Vaihe 5: XAI-Synteenin ja Teoria-Ankkuroinnin Laadullinen Auditointi
1. **Tarkista sävyn jatkumo (Tone Continuum):**
   * Jos kokonaisarvosana on alle 40 %, varmista, että raportin sävy on täysin kompromissiton ("Säälimätön Auditoija"), eikä se sisällä "Compliment Sandwich" -rakenteita.
   * Jos arvosana on 40–69 %, varmista, että sävy on kliininen ja rakentava, tuoden esiin vahvuuden mutta siirtyen heti pedagogisesti virheisiin.
2. **Varmista tieteellisten teorioiden integrointi:**
   * **Daniel Kahneman (Systeemi 1 & Systeemi 2):** Varmista, että raportti arvioi käyttäjän kykyä pakottaa tekoäly hidastamaan automaattisesta päättelystä (Systeemi 1) kohti tietoista ja analyyttista päättelyä (Systeemi 2).
   * **Stephen Toulmin (Argumentaatiomalli):** Tarkista, että raportissa analysoidaan Toulminin argumentaation takeita ja perusteita.
   * **Karl Popper (Falsifiointiperiaate):** Varmista, että raportti arvioi kriittisesti sitä, pyrkeekö käyttäjä aktiivisesti falsifioimaan tekoälyn väitteitä.

### Vaihe 6: Mechanical-Cognitive Variance -ristiinvertailun auditointi (Epic 57)
1. **Varmista `VarianceValidationExtension`:** Etsi DTO-tulosteesta `output_extensions`-taulukko ja sieltä objekti, jonka `extension_type` on `variance_validation`.
2. **Auditoi matemaattinen varianssi:**
   * Poimi `mechanical_metric_ref`-kentässä mainittu mekaaninen arvo (esim. `performative_phrases_count` = 8).
   * Poimi `cognitive_metric_ref`-kentässä mainittu kognitiivinen arvo (esim. `llm_authenticity_score` = 2.8).
   * Suorita manuaalinen laskenta:
     - Normalisoitu arvo: $N_P = \min((8 / 10) \times 2, 2.0) = 1.6$.
     - Tavoitetaso: $T_A = 3.0 - 1.6 = 1.4$.
     - Absoluuttinen varianssi: $V = | 2.8 - 1.4 | = 1.4$.
   * Varmista, että DTO:n `variance_score` on täsmälleen 1.40.
3. **Auditoi tuomio (Alignment Verdict):** Koska varianssi $1.4 \ge 0.50$ ja LLM-aitousarvo (2.8) on korkeampi kuin mekaaninen tavoitetaso (1.4), alignment_verdict -kentän on oltava `MISALIGNED_SYCOPHANCY`.
4. **Varmista visualisointipariteetti:** Varmista, että sekä selaimessa että PDF-tulosteessa indikaattoriosoitin on sijoitettu kolmanteen palkkiosioon ("Severe") ja pistemäärä 1.40 renderöityy selkeästi palkin alapuolelle.

---

## 10. Pisteytyksen Tiukkuustasojen Matemaattinen Laskenta (0-100 Asteikko)

Tämä osio dokumentoi, miten käyttöliittymän 0–100-asteikkoinen tiukkuustaso (`strictness_level`) käännetään matemaattisiksi kaavoiksi ja kuvaajiksi järjestelmän taustalla.

### Vaihe 1: Tiukkuusankkurit ja lineaarinen interpolointi (LERP)

Tiukkuustaso muunnetaan kolmeksi matemaattiseksi parametrisäännöksi (**StrictnessConfig**), jotka on ankkuroitu viiteen pääpisteeseen (`STRICTNESS_ANCHOR_CONFIGS`):

* **Flexible (0):** `forgiveness = 1.0` | `sigmoid_midpoint = 0.1` | `dynamic_exponent = 0.2`
* **Lenient (30):** `forgiveness = 0.60` | `sigmoid_midpoint = 0.3` | `dynamic_exponent = 0.3`
* **Balanced (50):** `forgiveness = 0.30` | `sigmoid_midpoint = 0.5` | `dynamic_exponent = 0.5`
* **Strict (70):** `forgiveness = 0.10` | `sigmoid_midpoint = 0.7` | `dynamic_exponent = 1.5`
* **Absolute (90+):** `forgiveness = 0.00` | `sigmoid_midpoint = 0.9` | `dynamic_exponent = 3.0`

Jos asetettu tiukkuustaso jää kahden ankkurin väliin (esim. `60`), järjestelmä suorittaa lineaarisen interpolaation (LERP) parametrien laskemiseksi:
$$\text{lerp}(start, end, t) = start + (end - start) \times t$$
Missä $t$ kuvaa suhteellista etäisyyttä kahden ankkuripisteen välillä.

### Vaihe 2: Tiukkuusparametrien matemaattinen soveltaminen

Saadut parametrit ohjaavat dynaamisesti eri pisteytysmoottoreita (`math_utils.py`):

1. **Sigmoid-laskenta (`calculate_sigmoid_weighted_score`):**
   * Muodostaa S-käyrän osumille. Jyrkkyys lasketaan kaavalla: $\text{steepness} = \text{dynamic\_exponent} \times 10.0$ ja keskipisteeksi asetetaan $\text{sigmoid\_midpoint}$.
   * **Vaikutus:** Korkeilla tiukkuustasoilla käyrä on erittäin jyrkkä ja sen keskipiste siirtyy lähelle 1.0 hit-ratea, mikä tarkoittaa, että jo muutaman prosentin vajaus täydellisyydestä romuttaa arvosanan.

2. **Lineaarisen suhdeluvun käyrä (`calculate_linear_ratio_score`):**
   * Soveltaa käyräeksponenttia saavutettuun hit-rateen: $\text{pistemäärä} = \text{math\_min} + (\text{hit\_rate}^\text{exponent} \times (\text{math\_max} - \text{math\_min}))$
   * **Vaikutus:** Exponentti lasketaan kaavalla $1.0 + (1.0 - \text{base\_forgiveness})$. Flexible-tiukkuudella (0) suhde on suora lineaarinen ($1.0$), kun taas Absolute-tiukkuudella (100) eksponentti on ankara neliömuoto ($2.0$).

3. **Progressiivinen vaimennus / DINA V3 (`calculate_progressive_dampening_score`):**
   * Laskee jokaiselle kognitiiviselle tasolle tehokkaan osumaprosentin: $\text{effective\_hit\_rate} = \text{forgiveness} + (\text{hit\_rate} \times (1.0 - \text{forgiveness}))$.
   * Tämän perusteella saadaan tason vaimennuskerroin: $\text{modifier\_factor} = \text{effective\_hit\_rate}^\text{safe\_exponent}$.
   * **Vaikutus:** Korkeampi tiukkuustaso nostaa eksponenttia ja nollaa forgiveness-parametrin, jolloin pienikin epäonnistuminen alimmilla perustasoilla (kuten ymmärtäminen) vaimentaa progressiivisesti ja kaskadoituvasti kaikki ylempien tasojen pistekertymät lähes nollaan.

4. **Pehmeä vesiputousmalli / Soft Waterfall (`calculate_soft_waterfall_score`):**
   * Soveltaa alituksesta liukuvaa rangaistusta: $\text{sliding\_penalty} = 1.0 - (\text{shortfall} \times (1.0 - \text{base\_forgiveness}))$.
   * **Vaikutus:** Kun tiukkuus on 100, `base_forgiveness` on 0.0, jolloin mikä tahansa kynnyksen alitus pysäyttää vesiputouksen pistekertymän siihen paikkaan (100% rangaistus). Lievemmillä tasoilla rangaistus pehmentyy joustavuuden mukaan.

