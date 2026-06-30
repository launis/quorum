# ** EPIC 91: Quote Evidence Architecture & 2-Stage Opaque Schema**

## ** Tavoite**

Poistaa kaikki nykyiset regex-pohjaiset ja merkkijonosplittauksiin (`|||` tai `<<QRM-SRC...>>`) perustuvat purkkaviritykset LLM-koodista, backendin esityskerroksesta (`blueprint.py`) ja Flutterin käyttöliittymästä. Siirtyä puhtaaseen Pydantic-pohjaiseen `QuoteEvidenceDTO`-rakenteeseen, joka takaa 100% deterministisen ja vikasietoisen esitystavan lainauksille ja niiden lähteille ("Quote Evidence Architecture"). Tällä varmistetaan, että lähde-badget ja itse lainaukset näkyvät käyttöliittymässä aina täydellisesti ilman katkeavia lihavointeja.

## ** ARKKITEHTONINEN VIITEKEHYS JA LAATUPERIAATTEET (Hardening-viitekehys)**

Tämän Epicin toteutuksessa noudatetaan Quorum V2:n tiukkaa laadunvarmistuksen ideologiaa:
1. **Zero-Compromise Pydantic-validointi (Sääntö 10):** Kaikki LLM:n tuotokset ja UI-payloadit hydratoidaan ja validoidaan tiukasti Pydantic-malleilla.
2. **Explicit Quarantine State (Transparency over Silent Degradation, Sääntö 100):** LLM on stokastinen. Jos alias-resoluutio (esim. `DOC-99`) epäonnistuu, koko kallista matriisiajoa **EI** saa kaataa, mutta hallusinaatiota **EI SAA** myöskään piilottaa asettamalla lähdettä hiljaisesti Noneksi (Silent Degradation). Viallisen lainauksen `source_id` asetetaan `None`, mutta alkuperäinen `DOC-99` tallennetaan uuteen `unresolved_alias` -kenttään forensista auditointia ja UI-varoituksia varten.
3. **Opaque Stripe ID Mandate (Sääntö 25):** Tietokanta toimii SSOT:na, ja tallentaa relaatiot vain aitojen `doc_...` tyyppisten Opaque ID:iden avulla, ei koskaan ajokohtaisilla "Fake ID":illä.
4. **Taaksepäinyhteensopivuuden Ehdoton Kielto (Zero-Compromise Pledge, Sääntö 52):** Tämän Epicin johdosta **mitään vanhoja ajoja ei tarvitse eikä saa tukea**. Vanhojen matriisiajon datarakenteiden (legacy string-parsing) tukeminen uudessa koodissa on ankarasti kielletty, koska se saastuttaisi uuden arkkitehtuurin. Vanha tietokanta tullaan tuhoamaan ja siementämään uudelleen puhtaalta pöydältä. Tavoitteena on 100% matemaattinen puhtaus uudelle datalle.
5. **Semantic Paraphrase & Chimera Quote Prevention (Airlock 2 - Async Domain Validation):** Pydantic (`Airlock 1`) hoitaa vain rakenteen ja hydraation. Pydantic validoi vain tyypit ja skeeman muodon (onko `quote_fragments` lista jne.). **Fuzzy Matcheria EI SAA ajaa Pydanticin `@model_validator` -metodissa**, koska se on synkroninen ja aiheuttaa Event Loopin nälkiintymistä (GIL Starvation) Kahnin algoritmin evaluoinnin aikana (Epic 92). Sen sijaan luodaan erillinen, asynkroninen **`EvidenceAnchoringService`**, joka ottaa vastaan onnistuneesti hydratoidun `List[QuoteEvidenceDTO]` -listan ja ajaa raskaat Aho-Corasick / Fuzzy -haut eräajoina hyödyntäen `asyncio.to_thread()` -vektorisointia. Tämä estää kaksi hengenvaarallista hallusinaatiota:
   * **Semantic Paraphrase:** LLM muuttaa sanoja (esim. *"shall"* -> *"must"*).
   * **The Chimera Quote (Cross-Chunk Splicing):** LLM yhdistää kaksi erillistä lausetta eri dokumenteista yhdeksi lainaukseksi säästääkseen tokeneita (esim. kolmipisteen `...` avulla). 
   * **Deterministic Python Mitigation (Max-Gap Constraint):** Fuzzy Matcherin algoritmin ja dynaamisen kynnysarvon (`get_lexical_fuzz_threshold()`) on pakotettava tiukka **Max-Gap threshold constraint**. Kun Python yrittää täsmätä `QuoteEvidenceDTO`:ta DOC-1:n raakatekstiin, sen on varmistettava yhtenäinen fyysinen olemassaolo (contiguous physical existence).
   * **The Epistemological Escape Hatch (Multi-Quote Arrays):** Epic 92:n vaatima looginen päättely (Anaphora Resolution) vaatii usein todisteita, jotka ylittävät kappalerajat. Jotta järjestelmä ei taistelisi itseään vastaan (hylkäämällä laillisen, mutta sivutetun datan Chimera-leikkauksena), **LLM:n on sallittava palauttaa taulukko fragmenteista (esim. `["osa 1", "osa 2"]`) yhden merkkijonon sijaan**. Python ajaa Max-Gap -tarkistuksen jokaiselle fragmentille *itsenäisesti*. Näin säilytetään 100% fyysinen todistusketju ilman vääriä CONTESTED-tiloja.
   * **CONTESTED-tilan Pakotus:** Vain jos yksittäisen *fragmentin* sisällä LLM on leikannut tekstejä yli rajojen (spliced texts across boundaries), yhtenäinen haku epäonnistuu. Python puuttuu tähän deterministisesti: se pakottaa `source_id = None`, asettaa lipun `unresolved_alias = "SPLICED_HALLUCINATION"`, ja pakottaa atomin tilaksi **CONTESTED**, mikä vaatii välitöntä ihmisen arviointia (Human Review).

## ** VAIHE 1: LLM Prompt & Pydantic-skeeman uudistus**

**Vastuualue:** Backend (Models & LLM Generation)  
**Tavoite:** Pakottaa LLM tuottamaan rakenteellista JSON-dataa (objekteja) puhtaan merkkijonotekstin sijaan, ja varmistaa tiukka *Opaque Stripe ID Mandate* (esim. `doc_1a2b3c4d5e6f7a8b`) tietokantatasolla.

* **Task 1.1: LLM Prompt -uudelleenkirjoitus (`field_prompts.py`)**
  * **Tiedosto:** `backend_v2/models/prompts/field_prompts.py`
  * Nykyinen `DESC_EXACT_QUOTES` käskee LLM:ää sisällyttämään `<<QRM-SRC-...>>` -aliaksen suoraan merkkijonon sisään (esim. `<<QRM-SRC-INT-INPUTSPRODUCTTEXT>>: [exact quote]`). Tämä on Primitive Obsession -antipattern (Sääntö 97) ja koko ongelman juurisyy.
  * **Uudelleenkirjoita prompt** ohjeistamaan LLM palauttamaan data **Positional Array Ingress** -muodossa Token Compressionin saavuttamiseksi (määritelty Epic 92:ssa): `[["DOC-1", "..."]]`.

* **Task 1.2: Pydantic-mallien luonti (`LLMExtractedQuote` & `QuoteEvidenceDTO`)**
  * **Tiedostot:** Uudet mallit `backend_v2/models/` -hakemistoon.
  * Luo malli **vain LLM:n käyttöön**: `LLMExtractedQuote` (kentät `source_alias: str` ja `text: str | list[str]`). Tämä malli hyödyntää Epic 92:n Universal Ingress Pipelinea (`@model_validator(mode='before')`) tuplejen automaattiseen hydraatioon ja muuntaa yksittäiset stringit listoiksi.
  * Luo malli **SSOT-tietokantaan ja UI-siirtoon**: `QuoteEvidenceDTO` (kentät `source_id: str | None`, `unresolved_alias: str | None`, `quote_fragments: list[str]`, `is_auto_healed: bool = False` ja `is_human_override: bool = False`). (HUOM: Jos `source_id` löytyy, sen on oltava tiukan standardin mukainen Opaque Stripe ID).

* **Task 1.3: Kaikkien neljän LLM-skeeman migraatio**
  * `exact_quotes: list[str]` -> `exact_quotes: list[LLMExtractedQuote]` on muutettava **kaikissa neljässä** Pydantic-mallissa, jotka LLM tuottaa:

  | Malli | Tiedosto | Kuvaus |
  |-------|----------|--------|
  | `LightweightExtractionAtom` | `backend_v2/models/dtos/lightweight_matrix.py` (L153) | Zero-Reasoning -atomi |
  | `AtomEvaluationItemDTO` | `backend_v2/models/dtos/lightweight_matrix.py` (L274) | Evaluointiatomi (pääskema) |
  | `BaseTDAExtraction` | `backend_v2/models/v2_core.py` (L1406) | Micro-CoT -poiminta |
  | `StepDTOStrict` / `StepDTOSemantic` | `backend_v2/models/dtos/evaluation_steps.py` (L66) | Step-evaluointimalli |

  * Lisäksi esityskerroksen DTO: `ScorecardAtomDTO` (`backend_v2/models/v2_core.py` L848).

* **Task 1.4: Listojen Uudelleennimeäminen Aliaksiksi (LLM-rajapinta)**
  * Koska LLM palauttaa tietokantaviitteiden sijaan aliaksia (kuten `DOC-1`), on harhaanjohtavaa kutsua niitä nimellä `_ids`.
  * Muuta LLM-malleissa (`AtomEvaluationItemDTO`, `LightweightExtractionAtom`, `StepDTOStrict`) oleva kenttä `used_evidence_ids` -> `used_source_aliases: list[str]`.
  * Muuta `StepDTOStrict`-mallissa oleva kenttä `source_document_ids` -> `source_document_aliases: list[str]`.
  * Päivitä `field_prompts.py` heijastamaan näitä uusia nimiä ja selventämään, että LLM:n tulee palauttaa aliaksia.

* **Task 1.5: 2-Stage Translation Pipeline (Alias-resoluutio)**
  * **Vaihe 1 - LLM Output (Token-optimoitu Fake ID):** Koska pitkät Opaque ID:t (esim. `doc_1a2b3c4d5e6f7a8b`) kuluttavat tokeneita ja aiheuttavat tekoälylle kirjoitusvirheitä, `AliasRegistry` muutetaan generoimaan erittäin lyhyitä viitteitä LLM:lle (esim. `DOC-1`, `DOC-2`).
  * **Vaihe 2 - Alias-resoluutio ja SSOT-tallennus:** `scoring.py`:n post-prosessointivaiheessa backend muuttaa aliakset aidoiksi Opaque ID:iksi. 
    1. Kääntää `LLMExtractedQuote` -> `QuoteEvidenceDTO`.
    2. Kääntää `used_source_aliases` -> `used_evidence_ids` (SSOT tietokantamalleihin kuten `ScorecardAtomDTO`).
    3. Kääntää `source_document_aliases` -> `source_document_ids`.
  * **Deterministic Reverse-Anchoring (Auto-Healing):** Jos alias on tuntematon (hallusinaatio, esim. `DOC-99`), ennen hylkäämistä `EvidenceAnchoringService` suorittaa nopean merkkijonohaun (esim. Aho-Corasick tai BM25) jokaiselle `quote_fragments`-listan jäsenelle kaikista session aktiivisista lähdedokumenteista. Jos **täydellinen osuma** jokaiselle fragmentille löytyy samasta dokumentista (esim. `doc_456`), Python korjaa `source_id`:n automaattisesti ja asettaa `is_auto_healed = True`. Tämä korjaa LLM:n spatiaalisen hallusinaation turvallisesti.
  * **Serialization Latency & CPU Offloading (`EvidenceAnchoringService`):** Tuhansien `LLMExtractedQuote` -objektien kääntäminen `QuoteEvidenceDTO`:ksi ja raskaiden Fuzzy/Aho-Corasick -merkkijonohakujen ajaminen synkronisessa silmukassa (`scoring.py`) tukkii Pythonin Event Loopin ja aiheuttaa API-latenssipiikkejä. Pydantic-hydraation jälkeen `EvidenceAnchoringService` ajaa prosessin asynkronisena eräajona (Batch Vectorization) hyödyntäen `asyncio.to_thread()` -mekanismia.
  * **Quarantine Fallback:** Vain jos Auto-Healing ei löydä osumaa, `AliasRegistry.resolve()` palauttaa `None`. Tällöin `QuoteEvidenceDTO`:n `source_id` asetetaan `None`, ja alkuperäinen hallusinoitu alias tallennetaan `unresolved_alias` -kenttään (Silent Degradation on kielletty).
  * **HUOM: Resoluution ainoa paikka on `scoring.py`.** `blueprint.py` ei saa koskaan tehdä mitään alias-parsintaa, koska tietokannasta tulevat objektit ovat jo puhtaita Opaque ID -viitteitä.

* **Task 1.6: Explicit Quarantine State (BFF & UI Tuki)**
  * Flutterin käyttöliittymän (UI) on reagoitava `unresolved_alias` -kenttään. Jos se ei ole `null`, käyttöliittymään piirretään varoitusbadge: **"⚠️ Unverified Source ({unresolved_alias})"**.
  * Tämä takaa auditoijille 100% läpinäkyvyyden siihen, että lainaus on tekoälyn hallusinoimasta lähteestä.
  * **Muutos:** Luo `resolve_graceful()` -metodi, joka palauttaa `None` tuntemattomalle aliakselle ja kirjaa `logger.warning`:n. Säilytä vanha `resolve()` muita käyttötarkoituksia varten.

---

## ** VAIHE 2: Tulostuksen rakennus ja Frontend Pariteetti (Display Tier)**

**Vastuualue:** Backend (Presentation) & Frontend (Flutter)  
**Tavoite:** Luoda deterministinen putki tietokannasta Flutterin ruudulle. Kaikki regex-parsinta poistetaan.

* **Task 2.1: BFF:n Puhdistus (Immutability & O(1) Manifest)**
  * **Tiedosto:** `backend_v2/services/blueprint.py`
  * **Siivous:** Poista nykyiset `scoring.py` (L866-897) ja `blueprint.py` (L481-501) -tiedostojen väliaikaiset Regex-purkkaviritykset (`<<QRM-SRC...>>` -parsinta ja `|||`-generointi) kokonaan.
  * **O(1) Snapshot -haku (Pointer-Based Manifest Normalization):**
    * Jotta `blueprint.py` pystyy palauttamaan Flutterille ihmisluettavan lähteen nimen (Display Name, esim. `Sopimus.pdf`) nopeasti O(1) aikavaativuudella, emme voi iteroida rekursiivisesti monimutkaista ja syvää `inputs`-JSON-puuta.
    * **Bloat-esto (Payload Bloat Prevention):** ÄLÄ tallenna täyttä `source_identity_manifest` -sanakirjaa suoraan `ExecutionRecord`-objektiin (koska se paisuttaisi rivikokoa eksponentiaalisesti satojen dokumenttien ajoissa).
    * **Normalisoitu Tallennus:** Tallenna manifesti normalisoituna joko erilliseen `ExecutionManifest`-tauluun (relational-tyyliin tietokannassa) tai Redis-hashmappiin, avaimena `execution_id`.
    * Renderöintivaiheessa `blueprint.py` tekee yksinkertaisen joined-haun (`O(1)`) hakeakseen manifestin ajon ID:llä: `manifest.get(source_id, "Tuntematon lähde")`. Tämä pienentää tietokantadokumentin kokoa >90%.
  * **Muuttumaton historia (Immutability):** `blueprint.py` ei saa koskaan tehdä tietokantakyselyä live-lähdetauluun renderöintihetkellä. Jos alkuperäinen tiedosto on poistettu organisaatiosta tai nimetty uudelleen, vanhan matriisiajon raportin pitää yhä näyttää tiedoston alkuperäinen nimi, joka lukittiin `source_identity_manifest`:iin ajon hetkellä.

* **Task 2.2: `synthesis.py` -yhteensopivuus**
  * **Tiedosto:** `backend_v2/hooks/synthesis.py` (L190-209)
  * Nykyinen koodi lukee `exact_quotes` raakana `list[str]` ja trunkaa merkkijonoja (`q[:300]`). Jos tyyppi muuttuu `list[QuoteEvidenceDTO]`:ksi, tämä koodi kaatuu.
  * **Muutos:** Päivitä `_strip_heavy_keys` lukemaan `QuoteEvidenceDTO`-objektien `.quote_text` -kenttää trunkkauksen aikana.

* **Task 2.3: Flutter DTO & UI Rendering**
  * Päivitä `client_app_v2/lib/features/execution/models/scorecard_dto.dart` vastaamaan uutta Pydantic-rakennetta (luo uusi `QuoteEvidenceDto` Freezed-luokka).
  * Muokkaa `atom_matrix_table_widget.dart` poistamalla merkkijonon splittaamiset (`contains('|||')`). Renderöi lähdebadge (`sourceName`) ja lainausteksti (`quoteText`) suoraan olion kentistä. Tämä poistaa kaikki lihavointivirheet ja haamulähteet.

---

## ** VAIHE 3: EU AI Act & Human Oversight (Käyttäjän yliohjaus)**

**Vastuualue:** Backend (DTO) & Frontend (Flutter)  
**Tavoite:** EU AI Actin Artikla 14 edellyttää ihmisen valvontaa (Human-in-the-Loop). Järjestelmän pitää mahdollistaa se, että loppukäyttäjä voi vastustaa tekoälyn päätöstä ja ylikirjoittaa sen matriisin rivinäytöllä.

* **Task 3.1: Immutable AI Trace (Varjostava DTO)**
  * **Datamurhan esto (Ei boolean-lippuja):** Tekoälyn tuottamia alkuperäisiä lainauksia (`exact_quotes`) tai statuksia ei saa koskaan ylikirjoittaa tai sekoittaa ihmisen dataan.
  * Luo uusi, täysin eristetty objekti ihmisen yliohjaukselle:
    ```python
    class HumanOverrideDTO(BaseModel):
        new_status: str  # Ihmisen antama uusi arvosana (esim. PASS / FAIL)
        reason: str      # Perustelu tekoälyn kumoamiselle
        evidence_quotes: list[QuoteEvidenceDTO]  # Ihmisen manuaalisesti syöttämät lainaukset
        overridden_by: str
        overridden_at: datetime
    ```
  * Lisää `ScorecardAtomDTO`-malliin kenttä: `human_override: HumanOverrideDTO | None = None`. Tämä varjostaa tekoälyn tuloksen tuhoamatta alkuperäistä Audit Trailia.

* **Task 3.2: Matriisien Rivinäyttö (Flutter)**
  * Päivitä `atom_matrix_table_widget.dart` huomioimaan ihmisen tekemä ohitus.
  * **Jos `humanOverride != null`:**
    1. Piilota/haalista tekoälyn alkuperäinen perustelu ja alkuperäiset lainaukset.
    2. Piirrä matriisiin visuaalisesti korostettu (esim. erivärinen) laatikko: **"👨‍⚖️ Ihmisen päätös (EU AI Act) / Human Override"**.
    3. Näytä laatikon sisällä ihmisen antama uusi status (`newStatus`), perustelu (`reason`) ja ihmisen omat lainaukset (`evidenceQuotes`). Tällä taataan auditoijille 100% läpinäkyvyys siihen, mitä tekoäly päätteli alun perin, ja mitä ihminen muutti.

* **Task 3.3: Käyttöliittymän Toiminnallisuus (Miten ohitus tehdään näytöltä)**
  * **Painike:** Lisää `atom_matrix_table_widget.dart` -tiedostossa kunkin matriisirivin (atomin) loppuun "Yliohjaa päätös" (Human Override) -painike (esim. `IconButton` oikeuden vasara- tai muokkauskuvakkeella).
  * **Modaali (HumanOverrideDialog):** Napin painaminen avaa dialogin, joka pakottaa käyttäjän syöttämään kolme EU AI Act -auditoinnin vaatimaa kenttää:
    1. **Uusi arvosana (New Status):** Esimerkiksi `PASS` tai `FAIL`.
    2. **Perustelu (Reason):** Kirjallinen selitys siitä, miksi tekoäly on väärässä.
    3. **Todistusaineisto (Evidence):** Käyttäjän manuaalisesti tekstistä kopioima oikea lainaus.
  * **API-kutsu:** Kun dialogi tallennetaan, Flutter lähettää backendille ohitustapahtuman (josta muodostetaan `HumanOverrideDTO`).

* **Task 3.4: Tapahtumapohjainen Uudelleenlaskenta (Event-Driven Overrides)**
  * **Asynkroninen API-palvelin:** Uusi Override-API-reitti (esim. `PATCH /api/v2/executions/{id}/atoms/{atom_id}/override`) päivittää atomin tilan (lisäämällä `human_override` -objektin) tietokantaan ja palauttaa välittömästi **HTTP 202 Accepted**. Tämä vapauttaa Flutter-käyttöliittymän heti ilman UX-latenssia.
  * **Taustatyö & Debouncing (Background Dispatch & Locking):** Jotta nopeat peräkkäiset yliohjaukset (esim. käyttäjä klikkaa 3 atomia putkeen) eivät aiheuta kilpatilannetta (Race Condition) tai korruptoi DAG-tilaa, HTTP-reititin ei käynnistä matematiikkamoottoria välittömästi. Se asettaa **Redis-debouncerin** (esim. 1,5 sekuntia). Vasta kun yliohjausten tulva loppuu, yksi ainoa taustatyö käynnistää irti kytketyn matematiikkamoottorin (`scoring_engine.recalculate()`).
  * **Reaktiivinen UI-päivitys & Optimistic Versioning (SSE):** Kun matematiikka ja PDF-generointi on suoritettu taustalla, backend lähettää Flutterille Server-Sent Event (SSE) -viestin. **Kriittistä:** Jokaiseen SSE-viestiin on liitettävä `version` tai `updated_at` aikaleima. Flutterin käyttöliittymä vertaa viestin versiota lokaaliin tilaansa. Jos se saa vanhentuneen SSE-viestin (Stale State), se hylkää sen hiljaisesti. Tämä takaa korruptoitumattoman UI-synkronoinnin.
  * *Miksi?* Synkroninen satojen atomien DAG-uudelleenlaskenta HTTP-säikeessä aiheuttaisi sietämätöntä viivettä ja API-aikakatkaisuja (Timeouts). Tapahtumapohjainen (Event-Driven) arkkitehtuuri on välttämätön Quorum V2:n skaalautuvuudelle.

---

## ** Hyväksymiskriteerit (Definition of Done)**

1. `exact_quotes` on **kaikissa neljässä LLM-skeemassa ja esityskerroksen DTO:ssa** lista `QuoteEvidenceDTO`-objekteja, ei merkkijonoja.
2. `field_prompts.py`:n `DESC_EXACT_QUOTES` ei enää ohjeista LLM:ää sisällyttämään aliaksia merkkijonoihin. LLM palauttaa rakenteelliset `{"source_id": "...", "quote_text": "..."}` -objektit.
3. Tietokantaan ei koskaan tallennu `<<QRM...>>` tai `DOC-1` tyyppisiä ajokohtaisia viitteitä, vaan ainoastaan relaatiotason Opaque Stripe ID -viitteitä (`doc_...` tai `prf_...`).
4. Alias-resoluutio tapahtuu **vain ja ainoastaan** `scoring.py`:ssä. `blueprint.py` ei tee mitään regex-parsintaa.
5. `AliasRegistry` tukee Graceful Degradation -periaatetta (tuntematon alias → `None`, ei Exception).
6. `synthesis.py` osaa lukea `QuoteEvidenceDTO`-objekteja ilman kaatumista.
7. Flutterissa `atom_matrix_table_widget.dart` ei tee enää minkäänlaista regex-splittausta stringeille, vaan rakentaa UI:n puhtaasti DTO-kentistä.
8. Python-yksikkötestit (`backend_audit_loop.py`) ja Flutterin koodigenerointi (`flutter_audit_loop.py`) menevät läpi puhtain paperein uuden tiukemman skeeman kanssa.

---

## ** Vaikutusaluekartta (Impact Map)**

| Tiedosto | Muutos | Vaihe |
|----------|--------|-------|
| `backend_v2/models/prompts/field_prompts.py` | Prompt-uudelleenkirjoitus (juurisyy!) | 1.1 |
| `backend_v2/models/` (uusi) | `QuoteEvidenceDTO` -mallin luonti | 1.2 |
| `backend_v2/models/dtos/lightweight_matrix.py` | 2x `list[str]` → `list[QuoteEvidenceDTO]` | 1.3 |
| `backend_v2/models/v2_core.py` | `BaseTDAExtraction` + `ScorecardAtomDTO` | 1.3 |
| `backend_v2/models/dtos/evaluation_steps.py` | `StepDTOStrict` | 1.3 |
| `backend_v2/services/mcp/alias_registry.py` | `resolve_graceful()` | 1.5 |
| `backend_v2/hooks/scoring.py` | Alias-resoluutio + regex-poisto | 1.4, 2.1 |
| `backend_v2/services/blueprint.py` | Regex-poisto + Snapshot-lukeminen | 2.1 |
| `backend_v2/hooks/synthesis.py` | DTO-yhteensopivuus | 2.2 |
| `client_app_v2/.../scorecard_dto.dart` | `QuoteEvidenceDto` Freezed-luokka | 2.3 |
| `client_app_v2/.../atom_matrix_table_widget.dart` | `split('|||')` -poisto | 2.3 |

---

### 1. Backend Pydantic-mallit (Domain Isolation)
Rakennetaan tiukka raja LLM-tulosten ja tietokannan välille, jotta tekoäly ei näe sille kuulumattomia kenttiä.

**1A. LLM-Rajapinta (`LLMExtractedQuote`)**
Luo malli, jota vain LLM käyttää generoinnissa.
```python
class LLMExtractedQuote(BaseModel):
    source_alias: str = Field(description="Lyhyt lähde-alias, esim. DOC-1")
    text: str = Field(description="Tarkka lainaus tekstistä")
    
    # Fail-Soft: Sallii LLM:n hallusinoimat lisäkentät kaatamatta ohjelmaa!
    model_config = ConfigDict(extra="ignore")
```
Päivitä kaikki 4 LLM-mallia (`LightweightExtractionAtom`, `AtomEvaluationItemDTO`, `BaseTDAExtraction`, `StepDTOStrict`) käyttämään:
`exact_quotes: list[LLMExtractedQuote]`

**1B. SSOT-Tietokanta ja UI-Rajapinta (Immutable AI Trace)**
Luo pysyvä malli tietokantaa ja Flutteria varten. Tekoälyn alkuperäinen data (esim. `QuoteEvidenceDTO`) säilyy aina muuttumattomana.
```python
class QuoteEvidenceDTO(V2CoreBase):
    quote_text: str
    source_id: str | None = None

class HumanOverrideDTO(BaseModel):
    new_status: str
    reason: str
    evidence_quotes: list[QuoteEvidenceDTO]
    overridden_by: str
    overridden_at: datetime
```
Lisää `ScorecardAtomDTO`:hon kenttä `human_override: HumanOverrideDTO | None = None`.

### 2. LLM Prompt & 2-Stage Translation
* **Prompt:** Uudelleenkirjoita `field_prompts.py` → LLM palauttaa structuroidun `LLMExtractedQuote`-listan, eikä enää upota aliaksia merkkijonon sisään.
* **Alias Resoluutio (`scoring.py`):** Kun LLM palauttaa tuloksen, `scoring.py` purkaa `DOC-1` → aito Opaque ID (esim. `doc_1a2b3c...`). Jos alias on tuntematon (hallusinaatio), `AliasRegistry.resolve_graceful()` palauttaa `None`. 
* **Käännös:** Luodaan `QuoteEvidenceDTO` (Opaque ID:llä ja `is_human_override=False`) ja tallennetaan se tietokantaan. LLM-mallit tuhotaan.

### 3. Presentation Tier (BFF - `blueprint.py`)
Koodin tulee ottaa tietokannasta `QuoteEvidenceDTO`-lista ja serialisoida se Frontend-yhteensopivaksi DTO:ksi rikastamalla se nimellä **Snapshotista**:

```python
# blueprint.py palauttaa Flutterille:
{
    "sourceId": quote.source_id,
    "sourceName": resolve_name_from_execution_inputs(quote.source_id), # O(1) haku snapshotista
    "quoteText": quote.quote_text
}
```

### 4. Dumb Frontend (Flutter UI)
* Päivitetään Dartin DTO (`ScorecardAtomDto` ja uusi `QuoteEvidenceDto`).
* `atom_matrix_table_widget.dart` riisutaan **kaikesta** parsintalogiikasta.
* Ei `.split("|||")`, ei `.contains()`-hakkerointia. UI vain ottaa objektin ja renderöi `sourceName` → Badge ja `quoteText` → Teksti. Yliohjauksen sattuessa piirretään "👨‍⚖️ Ihmisen päätös" -laatikko. Ehdoton determinismi saavutettu.
