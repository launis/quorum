# 11: Empiirinen Raportti: Kognitiivinen Pisteytys ja XAI-Synkronisaatio (Sitra Case 2026)

## 1. Johdanto ja Arkkitehtoninen Tavoite
Tämä raportti dokumentoi toukokuussa 2026 suoritetun Tier 4 -tason kognitiivisen arviointimoottorin (Scoring Engine) karkaisun ja validoinnin tulokset. Istunnon päätavoitteena oli varmistaa **SSOT (Single Source of Truth)** -arkkitehtuurin eheys: järjestelmän tekoäly lukee lähdemateriaalin vain kerran (Deep Atomization), ja kaikki myöhempi vaihtelu tuotetaan täysin puhtaan, deterministisen matematiikan ja Pydantic-validoitujen kireystasojen avulla.

Samalla ratkaistiin kriittinen haaste Synteesi-LLM:n käyttäytymisessä ("Compliment Sandwich" -ongelma), sitomalla johdon yhteenvedon sanallinen sävy suoraan asynkronisen Workerin laskemaan lopulliseen, normalisoituun matemaattiseen arvosanaan.

## 2. Matemaattiset Vaihteet (The 4 Gears)
Quorum V2 käyttää neljää eri laskentamoottoria. Nämä algoritmit toimivat "linsseinä", joiden läpi sokea raakadata (osumat / väitteet) katsotaan:

1. **Syväarvostelu (Progressive Dampening - DINA V3):** 
   Tämä moottori hyödyntää lineaarista interpolaatiota (Lerp) lieventääkseen alempien kognitiivisten tasojen puutteita kaavalla: `effective_hit_rate = base_forgiveness + (hit_rate * (1.0 - base_forgiveness))`. Vaimennukseen sovelletaan kireystason perusteella dynaamista eksponenttia, jolloin täydellinenkään ylemmän tason suoritus ei voi kompensoida täysin murentunutta perustaa, mutta pisteet eivät romahda absoluuttisesti nollaan yksittäisen virheen takia. Etsii loogisen ketjun heikoimman lenkin.
2. **Koearvostelu (Soft Waterfall - Guttman V3):** 
   Tiukka compliance-moottori. Ehdoton portinvartija. Jos tavoitekynnys (threshold) alitetaan, järjestelmä ei enää lukitse koko pisteytystä "rikkinäisiin tikapuihin", vaan laskee vajauksen (`shortfall`) ja soveltaa **liukuvaa rangaistuskerrointa** (sliding penalty multiplier) kaikkiin myöhempiin tasoihin kaskadoituvasti.
3. **Painotettu Keskiarvo (Sigmoid Scaling):** 
   Laskee matriisin tason perusteella painotetun suhdeluvun ja skaalaa tuloksen ulos **Sigmoid (logistic) -käyrällä**: `raw_sigmoid = 1 / (1 + math.exp(-steepness * (hit_rate - midpoint)))`. Kireystaso liikuttaa Sigmoidin keskipistettä, jolloin tiukempi kireystaso vaatii eksponentiaalisesti puhtaampaa osumaprosenttia korkean arvosanan saamiseksi. Järjestelmä suorittaa täyden matemaattisen normalisoinnin absoluuttisten ääripäiden väliin.
4. **Lineaarinen Keskiarvo (MAD Outlier Rejection):** 
   Puhtaassa keskiarvossa järjestelmä on alttiimpi datapisteille, jotka heikentävät muuten vahvaa profiilia. Tämä moottori tunnistaa tilastolliset anomaliat hyödyntämällä **Median Absolute Deviation (MAD)** -menetelmää. Jos yksittäinen taso poikkeaa merkittävästi aggregaatin mediaanista (`hit_rate < median - 3.0 * MAD` ja `hit_rate < 0.30`), tason painoarvoa alennetaan (0.25x), suojellen näin kokonaisarvosanaa perusteettomilta romahduksilta.

## 3. Empiirinen Testiajo (Sitra Supermegatrendit)
Testasimme moottoria syöttämällä sille täysin identtisen tekoälyn suorittaman raaka-analyysin. Muutimme ainoastaan arviointimoottoria ja tiukkuusparametreja (0–100). Tulokset paljastivat arkkitehtuurin valtavan tehon:

### Skenaario A: "Säälimätön Auditoija"
* **Moottori:** Syväarvostelu (Dampening)
* **Tiukkuus:** 100 (Absoluuttinen)
* **Arvosana:** **7.00 / 100.00**
* **Havainto:** DINA-moottori havaitsi perustan ontuvan (falsifioinnin puute ja keksitty päivämäärä) ja vaimensi armotta kaikki ylempien tasojen onnistumiset nollaan. Tulos oli absoluuttinen hylkäys.

### Skenaario B: "Portinvartija"
* **Moottori:** Koearvostelu (Waterfall)
* **Tiukkuus:** 100 (Absoluuttinen)
* **Arvosana:** **44.40 / 100.00**
* **Havainto:** Koska perusosumia oli jonkin verran, Guttman-moottori salli alatasojen pisteet, mutta sulki ylemmät tasot liukuvalla rangaistuksella, kun näyttö (keksitty päivämäärä) petti. Tuloksena hylätty, mutta ei nollattu suoritus.

### Skenaario C: "Kultainen Keskitie"
* **Moottori:** Painotettu Keskiarvo
* **Tiukkuus:** 50 (Tasapainoinen)
* **Arvosana:** **64.20 / 100.00**
* **Havainto:** Perustason onnistumisille (esim. "supermegatrendien" innovaatio) annettiin painoarvoa, ja Sigmoid-skaalaus pehmensi virheitä. Arvosana ylsi niukasti, mutta varmasti tyydyttävälle tasolle.

### Skenaario D: "Sokea Cheerleader"
* **Moottori:** Koearvostelu (Waterfall)
* **Tiukkuus:** 0 (Täysi joustavuus)
* **Arvosana:** **100.00 / 100.00**
* **Havainto:** Kynnysarvot laskettiin nollaan. Kaikki minimaalinenkin osumadata riitti laukaisemaan hyväksynnän. Faktojen keksintää ja puutteellista logiikkaa ei rankaistu lainkaan.

## 4. XAI-Synkronisaatio ja Dynaaminen Sävy (Tone Continuum)
Pelkkä matematiikka ei riitä, jos XAI-tekstisynteesi ei tue sitä. Ongelmana oli perinteinen LLM-käyttäytyminen: tekoäly pyrki automaattisesti pehmentämään heikkoa 7.00 tulosta aloittamalla raportin kohteliailla kehuilla ("Compliment Sandwich").

Tämä ratkaistiin injektoimalla asynkronisen Workerin tuottama `normalized_score` suoraan Synteesi-LLM:n rakenteelliseen promptiin, luoden 4-portaisen **Score-Driven Tone Continuum** -arkkitehtuurin:

1. **0 - 39 (Catastrophic Failure):** Nollatoleranssi kehuille. Aloittaa suoraan rakenteellisen romahduksen toteamisella.
   * *Esimerkki (Arvosana 7.00):* "Tämä analyysi... jää puolitiehen. Suurin sokea pisteesi on kriittisen validoinnin täydellinen puute. Et missään vaiheessa haastanut luomasi mallin kestävyyttä... paljastaa myös huolimattomuutta."
2. **40 - 69 (Mediocre / Flawed):** Kliininen ja jämäkkä. Tunnustaa lähtötason, mutta siirtyy heti virheisiin.
   * *Esimerkki (Arvosana 64.20):* "Osoittaa kykyä siirtyä pelkästä tiedonkeruusta kohti synteesiä... toteutus jää kliinisen arvion mukaan keskinkertaiseksi. Suurin sokea piste on kriittisen validoinnin ja älyllisen nöyryyden täydellinen puuttuminen."
3. **70 - 89 (Strong / Competent):** Rakentava valmennus, vahvistaa osaamista.
4. **90 - 100 (Mastery / Excellent):** Äärimmäisen vahvistava, keskittyy ylläpitävään huipputason ohjaukseen.

## 5. Yhteenveto: Zero-Math ja Opaque Integrity
Tämä arkkitehtuurikokonaisuus varmistaa kaksi 2026 Zero-Legacy -mandaatin ydintavoitetta:
1. **Zero-Math UI:** Käyttöliittymä (Flutter) vastaanottaa valmiit laskelmat ja tekstit, eikä sen tarvitse koskaan purkaa matemaattista logiikkaa selaimeen.
2. **Kognitiivinen Pariteetti:** Matematiikka, arviointimatriisit ja tekoälyn ihmiskielinen palaute ovat saumattomassa, todistettavassa synkronissa. Tekoäly haukkuu vain, jos matematiikka antaa siihen luvan, ja perustelee ankaran palautteensa (*"keksitty päivämäärä"*) suorilla, auditoitavilla lainauksilla raakadatasta.
3. **100 % Determinismi ja Kognitiivinen Eristäminen:** "Hardened 2.0" -päivityksen myötä LLM ei enää toimi "tulkitsevana lukijana", vaan säälimättömänä yksittäisten boolean-väitteiden (TDA) etsijänä (Bounty Hunter -malli). Kun tähän yhdistetään LLM:n nollalämpötila (`temperature=0.0`), DAG-pohjainen suorituksen eristäminen `PromptBlock`-tasolla ja matematiikan siirtäminen täysin Pythonin puolelle, koko järjestelmä saavuttaa käytännössä täydellisen (99,9 %) determinismin. Kyselyjen suoritusjärjestyksen muuttaminen ei enää aiheuta aiemmin havaittua huomiokyvyn harhautumista (Attention Drift), sillä kyselyt on eristetty toisistaan ja ne nojaavat puhtaaseen TDA-tekstinhakuun.

## 6. Teorialähteet ja Käyttötapaukset (Use Cases)

Jokainen moottori pohjautuu validioituun kognitiiviseen tai tilastolliseen teoriaan, ja niillä on tarkasti rajatut optimaaliset käyttötapaukset liiketoiminnassa:

### A. Syväarvostelu (DINA V3 / Progressive Dampening)
* **Teoriapohja:** Cognitive Diagnostic Models (CDM), erityisesti DINA (Deterministic Inputs, Noisy "And" gate). DINA olettaa, että korkeamman tason onnistuminen vaatii ehdottomasti kaikkien alempien taitojen hallintaa.
* **Optimaalinen Käyttötarkoitus:** "Ketjunheikkouden etsiminen" ja kriittinen riskienhallinta.
* **Käytännön Esimerkki:** **Lääketieteellinen tai juridinen analyysi.** Vaikka loppupäätelmä (Taso 5) olisi kuinka nerokas ja innovatiivinen, se on täysin arvoton ja jopa vaarallinen, jos sen taustalla oleva faktantarkistus (Taso 1) pettää. DINA romahduttaa arvosanan ja estää "vaarallisen innovaation" menemästä läpi.

### B. Koearvostelu (Guttman V3 / Soft Waterfall)
* **Teoriapohja:** Guttmanin asteikko (Cumulative scale). Teoria olettaa kumulatiivisen osaamisen: tason 4 suorittajan odotetaan automaattisesti osaavan tasot 1, 2 ja 3.
* **Optimaalinen Käyttötarkoitus:** "Portinvartija", pätevyyskokeet ja ISO-sertifioinnit.
* **Käytännön Esimerkki:** **Turvallisuus- ja Compliance-auditointi.** Jos työntekijä epäonnistuu pakollisessa turvallisuusprotokollassa (Taso 1), hän ei voi "korvata" tätä puutetta kirjoittamalla hyvän esseen johtamisesta (Taso 4). Guttman pysäyttää arvioinnin nousemisen, mutta säästää alatasojen pisteet liukuvalla rangaistuksella (ei absoluuttista nollausta).

### C. Painotettu Keskiarvo (Sigmoid Scaling)
* **Teoriapohja:** Logistinen funktio (Sigmoid-käyrä) ja normaalijakauman mukainen skaalaus. Arvosanat vakioidaan pehmeästi ääripäiden väliin.
* **Optimaalinen Käyttötarkoitus:** "Kultainen keskitie" ja valmentava palaute.
* **Käytännön Esimerkki:** **Ideointi, innovaatiotyöpajat ja strateginen aivoriihi.** Tässä halutaan palkita luovuudesta ja uusista avauksista (esim. uusi supermegatrendi). Vaikka perusteluissa olisi pieniä aukkoja, Sigmoid-skaalaus pehmentää virheitä ja tuottaa motivoivan, rakentavan arvosanan (esim. 64.20), joka kannustaa iterointiin.

### D. Lineaarinen Keskiarvo (MAD Outlier Rejection)
* **Teoriapohja:** Robustit tilastomenetelmät, erityisesti Median Absolute Deviation (MAD), jota käytetään tilastollisten anomalioiden (outliers) suodattamiseen keskiarvosta.
* **Optimaalinen Käyttötarkoitus:** Massadatan suodatus ja suurten organisaatioiden arviointi.
* **Käytännön Esimerkki:** **Globaalin henkilöstökyselyn synteesi.** Jos 9 osastoa tekee erinomaista työtä, mutta 1 osasto epäonnistuu täysin (koska he ymmärsivät kyselyn ohjeistuksen väärin), perinteinen keskiarvo romahtaisi. MAD tunnistaa tämän yhden epäonnistumisen "anomaliaksi" ja pienentää sen painoarvoa, suojellen koko yrityksen globaalia arvosanaa perusteettomalta romahdukselta.

## 7. Hybrid Truth ja Käyttäjän Roolin Luokittelu (Passenger -> Architect)

Kognitiivisen arvioinnin lisäksi järjestelmä suorittaa synteesivaiheessa käyttäjän roolin luokittelun (Matkustaja, Suunnistaja, Kuski, Arkkitehti). Tämä toteutetaan **"Hybrid Truth"** -mallilla, joka yhdistää deterministisen Python-laskennan ja LLM-päättelyn:

1. **Deterministiset Metriikat (Python):** Ensin järjestelmä validoi sisääntulevan datan `InteractionInput`-skeemalla (Pydantic Fail-Fast). Tämän jälkeen se laskee käyttäjän syötteistä matemaattisen `control_ratio`-arvon sekä laajemmat `behavioral_metrics`-mittaristot (kuten `imperative_command_count`, `say_do_gap` ja `automation_bias`). *Huomaa: Taustajärjestelmä ei itse tee staattista if-else -luokittelua koodissa.*
2. **LLM-Arviointi ja Hybrid Truth Mandate:** Nämä Pythonin laskemat suhdeluvut ja metriikat syötetään `<execution_parameters>`-tunnisteen sisällä yhdessä raakadatan (`<source_data><user_payload>`) kanssa asynkronisesti nopealle LLM-suorittimelle (`execute_structured_task`). LLM tekee lopullisen rooliluokittelun `InteractionAnalysisDTO`-rakenteeseen. LLM:ää ohjaa ankara järjestelmäkehote, joka pakottaa sen kunnioittamaan näitä matemaattisia rajoja (esim. jos käyttäjän `control_ratio` on matala, tekoälyltä on evätty oikeus luokitella hänet *Arkkitehdiksi*, olipa hänen sävynsä kuinka käskevä tahansa).
3. **Yhteenvetoon Injektointi:** Senior Executive Coach -synteesikehotteen `STRUCTURAL RIGIDITY` -sääntö pakottaa LLM-synteesin nostamaan tämän roolin raportin toiseen kappaleeseen (esim. "**Käyttäjän Rooli: Arkkitehti**") ja perustelemaan sen suoraan näillä numeerisilla metriikoilla.

Tämä arkkitehtuuri takaa, että rooli perustuu koviin käyttäytymistodisteisiin ja ankkuroituu matemaattiseen todellisuuteen, vaikka itse luokittelu suoritetaankin kielimallin hybridi-päättelyportissa.

## 8. Ohjeet Tarkan Manuaalisen Auditoinnin Toteuttamiseen

Tämä osio tarjoaa askeleittaisen ohjeistuksen siitä, miten auditoija tai analyytikko voi itsenäisesti ja manuaalisesti jäljittää ja varmistaa järjestelmän tuottaman arvioinnin ilman koodin kirjoittamista. Prosessi perustuu suoraan tietokannan (`db_v2.json`) ja suorituslokin (`execution_trace.json`) rakenteiden lukemiseen.

### Vaihe 1: Aineiston ja Alkutilan Varmistus
Ennen matemaattisen pisteytyksen tarkistamista on varmistettava, että analysoitava raakadata on oikeaa.
1. **Etsi suoritustunnus (Execution ID):** Paikanna analysoitava suoritus (esim. `exe_b6c7f868eccf4e8988889daf3ae1dfd4`) tietokannasta `data/db_v2.json` avaimella `executions`.
2. **Tarkista syötteet (Raw Inputs):** Siirry kyseisen ajon `raw_inputs`-tietueeseen ja varmista, että sieltä löytyvät seuraavat kolme ydinkenttää:
   * `product_text`: Käyttäjän tuottama lopputuotos (esim. Sitra-megatrendianalyysi).
   * `chat_log`: Käyttäjän ja tekoälyn välinen keskusteluhistoria.
   * `reflection_text`: Käyttäjän tekemä reflektio omasta roolistaan ja toiminnastaan.
3. **Varmista, ettei baseline-dataa ole muokattu:** Tarkista `executions`-tietueen `status`-arvo. Sen on oltava `completed`. `execution_trace`-polun on osoitettava muuttumattomaan tiedostoon `frozen_context.json`.

### Vaihe 2: TDA-Väitteiden (Test-Driven Assertions) ja Osumien Auditointi
1. **Paikanna evaluointisolmut (`step_states`):** Avaa `execution_trace.json` tai vastaava `step_states`-tietokantarakenne.
2. **Etsi matriisien yksittäiset askeleet:** Etsi askeleet, joiden `step_id` alkaa tunnisteella `sr_` (esim. `sr_d56fb84fbe13463a`). Jokainen tällainen askel edustaa yhden arviointimatriisin (esim. Argumentation Matrix, Logic & Reasoning Matrix) suoritusta.
3. **Varmista sokeiden osumien audit-loki (`evaluations`):** Etsi askeleen payloadista `evaluations`-lista. Jokaisen alkion (TDA-atomin) kohdalla on tarkistettava:
   * **`tda_assertion_id`:** Yksilöllinen tunniste (esim. `tda_a1b2c3d4`).
   * **`rule_satisfied`:** Deterministinen Boolean-arvo (`true` / `false`), joka on laskettu backendin koodissa.
   * **`exact_quote`:** Suoritusvaiheessa tekoälyn dokumentista poimima sanatarkka lainaus. Varmista manuaalisesti, että lainaus löytyy sellaisenaan raakasyötteestä (`product_text` tai `chat_log`). Jos lainaus poikkeaa kosmeettisesti, tarkista että `AnchorValidationService` on suorittanut onnistuneen RapidFuzz-kohdistuksen (fuzz-indeksit löytyvät trace-lokista).
   * **`semantic_reasoning`:** Tekoälyn tuottama lyhyt perustelu sille, miksi sääntö täyttyy tai ei täyty.

### Vaihe 3: Matemaattisen Yhteismitallisen Keskiarvon (Commensurate Average) Laskenta
Auditoijan on kyettävä toistamaan pisteytys käsin varmistaakseen backendin laskentakaavojen eheyden:
1. **Pessimistinen DLQ-osumatarkkuuden laskenta (0/1):** Varmista, ettei DLQ-tilaisten säännösten määrää poisteta nimittäjästä (Denominator), toisin kuin vanhassa arkkitehtuurissa optimistisesti tehtiin. Jokainen DLQ-tilaan päätynyt sääntö pisteytetään matemaattisesti nollana (0/1) pessimistic & reliable scoring -periaatteella. Tämä varmistaa, ettei matriisin arvosanaa paranneta silloin, kun data on viallista. Matriisille asetetaan käyttöliittymää varten keltainen "Puutteellinen data" -merkintä (Data Quality Flag).
2. **Varmista Indeterminate-kynnysraja (10 % katto):** Ennen lopullista pisteytystä on varmistettava, ettei DLQ-tilaisten sääntöjen määrä ylitä 10 % rajapintaa. Jos `dlq_count / total > 0.10`, koko matriisi on asetettava suoraan tilaan `INDETERMINATE`. Järjestelmä ei tällöin yritä laskea numeerista arvosanaa, vaan matriisi merkitään määrittelemättömäksi laadun ja eheyden takaamiseksi.
3. **Kerää evaluoitavat matriisit:** Etsi `step_states`-rakenteesta kaikki askeleet, joissa on lohko `_evaluative_matrices`. Nämä ovat matriiseja, joiden `is_evaluative` on tietokannassa määritetty arvoksi `true`.
4. **Hae kunkin matriisin normalisoitu arvosana:** Jokaisesta evaluoitavasta matriisista on laskettu ja tallennettu normalisoitu arvosana (asteikolla 0–100) avaimella `normalized_score` (tai `score_normalized` riippuen Output Profilen projisoinnista).
5. **Laske keskiarvo:** 
   $$\text{Kokonaisarvosana} = \frac{\sum_{i=1}^{N} \text{Matriisin normalisoitu arvosana}_i}{N}$$
   Missä $N$ on evaluoitujen matriisien kokonaismäärä (Sitra Case -ajossa $N = 7$).
   * *Esimerkki:* Jos 7 matriisin normalisoidut arvosanat ovat esimerkiksi: 44.40, 25.00, 30.00, 50.00, 20.00, 46.38 ja 40.00, niiden summa on $255.78$. Jaettuna 7:llä saadaan tismalleen $36.5397$ eli pyöristettynä **36,54 %**.
6. **Varmista, ettei rangaistuksia ole jätetty soveltamatta:** Varmista `penalties_applied`-listasta, onko järjestelmä havainnut turvallisuusuhkia (`threat_detected`) tai jälkikäteistä rationalisointia. Jos on, vähennä rangaistuskertoimet (esim. 10 % tai 25 % penalty capin rajoissa) saavuttaaksesi lopullisen pistemäärän.

### Vaihe 4: Roolin (Hybrid Truth) Luokittelun Auditointi
Käyttäjän roolin luokittelu ("Passenger" $\rightarrow$ "Architect") on pystyttävä todentamaan matemaattisesti:
1. **Tarkista `control_ratio`:** Etsi lokista deterministinen arvo `control_ratio` (laskettu käyttäjän syötteiden suhteesta tekoälyn tuotoksiin).
   * **Heuristiset tavoiterajat tekoälyn System Instructions -säännöissä:**
     * Jos `control_ratio < 0.20`, käyttäjän roolin on oltava **Matkustaja (Passenger)**.
     * Jos `0.20 <= control_ratio < 0.50`, roolin on oltava **Suunnistaja (Navigator)**.
     * Jos `0.50 <= control_ratio < 0.80`, roolin on oltava **Kuski (Driver)**.
     * Jos `control_ratio >= 0.80` ja `imperative_command_count > 5`, roolin on oltava **Arkkitehti (Architect)**.
   * *Huomaa luokittelun hybridiluonne:* Luokittelua ei suoriteta kovakoodatuilla if-else -rakenteilla Pythonissa, vaan Python laskee kovat metriikat ja kielimalli tekee luokituksen näitä ehtoja orjallisesti noudattaen (Hybrid Truth Mandate).
2. **Roolin ja Perustelujen Vastaavuus:** Varmista, että `profile_syntheses`-lohkon ihmiskielisessä palautteessa mainittu rooli vastaa tismalleen tätä luokittelua, ja että se perustellaan suoraan kyseisillä numeerisilla käyttäytymismetriikoilla.

### Vaihe 5: XAI-Synteesin ja Teoria-Ankkuroinnin Laadullinen Auditointi
Lopuksi auditoidaan ihmiskielisen raportin ja tieteellisen viitekehyksen vastaavuus:
1. **Tarkista sävyn jatkumo (Tone Continuum):**
   * Jos kokonaisarvosana on alle 40 %, varmista, että raportin sävy on täysin kompromissiton ("Säälimätön Auditoija"), eikä se sisällä lieventäviä "Compliment Sandwich" -rakenteita.
   * Jos arvosana on 40–69 %, varmista, että sävy on kliininen ja rakentava, tuoden esiin vahvuuden ("Supermegatrendit") mutta siirtyen heti pedagogisesti virheisiin.
2. **Varmista tieteellisten teorioiden integrointi:**
   * **Daniel Kahneman (Systeemi 1 & Systeemi 2):** Varmista, että raportti arvioi käyttäjän kykyä pakottaa tekoäly hidastamaan automaattisesta ja laiskasta assosiaatiopäättelystä (Systeemi 1) kohti tietoista, analyyttista ja strukturoitua päättelyä (Systeemi 2).
   * **Stephen Toulmin (Argumentaatiomalli):** Tarkista, että raportissa analysoidaan väitteiden taustoja (Backing), takeita (Warrant) ja perusteita (Grounds). Etsi maininnat siitä, miten väitteet on ankkuroitu lähteisiin.
   * **Karl Popper (Falsifiointiperiaate):** Varmista, että raportti arvioi kriittisesti sitä, pyrkeekö käyttäjä aktiivisesti etsimään sokeita pisteitä ja vastaesimerkkejä (falsifioimaan tekoälyn väitteitä) vai tyytyykö hän pelkkään verifiointiin (mielistelyn hyväksymiseen).

Tämän 5-vaiheisen auditoinnin suorittaminen antaa analyytikolle aukottoman ja matemaattisesti todistettavan varmistuksen siitä, että järjestelmä on toiminut täysin deterministisesti ja laadukkaasti.
