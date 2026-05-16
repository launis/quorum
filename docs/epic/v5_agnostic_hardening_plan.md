# V5 Agnostic Hardening Plan (Epic)

## Tavoite
Poistaa loput 11.4 % "haamuvarianssista" TDA (Task/Data Analysis) -putkesta. Tarkoituksena on estää tekoälyä toimimasta "lakimiehenä", joka perustelee miksi irtonaiset asiat liittyvät toisiinsa. Ratkaisun täytyy olla globaali, kieli- ja formaattiriippumaton, jotta sitä voidaan soveltaa yhtä lailla suomenkielisiin Sitra-raportteihin kuin englanninkieliseen koodiin tai lakitekstiin.

## Lähestymistapa: Globaali Asenneviritys (`ai_description`)
Emme muokkaa kaikkia 185 atomia (`ai_rule_description`) yksitellen. Sen sijaan muokkaamme `seed_data.json` -tiedoston `PromptBlock` -tasoisia `ai_description` -kenttiä. Tämä injektoi sokean ja ehdottoman asenteen koko analyysiputkeen jo ylätasolla.

## Uudet Globaalit Säännöt (Injektoitavat)

Nämä kolme sääntöä lisätään jokaisen `PromptBlock`:in `ai_description`-kenttään:

1.  **ANTI-LAWYER PROTOCOL (Trace Muzzling eli Asianajaja-moodin Tukehduttaminen)**
    *   *Tarkoitus:* Estetään mallia keksimästä post-hoc-rationalisointeja. LLM:n päätöksenteko ohjautuu sen tuottamien tokenien kautta (Chain of Thought). Jos se saa generoida proosaa ja aloittaa lauseen "Vaikka...", se on jo matkalla rationalisoimaan virheen oikeaksi. Ratkaisu on kieltää vapaa teksti kokonaan `mechanical_trace`-kentässä.
    *   *Teksti injektoitavaksi:* "ANTI-LAWYER TRACE PROTOCOL: Narrative prose, justifications, and arguments are STRICTLY BANNED in mechanical_trace. Words like 'implies', 'functionally', 'suggests', or 'conceptually' used to justify a match are hallucinations. To prevent hallucination and JSON decoding errors, your trace MUST strictly follow this exact 5-step piped logging format on a SINGLE LINE, using single quotes for extracted text: '[1. RAW TEXT: '<exact text>'] | [2. ANCHOR: '<word/suffix/none>'] | [3. TARGET: '<word/none/N/A>'] | [4. BRIDGE: '<syntax/anaphora/none>'] | [5. DECISION: <Pass/Fail>]'. If the rule FAILS logically (required syntax is broken OR a forbidden NEGATIVE CONDITION is found), set exact_quote to null but always complete the trace."

2.  **STRUCTURAL TOPOLOGY & BRIDGING (Rakenteellinen Topologia ja Copula)**
    *   *Tarkoitus:* Estää mallia luomasta loogisia yhteyksiä pelkän visuaalisen läheisyyden perusteella. Sarakkeet ja rivinvaihdot rikkovat yhteyden poikkeuksia lukuun ottamatta. Esimerkiksi taulukoissa formaatin rakenteellinen jakaja ymmärretään "Topologisena Copulana" eli sidossanana (IS/HAS).
    *   *Teksti injektoitavaksi:* "STRUCTURAL TOPOLOGY & BRIDGING: Visual proximity is NOT syntax. Independent table columns (`|`) and arbitrary paragraph breaks completely sever grammatical chains. EXCEPTIONS: 1) A list preceded by a colon (:) forms a strict syntactical tree. 2) Sentences can be bridged IF AND ONLY IF connected by explicit anaphora or discourse markers (e.g., 'This implies', 'Therefore'). 3) In markdown tables or key-value structures, the structural divider (e.g., `|`) acts as an implicit relational verb (Topological Copula) explicitly binding the cells together. In all other cases, you are FORBIDDEN from inferring relationships across formatting boundaries."

3.  **GRAMMAR-BASED ANCHORING (Semantiikasta Syntaksiin)**
    *   *Tarkoitus:* Poistaa säännöistä subjektiiviset määreet ja pakottaa malli tulkitsemaan tekstiä kieliagnostisten kielioppitermien kautta, välttäen ylisovittamista tiettyihin kieliin.
    *   *Teksti injektoitavaksi:* "GRAMMAR-BASED ANCHORING: You must translate all conceptual requirements into strict grammatical markers. A syntactic anchor or bridge can be a standalone word (free morpheme) OR a bound morpheme, affix, or clitic depending on the target language syntax. Do NOT evaluate meaning, tone, or intent. You must evaluate only the physical presence or absence of explicit grammatical syntax or morphology."

4.  **BACKEND LEXICAL VERIFIER (Mekaaninen TDA-Tarkistus)**
    *   *Tarkoitus:* Vaikka yllä olevat säännöt pakottavat LLM:n toimimaan mekaanisesti, stokastinen "Musta laatikko" voi silti hallusinoida otteen, joka täyttää Pydantic-skeeman (`str`), mutta ei fyysisesti esiinny lähdedokumentissa.
    *   *Konsepti:* Lisätään backend-tasolle (`hooks` tai Pydantic-validaattori) mekaaninen Python-tason tarkistus: `if exact_quote not in source_text`. Jos ote ei täsmää leksikaalisesti, osuma hylätään lennosta ja merkitään hallusinaatioksi. (Tämän käyttöönoton laajuus tutkitaan myöhemmin).

5.  **THE ABSOLUTE BLINDFOLD (Skaalojen Pimennys & Ordinal-to-Interval Korjaus)**
    *   *Tarkoitus:* LLM kärsii "Ordinal-to-Interval" -harhasta (Context Drift) ja arvioinnin regressiosta, jos sille syötetään matriisin pisteytysasteikko (1-5) ja sen semanttiset kuvaukset. Se yrittää takaisinmallintaa (reverse-engineer) osumansa tukemaan valitsemaansa arvosanaa.
    *   *Konsepti:* Varmistetaan `PromptCompiler` -tasolla, ettei LLM näe lainkaan arvioitavan matriisin skaaloja tai otsikoita. Sille syötetään ainoastaan irrallisia TDA-atomeita. LLM tuottaa pelkkää dataa, ja Python-tason `Tripartite Calculation Boundary` laskee lopullisen arvosanan matematiikalla.

## Turvallinen Askel-Askeleelta Toteutussuunnitelma (Stepped Rollout)

**Pikasuoritusohje (Kriittinen järjestys):**
1. `python scratch\v5_mass_refactor.py` (Päivittää `seed_data.json` -tiedoston)
2. `python backend_v2\seed\run_seed.py local` (Vie muutokset lokaaliin kantaan)

Koska olemme tekemässä massiivisia asenne- ja sääntömuutoksia (`seed_data.json`), etenemme yhden loogisen kokonaisuuden kerrallaan ja varmistamme peruutettavuuden ilman git-haarautumista (käyttäen manuaalisia tiedostokopioita).

- [x] **Vaihe 1: Datan Mutatoiminen ja JSON-eheyden Varmistus**
    *   *Toiminto:* Ajetaan refaktorointi, joka muokkaa `backend_v2/seed/seed_data.json` -tiedostoa. Skripti tekee automaattisesti kopion nimellä `seed_data_pre_v5.json`.
    *   *Arkkitehtuurisäännöt:* Livenä pyörivän tietokannan suora muokkaaminen on ankarasti kielletty. Kaikki rakenteelliset datamuutokset on tehtävä master-lähdetiedostoon (`seed_data.json`). Apuskriptin (`v5_mass_refactor.py`) täytyy käyttää yksinomaan `json.load()` ja `json.dump(..., indent=2)` -metodeja tiedoston eheyden säilyttämiseksi. Uusien ID-arvojen on ehdottomasti noudatettava Opaque Stripe ID -mallia (esim. `blk_xxx`), semanttisia merkkijonoja ei sallita.
    *   *Komento:* `python scratch\v5_mass_refactor.py`
    *   *Peruutussuunnitelma (Rollback):* Jos JSON näyttää korruptoituneelta, peruuta muutokset komennolla: 
        `Copy-Item backend_v2\seed\seed_data_pre_v5.json backend_v2\seed\seed_data.json -Force`

- [x] **Vaihe 2: Tietokannan Seeding ja Arkkitehtuuriauditointi**
    *   *Toiminto:* Tuodaan säännöt lokaaliin tietokantaan ja varmistetaan, etteivät uudet Pydantic-säännöt kaada olemassa olevaa arkkitehtuuria. Varmuuskopioidaan kanta ensin.
    *   *Arkkitehtuurisäännöt:* Järjestelmä ei saa sisältää "duct-tape" fallback-purkkakoodia tai tyhjiä `dict`-palautuksia dataongelmien peittämiseksi. Pydantic V2 (`extra='forbid'`, `strict=True`) validoi tiedot armotta (Fail-Fast). Backendin varmennuksissa on aina käytettävä yhtenäistä `backend_audit_loop.py` -skriptiä pelkkien raakojen pytest-ajojen sijaan. Virheiden ilmetessä on ratkaistava juurisyy kiertämisen sijaan.
    *   *Komennot:*
        1. `Copy-Item data\db_v2.json data\db_v2_v4_backup.json`
        2. `python backend_v2\seed\run_seed.py local`
        3. `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_seed_architectural_guardrails.py --test`
    *   *Peruutussuunnitelma (Rollback):* Jos testit kaatuvat (Pydantic ei hyväksy uusia sääntöjä), palauta vanha kanta komennolla: `Copy-Item data\db_v2_v4_backup.json data\db_v2.json -Force` (ja suorita lisäksi Vaiheen 1 peruutus).

- [x] **Vaihe 3: Tuotantoajo ja Varianssin Diffaus**
    *   *Toiminto:* Ajetaan TDA-putki uutta konfiguraatiota vastaan (esim. Sitra-aineisto).
    *   *Arkkitehtuurisäännöt:* Raskaat LLM-operaatiot eivät saa tukkia FastAPI:n pääsäiettä, vaan ne on ohjattava Arq-jonoon. Yhteyden aikakatkaisujen estämiseksi on käytettävä SSE-Heartbeatia pitkissä prosesseissa. Virhetilanteissa lokitetaan vain järjestelmän viite-ID (esim. `req_abc123`) ja poikkeuksen tyyppi. Asiakasdataa (PII) tai raakoja kehotteita ei saa koskaan kirjata lokiin.
    *   *Varmennus:* Ajetaan diffaus (`scratch\diff_executions.py`) vertailemaan uutta ajoa vanhaan. Tavoitteena on nähdä haamuvarianssin putoaminen 0 %:iin.
    *   *Peruutussuunnitelma (Rollback):* Jos TDA-tulokset hajoavat täysin, suorita Vaiheen 2 ja Vaiheen 1 rollbackit peruuttaaksesi koko Epicin.

- [x] **Vaihe 4: PromptCompiler Eristys (The Absolute Blindfold)**
    *   *Toiminto:* Vasta kun Vaihe 3 on todettu voittavaksi, siirrytään eristämään arviointiasteikko itse tekoälyltä (`backend_v2/services/orchestrator/prompt_compiler.py`).
    *   *Arkkitehtuurisäännöt:* **Prompt Compiler on jäädytetty arkkitehtuurin kulmakivi.** Sitä ei saa oletusarvoisesti muokata. Kaikkiin muutoksiin `prompt_compiler.py`-tiedostossa on pakollista kysyä käyttäjältä erikseen lupa (USER CONFIRMATION) ja liputtaa muutos selkeästi ennen toteutusta. Kaikkien tekoälylle syötettyjen dynaamisten parametrien tulee olla suljettuna nimenomaisiin XML-tageihin (kuten `<execution_parameters>`) ja järjestelmäohjeiden tulee olla pelkästään englanniksi.
    *   *Peruutussuunnitelma (Rollback):* Palauta `prompt_compiler.py` aiempaan tilaansa.

- [x] **Vaihe 5: Backend Lexical Verifier (Mekaaninen TDA)**
    *   *Toiminto:* Kytketään backend-tason fyysinen tarkistus (`AnchorValidationService`), joka hylkää LLM:n palauttaman osuman välittömästi, jos sitä ei löydy normalisoidusta lähdetekstistä.
    *   *Arkkitehtuurisäännöt:* Universal Fail-Fast -vaatimus. Dataa ei saa koskaan niellä hiljaisesti tyhjillä `try...except` -lohkoilla. Jos leksikaalinen vertailu epäonnistuu, prosessin tulee pysähtyä, virhe tulee lokittaa natiivisti `logger.error`:lla ja palauttaa eksplisiittisenä `AppException`-virheenä RFC 7807 -muodossa. Leksikaalinen vertailija ei saa käyttää naiivia purkkakoodia.
