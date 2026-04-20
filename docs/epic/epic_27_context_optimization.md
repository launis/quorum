# Epic 27: LLM Kontekstin Optimointi ja Tarkkuuden Maksimointi (Map-Reduce)

## 1. Tausta ja Tavoite
Backendin asynkroninen Chunking Service (Epic 23) jakaa valtavat matriisit useisiin kymmeniin osa-atomeihin ja pyytää mallia (Vertex AI / Gemini) arvioimaan ne. Vaikka raskaat `reasoning` ja `quote` kentät on jo ohjelmoitu siivottavaksi pois vanhoista askelista (`_strip_heavy_keys`), yksittäisen palasen (Chunk) LLM-kysely on kooltaan yhä giganttinen (esim. > 44 000 merkkiä). Tämä johtaa hitaisiin vasteaikoihin (1 - 1.5 min per kutsu), kasvaneisiin ajokustannuksiin ja altistaa rajapinnan 'Edge-Case 429 Payload exhaustion' -yhteysvirheille.

Tämän Epicin tavoitteena on toteuttaa häviötön (lossless) strateginen LLM-kontekstin optimointi. Tavoitteena on saavuttaa merkittävä Payload-koon minimointi, ja samalla **maksimoida** järjestelmän tarkkuus (Fidelity) purkamalla massiivisia tiedostosyötteitä siten, ettei yhdenkään Synthesis- tai raportointi-askeleen informaation eheys kärsi.

## 2. Toimenpiteet ja Ratkaisut

Vältämme tarkoituksella kaikkia menetelmiä, jotka asettavat synteesi-askeleet sokeiksi vanhalle tiedolle (esimerkiksi metadata-tagien täydellinen tyhjennys tai luontaisten nyanssien kadottaminen automaattisella tiivistämisellä/summarisaatiolla). Keskitämme optimoinnin kolmeen täsmävaiheeseen, jotka hyödyntävät suoraan toistensa synergioita:

### Vaihe 1: Tiukka Syötesuodatus (Strict Variable Isolation / Input Pruning)
**Toteutus:** 
Päivitetään `backend_v2.services.orchestrator.strategies.llm.compiler.build_xml_context` -metodia. Tällä hetkellä se injektoi LLM-kyselyn `<inputs>` -lohkoon koko DAG-tilan kaikkine asiakirjoineen (esim. koko 20 000 sanan `product_text` syötteen riippumatta askeleesta). Uudessa ratkaisussa metodi suodattaa säälimättömästi pois **kaikki ne muuttujat, joita ei ole eksplisiittisesti määritelty ko. askelelle** työnkulun `step.input_mappings` listassa.

**Tarkka analyysi vaikutuksista:**
*   **Vaikutus tarkkuuteen (Fidelity Boost - Nostava):** Tämä optimointi on puhtaasti posiitivinen ja se korottaa ajon tarkkuutta ehkäisemällä "hallusinaatioiden ristiinkontaminaatiota". Jos Askel B on tarkoitettu ratkomaan asioita vain Askeleen A tulosten pohjalta, muiden massiivisten lähtödokumenttien piilottaminen ohjaa kielimallin nojautumaan faktuaaliseen aiempaan tulokseen, vähentäen hämmentäviä tekstileikkauksia ja vahvistamalla keskittymistä.
*   **Vaikutus resursseihin (Säästö: Vahva):** Odotettavissa tuntuva jopa kymmenien tuhansien merkkien (-40 % – -60 %) purku niissä askeleissa, joiden vaaditaan syövän vain binääristä tulosdataa isojen raakatekstien perkaamisen sijaan.

### Vaihe 2: Kriteeristön Mikro-ohjaus (Dynamic Chunk Rubrics / Surgical Rubrics)
**Toteutus:** 
Muutetaan eristetyn `ChunkingService` -luokan logiikkaa siten, että jakaessaan 195 atomin matriisin matalamman koon paloihin, kyselypalvelu ei esitä Vertex AI:n kokoavana "ohjekirjana" koko matriisin sataa otsikkoa. Logiikka kerää `<EVALUATION_RUBRICS>` tagiin kevennetyn dynaamisen mini-matriisin, joka asettaa arvioitavaksi **ainoastaan kunkin palan sisältämien täsmäatomien valikoidut kriteerit (PromptBlocks)**.

**Tarkka analyysi vaikutuksista:**
*   **Vaikutus tarkkuuteen (Fidelity Boost - Nostava / Vakauttava):** Koska tekoälyn ei tarvitse kognitiivisessa avaruudessaan punnita vastaustensa osuvuutta koko valtavaa satapäistä listastoa vasten, huomiokerroin ("Attention Capacity") lepää vain absoluuttisesti relevantilla alueella. "Lost-in-the-middle" ilmiö hälvenee oleellisesti ja samalla minimoidaan LLM:n harhautuminen irrallisista tai ohipuhuvista kriteereistä muilla atomeilla.
*   **Vaikutus resursseihin (Säästö: Tuntuva):** Vähentää system promptin staattisen kehotteen ohjetekstitaakkaa välittömästi kymmenillä kilotavuilla optimoiden suoraan Token-kulutuksen hyötysuhteen.

### Vaihe 3: SystemConcurrency Päivitys ja Rinnakkaisajon Synteesi (The Payoff)
**Toteutus:** 
Syy varovaiselle nopeuskuristuksille on alkuperäinen giganttinen ja hidas (> 44k merkin) konteksti. Kun Vaiheet 1 ja 2 nipistävät ohjekirjojen tarkan koon tehokkaaseen minimiin samalla nostaen ajotarkkuutta huomattavasti, pystymme kääntämään uuden tehokkuuden nopeushyödyksi purkamalla API:n tuomat kuristuskahleet. 

Päivitetään luokka `SystemConcurrency` tiedostossa `backend_v2.models.enums.py` vakaaseen tehotiukkaan muotoon:

```python
class SystemConcurrency(int, Enum):
    MAX_CONCURRENT_WORKFLOWS = 1
    MAX_CONCURRENT_LLM_STEPS = 3       # Nostetaan rinnakkaisuutta asettamatta paineita (1 -> 3)
    LLM_MAX_RETRIES = 3
    LLM_MAX_CHUNK_SIZE = 40            # Kasvatetaan käsiteltävää atomialliikettä (15 -> 40)
    MATRIX_SAMPLING_LIMIT = 0
    LLM_DEFAULT_TIMEOUT_SECONDS = 300
    RATE_LIMIT_COOLDOWN_SECONDS = 65
```

**Tarkka analyysi vaikutuksista ja synergiasta:**
*   **Massiivinen Aikahyöty (Speedup):** Aiemmassa mallissa yli 200 atomin matriisi jouduttiin ajamaan 13 irrallisena palana (Chunk size 15). Sarjallinen läpikäynti vaatii isoa Vertex odottelua, tuhoten liki **~20 minuuttia** prosessointiaikaa. Uudella ratkaisulla täysi laajuus ladataan malliin **vain 5:llä ohjatulla palalla** (Chunk 40). Koska ammumme rinnakkain jopa 3 palaa kerrallaan asynkronisesta makasiinista (`MAX_CONCURRENT_LLM_STEPS = 3`), työjonon odotusaika kutistuu **arviolta n. 1 minuuttiin / palautukseen**. Suorituskykyloikka edustaa 20-kertaista parannusta loppukäyttäjälle.
*   **Askeleen Laajuus (Tarkkuuden kestävyys isommalle koolle):** Ilman Vaihetta 2 suurempi palamassa olisi riski, koska isolle datakuormalle (40) pakotettaisiin sokea epäsuhtainen vastaus 200:aan irralliseen kriteeriin ja ohjearvosanaan, heikentäen Attention -painotusta kohti vääriä tulkintoja. Koska injektoimme täsmälliset 40 kriteria kunkin 40-paketin pohjapiirrokseen ennakkoon (Vaihe 2), säilytämme maksimaalisen Pydantic / Failsafe Zero-Math tarkkuuden isoa laajuutta vastaan.
*   **Täydellinen Osuma API-kattoihin (Rate-Limit Survival):** Suurimpana etuna on vakauden hallinta (FinOps). Lokidata osoitti Vertex AI:n rajoittavan ohjatussa mallissaan kyselymäärät kattoon `rpm: 5` (Requests Per Minute = 5). Rajoittamalla Chunkin suuruuden tasan 40:een ja ajamalla 3 askelta samanaikaisesti asynkronisessa makasiinissa, kevennetyt, massiivisesti lyhennetyt XML Promptit pystyvät palaamaan turvallisesti juuri osumalla 5 pyynnön alle viiden sekunnin haamurajoissa — tuottaen täydellisen selviytymisen ilman massiivisia `429 RateLimitError` seiniä tai hidastavia re-try lenkkejä. Valittu numerokonfiguraatio on siis matemaattisesti optimaalinen kompromissi turvallisuuden ja työntekijän UX-ajansäästön välillä.

### Vaihe 4: Matriisikohtaisten laajennusten (Output Extensions) kiristäminen
**Toteutus:**
Karsimme nykyisestä `seed_data.json` tiedostosta massiivisen ja kaikkia matriiseja koskevan 10-kohtaisen `output_extensions` -listan (joka pitää sisällään *citation, falsification, missing_context, risk_flag, coaching, justification, theory_link, remediation_steps, emotional_sentiment, confidence*). 

Kaikki matriisit eivät tarvitse näitä kaikkia tuloskartoituksia. Jokaiselle matriisille räätälöidään vain sen oman "roolin" tai tavoitteen mukaiset välttämättömät laajennukset.

**Ehdotus matriisikohtaisiksi laajennuksiksi:**

1. **`matrix_kahneman` (System 1/2, Cognitive Friction)**
   * **Tarvitaan:** `justification`, `falsification`, `confidence`
   * **Perustelu:** Kognitiivisen tason arviointi vaatii perustelut ("miksi tämä on System 1"), falsifioinnin (itsestäänselvyyden murtaminen) ja varmuustason, mutta ei emotionaalista arviota tai korjaavia askelia tässä vaiheessa.

2. **`matrix_goodhart` (Performativiteetti & Driving)**
   * **Tarvitaan:** `justification`, `risk_flag`, `theory_link`
   * **Perustelu:** Goodhartin lain mittaus vaatii havaitun riskin liputtamisen, teoreettisen linkin (miten ohjaus epäonnistui) sekä loogisen perustelun sille, miten käyttäjä ohitettiin performatiivisena.

3. **`matrix_archivist` (Arkistointistandardit, Eeppinen linjaus)**
   * **Tarvitaan:** `justification`, `citation`, `missing_context`
   * **Perustelu:** Arkiston valvoja mittaa ankkurointia faktoihin ja menneisyyteen, joten tarkat lainaukset ja puuttuvan kontekstin osoittaminen ovat kausaalisesti tärkeimmät.

4. **`matrix_causal_analyst` (Kausaalisuuden Analyysi)**
   * **Tarvitaan:** `justification`, `falsification`, `remediation_steps`
   * **Perustelu:** Kun syy-seuraus -ongelmia puretaan (Post Hoc Ergo Propter Hoc), on tärkeää tarjota välittömät askeleet (remediation) sen korjaamiseksi.

5. **`matrix_falsifier` (Armoton Falsifioija)**
   * **Tarvitaan:** `justification`, `falsification`, `theory_link`
   * **Perustelu:** Keskittyy täysin väitteiden murtamiseen, joten laajennettu falsifiointi ja sen teoreettinen ankkurointi ovat avainasemassa.

6. **`matrix_judge` (Ylituomari)**
   * **Tarvitaan:** `justification`, `risk_flag`, `confidence`
   * **Perustelu:** Ylituomarin lopputuomio ei tarvitse koodivalmennusta (coaching) tai empatiaa (emotional_sentiment). Ainoastaan perustelun oikeudelle, varmuustason ja mahdolliset laajemmat järjestelmätason riskit.

7. **`matrix_xai_reporter` (XAI-Raportoija)**
   * **Tarvitaan:** `justification`, `missing_context`, `confidence`
   * **Perustelu:** Kokonaisraportissa on olennaista viestiä loppukäyttäjälle, mihin havaintojen varmuus perustuu ja mitä tietoavaruudesta vielä puuttuu oheisohjauksen lisäksi.

**Analyysi vaikutuksista:**
*   **Vaikutus tarkkuuteen (Fidelity Boost - Nostava):** Estää tekoälyn "hallusinaatiot" ja "liika-avuliaisuuden" sellaisissa osa-alueissa (esim. emotionaalinen arvio), jotka eivät liity suoraan kyseisen agentin tuomitsemistehtävään. Rooli kirkastuu.
*   **Vaikutus resursseihin (Payload säästö - Tuntuva):** Poistamalla jopa 7 ylimääräistä ohjetta (arviointikriteeriä ja json-avainta) per jokainen matriisi, poistamme jälleen tuhansia merkkejä turhaa System Prompt -painolastia, mikä palvelee suoraan Epic 27:n konteksti-ikkunan optimointitavoitetta.

### Vaihe 5: Telemetria ja Mitattavuus (Acceptance Criteria)
**Toteutus:**
Jotta optimoinnin väitetyt säästöt (esim. 40-60% payload-leikkaus ja 20-kertainen suorituskykypomppu) voidaan todentaa tuotanto-olosuhteissa häviöttömiksi (lossless), järjestelmään on aktivoitava selkeä LLM-telemetrian mittapiste.

Askeleiden `worker_job_timeout` vakaus ja LLM-rajapinnan ohjaus nojaavat suoraan näihin lukuihin. Oletukset "edge case payload exhaustions"-virheistä eivät riitä korjausten todistamiseen.

**Hyväksymiskriteerit (Acceptance Criteria):**
1.  **Token-laskenta lokitetaan:** `LLMProvider` tai `LiteLLM Router` -tasolla tallennetaan järjestelmän lokiin tarkat Vertex API:sta palautuvat `prompt_tokens` ja `completion_tokens` jokaiselta yksittäiseltä chunk-kutsulta. Tämän on numeerisesti todennettava, että kymmenien tuhansien sanojen toisto Payloadista katoaa verrattuna aiempaan 846kt lähtötilanteeseen per kutsu.
2.  **API-Latenssin seuranta:** Jokaisen yksittäisen Map-Reduce -kutsun API-viive Vertex AI:ssä kirjataan lokiin ja liitetään `ExecutionTrace`-telemetriaan. Vaiheen 3 rinnakkaissuorituksen on osoitettava, että koko 195 atomin matriisin käsittelyaika putoaa toistuvasti alle viiteen minuuttiin aiemmasta yli 4 tunnin jumiutumisesta.
3.  **Verrannollinen laadunvarmistus (Fidelity):** Arvioinnin numeerinen varianssi ei saa kärsiä syötteiden eristämisestä. `hit_rate` osuuksien tulkinnassa ja askeleiden generoiduissa perusteluissa (justifications) tulee näkyä puhdasta faktakeskeisyyttä ilman ristiinkontaminaatiota, mikä voidaan todistaa suoraan Flutter-käyttöliittymän Diagnostic Scorecardin tai tallennettujen raporttien pohjalta.

### Vaihe 6: Testistrategia (A/B Shadow Mode)
**Toteutus:**
Koska termi "häviötön" (lossless) on erittäin vahva väite, on olemassa ohjelmistotekninen riski, että kun LLM:ltä viedään satoja tuhansia merkkejä ympäröivää kontekstia (Vaihe 1) ja jopa 80 % kriteeristöstä peitetään (Vaihe 2), malli menettää kykynsä lukea ns. "rivien välistä". Jotta voimme luottaa Epic 27:n tuloksiin tuotannossa, toteutamme tiukan A/B-vertailevan regressiotestin.

**Vaatimukset testaukselle:**
1. **Varjoajo (Shadow Mode / A/B Testi):** Valitaan yksi vakioitu, massiivinen datasetti (esim. 195 atomin Goodhart-matriisi ja laaja yli 100 sivun dokumentti). Ajo suoritetaan kahdesti:
   - **Putki A (Legacy):** Massiivinen "raaka" putki ilman Epic 27 -rajauksia, jossa koko DAG-historia ja kaikki matriisisäännöt näytetään kaikille chunkeille (joka synnyttää nykyisen 4 tunnin latenssin ja 846kt payloadit).
   - **Putki B (Optimoitu):** Uusi, aggressiivisesti rajattu Epic 27 -putki (Phase 1-4).
2. **Validointiskripti:** Kehitetään Python-validaattori (tai suoritetaan manuaalinen Audit-ajo), joka vertaa Putki A:n ja Putki B:n saamia tuotoksia (`db_v2.json` / `ExecutionHistory`).
3. **Laadun Todentaminen:** Skriptin/auditin tulee osoittaa, että uusi järjestelmä löytää vähintään saman määrän loogisesti paikkansapitäviä osumia (`TRUE` -evaluaatiot kriittisille kriteereille) ja että tuotetun JSON-datan perustelut (justifications) ovat loogiselta eheydeltään ja faktuaalisuudeltaan vähintään yhtä hyviä, mieluiten jopa terävämpiä ohjatun fokuksen myötä. Systemaattinen "silmien ummistaminen" tai huti-osumien (False Negatives) massiivinen lisääntyminen katsotaan Epicin epäonnistumiseksi.
