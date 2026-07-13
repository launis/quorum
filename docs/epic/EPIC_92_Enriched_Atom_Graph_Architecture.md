# Epic 92: Enriched Atom Graph Architecture (Vaihe 2/3)

> [!CAUTION]
> **RIIPPUVUUSVAROITUS:** Tämä on vaihe 2/3 uudesta arkkitehtuurista. Epic 91.5 (DTO Bridge) on oltava täysin implementoituna ja tuotannossa ENNEN kuin tämän Epicin moottoria aletaan rakentaa. Tämän Epicin uusi DAG-moottori on rakennettava tuottamaan puhdasta `ReportDataDto` -objektia. Vanha järjestelmä on samalla tuhottava ilman fallback-polkua.

> [!IMPORTANT]
> **THE CONTEXT-LOSS PARADOX RESOLUTION MANDATE**: Atomien flattauksen aiheuttama referenttien menetys (Anaphora) ja ehdollisuuden hajoaminen (Conditional Logic Decoupling) on ratkaistava ilman flat-list -arkkitehtuurin hylkäämistä. Järjestelmän tulee suorittaa "Enriched Atom Graph" -pipeline: 1. Probabilistinen LLM Resolution -passi (Anaphora + Condition -tunnistus) ja 2. Deterministinen Pydantic- ja Python-ohjattu ehdollinen arviointi.

## Strateginen Merkitys

Epic 92 muuttaa Quorumin **arviointityökalusta argumentaation analytiikka-alustaksi** — positio, jolla ei tällä hetkellä ole suoraa kilpailijaa. Tämä tapahtuu lisäämällä FActScoren ja SAFE:n (Google DeepMind) atomisen verifioinnin päälle kolme uniikkia kerrosta: **kausaalinen DAG-graafi**, **ehdollinen logiikka (N/A-tila)** ja **automaattiset korjausehdotukset**.

**Sovellusalueet:**

| Alue | Kohderyhmä | Ydinlupaus |
|---|---|---|
| **Koulutus** | Korkeakoulut, kouluttajat | Rakenteellinen palaute argumentaatiosta, ei pelkkä "oikein/väärin" |
| **Sääntely (ESG / EU AI Act)** | Compliance, tilintarkastus | Automaattinen todennettavuuskerros; EU AI Act Art. 13 & 14 |
| **Journalismi** | Toimitukset, faktantarkistus | Lähteen väitteen ja kirjoittajan tulkinnan automaattinen erottelu |
| **Tutkimus** | Yliopistot, tutkimuslaitokset | DAG paljastaa logiikkavirheet argumentaation rakenteessa |
| **Sisäinen laatu** | Yritykset, organisaatiot | Subjektiivisten päätösten tunnistaminen ja dokumentointi |

**Perustelut:**
- **Tieteellinen:** FActScore (EMNLP 2023), SAFE (DeepMind 2024), System 2 Attention (Meta AI 2023) — Epic 92 on näiden evoluutio, ei keksintö
- **Regulatorinen:** EU AI Act Art. 13 (läpinäkyvyys), CSRD-direktiivi (todennettavuus), ISO 42001 (AI-hallintajärjestelmä)
- **Kilpailullinen:** Yksikään työkalu ei yhdistä atomista purkua + kausaalista graafia + ehdollista logiikkaa + automaattisia korjausehdotuksia

---

## 1. Yhteenveto ja Tavoite (Objective)

Tämän kehityskokonaisuuden (Epic) tavoitteena on ratkaista arkkitehtuurinen haaste, jossa tekstin purkaminen erillisiksi väitteiksi (litistäminen, "Atom-Flattening") kadottaa ihmiskielen semanttiset riippuvuudet. Tämä aiheuttaa vääriä positiivisia ja negatiivisia tuloksia arviointimoottorin (Scoring Engine) pisteytysvaiheessa.

### Nykytilan Ongelma:
* **Viittaussuhteiden katkeaminen (Anaphora Resolution Failure)**: Lause "Se aiheutti tietokannan kaatumisen" menettää alkuperäisen kontekstinsa litteässä tietorakenteessa.
* **Ehdollisen logiikan hajoaminen (Conditional Logic Decoupling)**: Ehtolause "Jos järjestelmä vaarantuu, data poistetaan" purkautuu kahdeksi erilliseksi absoluuttiseksi väitteeksi. Jos dataa ei ole poistettu (koska järjestelmä ei alun perinkään vaarantunut), arviointimoottori rankaisee järjestelmää virheellisesti "Data poistetaan" -väitteen täyttymättömyydestä.
* **Semanttinen pirstaloituminen (Semantic Disjointedness)**: Yksittäiset irralliset faktat voivat erikseen olla tosia, mutta yhdistettyinä ne muodostavat alkuperäistä kontekstia vastoin olevan kokonaisuuden.

### Ratkaisu:
Luodaan rikastettu kausaaliverkko (Enriched Atom Graph), joka palauttaa semanttisen rakenteen litistettyyn luetteloon metatiedon avulla:
1. **Kontekstin ratkaisuvaihe (Resolution Pass) ennen litistämistä**: Kielimalli (LLM) ohjeistetaan ratkaisemaan pronominit eksplisiittisesti alkuperäisiksi entiteeteiksi ja tunnistamaan ehdollisuudet osana yksittäistä väitettä.
2. **Tietomallin päivitys (Pydantic Schema Update)**: Väiterakenne päivitetään tukemaan eksplisiittisiä ehtoja (`conditions`), puhdistettuja väitteitä (`resolved_claim`) ja riippuvuuksia (`depends_on_atom_ids`).
3. **Deterministinen arviointikoukku (Deterministic Evaluation Hook)**: Python-pohjainen suoritusmoottori tarkistaa ehdollisten väitteiden kohdalla edellytysten täyttymisen ensin. Jos alkuperäinen ehto ei toteudu, itse väitteen arviointi ohitetaan (oikosulkukaskadi, short-circuit cascade) loogisesti.

---

## 2. Arkkitehtuuristen sääntöjen huomiointi (Compliance Matrix)

* **01-python-backend.md (Fail-Fast Pydantic V2)**: Uudet `EnrichedAtom` ja `ClaimCondition` -luokat luodaan Pydantic V2:lla tiukkojen `ConfigDict(extra='forbid', strict=True)` -määritysten kanssa. 
* **05_llm_architecture.md (LLM Structured Execution)**: Resolution Pass ei palauta vapaata tekstiä, vaan se pakotetaan käyttämään Native Structured Outputs API:a (`LLMTaskExecutor.execute_structured_task()`) EnrichedAtom-muotoon.
* **Epic 91.5 Opit (Referential Integrity)**: Epic 91.5:ssä luotu `ReportDataDto` on erittäin tiukka (`strict=True, frozen=True`). Moottorin ulostulon on oltava puhdas Pydantic V2 -yhteensopiva rakenne. DAG-moottori vastaa orpojen graafiviittausten (hallusinoidut ID:t) siivoamisesta *ennen* lopullista DTO-konversiota, jotta `ReportDataDto`:n sisäinen referenssieheys-check ei räjähdä tuotannossa.
* **Epic 91.5 Opit (Anti-TDD Trap)**: Kun DAG-moottori rakennetaan, kymmenet vanhat arviointimoottorin testit alkavat kaatua. Kiusaus rakentaa moottoriin "legacy-yhteensopivuuskerros" pelkkien vanhojen (esim. `evidence_quotes` -juuritason) testien miellyttämiseksi on suuri. Epic 92:ssa meidän pitää uskaltaa poistaa vanhat mock-testit kokonaan ja luoda uudet *Golden Masterit*, jotka noudattavat uutta DAG-logiikkaa.
* **Epic 91.5 Opit (QuoteEvidenceDTO Deprecation)**: LLM-promptit eivät saa ohjeistaa AI:ta tuottamaan "globaalia lainauslistaa" raportin loppuun. AI:n tulee generoida Anaphora-passin yhteydessä puhtaita `tda_id` -viittauksia muihin atomeihin tai dokumentin lähteisiin, jotka DAG-moottori asettaa suoraan atomien sisälle.
* **00-antigravity-core.md (Zero-Compromise Pledge)**: Evaluation Hookit on kirjoitettava natiivisti Pythonilla. Järjestelmä ei saa luottaa LLM:n subjektiiviseen "ehdolliseen ymmärrykseen" arviointivaiheessa, vaan Python DAG päättelee ehtojen täyttymisen.
* **Forensic Immutability Mandate**: `source_quote` -kenttä on MUUTTUMATON (immutable). Resolution Pass EI SAA koskaan ylikirjoittaa tai muokata alkuperäistä lainausta generoidessaan `resolved_claim`-kenttää. Molemmat kentät on säilytettävä rinnakkain, koska `source_quote` on forensinen todistusaineisto ja `resolved_claim` on järjestelmän tulkinta siitä. Ilman molempia järjestelmän debuggaus ja auditointi on mahdotonta.
* **Reason-then-Format Mandate (Tam et al., EMNLP 2024)**: Skeeman kenttäjärjestys on kriittinen. LLM:n tulee tuottaa ensin vapaamuotoinen päättely (`resolved_claim`) ja vasta sitten strukturoitu metadata (`conditions`, `depends_on_tda_ids`). Tämä estää "Format Tax" -ilmiön, jossa tiukka skeemarakenne heikentää LLM:n analyyttistä syvyyttä.
* **Probabilistic Condition Evaluation Mandate (Language Variance)**: Aiempi oletus deterministisestä merkkijonohausta (regex) ehtojen täyttymisessä on kumottu kielen äärettömän varianssin vuoksi. Kuitenkin myös vektorihaku (Cosine Similarity) on ankarasti kielletty, koska se tuottaa vääriä positiivisia vastakkaisille väitteille (esim. "on" vs. "ei ole"). Ehdon arviointi suoritetaan deterministisen `ExtractiveSensorService`:n tai **dedikoidun Boolen LLM-kutsun** avulla (esim. Haiku).

### 2.1 Epistemic Boundaries (Tiedolliset Rajat)
Estääksemme järjestelmätason hallusinaatiot, meidän on armottomasti valvottava rajaa sen välillä, mitä LLM saa arvata ja mitä Pythonin on pakko todistaa (Separation of Concerns).

**100% Deterministic (Vaatii tiukan Python/Pydantic-logiikan):**
* **DAG Structural Integrity:** Syklin tunnistus (Cycle detection, O(V+E) DFS) ajetaan Pythonissa. LLM ei koskaan verifioi omaa graafitopologiaansa.
* **Stateful Short-Circuiting (N/A Cascade):** Tilan `N_A - Condition Not Met` eteneminen. Jos Python vastaanottaa tiedon, että Ehto A on epätosi, Python **deterministisesti pysäyttää** Seurauksen B suorituksen (`N_A` tai `BLOCKED`). LLM:llä on nolla (0) reititysvaltaa suoritusaikana.

**Fundamentally Probabilistic (Vaatii LLM-päättelyä):**
* **Causal Edge Mapping (Two-Pass ID-Mapping):** Sen semanttisen suhteen päätteleminen tekstistä, joka määrittää että Väite B riippuu loogisesti Väitteestä A.
* **Implicit Anaphora:** Abstraktien tai toimialakohtaisten pronominien purkaminen (anaforan ratkaisu, anaphora resolution), missä deterministinen perinteinen NLP kaatuu.
* **Boolean Sensor (Väitteen arviointi):** LLM toimii yksinomaan sensorina, joka palauttaa vapaamuotoisesta väitelauseesta probabilistisen totuusarvon (Tosi/Epätosi). Python-kerros ottaa tämän Boolean-arvon vastaan ja hoitaa deterministisen reitityksen. LLM ei koskaan itse päätä ehdollisesta ohituksesta.

## 3. Pydantic-tason Mallit ja Suunnittelu (Proposed Schema Parity)

> [!IMPORTANT]
> **KORJATTU:** Kausaalinen malli tukee odotettuja tiloja (Negative Conditions) deterministisen oikosulun varmistamiseksi. Syylliset vanhemmat tallennetaan listana audit-eheyden takia.

```python
from pydantic import Field, BaseModel, ConfigDict
from typing import Optional, List, Literal

class CausalEdge(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)
    edge_reasoning: str = Field(description="Chain-of-thought: LLM:n päättely siitä, miksi tämä kausaalisuhde on olemassa (Reason-then-Format).")
    tda_id: str = Field(description="Vanhemman atomin")
    source_id: str
    expected_status: ExecutionStatus = Field(default=ExecutionStatus.PASSED),
        description="Mahdollistaa negatiiviset ehdot."
    )
    # HUOM: edge_confidence on poistettu arkkitehtuurisäännöksellä (LLM Hallusinaatioriski).
    # Tasapelit / syklinkatkaisut ratkaistaan deterministisesti lokaalin `chunk_index` mukaan.

# 1. IMMUTABLE DOMAIN MODEL - VAIHE 1 (Staattinen louhintatulos)
class ExtractedAtom(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    reasoning: str = Field(description="Chain-of-thought: anaforan ja väitteen purkamisen päättely.")
    resolved_claim: str = Field(description="Puhdistettu väite")
    source_quote: str = Field(description="Sanatarkka lainaus alkuperäisestä tekstistä.")
    tda_id: str = Field(pattern=r"^tda_[a-fA-F0-9]{16,32}$")
    source_id: str | None = Field(description="Spatiaalinen ankkuri (Chunk ID).")

# 2. IMMUTABLE GRAPH WRAPPER - VAIHE 2 (Graafin topologia)
class LinkedAtomGraph(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    atom: ExtractedAtom
    depends_on: List[CausalEdge] = Field(
        default_factory=list, 
        description="Implisiittinen AND-lista. Atomi arvioidaan vain, jos kaikkien vanhempien tila täsmää expected_status -arvoihin."
    )

# 3. IMMUTABLE EXECUTION STATE MODEL (Arviointimoottorin lopullinen tuloste)
class AtomExecutionState(BaseModel):
    """Runtime tila yksittäiselle Atomille DAG:ssa"""
    tda_id: str
    status: ExecutionStatus = Field(default=ExecutionStatus.PENDING)
    short_circuit_reason_tda_ids: list[str] = Field(default_factory=list),
        description="Lista tda_id -arvoista, jotka oikosulkivat atomin (Blame determinismi)."
    )
    evaluation_reasoning: str | None = Field(default=None)
```

### 3.1 Two-Pass Hybrid-DAG Pipeline (Kustannus- ja Token-optimoitu Louhinta)

Alkuperäinen yhden vaiheen (Single-Pass) hypoteesi hylättiin, koska raskaiden `EnrichedAtom` JSON-rakenteiden tuottaminen kerralla ylittää nopeasti kielimallin tulosteen maksimirajan (Output Token Limit). Tämä kaataa suorituksen ja pakottaa järjestelmän päättymättömiin uudelleenyrityssilmukoihin (retry loops). Välttääksemme tämän siirrymme kaksivaiheiseen tunnisteiden kohdistusarkkitehtuuriin (Two-Pass ID-Mapping).

### 3.1.1 Phase 0: Map-Reduce Global Entity Ontology
Liukuva ikkuna ja GCEL-sääntömuisti on sokea yksittäisille kaukaisille entiteeteille ja pronomineille (Cross-Chunk Amnesia). Ennen Vaiheen 1 louhintaa ajetaan O(N) nopea Phase 0:
* **Toteutus:** Koko asiakirjasta uutetaan pelkät makrotason ehdot JA **ydinentiteetit** (erisnimet, organisaatiot, roolit) globaaliin `GlobalOntologyMap`-sanakirjaan.
* **Injektio:** Tämä sanasto injektoidaan system-promptina kaikkiin Vaiheen 1 (Chunk Extraction) lokaaleihin kutsuihin. Näin LLM osaa korvata pronominit (esim. "Se kaatui") suoraan oikeilla ydinentiteeteillä jo lokaalissa purussa (purkaen anaphoran), ilman että Vaiheen 2 Sliding Window'n tarvitsee yrittää kuroa 15 lohkon (chunk) matkaa umpeen sokkona.

#### Vaihe 1: Tekstin lohkominen ja paikallinen aliverkko (Chunked Extraction ja Local Sub-Graph)
Pitkä asiakirja jaetaan lohkoihin (lohkominen (chunking)). Kielimalli louhii jokaisesta lohkosta väitteitä (`resolved_claim`) ja purkaa pronominit (anaforan ratkaisu, anaphora resolution). Koska käsittely tapahtuu pienissä osissa, tulosteen maksimiraja ei ylity. 

**Paikallisen graafin rakennus (Lost-in-the-Middle -ratkaisu):** Koko verkon rakentamista ei jätetä Vaiheeseen 2, vaan kielimalli muodostaa jo Vaiheessa 1 lohkon sisäisen riippuvuusverkon (Local Sub-Graph). Tässä pienessä konteksti-ikkunassa LLM'n huomiokyky on huipussaan, jolloin lokaalit riippuvuudet saadaan talteen virheettömästi.

### 3.1.2 Global Condition & Event Ledger (O(1) Cross-Chunk Memory)
Pelkkä entiteettien louhinta (Map-Reduce Entity Resolution) ei kykene purkamaan abstrakteja makrotason ehtoja. Cross-Chunk Amnesia ratkaistaan hierarkkisella **Global Condition & Event Ledger (GCEL)** -putkella:

1. **Globaalien ehtojen louhinta (Map-vaihe):** Lohkomisvaiheessa (lohkominen (chunking)) LLM poimii litteäksi listaksi erisnimien lisäksi dokumentin **globaalit ehdot, säännöt ja makrotapahtumat** (esim. `COND_01: "SLA-rangaistus astuu voimaan vain, jos..."`).
2. **Kanonisointi:** Nämä tallennetaan ja deduplikoidaan `GlobalConditionMap`-hakemistoon.
3. **Cross-Chunk Injektio:** Kun Sliding Window (Vaihe 2) rakentaa graafia, jokaiseen liukuvaan ikkunaan injektoidaan aina koko tiivistetty `GlobalConditionMap`. LLM pystyy piirtämään `CausalEdge`-viittauksen ikkunassa olevasta väitteestä suoraan globaaliin ehtoon, vaikka ne olisivat kaukana toisistaan. Ikkunan koko pysyy pienenä (O(1) skaalautuvuus).

Python antaa jokaiselle puretulle väitteelle globaalin Opaque ID:n (UUID). **Huomio (AliasEngine Mandate):** Pitkiä UUID-tunnisteita EI SAA syöttää sellaisenaan LLM:lle, koska se aiheuttaa Token Bloatia. `AliasEngine` rekisteröi nämä ja muuttaa lyhyiksi ankkureiksi (`a0`).

**Kriittinen sääntö (Pydantic Pre-Validation Hydration):** `AliasEngine.hydrate_dict_list()` on suoritettava natiiviin Python `dict`-raakadataan ENNEN kuin sitä yritetään syöttää `ExtractedAtom.model_validate()` -metodille. Jos validointi yritettäisiin ensin, Pydanticin Strict Regex (`^tda_...`) kaatuisi LLM'n tuottamiin lyhyisiin aliaksiin.

### 3.1.3 Deterministinen Graafin Eheytys (Cycle Breaker & Phantom Isolation)
LLM'n hallusinoimaa topologiaa ei saa koskaan sokeasti hyväksyä tai antaa sen kaataa TaskGroupia poikkeuksiin.
* **Haamuviittausten käsittely (Phantom Edge Handling, Strict-yhteensopiva):** Jos Vaihe 2 (liukuva ikkuna, sliding window) viittaa tunnisteeseen, jota ei ole olemassa (esim. `a99`), tietojen koostaminen (hydraus, hydration) ei saa sivuuttaa sitä hiljaisesti (The Silent Drop Loophole). Hiljainen sivuuttaminen tekisi ehtolauseesta virheellisesti absoluuttisen väitteen. Lapsiatomi eristetään välittömästi tilaan `SYSTEM_ERROR` (syynä `UNRESOLVED_DEPENDENCY`). Tämä ylläpitää nopean vikaantumisen (Fail-Fast) arkkitehtuuria.
* **Deterministinen syklin eristäminen (Fail-Fast):** Ennen topologista arviointia kausaaliverkko analysoidaan syvyyshaulla (DFS / `networkx.simple_cycles()`). Jos kehäpäätelmä (sykli, esim. A -> B -> A) havaitaan, järjestelmä EI KOSKAAN saa yrittää korjata sitä hiljaisesti poistamalla kaaria. Kaikki sykliin osallistuvat solmut eristetään välittömästi tilaan `SYSTEM_ERROR` (Syy: `CYCLIC_DEPENDENCY_DETECTED`). Tämä ylläpitää tiukkaa Fail-Fast -politiikkaa.

#### Vaihe 2: Hierarkkinen Global Graph Linker (Sliding Window)
Jos kaikki sadat atomit syötettäisiin kerralla Vaiheelle 2, malli kärsisi "Lost in the Middle" -ilmiöstä ja jättäisi huomiotta listan keskellä olevia riippuvuuksia. Koska Vaihe 1 on jo rakentanut lokaalit aligraafit, Vaiheen 2 tehtävä muuttuu **Hierarkkiseksi Linkittäjäksi**, joka käyttää **Sliding Window -algoritmia**:

1. **Järjestys:** Aligraafit järjestetään alkuperäisen dokumentin spatiaalisen järjestyksen mukaan (`chunk_index`).
2. **Ikkunakoko:** `W = settings.GRAPH_LINKER_WINDOW_SIZE` (oletus: 4 lohko (chunk)a). Overlap: `O = settings.GRAPH_LINKER_OVERLAP` (oletus: 2 lohko (chunk)a).
3. **Iteraatio:** LLM saa kerrallaan W lohkon (chunk) aligraafit ja etsii cross-chunk -riippuvuuksia vain näiden välillä. Jokaiselle tunnistetulle kaarelle LLM palauttaa `CausalEdge`-rakenteen `edge_reasoning`-päättelyineen.
   * *Prompt:* "Yhdistä nämä olemassa olevat aligraafit kausaalisesti toisiinsa alkuperäisen tekstin perusteella."
   * *Output:* LLM palauttaa lyhyiden tunnisteiden tunnisteiden kohdistuksen (ID mapping): `{"a5": [{"edge_reasoning": "...", "tda_id": "a1", "expected_status": "PASSED"}]}`.
4. **Merge:** Python yhdistää deterministisesti kaikkien ikkunoiden tuottamat inter-chunk -kaaret. Duplikaattikaaret (sama `tda_id`-pari) yhdistetään deterministisesti ja toisteiset kaaret poistetaan.
5. **Transitiivisuustarkistus:** Lopullinen graafi ajetaan `GraphValidatorService`:n läpi syklien ja orpojen tunnistamiseksi.

**Aikakompleksisuus:** O(N/W) LLM-kutsua, missä N on lohko (chunk)en määrä. Jokainen kutsu on kevyt, koska konteksti sisältää vain W lohkon (chunk) atomit (tyypillisesti < 40 atomia).

Suorituksen jälkeen Python-kerros käyttää deterministisesti `AliasEngine.hydrate_dict_list()` -metodia kääntääkseen lyhyet ankkurit (`a0`, `a5`) takaisin aidoiksi järjestelmätason UUID:iksi.

**VIKAANTUMISPOLITIIKKA (Ei Graceful Degradationia):** Jos liukuvan ikkunan kutsu epäonnistuu (DLQ ja Tenacity-retryjen jälkeen), ikkunan solmuja ei koskaan sivuuteta `UNLINKED`-tilaan. Kyseiset atomit pakotetaan välittömästi `SYSTEM_ERROR`-tilaan, mikä laukaisee alaspäin suuntautuvan `BLOCKED`-kaskadin.

Tämä vaihe viimeistelee täydellisen DAG:in (Directed Acyclic Graph) ilman Output-kriisiä tai konteksti-ikkunan sokeita pisteitä. Se ratkaisee hajallaan olevien aligraafien riippuvuudet toisistaan, **edellyttäen, että Vaihe 1 kykeni limityksen avulla purkamaan pronominit oikein**.

### 3.1.4 Context-Aware Linker (Amnesian ja Sokeuden torjunta)
Context-Aware Linker (Amnesian ja Sokeuden torjunta)
Vaiheen 2 DAG-rakentaja ei saa toimia "sokeana yhdistäjänä" (Blind Linker). Jos sille syötetään pelkät litteät väitelauseet ilman alkuperäistä kontekstia, se kadottaa kielelliset kausaliteettimerkit (esim. "koska", "siksi") ja alkaa hallusinoida linkkejä paniikissa. Vaihe 2:n LLM-kutsulle on **ehdottomasti** syötettävä alkuperäiset tekstikappaleet (`source_quote` tai koko asiateksti) sekä vaiheessa 1 poimitut litteät atomit samanaikaisesti. Tämä varmistaa, että kausaalisen verkon luominen perustuu aitoon kielelliseen rakenteeseen, ei irrallisten lauseiden spekulointiin.

### 3.2 Karsittu Riippuvuuslogiikka (Implisiittinen AND)

> [!NOTE]
> **Karsinta 1 (Pareto 80/20):** Alkuperäinen suunnitelma Turing-täydellisestä DNF-logiikasta (OR/AND-portit) hylättiin ylisuunnitteluna (overengineering). LLM:n kyky poimia monimutkaisia Boolean-portteja vapaasta tekstistä johtaa hallusinaatioihin ("Format Tax"). 

Ratkaisemme riippuvuudet **yksinkertaisella implisiittisellä AND-listalla** (`depends_on`). Oletamme, että jos atomilla on useita vanhempia, niiden kaikkien on täytyttävä (`PASSED`). Tämä kattaa 95 % tosimaailman vaatimuksista (esim. "Jos ehto A ja ehto B täyttyvät..."). Mahdolliset monimutkaisemmat skenaariot ratkaistaan suoraan LLM'n luonnollisen kielen ymmärryksellä atomin `resolved_claim` -tekstissä, ei monimutkaisilla Pydantic-porteilla.

### 3.6 Moottorin Eristäminen (TaskGroup over Gather)
`TopologicalEvaluator` toimii **yhden Stepin sisäisenä** atomitason arvioijana. Se ei korvaa nykyistä työnkulkutason orkestroijaa (`dag_executor.py`), vaan `LLMNodeStrategy` delegoi arviointilogiikan `TopologicalEvaluator`ille.ion (Ei-lukitseva Kaskadi)

> [!IMPORTANT]
> **Hitaiden yksittäissuoritusten viiveen (Straggler) ratkaisu:** Koska Injektiossa 2 lisättiin deterministinen syklinkatkaisija (Cycle Breaker), tapahtumapohjainen (event-driven) asynkroninen suoritus on nyt täysin turvallinen (ei lukkiutumisriskiä, deadlock). Moottori hyödyntää natiivia Python 3.11+ `TaskGroup`-rinnakkaisajoa ja solmukohtaisia tapahtumalukkoja:

1. **Globaali käynnistys (Global Spawning):** Jokaiselle graafin solmulle luodaan `asyncio.Event()` ja oma asynkroninen tehtävä (Task), jotka kaikki käynnistetään samaan `asyncio.TaskGroup`:iin samanaikaisesti. Rajapintakutsujen (API) rinnakkaisuutta säädellään semaforeilla (`asyncio.Semaphore`).
2. **Fail-Safe Suorituskuori (DLQ & Deadlock Prevention):** Koko solmun suoritus (odotus mukaan lukien) ON EHDOTTOMASTI käärittävä `try...except Exception...finally` -lohkoon. Jos solmu kaatuu käsittelemättömään poikkeukseen, poikkeus siepataan (ei anneta kaataa koko `TaskGroup`ia ja peruuttaa muita ajossa olevia solmuja) ja solmu ohjataan DLQ-tilaan (`SYSTEM_ERROR`). **Kriittisin kohta:** Valmiussignaali `finished_event.set()` on pakko kutsua `finally`-lohkossa. Muuten kaatunut vanhempi jättää lapsensa ikuiseen lukkoon (`Deadlock`), kun lapset jäävät odottamaan `await parent.finished_event.wait()` -kutsua, jota ei koskaan tapahdu.
3. **Solmukohtainen odotus (Node-Level Wait):** Tehtävän ensimmäinen toimenpide on asynkroninen odotus, joka purkautuu heti kun *vain sen omat* vanhemmat ovat valmiita. **Kriittinen sääntö:** Tätä ei saa tehdä `asyncio.gather` -kutsulla, sillä sen virheidenkäsittely jättää kaatuessa zombitehtäviä muistiin. Odotus on suoritettava turvallisella, sekventiaalisella asynkronisella silmukalla: `for parent in parents: await parent.finished_event.wait()`. Tämä ratkaisee kerrosmallin aiheuttaman synkronointipullonkaulan turvallisesti.
4. **Deterministinen kaskadi (Prioriteettimatriisi, Parent Priority Matrix):** Kun vanhempien tilat on selvitetty, ne tarkastetaan. Jos yksikin vanhempi on tilassa `SYSTEM_ERROR` tai `BLOCKED`, lapsi merkitään välittömästi kaskadina tilaan `BLOCKED`. Jos vanhemman tila on odotusten vastainen (esim. ehto on epätosi ja odotus oli `PASSED`), lapsi ohitetaan ja saa tilan `N_A` (oikosulku). Syyllisten solmujen tunnisteet tallennetaan `short_circuit_reason_tda_ids` -listaan.
5. **Oikosulkureaktio (Short-Circuit Reaction):** Oikosulkutilanteissa tehtävä asettaa oman valmiussignaalinsa `finished_event.set()` millisekunneissa ilman uutta kielimallikutsua, mikä laukaisee ketjureaktion (kaskadin) alaspäin salamannopeasti.

### 3.4 Yksinkertaistettu Tilakone (6 Core States)

> [!NOTE]
> **Karsinta 3 (Pareto 80/20):** Alkuperäiset monimutkaiset ajonaikaiset tilat on supistettu kuuteen (6) ydintilaan selkeyden, determinismin ja Pydantic-yhteensopivuuden takaamiseksi. Graafi- ja infrastruktuurivirheet niputetaan yhteen, kun taas loogiset estot periytyvät puussa alaspäin.

1. **`PENDING`**: Odottaa suoritusta.
2. **`PASSED`**: Väite tai ehto arvioitiin todeksi (Hyväksytty).
3. **`FAILED`**: Väite tai ehto arvioitiin epätodeksi (Hylätty).
4. **`N_A`**: Looginen ohitus (Oikosulku, Short-Circuit). Lapsisolmun arviointi ohitettiin deterministisesti, koska sen vanhemman asettama ehto ei täyttynyt.
5. **`BLOCKED`**: Suoritus estynyt kaskadina. Lapsisolmun arviointi estettiin automaattisesti, koska ketjussa ylempänä oleva vanhempi kaatui järjestelmävirheeseen tai on ratkaisematon.
6. **`SYSTEM_ERROR`**: Ristiriita, infrastruktuurin kaatuminen, API-virhe tai ratkaisematon syklinen viite. Tarkemmat virhesyyt, kuten mallien erimielisyys (Contested), tallennetaan metadatakenttään `evaluation_reasoning`.

**Adaptiivinen arviointistrategia (Adaptive 1-Then-3 Evaluator / Tiered Bo3):** Ehtoarviointi käyttää dynaamista eskalointia API-kutsuissa: Tehdään ensin 1 nopean mallin kutsu. Jos luottamus on korkea, tila lukitaan (`PASSED`/`FAILED`). Vain, jos luottamus on kynnysarvoa matalampi tai tulos epäselvä, laukaistaan lisäkutsut (paras kolmesta -konsensus, Best-of-Three). Tämä leikkaa API-kustannuksia säilyttäen argumentaation tarkkuuden.

> [!WARNING]
> **Cross-Language Enum Parity (Kriittinen UI-Mandaatti):** Uusien tilojen (kuten `N_A`, `BLOCKED` ja `SYSTEM_ERROR`) tuominen backendin Pydantic-malleihin rikkoo Frontendin välittömästi (Null-Pointer), jos niitä ei synkronoida Flutterin koodikantaan. Kaikki Pydantic-tilat on EHDOTTOMASTI peilattava Dart-koodikannan `enums.dart` -tiedostoon `@JsonEnum()` -annotaatioilla varustettuna (Freezed-valmius). Frontendin on pystyttävä desiarlisoimaan jokainen näistä 6 tilasta luotettavasti.

### 3.5 Kieliriippumattomuus (Cross-Lingual Resilience)
* **LLM Semantic Parsing:** Koska Stage 1 luottaa kielimallin syvään semanttiseen ymmärrykseen, pronominien purkaminen on kieliriippumatonta. LLM ymmärtää pro-drop -kielten piilopronominit, agglutinatiiviset päätteet ja englannin eksplisiittiset pronominit yhtä lailla.
* **Agnostinen Python-kerros:** Python-kerros ja Pydantic-mallit toimivat puhtaasti matemaattisilla graafeilla. Koodi ei etsi tekstistä sanaa "Jos", vaan ohjaa suoritusta täysin kieliriippumattomien Opaque Stripe ID -relaatioiden avulla.

### 3.6 Legacy Component Migration (SSOT Consolidation)
Jotta arkkitehtuuri pysyy ehdottoman Single Source of Truth (SSOT) -säännön alaisena, Epic 92 määrittelee olemassa olevien legacy-komponenttien uudet roolit:
* **`AliasEngine` (Opaque ID Hydration):** Ylennetään koko DAG-moottorin absoluuttiseksi muistinhallintayksiköksi. Vastuuta laajennetaan tukemaan graafin kausaalilinkkejä (Causal Edges). Tämä on ainoa auktorisoitu tapa kääntää raskaat UUID:t LLM-ystävällisiksi ankkureiksi (`a1`, `src_1`) koko backendissä.
* **Nykyiset `Chunk`-ohjelmistot (esim. ChunkWorker):** Nykyisiltä tekstiä pilkkovilta ja arvioivilta palveluilta **riistetään täysin** oikeus asynkroniseen LLM-orkestrointiin, tapahtumaluuppeihin ja omatoimiseen virheidenkäsittelyyn. Ne alennetaan pelkiksi "Datan Tuottajiksi" (Producers). Niiden ainoa tehtävä on pilkkoa dokumentti ja syöttää raaka data uuteen `TopologicalEvaluator`-moottoriin. Tämä poistaa koodikannasta rinnakkaiset ja kilpailevat LLM-suoritusmoottorit.

### 3.7 Risk Mitigation (Critical Safeguards)
Tämän arkkitehtuurin tekniset riskit on torjuttava jo suunnitteluvaiheessa:
1. **TaskGroup Cascade of Death & DLQ Mandate:** `asyncio.TaskGroup` peruuttaa kaikki tehtävät yhden kaatuessa. Tämän estämiseksi solmun sisällä on oltava tiukka Error Boundary. Tilapäisiä virheitä (API 503, Rate Limits) EI SAA kuitata pelkällä lokaalilla `try-except` -ohituksella, vaan niiden on mentävä LLMTaskExecutorin natiivin Tenacity-retry ja DLQ (Dead Letter Queue) -putken läpi. Vasta kun DLQ on ammennettu tyhjiin, solmun käsittelemätön poikkeus (unhandled exception) on nieltävä (swallowed) ja solmu on merkittävä tilaan `SYSTEM_ERROR`. **Kriittinen sääntö:** Jokaisen Taskin on ehdottomasti suoritettava `finished_event.set()` `finally:` -lohkossa. Muuten järjestelmä ajautuu ikuiseen Event Loop -deadlockiin.
2. **Event Loop -lukkiutuminen (NetworkX):** Raskaat synkroniset graafialgoritmit (kuten syklinetsintä) on ehdottomasti ajettava erillisessä säikeessä `await asyncio.to_thread()` avustuksella, jotta FastAPI:n asynkroninen Event Loop ei jäädy suurten graafien kohdalla.
3. **AliasEngine -Muistivuodot:** Koska AliasEngine toimii keskusmuistina, sen elinkaari (Scope) on rajattava tarkasti Request- tai Job-kohtaiseksi. Globaalin, tyhjentämättömän tilan pitäminen muistissa on kielletty muistivuotojen estämiseksi.
4. **Frozen State Mutability (event.model_copy):** Koska DAG-moottorin mallit on merkittävä globaalilla `ConfigDict(frozen=True)` -asetuksella, tilamuutoksia EI SAA koskaan tehdä ohittamalla tyyppiturvallisuutta väliaikaisilla Python-sanakirjoilla (no_naked_dicts_in_state). Kaikki tilamutaatiot ajon aikana on EHDOTTOMASTI tehtävä `event.model_copy(update={...})` -metodilla, joka takaa immutaabelin event sourcing -mallin rikkoutumattomuuden.
5. **Data Healing Validator (mode='before'):** Graceful Degradation on varmistettava data-muotoiluvaiheessa. Jos LLM hallusinoi (esim. lainauksen contextual_override-tilassa), perinteinen `@model_validator(mode='after')` kaataisi koko kalliin LLM-ajon `ValueError` -poikkeukseen (Fail Fast liian myöhään). Koska Pydantic-malli on `frozen=True`, kenttien korjaus/parannus (healing) on pakko mutatoitava EHDOTTOMASTI `mode='before'` -vaiheessa ennen mallin jäätymistä. Näin turvataan kallis ajo pelkältä muotovirheeltä.

---

## 4. MVP Vaiheistus (Phased Implementation Strategy)

Arkkitehtuuri on jaettu suorituskykyä ja asiakasarvoa nopeasti tuottaviin MVP-vaiheisiin (Minimum Viable Product). Tämä estää "God Phase" -ongelman eristämällä tietomallien, LLM-promptauksen ja liiketoimintalogiikan testaamisen.

### Vaihe 1: Topological Engine & Deterministic Rules (SSOT Foundation)
* **Mitä tehdään:** Rakennetaan graafin suoritusmoottori, syklinmurtaja (`networkx`) ja tilakone (6 tilaa). **SSOT-sääntö (Single Source of Truth):** Näitä komponentteja ei saa rakentaa siiloutuneina skripteinä vain tätä Epiciä varten. Ne on suunniteltava ja abstrahoitava siten, että ne palvelevat globaalina, uudelleenkäytettävänä standardina mille tahansa DAG-pohjaiselle arvioinnille koko järjestelmässä. Ei LLM-koodia, ei tietokantakoodia.
* **Deliverables:**
  * `LinkedAtomGraph` ja 6-tilaisen koneen globaalit Pydantic SSOT -mallit.
  * Deterministinen kausaalimoottori (TaskGroup) ja syklinmurtaja, jotka on eriytetty itsenäisiksi palveluluokiksi (100% testikattavuus).
  * **Legacy Migration First (UI-Validointi):** Ennen uuden Epic 92 -logiikan aktivointia, *nykyinen* olemassa oleva arviointilogiikka on refaktoroitava käyttämään tätä uutta SSOT-moottoria. Vaihe 1 katsotaan valmiiksi vasta, kun SSOT-komponentti on täysin eristetty ja vanhat ominaisuudet toimivat saumattomasti uuden moottorin läpi siten, että testiajot käyttöliittymän (UI) kautta ovat menneet todennetusti läpi. Vasta tämän jälkeen siirrytään seuraavaan vaiheeseen.
  * **Knowledge Item (KI) Rekisteröinti:** Uuden `TopologicalEngine` SSOT-moottorin käyttöohjeet ja säännöt on kirjattava tekoälyn Knowledge Baseen (`<appDataDir>\knowledge\`), jotta tulevat agentit osaavat automaattisesti reitittää kaikki DAG-tarpeet tämän moottorin kautta luomatta uusia päällekkäisyyksiä.
* **Hyödyt (Business Value):** Luodaan matemaattisesti virheetön, fail-fast -turvattu perusta, joka ratkaisee Epic 92:n tarpeiden lisäksi myös tulevien ominaisuuksien graafisuoritusvaatimukset ilman koodin duplikaatiota.

### Vaihe 2: Local Extraction & GECL (LLM Pipeline)
* **Mitä tehdään:** Toteutetaan yksittäisen tekstipalan (Chunk) analyysi (Global Entity/Concept Logic). LLM tuottaa irrallisia Atomeja Opaque ID:illä.
* **Deliverables:**
  * Prompt-rakenteet Atomeiden tunnistamiseen ja puhdistamiseen (Anaforien purku).
  * `AliasEngine` -integraatio, joka lukitsee Atomeille puhtaat `tda_` tunnisteet ilman token-bloatia.
* **Hyödyt (Business Value):** Järjestelmä oppii lukemaan tekstiä kuin asiantuntija, palastelemaan sen pieniin itsenäisiin faktoihin ja varmentamaan sanatarkat lainaukset (Source Quotes).

### Vaihe 3: Global Sliding Window (The Synthesizer)
* **Mitä tehdään:** Kytketään Vaiheen 2 irralliset atomit toisiinsa liukuvalla ikkunalla.
* **Deliverables:**
  * Ikkunointialgoritmi, joka syöttää LLM:lle peräkkäisiä Chunk-tuloksia.
  * LLM generoi `CausalEdge` -riippuvuudet (A -> B) yli tekstirajojen.
* **Hyödyt (Business Value):** Poistaa "straggler" eli tiedonhukka-ongelman. Järjestelmä ymmärtää nyt laajoja syy-seuraus-suhteita sadan sivun dokumenteissa ilman, että kaikki teksti täytyy sulloa kerralla tekoälyn muistiin.

### Vaihe 4: The Graph Execution & Cascade (Full System Test)
* **Mitä tehdään:** Yhdistetään Vaiheen 1 moottori ja Vaiheen 3 tuottama verkko. Järjestelmä simuloi sensoreita ja ajaa koko verkon läpi.
* **Deliverables:**
  * Pää-Orchestrator, joka käynnistää asynkronisen TaskGroup-kaskadin.
  * `N_A` and `BLOCKED` propagointi oikealla datalla.
* **Hyödyt (Business Value):** Tuo logiikan eloon. Järjestelmä pystyy nyt päättelemään: *"Koska Sääntö A ei täyttynyt sivulla 5, pysäytän automaattisesti seuraukset B, C ja D sivuilla 10 ja 12."*

### Vaihe 5: Schema Projection (The Output)
* **Mitä tehdään:** Transformoidaan matemaattinen graafi ihmisen tai Excelin ymmärtämään muotoon.
* **Phase 5.5: ResultProjector:**
  * Epic 91.5:n vaatiman `ResultProjector`-rajapinnan toteutus: `AtomExecutionState` muunnetaan `AtomResultDTO` ja `HydratedAtomDTO` -objekteiksi.
  * Tässä vaiheessa suoritetaan staattisen `source_quote`-tiedon hajautus ja topologinen lajittelu.
  * *Huom:* Phase 5.5:n ulostulo pakataan `ReportDataDto`-muotoon (Epic 93:n vaatima SSOT kontrakt).
* **Deliverables:**
  * SDUI (Server-Driven UI) -muuntimet Flutterille (värikoodatut nodet, virhekortit).
  * Litteät raportti-DTO:t (CSV/Excel/PDF -valmius).
* **Hyödyt (Business Value):** Antaa loppukäyttäjälle auditoitavan, visuaalisen ja ymmärrettävän raportin koko monimutkaisesta päätöksentekoprosessista ja antaa mahdollisuuden viedä se suoraan ulkoisiin järjestelmiin.

---

## 5. Definition of Done (DoD)
1. **Schema Validation**: Mallit tukevat `EnrichedAtom` -rakenteita.
2. **Two-Pass DAG Builder**: Riippuvuudet puretaan kevyellä Vaihe 2 -kutsulla Output Token -rajojen kiertämiseksi.
3. **Conditional Short-Circuit**: Ehdolliset atomit ohitetaan, jos itse ehto arvioidaan Boolean Evaluatorilla epätodeksi. Lapsiatomeja ei lähetetä LLM:lle (Säästöt).
4. **Short-Circuit Traceability**: Jokainen `N/A`-tila sisältää `short_circuit_reason_tda_id` -kentän.
5. **Audit Loop**: Kaikki uudet ja vanhat yksikkötestit menevät läpi.

---

## 6. Käyttöliittymän ja Seed-Datan Muutokset (Admin Studio UI)

**Kriittinen sääntö (ID Hydration & UI Rendering):** Kaikki käyttöliittymäkomponentit ja vientityökalut (Excel, PDF), jotka esittävät `tda_id` -viittauksia (erityisesti `depends_on_tda_ids` ja `short_circuit_reason_tda_id`), on ehdottomasti rikastettava. Järjestelmän tulee ohjelmallisesti hakea pelkän Opaque ID:n rinnalle tietokannasta (tai tulos-payloadin sanakirjasta) kyseisen solmun `resolved_claim` -tekst (esim. `tda_123 ("Järjestelmä on vaarantunut")`). Opaque ID:tä ei saa koskaan esittää loppukäyttäjälle pelkkänä koodina ilman sen semanttista selitettä.

### 6.1 Audit Trail / Suoritusraportti UI (Execution Viewer)
Tämä on merkittävin visuaalinen muutos loppukäyttäjälle ja auditoijalle:
* **Graafinen Puunäkymä (DAG Viewer)**: Matriisin tulosnäkymässä tulokset voidaan sisentää riippuvuuksien mukaan. Ehtolause näkyy ylätasona, ja sen alaisuudessa on ehdollinen väite.
* **Uusi Status: `N/A` (Harmaa) + Short-Circuit Metadata**: Punaisen (`FAILED`) ja vihreän (`PASSED`) rinnalle tuodaan harmaa/neutraali tila. `N/A`-tilalla on aina näkyvissä syy: auditoija näkee suoraan, mikä ehtoatomi epäonnistui (esim. *"Ohitettu: Ehto [atm_abc123] 'Järjestelmä on vaarantunut' → FALSE"*). Klikkaus vie suoraan ehtoatomin yksityiskohtiin.
* **Spatiaalinen Korostus (Ankkurointi)**: Jos käyttäjä klikkaa ehdollista väitettä, käyttöliittymän lähdetekstinäkymä (Source Text Viewer) korostaa tarkalleen sen ehtolauseen ("Jos järjestelmä on vaarantunut..."), joka laukaisi tai esti arvioinnin.
* **Manual Override N/A-tiloille:** Koska koneellinen Boolean Evaluator voi tehdä virheitä (SPoF), Admin UI:hin on rakennettava kyvykkyys yliajaa ehtoarviointi. Jos ihminen huomaa, että ehto onkin täyttynyt, hänen on voitava klikata "Manual Override" N/A-tilassa olevalle atomille. Tämä laukaisee ohitetun alipuun arvioinnin takautuvasti.

### 6.2 Data Contract / Suoritusraportin Rakenne (Result Payload)
Kun yksittäinen ajo (Execution) valmistuu, sen tulokset on paketoitava rakenteeseen, joka tukee graafia mutta on helppo siirtää verkon yli (esim. käyttöliittymälle tai API-asiakkaalle). Koska DAG-verkossa yhdellä solmulla voi olla useita vanhempia, puhdas sisäkkäinen JSON-puu (Nested Tree) aiheuttaisi ristiinkytkentöjen monistumista. Siksi tulosraportti käyttää **Flat Adjacency List** -muotoa:

#### 6.2.1 Tilojen UI-Niputus (Status Projection)
Vaikka arviointimoottori (Backend) erottelee luonnolliset ohitukset (`N_A`) virheistä (`SYSTEM_ERROR`), käyttöliittymä pitää asiat vieläkin yksinkertaisempana. Payloadin generointivaiheessa (`ResultProjector`) moottorin viisi (5) tilaa vastaavat lähes sellaisenaan UI-esitystä:

1. **HYVÄKSYTTY** (`PASSED`)
2. **HYLÄTTY** (`FAILED`)
3. **OHITETTU** (`N_A`): Looginen N/A oikosulku, syyt löytyvät `short_circuit_reason_tda_ids` -kentästä (lista). Näkyy harmaana.
4. **JÄRJESTELMÄVIRHE** (`SYSTEM_ERROR`): Kriittinen infrastruktuuri, ristiriita tai topologiavirhe. Odottaa auditoijan manuaalista päätöstä. Näkyy varoitusvärillä.

```json
{
  "execution_id": "exec_abc123",
  "global_metrics": {
    "total_atoms": 45,
    "evaluated": 40,
    "short_circuited_na": 5
  },
  "results": [
    {
      "tda_id": "tda_1",
      "status": "PASSED",
      "depends_on_tda_ids": [],
      "short_circuit_reason_tda_ids": [],
      "evaluation_reasoning": "Lokit osoittavat selkeän murron."
    },
    {
      "tda_id": "tda_2",
      "status": "N_A",
      "depends_on_tda_ids": ["tda_1"],
      "short_circuit_reason_tda_ids": ["tda_1"] 
    }
  ],
  "hydrated_references": {
    "tda_1": {
      "resolved_claim": "Järjestelmä on vaarantunut",
      "source_quote": "Systeemi hakkeroitiin eilen..."
    },
    "tda_2": {
      "resolved_claim": "Poista data",
      "source_quote": "Tällöin data on poistettava heti."
    }
  }
}
```
**Hyödyt (SDUI & Strict Parity):** Tämä rakenne erottaa ajonaikaisen tilan (`results`) staattisesta tiedosta (`hydrated_references`). Se poistaa massiivisen datan duplikoinnin ja tekee Pydantic-validoinnista huomattavasti nopeampaa. Tärkeimpänä: tämä tukee **Epic 93:n SDUI-tavoitetta**. Koska graafiset 2D-verkot rikkoisivat PDF/Flutter-symmetrian (Strict ICU Markdown Parity), backendin "Projector" lukee tämän litteän listan ja luo siitä pelkkää Enum-ohjattua, hierarkkista Markdown-taulukkoa tai sisennettyä listaa. Flutter ja PDF-moottori renderöivät litteän tekstipuun (ja `source_quote`-blokit) identtisesti, puhtaasti DTO-datan pohjalta ilman erillisiä tietokantahakuja UI:ssa.

#### 6.2.1.1 Pydantic V2 DTO -Määrittely (Siirretty)
> [!NOTE]
> Varsinaiset Pydantic V2 DTO -mallit (kuten `ReportDataDto`, `AtomResultDTO` ja `HydratedAtomDTO`) on eriytetty omaan perustamisvaiheeseensa. Katso **Epic 91.5: The Universal DTO Bridge** nähdäksesi tarkan kooditason sopimuksen.

#### 6.2.2 Decoupled Scoring Architecture (Asynkroninen Jälkilaskenta)
Vaikka numeerinen dampening-matematiikka on revitty irti ydinsuoritusputkesta (Execution Pipeline) ja DTO-kannasta, järjestelmällä voi silti olla tarve joskus esittää loppukäyttäjälle yksinkertaistettu prosenttiluku tai arvosana. Tämä toteutetaan täysin **irrallaan DAG-moottorin suorituksesta**.

* **Pisteytyksen Mutaatio Ilman Kustannuksia (Zero-Cost Recalculation):** Koska DAG-moottori tuottaa ainoastaan deterministisiä, kausaalisia tiloja (`PASSED`, `FAILED`, `N_A`), mahdollinen numeerinen pisteytys lasketaan vasta jälkikäteen. Laskennan tekee käyttöliittymä (Frontend) tai täysin erillinen asynkroninen raportointimoottori (Reporting Engine) pelkkien tilojen perusteella.
* **Jälkilaskennan Voima:** Jos asiakas haluaa myöhemmin muuttaa matematiikan sääntöjä (esim. "muuta FAILED-tilan saaman sakon painotusta" tai "salli IGNORE_NULL-optimismi"), satoja tuhansia kalliita ja hitaita LLM-ajoja ei tarvitse koskaan ajaa uudelleen! Pisteet voidaan laskea uudelleen lennosta kaikille historiassa ajetuille asiakirjoille, koska taustalla oleva totuus (Immutable Execution State) on täydellinen, säilytetty ja matemaattisesti puhdas. Tämä on irti kytketyn (Decoupled) datamallin suurin arvolupaus.

### 6.3 Asiakkaan Hyödyt ja Arvolupaus (End-User Value)
Miksi tämä arkkitehtuuri on loppuasiakkaalle (esim. compliance-upseerille, juristille tai kouluttajalle) täysin mullistava, ja mitä hän konkreettisesti näkee suorituksen jälkeen UI:ssa?

1. **Argumentaation Röntgenkuva ("Why", ei pelkkä "What"):** Asiakas ei näe enää pelkkää tylsää "80% oikein" -arvosanaa tai mustan laatikon tiivistelmää. Hän näkee visuaalisen puun (DAG), joka paljastaa tarkalleen *missä kohtaa* argumentin logiikka petti. "Väitteesi pohja (A) oli tosi, mutta siitä johdettu seuraus (B) oli keksitty." Quorum muuttuu dokumentinlukijasta logiikan analysaattoriksi.
2. **Forensinen Todistettavuus ja XAI (Explainable AI):** Kun asioita ohitetaan (N/A-tila), asiakas näkee välittömästi syyn: *"Tätä kappaletta ei tutkittu, koska Ehto X (Järjestelmä on vaarantunut) ei täyttynyt."* Lisäksi jokainen solmu on klikattavissa, jolloin UI korostaa tarkalleen sen yhden lauseen alkuperäisestä 1000-sivuisesta PDF-dokumentista, johon solmu ja ehto perustuvat. Tämä täyttää EU AI Actin (Art. 13) ja CSRD:n tiukimmatkin läpinäkyvyysvaatimukset.
3. **Interaktiivinen Skenaariotestaus (What-If):** Koska graafi on matemaattinen ja sisältää selkeät portit, UI voi tarjota asiakkaalle "Manual Override" -kytkimen. Asiakas voi leikkiä skenaarioilla: *"Mitä jos pakotankin tämän ehdon tilaan TRUE, vaikka kone sanoi FALSE?"* Järjestelmä laukaisee vain ohitetun alipuun arvioinnin uudelleen. Tämä muuttaa Quorumin staattisesta arviointityökalusta interaktiiviseksi simulaatioalustaksi, jolla ammattilaiset voivat koeponnistaa dokumenttiensa kestävyyttä.

### 6.4 Excel-raportointi (UI / Vienti)

Uuden DAG-arkkitehtuurin (Domain vs. Execution State) myötä Excel-tulosteen luonne muuttuu pelkästä listasta täysin auditoitavaksi **Tapahtumalokiksi (Execution Ledger)**. 

**Kielellinen direktiivi (Linguistic Directives):** Kuten `linguistic_directives.py` määrittää, vaikka LLM:n sisäinen päättely (Chain-of-Thought) suoritetaan englanniksi (`required_reasoning_language = English`) maksimaalisen kognitiivisen syvyyden saavuttamiseksi, Excel-raporttiin ja loppukäyttäjän UI:hin kaikki tekstit ja perustelut käännetään automaattisesti kohdekielelle (esim. suomeksi). Englantia ei koskaan näytetä loppukäyttäjälle ilman erillistä pyyntöä.

Tässä on ehdotus uudesta Excel-raportin rakenteesta. Se heijastaa suoraan erotettua arkkitehtuuria: `EnrichedAtom` (Sarakkeet 1-4) ja `AtomExecutionState` (Sarakkeet 5-8).

| TDA ID | Puhdistettu Väite | Ehto / Portti | Riippuu (Depends On) | Tila (Status) | Varmuus | Moottorin Perustelu (Käännetty) | Ohituksen Syy (Kaskadi) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `tda_8f3a9b...` | Työtehtävä on kampussidonnainen. | Työntekijä on HR/Talous (FALSE) | | **HYVÄKSYTTY** | 0.99 | *Pekka on IT-lähituessa. Tehtävä ei ole HR/Talous, joten kampussidonnaisuuden ehto täyttyy muulla perusteella.* | |
| `tda_4c7d2e...` | Työntekijän läsnäoloa vaaditaan opiskelijapalveluiden takaamiseksi. | Riippuu kampussidonnaisuudesta | `tda_8f3a9b...` ("Työtehtävä on kampussidonnainen.") | **HYVÄKSYTTY** | 0.95 | *IT-lähituen rooli vaatii fyysistä läsnäoloa opiskelijoiden laiteongelmien korjaamiseksi.* | |
| `tda_9b6a1f...` | Työntekijälle korvataan läsnäolo laajennetulla työaikajoustolla. | Työ on kampussidonnaista (TRUE) | `tda_4c7d2e...` ("Työntekijän läsnäoloa vaaditaan...") | **HYVÄKSYTTY** | 0.98 | *Koska Pekan rooli vahvistettiin kampussidonnaiseksi, oikeus työaikajoustoon astuu voimaan.* | |
| `tda_2e4a8d...` | Työntekijälle säilytetään oma tai jaettu fyysinen työhuone. | Käsittelee luottamuksellista tietoa (TRUE) | `tda_8f3a9b...` ("Työtehtävä on kampussidonnainen.") | **HYLÄTTY** | 0.99 | *Pekka on IT-tuki, ei HR tai Talous. Politiikka rajaa omat työhuoneet vain luottamuksellista dataa käsitteleville.* | |
| `tda_5f1c4e...` | Työntekijää ei sijoiteta avokonttoriin. | Työhuone myönnettiin (TRUE) | `tda_2e4a8d...` ("Työntekijälle säilytetään oma...") | **OHITETTU** | - | - | `tda_2e4a8d...` ("Työntekijälle säilytetään oma...") |
| `tda_1a9b8c...` | Etätyöhön soveltuvissa tehtävissä ollaan enintään 3 päivää etänä. | Tehtävä soveltuu etätyöhön (TRUE) | `tda_4c7d2e...` ("Työntekijän läsnäoloa vaaditaan...") | **RISTIRIITAINEN**| 0.70 | *Pekan tehtävä (IT-tuki) on kampussidonnainen, mutta hakemuksessa hän mainitsee tekevänsä pelkkää etähallintaa tiistaisin. Teksti on ristiriitainen pelkän etähallinnan osalta.* | |

**Auditoijan hyödyt Excelissä:**
1. **Syy-seuraussuhteet ja Luettavuus:** Sarakkeista "Riippuu" ja "Ohituksen Syy" näkee heti paitsi viitatun ID:n, myös haetun tekstin tietokannasta (esim. `tda_2e4... ("Työntekijälle säilytetään oma...")`). Auditoijan ei tarvitse hyppiä riveiltä toiselle ymmärtääkseen, miksi jokin rivi ohitettiin, sillä syy-yhteys lukee suoraan samalla rivillä. Tästä jää täydellinen todistusaineisto.
2. **Kielimuurin ylitys:** `linguistic_directives.py`:n mukaisesti LLM käyttää englanninkielistä "Chain of Thought" -päättelyä verhon takana maksimoidakseen loogisen päättelykyvyn, mutta compliance-upseeri näkee Excelissä ja käyttöliittymässä ainoastaan laadukasta suomenkielistä tekstiä.
3. **Turvallisuus (SPoF-suoja):** Kun luottamus laskee, LLM ei arvaa sokeasti ja pilaa dataa sokealla `HYLÄTTY/OHITETTU` -kaskadilla, vaan asettaa solmun `SYSTEM_ERROR` -tilaan keltaisella huomiovärillä ja kirjaa syyksi mallien erimielisyyden (Contested). Tällöin compliance-tiimin on helppo suodattaa Excelissä nämä rivit manuaalista tarkistusta varten.

---

## 7. Vaikutusanalyysi

### 7.1 Kustannus- ja Latenssivaikutus

| Mittari | Vaikutus | Selitys |
|---|---|---|
| **LLM-kutsut** | +1 kevyt lisäkutsu (Vaihe 2) | Graafin rakennus on lyhyt JSON-linkitys nopealla mallilla (Haiku), joka poistaa massiivisen Output Token -ongelman ja kaatumiset. |
| **Oikosuljetut kutsut** | -N kutsua per ajo | Jos ehto A ei täyty, ehdosta A riippuvia lapsisääntöjä ei lähetetä kalliiseen LLM-arviointiin lainkaan. Tämä maksaa Vaihe 2:n kulut moninkertaisesti takaisin. |
| **Retry-luupit** | Merkittävästi vähemmän | Pienempi Output Token -koko ja selkeä ID-mäppäys vähentää Pydantic-kaatumisia. |

### 7.2 Vertailutaulukko: Ennen ja jälkeen

| Dimensio | Nykytila (ennen Epic 92) | Epic 92:n jälkeen |
|---|---|---|
| **Moottorin tilat (Backend)** | 4 (PASS, FAIL, DLQ, CONTESTED) | 5 (PASS, FAIL, N_A, PENDING, ERROR) |
| **Näkyvät tilat (UI/Excel)** | 4 | 4 (+ OHITETTU, JÄRJESTELMÄVIRHE) |
| **Selitys tulokselle** | "Mikä" (pelkkä tulos) | "Mikä" + **"Miksi"** + **"Mistä"** (XAI) |
| **Väärät negatiiviset** | Yleisiä ehdollisissa lauseissa | Eliminoitu N/A-tilalla ja ehtoarvioinnilla |
| **Pronominit** | Ratkaisematta → hallusinaatioriski | Purettu eksplisiittisesti → `resolved_claim` |
| **Riippuvuudet väitteiden välillä** | Ei tietoa (litteä lista) | Täysi DAG-graafi (`depends_on_tda_ids`) |
| **Lähteen jäljitettävyys** | `source_quote` + `source_id` | `source_quote` + `resolved_claim` + `source_id` + ehdon lähde |
| **Auditoitavuus** | Litteä tulosrivi | Kausaalinen puu perusteluineen |

---

## 8. Tieteelliset Viittaukset (Academic References)

Tämän Epicin arkkitehtuuri perustuu seuraaviin vertaisarvioituihin tutkimuksiin:

* **FActScore** — Min et al. (EMNLP 2023): Atomaarinen propositioiden purkaminen ja itsenäinen verifiointi.
* **SAFE** (Search-Augmented Factuality Evaluator) — Wei et al. (Google DeepMind, 2024): Hakuavusteinen faktuaalisuuden arviointi atomeista.
* **"Let Me Speak Freely?"** — Tam et al. (EMNLP 2024): Empiirinen todiste siitä, että tiukkojen JSON-skeemojen pakottaminen heikentää LLM:n päättelykykyä.
* **"LLMs Cannot Self-Correct Reasoning Yet"** — Huang et al. (ICLR 2024): Todiste siitä, että LLM ei pysty korjaamaan omia päättelyvirheitään ilman arkkitehtuurisesti erillistä palautetta. Perustelee deterministisen ehtoarvioinnin ja Kahnin algoritmin.
* **System 2 Attention** — Weston & Sukhbaatar (Meta AI, 2023): Kahnemaenin System 1/System 2 -dualismiin pohjautuva malli.
