# EPIC 88: Unified Forensic Traceability (XAI-Kausaalimäppäys & Rakenteellinen Todistusaineisto)

## 1. Yhteenveto & Tavoite (Executive Summary)

Tämä Epic on synteesi aiemmista suunnitelmista (EPIC 86 ja EPIC 87), joiden tavoitteena oli parantaa Quorum V2 -arkkitehtuurin läpinäkyvyyttä (XAI - Explainable AI) ja todistusaineiston hallintaa. 

**Perusongelma (System 1 -ajattelun ansa):**
Tekoälyjärjestelmissä todistusaineisto (esim. tekstistä poimitut sitaatit) ja työkalujen käyttö (esim. ulkoiset verkkohaut) jäävät usein irrallisiksi saarekkeiksi. Käyttäjä näkee, että tekoäly teki haun X ja antoi arvosanan Y, mutta *syy-seuraussuhde* näiden välillä on LLM:n mustassa laatikossa. Aiemmin pohdimme ongelman ratkaisemista kahdella erillisellä polulla: ryhmittelemällä sitaatit (EPIC 86) ja pakottamalla LLM selittämään hakujen vaikutukset (EPIC 87).

**Ratkaisu (System 2 -synteesi):**
Nämä kaksi polkua yhdistyvät täydellisesti, kun luomme **universaalin todistusaineisto-atomin (`EvidenceQuoteDTO`)**. Tätä mallia käytetään **kaikissa järjestelmän atomeissa ja matriiseissa** (mukaan lukien Archivist-matriisi). Jatkossa *mikään* tekoälyn väite ei ole vain irrallinen merkkijono, vaan itsenäinen objekti, jolla on sisäinen lähdeviite (`source_reference`) tai oma unikaali ID. 

Jos väite vaati ulkoisen verkkohaun (MCP), LLM sitoo tämän yksittäisen atomin suoraan hakutuloksen ID:hen (`used_mcp_ids`). Näin saamme rakennettua täydellisen **deterministisen kausaalisen sillan (Causal Bridge)**: sisäiset sitaatit toimivat suorina viitteinä tekstiin, ja ulkoisesti todennetut sitaatit linkittyvät graafina suoraan MCP-lokeihin. Kaikki graafin rakentaminen siirretään pois LLM:ltä ja suoritetaan deterministisesti puhtaassa Python-koodissa (`BlueprintTransformer`).

---

## 2. Arkkitehtuurinen Konsepti & Perustelut (System 2 Deep Dive)

### 2.1 Miksi LLM ei saa rakentaa graafia itse? (Falsifikaatio)
*Hypoteesi:* LLM voisi itse tulostaa valmiin JSON-rakenteen, jossa se kertoo "Haku A vaikutti sääntöön B, ja tässä on todisteet."
*Falsifikaatio:* Varianssitestaus (kuten 28.6.2026 suoritettu E2E-testi) osoittaa, että kun LLM:lle annetaan liian monimutkainen relationaalinen tehtävä, se alkaa hallusinoida ID-koodeja ja unohtaa reunaehtoja (Goodhartin laki). LLM on stokastinen generaattori, ei relaatiotietokanta.
*Johtopäätös:* LLM:n vastuulle jätetään ainoastaan **yhden suunnan** atominen osoitus (Sitaatti $\rightarrow$ Hakutuloksen ID). Python-backend vastaa matemaattisen syy-seuraus -graafin kokoamisesta molempiin suuntiin.

### 2.2 Chunk-tasoinen Voileipä-injektio (Sandwich Prompting)
**Ongelma (Lost in the Middle ja Megadokumentit):** Suurilla konteksti-ikkunoilla LLM menettää paikallisen tarkkuutensa (Local Attention). Jos tulostamme aliaksen vain 15 000 tokenin pituisen PDF-dokumentin alkuun ja loppuun, ja malli poimii faktan tokenin 8000 kohdalta, se on jo unohtanut aliaksen.
**Ratkaisu:** Kausaalinen injektio tehdään Chunk-tasolla. Backend pilkkoo isot lähdedokumentit ja MCP-tulokset n. 1000–1500 tokenin paloihin. Alias toistetaan **jokaisen palan** yhteydessä:
```xml
<search_result ID="<<QRM-SRC-1>>" chunk="1/15">
[Tekstisisältö 1-1000 tokenia...]
</search_result>
<search_result ID="<<QRM-SRC-1>>" chunk="2/15">
[Tekstisisältö 1001-2000 tokenia...]
</search_result>
```

**Kriittinen Vaatimus (Chunk Overlap):** Kun dokumentteja tai hakutuloksia pilkotaan `alias_registry.py`:ssä, koodiin on ehdottomasti ohjelmoitava **n. 150-200 tokenin Chunk Overlap (Lomittuminen)**. Jos teksti katkaistaan kylmästi rajalta, LLM:n poimima kokonainen lause saattaa jakautua kahteen eri lohkoon. Vaikka LLM osaisi yhdistää sen kielellisesti ymmärrystä varten, asynkronisessa Workerissa suoritettava RapidFuzz-käänteishaku tulisi kaatumaan (Didactic DLQ), koska kumpikaan yksittäinen lohko ei sisällä koko haettavaa merkkijonoa. Lomittuminen takaa, että jokainen lause mahtuu vähintään kerran kokonaisena yhteen lohkoon.
Tämä takaa, että alias on aina fyysisesti (kielellisessä avaruudessa) lähellä löydettyä faktaa, ja malli kykenee sitomaan ne toisiinsa virheettömästi pitkissäkin dokumenteissa.

Kun LLM arviointilogiikassaan löytää säännön täyttävän sitaatin, se dokumentoi yhteyden Pydantic-skeemassa tällä kevennetyllä tunnisteella:
```json
{
  "text": "Työterveyslaitos suosittelee kahta läsnäolopäivää.",
  "used_mcp_ids": ["<<QRM-SRC-1>>"]
}
```

### 2.3 Kunniallinen Ulospääsy (The Escape Hatch)
**Ongelma:** Jos Pydantic-skeema vaatii LLM:ltä todistusaineisto-objektien listaa, malli kokee usein kognitiivista painetta (Sycophancy) tuottaa edes jotain täyttääkseen skeeman, mikä johtaa keksittyihin faktoihin tai vääristeltyihin tiivistyksiin.
**Ratkaisu:** Annamme mallille eksplisiittisen "ulospääsyn". Pydantic-kentän `description` -attribuuttiin ohjelmoidaan vahva psykologinen lupa: *"Tyhjä lista on täysin oikea vastaus faktojen puuttuessa."* Tämä purkaa mallin paineen keksiä dataa ja vähentää hallusinaatioiden riskiä radikaalisti.

### 2.4 Negatiiviset Rajoitteet ja Eteenpäin kytketty Konsistenssi
**Ongelma (Kaksoissidos ja Negatiivinen Rajoite):** Jos vaadimme mekaanisesti, että `level > 0` vaatii aina sitaatin, rikomme **negatiivisten rajoitteiden** arvioinnin (esim. "Varmista ettei tekstissä ole henkilötietoja" tai "Varmista ettei ole absoluuttisia väitteitä"). Jos teksti noudattaa tällaista sääntöä täydellisesti, rikkomusta ei löydy (`quotes = []`), jolloin arvosanan pitäisi olla korkein mahdollinen (`level = 5`). Mekaaninen validaattori kaataisi täydellisen ajon ja pakottaisi mallin joko antamaan väärän arvosanan (0) tai hallusinoimaan keksityn rikkomuksen.
**Ratkaisu (Safest Way):** Emme sido arvosanaa ja sitaatteja toisiinsa jäykällä `raise ValueError` -validaattorilla Pydanticissa. Luotamme täysin **Evidence-First Forcing** -arkkitehtuuriin (sitaatit uutetaan ensin). Lisäksi laajennamme "Kunniallista ulospääsyä" (Escape Hatch) mallin promptissa kattamaan negatiiviset säännöt: *"Jos sääntö on negatiivinen rajoite ja teksti noudattaa sitä (rikkomuksia ei ole), palauta tyhjä lista [] ja anna korkea arvosana."* Näin malli voi loogisesti antaa positiivisen arvosanan ilman todisteita, kun säännön luonne sitä edellyttää.

### 2.5 Deterministinen Käänteishaku (Reverse Lookup)
`BlueprintTransformer` (Python) käsittelee valmiin JSON:n ja luo kaksisuuntaisen XAI-jäljitettävyyden esityskerrokselle (PDF/Flutter) ilman, että esityskerros joutuu suorittamaan logiikkaa (Flat MVC -mandatti):

1. **Käänteishaku (Sanakirja):** Python lukee listasta aliaksen `<<QRM-SRC-1>>` ja kääntää sen alkuperäiseksi UUID:ksi (esim. `tavily_1a2b...`).
2. **Sitaatin rikastaminen:** Python asettaa sitaatille `is_mcp_verified = True` ja päivittää `used_mcp_ids` -listaan todelliset UUID:t esityskerrosta varten.
3. **Audit-lokin rikastaminen:** Python etsii audittilokista alkuperäisen haun ja lisää sen listaan tiedon: `impacted_axis_names: ["Episteeminen Nöyryys"]`.

### 2.6 Kognitiivinen Kitka ja XAI-kokemus (Cognitive Friction)
Pakottamalla LLM:n rakenteelliseen CoT-päättelyyn (`knowledge_gap` ja `search_rationale`) luomme tahallista **kognitiivista kitkaa (Friction)**.
* **XAI herää eloon:** Käyttäjä ei näe lokissa mystistä tekstiä "Tekoäly teki haun". Hän näkee kirkkaan asiantuntijapäättelyn: *"Järjestelmä havaitsi, että dokumentista puuttuu maininta verotusarvoista, ja siksi se haki Verohallinnon ohjeen."* Tämä läpinäkyvyys poistaa loppukäyttäjän epäluulon mustaa laatikkoa kohtaan välittömästi.
* **Falsifikaatio (Sofismi-ansa):** Estääkö tämä yksinään roskahaut? Ei. LLM ei pysähdy miettimään asioita abstraktisti. Jos sen "Systeemi 1" -heuristiikka haluaa tehdä turhan haun, mallin kielellinen ylivoima keksii sille millisekunnissa ällistyttävän vakuuttavan ja akateemisen `search_rationale`:n. CoT tekee roskahauista vain poikkeuksellisen hienosti perusteltuja.
* **Arkkitehtuurinen Vahvistus:** Tästä syystä CoT on ensisijaisesti **käyttäjäkokemuksen (XAI) työkalu**, ei tekninen turvamekanismi. Varsinaisena arkkitehtuurisena jarruna toimii ehdoton, kooditason rajoite: **Mekaaninen iteraatiokatto (Max Loop Depth)** (esim. `MAX_TOOL_TURNS = 2`). Kognitiivinen kitka luo luottamusta, mutta vain kova koodi estää ikuiset hakusilmukat ja kontekstin tukkeutumisen.

### 2.7 Evidence-First Forcing (Käänteinen generointijärjestys)
**Ongelma:** LLM:t generoivat tekstiä token kerrallaan ylhäältä alas. Jos Pydantic-malli pyytää ensin arvosanaa (`level`) ja vasta sen jälkeen todisteita (`quotes`), LLM tekee nopean heuristisen päätöksen (System 1) ja ankkuroituu siihen ("Annoin jo korkean arvosanan"). Tämän jälkeen se syyllistyy jälkikäteisrationalisointiin: se etsii teksteistä väkisin (cherry-picking) todisteita oikeuttaakseen jo tehdyn päätöksen.
**Ratkaisu:** Kognitiivinen järjestys käännetään ylösalaisin (Bottom-up -induktio). Pydantic-mallissa `quotes`-kenttä on sijoitettava *ennen* `level`-kenttää. Tämä pakottaa mallin keräämään empirian ensin. Arvosana saa olla vain looginen seuraus niistä faktoista, jotka se on juuri tulostanut ylemmille riveille.

### 2.8 XAI-teatterin Esto (Semantic Sanity Check)
**Ongelma (XAI-teatteri):** Vaikka Python kääntäisi ja todentaisi semanttisen aliaksen (`<<QRM-SRC-1>>`), se on täysin sokea sille, onko itse *sitaatti* aito. LLM saattaisi keksiä täydellisen kuuloisen sitaatin ja lätkäistä sille validin aliaksen. 
**Ongelma (Suomen kielen hauraus):** Puhdas `Exact Match` kaatuu tuotannossa aina PDF-tavutusviivojen ja whitespace-muutosten takia. Toisaalta perinteinen sumea haku (> 90 % Levenshtein-kynnys) on liian ankara suomen kielen kaltaisille agglutinoiville kielille, joissa yhdyssanat ja taivutukset muuttuvat.
**Ratkaisu (Kielikohtainen kynnys + Aggressiivinen Normalisointi):** Käänteishaku vaatii rinnalleen **Sumean Merkkijonohaun (Fuzzy Text Matching)**, mutta se suoritetaan kahdella tarkkuustasolla:
1. **Esiprosessointi:** Quorumin olemassa oleva funktio `AnchorValidationService.normalize_text_with_mapping()` on **pakollinen**. Se poistaa välimerkit, rivinvaihdot, HTML-tägit ja skandinaaviset merkit (ä -> a), jättäen vain puhtaan aakkosnumeerisen rungon.
2. **Kielikohtainen Kynnys (Locale-based Threshold):** Kynnysarvoa ei ole hardkoodattu. Järjestelmä käyttää funktiota `get_lexical_fuzz_threshold(locale)` (`enums.py`), joka mukauttaa vaatimuksen kielen rakenteen mukaan:
   - **85.0 % (Agglutinatiiviset):** Suomi, unkari, turkki (sallii yhdyssanojen ja taivutusten varianssia).
   - **92.0 % (Analyyttiset):** Englanti, ruotsi, saksa (tiukempi vaatimus).
   - **98.0 % (Eristävät):** Kiina, japani (lähes eksakti).

**Kansainvälisen Ohjelmiston Skaalautuvuus (Kriittinen Huomio):** Tämä dynaaminen locale-pohjainen lähestymistapa on täysin välttämätön, koska **Quorum ei ole pelkästään suomenkielinen ohjelmisto, vaan kansainvälinen alusta.** Jos kynnysarvo olisi koodattu kiinteästi suomen kielen vaatimusten mukaisesti (85 %), se heikentäisi englanninkielisten dokumenttien analyysin tiukkuutta ja lisäisi XAI-teatterin riskiä. Vastaavasti kiinteä englannin kielen kynnys (92 %) tekisi järjestelmästä käyttökelvottoman agglutinatiivisilla kielillä. `get_lexical_fuzz_threshold` takaa, että jokainen käyttäjäkieli saa optimaalisen tasapainon jouston ja matemaattisen totuuden välillä.

Tämä yhdistelmä sallii LLM:n korjata typografiaa suomen kielessä ilman jatkuvia "Didaktisia DLQ-silmukoita", mutta estää sitä silti keksimästä sanoja. Jos sumea osuma epäonnistuu -> DLQ: *"Sitaattia ei löydy fyysisesti lähteestä. Älä tiivistä, kopioi sanatarkasti."* Tämä kooditason pakotus muuttaa XAI:n teatterista matemaattiseksi totuudeksi kielestä riippumatta.

#### 2.8.1 Temporaalinen Epästabiilius ja API-pullonkaula (Arkkitehtuurinen vaatimus)
**Kriittinen sääntö:** Sumeaa hakua (`AnchorValidationService.calculate_fuzzy_score`) **EI SAA** suorittaa lennossa `BlueprintTransformerissa` silloin, kun käyttäjä lataa raportin (esim. `GET /api/v2/execution/executions/{id}/report`). Tähän on kaksi kriittistä arkkitehtuurista syytä:
1. **API-pullonkaula (CPU-Blocking):** FastAPI on asynkroninen. O(N*M) -monimutkaisuuden Levenshtein-etäisyyksien laskeminen satojen sitaattien ja satojen sivujen PDF-dokumenttien välillä synkronisesti HTTP GET -kutsun aikana tukkii koko Pythonin event loopin ja nostaa vasteajat sekunteihin (tai aiheuttaa timeoutteja).
2. **Historiallisen datan muuttuvuus (Forensic Breach):** Quorumissa Execution on immutaabeli tilannekuva. Jos `is_mcp_verified` laskettaisiin lennossa, ja sumean haun kynnysarvoa (esim. 85 % -> 88 %) muutettaisiin koodissa tulevaisuudessa, kaikki vuosia vanhat, aiemmin validit raportit muuttuisivat takautuvasti invalideiksi. Tämä tuhoaisi järjestelmän Sovereign Traceability -lupauksen täysin.

**Ratkaisu (Asynkroninen Esilaskenta):** Sumea haku ja kynnysarvon ylityksen varmistus (`is_mcp_verified`) on suoritettava **asynkronisesti tausta-ajon (Worker) aikana** (esim. `validation.py` tai `integrity.py` -hookeissa LLM-kutsun jälkeen). Validointitulos (boolean) tallennetaan pysyvästi osana ajon `execution_trace` -lokia. `BlueprintTransformer` on "tyhmä", puhdas funktio, joka ainoastaan lukee tämän valmiiksi lasketun totuusarvon tietokannasta, taaten 100 % API-suorituskyvyn ja absoluuttisen historiallisen stabiiliuden.
---

## 3. Tietomallit (DTO Specifications)

### 3.1 Universaali Todistusaineiston Atomimalli (Backend & Frontend)
Tätä mallia käytetään **kaikissa** arvioinneissa (Matrix, Archivist, standardiatomit). Se tekee jokaisesta väitteestä jäljitettävän ensiluokkaisen kansalaisen (First-Class Citizen).

```python
class EvidenceQuoteDTO(V2CoreBase):
    id: str = Field(default_factory=lambda: f"evq_{uuid.uuid4().hex[:12]}")  # Opaque Stripe ID (Quorum-konventio)
    text: str                                               # Itse sitaatti tai fakta
    source_reference: str | None = Field(default=None)      # Sisäinen lähde (esim. Sivu 12, Kappale 3)
    
    # Human-in-the-loop (Soft Delete)
    user_rejected: bool = False                             # Käyttäjän hylkäämä (Poisoning the Well -esto)
    rejection_reason: str | None = None                     # Miksi asiantuntija hylkäsi tämän
    
    # MCP-laajennus (Täytetään vain jos fakta varmennettiin työkalulla)
    is_mcp_verified: bool = False
    used_evidence_ids: list[str] | None = Field(default_factory=list)  # Sallitaan None, käännetään tyhjäksi listaksi

    @field_validator("used_evidence_ids", mode="before")
    def sanitize_lists(cls, v):
        # Mekaanisten syntaksivirheiden tyylkäs sieto:
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return v

class LevelQuotesDTO(BaseModel):
    # Evidence-First Forcing: Todisteet uutetaan ennen arvosanaa!
    quotes: list[EvidenceQuoteDTO] | None = Field(
        default_factory=list,
        description="Suorat lainaukset. JOS sääntöä tukevia todisteita ei löydy, palauta TÄYSIN TYHJÄ LISTA []. (Huom: Jos arvioit negatiivista rajoitetta ja teksti noudattaa sitä täydellisesti, palauta tyhjä lista ja korkea arvosana)."
    )
    level: int
    level_name: str

    @field_validator("quotes", mode="before")
    def sanitize_quotes(cls, v):
        if v is None:
            return []
        return v

class RowForensicsDTO(BaseModel):
    level_quotes: list[LevelQuotesDTO] = Field(default_factory=list)
```

#### 3.1.1 ID-stabiilius ja Persistenssi (Kriittinen Arkkitehtuuripäätös)
**Ongelma 1 (Hash-kollisio):** Jos LLM uuttaa täsmälleen saman lyhyen sitaatin (esim. "Ei havaittuja poikkeamia") kaksi kertaa samassa lohkossa eri sääntöihin, niiden tekstipohjainen hash on identtinen. Jos asiantuntija hylkää niistä toisen, molemmat hylkääntyvät. Tämä tuhoaa Soft Delete -mekanismin tarkkuuden.

**Ongelma 2 (Orvot ylikirjoitukset / Hauras ID):** DTO:n on tarkoitus olla johdettu näkymä (derived view). Jos `EvidenceQuoteDTO.id` laskettaisiin dynaamisesti lennossa hash-funktiolla (esim. `hash(execution_id + quote_text)`), järjestelmä olisi äärimmäisen hauras. Jos tekstin normalisointi tulevaisuudessa muuttuu (esim. välilyöntien siivous), hash muuttuu. Tällöin kaikki tietokantaan aiemmin tallennetut Soft Delete -tapahtumat (`evidence_override`) osoittaisivat väärään ID:hen (Orphaned Override) ja hylätyt sitaatit palaisivat raportteihin.

**Ratkaisu (Persistoitu Opaque ID):** Hash-funktiota **EI SAA** käyttää primaariavaimena mutatoitavalle datalle (Soft Delete). Oikea UUID4 (`evq_...`) on generoitava Workerissa heti uuton jälkeen, ja tämä pysyvä UUID on **tallennuttava pysyvästi `execution_trace`-lokiin** alkuperäisen poimintatapahtuman sisään (esim. atomin metadataan tai erilliseen sanakirjaan `quote_id_map`).
Kun `BlueprintTransformer` rakentaa `RowForensicsDTO`:n, se *lukee* tämän saman ID:n suoraan tracesta. Näin ID on täysin immuuni tekstin normalisoinnin muutoksille ja takaa katkeamattoman relaation `evidence_override` -lokitapahtumiin, estäen myös hash-kollisiot identtisillä sitaateilla.

#### 3.1.2 N x M Lähdemäppäyksen Katoaminen (Autonominen Relaatio)
**Ongelma:** Kuten arkkitehtuurissa on linjattu, haluamme pitää LLM:n palauttaman Pydantic-skeeman mahdollisimman litteänä ja yksinkertaisena välttääksemme JSON-jäsennysvirheet ja hallusinaatiot. Tämän vuoksi LLM palauttaa yksinkertaiset litteät listat: `exact_quotes: list[str]` ja `used_evidence_ids: list[str]`. 
Mutta jos LLM palauttaa esimerkiksi kolme sitaattia ja kaksi lähde-id:tä, mistä järjestelmä tietää, mikä sitaatti kuuluu mihinkin lähteeseen? Epicin alkuperäinen luonnos ei ratkaissut tätä M:N -relaatiota.

**Ratkaisu (Worker-tason Brute Force):** Emme pakota LLM:ää tuottamaan monimutkaisia nästettyjä objekteja (esim. `[{"quote": "...", "source": "..."}]`). Sen sijaan **Python (Worker-vaiheessa)** hoitaa työn. Kun Worker saa listan sitaatteja ja listan lähteitä, se suorittaa asynkronisesti O(N*M) sumean haun: jokainen uutettu sitaatti ajetaan RapidFuzzilla kaikkia LLM:n palauttamia `used_evidence_ids` -lähteiden sisältöjä vasten.
* Paras osuma (joka ylittää `get_lexical_fuzz_threshold` -rajan) "voittaa" ja määrittää, mihin lähteeseen sitaatti oikeasti kuuluu.
* Tämän perusteella Python kytkee `EvidenceQuoteDTO`:lle oikean `source_reference`-arvon tietokantaan.
Tämä pitää LLM-promptit ja Pydantic-skeemat "tyhminä ja turvallisina", siirtäen raskaamman relaatiologiikan turvallisesti asynkronisen Python-Workerin hartioille.

### 3.2 Audit-lokin malli
```python
class MCPAuditTraceDTO(BaseModel):
    id: str             # esim. "tavily_1a2b" tai "source_doc_abc123"
    tool_id: str        # esim. "mcp_tavily_search" tai "source_document" (yhdenmukainen koodin kenttänimen kanssa)
    # Rakenteellinen CoT (Pre-Action Reasoning) roska-hakujen estämiseksi:
    knowledge_gap: str  = Field(description="Mikä tietty fakta säännön täyttymisen todentamiseksi tällä hetkellä puuttuu?")
    search_rationale: str = Field(description="Miten valitsemasi hakutermit täyttävät tämän nimenomaisen aukon?")
    impacted_axis_names: list[str] = Field(default_factory=list) # Python täyttää käänteishaulla
```

#### 3.2.1 Firestoren 1 MiB Kokoraja ja Viittausarkkitehtuuri (StorageService)
**Kriittinen sääntö:** `MCPAuditTraceDTO` (tai mikään muukaan ajon aikainen lokitietue) **EI SAA KOSKAAN** tallentaa työkalun palauttamaa raakatekstiä (esim. ladattua Wikipedia-artikkelia tai 50-sivuisen lähde-PDF:n sisältöä) sellaisenaan tietokantaan.
**Syy:** Quorumin tietokantakerros (esim. Firestore) on rajoitettu ehdottomaan 1 MiB maksimikokoon per dokumentti (`execution` record). Raakadatan tallentaminen johtaa välittömään *Document too large* -kaatumiseen.
**Ratkaisu (Pointer-malli):** Aivan kuten Quorum käsittelee jo nykyisellään suuria lähtötiedostoja (Source Documents), MCP-työkalujen ja sisäisten RAG-hakujen on tallennettava raakadata fyysiseen tallennustilaan (Cloud Storage / lokaali levy `StorageServicen` kautta). Audit-lokiin tallennetaan pelkkä viittaus, esim. `source_uri: "gs://bucket/mcp_cache/wiki_123.txt"`. Sumean haun (Fuzzy Match) suorittava Worker lataa tekstin välimuistiin URI:n perusteella vain lukuhetkellä, pitäen tietokantatransaktion (ja koko `execution`-dokumentin) mikroskooppisen pienenä.

---

## 4. Toteutuksen Vaiheet (Implementation Tiers)

### 4.1 Koodauksen Laatuvaatimukset (Hardening.xml Yhteensopivuus)
Tämä Epic toteutetaan noudattaen täydellisesti modernia 2026 Python-arkkitehtuuria ja `c:\src\quorum\scripts\hardening.xml` -säännöstöä, **sillä poikkeuksella, että tämän Epicin arkkitehtuuriset muutokset kumoavat legacy-koodin editointikiellot** (kuten Pydantic-skeemojen lukitukset tai olemassa olevien funktioiden jäätymiset). Uutta ominaisuutta rakennettaessa:
1. **Moderni Syntaksi (Säännöt 24, 60):** Käytetään `list[str] | None` ja PEP 695 tyyppialiaksia.
2. **Fail-Fast Pydantic (Säännöt 1-11):** Käytetään tiukkaa hydratointia ja `@field_validator(mode="before")` -funktioita nolla-arvojen turvalliseen käsittelyyn.
3. **SRP ja Pienet Funktiot (Sääntö 88):** Vältetään God Methodeita. Raskas haku (N x M) siirretään Asynkroniseen Workeriin (Sääntö 34), ja koodi pidetään modulaarisena.

---

### Vaihe 1: Rakenteellinen CoT Työkalukutsuihin (Pre-Action Reasoning)
*   **Kohde:** `backend_v2/models/domain/mcp.py`
*   **Toimenpide:** Korvataan summittaiset perustelukentät rakenteellisella "Chain-of-Thought" -vaatimuksella `MCPAuditTrace`- ja `CitationExtractionItemDTO`-malleissa. Lisätään kentät `knowledge_gap` ja `search_rationale`, jotka pakottavat mallin hidastamaan ajattelua (System 2) ennen työkalun suorittamista, karsien tehokkaasti ns. "roskahakujen" määrää.

### Vaihe 2: DTO-mallien ja injektion päivitys
*   **Kohde:** `v2_core.py`, `lightweight_matrix.py`
*   **Toimenpide:** Otetaan käyttöön yllä kuvatut `EvidenceQuoteDTO` ja `RowForensicsDTO`. Päivitetään LLM:n konteksti-injektio tuottamaan `<search_result id="...">` -tägit.

### Vaihe 3: Blueprint Transformer (Käänteishaku ja Legacy Adapter)
*   **Kohde:** `backend_v2/services/blueprint.py`
*   **Toimenpide:** Koodataan logiikka, joka iteroi matriisirivien `RowForensicsDTO` läpi, lukien `is_mcp_verified` -arvot ja UUID:t suoraan ajon lokista muokkaamatta niitä lennossa.
*   **Legacy Adapter:** Koska tietokannassa on vanhoja ajoja ennen Epic 88:n DTO-uudistusta, Transformerille on koodattava *Legacy Adapter*. Jos vanha ajo käyttää vanhaa tietorakennetta (esim. UUID:t puuttuvat), Adapter hoitaa datan siirtymän kaatumatta (esim. jättämällä `evq_id`:n tyhjäksi tai generoimalla epävirallisen hashin vain katselua varten, poistaen Soft Delete -ominaisuuden kyseiseltä riviltä).

### Vaihe 4: Esityskerros (Flutter & Jinja2)
*   **Kohde:** `AtomMatrixTableWidget` (Flutter) ja `report_template.jinja2`.
*   **Toimenpide (Matriisi):** Renderöidään sitaatit tasoittain sisennetyillä listoilla. Jos `is_mcp_verified == True`, lisätään sitaatin perään suurennuslasi/tarkistusmerkki-ikoni. Implementoi `✕`-hylkäysnappi ja sen Optimistic Update -tilamuutos Riverpodissa (ks. 5.3.3).
*   **Toimenpide (PDF/Jinja2):** Jinja2-templatesta (`report_template.jinja2`) on **ehdottomasti poistettava kaikki vanha deduplikaatiologiikka (esim. `seen_quotes` -sanastot)**. Koska uusi DTO on hierarkkinen (tasot sisältävät suoraan omat sitaattinsa), template saa ainoastaan iteroida ja tulostaa litteästi uutta pintarakennetta. XAI-lokiosioon lisätään haun perustelu (`knowledge_gap` ja `search_rationale`).

---

## 5. Datan Elinkaari, API ja CRUD-politiikka (Append-Only Protocol)

Koska `EvidenceQuoteDTO` ja `MCPAuditTraceDTO` ovat luonteeltaan todistusaineistoa (Forensic Evidence), niiden elinkaari eroaa perinteisestä CRUD-mallista (Create, Read, Update, Delete). Käyttäjällä **ei ole** suoraa hallintaa tähän dataan, vaan se syntyy ja elää osana laajempaa ajoa (Execution).

### 5.1 Luominen (Create - Autonominen generointi)
Käyttäjä ei koskaan tee POST-pyyntöä luodakseen sitaatin. Sitaatit syntyvät yksinomaan tekoälyn suorittamien työnkulkujen (Workflows) aikana. Kun ajo valmistuu, taustajärjestelmä (Worker) tallentaa raakaatan (atomien `exact_quotes`, `used_evidence_ids`, `MCPAuditTrace`) pysyvästi ajon tietokantatietueeseen (`executions`-taulu) sekä tiedostojärjestelmään (`execution_trace`). `RowForensicsDTO` on **johdettu (derived) näkymä**, joka koostetaan lennossa `BlueprintTransformerissa` jokaisella raporttikyselyllä tästä raakadatasta — sitä ei tallenneta tietokantaan erikseen (ks. Liite D.1 ADR).

### 5.2 Luku ja Esittäminen (Read - ReportDataDTO & Flutter)
Esittäminen tapahtuu olemassa olevan "Report"-rajapinnan kautta (`GET /api/v2/execution/executions/{id}/report`). 
1. `BlueprintTransformer` muuntaa raa'an ajodatan (sisältäen ristiinlinkitykset) puhtaaseen esitysmuotoon (`ReportDataDTO`).
2. Flutter-asiakasohjelma (Client App V2) hakee tämän datan.
3. UI renderöi `RowForensicsDTO`:n sisällön lukutilassa. Käyttäjä näkee säännön alla tasoryhmitellyt sitaatit (esim. "Taso 4: Erinomainen") ja mahdollisen suurennuslasi-ikonin (MCP-todennettu).

### 5.3 Soft Delete ja Ihmisen Valta (Human Override)
Tiedämme (varianssitesteistä), että tekoäly tekee virheitä. Jos data on tiukan Append-Only -säännön alainen, vaarana on *Poisoning the Well* (organisaation tietokannan myrkyttyminen LLM-hallusinaatioilla). 
Forensic Sovereignty (lokin muuttumattomuus) säilytetään ilman teknologista diktatuuria **Soft Delete** -mekanismilla:
- Alkuperäistä tekoälyn `EvidenceQuoteDTO`:ta ei koskaan *poisteta* tietokannasta, eikä sen tekstiä muokata. Kryptografinen jälki siitä, mitä malli alun perin sanoi, säilyy ikuisesti.
- Käyttäjä voi kuitenkin UI:ssa merkitä sitaatin hylätyksi. Tämä on ainoa sallittu muokkaus (PUT), joka asettaa `user_rejected = True` (ja mahdollistaa `rejection_reason` kirjaamisen).
- Flutter UI piirtää tällaisen sitaatin yli punaisen viivan. Tämä palauttaa asiantuntijalle vallan (Agency) siivota tulokset tuotantoa varten joutumatta maksamaan uuden pitkän ajon kustannuksia.

#### 5.3.1 Käyttöoikeusrakenne (Authorization Model)

Sitaatin hylkäys on **forensinen veto**, ei hallinnollinen toimenpide. Siksi oikeus ei vaadi ADMIN-roolia — asiantuntija (MEMBER), joka suoritti ajon, on paras arvioimaan sitaatin osuvuuden.

| Rooli | Oikeus | Rajaus |
| :--- | :--- | :--- |
| `ROOT` | Voi hylätä minkä tahansa ajon sitaatteja | Ei rajausta |
| `ADMIN` | Voi hylätä minkä tahansa organisaation ajon sitaatteja | `execution.organization_id == user.organization_id` |
| `MANAGER` | Voi hylätä alaistensa ja omiensa ajon sitaatteja | `execution.created_by == user.uid` TAI käyttäjä kuuluu managerin tiimiin |
| `MEMBER` | Voi hylätä **vain omien ajojensa** sitaatteja | `execution.created_by == user.uid` |
| `VIEWER` | ❌ Ei oikeutta hylätä | Lukuoikeus, ei kirjoitusoikeutta |

**Turvallisuus:** Koska `user_rejected` on Append-Only Soft Delete, virheellinen hylkäys ei tuhoa dataa. Alkuperäinen sitaatti säilyy ikuisesti. ADMIN voi tarkastella audit-lokia (`rejected_by`, `rejected_at`, `rejection_reason`) ja arvioida, oliko hylkäys perusteltu.

#### 5.3.2 API-rajapinta

```
PUT /api/v2/execution/executions/{exec_id}/evidence/{evq_id}/reject

Headers:  Authorization: Bearer <token>
Body:     { "rejection_reason": "Sitaatti on irrotettu kontekstista" }

Response: 200 OK  { "status": "rejected", "evq_id": "evq_a1b2c3d4e5f6" }
Error:    403     { "detail": "Insufficient privileges or not execution owner" }
Error:    404     { "detail": "Evidence quote not found" }
```

#### 5.3.3 Optimistic UI & Riverpod (Käyttöliittymän Reaktiivisuus)
**Ongelma:** Kun käyttäjä painaa Flutter-käyttöliittymässä sitaatin kohdalla ✕-painiketta (Soft Delete), pelkkä HTTP PUT -kutsun lähettäminen backendiin ei yksinään päivitä näkymää (esim. piirrä punaista yliviivausta sitaatin yli), koska näkymän tila elää Riverpodin tilanhallinnassa. Jos tilaa ei päivitetä, käyttäjä joutuisi odottamaan koko raportin hidasta uudelleenlataamista (GET).

**Ratkaisu (Optimistic Update):** Flutter-asiakasohjelman `ExecutionController` -luokkaan (joka hallinnoi raportin tilaa) on koodattava metodi `rejectEvidenceQuote(quoteId, reason)`. 
1. Tämä metodi lähettää asynkronisen HTTP PUT -kutsun.
2. Jos API-kutsu onnistuu (200 OK), metodi luo välittömästi **immutaabelin kopion nykyisestä tilasta** (esim. `state = state.copyWith(...)`), jossa kyseisen `EvidenceQuoteDTO`:n arvo `user_rejected` asetetaan todeksi (`true`).
3. Tämä tilamuutos pakottaa Riverpodin reaktiivisesti uudelleenrenderöimään (re-render) vain kyseisen `AtomMatrixTableWidget` -solun, jolloin yliviivaus ilmestyy näytölle välittömästi (Optimistic UI) ilman raskasta API-tiedonhakua.
### 5.4 Kansainvälisyys (i18n & No-String Mandate)
Koska Quorum on kansainvälinen ohjelmistoalusta, Forensic Traceability -ominaisuuksien on skaalauduttava saumattomasti yli kielirajojen. Kieliriippumattomuus on varmistettava seuraavissa neljässä arkkitehtuurin solmukohdassa:

1. **Flutterin No-String Mandate:** Uusia käyttöliittymätekstejä (esim. *"Asiantuntijan hylkäämä"*, *"Sitaatti varmennettu ulkoisella haulla"*) ei saa koskaan kovakoodata `atom_matrix_table_widget.dart` -tiedostoon. Kaikki uudet tekstit on vietävä `.arb`-käännöstiedostoihin (esim. `app_en.arb`, `app_fi.arb`) ICU-muodossa.
2. **PDF-moottorin (Jinja2) monikielisyys:** Kuten Flutter, myös PDF-moottori on käännösriippuvainen. Jinja-templateissa (`report_template.jinja2`) ei saa olla kovakoodattua kieltä, vaan kaikki visuaaliset lisäykset on ajettava käännösfiltterin läpi (esim. `{{ _("rejected_by_user") }}`).
3. **Kone-Kone -kommunikaatio (Didactic DLQ):** Kun sumea haku epäonnistuu ja Python palauttaa `SemanticEvidenceErrorin` takaisin LLM:lle, tämän **virheilmoituksen on oltava LLM:n järjestelmäpromptin kielellä** (yleensä englanti). Vaikka käyttäjä analysoisi ruotsinkielistä dokumenttia, DLQ-promptin on oltava englanniksi, jotta se ei riko LLM:n kognitiivista kontekstia.
4. **Semantic Reasoning (Perustelujen kieli):** PromptBlockeissa on pakotettava LLM tuottamaan asiantuntijalle suunnatut perustelut (esim. miksi tämä sitaatti todistaa säännön täyttymisen) **aina kohdekielellä** (käyttäjän UI-kieli), ei automaattisesti käsiteltävän dokumentin kielellä. Tämä takaa asiantuntijalle kykenevyyden tehdä aidosti tietoinen Soft Delete -päätös riippumatta lähdeaineiston kielestä.

**Sisäinen toteutus (Append-Only):** Endpoint ei muokkaa olemassa olevaa dataa. Se appendoi uuden `evidence_override` TraceEvent -tapahtuman ajon `execution_trace`-listaan:
```python
TraceEvent(
    step_name="evidence_override",
    event_type="evidence_override",
    content={
        "evq_id": "evq_a1b2c3d4e5f6",
        "user_rejected": True,
        "rejection_reason": "Sitaatti on irrotettu kontekstista",
        "rejected_by": current_user.uid,
        "rejected_at": "2026-06-28T13:30:00Z"
    }
)
```
`BlueprintTransformer.build_report_dto()` lukee nämä tapahtumat ja asettaa vastaavan `EvidenceQuoteDTO.user_rejected = True` koostamisvaiheessa.

### 5.4 Archivist-tietokannan RAG-integraatio (Y-Funnel Extraction)
Kun `EvidenceQuoteDTO` viedään Archivist-matriisiin (esim. organisaation pysyvään muistiin kerätty tieto), se uutetaan (Extract) alkuperäisestä ajosta taustaprosessissa. 
Tässä kohtaa "Soft Delete" pelastaa järjestelmän: Agentit rikastavat tietokantaa ajojen sivutuotteena, mutta ne **suodattavat tiukasti pois** kaikki sitaatit, joissa `user_rejected == True`. Näin varmistetaan, että tulevat RAG-haut käyttävät vain asiantuntijan hiljaisesti hyväksymää, korkean luotettavuuden dataa.

---

## 6. Onnistumisen Kriteerit (Quality Gates)
- [ ] **Universaali Forensic Sovereignty:** Jokainen tekoälyn esittämä väite koko järjestelmässä tallentuu `EvidenceQuoteDTO`-muodossa. Sisäisillä väitteillä on suora `source_reference`, ja ulkoisilla hauilla on katkeamaton jälki: `Haku -> Tracen ID -> Evidence Quote -> Matriisin sääntö`. Nämä voidaan myöhemmin parsia suoraan Archivist-tietokantaan RAG-hakuja varten.
- [ ] **Flat UI:** Flutter-koodissa ja Jinja2-templatessa ei ole lainkaan for-luuppeja, jotka yrittäisivät mäpätä hakuja matriiseihin. Ne vain tulostavat valmiit DTO-listat.
- [ ] **Fail-Fast & Didaktinen DLQ (Ei hiljaisia pudotuksia):** Jos LLM hallusinoi aliaksen, jota ei löydy Pythonin sanakirjasta, sitä EI pudoteta hiljaa. Pydantic laukaisee virheen, joka lähetetään DLQ/Retry-kiertoon (EPIC 81). Ikuisen DLQ-silmukan (Deadlock) ja "pakotetun valehtelun" estämiseksi virheilmoituksen on oltava dynaaminen ja sisällettävä aina *Escape Hatch*: *"Kausaalinen integriteettivirhe: Viittasit olemattomaan lähteeseen <<QRM-SRC-99>>. Käytettävissäsi olevat lähteet ovat VAIN: [<<QRM-SRC-1>>]. JOS nämä lähteet eivät oikeasti sisällä väitettäsi, PALAUTA TYHJÄ LISTA []. Älä keksi lähteitä."* Tämä katkaisee deadlockin välittömästi antamalla mallille luvan perääntyä sen sijaan, että se yrittäisi pakottaa keksityn faktan johonkin sallituista lähteistä.
- [ ] **Mekaaninen Totuus (Ei XAI-teatteria):** Pelkkä validi alias ei riitä todennukseen. Backend suorittaa sumean merkkijonohaun (Fuzzy Text Matching / RapidFuzz Levenshtein) LLM:n poimimalle sitaatille suhteessa lähdedokumenttiin. Typografia sallitaan, parafraaseja ei. Vain mekaanisen (> 90%) osuman myötä `is_mcp_verified` voi muuttua todeksi.
- [ ] **Kausaalisen Orpouden Esto (Soft Delete Cascading):** Jos tason kaikki todisteet kumotaan asiantuntijan toimesta (`user_rejected == True`), itse matriisin arvosana tai taso on liputettava (UI/PDF) selkeällä varoituksella, ettei korkea arvosana jää dokumenttiin ilman kausaalisia perusteita.

---

## 7. Esityskerros ja UI-pariteetti (Tulostus)
Unified Reporting -strategian ja Flat MVC -mandatin mukaisesti esityskerrokset (Flutter ja PDF) ovat "tyhmiä renderöijiä". Kaikki älykkyys ja datan ryhmittely tapahtuu Pythonissa (`RowForensicsDTO`).

### 7.1 Tulostuksen uusi asettelu (Matrix Summary)
* **Sitaattien ryhmittely (Evidence-First UI):** Litteän listan sijaan `Lainaukset (quotes)` -sarake tulostaa sitaatit ryhmiteltynä niiden tason alle (esim. väliotsikko: **[Taso 5: Itsekriittinen]** ja sen alla tähän tasoon liittyvät `EvidenceQuoteDTO` -sitaatit).
* **Lähdeviitteet ja XAI-ikonit:** Jokaisen sitaatin perässä/alla tulostetaan `source_reference`. Jos sitaatilla on `is_mcp_verified == True`, sen viereen tulostetaan vihreä ✅ "MCP-Varmennettu" -teksti (tai ikoni).
* **Yliviivaus (Soft Delete):** Jos asiantuntija on hylännyt sitaatin (`user_rejected == True`), tulostusmoottori piirtää tekstin yliviivattuna (Flutterissa `TextDecoration.lineThrough`, PDF:ssä `<del>`-tägi). Näin raportin lukija näkee täydellisen audit-lokin myös tekoälyn virheistä, jotka ihminen on kumonnut.
* **Kaskadoituva liputus (Kausaalisen Orpouden esto):** Jos säännön tason *kaikki* sitaatit on hylätty (kaikki listan alkiot ovat `user_rejected == True`), käyttöliittymä renderöi myös itse arvosanan viereen varoitusikonin ⚠️ *"Arvosanan perusteet kumottu asiantuntijan toimesta"*. Näin vältetään tila, jossa arvosana (esim. Taso 4/5) jää ilmaan ilman todisteita. Ajoa ei tarvitse uusia raskaasti backendissä, mutta lukijaa varoitetaan heti logiikan katkeamisesta.
* **100 % Pariteetti:** Kummassakin käyttöliittymässä (PDF ja Flutter) tapahtuu tismalleen samat yksinkertaiset ehtolauseet (IF verified THEN ikoni, IF rejected THEN yliviivaus, IF all_rejected THEN varoitus). Käyttöliittymä ei koskaan suorita luuppeja alkuperäistä dataa etsiäkseen.

### 7.2 Soft Delete -käyttöliittymä (Evidence Rejection UI)
Soft Delete -toiminnallisuus on saavutettavissa vain ajon raporttilistanäkymässä (Matrix Summary). Käyttöliittymä noudattaa "minimaalisuus + peruuttamattomuuden selkeys" -periaatetta.

#### 7.2.1 Sitaatin hylkäysinteraktio (Flutter)

Jokaisen `EvidenceQuoteDTO`-sitaatin vieressä on pieni punainen ✕-painike ("Hylkää"), joka näkyy **vain** käyttäjille, joilla on kirjoitusoikeus (MEMBER+ omiin ajoihinsa, ADMIN+ kaikkiin). VIEWER-roolille painike ei renderöidy.

**Interaktiosekvenssi:**
1. Käyttäjä hover:aa sitaatin päälle → ✕-painike tulee näkyviin (opacity-animaatio)
2. Käyttäjä painaa ✕ → avautuu `AlertDialog`:
   - **Otsikko:** "Hylkää sitaatti?"
   - **Sisältö:** Sitaatin teksti (enintään 100 merkkiä) kursiivilla
   - **Syy-kenttä:** `TextField` (valinnainen) — placeholder: *"Miksi sitaatti ei ole osuva? (valinnainen)"*
   - **Toimintopainikkeet:**
     - "Peruuta" (harmaa) → sulkee dialogin, ei muutosta
     - "Hylkää" (punainen) → kutsuu API-endpointia `PUT .../evidence/{evq_id}/reject`
3. Onnistuneen API-kutsun jälkeen:
   - Sitaatti saa välittömästi yliviivauksen (`TextDecoration.lineThrough`, punainen opacity 60%)
   - ✕-painike katoaa (hylkäys on peruuttamaton)
   - Jos kaikki tason sitaatit on nyt hylätty → ⚠️-varoitus ilmestyy arvosanan viereen (Optimistic UI -päivitys)
4. Virhetilanteessa → `SnackBar`: *"Sitaatin hylkäys epäonnistui. Yritä uudelleen."*

#### 7.2.2 Hylätyn sitaatin renderöinti (Lukutila)

| Tila | Flutter | PDF (Jinja2) |
| :--- | :--- | :--- |
| Normaali sitaatti | Musta teksti, ei ikonia | Normaali fontti |
| MCP-varmennettu | Musta teksti + ✅ vihreä ikoni | Teksti + `✅ MCP-Varmennettu` |
| Hylätty | ~~Yliviivattu~~ punainen teksti, ✕-painike piilotettu | `<del style="color:#999">teksti</del>` |
| Hylätty + syy | ~~Yliviivattu~~ + Tooltip: syy-teksti | `<del>teksti</del>` + pieni kursiivikommentti |
| Kaikki hylätty (taso) | Arvosanan vieressä ⚠️ Tooltip | ⚠️ "Arvosanan perusteet kumottu" |

#### 7.2.3 PDF-raportti (Jinja2)

PDF on staattinen tuloste — siinä ei ole interaktiivista ✕-painiketta. PDF renderöi hylätyt sitaatit yliviivattuina `<del>`-tägillä ja näyttää `rejection_reason`:n pienenä kursiivitekstinä sitaatin alla. Tämä on pelkkää lukutilaa.

#### 7.2.4 Peruuttamattomuus

Soft Delete on **yksisuuntainen operaatio**. Hylkäystä ei voi perua UI:sta. Tämä on tietoinen arkkitehtuurinen päätös:
- **Perustelu:** Forensinen audit-loki vaatii, että jokainen tapahtuma on muuttumaton. "Peru hylkäys" -toiminto loisi monimutkaisen tapahtumaketjun (override → undo_override → re-override), joka vaikeuttaisi lokin tulkintaa.
- **Turvaverkko:** Jos hylkäys on virheellinen, ADMIN voi luoda kokonaan uuden ajon samalla konfiguraatiolla. Alkuperäinen data (mukaan lukien hylätty sitaatti) säilyy vanhassa ajossa ikuisesti.

---

## 8. Toteutus ja Siirtymästrategia (Migration & Rollout)
Epic 88 on arkkitehtuurinen **Breaking Change**, joka korvaa täysin sen, miten Quorum-järjestelmän matriisiarvioinnit, promptit ja tulosteputki (UI/PDF) toimivat. Tuotannon rikkomisen välttämiseksi siirtymä toteutetaan rinnakkaisena "V2 Moottorina" (Shadow Mode).

### Vaihe 1: Rinnakkaiset Tietomallit (Domain Isolation)
* Luodaan uudet `EvidenceQuoteDTO` ja `LevelQuotesDTO` -mallit koskematta nykyisiin (legacy) DTO-malleihin (kuten `EvidenceItem`).
* Koodataan "Eteenpäin kytketty konsistenssi" (Laiskuuden esto) ja "Didaktinen DLQ" suoraan näiden uusien mallien Pydantic-validaattoreihin.

### Vaihe 2: Rinnakkainen Työnkulku (V2 Engine)
* Rakennetaan taustajärjestelmään uusi työnkulkuputki (esim. `MatrixEvaluatorV2`), joka injektoi "Voileipä-aliakset" (`<<QRM-SRC-x>>`) ja hyödyntää uutta "Evidence-First Forcing" -promptauslogiikkaa. 
* Vanha järjestelmä jatkaa tuotannon palvelemista nykyisillä säännöillä.

### Vaihe 3: Varianssitestaus ja Varmennus (Shadow Testing)
* Käytetään järjestelmän E2E-skriptejä (esim. `run_e2e_variance_test.py`) testaamaan uutta V2-moottoria eristetysti.
* Mitataan ja todennetaan (Mekaaninen Totuus), että hallusinaatiot ja "Lost in the Middle" -virheet putoavat nollaan ilman ikuisia DLQ-looppeja.

### Vaihe 4: Esityskerroksen Päivitys ja Tuotannon Kytkös (Hard Cutover)
* Päivitetään Flutter-käyttöliittymä ja PDF:n Jinja2-templatet tukemaan ryhmiteltyä näkymää, Soft Delete -hylkäyksiä ja XAI-ikoneita.
* **Ei Legacy-fallbackia:** Kun 100 % visuaalinen pariteetti ja stabiilius on varmistettu, ohjataan tuotannon liikenne täysin V2-moottoriin. Koodikantaan **ei rakenneta eikä jätetä minkäänlaista fallback-logiikkaa (taaksepäin yhteensopivuutta) vanhoille ajoille**. Vanhat DTO-mallit ja niihin liittyvä purkulogiikka poistetaan koodikannasta armottomasti (Clean Architecture -mandatti). Mahdolliset vanhat raportit on luettavissa staattisista PDF-arkistoista, backend ei yritä tukea niitä lennosta.

---

## Liite A: Koodivaikutusanalyysi (System 2 Deep Dive — Luku 2)
Tämä osio mäppää jokaisen luvun 2 arkkitehtuurisen konseptin tarkkaan koodikantaan ja erittelee, mitä olemassa olevia tiedostoja muutetaan, mitä uutta luodaan ja miksi.

### A.1 Luku 2.1 — LLM ei saa rakentaa graafia itse
**Nykytila koodissa:** Tämä periaate ON JO toteutettu. `BlueprintTransformer` (`backend_v2/services/blueprint.py`, rivit 1049–1076) rakentaa käänteishaun `used_evidence_ids` → `impacted_axis_names` deterministisesti Pythonissa. LLM:n tehtäväksi jätetään vain `used_evidence_ids`-listan täyttö atomikohtaisesti (`backend_v2/models/dtos/lightweight_matrix.py`, rivi 267).
**Muutostarve:** Ei suoraa koodimuutosta. Periaate vahvistettu.
**Falsifikaatio:** BlueprintTransformerin `extract_evidence_ids()` -funktio (rivi 1053) iteroi `payload`-dictejä rekursiivisesti, mikä tarkoittaa, että se ei ole sidottu mihinkään tiettyyn DTO-rakenteeseen. Tämä on hyvä: uusi `EvidenceQuoteDTO` toimii samalla mekanismilla, kunhan sen `used_mcp_ids` -kenttä nimetään uudelleen `used_evidence_ids`ksi **TAI** `extract_evidence_ids` laajennetaan etsimään myös `used_mcp_ids` -avainta.

> **Toimenpide:** `backend_v2/services/blueprint.py` — Laajenna `extract_evidence_ids()` (rivi 1055) etsimään sekä `used_evidence_ids` että `used_mcp_ids` avaimia, tai yhdenmukaista kenttänimi uudessa DTO:ssa.

---

### A.2 Luku 2.2 — Chunk-tasoinen Voileipä-injektio
**Nykytila koodissa:** `mcp_tool_loop.py` (rivi 556) injektoi hakutulokset `<search_result id="tavily_xxxx">` -tägeihin. Nykyinen koodi **EI pilko** tuloksia chunkkeihin. Koko `response_summary` injektoidaan yhtenä palana. Kuitenkin Tavily palauttaa yleensä lyhyen `answer`-tiivistelmän (ei kokonaista 15k-tokenin dokumenttia), joten "Lost in the Middle" -riski on Tavilyn tapauksessa teoreettinen.
**Falsifikaatio:** Varsinainen riski kohdistuu sisäisiin PDF-dokumentteihin (käyttäjän lähdeaineisto), jotka injektoidaan LLM:n kontekstiin kokonaisuudessaan `source_context`-parametrina (`mcp_tool_loop.py`, rivi 271). Näissä dokumenteissa EI OLE mitään ID-tägiä. LLM saa ne puhtaana raakakekstinä system/user-viestissä.
**Kriittinen havainto:** Chunkkaaminen ja aliaksointi ovat relevantteja **kahdessa eri kohdassa**:
1. **MCP-hakutulokset (ulkoiset):** `_build_tool_evidence_message()` ja Phase 2 -injektio (rivit 552–564). Näihin voi lisätä `<<QRM-SRC-x>>` aliakset suoraan.
2. **Lähde-PDF:t (sisäiset):** Nämä injektoidaan LLM:n viesteihin orkestraattoritasolla (`backend_v2/services/orchestrator/strategies/llm.py`). Chunkkaus ja aliaksointi edellyttävät uuden esikäsittelyfunktion luomista tänne.

> **Arkkitehtuurinen yhdistäminen (Unified Source Pipeline):** Koodianalyysi paljasti, että sisäiset lähdedokumentit (PDF) ja ulkoiset hakutulokset (MCP/Tavily) kulkevat nykyisin **täysin eri koodipolkuja** pitkin ja päätyvät LLM:lle eri muodoissa. Epic 88:n jälkeen molemmat TÄYTYY prosessoida **identtisellä logiikalla ja samalla ohjelmistolla**:
>
> **Uusi tiedosto:** `backend_v2/services/mcp/alias_registry.py` — Keskitetty rekisteri, joka hallitsee kaikkia lähteitä (sisäiset PDF:t JA ulkoiset MCP-haut) yhdellä juoksevalla `<<QRM-SRC-N>>` -laskurilla. Jokainen lähde (olipa se käyttäjän PDF tai Tavily-hakutulos) rekisteröidään tänne ja saa yksilöllisen aliaksen.
>
> **Yhteinen injektiofunktio:** `alias_registry.py` tarjoaa funktion `wrap_source_chunks(text: str, source_id: str) -> list[str]`, joka:
> 1. Rekisteröi lähteen ja antaa sille aliaksen (`<<QRM-SRC-N>>`)
> 2. Pilkkoo tekstin n. 1000–1500 tokenin paloihin
> 3. Käärii jokaisen palan `<search_result ID="<<QRM-SRC-N>>" chunk="M/T">` -tägeihin
>
> **Muutettavat kutsupaikat:**
> - `backend_v2/services/mcp/mcp_tool_loop.py` (rivit 552–564): Phase 2 -injektio kutsuu `wrap_source_chunks()` MCP-hakutuloksille
> - `backend_v2/services/orchestrator/strategies/llm.py`: Lähde-PDF:ien injektio kutsuu **samaa** `wrap_source_chunks()` -funktiota
>
> **Seuraus:** LLM näkee yhtenäisen virran identtisesti muotoiltuja `<search_result>` -tageja riippumatta siitä, onko lähde sisäinen PDF vai ulkoinen verkkohaku. Reverse Lookup, Fuzzy Match ja `is_mcp_verified` -logiikka toimivat identtisesti molemmille lähdetyypeille `BlueprintTransformerissa`.
>
> **Yhtenäinen tallennus (Unified Storage):** Injektioputken yhdistäminen edellyttää, että myös **tallennus** on yhdenmukainen. Nykyisin MCP-hakutulokset tallennetaan rakenteisesti `MCPAuditTrace`-malliin (`FrozenContext.mcp_tool_audit`), mutta lähde-PDF:t ovat pelkkää raakakekstiä (`forensic_input_path`-tiedostopolku ilman Pydantic-rakennetta). Jos `BlueprintTransformer` joutuu Reverse Lookupissa hakemaan dataa kahdesta eri paikasta, yhtenäisyys hajoaa.
>
> **Ratkaisu:** `MCPAuditTrace`-mallia laajennetaan (tai se yleistetään) kattamaan **kaikki** lähteet. Sisäinen PDF-dokumentti rekisteröidään ajon alkaessa samaan `FrozenContext.mcp_tool_audit` -listaan (tai uudelleennimettyyn `source_audit_traces` -listaan) omana `MCPAuditTrace`-tietueenaan, jossa `tool_id = "source_document"`, `response_summary` sisältää raakadatan ja `id` on aliaksen käänteisavain. Näin kaikki lähteet — sisäiset ja ulkoiset — elävät **samassa Pydantic-rakenteessa, samassa tietokantakentässä, ja BlueprintTransformer käsittelee ne yhdellä for-luupilla.**
>
> **Laajennettavuustakuu (Open/Closed Principle):** Koko putki (injektio → tallennus → reverse lookup → fuzzy match → esitys) on **täysin lähdetyypistä riippumaton**. `tool_id`-kenttä toimii ainoana diskriminaattorina. Uuden lähdetyypin lisääminen tulevaisuudessa (esim. RAG-haku Archivist-kannasta, Excel-liite, API-kutsu ulkoiseen rekisteriin) vaatii **vain yhden asian**: uuden `tool_id`-arvon (esim. `"archivist_rag"`, `"excel_attachment"`). Muu putki (aliaksointi `<<QRM-SRC-N>>`, chunkkaus, Pydantic-tallennus, BlueprintTransformerin reverse lookup ja fuzzy match) toimii automaattisesti ilman yhtäkään koodimuutosta. **Kovakoodattua Tavily- tai PDF-spesifiä logiikkaa EI SAA kirjoittaa putken sisälle.** Hard Cutover -vaiheessa `MCPAuditTrace` uudelleennimetään yleisemmäksi (esim. `SourceAuditTrace` tai `ForensicSourceTrace`), jotta nimi ei johda seuraavaa kehittäjää harhaan.

---

### A.3 Luku 2.3 — Kunniallinen Ulospääsy (Escape Hatch)
**Nykytila koodissa:** `LightweightExtractionAtom.exact_quotes` (rivi 153 `lightweight_matrix.py`) ja `AtomEvaluationItemDTO.exact_quotes` (rivi 272) käyttävät molemmat `default_factory=list`. Olemassa oleva Pydantic-kenttä SALLII tyhjän listan, mutta `description`-attribuutti **ei sisällä** eksplisiittistä psykologista lupaa ("tyhjä lista on oikea vastaus").
**Muutostarve:** Kyllä, mutta kyseessä on puhdas `description`-tekstin päivitys (Prompt Engineering).

> **Toimenpide:** `backend_v2/models/dtos/lightweight_matrix.py` — Lisää `exact_quotes`-kentän `description`-attribuuttiin lause: *"Jos sääntöä tukevia todisteita ei löydy, palauta TÄYSIN TYHJÄ LISTA []. Tyhjä lista on oikea vastaus."* Sama muutos: `backend_v2/models/dtos/evaluation_steps.py`.

---

### A.4 Luku 2.4 — Negatiiviset Rajoitteet
**Nykytila koodissa:** Nykyisessä koodissa EI OLE `Forward-Consistency Validator` -mekanismia (se oli vain Epic-dokumentissa ehdotettu). Sitä ei siis tarvitse poistaa.
**Muutostarve:** Ei koodimuutosta. Tämä kohta on puhtaasti arkkitehtuurinen linjaus siitä, mitä EI SAA toteuttaa. Kuvataan prompti-ohjauksena Escape Hatchin rinnalla (Luku 2.3).

---

### A.5 Luku 2.5 — Deterministinen Käänteishaku (Reverse Lookup)
**Nykytila koodissa:** Tämä mekanismi ON JO osittain koodissa. `BlueprintTransformer` (`blueprint.py`, rivit 1049–1076) suorittaa käänteishaun `used_evidence_ids` → `impacted_axis_names`. Mutta:
1. **Puuttuu:** Aliaksien käänteismuunnos (`<<QRM-SRC-x>>` → UUID). Tätä tarvitaan vasta kun Luku 2.2:n aliaksointi on toteutettu.
2. **Puuttuu:** `is_mcp_verified`-kentän asettaminen. Nykyinen `MatrixScorecardRowDTO` (`v2_core.py`, rivi 834) ei tunne tällaista kenttää.
3. **Olemassa:** `impacted_axis_names`-logiikka toimii jo täydellisesti.

> **Toimenpide 1:** `backend_v2/models/v2_core.py` (`MatrixScorecardRowDTO`, rivi 834) — Lisää kenttä `is_mcp_verified: bool = False`.
> **Toimenpide 2:** `backend_v2/services/blueprint.py` (rivit 1049–1076) — Laajenna Reverse Lookup -logiikkaa: Jos `used_evidence_ids` sisältää aliaksen, käännä se UUID:ksi sanakirjasta ja aseta `is_mcp_verified = True`.
> **Toimenpide 3:** `backend_v2/services/blueprint.py` — Lisää Fuzzy Match -tarkistus (Luku 2.8) ennen `is_mcp_verified = True` -asetusta.

---

### A.6 Luku 2.6 — Kognitiivinen Kitka (knowledge_gap & search_rationale)
**Nykytila koodissa:** `CitationExtractionItemDTO` (`backend_v2/models/domain/mcp.py`, rivi 100) sisältää `reasoning`-kentän (max 150 merkkiä). `MCPAuditTrace` (`v2_core.py`, rivi 589) sisältää saman kentän. **Kenttiä `knowledge_gap` ja `search_rationale` EI OLE koodissa.** Nykyinen `reasoning` on vapaa yhden lauseen kenttä, joka sallii "Systeemi 1" -tason geneerisen selityksen.
**Iteraatiokatto:** `MAX_TOOL_CALLS_PER_STEP = 3` (`mcp_tool_loop.py`, rivi 39) ON JO olemassa. Tämä estää ikuiset hakusilmukat kooditasolla.

> **Toimenpide 1:** `backend_v2/models/domain/mcp.py` (`CitationExtractionItemDTO`, rivi 100) — Korvaa `reasoning: str` kahdella erillisellä kentällä: `knowledge_gap: str` ja `search_rationale: str`.
> **Toimenpide 2:** `backend_v2/models/v2_core.py` (`MCPAuditTrace`, rivi 581) — Lisää kentät `knowledge_gap: str = ""` ja `search_rationale: str = ""` (olemassa oleva `reasoning` säilytetään taaksepäin yhteensopivuutta varten siirtymävaiheessa, siivotaan Hard Cutoverissa).
> **Toimenpide 3:** `backend_v2/services/mcp/mcp_tool_loop.py` (`_execute_tavily_search`, rivi 145) — Välitä uudet kentät `MCPAuditTrace`-konstruktoriin.

---

### A.7 Luku 2.7 — Evidence-First Forcing
**Nykytila koodissa:** Nykyinen `AtomEvaluationItemDTO` (`lightweight_matrix.py`, rivi 251) määrittelee kentät tässä järjestyksessä: `atom_id`, `used_evidence_ids`, `extracted_facts`, `exact_quotes`, `internal_logic_en`, `status`, `counter_quote`, `semantic_reasoning`, `contextual_override`... Eli `exact_quotes` ON jo ennen `status`-kenttää (arvosana). Tämä on hyvä! Mutta `LightweightExtractionAtom` (rivi 137) noudattaa samaa järjestystä.
**Falsifikaatio:** Evidence-First Forcing toimii vain, jos LLM generoi JSON:ia token kerrallaan vasemmalta oikealle. Nykyiset mallit (GPT-4o, Gemini) generoivat JSON:ia rakenteellisesti avain kerrallaan ylhäältä alas. Kenttäjärjestys Pydantic-mallissa todella vaikuttaa LLM:n generointijärjestykseen, koska JSON-skeema säilyttää kenttäjärjestyksen.
**Kriittinen havainto:** Vaikka `exact_quotes` on jo ennen `status`-kenttää, arvosanaa ei suoraan vastaa mikään nykyinen yksittäinen kenttä. Pisteytys tapahtuu aggregaattitasolla `BlueprintTransformerissa`, ei atomitasolla LLM:n generoimana. Tämä tarkoittaa, että Evidence-First Forcing on nykyarkkitehtuurissa **luonnostaan toteutettu**: LLM uuttaa todisteita atomitasolla, ja Python laskee pisteet jälkikäteen.

> **Toimenpide:** Ei välitöntä koodimuutosta. Arkkitehtuurin nykyinen rakenne (LLM uuttaa atomit, Python pisteyttää) toteuttaa Evidence-First Forcingin luonnostaan.

---

### A.8 Luku 2.8 — XAI-teatterin Esto (Fuzzy Match)
**Nykytila koodissa:** `AnchorValidationService` (`backend_v2/services/orchestrator/anchor_validation_service.py`, rivi 14) ON JO olemassa ja sisältää:
1. `normalize_text_with_mapping()` — Poistaa diakriittiset merkit, HTML-tägit, välimerkit ja whitespace-merkit.
2. `strict_match()` — Normalisoitu substring-haku.
3. `calculate_fuzzy_score()` — RapidFuzz-pohjainen sumea merkkijonohaku.
Tämä palvelu on jo käytössä `integrity.py` hookissa (`_is_hallucinated()`, rivi 114) ja `mcp_tool_loop.py` korjauslogiikassa (rivi 463).
**Hyvä uutinen:** Varmennus-infrastruktuuri on jo rakennettu. Sitä EI tarvitse kirjoittaa alusta asti.
**Kriittinen havainto:** Nykyinen `integrity.py` hook tarkistaa sitaatit **sisäistä** lähdetekstiä vasten. Se EI tarkista ulkoisista MCP-hauista peräisin olevia sitaatteja. Epic 88:n `is_mcp_verified` vaatii, että Fuzzy Match suoritetaan myös MCP-hakutuloksen raakadataa vasten.

> **Toimenpide 1:** `backend_v2/services/blueprint.py` — Reverse Lookup -vaiheessa (rivit 1049–1076) lisää kutsu `AnchorValidationService.calculate_fuzzy_score()`, joka vertaa LLM:n palauttamaa `text`-kenttää alkuperäisen MCP-hakutuloksen `response_summary`-kenttään. Aseta `is_mcp_verified = True` vain jos osuma ylittää kynnysarvon.
> **Toimenpide 2:** Tarvitaan pääsy alkuperäiseen hakutuloksen raakadataan Blueprint-vaiheessa. Tämä data on jo tallessa `MCPAuditTrace.response_summary`-kentässä (`FrozenContext.mcp_tool_audit`), joten uusia tietokantahakuja ei tarvita.

---

### A.9 Yhteenveto — Muutostarpeet tiedostoittain

| Tiedosto | Muutos | Epic-luku |
| :--- | :--- | :---: |
| `backend_v2/models/domain/mcp.py` | `CitationExtractionItemDTO`: `reasoning` → `knowledge_gap` + `search_rationale` | 2.6 |
| `backend_v2/models/v2_core.py` | `MCPAuditTrace`: Lisää `knowledge_gap`, `search_rationale` | 2.6 |
| `backend_v2/models/v2_core.py` | `MatrixScorecardRowDTO`: Lisää `is_mcp_verified: bool` | 2.5 |
| `backend_v2/models/dtos/lightweight_matrix.py` | `exact_quotes` description: Lisää Escape Hatch -ohje | 2.3 |
| `backend_v2/models/dtos/evaluation_steps.py` | `exact_quotes` description: Lisää Escape Hatch -ohje | 2.3 |
| `backend_v2/services/mcp/mcp_tool_loop.py` | Phase 2 injektio: kutsuu `alias_registry.wrap_source_chunks()` | 2.2 |
| `backend_v2/services/mcp/alias_registry.py` | **[UUSI]** Yhtenäinen lähderekisteri ja chunkkaus (PDF + MCP samalla logiikalla) | 2.2 |
| `backend_v2/services/orchestrator/strategies/llm.py` | Lähde-PDF injektio: kutsuu **samaa** `alias_registry.wrap_source_chunks()` | 2.2 |
| `backend_v2/services/blueprint.py` | `extract_evidence_ids()`: Tuki `used_mcp_ids`-avaimelle | 2.1 |
| `backend_v2/services/blueprint.py` | Reverse Lookup: Aliaksen käännös + `is_mcp_verified` + Fuzzy Match | 2.5, 2.8 |
| `backend_v2/services/mcp/mcp_tool_loop.py` | `_execute_tavily_search`: Uudet CoT-kentät MCPAuditTraceen | 2.6 |

### A.10 Falsifikaatio: Mitä tämä analyysi saattoi missata?
1. **Seed Data:** Jos `MCPAuditTrace`-malliin lisätään uusia pakollisia kenttiä (`knowledge_gap`, `search_rationale`), olemassa olevat testien seed-datat ja `seed_data.json` saattavat rikkoutua. Kentille ON annettava `default=""` -arvo.
2. **Flutterin parsinta:** Kaikki `MatrixScorecardRowDTO`-kenttien muutokset on peilattava Dartin vastaavaan malliin (`client_app_v2/lib/models/`). `is_mcp_verified` on lisättävä sinne ennen Hard Cutoveria.
3. **Testikattavuus:** `test_blueprint.py` sisältää jo testin `used_evidence_ids` → `impacted_axis_names` -mäppäykselle (rivi 1586). Tämä testi ON päivitettävä kattamaan myös aliaksienkäännös ja `is_mcp_verified`-asetus.

---

## Liite B: Koodivaikutusanalyysi (System 2 Deep Dive — Luku 3: Tietomallit)
Tämä osio mäppää jokaisen luvun 3 ehdotetun Pydantic-mallin todelliseen koodikantaan, seuraa koko datavirran (LLM → DTO → tietokanta → BlueprintTransformer → UI/PDF) ja erittelee tarkat muutostarpeet.

### B.1 `EvidenceQuoteDTO` — Missä se korvaa nykyisen rakenteen?

**Nykytilan datavirta (sitaattien kulku koodissa):**
1. LLM generoi `exact_quotes: list[str]` — **litteänä merkkijonolistana** — osana `AtomEvaluationItemDTO` -mallia (`lightweight_matrix.py`, rivi 272) tai `StepDTOStrict` -mallia (`evaluation_steps.py`, rivi 66).
2. Hook `integrity.py` (`_is_hallucinated()`, rivi 114) validoi jokaisen sitaatin fuzzy-matchilla lähdetekstiä vasten ja pudottaa hallusinaatiot.
3. `BlueprintTransformer` (`blueprint.py`, rivit 430–459) nostaa (hoist) validoidut sitaatit atomeilta ja litistää ne yksinkertaiseksi `quotes_list: list[str]` -listaksi `MatrixScorecardRowDTO`:lle (rivi 893 `v2_core.py`).
4. `ReportDataDTO` (rivi 951) sisältää `MatrixScorecardRowDTO` -listoja, jotka Flutter/PDF lukee.

**Kriittinen havainto:** Sitaatit ovat nykyisin **pelkkiä merkkijonoja** (`list[str]`) koko putken läpi. Niillä ei ole ID:tä, ei `source_reference`-kenttää, ei `user_rejected`-tilaa, ei `is_mcp_verified`-lippua. Epic 88:n `EvidenceQuoteDTO` lisää kaikki nämä — mikä tarkoittaa, että **jokainen sitaattia käsittelevä koodi on päivitettävä.**

**Muutokset tiedostoittain:**

> **1. LLM:n tuloste (Generointivaihe):**
> - `backend_v2/models/dtos/lightweight_matrix.py` (`AtomEvaluationItemDTO`, rivi 272): Nykyinen `exact_quotes: list[str]` korvataan kenttäryhmällä: `exact_quotes: list[str]` säilyy (LLM generoi litteän listan, koska sille EI saa antaa rikasta objektia), mutta lisätään `used_mcp_ids: list[str]` (olemassa jo rivillä 267 — ✅ ei muutosta) ja `source_document_ids: list[str]` (olemassa jo rivillä 63 `evaluation_steps.py`ssa — ✅ ei muutosta).
> - `backend_v2/models/dtos/evaluation_steps.py` (`StepDTOStrict`, rivi 66): Sama periaate.
>
> **Falsifikaatio (Kriittinen):** LLM EI SAA generoida `EvidenceQuoteDTO`-objekteja suoraan. LLM on stokastinen generaattori; jos sille annetaan monimutkainen nested-skeema (`id`, `source_reference`, `user_rejected`, `is_mcp_verified`), se alkaa hallusinoida arvoja. LLM:n tulee generoida edelleen yksinkertaista `list[str]` + `list[str]` (sitaatit + lähde-ID:t). **`EvidenceQuoteDTO` syntyy vasta Pythonissa** BlueprintTransformer-vaiheessa, kun litteät listat yhdistetään deterministisesti rikkaaksi objektiksi.

> **2. Validointivaihe (Integrity Hook):**
> - `backend_v2/hooks/integrity.py` (`_verify_payload_citations`, rivi 137): Nykyinen logiikka iteroi `list[str]` -sitaatteja. Koska LLM generoi edelleen `list[str]`, **tämä koodi ei vaadi muutosta tässä vaiheessa.** Fuzzy Match toimii samoin.

> **3. Transformointivaihe (BlueprintTransformer — EvidenceQuoteDTO syntyy tässä):**
> - `backend_v2/services/blueprint.py` (rivit 430–459, `quotes_list`-hoisting): Tämä on **suurin muutos**. Nykyinen logiikka litistää sitaatit merkkijonolistaksi. Epic 88 vaatii, että jokainen sitaatti **korotetaan `EvidenceQuoteDTO`-objektiksi**:
>   - `text` = alkuperäinen merkkijono
>   - `id` = Python-generoitu UUID (`f"evq_{uuid.uuid4().hex[:12]}"`)
>   - `source_reference` = atomin `structural_location`-kenttä (jos `contextual_override == True`)
>   - `used_mcp_ids` = atomin `used_evidence_ids` -listasta aliaksen käännön jälkeen
>   - `is_mcp_verified` = Fuzzy Match -tulos `AnchorValidationService`llä MCP-vastetta vasten
>   - `user_rejected = False` (oletusarvo, käyttäjä muuttaa myöhemmin UI:ssa)
>
> - `backend_v2/models/v2_core.py` (`MatrixScorecardRowDTO`, rivi 893): Nykyinen `quotes_list: list[str] | None` korvataan kentällä `evidence_quotes: list[EvidenceQuoteDTO] = Field(default_factory=list)`. Vanha kenttä poistetaan Hard Cutoverissa.

> **4. Tallennusvaihe (Tietokanta):**
> - `backend_v2/models/v2_core.py` (`ReportDataDTO`, rivi 951 ja `ReportLayoutDTO` rivi 936): Nämä sisältävät `MatrixScorecardRowDTO` -listoja. Koska `MatrixScorecardRowDTO` päivitetään sisältämään `evidence_quotes: list[EvidenceQuoteDTO]`, kaikki tämä data serialisoituu JSON:ksi automaattisesti Pydanticin `.model_dump(mode="json")` -kautta. **Ei erillistä tietokantamigraatiota** — TinyDB/Firestore tallentaa Pydantic-mallien JSON-dumpin sellaisenaan.

> **5. Esityskerros (Flutter & PDF):**
> - Flutter: Dartin vastaava malli (`client_app_v2/lib/models/`) on päivitettävä: `quotesList: List<String>` → `evidenceQuotes: List<EvidenceQuoteDTO>` (Dart-malli `EvidenceQuoteDTO` luodaan).
> - PDF/Jinja2: Template päivitetään iteroimaan `evidence_quotes` -listaa objekteina (ei pelkkinä merkkijonoina).

---

### B.2 `LevelQuotesDTO` — Tason mukainen ryhmittely

**Nykytila koodissa:** Tätä mallia **ei ole** nykyisessä koodikannassa. Sitaatit ovat litteä lista ilman tasoryhmittelyä.
**Mistä data tulee?** Nykyinen `MatrixScorecardRowDTO` sisältää kentän `level_names: dict[str, str] | None` (rivi 879, esim. `{"1": "Heikko", "5": "Erinomainen"}`). Nämä tason nimet ovat jo olemassa, mutta sitaatteja EI ole ryhmitelty niiden alle.

**Muutostarve:**
> **Toimenpide:** `backend_v2/services/blueprint.py` — BlueprintTransformer-vaiheessa, kun `EvidenceQuoteDTO` -objektit luodaan, ne ryhmitellään atomin `status`- ja/tai `internal_logic_en` -datan perusteella tasoihin. `LevelQuotesDTO` luodaan Pythonissa (ei LLM:ssä!). Tulos tallennetaan `MatrixScorecardRowDTO.level_quotes: list[LevelQuotesDTO]` -kenttään.
>
> **Falsifikaatio:** Mistä tulee tieto siitä, mihin TASOON (level) kukin sitaatti kuuluu? Nykyisessä arkkitehtuurissa LLM ei generoi tason numeroa sitaattia kohti. Pisteytys tapahtuu atomitasolla Python-koodissa (DINA/Waterfall). **Ratkaisu:** Atomin `atom_id` on sidottu scale-ankuriin (`level_breakdown`, rivi 874). BlueprintTransformer voi johtaa tason tästä mäppäyksestä. Tämä vaatii, että transformerin logiikka rikastetaan: atomin score → tason numero → `LevelQuotesDTO.level`.

---

### B.3 `RowForensicsDTO` — Aito Pydantic-malli (ei litteä integrointi)

**Nykytila koodissa:** Tätä mallia **ei ole** erikseen. Sen rooli jakaantuu nykyisin `MatrixScorecardRowDTO`:n kenttien (rivi 834) kesken: `quotes_list`, `used_evidence_ids`, ja XAI-laajennukset. `MatrixScorecardRowDTO` on jo **30+ kenttää laaja** (rivit 834–898).

**Analyysi: Litteä vs. Aito malli:**
Koska Epic 88 on eksplisiittisesti *Breaking Change* ilman legacy-fallbackia (luku 8.4), JSON-polkujen murros ei ole este. Aito Pydantic-malli tarjoaa kolme konkreettista etua:

1. **Laskenta mallissa, ei esityskerroksessa (Zero-Math Templates).** `RowForensicsDTO` voi kapseloida kausaalisen orpouden logiikan `@computed_field` -dekoraattorilla. Flutter/PDF tarkistaa vain valmiin boolean-arvon.
2. **Testattavuus.** `RowForensicsDTO` testataan isolaatiossa ilman koko `MatrixScorecardRowDTO`:n konstruointia.
3. **Open/Closed Principle.** Tulevat forensiikkakentät lisätään `RowForensicsDTO`:lle koskematta vanhempimallia.

> **Suositus (Aito nested Pydantic-malli):**
> ```python
> class RowForensicsDTO(V2CoreBase):
>     evidence_quotes: list[EvidenceQuoteDTO] = Field(default_factory=list)
>     level_quotes: list[LevelQuotesDTO] = Field(default_factory=list)
>
>     @computed_field
>     @property
>     def all_evidence_rejected(self) -> bool:
>         """Kaskadoituva liputus (luku 7.1): True jos KAIKKI sitaatit on hylätty."""
>         all_quotes = [q for lq in self.level_quotes for q in lq.quotes]
>         return len(all_quotes) > 0 and all(q.user_rejected for q in all_quotes)
> ```
>
> **Toimenpide:** `backend_v2/models/v2_core.py` (`MatrixScorecardRowDTO`, rivi 834): Lisätään kenttä `forensics: RowForensicsDTO | None = None`. Vanhat kentät `quotes_list` ja `used_evidence_ids` säilytetään siirtymävaiheessa, mutta merkitään `deprecated` ja poistetaan Hard Cutoverissa.
>
> **Seuraus esityskerrokselle:** Flutter/PDF ei laske mitään. Se lukee `row.forensics.all_evidence_rejected` (boolean) ja renderöi ⚠️ -ikonin. Tämä noudattaa Flat MVC -mandaattia täydellisesti.

---

### B.4 `MCPAuditTraceDTO` (Luku 3.2) — jo käsitelty Liitteessä A

**Nykytila koodissa:** `MCPAuditTrace` (`v2_core.py`, rivi 581) on jo olemassa. Liitteen A analyysi kattaa `knowledge_gap` ja `search_rationale` -kenttien lisäyksen sekä laajentamisen kattamaan myös sisäiset dokumenttilähteet (`tool_id = "source_document"`).
**Luvun 3 lisä:** Luvussa 3.2 on kenttä `tool_name: str`, mutta nykyisessä koodissa vastaava kenttä on `tool_id: str` (rivi 585). **Ei ristiriitaa**, mutta Epic-dokumentin skeema tulisi yhdenmukaistaa koodin kanssa: `tool_name` → `tool_id`.

---

### B.5 Yhteenveto — Luvun 3 muutokset tiedostoittain

| Tiedosto | Muutos | Epic-kohta |
| :--- | :--- | :---: |
| `backend_v2/models/v2_core.py` | **[UUSI DTO]** `EvidenceQuoteDTO`, `LevelQuotesDTO`, `RowForensicsDTO` (aito Pydantic-malli `@computed_field`-tuella) | 3.1 |
| `backend_v2/models/v2_core.py` | `MatrixScorecardRowDTO`: Lisätään `forensics: RowForensicsDTO \| None = None`. Vanha `quotes_list` merkitään deprecated. | 3.1 |
| `backend_v2/services/blueprint.py` | Quotes hoisting (rivit 430–459): Litteä `list[str]` → `EvidenceQuoteDTO`-objektien luonti, tasoryhmittely → `RowForensicsDTO` | 3.1 |
| `backend_v2/models/prompts/field_prompts.py` | `DESC_EXACT_QUOTES`: Lisää Escape Hatch -lause ("tyhjä lista on oikea vastaus") | 3.1 |
| `client_app_v2/lib/models/` | **[UUSI]** Dart-mallit `EvidenceQuoteDTO`, `LevelQuotesDTO`, `RowForensicsDTO` | 3.1 |
| `backend_v2/templates/` | Jinja2-templatejen päivitys: `row.forensics.evidence_quotes` -iterointi | 3.1 |

### B.6 Falsifikaatio: Kriittiset riskit

1. **LLM:n skeemakompleksisuus:** Jos `EvidenceQuoteDTO` annettaisiin LLM:n generoitavaksi, hallusinaatiot räjähtäisivät. **Ratkaisu (vahvistettu):** LLM generoi edelleen litteän `list[str]`, Python korottaa ne objekteiksi. Tämä on dokumentoitu eksplisiittisesti.
2. **Kenttänimien ristiriita:** Epic-dokumentin luvussa 3.1 `EvidenceQuoteDTO` käyttää kenttää `used_mcp_ids`. Nykyisessä koodissa vastaava kenttä on `used_evidence_ids` (rivi 267 `lightweight_matrix.py`). **Suositus:** Yhdenmukaista Epic-dokumentin kenttänimi koodin kanssa → `used_evidence_ids`.
3. **Kenttänimien ristiriita 2:** Epic-dokumentin luvussa 3.2 käytetään `tool_name`, koodissa `tool_id`. **Suositus:** Yhdenmukaista → `tool_id`.
4. **`EvidenceQuoteDTO.id` generointi:** Epic ehdottaa `generate_uuid`-funktiota, jota ei ole koodissa. Quorumin konventio on `lambda: f"evq_{uuid.uuid4().hex[:12]}"` (Opaque Stripe ID -patternia noudattaen, kuten `chk_`, `tda_`, `org_`, `usr_`).

---

## Liite C: Koodivaikutusanalyysi (System 2 Deep Dive — Luku 4: Toteutuksen Vaiheet)
Tämä osio mäppää jokaisen luvun 4 toteutusvaiheen tarkkaan koodikantaan: kuka kutsuu mitä, missä data syntyy ja mitä tarkalleen muutetaan.

### C.1 Vaihe 1: Rakenteellinen CoT (`knowledge_gap` + `search_rationale`)

**Nykytila koodissa — tarkka datavirta:**
1. LLM generoi `CitationExtractionItemDTO` -objekteja Phase 0:ssa (`mcp_tool_loop.py`, rivit 376–390). Tämän mallin `reasoning`-kenttä (rivi 107, `mcp.py`) on vapaa max 150 merkin teksti.
2. `_execute_tavily_search()` (rivi 145, `mcp_tool_loop.py`) saa `reasoning`-arvon ja välittää sen suoraan `MCPAuditTrace`-konstruktorille (rivi 197).
3. `MCPAuditTrace` tallentaa `reasoning`-kentän (rivi 589, `v2_core.py`), joka päätyy `FrozenContext.mcp_tool_audit` -listaan tietokantaan.
4. Flutter lukee `reasoning`-kentän ja renderöi sen `xai_evidence_box.dart`-widgetissä (rivi 196).

**Muutoksen vaikutusketju (tarkat tiedostot):**

> **1. Pydantic-malli (LLM:n tulosteskeema):**
> - `backend_v2/models/domain/mcp.py` (`CitationExtractionItemDTO`, rivi 100): `reasoning: str` → `knowledge_gap: str` + `search_rationale: str`. Molemmat max 150 merkkiä. `description`-attribuutti pakottaa rakenteellisen ajattelun.
>
> **2. Extraktio-prompti (mikä ohjeistaa LLM:ää):**
> - `backend_v2/services/mcp/mcp_tool_loop.py` (rivit 350–357): `extraction_sys_msg`-prompti päivitetään ohjeistamaan LLM:ää täyttämään kaksi erillistä CoT-kenttää yhden `reasoning`-lauseen sijaan.
>
> **3. Audit Trace -tallennus:**
> - `backend_v2/services/mcp/mcp_tool_loop.py` (`_execute_tavily_search`, rivi 191–202): `MCPAuditTrace`-konstruktorikutsu: `reasoning=reasoning` → `knowledge_gap=citation.knowledge_gap, search_rationale=citation.search_rationale`.
> - `backend_v2/models/v2_core.py` (`MCPAuditTrace`, rivi 581): Lisää kentät `knowledge_gap: str = ""` ja `search_rationale: str = ""`. `reasoning` säilytetään siirtymävaiheessa defaultilla.
>
> **4. Flutter-esityskerros:**
> - `client_app_v2/lib/features/execution/models/report_data_dto.dart` (`MCPToolAuditDTO`): Lisää `knowledgeGap` ja `searchRationale` kentät.
> - `client_app_v2/lib/features/execution/views/widgets/xai_evidence_box.dart` (rivit 196+): Renderöi kaksi erillistä kohtaa (`reasoning`-lauseen tilalle):
>   - 🔍 *"Tietoaukko:"* `knowledge_gap`
>   - 🎯 *"Hakustrategia:"* `search_rationale`
>
> **5. PDF/Jinja2:**
> - `backend_v2/templates/report_template.jinja2`: Audit-lokiosioon lisätään `knowledge_gap` ja `search_rationale` renderöinti (`impacted_axis_names` on jo olemassa rivillä 592+).
>
> **Falsifikaatio:** Nykyinen `CitationExtractionItemDTO` on `frozen=True, extra="forbid"` (rivi 103 `mcp.py`). Tämä tarkoittaa, että kenttien nimeäminen on BREAKING CHANGE — vanhoja `reasoning`-kenttiä sisältäviä LLM-tuloksia ei voi parsia uudelleen. Mutta koska LLM-tulosteita ei tallenneta tietokantaan (ne parsitaan lennossa), tämä ei ole ongelma. Ainoa rikkoutuva kohta on `MCPAuditTrace.reasoning`, joka ON tietokannassa olemassa olevissa ajoissa. **Ratkaisu:** `reasoning` pidetään `MCPAuditTrace`ssa default-arvolla ja poistetaan vasta Hard Cutoverissa.

---

### C.2 Vaihe 2: DTO-mallien ja injektion päivitys

**Nykytila koodissa — Epic-dokumentin epätarkkuus:**
Luku 4 Vaihe 2 sanoo: *"Kohde: `v2_core.py`, `matrix.py`"*. Tiedostoa `matrix.py` **ei ole olemassa** koodikannassa. Oikeat tiedostot ovat:
- `backend_v2/models/v2_core.py` — `MatrixScorecardRowDTO`, `MCPAuditTrace`, `FrozenContext`
- `backend_v2/models/dtos/lightweight_matrix.py` — `AtomEvaluationItemDTO`, `LightweightExtractionAtom`

**Muutoksen tarkka sisältö (jo eritelty liitteissä A ja B):**
> **DTO-mallit:** `EvidenceQuoteDTO`, `LevelQuotesDTO`, `RowForensicsDTO` lisätään `v2_core.py`:hin. `MatrixScorecardRowDTO` saa kentän `forensics: RowForensicsDTO | None = None`.
>
> **Injektion päivitys (Unified Source Pipeline):** `alias_registry.py` luodaan. Sekä `mcp_tool_loop.py` (rivit 552–564) että `llm.py` kutsuvat samaa `wrap_source_chunks()`-funktiota. Tämä on jo käsitelty Liitteessä A.2.
>
> **Epic-dokumentin korjaus:** Viittaus `matrix.py`:hin korjataan → `lightweight_matrix.py` ja `v2_core.py`.

---

### C.3 Vaihe 3: Blueprint Transformer (Käänteishaku)

**Nykytila koodissa — mitä on jo olemassa:**
`BlueprintTransformer` (`blueprint.py`, rivit 1049–1076) tekee jo kaksi asiaa:
1. Kerää `used_evidence_ids` kaikista matriisien payloadeista (rekursiivinen `extract_evidence_ids`)
2. Käänteismäppää ne `impacted_axis_names`-listaan `MCPAuditTrace`-tietueissa

**Mitä puuttuu (tarkat lisäykset):**

> **1. Aliaksen käännös (`<<QRM-SRC-N>>` → UUID):**
> - `backend_v2/services/blueprint.py` (rivit 1049–1076): Lue `alias_map` sanakirja `FrozenContext`-mallista (tai `alias_registry`-palvelulta). Jokainen `used_evidence_ids`:ssä oleva `<<QRM-SRC-N>>` käännetään todelliseksi UUID:ksi ennen `impacted_axis_names` -mäppäystä.
> - **Uusi kenttä:** `FrozenContext` (`v2_core.py`, rivi 1227) saa kentän `source_alias_map: dict[str, str] = Field(default_factory=dict)`, johon `alias_registry` tallentaa `<<QRM-SRC-1>>` → `tavily_xxxx` mäppäyksen ajon aikana.
>
> **2. `RowForensicsDTO`-objektien koostaminen:**
> - `backend_v2/services/blueprint.py` (rivit 430–459): Nykyinen `quotes_list` hoisting-logiikka korvataan uudella logiikalla, joka:
>   a. Luo `EvidenceQuoteDTO`-objektit jokaiselle sitaatille
>   b. Suorittaa Fuzzy Match -tarkistuksen `AnchorValidationService`llä MCP-lähteen `response_summary`-kenttää vasten → `is_mcp_verified`
>   c. Ryhmittelee `LevelQuotesDTO`:hin atomin `atom_id` → `level_breakdown` -mäppäyksellä
>   d. Kokoaa `RowForensicsDTO`-objektin ja asettaa sen `MatrixScorecardRowDTO.forensics`-kenttään
>
> **3. `is_mcp_verified` asetus:**
> - Tapahtuu kohdassa 2b. Vaatii pääsyn `mcp_audit_data`-listaan, joka on jo saatavilla samassa kontekstissa (rivi 1039).
>
> **Falsifikaatio:** `extract_evidence_ids()` (rivi 1053) iteroi `payload`-dictejä rekursiivisesti. Jos `alias_map` sisältää `<<QRM-SRC-N>>` -avaimia ja atomin `used_evidence_ids` sisältää saman avaimen, käännös toimii. MUTTA: entä jos LLM kirjoittaa aliaksen väärin (esim. `<<QRM-SRC-01>>` vs. `<<QRM-SRC-1>>`)? **Ratkaisu:** `alias_registry.py`:n `resolve()`-funktio normalisoi aliaksen ennen hakua (poistaa johtavat nollat jne.) ja heittää Fail-Fast -virheen, jos normalisoitu alias ei löydy sanakirjasta.

---

### C.4 Vaihe 4: Esityskerros (Flutter & Jinja2)

**Nykytila koodissa — Flutter:**
- `scorecard_dto.dart` (rivi 76): `@JsonKey(name: 'quotes_list') @Default([]) List<String> quotesList` — litteä merkkijonolista.
- `atom_matrix_table_widget.dart` (rivit 226, 349): Renderöi sitaatit yksinkertaisena markdown-listana (`m.quotesList.map((q) => '- $q').join('\n')`).
- `report_data_dto.dart` (rivi 107): `MCPToolAuditDTO` sisältää `impactedAxisNames` ja `reasoning` (yhtenä kenttänä).

**Nykytila koodissa — Jinja2 (PDF):**
- `report_template.jinja2` (rivit 259–267): Renderöi `cited_text_quote` yksittäisenä otteena. EI iteroi `quotes_list`-kenttää PDF-puolella lainkaan (vain Flutter tekee sen).

**Muutokset:**

> **Flutter (Freezed/json_serializable — koodingenerointi):**
> 1. `client_app_v2/lib/features/execution/models/scorecard_dto.dart`: Lisää `@JsonKey(name: 'forensics') RowForensicsDTO? forensics`. Vanha `quotesList` merkitään `@Deprecated`.
> 2. **[UUSI]** `client_app_v2/lib/features/execution/models/forensics_dto.dart`: Dart-mallit `EvidenceQuoteDTO`, `LevelQuotesDTO`, `RowForensicsDTO` (Freezed + json_serializable).
> 3. `client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart` (rivit 226–236, 349–353): Korvataan `m.quotesList`-iterointi → `m.forensics?.levelQuotes`-iterointi. Renderöi tasoryhmitellyt sitaatit, ✅-ikoni jos `isMcpVerified`, yliviivaus jos `userRejected`, ⚠️ jos `allEvidenceRejected`.
> 4. `client_app_v2/lib/features/execution/models/report_data_dto.dart` (`MCPToolAuditDTO`): Lisää `knowledgeGap` ja `searchRationale`. `reasoning` merkitään `@Deprecated`.
> 5. `client_app_v2/lib/features/execution/views/widgets/xai_evidence_box.dart` (rivi 196+): Renderöi `knowledgeGap` ja `searchRationale` erillisiin osioihin.
> 6. **Koodingenerointi:** `dart run build_runner build` uudelleengeneroi `.freezed.dart` ja `.g.dart` tiedostot.
>
> **Jinja2 (PDF):**
> 1. `backend_v2/templates/report_template.jinja2` (rivit 259–280): Korvataan `cited_text_quote` -renderöinti → `forensics.level_quotes` -iterointi:
>    - Tason otsikko: `{% for lq in axis.forensics.level_quotes %}<h4>{{ lq.level_name }}</h4>{% endfor %}`
>    - Sitaatit: `{% for eq in lq.quotes %}{{ eq.text }}{% if eq.is_mcp_verified %} ✅{% endif %}{% if eq.user_rejected %}<del>{% endif %}{% endfor %}`
>    - Kaskadoituva varoitus: `{% if axis.forensics.all_evidence_rejected %}<span>⚠️ Arvosanan perusteet kumottu</span>{% endif %}`
> 2. Audit-lokin renderöinti (uusi osio templateen): `knowledge_gap` ja `search_rationale` MCP-audit -taulukossa.
>
> **Falsifikaatio:** Jinja2-templatessa `axis.forensics` voi olla `None` (jos ajo suoritettiin ennen Epic 88:a). **Ratkaisu:** `{% if axis.forensics %}` -tarkistus ennen forensics-renderöintiä. Vanha `cited_text_quote` -logiikka säilytetään `{% else %}` -haarassa siirtymävaiheessa.

---

### C.5 Yhteenveto — Luvun 4 muutostarpeet tiedostoittain

| Tiedosto | Muutos | Vaihe |
| :--- | :--- | :---: |
| `backend_v2/models/domain/mcp.py` | `CitationExtractionItemDTO`: `reasoning` → `knowledge_gap` + `search_rationale` | 1 |
| `backend_v2/models/v2_core.py` | `MCPAuditTrace`: Lisää `knowledge_gap`, `search_rationale` (default="") | 1 |
| `backend_v2/models/v2_core.py` | `FrozenContext`: Lisää `source_alias_map: dict[str, str]` | 3 |
| `backend_v2/services/mcp/mcp_tool_loop.py` | Phase 0 prompti + `_execute_tavily_search()` konstruktori | 1 |
| `backend_v2/services/mcp/alias_registry.py` | **[UUSI]** Unified Source Pipeline (Liite A.2) | 2 |
| `backend_v2/services/blueprint.py` | Aliaksen käännös + `RowForensicsDTO` koostaminen + Fuzzy Match | 3 |
| `client_app_v2/.../scorecard_dto.dart` | `forensics: RowForensicsDTO?` kenttä, `quotesList` deprecated | 4 |
| `client_app_v2/.../forensics_dto.dart` | **[UUSI]** Dart-mallit: `EvidenceQuoteDTO`, `LevelQuotesDTO`, `RowForensicsDTO` | 4 |
| `client_app_v2/.../atom_matrix_table_widget.dart` | Tasoryhmitelty renderöinti + ikonit + yliviivaus + varoitus | 4 |
| `client_app_v2/.../report_data_dto.dart` | `MCPToolAuditDTO`: `knowledgeGap` + `searchRationale` | 4 |
| `client_app_v2/.../xai_evidence_box.dart` | Kaksiosainen CoT-renderöinti | 4 |
| `backend_v2/templates/report_template.jinja2` | Forensics-renderöinti + Audit-loki CoT-osio | 4 |

### C.6 Falsifikaatio: Luvun 4 vaihejärjestys ja riippuvuudet

```
Vaihe 1 (CoT-kentät)  ← itsenäinen, voidaan toteuttaa ensin
       ↓
Vaihe 2 (DTO + alias_registry)  ← riippuu Vaiheen 1 kenttänimistä
       ↓
Vaihe 3 (BlueprintTransformer)  ← riippuu Vaiheen 2 DTO:ista ja alias_mapista
       ↓
Vaihe 4 (Esityskerros)  ← riippuu Vaiheen 3 tuottamasta RowForensicsDTO:sta
```

**Tämä järjestys on oikein.** Jokainen vaihe riippuu edellisestä. Rinnakkaisuutta ei ole mahdollista saavuttaa vaiheiden välillä, mutta **vaiheen sisällä** backend- ja frontend-kehitys voidaan ajaa rinnakkain:
- Vaihe 1: Backend-muutos (`mcp.py`, `v2_core.py`, `mcp_tool_loop.py`) → Flutter-muutos (`report_data_dto.dart`, `xai_evidence_box.dart`) rinnakkain.
- Vaihe 4: Flutter-muutos (`atom_matrix_table_widget.dart`) ja PDF-muutos (`report_template.jinja2`) rinnakkain.

### C.7 Epic-dokumentin korjaus
Luku 4 Vaihe 2 viittaa tiedostoon `matrix.py`, jota ei ole koodikannassa. Oikeat tiedostot ovat `lightweight_matrix.py` ja `v2_core.py`.

---

## Liite D: Koodivaikutusanalyysi (System 2 Deep Dive — Luku 5: Datan Elinkaari)
Tämä osio mäppää jokaisen luvun 5 väitteen todelliseen koodikantaan ja tunnistaa puuttuvat komponentit.

### D.1 Luku 5.1 — Luominen (Create - Autonominen generointi)

**Epic väittää:** *"Sitaatit syntyvät yksinomaan tekoälyn suorittamien työnkulkujen aikana. Worker tallentaa `RowForensicsDTO`:n ja Audit-lokit pysyvästi ajon tietokantatietueeseen (`executions`-taulu) sekä tiedostojärjestelmään (`execution_trace.json`)."*

**Verifikaatio koodissa:**
1. **`worker.py` (rivit 417–419, 438–439, 905):** Ajon valmistuessa Worker kutsuu `repository.update_execution(exec_id, {...})` ja tallentaa `execution_trace`-listan tietokantaan JSON-dumppeina. ✅ Tämä väite pitää paikkansa.
2. **`execution.py` (rivit 195–209):** `update_execution()` kutsuu `self.driver.update("executions", ...)`, joka tallentaa `executions`-tauluun (TinyDB/Firestore). ✅ Pitää paikkansa.
3. **`FrozenContext.mcp_tool_audit` (v2_core.py, rivi 1236):** Audit-lokit tallennetaan `FrozenContext`:iin, joka serialisoituu `execution_trace`-tapahtumien osaksi. ✅ Pitää paikkansa.

**Puutteet ja arkkitehtuuripäätös (ADR):**
> `RowForensicsDTO`:ta ei tallenneta mihinkään — se on **esitystason objekti**, joka syntyy vasta `BlueprintTransformer.build_report_dto()` -kutsun aikana eikä koskaan persistoidu tietokantaan. `ReportDataDTO` lasketaan lennossa joka kerta kun raporttia pyydetään (`execution.py`, rivi 680–684).
>
> **Päätös: `RowForensicsDTO`:ta EI tallenneta tietokantaan.** Se pysyy johdettuna (derived) näkymänä. Perustelut:
> - **Single Source of Truth:** Raakaata (`execution_trace` + `FrozenContext`) on ainoa totuuden lähde. Johdetun näkymän persistoiminen loisi kaksi totuutta, jotka voivat erota (esim. DLQ-retry korjaa atomin, mutta persistoitu forensics olisi vanhentunut).
> - **Arkkitehtuurin yhtenäisyys:** Koko `ReportDataDTO`-pipeline on johdettu näkymä. `RowForensicsDTO`:n persistoiminen rikkoisi tämän periaatteen.
> - **Suorituskyky riittää:** `AnchorValidationService.calculate_fuzzy_score()` käyttää RapidFuzz-kirjastoa (C-toteutus). 50 sitaattia × 10 MCP-lähdettä = 500 kutsua < 10ms. Ei pullonkaula.
>
> **ID-stabiilisuus ratkaistaan deterministisellä generoinnilla** (ei persistoinnilla):
> ```python
> import hashlib
> def _stable_evidence_id(execution_id: str, block_id: str, quote_text: str) -> str:
>     digest = hashlib.sha256(f"{execution_id}:{block_id}:{quote_text}".encode()).hexdigest()[:12]
>     return f"evq_{digest}"
> ```
> Sama syötedata tuottaa aina saman ID:n riippumatta siitä, kuinka monta kertaa `build_report_dto()` ajetaan. Soft Delete -mekanismin `evidence_override` TraceEvent viittaa tähän pysyvään `evq_`-ID:hen.
>
> **Snapshot-konsistenssi on tietoinen arkkitehtuurinen valinta.** Raportti näyttää AINA uusimman logiikan mukaisen tulkinnan raakadatasta (kuten SQL VIEW). Jos `BlueprintTransformerin` logiikka muuttuu, data näkyy uudella tavalla. Vanha logiikka säilyy Git-historiassa.

**Falsifikaatio:** Koska `RowForensicsDTO` lasketaan lennossa eikä tallenneta, `user_rejected`-tila EI VOI elää siinä. Se vaatii erillisen persistenssimekanismin. Tämä johtaa suoraan luvun 5.3 kriittiseen löytöön.

---

### D.2 Luku 5.2 — Luku ja Esittäminen (Read)

**Epic väittää:** *"Esittäminen tapahtuu olemassa olevan Report-rajapinnan kautta (`GET /api/v2/execution/executions/{id}/report`)".*

**Verifikaatio koodissa:**
- `backend_v2/services/execution.py` (rivit 676–684): `get_execution_report()` kutsuu `BlueprintTransformer.build_report_dto()` ja palauttaa `dto.model_dump(mode="json")`. ✅ Väite on tarkka ja oikein.
- Sama endpoint palauttaa myös HTML (rivi 686–707) ja PDF (rivi 709+) muotoja. ✅ Kaikki kolme formaattia käyttävät samaa `ReportDataDTO`-objektia pohjana.

**Ei muutosta tarvita** — rajapinta on jo olemassa ja toimii oikein. `RowForensicsDTO` kulkee osana `MatrixScorecardRowDTO`:ta, joka sisältyy `ReportDataDTO`:iin.

---

### D.3 Luku 5.3 — Soft Delete (Human Override) — KRIITTINEN LÖYTÖ

**Epic väittää:** *"Käyttäjä voi UI:ssa merkitä sitaatin hylätyksi. Tämä on ainoa sallittu muokkaus (PUT), joka asettaa `user_rejected = True`."*

**Nykytila koodissa:**
- `user_rejected`-kenttää **ei ole olemassa** yhdessäkään koodikannan Pydantic-mallissa. ✅ Tiedetty — tämä on uusi ominaisuus.
- **Kriittinen ongelma:** Missä `user_rejected`-tila persistoituu?

**Arkkitehtuurinen analyysi:**

> `EvidenceQuoteDTO` syntyy `BlueprintTransformerissa` (laskettu näkymä) eikä ole tietokannassa erillinen tietue. Jos käyttäjä painaa "Hylkää sitaatti" -nappia, mihin tämä tallennetaan?
>
> **Vaihtoehto A: Erillisenä dokumenttina tietokantaan.**
> Luodaan uusi taulu/kokoelma `evidence_overrides` (tai `forensic_overrides`), johon tallennetaan:
> ```python
> class EvidenceOverrideRecord(V2CoreBase):
>     execution_id: str
>     evidence_quote_id: str  # evq_xxxx (EvidenceQuoteDTO.id)
>     user_rejected: bool = True
>     rejection_reason: str | None = None
>     rejected_by: str  # käyttäjän ID
>     rejected_at: datetime
> ```
> BlueprintTransformer lukee nämä overridet ja yhdistää ne `EvidenceQuoteDTO`:hin koostamisvaiheessa.
>
> **Vaihtoehto B: Suoraan `execution_trace`-tietueeseen (inline patching).**
> Lisätään uusi `TraceEvent`-tyyppi `"evidence_override"`, joka tallennetaan ajon `execution_trace`-listaan. BlueprintTransformer lukee nämä tapahtumat ja asettaa `user_rejected = True` vastaavalle sitaatille.
>
> **Suositus (Vaihtoehto B — Append-Only):** Vaihtoehto B noudattaa jo olemassa olevaa Append-Only Event Sourcing -arkkitehtuuria. `execution_trace`-lista on muuttumaton sekvenssi — uusia tapahtumia apppenoidaan, vanhoja ei muokata. `evidence_override` on vain uusi tapahtumatyyppi. Tämä ei vaadi uutta taulua, ei uutta repositorya, eikä uutta API-reittiä (paitsi yksi uusi endpoint, joka appendoi overriden).

**Muutokset tiedostoittain:**

| Tiedosto | Muutos |
| :--- | :--- |
| `backend_v2/models/state.py` | **[UUSI]** `EvidenceOverrideEvent` (tai uusi `event_type` TraceEventissä) |
| `backend_v2/api/v2/execution.py` | **[UUSI ENDPOINT]** `PUT /executions/{id}/evidence/{evq_id}/reject` — appendoi override-tapahtuman |
| `backend_v2/services/execution.py` | **[UUSI METODI]** `reject_evidence_quote()` — validoi, appendoi TraceEvent |
| `backend_v2/services/blueprint.py` | **[MUUTOS]** `build_report_dto()`: Lue `evidence_override` -tapahtumat ja aseta `user_rejected = True` |
| `backend_v2/database/repositories/execution.py` | **[MUUTOS]** `append_trace_event()` — tai hyödynnetään olemassa olevaa `update_execution()` |
| `client_app_v2/.../atom_matrix_table_widget.dart` | **[UUSI]** "Hylkää sitaatti" -painike + API-kutsu |

---

### D.4 Luku 5.4 — Archivist-tietokannan RAG-integraatio

**Epic väittää:** *"EvidenceQuoteDTO viedään Archivist-matriisiin taustaprosessissa. Agentit suodattavat tiukasti pois kaikki sitaatit, joissa `user_rejected == True`."*

**Nykytila koodissa:**
- `ArchivistOutput` (`backend_v2/models/domain/archivist.py`) on olemassa ja sisältää omat kentät (`thought_process`, ArchiveCase-listat).
- Archivist ei nykyisin lue `EvidenceQuoteDTO`:ta suoraan ajoista. Se on itsenäinen agentti, joka operoi omalla datallaan.

**Muutostarve:**

> **Tämä on tulevaisuuden ominaisuus (Phase 2).** Epic 88:n ensimmäisessä toteutusvaiheessa Archivist-integraatiota EI tarvitse toteuttaa. `user_rejected`-suodatus on kuitenkin **arkkitehtuurisesti valmisteltu**: koska `EvidenceQuoteDTO.user_rejected` on osa mallia, tulevaisuuden Y-Funnel Extraction Hook voi suodattaa sen pois yksinkertaisella `[eq for eq in quotes if not eq.user_rejected]` -listakomprehensolla.
>
> **Ei koodimuutosta tässä vaiheessa.** Epic-dokumenttiin lisätään selkeä merkintä siitä, että 5.4 on Phase 2 -ominaisuus.

---

### D.5 Yhteenveto — Luvun 5 muutostarpeet tiedostoittain

| Tiedosto | Muutos | Epic-kohta |
| :--- | :--- | :---: |
| `backend_v2/models/state.py` | **[UUSI]** `EvidenceOverrideEvent` -tapahtumatyyppi | 5.3 |
| `backend_v2/api/v2/execution.py` | **[UUSI ENDPOINT]** `PUT .../evidence/{evq_id}/reject` | 5.3 |
| `backend_v2/services/execution.py` | **[UUSI METODI]** `reject_evidence_quote()` | 5.3 |
| `backend_v2/services/blueprint.py` | Override-tapahtumien lukeminen ja yhdistäminen `EvidenceQuoteDTO`:hin | 5.3 |
| `client_app_v2/.../atom_matrix_table_widget.dart` | "Hylkää sitaatti" -painike ja API-kutsu | 5.3 |

### D.6 Falsifikaatio: Kriittiset riskit ja korjaukset

1. **Epic-dokumentin harhaanjohtava väite (5.1):** `RowForensicsDTO` ei tallennu tietokantaan. Se on johdettu (derived) näkymä, joka lasketaan BlueprintTransformerissa lennossa raakadatasta (`execution_trace` + `FrozenContext`). Raakaata (atomien `exact_quotes`, `used_evidence_ids`, `MCPAuditTrace`) kyllä persistoituu. **Korjaus:** Epic-dokumentin luvun 5.1 sanamuoto on päivitettävä heijastamaan tätä.
2. **Soft Delete -persistenssi (5.3):** Suurin puuttuva komponentti. `user_rejected` ei voi elää `RowForensicsDTO`:ssa, koska se lasketaan lennossa. Ratkaisu: Append-Only `evidence_override` TraceEvent, joka liitetään ajon `execution_trace`-listaan. Vaatii uuden API-endpointin.
3. **Archivist-integraatio (5.4):** Ei toteuteta Epic 88:n Phase 1:ssä. Arkkitehtuurisesti valmisteltu `user_rejected`-kentällä, mutta varsinainen Y-Funnel Hook on tulevaisuutta.
4. **ID-stabiilisuus:** Koska `EvidenceQuoteDTO.id` generoidaan BlueprintTransformerissa lennossa, saman ajon eri raporttikyselyt saavat ERI `evq_`-ID:t! Tämä rikkoo Soft Delete -mekanismin, joka perustuu pysyvään `evq_`-ID:hen. **Ratkaisu:** `EvidenceQuoteDTO.id` on generoitava **deterministisesti** (esim. `f"evq_{hash(execution_id + block_id + quote_text)[:12]}"`) tai vaihtoehtoisesti `evq_`-ID tallennetaan `execution_trace`-tietueeseen ensimmäisellä raportin generoinnilla.

---

## Liite E: Koodivaikutusanalyysi (System 2 Deep Dive — Luku 6: Quality Gates)
Tämä osio verifioi jokaisen Quality Gate -kriteerin todellista koodikantaa vasten ja tunnistaa, mitkä komponentit vaativat muutoksia kriteerien täyttämiseksi.

### E.1 QG1: Universaali Forensic Sovereignty

**Kriteeri:** *"Jokainen tekoälyn esittämä väite tallentuu `EvidenceQuoteDTO`-muodossa. Sisäisillä väitteillä on suora `source_reference`, ja ulkoisilla hauilla on katkeamaton jälki: `Haku -> Tracen ID -> Evidence Quote -> Matriisin sääntö`."*

**Nykytila koodissa:**
- Atomitasolla `exact_quotes: list[str]` on jo olemassa kolmessa mallissa:
  - `lightweight_matrix.py` (`LightweightExtractionAtom`, rivi 153; `AtomEvaluationItemDTO`, rivi 272)
  - `evaluation_steps.py` (rivi 66)
  - `v2_core.py` (`MatrixScorecardRowDTO`, rivi 1376 — `quotes_list`)
- MCP Audit Trace -ketju on jo olemassa: `MCPAuditTrace.id` → `used_evidence_ids` → `impacted_axis_names` (blueprint.py rivit 1049–1076).
- `source_reference`-kenttää **ei ole olemassa** nykyisissä sitaattikenttissä. Sitaatit ovat puhtaita merkkijonoja.

**Mitä puuttuu QG1:n täyttämiseksi:**

> | Tiedosto | Muutos |
> | :--- | :--- |
> | `backend_v2/models/v2_core.py` | **[UUSI]** `EvidenceQuoteDTO` (ks. Liite B): `text`, `source_reference`, `is_mcp_verified`, `user_rejected`, `id` (deterministinen) |
> | `backend_v2/services/blueprint.py` | Hoisting-logiikka: litteä `list[str]` → `list[EvidenceQuoteDTO]`, `source_reference` lasketaan atomin `used_evidence_ids` + `alias_map` → `MCPAuditTrace.source_urls` ketjulla |
> | `backend_v2/services/mcp/alias_registry.py` | **[UUSI]** Unified aliasing `wrap_source_chunks()` + `resolve()` |
>
> **Ketju todennettava end-to-end:** `LLM generoi used_evidence_ids: ["<<QRM-SRC-1>>"]` → `alias_registry.resolve()` → `MCPAuditTrace(id="tavily_xxx")` → `EvidenceQuoteDTO(source_reference="tavily_xxx")` → `RowForensicsDTO.evidence_quotes[0]` → Flutter/PDF.

**Falsifikaatio:** Ketjun heikoin kohta on se, että `used_evidence_ids` on **valinnainen**. Jos LLM ei täytä sitä (tyhjä lista), sitaatti jää ilman `source_reference`-arvoa. Tämä ei riko järjestelmää (oletus on `None`), mutta vähentää forensiikan kattavuutta. **Ratkaisu:** `DESC_EXACT_QUOTES` -promptia päivitetään vaatimaan `used_evidence_ids`:n täyttöä aina kun `<search_result>`-tageja on kontekstissa. Tämä on ohjeistus, ei pakote — LLM:n skeema sallii tyhjän listan.

---

### E.2 QG2: Flat UI

**Kriteeri:** *"Flutter-koodissa ja Jinja2-templatessa ei ole lainkaan for-luuppeja, jotka yrittäisivät mäpätä hakuja matriiseihin."*

**Nykytila koodissa:**
- **Flutter:** `atom_matrix_table_widget.dart` (rivit 226–236, 349–353) iteroi `m.quotesList`, joka on valmiiksi ryhmitelty DTO-lista. Ei yritä mäpätä hakuja matriiseihin. ✅ Periaate on jo noudatettu.
- **Jinja2:** `report_template.jinja2` (rivit 259–267) renderöi `axis.cited_text_quote` yksittäisenä kenttänä. Ei luuppeja hakulle. ✅ Periaate on jo noudatettu.
- **Reverse Lookup:** `blueprint.py` (rivit 1049–1076) tekee `used_evidence_ids` → `impacted_axis_names` mäppäyksen **Pythonissa**, ei esityskerroksessa. ✅ Oikein.

**Muutos QG2:n täyttämiseksi:**

> **Ei koodimuutosta olemassa olevaan logiikkaan.** QG2 on arkkitehtuurinen periaate, joka on jo noudatettu. Epic 88:n uusi `RowForensicsDTO` → `forensics.level_quotes` iterointi on suunniteltava samalla periaatteella: Flutter ja Jinja2 vain iteroivat valmiit listat, eivät hae tai mäppää mitään.
>
> **Testausmandaatti:** Audit-skripti (tai code review -tarkistus) varmistaa, ettei `atom_matrix_table_widget.dart` tai `report_template.jinja2` sisällä `mcp_audit`-hakuja tai `source_alias_map`-viittauksia.

---

### E.3 QG3: Fail-Fast & Didaktinen DLQ (Escape Hatch)

**Kriteeri:** *"Jos LLM hallusinoi aliaksen, Pydantic laukaisee virheen, joka lähetetään DLQ/Retry-kiertoon. Virheilmoitus sisältää Escape Hatch."*

**Nykytila koodissa:**

1. **DLQ-mekanismi ON olemassa:** `worker.py` (rivi 153) tarkistaa `_dlq_status == "FAILED/DLQ"` ja reitittää virheen. Chunk-taso (rivit 95+, `chunk_worker.py`) nappaa `SemanticEvidenceError`:n.
2. **Self-Healing retry -silmukka ON olemassa:** `llm_task_executor.py` (rivit 289–472) ajaa schema- ja loogisen validoinnin retry-silmukan. `PromptCompiler.get_schema_healing_prompt()` (rivi 407, `prompt_compiler.py`) generoi korjauskehotteen.
3. **Aliaksen validointia EI OLE:** `used_evidence_ids`-kenttää ei validoida missään. LLM voi kirjoittaa `<<QRM-SRC-99>>` ja se menee läpi ilman virhettä.
4. **Escape Hatch -logiikkaa EI OLE:** Nykyinen `get_schema_healing_prompt()` (rivit 428–436) ei tarjoa mallille "tyhjä lista on oikea vastaus" -vaihtoehtoa. `is_logical_error`-haara käskee: "Regenerate your response ensuring all logical validations pass." Tämä pakottaa miellyttämisenhaluisen mallin valehtelemaan.

**Muutokset QG3:n täyttämiseksi:**

> | Tiedosto | Muutos |
> | :--- | :--- |
> | `backend_v2/services/mcp/alias_registry.py` | `resolve(alias, alias_map)`: Validoi, ettei alias ole tuntematon. Heittää `SemanticEvidenceError` dynaamisella viestillä |
> | `backend_v2/services/llm_task_executor.py` | Lisää `used_evidence_ids` validointikoukku `_perform_semantic_validation()` -funktioon (rivi 181+). Tarkistaa, että jokainen ID on sallitussa alias_mapissa |
> | `backend_v2/services/orchestrator/prompt_compiler.py` | **Escape Hatch -lisäys** `get_schema_healing_prompt()` -funktioon (rivi 428): `is_logical_error`-haaran loppuun lisätään: *"JOS nämä lähteet eivät sisällä väitettäsi, PALAUTA TYHJÄ LISTA []. Älä keksi lähteitä."* |
> | `backend_v2/models/prompts/field_prompts.py` | `DESC_EXACT_QUOTES`: Lisää Escape Hatch -lause promptiin: *"Jos lähdedokumentti ei sisällä sopivia sitaatteja, tyhjä lista on oikea vastaus."* |

**Falsifikaatio:** Escape Hatch luo riskin, että LLM käyttää sitä liian helposti (laiskuus: palauttaa tyhjän listan väittämättä etsineensä). **Ratkaisu:** `RowForensicsDTO.all_evidence_rejected` @computed_field liputttaa tyhjät forensics-tulokset. Lisäksi `knowledge_gap` CoT-kenttä (Vaihe 1) pakottaa mallin perustelemaan, miksi lähdedokumentti ei sisältänyt vastausta.

---

### E.4 QG4: Mekaaninen Totuus (Ei XAI-teatteria)

**Kriteeri:** *"Backend suorittaa sumean merkkijonohaun (Fuzzy Text Matching / Levenshtein) LLM:n poimimalle sitaatille suhteessa lähdedokumenttiin. > 90% osuman myötä `is_mcp_verified` voi muuttua todeksi."*

**Nykytila koodissa:**
- `AnchorValidationService.calculate_fuzzy_score()` (rivi 93, `anchor_validation_service.py`) käyttää **RapidFuzz**-kirjastoa. ✅ Oikein.
  - Lyhyet sitaatit (< 30 merkkiä): `fuzz.partial_ratio()` (kontiguiteetti-guard)
  - Pitkät sitaatit (≥ 30 merkkiä): `fuzz.token_set_ratio()` (sana-tason vastaavuus)
- `AnchorValidationService.validate_evidence()` (rivi 112) suorittaa validoinnin atomitasolla. Threshold tulee `get_lexical_fuzz_threshold(locale)`:sta.
- **Kosini-samankaltaisuutta EI käytetä missään koodikannassa.** ✅ Verifioitu.

**Mitä puuttuu:**

> `is_mcp_verified`-kenttää ei ole olemassa. Se on uusi laskenta, joka suoritetaan `BlueprintTransformerissa`:
>
> | Tiedosto | Muutos |
> | :--- | :--- |
> | `backend_v2/services/blueprint.py` | `RowForensicsDTO` koostamisvaiheessa: jokaisen `EvidenceQuoteDTO`:n `text` verifioidaan `AnchorValidationService.calculate_fuzzy_score()`:llä vastaavan `MCPAuditTrace.response_summary`:n suhteen. Jos tulos > 90 → `is_mcp_verified = True` |
>
> **Falsifikaatio:** `fuzz.token_set_ratio()` (pitkille sitaateille) sallii sanojen uudelleenjärjestelyn. Tämä voi hyväksyä parafraaseja, joissa sanat ovat samat mutta järjestys eri. **Vaikutus:** Vähäinen, koska `is_mcp_verified` on lisäindikaattori (bonus-merkki), ei portinvartija. Sitaatin päävalidointi tapahtuu jo `validate_evidence()`:ssa atomitasolla ennen tallennusta. `is_mcp_verified` on *täydentävä* tarkistus, joka kertoo, löytyykö sama fakta myös ulkoisesta lähteestä.

---

### E.5 QG5: Kausaalisen Orpouden Esto

**Kriteeri:** *"Jos tason kaikki todisteet kumotaan, itse matriisin arvosana on liputettava varoituksella."*

**Nykytila koodissa:**
- `user_rejected`-kenttää **ei ole olemassa** — toteutetaan Epic 88:ssa (ks. Liite D.3).
- Kaskadoituvaa liputuslogiikkaa **ei ole olemassa** — toteutetaan `RowForensicsDTO.all_evidence_rejected` @computed_field:nä (ks. Liite B.3).

**Muutokset QG5:n täyttämiseksi:**

> | Tiedosto | Muutos |
> | :--- | :--- |
> | `backend_v2/models/v2_core.py` | `RowForensicsDTO`: `@computed_field all_evidence_rejected` — palauttaa `True` jos kaikkien `evidence_quotes`:n `user_rejected == True` |
> | `client_app_v2/.../atom_matrix_table_widget.dart` | Jos `forensics.allEvidenceRejected == true`, renderöi ⚠️ -ikoni arvosanan viereen |
> | `backend_v2/templates/report_template.jinja2` | `{% if axis.forensics.all_evidence_rejected %}⚠️{% endif %}` |
>
> **Falsifikaatio:** Jos `evidence_quotes`-lista on tyhjä (ei sitaatteja lainkaan), `all()` palauttaa `True` tyhjälle listalle Pythonissa. Tämä aiheuttaisi väärän varoituksen riveille, joille LLM ei generoinut sitaatteja. **Ratkaisu:** `@computed_field` palauttaa `True` vain jos lista on **epätyhjä** JA kaikki ovat rejected:
> ```python
> @computed_field
> @property
> def all_evidence_rejected(self) -> bool:
>     return len(self.evidence_quotes) > 0 and all(eq.user_rejected for eq in self.evidence_quotes)
> ```

---

### E.6 Yhteenveto — Luvun 6 muutostarpeet tiedostoittain

| Tiedosto | Muutos | QG |
| :--- | :--- | :---: |
| `backend_v2/models/v2_core.py` | `EvidenceQuoteDTO` + `RowForensicsDTO` (`@computed_field all_evidence_rejected`) | QG1, QG5 |
| `backend_v2/services/blueprint.py` | Sitaattien hoisting → `EvidenceQuoteDTO` + `is_mcp_verified` fuzzy-tarkistus | QG1, QG4 |
| `backend_v2/services/mcp/alias_registry.py` | Aliaksen validointi + Fail-Fast `SemanticEvidenceError` | QG3 |
| `backend_v2/services/orchestrator/prompt_compiler.py` | Escape Hatch -lause `get_schema_healing_prompt()`:iin | QG3 |
| `backend_v2/models/prompts/field_prompts.py` | `DESC_EXACT_QUOTES`: Escape Hatch | QG3 |
| `backend_v2/services/llm_task_executor.py` | `used_evidence_ids` alias-validointi `_perform_semantic_validation()`:iin | QG3 |
| `client_app_v2/.../atom_matrix_table_widget.dart` | `allEvidenceRejected` ⚠️ -ikoni | QG5 |
| `backend_v2/templates/report_template.jinja2` | `all_evidence_rejected` ⚠️ -varoitus | QG5 |

### E.7 Falsifikaatio: Quality Gaten testattavuus

Jokainen Quality Gate on mekaanisesti testattavissa:

| QG | Testistrategia |
| :--- | :--- |
| QG1 | Yksikkötesti: `build_report_dto()` palauttaa `RowForensicsDTO`:n, jonka jokainen `EvidenceQuoteDTO` sisältää ei-tyhjän `source_reference`:n, kun `used_evidence_ids` on täytetty |
| QG2 | Staattinen analyysi: `grep -r "mcp_audit\|source_alias_map" client_app_v2/ backend_v2/templates/` palauttaa 0 tulosta |
| QG3 | Yksikkötesti: `alias_registry.resolve("<<QRM-SRC-99>>", {"<<QRM-SRC-1>>": "x"})` heittää `SemanticEvidenceError` dynaamisella Escape Hatch -viestillä |
| QG4 | Yksikkötesti: `AnchorValidationService.calculate_fuzzy_score(norm_quote, mcp_response_norm) > 90.0` → `is_mcp_verified = True` |
| QG5 | Yksikkötesti: `RowForensicsDTO(evidence_quotes=[EvidenceQuoteDTO(user_rejected=True)]).all_evidence_rejected == True` JA `RowForensicsDTO(evidence_quotes=[]).all_evidence_rejected == False` |

---

## Liite F: Koodivaikutusanalyysi (System 2 Deep Dive — Luku 7: Esityskerros ja UI-pariteetti)
Tämä osio verifioi jokaisen luvun 7 renderöintiväitteen todellista Flutter- ja Jinja2-koodikantaa vasten.

### F.1 Sitaattien ryhmittely — Evidence-First UI

**Epic väittää:** *"Litteän listan sijaan `Lainaukset (quotes)` -sarake tulostaa sitaatit ryhmiteltynä niiden tason alle."*

**Nykytila koodissa:**

1. **Python** — `MatrixScorecardRowDTO.quotes_list` (`v2_core.py`, rivi 893): `list[str] | None`. Litteä merkkijonolista — **ei tasoryhmittelyä**. Ryhmittely tapahtuu vasta `RowForensicsDTO`:n kautta (uusi), ei nykyisen `quotes_list`-kentän kautta.
2. **Blueprint** — `blueprint.py` (rivit 430–459): `quotes_list` koostetaan litteäksi listaksi. Deduplikaatio ja trunkaus (150 merkkiä) tehdään, mutta tasotietoa **ei säilytetä**.
3. **Flutter** — `atom_matrix_table_widget.dart` (rivit 226–239, 349–354): Renderöi litteän listan Markdown-bulleteina: `m.quotesList.map((q) => '- $q').join('\n')`. **Ei tasoryhmittelyä.** ✅ Nykyinen koodi ei yritä tehdä mitään älyä — se on puhdas renderöijä.
4. **Jinja2** — `report_template.jinja2` (rivit 259–267): Renderöi yksittäisen `cited_text_quote`-kentän — **ei iteroi `quotes_list`:iä lainkaan**.

**Muutokset tiedostoittain:**

> | Tiedosto | Muutos |
> | :--- | :--- |
> | `backend_v2/models/v2_core.py` | `RowForensicsDTO.level_quotes: list[LevelQuotesDTO]` — jo suunniteltu Liitteessä B. `LevelQuotesDTO` sisältää `level: int`, `level_name: str`, `quotes: list[EvidenceQuoteDTO]` |
> | `backend_v2/services/blueprint.py` | Hoisting-logiikka: nykyinen litteä `quotes_list`-koostaminen (rivit 430–459) korvataan `RowForensicsDTO`:n koostamisella. Atomitason `exact_quotes` + `used_evidence_ids` → `EvidenceQuoteDTO`:t, ryhmitellään tason mukaan → `LevelQuotesDTO`-lista |
> | `client_app_v2/.../scorecard_dto.dart` | `quotesList: List<String>` → korvataan `forensics: RowForensicsDto?` (nullable, koska vanhat ajot eivät sisällä forensics-dataa) |
> | `client_app_v2/.../atom_matrix_table_widget.dart` | Nykyinen `m.quotesList.map((q) => '- $q')` -renderöinti korvataan sisäkkäisellä iterointilogiikalla: `forensics.levelQuotes.forEach((lq) => { header(lq.levelName); lq.quotes.forEach((eq) => renderQuote(eq)); })` |
> | `backend_v2/templates/report_template.jinja2` | Nykyinen `cited_text_quote` -kenttä korvataan `forensics.level_quotes` -iterointilogiikalla. **HUOM:** Tämä on uutta koodia, ei refaktorointia — Jinja2 ei nykyisin renderöi `quotes_list`-listaa lainkaan |

**Falsifikaatio:** Flutter-widgetin `scorecard_dto.dart` on Freezed-generoitu. Kenttämuutos (`quotesList` → `forensics`) vaatii `build_runner`-ajon. Lisäksi `scorecard_dto.g.dart` ja `scorecard_dto.freezed.dart` regeneroituvat automaattisesti. **Riski:** Jos uusi kenttänimi ei mäppäydy backend-JSON:iin, Freezed deserializes sen `null`:ksi hiljaisesti (koska kenttä on nullable). Tämä ei kaadu, mutta forensics-data katoaa. **Ratkaisu:** Integration-testillä varmistetaan, että `build_report_dto()` palauttaman JSON:in `forensics`-kenttä deserializoituu oikein Freezed-malliin.

---

### F.2 Lähdeviitteet ja XAI-ikonit (`is_mcp_verified`)

**Epic väittää:** *"Jos sitaatilla on `is_mcp_verified == True`, sen viereen tulostetaan vihreä ✅."*

**Nykytila koodissa:**
- `is_mcp_verified`-kenttää **ei ole olemassa** missään — uusi kenttä `EvidenceQuoteDTO`:ssa.
- Nykyinen Jinja2-template renderöi jo `✅ Tarkistettu Googlen lähteistä:` (rivi 278) — mutta tämä on hardkoodattu `cited_web_citation`-kenttään, ei `is_mcp_verified`-logiikkaan.

**Muutokset tiedostoittain:**

> | Tiedosto | Muutos |
> | :--- | :--- |
> | Flutter `atom_matrix_table_widget.dart` | Jokaisen sitaatin perässä: `if (eq.isMcpVerified) Icon(Icons.verified, color: Colors.green)` |
> | Jinja2 `report_template.jinja2` | `{% if quote.is_mcp_verified %}<span style="color:green">✅ MCP-Varmennettu</span>{% endif %}` |
> | Flutter `scorecard_dto.dart` | Uusi Freezed-malli `EvidenceQuoteDto` kentällä `isMcpVerified` |

**Falsifikaatio:** Nykyinen hardkoodattu `✅ Tarkistettu Googlen lähteistä:` (Jinja2, rivi 278) on **ristiriidassa** uuden `is_mcp_verified`-logiikan kanssa. Jos molemmat jäävät koodiin, samassa raportissa voi näkyä kaksi eri vihreää merkkiä eri semantiikoilla. **Ratkaisu:** Vanha `cited_web_citation` ✅-ikoni poistetaan ja korvataan uudella `is_mcp_verified` -ehtolauseella. Tämä on breaking change vanhoille ajoille, joissa `cited_web_citation` on ainoa lähde — mutta se on konsistentti Epic 88:n kanssa.

---

### F.3 Yliviivaus (Soft Delete)

**Epic väittää:** *"Flutterissa `TextDecoration.lineThrough`, PDF:ssä `<del>`-tägi."*

**Nykytila koodissa:**
- `user_rejected`-kenttää **ei ole olemassa** — uusi ominaisuus (ks. Liite D.3).
- Flutter ei renderöi yliviivauksia nykyisin.
- Jinja2 ei käytä `<del>`-tägiä nykyisin.

**Muutokset tiedostoittain:**

> | Tiedosto | Muutos |
> | :--- | :--- |
> | Flutter `atom_matrix_table_widget.dart` | `if (eq.userRejected) TextStyle(decoration: TextDecoration.lineThrough, color: Colors.red.withOpacity(0.6))` |
> | Jinja2 `report_template.jinja2` | `{% if quote.user_rejected %}<del style="color: #999">{{ quote.text }}</del>{% else %}{{ quote.text }}{% endif %}` |
> | Flutter `scorecard_dto.dart` | `EvidenceQuoteDto` kenttä: `@Default(false) bool userRejected` |

**Ei falsifikaatioriskiä** — yksinkertaisia ehtolauseita.

---

### F.4 Kaskadoituva liputus (`all_evidence_rejected`)

**Epic väittää:** *"Jos säännön tason kaikki sitaatit on hylätty, käyttöliittymä renderöi arvosanan viereen varoitusikonin ⚠️."*

**Nykytila koodissa:**
- Logiikkaa **ei ole olemassa** — uusi ominaisuus.
- `all_evidence_rejected` lasketaan `RowForensicsDTO`:n `@computed_field`:nä Pythonissa (ks. Liite E.5).

**Muutokset tiedostoittain:**

> | Tiedosto | Muutos |
> | :--- | :--- |
> | Flutter `atom_matrix_table_widget.dart` | Arvosanasarakkeen viereen: `if (m.forensics?.allEvidenceRejected == true) Tooltip(message: l10n.evidenceRejectedWarning, child: Icon(Icons.warning, color: Colors.amber))` |
> | Jinja2 `report_template.jinja2` | `{% if axis.forensics and axis.forensics.all_evidence_rejected %}<span style="color: #f57c00">⚠️ Arvosanan perusteet kumottu</span>{% endif %}` |
> | Flutter `scorecard_dto.dart` | `RowForensicsDto` kenttä: `@Default(false) bool allEvidenceRejected` |

**Falsifikaatio:** `all_evidence_rejected` on `@computed_field` Pythonissa, joten se serialisoituu JSON:iin automaattisesti. Flutter deserializoi sen Freezed-malliin. Ketju toimii **sillä ehdolla**, että `RowForensicsDTO.model_dump(mode="json")` sisältää `all_evidence_rejected`-kentän. ✅ Pydantic V2 `@computed_field` sisältyy `model_dump()`:iin oletusarvoisesti.

---

### F.5 100% Pariteetti (Flutter ↔ PDF)

**Epic väittää:** *"Kummassakin käyttöliittymässä tapahtuu tismalleen samat ehtolauseet."*

**Verifikaatio:**

> Kaikkien neljän ehtolauseen (ryhmittely, ikoni, yliviivaus, varoitus) on oltava identtisiä molemmissa renderöijissä. Tämä on **testausmandaatti**, ei koodimuutos. Pariteettitesti:
>
> | Ehtolause | Flutter | Jinja2 |
> | :--- | :--- | :--- |
> | Tasoryhmittely | `forensics.levelQuotes.forEach(...)` | `{% for lq in axis.forensics.level_quotes %}` |
> | MCP-ikoni | `if (eq.isMcpVerified) Icon(...)` | `{% if quote.is_mcp_verified %}✅{% endif %}` |
> | Yliviivaus | `TextDecoration.lineThrough` | `<del>` |
> | Varoitus | `if (forensics.allEvidenceRejected) Icon(...)` | `{% if forensics.all_evidence_rejected %}⚠️{% endif %}` |
>
> **Pariteetin automaattinen valvonta:** E2E-varianssi-testiskripti (`run_e2e_variance_test.py`) voi verrata Flutter-JSON:ia ja PDF-HTML:ää saman ajon osalta.

**Falsifikaatio:** Jinja2:n `ns.seen_quotes` -deduplikaatiologiikka (rivi 261) tekee ylimääräistä työtä, jota Flutter ei tee. Tämä voi aiheuttaa tilanteen, jossa PDF näyttää vähemmän sitaatteja kuin Flutter. **Ratkaisu:** Deduplikaatio siirretään Pythoniin (`BlueprintTransformer`), jolloin molemmat renderöijät saavat tismalleen saman dedupl. listan. Nykyinen `seen_quotes` Jinja2:ssa poistetaan.

---

### F.6 Yhteenveto — Luvun 7 muutostarpeet tiedostoittain

| Tiedosto | Muutos | 7.1 kohta |
| :--- | :--- | :---: |
| `backend_v2/models/v2_core.py` | `RowForensicsDTO`, `LevelQuotesDTO`, `EvidenceQuoteDTO` | Ryhmittely |
| `backend_v2/services/blueprint.py` | Litteä `quotes_list` → `RowForensicsDTO` hoisting. Deduplikaatio Pythoniin | Ryhmittely, Pariteetti |
| `client_app_v2/.../scorecard_dto.dart` | `quotesList: List<String>` → `forensics: RowForensicsDto?` + uudet Freezed-mallit | Kaikki |
| `client_app_v2/.../atom_matrix_table_widget.dart` | Sisäkkäinen iterointi `forensics.levelQuotes`, ✅-ikoni, yliviivaus, ⚠️-varoitus | Kaikki |
| `backend_v2/templates/report_template.jinja2` | `cited_text_quote` → `forensics.level_quotes` iterointi. `ns.seen_quotes` poistetaan. ✅ ja ⚠️ ehtolauseet | Kaikki |

### F.7 Falsifikaatio: Kriittiset riskit ja korjaukset

1. **Jinja2 ei renderöi `quotes_list`-kenttää lainkaan** — se käyttää yksittäistä `cited_text_quote`-kenttää. Tämä tarkoittaa, että PDF-puolella forensics-renderöinti on **kokonaan uutta koodia**, ei refaktorointia. Tärkeä tieto työmäärä-arviolle.
2. **`cited_web_citation` ✅-ikoni on ristiriidassa** uuden `is_mcp_verified`-logiikan kanssa. Vanha ikoni poistetaan.
3. **Jinja2:n `ns.seen_quotes` deduplikaatio** tehdään renderöintitasolla — se on pariteettiriski. Siirretään Pythoniin.
4. **Freezed-regenerointi** on pakollinen muutoksen jälkeen (`dart run build_runner build`). Kentän deserializoinnin onnistuminen vaatii integration-testin.

