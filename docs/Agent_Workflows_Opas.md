# Agenttien Työkulkujen (Workflows) Käyttöopas (V2026)

Tämä opas on suunnattu ohjelmistokehittäjälle (sinulle) ja se selittää `c:\src\quorum\.agents\workflows\` hakemiston työkalujen tarkoituksen, käyttöajankohdan sekä sisäisen logiikan. Koko järjestelmä perustuu Tier-malliin (Tasot 1-5), joka estää tekoälyä hallusinoimasta ja pakottaa sen työskentelemään askel kerrallaan arkkitehtuurisääntöjen puitteissa.

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

---

## 3. Konepellin alla: Työnkulkujen Ohjausarkkitehtuuri (Päivitetty)

Kaikki yllä mainitut työnkulut hyödyntävät äärimmilleen viritettyä Prompt Engineering -arkkitehtuuria varmistaakseen agentin maksimaalisen tarkkuuden ja "Fail-Fast" -kiellon noudattamisen:

*   **Ehdollistettu Sääntöjen Lataus (Dynamic Context):** Token-hukan ja kontekstin laimenemisen välttämiseksi työnkulut eivät koskaan lataa turhia sääntöjä muistiin. Ne pohjustautuvat `00-antigravity-core` -määritykseen, ja päättelevät dynaamisesti ladataanko muistiin *lisäksi* backendin (`01`) vai frontendin (`02`) säännöt.
*   **XML-Kapselointi:** Jokainen järjestelmän `/tier` -työnkulku (kts. `.agents/workflows/`) on uudelleenkoodattu taustalla puhtaaseen **<system_prompt>** XML-rautaiseen muottiin. Tämä luo mallin ohjausmekanismille vankilan, jossa tavoitteet (`<objective>`), oppaat (`<context_rules>`) ja absoluuttisesti noudatettavat työvaiheet (`<execution_protocol>`) pidetään kognitiivisesti täysin erillään toisistaan.
