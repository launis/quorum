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

Kognitiivisen arvioinnin lisäksi järjestelmä suorittaa synteesivaiheessa käyttäjän roolin luokittelun (Matkustaja, Suunnistaja, Kuski, Arkkitehti). Tämä toteutetaan "Hybrid Truth" -mallilla, joka yhdistää deterministisen Python-laskennan ja LLM-päättelyn. Kooditasolla `interaction_hook.py`:ssa tapahtuu tarkalleen seuraavaa:

1. **Deterministinen Ankkuri (Python):** Ensin järjestelmä validoi sisääntulevan datan `InteractionInput`-skeemalla (Pydantic Fail-Fast). Tämän jälkeen se laskee käyttäjän syötteistä matemaattisen `control_ratio`-arvon sekä laajemmat `behavioral_metrics`-mittaristot, joihin kuuluvat `imperative_command_count`, `say_do_gap` ja `automation_bias`.
2. **LLM-Arviointi (Hybrid Truth):** Nämä suhdeluvut syötetään `<execution_parameters>`-tunnisteen sisällä yhdessä puhtaan raakadatan (`<source_data><user_payload>`) kanssa asynkronisesti nopealle LLM:lle (`execute_structured_task`). LLM käyttää tiukkaa Järjestelmäkehotetta, joka ohjaa luokittelemaan käyttäjän roolin tiukasti suhdelukuihin nojaten. Vastauksena palautetaan Pydantic-validoitu `InteractionAnalysisDTO`, jonka on ehdottomasti sisällettävä roolin lisäksi kentät `thought_process`, `conclusion` ja `confidence_score`.
3. **Yhteenvetoon Injektointi:** Senior Executive Coach -synteesikehotteen `STRUCTURAL RIGIDITY` -sääntö pakottaa LLM:n nostamaan tämän roolin raportin toiseen kappaleeseen (esim. "**Käyttäjän Rooli: Arkkitehti**") ja perustelemaan sen suoraan deterministisillä metriikoilla, kuten `control_ratio`.

Tämä arkkitehtuuri takaa, että tekoäly ei voi hallusinoida "Arkkitehti"-roolia tyhjästä, jos deterministiset ankkurit (kuten matala käskymäärä tai matala control_ratio) osoittavat passiivisuutta.
