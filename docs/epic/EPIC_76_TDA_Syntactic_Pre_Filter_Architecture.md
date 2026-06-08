# EPIC 76: TDA Syntactic Pre-Filter Architecture

## 1. Yhteenveto & Tavoite (Executive Summary)

Quorum V2 -järjestelmässä TDA (Test-Driven Assertion) -arviointi luottaa kielimalliin (LLM) sokeana uuttajana (*Semantic Extractor*). Kuitenkin analyysissä ([mismatch_traces_raw.md](file:///c:/src/quorum/scratch/mismatch_traces_raw.md)) on havaittu, että:
1. Kielimalli "venyttää" syntaktisia ankkureita (esim. hyväksyy sanan *"rajoite"* säännössä, jossa vaaditaan ankarasti tarkkaa ilmausta *"rajoituksena on"*).
2. Kielimalli tekee loogisia virheitä käänteisissä ehdoissa (*Negative Conditions*), palauttaen `TRUE` vaikka negatiivinen ehto täyttyy.
3. Kielimallin kutsuminen jokaiselle 186 atomille maksaa latenssia ja API-kustannuksia, vaikka osaa ankkurisanoista ei esiinny lähdetekstissä lainkaan.

**Tavoite:**
* Luoda **TDA Syntactic Pre-Filter** -malli, jossa suurin osa sanakohtaisista ankkuritarkistuksista siirretään Python-tasolle ennen LLM-kutsua.
* Jos vaadittua ankkuria (tai sen sallittuja taivutusmuotoja) ei ole tekstissä, askeleen arviointi merkitään suoraan `FAILED/FALSE`-tilaan ilman LLM-kutsua.
* Tämä nostaa mittauksen konsistenssin lähes 100 %:iin ja nopeuttaa ajoja huomattavasti.

---

## 2. Nykyisten ongelmien tarkka kuvaus

### Kohde A: Kognitiivinen ennakointi ja ankkurien venytys (Semantic Stretching)
* **Kuvaus:** Jos säännössä on määritelty lista ankkureista (esim. `['unohdit', 'lisää vielä', 'korjaa tuo']`), LLM saattaa hyväksyä lauseen *"Ota huomioon..."* tai *"Päätin lisätä..."* perustuen semanttiseen samankaltaisuuteen. Tämä johtaa eri ajokertojen väliseen oskillointiin ja 18.3 %:n varianssiin.
* **Seuraus:** Epätarkat tuomiot, jotka eivät vastaa tiukkoja syntaktisia kriteerejä.

### Kohde B: API-kustannus ja latenssi (Token/Time Waste)
* **Kuvaus:** Järjestelmä suorittaa Map-Reduce-lohkoja (Chunk workers) rinnakkain kaikille atomeille. Suurin osa atomeista (kuten virheiden tai post-hoc-ohitusten etsiminen) palauttaa `FALSE`, koska ankkureita ei ole tekstissä.
* **Seuraus:** Jokainen turha LLM-pyyntö maksaa latenssia (1–3 sekuntia) ja lisää Vertex AI -tokenkuluja, vaikka tulos voitaisiin päätellä millisekunneissa regexillä.

---

## 3. Ehdotetut arkkitehtuurimuutokset

### Osa 1: Deterministinen Pre-Filter Rekisteri (PreFilterRegistry)
* Luodaan Python-tasolle apuluokka `PreFilterRegistry`, joka parsii säännön (TDA Assertion) `<anchors>` tai `<step1_lexical_anchors>` -osiot.
* Rekisteri ylläpitää sääntöjen ankkuritietoja ja osaa suorittaa nopean, suomen kielen morfologian huomioivan hakutarkistuksen (Regex / Lemmatization).

### Osa 2: Monikielinen ankkurien haku (Multilingual Anchor Matching)
* **Ei tarvetta erilliselle kääntäjälle:** Koska järjestelmä tukee monikielisyyttä, TDA-säännöt ([seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json)) sisältävät jo valmiiksi ankkurit molemmilla kielillä XML-rakenteessa (esim. `<anchor>however</anchor><anchor>kuitenkin</anchor>`).
* `PreFilterRegistry` parsii kaikki XML-lapsisolmut `<anchor>`-tagin sisältä ja muodostaa niistä hakulistan.
* Hakulistan sanat normalisoidaan ja etsitään suoraan kohdetekstistä. Tämä tekee pre-filtteristä automaattisesti **monikielisen** ilman riippuvuutta ulkopuolisiin käännösrajapintoihin tai synonyymihakuihin.

### Osa 3: LLMNodeStrategy Pre-Flight -ohjaus
* Tiedostossa [llm.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm.py) askeleen suoritus vaiheistetaan:
  1. **Pre-Flight Filter:** Ajetaan `PreFilterRegistry` arvioitaville atomeille.
  2. **Short-Circuiting:** Jos sääntö vaatii ankkuria, eikä sitä löydy lähdetekstistä millään sallitulla muodolla, asetetaan atomi suoraan tilaan `FALSE` (ja `exact_quote = None`).
  3. **Conditional Execution:** LLM-kutsu (Map-Reduce) suoritetaan *ainoastaan* niille atomeille, joiden vaatimat syntaktiset ankkurit ovat fyysisesti läsnä tekstissä.

---

## 4. Toteutuksen Vaiheet

### Vaihe 1: PreFilterRegistry ja sääntöjen ankkuriparsinta
* Luodaan `backend_v2/services/orchestrator/pre_filter.py`.
* Implementoidaan regex-pohjainen ankkuritunnistus, joka tukee perustaivutuksia (esim. `"rajoite"` -> `"rajoitteena"`, `"rajoituksena"`, `"rajoitukset"`).

### Vaihe 2: Kytkentä LLMNodeStrategyyn
* Päivitetään [llm.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm.py) hyödyntämään esisuodatusta ennen `ChunkWorker`-kutsuja.
* Varmistetaan, että `TraceEvent`- snapshotit tallentuvat oikein myös ohitetuille atomeille.

### Vaihe 3: Testien verifiointi ja profilointi
* Varmistetaan, että yksikkötestit läpäisevät laatuportin.
* Mitataan suoritusajan ja API-kustannusten säästöt simulaatioajossa.

---

## 5. Onnistumisen Kriteerit

* [ ] Kaikki ankkureita vaativat säännöt, joiden ankkureita ei ole tekstissä, päättyvät tilaan `FALSE` millisekunneissa ilman LLM-pyyntöä.
* [ ] Parittainen konsistenssi (Self-Consistency) nousee yli 95 %:iin.
* [ ] Ajon kokonaislatenssi pienenee vähintään 20 %.
* [ ] Kaikki olemassa olevat yksikkötestit läpäisevät backendin auditointisilmukan.
