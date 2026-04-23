# Epic 35: Dynamic UI Routing and Targeted Matrix Pruning

## Goal
Palauttaa järjestelmä aitoon "UI on diktaattori" (Code is the Truth) -arkkitehtuuriin noudattaen ehdotonta Zero-Compromise Fail-Fast -protokollaa. Poistaa taustajärjestelmän (backend) kovakoodatut input-pakotukset ja muuttaa tokenien säästöön tarkoitettu karsinta (pruning) kohdennetuksi niin, että matriiseista säilytetään ainoastaan BARS-solmukohtaiset True/False-osumat sekä kokonaisarviointi (kuten `lue_tulokset.py` määrittelee), mutta muihin data-avaimiin ei kajota.

## 1. Tiedostojen Injektoinnin Poistaminen (Explicit Input Routing)
### Ongelma
Tällä hetkellä `backend_v2/services/orchestrator/strategies/llm.py` pakottaa kaikki työnkulkuun määritellyt `expected_inputs` (kuten alkuperäiset PDF/tekstitiedostot) automaattisesti jokaisen LLM-stepin kontekstiin. Käyttöliittymän (UI) `input_mappings`-asetus ohitetaan täysin näiden osalta. Tämä rikkoo säännön `ui_driven_synthesis_boundary`, aiheuttaa massiivisia 1.04M tokenien ylityksiä (Token Explosions) ja piilottaa datan kulkua.

### Ratkaisu
*   Poistetaan `llm.py` -tiedostosta `expected_inputs`-dokumenttien automaattinen injektio.
*   Jatkossa tekoäly (LLM) saa alkuperäiset tiedostot *vain*, jos käyttöliittymästä on tehty niille eksplisiittinen mäppäys (esim. `Lähdemateriaali -> $inputs.laakarikirjaus`).
*   **Huomio `input_processing.py` -yhteensopivuudesta (Strict In-Memory Resolution):** Kun data mäpätään `$inputs`-polusta, sen on **ehdottomasti** tultava valmiiksi prosessoidusta `state.inputs` -välimuistista. `input_processing.py` -hook on työnkulun alussa jo hoitanut `ai_description` -ohjeiden injektoinnin, chat-historian jäsentelyn ja kyselylomakkeiden Markdown-muotoilun. `ContextRouter` ei saa missään tilanteessa yrittää lukea alkuperäisiä tiedostoja levyltä (tai blobeista) uudelleen, eikä käynnistää uutta AI/Markdown-prosessointia synteesihetkellä. UI:n kutsuma polku palauttaa puhtaasti sen stringin, joka muistissa jo lepää.
*   Tiedostojen nimien ja sisältöjen on oltava täysin dynaamisia; järjestelmä ei saa olettaa tiettyjen nimettyjen dokumenttien (kuten "lopputuote" tai "keskusteluhistoria") olemassaoloa.

## 2. Globaalin `$steps` Ohituksen Purkaminen (Namespace Resolution)
### Ongelma
Jos käyttöliittymästä yrittää viitata globaalisti edellisiin tuloksiin käyttämällä polkua `$steps`, `llm.py` ohittaa tämän täysin (`if path in ("steps", "$steps"): continue`). Tämän vuoksi UI:sta ei tällä hetkellä voi määrätä tekoälylle laajoja tuloskonteksteja ilman, että ne pitää mäpätä yksi kerrallaan.

### Ratkaisu
*   Poistetaan `continue`-ohitus.
*   Mahdollistetaan `PromptCompiler`:lle kyetä hakemaan dataa suoraan UI:n määrittämistä poluista. Jos UI pyytää `$steps`, tekoäly saa kaiken, mitä karsinnan jäljiltä on jäljellä. Jos UI pyytää `$steps.step_1.outputs.evaluations`, tekoäly saa tarkalleen sen.

## 3. UI Syötekartoitusten (Input Mappings) Täydellinen Määräysvalta
Tämän Epicin suorittamisen jälkeen käyttöliittymän "Syötekartoitukset (Tilan injektointi)" -alasvetovalikon valinnat ovat 100% absoluuttinen totuus (Code is the Truth). Piilotettu backend-magia poistuu ja seuraavat UI-käskyt toimivat täsmälleen siten kuin käyttäjä ne määrittelee:

*   **Kaikki alkuperäiset syötteet yhdistettynä (`$inputs`)**: AI saa *kaikki* työnkululle ladatut ja generoidut alkuperäiset tiedostot valmiiksi prosessoidussa muodossa (hakenut suoraan `state.inputs` -tilarakenteesta). **Tärkeää:** Jos tätä ei valita, backend EI enää injektoi tiedostoja väkisin taustalla!
*   **Syöte: [Tietty tiedosto] (esim. `$inputs.product_text`)**: AI saa täsmälleen tämän yksittäisen syötteen suoraan prosessoidusta välimuistista (In-Memory), ei levyltä.
*   **[Tietty aiempi steppi] (esim. Faktantarkistaja eli `$steps.sr_xyz.outputs`)**: AI saa täsmälleen kyseisen yksittäisen vaiheen tulosdatan sellaisenaan.

Käyttöliittymä (UI) on tästä eteenpäin diktaattori: mitä ei UI:ssa mäpätä, sitä ei LLM-kontekstiin siirretä.

## 4. Kohdennettu Pruning ja Feature Sovereignty (UI-Driven Pruning)
### Ongelma
Token-säästöön tarkoitettu funktio `_strip_heavy_keys()` tuhoaa raa'asti ja sokeasti kaiken tekstin (esim. lainaukset ja kognitiiviset perustelut) koko kontekstin laajuudelta muokkaamalla sanakirjaa (`dict`) lennosta. Se tuhoaa vahingossa myös muiden steppien raportointidataa.
**Kriittinen löydös (Feature Sovereignty):** Jos karsimme matriiseista sokeasti "vain True/False" -tiedot, rikomme tulostusprofiilien (`OutputProfile`) määräysvaltaa! Käyttäjä voi UI:ssa (esim. `prf_5d6e7f8091a2b3c4`) ruksia näkyviin XAI-laajennoksia kuten `falsification`, `coaching` tai `remediationSteps`. Jos pudotamme nämä perustelut token-säästön nimissä, syntetisoiva tekoäly ei koskaan näe niitä eikä voi kirjoittaa niitä lopulliseen raporttiin.

### Ratkaisu: Decoupled Architecture (Täydellinen Irrotus)
Matriisiajo (tiedon generointi) ja Output Profile (tiedon esittäminen) on erotettava toisistaan täysin. Käyttäjän on voitava ajaa matriisi kerran, ja sen jälkeen generoida kymmeniä erilaisia loppuraportteja eri profiileilla ilman, että raskaita analyysejä ajetaan uudelleen.

#### Tietokannat ja API-rajapinnat (Nykytila)
*   **Tietokantamallit:** Raakadata (100% matriisiajo) lepää TinyDB/Firestore-kannassa `ExecutionRecord.execution_trace` -listassa (Event Sourcing). Lopullinen synteesi tallennetaan samaan tietueeseen välimuistiin: `ExecutionRecord.profile_syntheses[profile_id].synthesized_markdown`.
*   **Rajapinta (API):** Synteesi ei tapahdu matriisiajon aikana, vaan se on "On-Demand Rendering" -prosessi. Se käynnistyy, kun UI kutsuu rajapintaa `GET /api/v2/executions/{execution_id}/render?profile_id=XXX`. Jos käyttäjä haluaa ajaa synteesin uudelleen eri asetuksilla, UI kutsuu ensin välimuistin tyhjennystä `DELETE /api/v2/executions/{execution_id}/profiles/{profile_id}` ja lataa raportin uudelleen.

#### DTO-roolit ja Tiedonsiirto (Data Contracts)
Data kulkee kerrosten välillä tiukkojen Pydantic-mallien läpi noudattaen Zero-Compromise -periaatetta:
1.  **Raakadata DTO (Vaihe 1):** Matriisien tuottama massiivinen data on kääritty `TraceEvent` -objekteihin. Tämä on "raskas tila", joka on tarkoitettu vain tietokantaan, ei LLM:n kontekstiin.
2.  **Kevyttila DTO (Vaihe 2):** Uusi luotava `LightweightMatrixOutput` DTO. Tämä on `ContextRouter`in rakentama karsittu projektio ("Cognitive Radar Map"), joka toimii suojamuurina. Se sallii LLM-kontekstiin vain puhtaat booleaanit, `justification`-kentät ja UI:n sallimat XAI-laajennokset.
3.  **SDUI DTO (Vaihe 3):** Synteesi-LLM pakotetaan vastaamaan tarkalla SDUI (Server-Driven UI) -arraylla (esim. `HeroInsightBlock`), ei Markdownilla. Tämä DTO validoidaan taustalla, ja vasta onnistumisen jälkeen teksti muunnetaan Flutterille valmiiksi `synthesized_markdown` -tiedostoksi.
4.  **UI DTO (Käyttöliittymä):** Lopulta kaikki data lähetetään Flutterille `ReportDataDTO` -objektissa, missä yksittäiset matriisitulokset (ja pelastetut `justification`-kentät) asuvat `ReportAxisDTO` -malleina.

*   **Phase 1: 100% Data Capture / Matriisiajo (NYKYTILA - TOIMII JO):** Kun työnkulun matriisi (esim. `matrix_toulmin`) suoritetaan, tekoäly tuottaa **kaikki** `seed_data.json` -tiedostossa kyseiselle matriisille määritellyt `output_extensions` -laajennokset (esim. `falsification`, `coaching`). Mitään ei karsita tässä vaiheessa. Tietokantaan (Execution State) tallennetaan aina 100% täydellinen tulos. Tähän EI tarvitse tehdä muutoksia.
*   **Phase 2: Late-Binding Pruning / Synteesivaihe (UUSI KEHITYS - RAKENNETTAVA):** Karsinta (`Pruning`) tapahtuu uudessa `ContextRouter`:ssa *vasta silloin*, kun käyttäjä tai UI pyytää lopullista raporttia tietyllä Output Profilella. Vanha, sokea `_strip_heavy_keys()` poistetaan kokonaan.
*   **UI-Driven Matrix Pruning & `output_config` -integraatio:** 
    *   **Kriittinen REST-sääntö ja Tietoturva:** Kun UI laukaisee synteesin (Post-Execution Synthesis), se lähettää `GET`-pyynnön query-parametrina *ainoastaan* `profile_id` -tiedon (esim. `?profile_id=prf_123`). UI EI SAA lähettää itse `output_config` -objektia pyynnön bodyssä. Tämä on välttämätöntä kahdesta syystä: 1) `GET`-pyynnöissä ei saa olla JSON-bodya (muuttaminen `POST`-pyynnöksi tuhoaisi Flutterin Stale-While-Revalidate -välimuistipollauksen), ja 2) Client-side injection -hyökkäysten estäminen (käyttäjä ei voi manipuloida taustajärjestelmän karsintasääntöjä).
    *   `ContextRouter` on puhdas orkestraattoritason logiikkakomponentti (SRP). Se **ei** tee tietokantakyselyitä itse. Service-kerros (`ExecutionService`) lukee `profile_id`:n perusteella oikean `OutputProfile` -määrityksen turvallisesti tietokannasta/seedistä. Sen jälkeen `ExecutionService` injektoi `output_config` -määrityksen `ContextRouter`ille täysin palvelimen sisäisenä in-memory operaationa yhdessä matriisien 100% raakadatan kanssa. Router suorittaa projektion ja leikkaa datan profiilin sääntöjen mukaisesti.
*   **Välivaiheiden reititys (Intermediate Routing - Kriittinen Suojamuuri):** Jos käyttöliittymä mäppää synteesin sijasta työnkulun välivaiheen (esim. Steppi A -> Steppi B viittaamalla polkuun `$steps.step_A`), UI:n tai työnkulun määrityksen on pakko välittää `routing_mode` (esim. `strict_booleans_only` tai `full_xai`). Epic 35 määrää ehdottoman **Fail-Fast** -säännön (Code is Truth = You explicitly map it, or it crashes): Jos välivaiheen mäppäyksellä ei ole eksplisiittistä karsintasääntöä, `ContextRouter` EI SAA yrittää pelastaa tilannetta arvauksella. Järjestelmän on kaaduttava välittömästi `MissingRoutingModeError` (RFC 7807) -virheeseen. UI:n on pakko ottaa kantaa siihen, ladataanko välivaiheeseen raskas raakadata vai karsittu kevyttila.
*   **Mitä säilytetään oletuksena:** True/False -tiedot per BARS-solmu sekä kokonaisarviointi (`blk_XXX_normalized`, `blk_XXX_level_breakdown`, `blk_XXX_justification`).
*   **Mitä säilytetään ehdollisesti:** Ne XAI-laajennokset (esim. `coaching`, `emotionalSentiment`), jotka löytyvät UI:n lähettämästä `output_config` -määrityksestä.
*   **Mitä poistetaan:** Raskaat `shuffled_atoms` -kentät sekä ne syvälliset teksti- ja quote-perustelut, joita UI *ei* ole pyytänyt `output_config`in kautta. 
*   **No Naked Dicts:** Tämä dynaaminen projektio (`LightweightMatrixOutput`) on Pydantic-malli, ja se käännetään tekoälyn kontekstiin turvallisesti `.model_dump(mode='json')` kautta (`rule: no_naked_dicts_in_state`).

## 5. Arkkitehtoniset Suojamuurit (Best Practices)
Käyttöliittymän absoluuttinen diktatuuri edellyttää, että taustajärjestelmä on suojattu inhimillisiltä konfiguraatiovirheiltä (Zero-Compromise Fail-Fast). Jotta koodaava tekoäly ei yritä arvata DTO-malleja tai käyttää kiellettyjä `Any`/`Optional` -kenttiä, Epic 35 määrittelee niiden rakenteet etukäteen.

### 5.1 Eksaktit Pydantic-tietosopimukset (Data Contracts)
Rakennetaan uusi Pydantic-malli (`LightweightMatrixOutput`), jonka kautta matriisitulokset ajetaan synteesiin. Vältetään Duck Typing ja raaka sanakirjamanipulaatio kokonaan.
*   **Ei "Mega-malleja":** Malli EI SAA käyttää kymmeniä `Optional` tai `| None` kenttiä dynaamisille XAI-laajennuksille (kuten `coaching: str | None`). Dynaaminen karsinta hoidetaan tiukasti tyypitetyllä sanakirjalla: `extensions: dict[XaiExtensionType, str]`.
*   **Tiukat Atomit:** BARS-atomit on välitettävä tiukkana Bool-sanakirjana (ID -> Osuma), ei vapaamuotoisena datana.
*   **SDUI Discriminator:** Flutterin Freezed/Riverpod-arkkitehtuuri kaatuu (TypeError), jos SDUI-objekteilla ei ole staattista `type` -Literal kenttää. Polymorfisten SDUI-lohkojen on aina perittävä abstrakti kantaluokka.

**Skeemojen pakotetut ytimet (Koodin tuottamisen pohja):**
# 1. Output Profile Konfiguraatio
class OutputProfileConfig(BaseModel):
    visible_extensions: list[XaiExtensionType] = Field(default_factory=list)
    # UI voi lähettää täällä myös muita näyttöasetuksia tulevaisuudessa.
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

# 2. Karsittu Kevyttila (Dynaaminen reititys)
class LightweightMatrixOutput(BaseModel):
    normalized_score: float = Field(ge=0.0, le=1.0)
    level_breakdown: str
    justification: str
    evaluated_atoms: dict[str, bool] = Field(default_factory=dict) # Sokea ID -> True/False (esim. {"node_abc": True})
    extensions: dict[XaiExtensionType, str] = Field(default_factory=dict) # UI:n tilaamat XAI-laajennukset

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

# 3. SDUI Synteesin Ulostulo (Flutter Parity)
# HUOM: Nämä on sijoitettava valmiiseen tiedostoon: backend_v2/models/view/sdui.py
# Uusia SDUI-malleja tai tiedostoja ei saa luoda tätä varten ohi olemassa olevan arkkitehtuurin.
class SduiBlockBase(BaseModel):
    block_type: str # Pakollinen discriminator (Riverpod reititys)

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

class HeroInsightBlock(SduiBlockBase):
    block_type: Literal["hero_insight"] = "hero_insight" # Pakottaa Dart-yhteensopivuuden
    title: str
    insight_text: str

# Polymorfinen reititys (Kriittinen Pydantic-validaatiolle)
AnySduiBlock = Annotated[
    Union[HeroInsightBlock], # Tähän lisätään tulevaisuudessa muut lohkot
    Field(discriminator="block_type")
]
```

### 5.2 Turvallinen Polun Purkaminen (Safe Dot-Notation Parser)
Käyttöliittymä antaa dynaamisia polkuja, kuten `$steps.step_1.outputs`. Tekoälyn (koodarin) on purettava nämä polut rakentamalla **Turvallinen Iteratiivinen Purkaja**. Tämä uusi aliohjelma on toteutettava olemassa olevaan util-tiedostoon `backend_v2/utils/dict_utils.py` (esim. nimellä `resolve_dot_notation`), jotta vältetään uusien tiedostojen turha luonti.
*   **Kielletty: `eval()` ja `exec()`:** Dynaamisten merkkijonojen ajaminen suoritettavana koodina (esim. `eval(f"state.{path}")`) on kriittinen tietoturva-aukko ja ankarasti kielletty.
*   **Kielletty: Sokeat Fallbackit:** Polkuja ei saa "arvailla" antamalla oletusarvoja tyyliin `getattr(obj, part, None)` tai `dict.get(part, {})`. Tämä on suora `the_zero_compromise_pledge` -säännön loukkaus.
*   **Tiukka Iteratiivinen Haku:** Polku on **pakko** purkaa komennolla `parts = path.split('.')`. Tämän jälkeen tilaa iteroidaan puhtaasti askel kerrallaan: 
    *   Jos nykyinen solmu on sanakirja, arvo haetaan tiukasti `curr = curr[part]`. 
    *   Jos kyseessä on olio (esim. Pydantic-malli), arvo haetaan tiukasti `curr = getattr(curr, part)`.
    *   **Listojen käsittely:** Jos polun osa on indeksi (esim. `0` polusta `outputs.0` tai jos erillinen regex parsii `outputs[0]` -formaatin), se yritetään muuttaa kokonaisluvuksi `idx = int(part)` ja haetaan `curr = curr[idx]`.
*   **Zero-Duct-Tape Virheenkäsittely:** Koska `getattr`, `[part]` ja `[idx]` on pakotettu ilman oletusarvoja, ne nostavat heti `KeyError`, `AttributeError`, `IndexError` tai `ValueError` poikkeuksen, jos dataa/indeksiä ei ole tai se on rikki. Nämä kaikki napataan *iteratiivisen haun ympärillä* olevalla `try-except` -lohkolla, joka heittää välittömästi `MissingInputMappingError` (RFC 7807) ja kaataa työnkulun. Sokeat `except Exception: pass` tai `return None` ("Duct Tape") ovat `the_duct_tape_ban` -säännön vastaisia ja siksi kiellettyjä.

### 5.3 Olemassaolevien Työkalujen Uudelleenkäyttö (Dependency Firewall)
Toteutuksessa on ehdottomasti nojattava projektin valmiisiin ratkaisuihin ja komponentteihin. Omien "pyörien keksiminen" tai uusien kirjastojen asentaminen arkkitehtuuriongelmien kiertämiseksi on ankarasti kielletty (Sääntö: `dependency_hallucination_firewall`).
1.  **Token-laskenta ja heuristiikka:** `TokenLimitExceededError` -katkaisun laskenta on toteutettava olemassa olevan integraatiokerroksen avulla, eli kutsumalla `litellm.token_counter(text=...)`. Tekoäly (koodari) EI SAA asentaa projektiin uutta `tiktoken` tai `transformers` -riippuvuutta (eikä importoida niitä suoraan ohi `litellm`:n).
2.  **Tietokantayhteydet ja Välimuistit:** Synteesitulokset ja ContextRouterin tilat tallennetaan suoraan olemassa olevan TinyDB/Event Sourcing -arkkitehtuurin kautta (esim. `ExecutionRecord.profile_syntheses`). Uusien in-memory välimuistien (kuten globaali `dict()` sanakirja) tai uusien tietokantamoottorien (kuten Redis tai SQLite rinnalle) pystyttäminen on täysin kielletty.
3.  **Apuohjelmien (Utils) kierrätys:** Jos tarvitaan sanakirjamanipulaatiota tai tyyppiturvallisuutta, on käytettävä olemassa olevia apuohjelmia, kuten `backend_v2/utils/pydantic_utils.py` (`inflate`-funktio) ja `backend_v2/utils/dict_utils.py`. Uusien rinnakkaisten apuohjelmatiedostojen luonti on kielletty.
4.  **Pakettien Jäädytys:** Koko Epic 35 on suunniteltu ratkaistavaksi 100% olemassa olevalla koodikannalla. `pyproject.toml` ja `uv.lock` -tiedostoihin ei saa tehdä yhtäkään lisäystä tämän Epicin toteutuksen aikana.

2.  **The Zero Compromise Pledge & The Duct Tape Ban:** `hasattr()`, `isinstance(dict)`, taaksepäinyhteensopivuus, "jos A puuttuu, kokeile B" -ketjut ja `.get("avain", "default")` ovat täysin kiellettyjä. Puuttuvia UI-mäppäyksiä EI paikata tyhjillä listoilla `[]` tai tyhjillä sanakirjoilla `{}`.
3.  **Fail-Fast puuttuvilla UI-mäppäyksillä (Code is Truth):** Jos UI on mäpännyt syötteen (esim. `$inputs.haastattelu`), jota ei tilarakenteesta löydy, järjestelmä EI yritä jatkaa tai paikata tilannetta. Se heittää välittömästi `MissingInputMappingError` (RFC 7807) ja kaataa työnkulun.
4.  **Token Limit -suojamuuri `$steps`-polulle (Fail-Fast):** Korjattu globaali `$steps`-hakutoiminto laskee datan koon, mutta EI SAA käyttää sokeaa leikkuria (silent truncation). Jos UI:n mäppäämä data ylittää määritellyn `max_tokens`-rajan, järjestelmä ei saa leikata tekstiä piilossa (mikä rikkoisi JSON-rakenteet ja "UI on diktaattori" -periaatteen). Sen sijaan järjestelmän on heitettävä välitön `TokenLimitExceededError` (RFC 7807) ja kaaduttava. Tämä pakottaa mallin rakentajan korjaamaan reitityksen tarkemmaksi (esim. pyytämään vain `$steps.step_1.outputs`).
5.  **Feature Sovereignty & UI Driven Synthesis Boundary:** Karsintalogiikka (Pruning) kunnioittaa absoluuttisesti tulostusprofiileja (Output Profiles). Jos UI määrää, että esim. `falsification` tai `coaching` on tulostettava raporttiin, backendin karsintamekanismi ei koskaan piilota tätä dataa syntetisoivalta tekoälyltä tokenien säästämisen varjolla. Optimointi ei saa rampauttaa liiketoiminnallisia ominaisuuksia.
6.  **Fail-Fast for Missing Output Config:** Jos synteesikutsu tulee ilman eksplisiittistä `output_config` -objektia tai arrayta, `ContextRouter` EI SAA yrittää arvata "hyviä oletusasetuksia". Koko synteesipyyntö on kaadettava välittömästi `ConfigurationError` (RFC 7807) -poikkeukseen. UI on diktaattori, ja diktaattorin on annettava selkeä käsky.

## 6. Tier 2 Hardening -Yhteensopivuus (Phase 9)
Epic noudattaa `.agents/rules/01-python-backend.md` -tiedoston määrityksiä orjallisesti:
*   `strict_pydantic_v2_rust`: Käytetään `ConfigDict(extra="forbid", strict=True)` ja parsitaan data puhtaasti `.model_validate()` ja `.model_dump()` kautta. Sanakirjojen suora `.pop()` tai `.get()` ohitetaan.
*   `no_naked_dicts_in_state`: Välimuistiin (State) ei työnnetä paljaita sanakirjoja ohittaen tarkastukset.
*   `the_zero_compromise_pledge`: Ehdoton kielto `hasattr` ja kielen tason arvauksille tai laastaroinnille datan etsinnässä. Code is Truth = You explicitly map it, or it crashes.
*   `the_duct_tape_ban`: Ei laajoja `try...except Exception: pass` blokkeja tai väärennettyjä oletusarvoja, kun data puuttuu.
*   `python_314_modern_syntax`: `| None` sallittu, `Optional` kielletty. Ei `asyncio.gather()`. PEP 695 generics käytössä.
*   `no_inline_imports`: Kaikki importit tiedoston alussa. Inline importit ovat täysin kiellettyjä.
*   `ui_driven_synthesis_boundary`: Pakotetaan datan tarkka suodatus käyttöliittymän määritysten mukaan taustadumppauksen sijaan.

## 7. Monoliitin Purku (Refactoring `llm.py`)
Tällä hetkellä `LLMNodeStrategy.execute()` on massiivinen (yli 500 riviä). Vastuut jaetaan puhtaasti uuteen `ContextRouter` -moduuliin (`backend_v2/services/orchestrator/context_router.py`).

### ContextRouterin Konkreettinen Arkkitehtuuri
`ContextRouter` vastaa yksinomaan käyttöliittymän `input_mappings` -polkujen purkamisesta ja datan karsinnasta (Pruning) synteesiä varten. Se on arkkitehtuurin suojamuuri.

**Näin karsinta toimii teknisesti (Zero-Compromise):**
1.  **Kielletty Anti-Pattern (Lennosta generoidut sanakirjat):** Järjestelmä EI SAA tehdä näin: `raw_dict = trace_event.model_dump(); del raw_dict["shuffled_atoms"]`. Raakojen sanakirjojen (naked dicts) manipulointi lennosta ja niiden syöttäminen LLM:lle on ehdottomasti kielletty, koska se tuhoaa tyyppiturvallisuuden ja avaa oven piilobugeille.
2.  **`output_config` muuntaminen Pydantic-logiikaksi:** Synteesivaiheessa UI lähettää `OutputProfile`n, joka sisältää listan `visible_extensions` (esim. `[XaiExtensionType.COACHING]`).
3.  **Strict Object Instantiation (In-Memory Mapping):** Service-kerros injektoi raskaat `TraceEvent` -objektit routerille. Sen sijaan, että router yrittäisi poistella niistä kenttiä (exclude), se **rakentaa puhtaalta pöydältä** uuden `LightweightMatrixOutput` -Pydantic-mallin jokaiselle matriisille.
4.  **Täsmäpoiminta (Explicit Mapping) ja Asymmetrinen Data:** 
    *   Router asettaa staattiset kentät suoraan: `normalized_score = event.score`, `justification = event.justification`.
    *   Tämän jälkeen router iteroi UI:n pyytämän `visible_extensions` -listan. Vain listalta löytyvät XAI-laajennukset poimitaan `TraceEvent`:stä ja sijoitetaan turvallisesti tyypitettyyn `extensions: dict[XaiExtensionType, str]` -sanakirjaan.
    *   **Kriittinen Fail-Fast (Asymmetrinen data):** Jos UI on tilannut `visible_extensions` -listassa laajennuksen (esim. `COACHING`), jota ei löydy alkuperäisestä `TraceEvent`-objektista datan korruptoitumisen tai aikaisemman API-virheen vuoksi, järjestelmä EI SAA ohittaa tätä sokeasti (esim. `dict.get()` tai asettamalla tyhjä merkkijono). Zero-Compromise -hengessä `ContextRouter`in on kaaduttava välittömästi `MissingXaiExtensionError` (RFC 7807) -poikkeukseen. Data on joko täydellistä, tai työnkulku keskeytyy.
5.  **JSON-käännös ja LLM-injektio (`ephemeral_caching_topology` & `role_segregation_and_fencing`):** Lopuksi LLM:n kontekstiin viedään puhdas ja turvallinen merkkijono kutsumalla `.model_dump_json()`. Synteesi-tekoäly lukee aina tiukasti tyypitettyä, Pydanticin validoimaa JSON-rakennetta, ei koskaan koodin keskellä manipuloitua raaka-sanakirjaa. **Kriittinen sääntö:** Tämä dynaaminen JSON-data sijoitetaan *yksinomaan* LLM:n `user` -viestiin ja suojataan XML-tageilla (esim. `<matrix_data>...</matrix_data>`). `system` -viesti pidetään 100% staattisena välimuistituksen (Context Caching) maksimoimiseksi.

## 8. Synteesivaiheen Toteutus (Päätuloksen Generointi)
Käyttöliittymän tulostusprofiili (esim. `prf_5d6e7f8091a2b3c4`) määrittelee tarkan system_directiven (esim. `<role>Senior Executive Coach</role>`) ja otsikoinnit. Miten tämä lopullinen raportti generoidaan teknisesti?

### Nykyinen ratkaisu (Anti-Patterns)
*   **Sokea Data-Dump:** LLM saa sokean ja joko massiivisesti ylisuuren tai rikkoutuneen (`_strip_heavy_keys`) datadumpin kaikista stepeistä. 
*   **Vapaa Markdown:** Järjestelmä käyttää mahdollisesti `run_chat()`-metodia, ja pyytää tekoälyä kirjoittamaan "hyvän raportin" Markdownina. Tämä kaataa UI-renderöinnin, koska rakenne on arvaamaton.
*   **Kielisekaannus (Intelligence Dropping):** Tekoäly pakotetaan analysoimaan monimutkainen matriisidata ja generoimaan lopputulos suoraan suomeksi. Tämä vie valtavasti prosessointitehoa kielen kääntämiseen ja romahduttaa loogisen päättelyn laadun.

### Tuleva ratkaisu (Zero-Compromise Architecture - KAIKKI ALLA ON UUTTA KEHITYSTÄ)
1.  **Late-Binding Context Routing:** Koska Output Profile valitaan (tai voidaan vaihtaa) vasta matriisiajon jälkeen, tekoälylle syötetään `ContextRouter`in kautta täsmälleen vain ne matriisit ja atomit, jotka synteesihetkellä valittu profiili määrittelee.
2.  **`output_config` Reitityksen Ytimenä:** Synteesivaihe saa UI:lta `output_config` -objektin. `ContextRouter` suodattaa tietokannassa lepäävän 100% matriisiraakadatan tämän konfiguraation perusteella (leikkaamalla pois piilotetut XAI-kentät tokenien säästämiseksi). Mitään ylimääräistä taustadataa ei injektoida synteesi-tekoälylle (`ui_driven_synthesis_boundary`).
3.  **Structural Sovereignty (SDUI Pydantic pakotus & Skeeman Injektointi):** Synteesivaihe pakotetaan käyttämään `run_structured_task()` -metodia. LLM ei palauta vapaata tekstiä, vaan tarkan Server-Driven UI (SDUI) -arrayn (esim. `list[AnySduiBlock]`), jotta Flutter-käyttöliittymä osaa renderöidä sen natiivisti ilman arvaamista (`structured_sdui_outputs`). 
    *   **Fail-Fast & Self-Healing:** Jos LLM hallusinoi kenttiä tai unohtaa `block_type` -discriminatorin, Pydantic-validointi heittää välittömästi `ValidationError`-poikkeuksen. Jotta rajapinta ei kaadu suoraan 500 Internal Server Erroriin, synteesivaiheen on EHDOTTOMASTI kutsuttava `run_structured_task(..., max_retries=3)`. Tämä laukaisee olemassa olevan arkkitehtuurin automaattisen Semantic Self-Healing -mekanismin (Epic 12), joka syöttää virheen takaisin LLM:lle ja pakottaa sen korjaamaan JSON-rakenteen.
4.  **The English-Only Mandate (System Prompt Refaktorointi):** Itse kognitiivinen synteesipäättely ja tekstin tuotanto tapahtuvat **100% englanniksi** maksimaalisen älykkyyden ja "kognitiivisen kitkan" säilyttämiseksi. Jotta LLM ei murra tätä sääntöä, `seed_data.json` -tiedostossa olevat synteesiprofiilien järjestelmäkehotteet (`<system_directive>`) on refaktoroitava suomesta englanniksi (esim. "Siirtymä vaaka-akselilla..." -> "A horizontal shift to the right indicates..."). Vasta kun englanninkielinen SDUI-objekti on valmis, erillinen `translation_hook` kääntää näytettävät tekstit käyttäjän pyytämälle kielelle. 
    *   **Suorituspaikka Pipelinessa (Database Integrity):** `translation_hook` suoritetaan VASTA SITTEN, kun englanninkielinen raaka-synteesi on jo tallennettu tietokantaan (`ExecutionRecord.profile_syntheses`). Hook ajetaan lennosta juuri ennen kuin HTTP-vastaus palautetaan API:sta Flutter-asiakkaalle. Tietokantaan ei saa koskaan tallentaa käännettyjä objekteja, jotta "Ground Truth" pysyy ikuisesti englanninkielisenä.
    *   **Kriittinen rajaus (Pydantic-turvallisuus & Immutability):** Koska kaikki mallit ovat Quorum-arkkitehtuurissa jäädytettyjä (`frozen=True`), suora arvosijoitus (esim. `obj.title = "Uusi"`) kaataa järjestelmän välittömästi. Käännös on **pakko** toteuttaa seuraavalla ehdottomalla kaavalla: 1) Pura objekti sanakirjaksi `raw_dict = obj.model_dump()`. 2) Iteroi sanakirjaa rekursiivisesti ja käännä *vain ja ainoastaan* merkkijono-arvot (stringit). 3) Luo ja palauta uusi jäädytetty objekti: `model_class.model_validate(raw_dict)`. Sanakirjan avaimia tai Pydantic-rakennetta EI SAA muuttaa.

## Verification Plan
1. Validoidaan, että automaattinen injektio poistuu ja UI-mäppäyksen ohittaminen tiedostoilta johtaa Fail-Fast -tilaan tai tyhjään (mutta odotettuun) kontekstiin LLM-kutsussa.
2. Varmistetaan `lue_tulokset.py` ajamalla, että järjestelmä tuottaa yhä täydellisen BARS-raportin pelkkien Pydantic-mallilla typistettyjen True/False -atomien ja kokonaisarvioinnin avulla, eikä yhtään ylimääräistä tekstiä lipsu matriisien lokiin (Rule: `no_naked_dicts_in_state`).
3. Testataan `$steps` polun purkaminen turvallisesti ilman Token-räjähdyksiä.
4. Suoritetaan `backend_audit_loop.py` uusien tiedostojen osalta virheiden välttämiseksi (`universal_quality_gate`).
