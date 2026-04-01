# Agenttien Työkulkujen (Workflows) Käyttöopas (V2026)

Tämä opas on suunnattu ohjelmistokehittäjälle (sinulle) ja se selittää `quorum\.agents\workflows\` hakemiston työkalujen tarkoituksen, käyttöajankohdan sekä sisäisen logiikan. Koko järjestelmä perustuu Tier-malliin (Tasot 1-5), joka estää tekoälyä hallusinoimasta ja pakottaa sen työskentelemään askel kerrallaan arkkitehtuurisääntöjen puitteissa.

---

## 1. Yleiskatsaus Työkuluista (Milloin ja miksi?)

Agentin komentaminen tapahtuu kutsumalla työnkulkua sen nimellä (esim. *"Aja /tier1-planner..."* tai *"Auta minua, /tier4-bug-hunting"*).

*   **`/tier1-planner` (Okkultistinen Arkkitehti):** 
    *   **Miksi:** Uuden laajan ominaisuuden (Epic) tai arkkitehtuurimuutoksen aloitus. Estää tekoälyä kirjoittamasta koodia summamutikassa.
    *   **Toiminta:** Tuottaa loogisesti jaetun virstanpylvässuunnitelman `implementation_plan.md` -tiedostoon. Koodia ei tuoteta riviäkään.
*   **`/tier2-execute` (Mekaaninen Toteuttaja):** 
    *   **Miksi:** Suunnitelma on valmis ja hyväksytty.
    *   **Toiminta:** Pakottaa agentin toteuttamaan vain **yhden askeleen kerrallaan**. Vaatii yksikkötestin koodauksen ja The Universal Quality Gate -komentojen luovutuksen sinulle ajettavaksi ennen luvan pyytämistä seuraavaan askeleeseen.
*   **`/tier3-feature-refactor` (Yksittäinen Koodari):** 
    *   **Miksi:** Yksittäisen ominaisuuden rakennus.
    *   **Toiminta:** Toimii koodausassistenttina, mutta on Arkkitehtuurisäännöstön mukaisesti velvoitettu TDD-mandaattiin: ominaisuutta ei rakenneta ilman yksikkötestiparia (`pytest` / `flutter test`).
*   **`/tier3-database-reset` (Tietokannan Siivooja):** 
    *   **Miksi:** Turvallinen, rutiininomainen lokaalin TinyDB:n pyyhintä ja uudelleensiemennys Seed-datan pohjalta ilman koodimuutoksia.
*   **`/tier4-bug-hunting` (Verikoira):** 
    *   **Miksi:** Sovellus kaatuu tai heittää 500-virhettä.
    *   **Toiminta:** Pakotettu TDD (Red-Green-Refactor) -malliin. Vaatii bugin toisintavan rikkinäisen yksikkötestin luomista ENNEN koodin paikkaamista. Estää näin "purkkaviritykset".
*   **`/tier5-zero-shortcut-audit` (Armoton Katselmoija):** 
    *   **Miksi:** Halutaan varmistaa, että vastakirjoitettu koodi täyttää kaikki V5.2 Phase 9 -laatuvaatimukset.
    *   **Toiminta:** Hylkää koodin välittömästi (REFUSED), mikäli siihen ei ole kirjoitettu testejä tai linttaus- / koodauskomentoja (The Universal Quality Gate) yritetään kiertää.

---

## 2. Moniosaiset Hardening-Audit -Ketjut (Erikoistyönkulut)

Tärkeimmät ja järeimmät työkalut laadunvarmistukseen ovat **`/tier2-hardening-backend`** ja **`/tier2-hardening-frontend`**. Ne on suunniteltu valtavien hakemistopuiden (kuten koko `backend_v2` tai `client_app_v2`) systemaattiseen läpikäyntiin ilman tekoälyn konteksti-ikkunan romahtamista.

Näitä työnkulkuja ohjataan yhteistyössä interaktiivisena silmukkana (Loop).

### Vaihe 1: Kartoitus (Mapping)
1.  **Sinun komentosi:** *"Aloita /tier2-hardening-backend kansioon `backend_v2/routers`"*
2.  **Agentin toiminta:** Agentti listaa kansion sisällön ja skippaa automaattisesti turhat roskakansiot (esim. `__pycache__` tai generoidut tiedostot). Se rakentaa chattiin virtuaalisen Markdown-tarkistuslistan jokaisesta löytämästään alihakemistosta.
3.  **Agentin tila:** Agentti pysähtyy automaattisesti asettaen Checkpointin: *"Lista valmis. Odotan PROCEED-komentoa."*

### Vaihe 2: Auditointi (One at a time)
1.  **Sinun komentosi:** *"PROCEED"*
2.  **Agentin toiminta:** Agentti poimii listan **ensimmäisen** kansion. Se lukee kaikki kansion sisällä olevat `.py` tai `.dart` -tiedostot kerralla muistiin.
3.  **Syväanalyysi:** Koodia verrataan millimetrin tarkasti Phase 9 sääntöihin. (Etsitään mm. huonoa asynkronista koodia, dict-purkuja Pydanticin sijasta, raakoja exceptioneja).
4.  **Agentin tila:** Agentti listaa virheet tai ilmoittaa kansion olevan virheetön. Lopuksi se kysyy: *"Haluatko komennon FIX vai NEXT?"*

### Vaihe 3: Korjaus (Remediation)
1.  **Sinun komentosi:** *"FIX"*
2.  **Agentin toiminta:** Agentti avaa sisäiset muokkaustyökalunsa (MCP `replace_file_content`) ja tekee korjaavat koodimuutokset. Tekoäly on myös ohjeistettu vaatimaan yksikkötestien asiallista suorittamista/päivittämistä ohjelmointimuutosten jälkeen.
3.  **Vahvistus ja Testaus:** Agentti luovuttaa sinulle **The Universal Quality Gate** -komennot kopioitavaksi terminaaliin (esim. ohjeet Ruff/Mypy/Pytest tai Flutter Analyze/L10n/Test ajoon).
4.  **Agentin tila:** Korjaus on valmis kansion osalta.
5.  **Luuppi alusta (Kontekstin nollaus):** Tekoäly voi unohtaa säännöt pitkän muokkauksen aikana (Context Amnesia). Siksi edetään aina **vain yksi kansio kerrallaan**. Pelkän "PROCEED"-sanan sijaan turvallisin jatkokomento on: *"PROCEED. Aja /tier2-hardening-backend uudestaan listan seuraavalle kansion kohdalle."*

### Nyrkkisääntö: Milloin avata uusi kontekstiikkuna (Uusi Chat)?
Hardening-workflow lukee satoja rivejä koodia kerralla. Pitkä konteksti aiheuttaa arkkitehtuurisääntöjen unohtamista.

1. **Säännöllisyys:** Vaihda kontekstiikkunaa noin **1–3 alihakemiston välein**, tai aina kun teit merkittäviä korjauksia (FIX-vaihe). Puhtaissa kansioissa (NEXT) voit mennä jopa 5-10 kansiota.
2. **Atomiset Git-tallennuspisteet:** Älä avaa uutta ikkunaa, jos koodaus on rikki. Tee aina *Git commit* onnistuneen korjaus- ja testauskierroksen jälkeen selkeäksi tallennuspisteeksi, ja avaa uusi ikkuna vasta sitten.
3. **Kontekstin siirto:** Et tarvitse kartoitusvaihetta (Mapping) uudessa ikkunassa. Ohjeista uutta chattiä suoraan:
   > *"Jatkamme jatkuvaa @tier2-hardening-backend.md -prosessia. Olemme vaiheessa 2 (Auditing). Tässä on jäljellä oleva task_backend.md -tarkistuslista: [liitä tekemättömät hakemistot]. Aloita ensimmäisestä kohdasta."*

---

## 3. Konepellin alla: Työnkulkujen Ohjausarkkitehtuuri

Kaikki yllä mainitut työnkulut hyödyntävät äärimmilleen viritettyä Prompt Engineering -arkkitehtuuria varmistaakseen agentin maksimaalisen tarkkuuden ja "Fail-Fast" -kiellon noudattamisen:

*   **Ehdollistettu Sääntöjen Lataus (Dynamic Context):** Token-hukan ja kontekstin laimenemisen välttämiseksi työnkulut eivät koskaan lataa turhia sääntöjä muistiin. Ne pohjustautuvat `00-antigravity-core` -määritykseen, ja päättelevät dynaamisesti ladataanko muistiin *lisäksi* backendin (`01`) vai frontendin (`02`) säännöt.
*   **XML-Kapselointi (System Prompt):** Jokainen järjestelmän `/tier` -työnkulku (kts. `.agents/workflows/`) on uudelleenkoodattu taustalla puhtaaseen **`<system_prompt>`** XML-rautaiseen muottiin. Tämä luo ohjausmekanismille vankilan, jossa tavoitteet (`<objective>`), oppaat (`<context_rules>`) ja absoluuttisesti noudatettavat työvaiheet (`<execution_protocol>`) pidetään kognitiivisesti erillään toisistaan.
*   **Kontrastiivinen Säännöstö (Contrastive Prompting):** Järjestelmän lokaalit ydinarkkitehtuurisäännöt (`.agents/rules/`) on irrotettu perinteisestä ihmisluettavasta tekstistä, ja koodattu tiukkoihin `<catastrophic_system_bans>` ja `<architectural_invariants>` XML-ryhmiin. Jokainen kielto esitetään tekoälylle ehdottomana mekaanisena parina: `<banned_pattern>` (purkkakoodikuvailu) -> `<mandatory_pattern>` (arkkitehtuurin mukainen ratkaisu). Ehdottomalla vastinparilla eliminoidaan laajoissa koodirefaktoroinneissa tekoälyn taipumus luikerrella ongelmista asettamalla purkkaratkaisuja.

---

## 4. Työnkulkujen Kultainen Sääntö: Atomiset Tallennukset (Atomic Commits)

Perinteisessä ihmisten välisessä koodauksessa yksi iso "päivän päätteeksi" tehtävä koottu commit on arkipäiväistä. Mutta kun koodiparina on **tekoälyagentti (Agentic AI)**, yhden suuren commitin taktiikka muuttuu valtavaksi riskiksi ja hidasteeksi. 

Tästä syystä koko Antigravity-järjestelmä nojautuu `atomic_checkpoint_mandate` -sääntöön, joka pakottaa koodaajan ja tekoälyn tallentamaan jokaisen loogisen, testatun askeleen välittömästi Gitiin tarkoilla tiedostopoluilla (esim. `git add client_app_v2/...` - koskaan ei saa käyttää komentoa `git add .`).

### ❌ Yhden ison kootun tallennuksen (Big Commit) haitat tekoälykehityksessä:

1. **Korttitalo-efekti (The House of Cards):** Tekoäly voi askeleessa 5 tehdä massiivisen hallusinaation ja rikkoa tiedoston rakenteen täysin. Jos aiemmat 4 askelta on tallentamatta, et voi perua pelkkää 5. askelta komennolla `git restore .` menettämättä myös aiempia onnistumisia.
2. **Tekoälyn sokeutuminen (Context Confusion):** Tekoälyn konteksti-ikkuna täyttyy nopeasti. Jos kymmenen muuttunutta kooditiedostoa roikkuu tallentamattomana Gitiin, uuden chatti-ikkunan avaaminen tekee tekoälylle mahdottomaksi päätellä nopeasti, mikä on puhdas lähtötilanne.

### ✅ Atomisten mikro-tallennusten (Atomic Commits) hyödyt:

1. **Voittamaton peruutettavuus (Rollback):** Voit kokeilla villeimpiäkin refaktorointi-ideoita nopeasti. Jos tekoäly erehtyy tai koodiratkaisu on väärä, tilanteen nollaus on sekuntien peliä (`git restore`) ja peli jatkuu minuutti sitten tallennetusta turvallisesta tilasta.
2. **Tarkka vianetsintä (Bisecting):** Kymmenestä selkeästä 20 rivin mikro-commitista on huomattavasti helpompaa ja nopeampaa jäljittää kaatumisen aiheuttanut virherivi (esim. ohjelmiston regressio), kuin kahlata läpi tuhansien rivien yhteis-commitia.
3. **Turvalliset tauot ja selkeys (Clean State):** Kun atominen askel on Gitissä lukittuna ja laatuportti on täytetty, projekti on aina periaatteellisessa tuotantovalmiudessa. Koodaushetken voi tauottaa milloin tahansa ilman pelkoa keskeneräisten muokkausten unohtumisesta.

### 🎮 Yhteenveto uudesta todellisuudesta (Super Mario -malli)

Tämä "jatkuvan mikro-tallennuksen" malli muuttaa Gitin perinteisestä versionhallinnasta eräänlaiseksi **jatkuvaksi pelikonsolin Super Mario -tallennuspisteeksi (Save State).**

* **Ei enää "Perjantai-iltapäivän Kaaosta":** Et enää koodaa kolmea päivää ja huomaa perjantaina, että koodi on solmussa, saati yritä purkaa 40 muuttunutta tiedostoa irti toisistaan ennen paniikkinomaista `git add .` -massa-commitia. Jokainen oikein toimiva palanen on jo kuitattu turvallisesti lukkoon heti tekoälyn suorituksen jälkeen.
* **"Ctrl + Z" x 100:** Koska sinulla ei ole enää tallentamattoman koodin "massoja", tekoälyn tuottamat umpikujat tai hallusinaatiot ovat täysin merkityksettömiä. Kaadat vain juuri kyseisen yrityksen roskakoriin `git restore .` -komennolla, poistut nykyisestä chat-ikkunasta ja avaat uuden puhtaan.
* **Ainoa poikkeus "Massa-commitiin" (Squashing):** Ainoa kerta kun niputat asioita massaksi, tapahtuu yleensä myöhemmin *Squash & Merge* -tyylillä (esim. GitHubin tai GitLabin käyttöliittymästä). Kun uusi ohjelmisto on vihdoin testattu, voit yhdistää kymmenet atomi-tallennukset yhdeksi ammattimaiseksi julkaisu-commitiksi tuotannon päähaaraan (`feat: Täysin uuden V2-järjestelmän käyttöönotto`).

Varsinaisessa "lokaalissa devaushiestä", johon tekoälynkoodaussääntömme (Tier-työnkulut) on rakennettu, sokea "massa-commit" on tästedes taaksejäänyttä elämää. Koodaat vain askel kerrallaan turvallisesti!
