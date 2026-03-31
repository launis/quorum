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
    *   **Toiminta:** Pakottaa agentin avaamaan `implementation_plan.md` tiedoston ja toteuttamaan vain ja ainoastaan **yhden askeleen kerrallaan**. Vaatii sinulta luvan ("PROCEED") jokaisen askeleen välillä.
*   **`/tier3-feature-refactor` (Yksittäinen Koodari):** 
    *   **Miksi:** Yksittäisen skriptin refaktorointi tai pienen UI-komponentin rakennus, joka ei vaadi isoa Tier 1 -suunnitelmaa.
*   **`/tier3-database-reset` (Tietokannan Siivooja):** 
    *   **Miksi:** Turvallinen, rutiininomainen lokaalin TinyDB:n pyyhintä ja uudelleensiemennys Seed-datan pohjalta ilman koodimuutoksia.
*   **`/tier4-bug-hunting` (Verikoira):** 
    *   **Miksi:** Sovellus kaatuu tai heittää 500-virhettä.
    *   **Toiminta:** Estää agenttia käyttämästä "purkkavirityksiä" (kuten `try-except pass`). Pakottaa agentin seuraamaan datavirtaa ja etsimään virheen juurisyyn Fail-Fast -sääntöjen läpi.
*   **`/tier5-zero-shortcut-audit` (Armoton Katselmoija):** 
    *   **Miksi:** Halutaan varmistaa, että vastakirjoitettu koodi täyttää V5.2 Phase 9 -laatuvaatimukset.
    *   **Toiminta:** Etsii aggressiivisesti f-stringejä lokeista, puuttuvia Isolate-kutsuja tai paljastuneita Pydantic-sanakirjoja.

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
2.  **Agentin toiminta:** Agentti avaa sisäiset muokkaustyökalunsa (MCP `replace_file_content`) ja tekee korjaavat koodimuutokset suoraan tiedostojärjestelmään. Frontendin tapauksessa se siirtää raskaat JSON-purut `Isolate.run`-sisään tyyppiturvallisesti.
3.  **Vahvistus ja Testaus:** Agentti antaa sinulle lokaalit Audit-komennot kopioitavaksi terminaaliin (esim. `uv run ruff check... --fix` tai `dart format`).
4.  **Agentin tila:** Korjaus on valmis kansion osalta.
5.  **Luuppi alusta (Kontekstin nollaus):** Kun siirrytään seuraavaan kansioon, tekoäly on saattanut jo "unohtaa" alkuperäiset säännöt pitkän koodaamisen takia (Context Amnesia). Siksi on erittäin tärkeää tehdä aina **vain yksi kansio kerrallaan**. Pelkän "PROCEED" sanan sijaan on turvallisinta komentaa: *"PROCEED. Aja /tier2-hardening-backend uudestaan listan seuraavalle kansion kohdalle."* Tämä pakottaa agentin lukemaan säännöt tuoreeltaan muistiin ennen uutta kansiota.
