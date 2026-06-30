# Epic 92: Enriched Atom Graph Architecture (Kontekstuaalisen Atomisaation Korjaus)

> [!IMPORTANT]
> **THE CONTEXT-LOSS PARADOX RESOLUTION MANDATE**: Atomien flattauksen aiheuttama referenttien menetys (Anaphora) ja ehdollisuuden hajoaminen (Conditional Logic Decoupling) on ratkaistava ilman flat-list -arkkitehtuurin hylkäämistä. Järjestelmän tulee suorittaa 2-vaiheinen "Enriched Atom Graph" -pipeline: 1. Probabilistinen LLM Resolution -passi (Anaphora + Condition -tunnistus) ja 2. Deterministinen Pydantic- ja Python-ohjattu ehdollinen arviointi.

### Strateginen Merkitys

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

Tämän Epicin tavoitteena on ratkaista arkkitehtuurinen virhe, jossa tekstin purkaminen erillisiksi atomeiksi (Atom-Flattening) tuhoaa ihmiskielen semanttiset riippuvuudet ja aiheuttaa vääriä positiivisia ja negatiivisia tuloksia (False Positives / Negatives) Scoring Engine -vaiheessa.

### Nykytilan Ongelma:
* **Anaphora Resolution Failure**: "It caused the database failure" menettää kontekstinsa flattauksessa.
* **Conditional Logic Decoupling**: "If system compromised, data deleted" purkautuu kahdeksi erilliseksi absoluuttiseksi väitteeksi. Jos dataa ei ole poistettu (koska järjestelmä ei ollut vaarantunut), arviointimoottori antaa "Data deleted" -atomille suuren hallusinaatiorangaistuksen.
* **Semantic Disjointedness**: Yksittäiset todet atomit voivat muodostaa kokonaisuuden, joka on alkuperäistä kontekstia vastoin.

### Ratkaisu:
Luodaan **Enriched Atom Graph**, joka upottaa semanttisen verkon flattaukseen metadatan avulla:
1. **Resolution Pass (Ennen flattausta)**: LLM ohjeistetaan ratkaisemaan pronominit eksplisiittisesti ja tunnistamaan ehdollisuudet osana atomia.
2. **Pydantic Schema Update**: Päivitetään Atom-rakenne tukemaan `conditions`, `resolved_claim` ja `depends_on_atom_ids` kenttiä.
3. **Deterministic Evaluation Hook**: Scoring Engine (Python-puolella) ohitetaan/muokataan ehdollisten atomien kohdalla tarkistamaan ehto ennen varsinaista väitteen validointia.

---

## 2. Arkkitehtuuristen sääntöjen huomiointi (Compliance Matrix)

* **01-python-backend.md (Fail-Fast Pydantic V2)**: Uudet `EnrichedAtom` ja `ClaimCondition` -luokat luodaan Pydantic V2:lla tiukkojen `ConfigDict(extra='forbid', strict=True)` -määritysten kanssa. 
* **05_llm_architecture.md (LLM Structured Execution)**: Resolution Pass ei palauta vapaata tekstiä, vaan se pakotetaan käyttämään Native Structured Outputs API:a (`LLMTaskExecutor.execute_structured_task()`) EnrichedAtom-muotoon.
* **00-antigravity-core.md (Zero-Compromise Pledge)**: Evaluation Hookit on kirjoitettava natiivisti Pythonilla. Järjestelmä ei saa luottaa LLM:n subjektiiviseen "ehdolliseen ymmärrykseen" arviointivaiheessa, vaan Python DAG päättelee ehtojen täyttymisen.
* **Forensic Immutability Mandate**: `source_quote` -kenttä on MUUTTUMATON (immutable). Resolution Pass EI SAA koskaan ylikirjoittaa tai muokata alkuperäistä lainausta generoidessaan `resolved_claim`-kenttää. Molemmat kentät on säilytettävä rinnakkain, koska `source_quote` on forensinen todistusaineisto ja `resolved_claim` on järjestelmän tulkinta siitä. Ilman molempia järjestelmän debuggaus ja auditointi on mahdotonta.
* **Reason-then-Format Mandate (Tam et al., EMNLP 2024)**: Skeeman kenttäjärjestys on kriittinen. LLM:n tulee tuottaa ensin vapaamuotoinen päättely (`resolved_claim`) ja vasta sitten strukturoitu metadata (`conditions`, `depends_on_local_indices`). Tämä estää "Format Tax" -ilmiön, jossa tiukka skeemarakenne heikentää LLM:n analyyttistä syvyyttä.
* **Probabilistic Condition Evaluation Mandate (Language Variance)**: Aiempi oletus deterministisestä merkkijonohausta ehtojen täyttymisessä on kumottu. Kielen äärettömän varianssin vuoksi ("If system compromised" vs. "Upon network breach") tiukka string-matching tuottaa massiivisesti vääriä negatiivisia (False Negatives). Siksi ehdon toteutumisen arviointi (Condition Evaluation) on **Fundamentally Probabilistic** ja vaatii LLM-päättelyä. Se on ajettava ensemble-moodissa (`high_entropy = True`) luotettavuuden takaamiseksi.

* **The Universal Ingress Pipeline Mandate:** Järjestelmä siirtyy hajautetuista LLM-jäsennysvirityksistä yhteen keskitettyyn Ingestion Boundary -moduuliin (esim. `backend_v2/services/llm/ingress_pipeline.py`). Sekä Epic 91 että Epic 92 hyödyntävät tätä yhteistä "Tolerant-Read / Strict-Write" -airlockia.
* **Token Compression & Explicit Attention Anchors:** LLM:n palauttamat toistuvat datat pakotetaan käyttämään Positional Array -rakennetta (`Tuple[str, ...]` eli `[["...", "..."]]`) raskaiden JSON-avaimien sijaan, mikä leikkaa token-bloatia jopa 40 %. **Kriittinen rajoite graafeille:** Vaikka tupleja käytetään, atomien välisissä graafiriippuvuuksissa ei saa luottaa pelkkään implisiittiseen taulukkoindeksiin (koska LLM ei osaa laskea ja hallusinoi). Graafeissa on pakko käyttää eksplisiittisiä "Attention Ankkureita" tuplen sisällä (esim. `[["a0", "Väite 1", []], ["a1", "Väite 2", ["a0"]]]`), jotta LLM:n huomiomekanismi (Attention) pysyy kiinni todellisuudessa. Universal Ingress Pipeline hoitaa näiden tuplejen hydraation.

### 2.1 Epistemic Boundaries (Tiedolliset Rajat)
Estääksemme järjestelmätason hallusinaatiot, meidän on armottomasti valvottava rajaa sen välillä, mitä LLM saa arvata ja mitä Pythonin on pakko todistaa.

**100% Deterministic (Vaatii tiukan Python/Pydantic-logiikan):**
* **DAG Structural Integrity:** Syklin tunnistus (Cycle detection, O(V+E) DFS) ajetaan Pythonissa. LLM ei koskaan verifioi omaa graafitopologiaansa.
* **Stateful Short-Circuiting (N/A Cascade):** Tilan `N/A - Condition Not Met` eteneminen. Jos Python vastaanottaa tiedon, että Ehto A on epätosi, Python **deterministisesti pysäyttää** Seurauksen B suorituksen (N/A). LLM:llä on nolla (0) reititysvaltaa suoritusaikana.
* **Tainted State Propagation (The Epistemic Circuit Breaker):** Jos solmu A joutuu karanteeniin (Epic 91 asettaa `source_id = None`), sen tila on `CONTESTED`. Kahnin algoritmin on suoritettava **Epistemic Cascade** ennen Vector-hakuja: Jos yksikin riippuvuus on `CONTESTED` tai `BLOCKED_BY_TAINT`, solmu ei saa suorittaa vektorivertailua eikä pudota tilaan `N/A`. Se perii saastumisen ja palauttaa tilan `NodeState.BLOCKED_BY_TAINT`. UI (Epic 90) renderöi tämän varoituksena (`visual_intent = warning`): *"🔒 Pending Human Review of upstream condition."* Tämä ratkaisee 'Phantom Taint Deadlock' -haavoittuvuuden.
* **ID Resolution:** Paikallisten taulukkoindeksien (`local_index`) kääntäminen muuttumattomiksi, globaaleiksi Stripe Opaque ID -tunnuksiksi (`tda_ids`).

**Fundamentally Probabilistic (Vaatii LLM- tai Vektori-päättelyä):**
* **Causal Edge Mapping:** Sen semanttisen suhteen päätteleminen tekstistä, joka määrittää että Väite B riippuu loogisesti Väitteestä A.
* **Implicit Anaphora:** Abstraktien tai toimialakohtaisten pronominien ("Yllä mainittu viitekehys") purkaminen, missä deterministinen perinteinen NLP kaatuu.
* **Speculative Matrix Pre-computation (Condition Evaluation):** Kielellisen varianssin vuoksi ehtojen täyttymistä ei voida arvioida regexillä. Jotta vältämme Kahnin algoritmin pysähtymisen sekventiaalisten upotuskutsujen takia (GIL / I/O -pullonkaula), suoritamme **Speculative Matrix Pre-computation** -operaation. Lähdedokumentti upotetaan yhtenäiseksi tensorimatriisiksi (`T_corpus`) jo ingestion-vaiheessa. Ennen DAG-ajon alkua, keräämme kaikki `condition_text` -merkkijonot kaikilta topologisilta syvyyksiltä ja upotamme ne yhdellä API-eräajolla (`T_conditions`). Tämän jälkeen laskemme kaikki kosinietäisyydet yhdellä salamannopealla matriisikertolaskulla ($O(1)$ ajassa, `T_conditions @ T_corpus.T`). Tämä luo reaaliaikaisen, muistinvaraisen totuustaulun (Cosine Similarity > 0.85) kaikista ehdoista, sallien Kahnin algoritmin reitittää graafia puhtaasti muistissa ilman minkäänlaista blokkautumista.

## 3. Pydantic-tason Mallit ja Suunnittelu (Proposed Schema Parity)

Lisätään / päivitetään uudet datamallit backendissä. Rakenne noudattaa V2 ydinmallien logiikkaa:

```python
from pydantic import Field, BaseModel, ConfigDict
from typing import Optional, List

class ClaimCondition(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    condition_id: str = Field(pattern=r"^tda_[a-fA-F0-9]{16,32}$", description="TDAAssertion Opaque ID, johon tämä ehto perustuu")
    condition_text: str = Field(description="Ehtolauseke, esim. 'Jos järjestelmä on vaarantunut'")
    source_id: str | None = Field(description="Spatiaalinen ankkuri: Alkuperäisen tekstikappaleen/lähteen ID, josta ehto löytyi.")
    is_hypothetical: bool = Field(description="Flag indicating if this is a hypothetical wrapper")
    
    # Turing-Complete Routing (XNOR Logic)
    expected_boolean_state: bool = Field(
        default=True,
        description="TRUE: Ehto katsotaan täyttyneeksi kun vektoritesti on TOSI (If). FALSE: Ehto katsotaan täyttyneeksi kun vektoritesti on EPÄTOSI (Otherwise/Unless)."
    )

class EnrichedAtom(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    
    tda_id: str = Field(pattern=r"^tda_[a-fA-F0-9]{16,32}$", description="Opaque Stripe ID (TDAAssertion), joka vastaa tätä väitettä")
    resolved_claim: str = Field(description="The absolute claim, with pronouns explicitly resolved by the LLM.")
    source_quote: str = Field(description="Exact verbatim quote from the source text. IMMUTABLE.")
    source_id: str | None = Field(description="Spatiaalinen ankkuri: Lähdedokumentin tai chunkin ID.")
    conditions: Optional[List[ClaimCondition]] = Field(default=None, description="Any conditional wrappers guarding this claim")
    
    # DAG Riippuvuudet (Single-Pass AST lokaalit indeksit käännettyinä fyysisiksi ID:iksi)
    depends_on_tda_ids: List[str] = Field(default_factory=list, description="Pointers to other tda_ids this claim logically depends on")
```

### 3.1 Single-Pass AST Pipeline (Kertavaikutteinen Hierarkkinen Louhinta)

> [!IMPORTANT]
> **Falsification of the Two-Pass Hypothesis:** Alkuperäinen oletus oli, että välimuistin säästämiseksi louhinta ja riippuvuuksien rakentaminen kannattaa jakaa kahteen LLM-vaiheeseen (Format Tax -optimointi). Tämä hypoteesi on kumottu "Cross-Chunk Amnesia" -haavoittuvuuden vuoksi: jos ehto on chunkissa A ja seuraus chunkissa B, toinen vaihe menettää spatiaalisen kontekstin ja joutuu hallusinoimaan riippuvuudet. 
> Siksi Epic 92 siirtyy **Single-Pass AST (Abstract Syntax Tree)** -malliin.

Modernit mallit (GPT-4o) kykenevät natiivisti tuottamaan syviä Pydantic-hierarkioita yhdellä lukukerralla. Kun LLM purkaa tekstiä, se rakentaa samalla lennosta riippuvuusgraafin käyttämällä lokaaleja indeksejä, koska sillä on *koko alkuperäinen teksti aktiivisessa muistissaan*.

#### Suoritusmalli (Single-Pass):
* LLM lukee tekstin ja palauttaa taulukon `EnrichedAtom` -olioita.
* Pronominit ratkaistaan eksplisiittisesti (`resolved_claim`) heti samassa vaiheessa.
* **Paikallinen viittaus (Local Indices):** Koska Python ei ole vielä ehtinyt luoda fyysisiä Opaque ID -tunnuksia atomeille, LLM käyttää sisäisiä indeksejä (esim. `local_index: 0`, `depends_on_local_indices: [0]`).

#### Kustannus- ja Latenssianalyysi
* **Poistettu Duct Tape:** Vältytään raskaalta `AliasResolutionService` -rakennelmalta, jossa pitkiä ID-tunnuksia muutettaisiin `[claim_1]` -aliaksiksi ja lähetettäisiin takaisin LLM:lle.
* **Nopeus:** Yksi API-kutsu per chunk verrattuna kahteen.
* **Laatu:** LLM:n ei tarvitse arvailla kontekstia jälkikäteen, mikä pudottaa hallusinaatioriskin lähelle nollaa.

### 3.2 Lokaalien indeksien kääntäminen Opaque ID:ksi (Python Resolving)

Miten alkuperäinen fyysinen ID-anto suhtautuu tähän uuteen malliin? Erinomaisesti, mutta järjestys muuttuu puhtaasti Python-vetoiseksi tapahtumaksi.

**JSON, jonka LLM palauttaa yhdellä passilla:**
```json
[
  { "local_index": 0, "resolved_claim": "Järjestelmä on vaarantunut" },
  { "local_index": 1, "resolved_claim": "Data poistetaan", "depends_on_local_indices": [0] }
]
```

**Pythonin suorittama deterministinen konversio:**
1. Python vastaanottaa JSON:in.
2. Python generoi fyysiset, globaalit Opaque Stripe ID:t (esim. `tda_A` ja `tda_B`) taulukon riveille 0 ja 1.
3. Python korvaa Pydantic-validaatiossa `depends_on_local_indices: [0]` muotoon `depends_on_tda_ids: ["tda_A"]`.
4. Lopuksi `local_index` -kentät tuhotaan (ephemeral), ja lopputuloksena on täysin globaalisti validi ja muuttumaton DAG-graafi.

Tämä on arkkitehtuurisesti huomattavasti suoraviivaisempi (elegantimpi) ja vähentää riippuvuuksia "purkkaliimoista" (kuten kustomoiduista alias-parseroinneista).

### 3.3 Disjunctive Condition Trap (XOR / Otherwise Branching)

Yksi arkkitehtuurin vaarallisimmista reunaehdoista (Edge Case) on ns. "Otherwise"-haaroitus.
**Skenaario:** *"Jos järjestelmä on vaarantunut, poista data. Muussa tapauksessa kirjaa normaali tila."*
**Ongelma:** Jos molemmat väitteet sidotaan samaan ehtoon (järjestelmä on vaarantunut), ja järjestelmä *ei* ole vaarantunut, molemmat peruutettaisiin (N/A). Tällöin "kirjaa normaali tila" -protokolla jäisi kokonaan arvioimatta, mikä aiheuttaisi vakavan compliance-sokean pisteen.

Tämän ratkaisemiseksi `ClaimCondition`-skeemaan lisättiin **Turing-Complete Routing (XNOR Logic)**:
* "Poista data" -väitteen ehdolle annetaan `expected_boolean_state = True`.
* "Kirjaa normaali tila" -väitteen ehdolle annetaan `expected_boolean_state = False`.

Kahnin algoritmia ajava arviointimoottori vertaa vektoritarkistuksen fyysistä tulosta tähän odotusarvoon XNOR-logiikalla: `if vector_check_result == expected_boolean_state`. 
Vain jos totuusarvot täsmäävät, atomi arvioidaan. Tämä mahdollistaa äärimmäisen monimutkaiset loogiset portit (esim. `A AND NOT B`) suoraan Python-kerroksessa sallimalla per-ehto polariteetin.

**Pydantic-tason varoitus (Auditoinnin läpinäkyvyys):**
Lisätään `EnrichedAtomBatch` (tai vastaavaan root-tason Pydantic-malliin) validaattori: Jos samaan `condition_id`:hen viittaavat atomit kaikki ovat `expected_boolean_state = True` (eli yhdelläkään ei ole `False`-haaraa), generoidaan `WARNING`-loki. Tämä ei estä suoritusta, mutta tekee auditoijalle välittömästi näkyväksi mahdollisen puutteen säännöstössä (eli "Muussa tapauksessa" -haara on saattanut unohtua).

### 3.4 Forensic Spatial Binding (Alemman tason ID:iden hyödyntäminen)
Ajoista saatavia alemman tason lähde-ID:itä (`source_id` / `used_evidence_ids`) hyödynnetään nyt kriittisenä spatiaalisena ankkurina:
1. **Anaphora-resoluution rajaus:** Kun LLM päättelee, mihin sana "Se" viittaa `resolved_claim`-kentässä, arviointi sidotaan `source_id`:n avulla vain siihen spesifiin tekstikappaleeseen (chunk), mistä lainaus on peräisin. Tämä estää mallia hallusinoimasta subjekteja muista dokumenteista.
2. **Ehtojen fyysinen eristys (Conditional Logic):** `ClaimCondition` sisältää oman `source_id`:n. Ehtoarviointi (deterministinen merkkijonohaku) suoritetaan vain tässä spesifissä lähde-ID:ssä. Tämä takaa, että ehto ("Jos järjestelmä on vaarantunut") arvioidaan juuri siinä kontekstissa missä se esitettiin, eikä se vuoda ristiin muiden dokumenttien ehtojen kanssa.


### 3.4 Ratkaisu "Cross-Chunk Amnesialle" (Rajat Ylittävä Riippuvuus)

Koska siirryimme Single-Pass AST -malliin (ei enää erillistä vaihetta, joka lukee kaikki atomit kerralla), meidän on ratkaistava tilanne, jossa Ehto A sijaitsee dokumentin alussa (Chunk 1) ja Seuraus B lopussa (Chunk 2). LLM ei Chunk 2:ta lukiessaan näe Chunk 1:n lokaaleja indeksejä. Tähän sovelletaan kahta arkkitehtuurista sääntöä, joiden valinta tapahtuu dynaamisesti token-määrän perusteella:

#### 3.4.1 MACRO_CHUNK_TOKEN_LIMIT ja Automaattinen Reititys
Jotta järjestelmä osaa valita oikean strategian ilman käyttäjän päätöksiä, lisäämme `backend_v2/models/enums.py` -tiedostoon uuden rajan:
```python
class SystemConcurrency(int, Enum):
    # ...
    # Kynnysarvo, jonka jälkeen siirrytään Macro-Chunkingista Rolling Contextiin
    MACRO_CHUNK_TOKEN_LIMIT = 100000 
```

Ennen LLM-kutsun suorittamista, asynkroninen orkestraattori (`services/llm_task_executor.py` tai vast.) laskee lähdetekstin fyysisen token-määrän (esim. `tiktoken`). Tämän perusteella orkestraattori valitsee suorituspolun automaattisesti:

#### 3.4.2 Suorituspolku A: Macro-Chunking (Ensisijainen sääntö)
Jos `document_tokens < MACRO_CHUNK_TOKEN_LIMIT`:
Modernien mallien (GPT-4o, Claude 3.5 Sonnet) laaja konteksti-ikkuna tarkoittaa, että keinotekoista pilkkomista (Micro-Batching) **ei käytetä** atomisaatiossa. Asiakirja syötetään yhtenä ainoana "Macro-Chunkina". Cross-Chunk Amnesia eliminoituu täydellisesti, ja Pydantic-mallin `depends_on_local_indices` riittää mihin tahansa viittaukseen (alku- ja loppupään välillä).

#### 3.4.3 Suorituspolku B: Rolling Context Injection (Varajärjestelmä)
Jos `document_tokens >= MACRO_CHUNK_TOKEN_LIMIT` (Massiivinen asiakirja):
Dokumentti on **pakko** pilkkoa osiin. Käytämme vierivää kontekstia (Rolling Context) ilman, että rikomme Single-Pass mallia.
* **Chunk 1:** LLM tuottaa atomit. Python antaa niille globaalit Opaque ID:t (esim. `tda_1`).
* **Chunk 2:** Ennen kuin Chunk 2 lähetetään LLM:lle, orkestraattori injektoi promptin alkuun `<previous_claims>`-XML-blokin, joka sisältää Chunk 1:stä puretut ehdot ja niiden Opaque ID:t (esim. `tda_1: "Järjestelmä on vaarantunut"`).
* **Pydantic-päivitys:** `EnrichedAtom` -skeema sallii riippuvuuksien asettamisen joko uusiin paikallisiin viitteisiin TAI suoraan edellisen chunkin globaaleihin Opaque ID -tunnuksiin:

```python
class EnrichedAtom(BaseModel):
    # ...
    depends_on_local_indices: List[int] = Field(default_factory=list, description="Dependencies within this same chunk")
    depends_on_previous_tda_ids: List[str] = Field(default_factory=list, description="Dependencies on claims explicitly passed in the <previous_claims> context")
```

Tämä ratkaisee globaalin DAG-eheyden täydellisesti ilman rumaa Alias Mapping -jälkikäsittelyä tai hallusinaatioherkkiä Two-Pass -kierroksia.

### 3.5 Topological Blocking ja Amdahlin Laki (Latenssin Hallinta)

Tunnistettu riski: *Quorum tällä hetkellä arvioi litteitä atomilistoja täysin rinnakkain (asyncio.gather). DAG pakottaa peräkkäisen suorituksen. Jos ketju on syvä (A → B → C), latenssi kasvaa lineaarisesti muodostaen Amdahlin pullonkaulan.*

Tämän ratkaisemiseksi arviointimoottori (Scoring Engine) siirtyy käyttämään matematiikkaan perustuvaa **Sub-Graph Parallelization (Kahn's Algorithm)** -reititystä:

**Erillinen moduuli (Monoliitin torjunta):**
Kahnin algoritmi ja DAG-evaluointi toteutetaan puhtaasti omaan tiedostoonsa (esim. `services/dag_evaluator.py`), jotta jo valmiiksi massiivinen `scoring.py` ei paisu. Tämä uusi moduuli ottaa vastaan atomilistan, laskee topologiset tasot ja palauttaa evaluointijärjestyksen. `scoring.py` kutsuu sitä vain ulkoisesti.

1. **Topological Depth Grouping (Kahnin Algoritmi):**
   * Ennen arvioinnin aloittamista Python laskee DAG:in Weakly Connected Components (WCC) ja ryhmittelee atomit topologisen syvyyden (Topological Depth) mukaan.
   * Kaikki atomit, joilla ei ole riippuvuuksia (Depth 0), arvioidaan täysin rinnakkain (`asyncio.gather`).
2. **Kaskadoitu Rinnakkaisuus:**
   * Kun Depth 0 on valmis, moottori kerää tulokset ja käynnistää kaikki Depth 1 -atomit (joilla ehto on täyttynyt) samanaikaisesti.
   * Tämä toistetaan kunnes koko graafi on käsitelty.
3. **Hyödyt:** Tämä palauttaa järjestelmän lähes alkuperäiseen asynkroniseen suorituskykyyn kunnioittaen samalla kausaalisuutta matemaattisen täydellisesti. Se estää täysin Speculative Executionin "turhat" kustannukset (ei arvioida asioita turhaan) ja Strict Lazyn katastrofaalisen latenssin.

---

## 4. Toteutusvaiheet (Implementation Phases)

### Phase 1: Pydantic Schema ja Resolution Pass Promptien Päivitys
* Implementoidaan `EnrichedAtom`, `ClaimCondition` and `EnrichedAtomBatch` -mallit backendiin.
* **Kustannusoptimointi:** Ei lisätä uutta erillistä LLM-kutsua! Päivitetään Atomization-vaiheen olemassa olevat LLM-promptit (Admin Studiossa/Seed-kannassa) ohjeistamaan pronominien purkamista ja ehtojen tunnistamista suoraan `EnrichedAtom` -listausta luodessa.

### Phase 2: Evaluation Enginen Ehdollinen Logiikka (Kahn's Algorithm & Vector Pre-Check)
* Muokataan Scoring Enginea rakentamaan DAG (Directed Acyclic Graph) `depends_on_tda_ids` -kenttien perusteella ja ryhmittelemään atomit Kahnin algoritmilla (Topological Depth Grouping).
* **Vectorized Semantic Pre-Check:** *Tiedolliset Rajat (Epistemic Boundaries)* -linjauksen mukaisesti ehdon totuusarviointia **ei** suoriteta deterministisellä merkkijonohaulla (regex) eikä raskaalla LLM-kutsulla. Ehdon teksti ja lähdeteksti muutetaan upotusvektoreiksi (esim. `text-embedding-3-small`), ja ehto katsotaan todeksi, jos Cosine Similarity on yli asetetun raja-arvon (esim. 0.85).
* Jos atomilla on ehtoja ja vektorivertailu toteaa, että ehto ei täyty, atomi merkitään välittömästi tilaan `N/A - Condition Not Met` välttäen False Positive -rangaistuksen. Vain jos ehto täyttyy (Cosine > 0.85), `resolved_claim` lähetetään varsinaiseen raskaaseen LLM-arviointiin.

### Phase 3: Executions.py ja DAG-läpinäkyvyys (Execution & Traceability)
* Hyödynnetään Opaque Stripe ID:tä (`atom_id`) `executions.py`-reitittimessä ja `dag_executor.py`:ssä rakentamaan visuaalinen ja matemaattinen suorituspuu (Execution Graph).
* Kun `executions.py` muodostaa lopputuloksen (esim. PDF-raportin tai JSON-palautuksen), `depends_on_atom_ids` -relaatioita käytetään esittämään looginen ketju: *"Koska ehto [atm_123] toteutui, väite [atm_456] arvioitiin"*. Tämä ratkaisee System 2 -tason selitettävyyden (XAI).
* Kuten aiemmissa Epiceissä (esim. Epic 59 Contextual Override), ainutlaatuinen `atom_id` mahdollistaa yksittäisten atomien tilan (PASS/FAIL/N/A) täsmällisen päivittämisen ja auditoinnin suorituksen aikana.

### Phase 4: Kieliriippumattomuus (Cross-Lingual Resilience)
* **LLM Semantic Parsing:** Koska Resolution Pass (Stage 1) luottaa kielimallin (LLM) syvään semanttiseen ymmärrykseen, anaphoran purkaminen on kieliriippumatonta. LLM ymmärtää pro-drop -kielten (esim. suomi: "Meni kauppaan") piilopronominit, agglutinatiiviset päätteet ja englannin eksplisiittiset pronominit ("He went") yhtä lailla.
* **Agnostinen Python-kerros:** Stage 2:n Python-kerros ja Pydantic-mallit (`depends_on_atom_ids`) toimivat puhtaasti matemaattisilla graafeilla. Koodi ei etsi tekstistä sanaa "Jos" tai "If", vaan ohjaa suoritusta täysin kieliriippumattomien Opaque Stripe ID -relaatioiden avulla.

### Phase 5: Telemetrian ja Raportoinnin Integrointi
* Varmistetaan, että `N/A` tai ehdolliset atomit eivät riko nykyistä UI:ta.
* Päivitetään mahdolliset raportointinäkymät esittämään "Ehto ei täyttynyt" eksplisiittisesti, jotta käyttäjä ymmärtää miksi väitettä ei penalisoitu.
* **Explicit Short-Circuit Metadata**: Kun atomi merkitään `N/A`-tilaan, järjestelmä tallentaa aina seuraavan metadatan:
  * `short_circuit_reason_atom_id`: Viittaus siihen ehto-atomiin (`atom_id`), joka ei täyttynyt ja laukaisi ohituksen.
  * `short_circuit_evaluation`: Ehdon arvioinnin tulos (`FALSE` = ehto ei täyttynyt, `DLQ` = ehdon arviointi kaatui teknisesti).
  * Ilman tätä metatietoa `N/A` olisi musta laatikko — auditoija näkisi ohituksen mutta ei koskaan tietäisi miksi.

---

## 5. Definition of Done (DoD)
1. **Schema Validation**: Atomien louhinta palauttaa `EnrichedAtom` -rakenteita. Pronominien resolving tapahtuu yhdessä ainoassa optimoidussa LLM-kutsussa.
2. **Conditional Short-Circuit**: Ehdolliset atomit ohitetaan `calculate_rule_satisfied()` -metodissa, jos itse ehto ei ole toteutunut kohdedatassa.
3. **Short-Circuit Traceability**: Jokainen `N/A`-tila sisältää `short_circuit_reason_atom_id` -kentän.
4. **Pydantic V2 Parity & Cycle Detection**: Mallit estävät rikkinäiset linkit (Broken DAG links) ja ikuiset silmukat (Circular Dependencies) O(V+E) DFS-algoritmilla jo Pydantic-validaatiossa.
5. **Audit Loop**: Kaikki uudet ja vanhat yksikkötestit menevät läpi `uv run python scripts/backend_audit_loop.py` -ajossa.

---

## 6. Käyttöliittymän ja Seed-Datan Muutokset (Admin Studio UI)

Jotta "Enriched Atom Graph" voidaan konfiguroida ja tuloksia ymmärtää, Admin Studio -käyttöliittymä (Flutter) vaatii seuraavat päivitykset:

### 6.1 Prompt Editor (Seed Data & System Blocks)
* **LLM Ohjeistuksen hallinta**: Admin Studioon lisätään/päivitetään erityinen `PromptBlock` (esim. *Resolution Pass Protocol*), jonka kautta ylläpitäjä voi hallinnoida tekstin purkuohjeita (pronominien ratkaisu ja ehtojen irrotus). Tämä tekee louhintalogiikasta läpinäkyvän ja dynaamisesti säädettävän ilman backendin koodimuutoksia.

### 6.2 Matrix Editor (TDAAssertion Config)
* **Käyttöliittymän yksinkertaisuus säilyy**: Varsinaisten arviointisääntöjen (Matrix) kirjoittaminen säilyy yhtä helppona kuin ennenkin. Ylläpitäjä määrittelee arvioitavan asian, ja järjestelmän uusi DAG-kerros hoitaa kontekstin automaattisesti.
* **Uusi asetus (Ehdollinen Ohitus)**: Sääntöeditoriin lisätään kytkin: *"Salli ehdollinen keskeytys (Enable Conditional Short-Circuit)"*. Jos tämä on pois päältä, sääntö arvioidaan pakolla riippumatta siitä, täyttyikö tekstin sisäinen ennakkoehto. Tämä antaa ylläpitäjälle kontrollin säädellä, kuinka tiukasti tekstiä rangaistaan.

### 6.3 Audit Trail / Suoritusraportti UI (Execution Viewer)
Tämä on merkittävin visuaalinen muutos loppukäyttäjälle ja auditoijalle:
* **Graafinen Puunäkymä (DAG Viewer)**: Matriisin tulosnäkymässä tulokset voidaan sisentää riippuvuuksien mukaan. Ehtolause näkyy ylätasona, ja sen alaisuudessa on ehdollinen väite.
* **Uusi Status: `N/A` (Harmaa) + Short-Circuit Metadata**: Punaisen (`FAILED`) ja vihreän (`PASSED`) rinnalle tuodaan harmaa/neutraali tila. `N/A`-tilalla on aina näkyvissä syy: auditoija näkee suoraan, mikä ehtoatomi epäonnistui (esim. *"Ohitettu: Ehto [atm_abc123] 'Järjestelmä on vaarantunut' → FALSE"*). Klikkaus vie suoraan ehtoatomin yksityiskohtiin.
* **Spatiaalinen Korostus (Ankkurointi)**: Jos käyttäjä klikkaa ehdollista väitettä, käyttöliittymän lähdetekstinäkymä (Source Text Viewer) korostaa tarkalleen sen ehtolauseen ("Jos järjestelmä on vaarantunut..."), joka laukaisi tai esti arvioinnin.

---

## 8. Vaikutusanalyysi: Mitä Epic 92 muuttaa käytännössä?

> [!NOTE]
> Tämä osio selittää Epicin vaikutukset arkikielellä. Se on tarkoitettu sekä tekniselle tiimille että liiketoimintapäättäjille, jotka haluavat ymmärtää, miksi tämä muutos kannattaa tehdä.

### 8.1 Mitä ajoissa muuttuu (Execution Impact)

#### 8.1.1 Nykytilan ongelma konkreettisena esimerkkinä

Kuvitellaan, että arvioitava teksti sisältää lauseen:

> *"Jos järjestelmä on vaarantunut, kaikki käyttäjädata poistetaan välittömästi."*

**Nykyinen järjestelmä (ennen Epic 92)** purkaa tämän lauseen kahdeksi erilliseksi "atomiksi":
1. `tda_A`: "Järjestelmä on vaarantunut" → LLM arvioi: löytyykö tämä tekstistä? → **FAIL** (ei löydy, koska järjestelmä ei ole vaarantunut)
2. `tda_B`: "Kaikki käyttäjädata poistetaan välittömästi" → LLM arvioi: löytyykö tämä tekstistä? → **FAIL** (dataa ei ole poistettu, koska ei ole syytä poistaa)

Molemmat saavat FAIL-tuloksen, mikä on **teknisesti oikein mutta loogisesti väärin**. Alkuperäinen lause on ehdollinen: dataa poistetaan *vain jos* järjestelmä on vaarantunut. Koska järjestelmää ei ole vaarantunut, datan poistamatta jättäminen on oikeaa toimintaa — ei virhe. Silti järjestelmä rankaisee tästä. Tämä on **väärä negatiivinen** (False Negative).

#### 8.1.2 Miten Epic 92 korjaa tämän

**Epic 92:n jälkeen** sama lause käsitellään näin:

1. **Pass 1 (Louhinta):** LLM lukee tekstin ja tunnistaa:
   - Väite B ("data poistetaan") riippuu ehdosta A ("järjestelmä on vaarantunut")
   - LLM merkitsee: `tda_B.conditions = [{ condition_text: "Jos järjestelmä on vaarantunut", condition_id: tda_A }]`

2. **Pass 2 (Graafin rakennus):** LLM saa väitelistan alias-muodossa (`claim_1`, `claim_2`) ja vahvistaa riippuvuuden: `claim_2 depends_on claim_1`.

3. **Python-arviointi (deterministinen):** Scoring Engine tarkistaa ensin ehdon:
   - Onko `tda_A` ("järjestelmä on vaarantunut") totta? → Deterministinen merkkijonohaku lähdetekstistä → **EI löydy** → Ehto on FALSE.
   - Koska ehto on FALSE, `tda_B`:tä **ei arvioida lainkaan**. Se saa tilan **`N/A - Condition Not Met`**.
   - Tallennettava metadata: `short_circuit_reason_tda_id: tda_A`, `short_circuit_evaluation: FALSE`.

**Lopputulos:** Väärä rangaistus eliminoitu. Auditoija näkee tarkalleen *miksi* väitettä ei arvioitu.

#### 8.1.3 Pronominien purku (Anaphora Resolution) käytännössä

Toinen yleinen ongelma nykytilassa: pronominit. Jos teksti sanoo:

> *"Palvelin kaatui tiistaina. Se aiheutti vakavan häiriön tietokantajärjestelmässä."*

**Nykytilassa** atomi "Se aiheutti vakavan häiriön" on merkityksetön, koska LLM ei tiedä, mihin "Se" viittaa. Se saattaa arvata väärin tai jättää arvioinnin epämääräiseksi.

**Epic 92:n jälkeen** `resolved_claim` -kenttä sisältää puretun version:
- `source_quote`: *"Se aiheutti vakavan häiriön tietokantajärjestelmässä."* (alkuperäinen, muuttumaton)
- `resolved_claim`: *"Palvelinkaatuminen aiheutti vakavan häiriön tietokantajärjestelmässä."* (pronomini purettu)

LLM arvioi nyt `resolved_claim`-kenttää, joka on yksiselitteinen. Alkuperäinen `source_quote` säilyy forensisena todisteena rinnalla (Immutability Mandate).

#### 8.1.4 Kustannusvaikutus ajoihin

| Mittari | Vaikutus | Selitys |
|---|---|---|
| **LLM-kutsut** | +1 kevyt lisäkutsu (Pass 2) | Graafin rakennus on lyhyt JSON-linkitys, ei raskas analyysi |
| **Oikosuljetut kutsut** | -N kutsua per ajo | Jos ehto A ei täyty, ehdosta A riippuvia sääntöjä ei lähetetä LLM:lle lainkaan |
| **Retry-luupit** | Merkittävästi vähemmän | Kaksi yksinkertaista tehtävää tuottaa vähemmän Pydantic-validaatiovirheitä kuin yksi monimutkainen |
| **Nettovaikutus** | Neutraali tai säästöä | Riippuu matriisin koosta: mitä enemmän ehdollisia sääntöjä, sitä enemmän säästöä |

### 8.2 Mitä uutta voimme kertoa tulosteena (Reporting Impact)

#### 8.2.1 Nykytilan raportointikyvykkyys

Tällä hetkellä ajon tuloste on käytännössä **litteä lista** tuloksia. Esimerkki `tulokset.csv`:stä:

```
tda_728cd0dff738... → PASS  (confidence: 1.0)
tda_64cce5cf564a... → FAIL  (confidence: 1.0)
tda_82f0d074668...  → CONTESTED (confidence: 0.67)
```

Auditoija näkee **mitä** tapahtui (PASS/FAIL), mutta ei **miksi**. Hän ei tiedä, olivatko tulokset toisistaan riippuvaisia, eikä hän tiedä, olisiko FAIL pitänyt olla N/A ehdollisuuden takia.

#### 8.2.2 Epic 92:n jälkeinen raportointikyvykkyys

Epic 92 mahdollistaa viisi täysin uutta tiedon tasoa, joita voimme tarjota tulosteena:

##### Taso 1: Kausaalinen selitysketju (XAI / Explainability)
> *"Väite `claim_2` ('Talouden perusta rakoilee') sai tuloksen PASS, **koska** sen ennakkoehto `claim_1` ('Luonnon kantokyky murenee') toteutui lähdetekstissä. Syy-seuraussuhde löydettiin lähteestä `src_1`: 'Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee.'"*

Auditoija näkee nyt **miksi** jokin arvioitiin tietyllä tavalla. Tämä on merkittävä ero verrattuna pelkkään "PASS, confidence 1.0" -riviin. Käyttäjä voi kyseenalaistaa syy-seurausketjun, ja järjestelmä voi näyttää sen perustelut.

##### Taso 2: Ehdollinen ohitus perusteluineen (N/A State)
> *"Väite `claim_5` ('Käyttäjädata poistetaan') → **N/A** — Ehto ei täyttynyt.*
> *Syy: Ennakkoehto `claim_3` ('Järjestelmä on vaarantunut') arvioitiin tilaan FALSE.*
> *Lähde: Dokumentti `src_1`, kappale 4."*

Tämä on täysin uusi tila, jota nykyinen järjestelmä ei tunne. `N/A` ei ole PASS eikä FAIL — se tarkoittaa, että väitteen arviointi **ei ollut relevantti** tässä kontekstissa. Ilman tätä tilaa sama väite saisi väärän FAIL-rangaistuksen.

##### Taso 3: Forensinen jäljitettävyys (source_quote vs. resolved_claim)
> *Alkuperäinen lainaus: "Se aiheutti vakavan häiriön järjestelmässä."*
> *Ratkaistu väite: "Palvelinkaatuminen aiheutti vakavan häiriön tietokantajärjestelmässä."*
> *Lähde: `src_2` (Raportti_Q3_2024.pdf)*

Auditoija näkee rinnakkain **mitä teksti oikeasti sanoi** ja **miten järjestelmä tulkitsi sen**. Jos tulkinta on väärä (LLM purki "Se"-pronominin väärin), virhe on välittömästi havaittavissa ja korjattavissa. Ilman molempia kenttiä debuggaus olisi mahdotonta, koska kukaan ei tietäisi, oliko virhe alkuperäisessä tekstissä vai järjestelmän tulkinnassa.

##### Taso 4: Riippuvuusgraafi (DAG-visualisointi)
Raporttiin voidaan piirtää visuaalinen puu, jossa näkyy mitkä väitteet riippuivat toisistaan:
```
claim_1 (PASS) ─┬─ claim_2 (PASS)
                └─ claim_3 (FAIL) ── claim_4 (N/A, ehto ei täyttynyt)
```
Tämä on **selitettävyyttä (XAI)**, jota yksikään tunnettu kilpaileva arviointijärjestelmä ei tarjoa. Useimmat FActScore-pohjaiset järjestelmät tuottavat vain litteitä listoja; Quorum tuottaa kausaalisen puun.

##### Taso 5: Spatiaalinen ankkurointi (Source Binding)
> *"Tämä väite löydettiin dokumentista `Raportti_Q3.pdf`, kappale 7.*
> *Ehto löydettiin samasta dokumentista, kappale 3."*

Kun järjestelmä arvioi useita dokumentteja samanaikaisesti (esim. raportti + chatlog + tuoteteksti), spatiaalinen ankkurointi varmistaa, ettei väitteitä sekoiteta ristiin eri dokumenttien välillä. Auditoija voi klikata suoraan oikeaan kohtaan lähdetekstissä.

### 8.3 Vertailutaulukko: Ennen ja jälkeen

| Dimensio | Nykytila (ennen Epic 92) | Epic 92:n jälkeen |
|---|---|---|
| **Tulostilat** | PASS / FAIL / DLQ / CONTESTED | PASS / FAIL / DLQ / CONTESTED / **N/A** |
| **Selitys tulokselle** | "Mikä" (pelkkä tulos) | "Mikä" + **"Miksi"** + **"Mistä"** |
| **Väärät negatiiviset** | Yleisiä ehdollisissa lauseissa | Eliminoitu N/A-tilalla ja ehtoarvioinnilla |
| **Pronominit** | Ratkaisematta → hallusinaatioriski | Purettu eksplisiittisesti → `resolved_claim` |
| **Riippuvuudet väitteiden välillä** | Ei tietoa (litteä lista) | Täysi DAG-graafi (`depends_on_tda_ids`) |
| **Lähteen jäljitettävyys** | `source_quote` + `source_id` | `source_quote` + `resolved_claim` + `source_id` + ehdon lähde |
| **Auditoitavuus** | Litteä tulosrivi | Kausaalinen puu perusteluineen |
| **LLM:n kognitiivinen kuorma** | Kaikki yhdellä kutsulla | Jaettu kahteen kevyeen askeleeseen (Two-Pass) |
| **Hallusinaatiosuoja ID:ille** | `src_N` -aliakset (vain dokumenteille) | Yleistetty `AliasResolutionService` (dokumentit + väitteet) |

### 8.4 Miksi tämä kannattaa toteuttaa — Liiketoiminta-argumentit

1. **Luotettavuus:** Ehdolliset väärät negatiiviset ovat vakava uskottavuusongelma. Jos järjestelmä rankaisee käyttäjää asiasta, joka on kontekstissaan täysin oikein, käyttäjä menettää luottamuksensa koko arviointiin. Epic 92 poistaa tämän systemaattisen vääristymän.

2. **Selitettävyys (XAI):** Sääntelypaineet (esim. EU AI Act) vaativat yhä enemmän algoritmisten päätösten selitettävyyttä. Kausaalinen puu, jossa jokainen päätös on jäljitettävissä lähdetekstiin ja perusteltu, on suoraan tähän tarpeeseen vastaava ominaisuus.

3. **Kustannustehokkuus:** Deterministinen oikosulku (N/A) tarkoittaa, että osa LLM-kutsuista voidaan ohittaa kokonaan. Mitä enemmän ehdollisia sääntöjä matriisissa on, sitä enemmän säästöä. Kaksivaiheinen malli vähentää myös kalliita Retry-luuppeja.

4. **Kilpailuetu:** FActScore ja SAFE (Google DeepMind) ovat alan standardi, mutta ne tuottavat vain litteitä atomeja. Quorumin Enriched Atom Graph on niiden arkkitehtuurinen evoluutio — se säilyttää atomien itsenäisyyden mutta lisää semanttisen verkon päälle. Tämä on julkaisematon ominaisuus akateemisessa kirjallisuudessa.

5. **Kieliriippumattomuus:** Koska pronominien purku (Anaphora Resolution) tapahtuu LLM:n semanttisella tasolla (ei regex-haulla), se toimii yhtä hyvin suomeksi, englanniksi, ruotsiksi tai millä tahansa kielellä. Python-kerros käsittelee vain ID-graafeja, ei koskaan tekstiä.

---

## 9. Tieteelliset Viittaukset (Academic References)

Tämän Epicin arkkitehtuuri perustuu seuraaviin vertaisarvioituihin tutkimuksiin:

* **FActScore** — Min et al. (EMNLP 2023): Atomaarinen propositioiden purkaminen ja itsenäinen verifiointi pitkien LLM-tuotosten hallusinaatioiden havaitsemiseksi.
* **SAFE** (Search-Augmented Factuality Evaluator) — Wei et al. (Google DeepMind, 2024): Hakuavusteinen faktuaalisuuden arviointi atomeista, jossa jokainen väite tarkistetaan itsenäisesti ulkoisia lähteitä vasten.
* **"Let Me Speak Freely?"** — Tam et al. (EMNLP 2024): Empiirinen todiste siitä, että tiukkojen JSON/XML-skeemojen pakottaminen heikentää LLM:n päättelykykyä ("Format Tax"). Perustelee Reason-then-Format -kenttäjärjestyksen.
* **"LLMs Cannot Self-Correct Reasoning Yet"** — Huang et al. (ICLR 2024): Todiste siitä, että LLM ei pysty korjaamaan omia päättelyvirheitään ilman arkkitehtuurisesti erillistä palautetta. Perustelee deterministisen ehtoarvioinnin ja ensemble-äänestyksen.
* **System 2 Attention** — Weston & Sukhbaatar (Meta AI, 2023): Kahnemaenin System 1/System 2 -dualismiin pohjautuva malli, jossa LLM:n autogressiivinen tuotanto (System 1) ohjataan deliberatiivisen validaatiokerroksen (System 2) läpi.
