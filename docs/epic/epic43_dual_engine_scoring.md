# Epic 43: Dual-Engine Scoring Architecture

## 1. Yhteenveto (Executive Summary)
Tavoitteena on mahdollistaa kahden täysin erillisen matemaattisen arviointimallin (Waterfall / Auditointi ja Dampening / Valmennus) vapaa valinta käyttöliittymästä, saumattomasti yhdessä Epic 42:n Kireystason (Strictness Level 0-100) kanssa.

**Liiketoiminta-arvo:** Mahdollistaa saman SaaS-alustan myymisen sekä armottomaan compliance-auditointiin että psykologiseen HR-valmennukseen, säilyttäen täyden arkkitehtonisen eheyden (Zero-Trust).

## 2. Arkkitehtoniset Tavoitteet
- **Laskennan eriyttäminen (Decoupling):** Matematiikka pidetään täysin erillään Pydantic-validaatioista. Laskentamallit on jaettu omiin erillisiin moottoreihinsa (Strategy Pattern) hakemistossa `backend_v2/utils/scoring/` (esim. `waterfall_engine.py` ja `dampening_engine.py`), jotta "Dual-Engine" -arkkitehtuuri toteutuu puhtaasti ja mahdollistaa mallien itsenäisen kehittämisen tulevaisuudessa.
- **DRY-periaate (Don't Repeat Yourself):** Pydantic-validaatiot (Kireystason `IMPLIED_INTENT` vs `EXPLICIT_QUOTE`) ja tekoälyn LLM-haut pysyvät samoina. Laskentamalli on ainoastaan "kytkin", joka muuttaa sokeiden `True/False` -osumien muuntamista lopulliseksi arvosanaksi Hook-kerroksessa.

## 3. Tekniset Vaatimukset (Backend)

### 3.1. Tietokanta ja Mallit (Pydantic / Enums)
- **Uusi Enum:** Lisätään `ScoringStrategy` (Arvot: `WATERFALL_FLOOR`, `PROGRESSIVE_DAMPENING`) domain-malleihin.
- **Päivitys:** `ExecutionCreate` ja `ExecutionRecord` DTO-malleihin lisätään `scoring_strategy` -kenttä (oletuksena `WATERFALL_FLOOR`).

### 3.2. Hook-Kerros (`backend_v2/hooks/scoring.py`)
- Muutetaan nykyinen `waterfall_scoring_hook` dynaamiseksi `matrix_scoring_hook` -hookiksi.
- Laskentalogiikka tuodaan uusista erillisistä moottoreista (`backend_v2.utils.scoring.waterfall_engine` ja `backend_v2.utils.scoring.dampening_engine`).
- Lisätään haaroitus: `if execution.scoring_strategy == ScoringStrategy.PROGRESSIVE_DAMPENING:`
- Haaroituksesta kutsutaan uutta Dampening-moottoria.
- Muuten kutsutaan Waterfall-moottoria.

### 3.3. Synteesi-Hook (`backend_v2/hooks/synthesis.py`)
- Päivitetään `text_consolidation_hook` -funktiota niin, että valittu `scoring_strategy` (Auditointi vs. Valmennus) injektoidaan LLM:n kontekstiin (esim. promptin `execution_parameters` -osioon).
- Näin "Chief Editor" -tekoäly ymmärtää kontekstin ja osaa sanoittaa lopullisen raportin oikean viitekehyksen kautta (esim. "Tämä on kehittävä valmennusarvio..." vs. "Tämä on tiukka compliance-auditointi...").

### 3.4. Matemaattiset Mallit (Scoring Engines)
Kaikki laskentamallit hyödyntävät backendin `math_utils.py` -tiedoston natiiveja, täsmällisiä matemaattisia funktioita. Tapaa laskea palautetta ei muuteta, vaan arkkitehtuuri ainoastaan altistaa nämä moottorit dynaamisesti valittavaksi.

- **WATERFALL_FLOOR (Auditointi):**
  - **Funktio:** `calculate_waterfall_floor`
  - **Logiikka:** Guttmanin asteikko (Guttman scale). Etsii absoluuttisen "lattian" iteroimalla alimmalta tasolta ylimmälle. Jos kriteerien osumaprosentti (`hit_rate`) ylittää määritellyn kynnyksen, taso läpäistään. Pysähtyy armottomasti heti, kun jokin taso epäonnistuu. Palauttaa sen tason arvon, joka viimeisenä läpäistiin.

- **PROGRESSIVE_DAMPENING (Valmennus):**
  - **Funktio:** `calculate_progressive_dampening_score`
  - **Logiikka:** CDM (Cognitive Diagnostic Model) / DINA -malli. Guttman-giljotiinin sijaan jokainen taso toimii "vaimentimena" (dampener) ylemmille tasoille. Jos alatason osumaprosentti on heikko, se alentaa rangaistuskertoimella (`math.sqrt(hit_rate)`) kaikkia ylempien tasojen tuottamia pisteitä. Estää absoluuttiset nollapudotukset, mutta rakenteelliset puutteet vaimentavat silti lopputulosta.

- **PURE_AVERAGE (Puhdas Keskiarvo / Testimalli):**
  - **Funktio:** Käyttää `calculate_weighted_score` -funktiota (mutta kaikilla kriteereillä on automaattinen painoarvo 1).
  - **Logiikka:** Laskee osumien matemaattisen suhteen maksimiin. Täysin lineaarinen malli ilman kerrannaisrangaistuksia virheistä. Esim. 3 osumaa 4:stä on 75 %. HUOM: Litistää BARS-matriisien tikapuulogiikan, jolloin ylin taso muuttuu samanarvoiseksi alimman tason kanssa.

- **WEIGHTED_AVERAGE (Painotettu Keskiarvo / Testimalli):**
  - **Funktio:** `calculate_weighted_score`
  - **Logiikka:** Laskee kaikkien matriisin osumien globaalin painotetun keskiarvon (`achieved_weights += hits * level`). Pisteet skaalataan suhteellisesti maksimipistemäärään nähden. Voidaan käyttää "Pure Average" -mallina, jos kaikkien kriteerien painoarvo on 1.

## 4. Tekniset Vaatimukset (Frontend / Flutter)
- **Käyttöliittymä (Työnkulun käynnistys):** Sama modal-ikkuna, missä valitaan Kireystaso (Slider 0-100), päivitetään sisältämään valintalista (Dropdown-valikko) matemaattisen mallin valitsemiseksi.
- **Valintalistan vaihtoehdot:**
  - `Auditointi-laskenta (Waterfall - Vaatii ehdottoman loogisen ketjun)` (Oletus)
  - `Valmennus-laskenta (Progressive Dampening - Palkitsee osasuorituksista)`
  - `Testaus: Puhdas Keskiarvo (Pure Average - Litistää BARS-tikapuut)`
  - `Testaus: Painotettu Keskiarvo (Weighted Average)`
- Valittu parametri lähetetään backendin `POST /executions` -rajapintaan.

## 5. Taaksepäin yhteensopivuus ja Migraatio
- **Nolla-toleranssi / Fail-Fast:** Taaksepäin yhteensopivuutta tai Pydantic-oletusarvoja (kuten default = Waterfall) **ei tueta**.
- Arkkitehtuurin Fail-Fast -periaatteen mukaisesti `scoring_strategy` on oltava eksplisiittisesti pakollinen kenttä kaikissa payload-malleissa.
- Jos kenttä puuttuu, järjestelmän tulee kaatua välittömästi (Fail-Fast) HTTP 422 -virheellä. Vanhaa dataa tai työnkulkuja ei tueta ilman eksplisiittistä parametria.
- **Järjestelmän laajuinen auditointi:** On varmistettava, ettei mikään järjestelmän osa (skriptit, API-rajapinnat, työnkulkumoottorit tai käyttöliittymäkomponentit) yritä peitellä virheitä tai tukea vanhoja legacy-asetuksia tämän toteutuksen ympärillä. Kaikki vanhat viritelmät ja fallback-logiikat on tuhottava.

## 6. Laatuportit ja Koodistandardit (Tier 2 Hardening)
Tämän Epicin puitteissa luotavien uusien ohjelmistojen (backend ja frontend) on mentävä täydellisesti läpi Tier 2 -karkaisusilmukoista (Hardening Loop). Seuraavat säännöt on "upotettu" osaksi tätä Epic-dokumenttia:

### 6.1. Backend (Tier 2 Hardening)
- **Zero-Compromise Pledge:** Pydantic-mallit on validoitava `.model_validate()` -funktiolla. Koodissa ei saa olla hiljaisia fallbackeja (`.get("default")`) tai tyhjien arvojen sietämistä.
- **Fail-Fast Hydration:** Sanakirjat (`dict`) on hydratoitava Pydantic-objekteiksi (kuten `StepOutputDTO`) ennen käsittelyä. Arvojen onkiminen `data.get("avain")` on ankarasti kielletty logiikkakerroksessa.
- **Opaque Stripe ID Mandate:** Kaikkien ID-arvojen on oltava natiiveja Stripe-tyylisiä (esim. `blk_...`, `usr_...`).
- **Tripartite Rendering Boundary:** Backend ei saa rakentaa Markdown-taulukoita, vaan palauttaa puhtaan DTO:n (Frontend ja PDF hoitavat renderöinnin natiivisti).
- **Yleiset:** Ei God-blockeja (`except Exception: pass`), `# type: ignore` vaatii tarkan error-koodin ja perustelun, ja Pydantic-skeemoissa `extra='forbid'` -käytäntö on voimassa.

### 6.2. Frontend (Tier 2 Hardening)
- **No Legacy Fallback Hacks:** Dart-koodissa ei saa käyttää null-coalescing (`?? 'default'`) -oikoteitä, jotka peittävät Pydantic API:n rakenteellisia virheitä. Myös `.maybeWhen` -metodin käyttö väärän datan ohittamiseen on kielletty.
- **Data Integrity:** UI-komponenttien on odotettava backendiltä tiukasti tyypitettyä dataa (Enumit kuten `ScoringStrategy`).
- Koodin on mentävä 100% läpi Flutterin lint-ajoista ilman ainuttakaan `Fail` -merkintää laatuportin taulukossa.
